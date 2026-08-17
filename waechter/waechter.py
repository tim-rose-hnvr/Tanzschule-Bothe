#!/usr/bin/env python3
"""SEO-Wächter für die Tanzschulen Familie Bothe.

Drei Stufen, wie in der Marktanalyse beschrieben:

  1  sensor     täglicher Crawl, Ergebnis als Momentaufnahme in Git
  2  pruefen    Regelwerk anwenden, Veränderung zum Vortag melden
  3  vorschlag  technische Fehler zu fertigen Korrekturen ausarbeiten

Der Wächter ändert von sich aus nichts an der Website. Stufe 3 schreibt
Vorschläge in eine Datei, die ein Mensch freigibt. Das ist Absicht: Technik
darf automatisch laufen, Inhalte und Preise nicht.

    python3 waechter.py sensor
    python3 waechter.py pruefen
    python3 waechter.py vorschlag
    python3 waechter.py bericht
"""
import argparse, html, json, re, subprocess, sys, pathlib, datetime
import concurrent.futures as cf

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from regeln import pruefe_seite, vergleiche, MUELL

HIER = pathlib.Path(__file__).parent
MOMENTE = HIER / "momentaufnahmen"
UA = "Mozilla/5.0 (compatible; BotheSEOWaechter/1.0)"

KONFIG = json.loads((HIER / "konfig.json").read_text(encoding="utf-8")) \
    if (HIER / "konfig.json").exists() else {}
BASIS = KONFIG.get("basis", "https://www.tanzschule-bothe.de")
MAX_SEITEN = KONFIG.get("max_seiten", 400)
PARALLEL = KONFIG.get("parallel", 6)


# ---------------------------------------------------------------- Werkzeuge
def hol(url, timeout=30):
    try:
        r = subprocess.run(
            ["curl", "-sSL", "--max-time", str(timeout), "-A", UA,
             "-w", "\n@@%{http_code}|%{time_starttransfer}|%{size_download}", url],
            capture_output=True, text=True)
        koerper, _, meta = r.stdout.rpartition("\n@@")
        code, ttfb, size = meta.split("|")
        return koerper, code.strip(), float(ttfb), int(size)
    except Exception:
        return "", "000", 0.0, 0


def sitemap_urls(basis):
    """Alle Seitenadressen aus der Sitemap, Unter-Sitemaps eingeschlossen."""
    urls, offen = [], []
    for pfad in ("/wp-sitemap.xml", "/sitemap.xml", "/sitemap_index.xml"):
        k, code, *_ = hol(basis + pfad, 25)
        if code.startswith("2") and "<loc>" in k:
            offen = re.findall(r"<loc>([^<]+\.xml[^<]*)</loc>", k)
            if not offen:
                return re.findall(r"<loc>([^<]+)</loc>", k)
            break
    for sm in offen:
        k, code, *_ = hol(sm, 25)
        if code.startswith("2"):
            urls += [u for u in re.findall(r"<loc>([^<]+)</loc>", k) if not u.endswith(".xml")]
    return urls


def analysiere(url):
    koerper, code, ttfb, size = hol(url)
    d = {"url": url, "code": code, "ttfb": round(ttfb, 2), "kb": round(size / 1024)}
    if not code.startswith("2") or not koerper:
        return d
    g = lambda p: (lambda m: m.group(1).strip() if m else None)(
        re.search(p, koerper, re.S | re.I))
    d["titel"] = re.sub(r"\s+", " ", g(r"<title>(.*?)</title>") or "")
    d["desc"] = re.sub(r"\s+", " ", g(
        r'<meta[^>]+name=["\']description["\'][^>]+content=["\'](.*?)["\']') or "")
    d["canonical"] = g(r'<link[^>]+rel=["\']canonical["\'][^>]+href=["\'](.*?)["\']')
    d["noindex"] = bool(re.search(r'name=["\']robots["\'][^>]*content=["\'][^"\']*noindex',
                                  koerper, re.I))
    d["h1"] = len(re.findall(r"<h1[\s>]", koerper, re.I))
    d["h2"] = len(re.findall(r"<h2[\s>]", koerper, re.I))
    d["ld"] = len(re.findall(r"application/ld\+json", koerper, re.I))
    d["og"] = len(re.findall(r'property=["\']og:', koerper, re.I))
    bilder = re.findall(r"<img[^>]*>", koerper, re.I)
    d["img_gesamt"] = len(bilder)
    d["img_ohne_alt"] = sum(1 for i in bilder if not re.search(r'alt=["\'][^"\']+["\']', i))
    # Erste H1 mitnehmen — Stufe 3 baut daraus Titel- und Beschreibungsvorschläge.
    h1 = re.search(r"<h1[^>]*>(.*?)</h1>", koerper, re.S | re.I)
    d["h1_text"] = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", h1.group(1))).strip()[:120] if h1 else ""
    text = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", koerper, flags=re.S | re.I)
    text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", text)).strip()
    d["woerter"] = len(text.split())
    d["auszug"] = inhaltstext(koerper)
    return d


# Kopf-, Navigations- und Fußzeilentext steht auf jeder Seite gleich und taugt
# deshalb nicht als Beschreibung. Erster Versuch zog genau den — die Vorschläge
# lauteten alle "Tanzschule Familie Bothe … +49 (0) 511 66 37 66".
BOILERPLATE = re.compile(
    r"\+49|\(0\) ?511|tanzen@|Zum Inhalt springen|Skip to (?:content|main)|"
    r"Cookie|Datenschutz|Impressum|Newsletter|Menü|Navigation|"
    r"Tanzschulen? Familie Bothe|Alle Rechte vorbehalten", re.I)


def inhaltstext(koerper: str, grenze: int = 700) -> str:
    """Fließtext der Seite, ohne Gerüst.

    Bevorzugt <main> oder <article>; sonst alles nach der ersten H1 — dort
    beginnt auf dieser Website verlässlich der eigentliche Inhalt.
    """
    m = re.search(r"<(?:main|article)\b[^>]*>(.*?)</(?:main|article)>", koerper, re.S | re.I)
    roh = m.group(1) if m else koerper
    nach_h1 = re.split(r"</h1\s*>", roh, maxsplit=1, flags=re.I)
    roh = nach_h1[1] if len(nach_h1) > 1 else roh
    roh = re.sub(r"<(script|style|nav|header|footer|form)[^>]*>.*?</\1>", " ",
                 roh, flags=re.S | re.I)
    roh = re.sub(r"<[^>]+>", " ", roh)
    roh = html.unescape(roh)
    teile = [t.strip() for t in re.split(r"(?<=[.!?])\s+|\n", roh) if t.strip()]
    gut = [t for t in teile if len(t) > 25 and not BOILERPLATE.search(t)]
    return re.sub(r"\s+", " ", " ".join(gut)).strip()[:grenze]


# ------------------------------------------------------------- Stufe 1
def sensor(args):
    urls = sitemap_urls(BASIS)
    if not urls:
        print("Keine Sitemap gefunden — Abbruch.", file=sys.stderr)
        return 2
    urls = urls[:MAX_SEITEN]
    print(f"Sensor: {len(urls)} Adressen aus der Sitemap von {BASIS}")
    seiten = {}
    with cf.ThreadPoolExecutor(max_workers=PARALLEL) as ex:
        for i, d in enumerate(ex.map(analysiere, urls), 1):
            seiten[d["url"]] = d
            if i % 25 == 0:
                print(f"  {i}/{len(urls)} …")
    MOMENTE.mkdir(exist_ok=True)
    heute = datetime.date.today().isoformat()
    ziel = MOMENTE / f"{heute}.json"
    ziel.write_text(json.dumps(
        {"stand": heute, "basis": BASIS, "anzahl": len(seiten), "seiten": seiten},
        ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"Momentaufnahme gespeichert: {ziel.relative_to(HIER)}")
    return 0


def lade(n=0):
    """n=0 neueste, n=1 vorletzte Momentaufnahme."""
    if not MOMENTE.exists():
        return None
    dateien = sorted(MOMENTE.glob("*.json"), reverse=True)
    if len(dateien) <= n:
        return None
    return json.loads(dateien[n].read_text(encoding="utf-8"))


# ------------------------------------------------------------- Stufe 2
def pruefen(args):
    jetzt = lade(0)
    if not jetzt:
        print("Keine Momentaufnahme vorhanden. Erst 'sensor' laufen lassen.", file=sys.stderr)
        return 2
    befunde = []
    for s in jetzt["seiten"].values():
        befunde += [b.dict() for b in pruefe_seite(s)]

    nach_schwere = {"kritisch": [], "hoch": [], "mittel": []}
    for b in befunde:
        nach_schwere[b["schwere"]].append(b)

    print(f"\nSTAND {jetzt['stand']} · {jetzt['anzahl']} Seiten geprüft")
    print("=" * 64)
    for stufe in ("kritisch", "hoch", "mittel"):
        gruppe = nach_schwere[stufe]
        print(f"\n{stufe.upper()}: {len(gruppe)} Befunde")
        zaehler = {}
        for b in gruppe:
            zaehler[b["regel"]] = zaehler.get(b["regel"], 0) + 1
        for regel, n in sorted(zaehler.items(), key=lambda x: -x[1]):
            beispiel = next(b for b in gruppe if b["regel"] == regel)
            print(f"  {n:>4}×  {regel:<26} z.B. {beispiel['url'].replace(BASIS, '')[:46]}")

    vorher = lade(1)
    if vorher:
        aend = vergleiche(vorher["seiten"], jetzt["seiten"])
        print(f"\nVERÄNDERUNG seit {vorher['stand']}: {len(aend)} Punkte")
        for v in aend[:20]:
            print(f"  [{v['art']:<8}] {v['url'].replace(BASIS, '')[:44]} — {v['text'][:70]}")
        if len(aend) > 20:
            print(f"  … und {len(aend) - 20} weitere")
    else:
        print("\nNoch keine Vorgänger-Momentaufnahme — Vergleich ab dem nächsten Lauf.")

    (HIER / "befunde.json").write_text(
        json.dumps({"stand": jetzt["stand"], "befunde": befunde},
                   ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\nBefunde gespeichert: befunde.json")
    return 1 if nach_schwere["kritisch"] else 0


# ------------------------------------------------------------- Stufe 3
def _titel_vorschlag(s):
    """Suchbegriff zuerst, Ort dazu, Marke zuletzt."""
    kern = (s.get("h1_text") or "").strip(" –—|·")
    if not kern:
        kern = re.sub(r"^Tanzschule[n]? Familie Bothe\s*[-–|]\s*", "",
                      s.get("titel") or "", flags=re.I).strip()
    if not kern:
        return None
    kern = kern.title() if kern.isupper() else kern
    ort = "Burgwedel" if "/bw" in s["url"] else "Hannover"
    t = f"{kern} in {ort} | Tanzschule Bothe"
    return t[:60] if len(t) > 60 else t


def _desc_vorschlag(s):
    """Beschreibung aus dem Fließtext der Seite, auf Satzgrenze gekürzt.

    Lieber keinen Vorschlag als einen schlechten: Wer Gerüsttext als
    Beschreibung einträgt, macht die Sache schlimmer als eine leere Angabe.
    """
    roh = re.sub(r"\s+", " ", s.get("auszug", "")).strip()
    if len(roh) < 60 or BOILERPLATE.search(roh[:80]):
        return None
    # Galerieseiten reihen dieselbe Bildunterschrift dutzendfach aneinander.
    # Daraus wird nie eine brauchbare Beschreibung.
    woerter = roh.lower().split()
    if len(woerter) >= 12 and len(set(woerter)) / len(woerter) < 0.55:
        return None
    text = ""
    for teil in re.split(r"(?<=[.!?])\s", roh):
        if len(text) + len(teil) + 1 > 158:
            break
        text = (text + " " + teil).strip()
    if len(text) < 60:                      # kein sauberer Satz zustande gekommen
        text = roh[:155].rsplit(" ", 1)[0] + " …"
    return text if len(text) >= 60 else None


def vorschlag(args):
    jetzt = lade(0)
    if not jetzt:
        print("Keine Momentaufnahme vorhanden.", file=sys.stderr)
        return 2
    out = []
    for s in jetzt["seiten"].values():
        if not s.get("code", "").startswith("2"):
            continue
        url = s["url"]
        if any(m in url.lower() for m in MUELL):
            out.append({"url": url, "art": "aus dem Index nehmen",
                        "hinweis": "Test- oder Altseite",
                        "vorher": s.get("titel", ""),
                        "nachher": 'Status 410 oder <meta name="robots" content="noindex">'})
            continue
        befunde = {b.regel for b in pruefe_seite(s)}
        if {"Beschreibung fehlt", "Beschreibung zu lang", "Beschreibung zu kurz"} & befunde:
            v = _desc_vorschlag(s)
            if v:
                out.append({"url": url, "art": "Beschreibung",
                            "hinweis": f"{len(s.get('desc') or '')} → {len(v)} Zeichen",
                            "vorher": (s.get("desc") or "")[:110], "nachher": v})
        if {"Marke steht vorn", "Ort fehlt im Titel", "Titel fehlt"} & befunde:
            v = _titel_vorschlag(s)
            if v and v != s.get("titel"):
                out.append({"url": url, "art": "Titel",
                            "hinweis": "Suchbegriff zuerst, Ort dazu",
                            "vorher": s.get("titel", ""), "nachher": v})

    ziel = HIER / "vorschlaege.json"
    ziel.write_text(json.dumps({"stand": jetzt["stand"], "vorschlaege": out},
                               ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(out)} Vorschläge erzeugt → vorschlaege.json")
    print("\nDiese Datei ist ein VORSCHLAG, keine Änderung. Ein Mensch gibt sie frei.\n")
    for v in out[:12]:
        print(f"  {v['art']:<22} {v['url'].replace(BASIS, '')[:40]}")
        print(f"     vorher : {v['vorher'][:88] or '—'}")
        print(f"     nachher: {v['nachher'][:88]}\n")
    if len(out) > 12:
        print(f"  … und {len(out) - 12} weitere in der Datei.")
    return 0


# ------------------------------------------------------------- Bericht
def bericht(args):
    p = HIER / "befunde.json"
    if not p.exists():
        print("Keine Befunde. Erst 'pruefen' laufen lassen.", file=sys.stderr)
        return 2
    d = json.loads(p.read_text(encoding="utf-8"))
    zaehler = {}
    for b in d["befunde"]:
        k = (b["schwere"], b["regel"])
        zaehler[k] = zaehler.get(k, 0) + 1
    zeilen = [f"# SEO-Wächter — Stand {d['stand']}", "",
              f"Insgesamt **{len(d['befunde'])} Befunde**.", "",
              "| Schwere | Regel | Anzahl |", "|---|---|---|"]
    for (schwere, regel), n in sorted(zaehler.items(), key=lambda x: (-x[1],)):
        zeilen.append(f"| {schwere} | {regel} | {n} |")
    md = "\n".join(zeilen) + "\n"
    (HIER / "bericht.md").write_text(md, encoding="utf-8")
    print(md)
    return 0


def main():
    ap = argparse.ArgumentParser(description="SEO-Wächter Tanzschulen Familie Bothe")
    sub = ap.add_subparsers(dest="befehl", required=True)
    sub.add_parser("sensor", help="Stufe 1 — Website crawlen und Momentaufnahme speichern")
    sub.add_parser("pruefen", help="Stufe 2 — Regelwerk anwenden und mit dem Vortag vergleichen")
    sub.add_parser("vorschlag", help="Stufe 3 — Korrekturvorschläge zur Freigabe erzeugen")
    sub.add_parser("bericht", help="Befunde als Markdown zusammenfassen")
    a = ap.parse_args()
    return {"sensor": sensor, "pruefen": pruefen,
            "vorschlag": vorschlag, "bericht": bericht}[a.befehl](a)


if __name__ == "__main__":
    sys.exit(main())
