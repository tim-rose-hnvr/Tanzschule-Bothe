#!/usr/bin/env python3
"""Vollerhebung Wettbewerb Hannover: Markenfarben, Kurse, Preise, SEO-Signale."""
import re, json, colorsys, subprocess, concurrent.futures as cf, pathlib

WURZEL = pathlib.Path(__file__).resolve().parent.parent
SP = WURZEL / "quellen"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121 Safari/537.36"

DOMAINS = {
    "tanzschule-bothe.de":   ("Tanzschulen Familie Bothe", "Tanzschule", "Hannover ×3"),
    "bothe.de":              ("Tanzschule Susanne Bothe", "Tanzschule", "Hannover"),
    "tanzschulemeiners.de":  ("ADTV Tanzschule Meiners", "Tanzschule", "Hannover Mitte"),
    "tanzschule-feeling.de": ("Tanzschule Feeling", "Tanzschule", "Hannover"),
    "move-dance.de":         ("Move & Dance", "Tanzschule", "Hannover"),
    "tanzschule-graeper.de": ("ADTV Tanzschule Bernd Gräper", "Tanzschule", "Langenhagen"),
    "jegella.de":            ("Tanzschule Jegella", "Tanzschule", "Lehrte"),
    "happyhours.de":         ("Happy Hours", "Preisführer", "Hannover"),
    "salsa-del-alma.de":     ("Salsa del Alma", "Spezialist", "Hannover"),
    "u-dance.de":            ("U-Dance", "Spezialist", "Hannover"),
    "moveandstyle.de":       ("Move & Style Dance Academy", "Urban", "Hannover"),
    "dafunk.dance":          ("Da Funk", "Urban", "Hannover"),
    "physicalpark.de":       ("Physicalpark", "Urban", "Hannover"),
    "ttc-gelb-weiss.de":     ("TTC Gelb-Weiss", "Verein", "Hannover"),
    "tanzsport-phoenix.de":  ("TSC Phoenix", "Verein", "Hannover"),
    "kressler.de":           ("Tanzschule Kressler", "Tanzschule", "Region"),
}

PFADE = ["", "/preise", "/preise.html", "/kurse", "/tanzkurse", "/kurse-und-preise",
         "/preisliste", "/anmeldung", "/tanzkurse/preise", "/index.php/kurse",
         "/de/tanzkurse-gruppen", "/tanzen/paare"]


def hol(url, t=30):
    try:
        r = subprocess.run(["curl", "-sSL", "--max-time", str(t), "-A", UA,
                            "-w", "\n@@%{http_code}", url], capture_output=True, text=True)
        b, _, c = r.stdout.rpartition("\n@@")
        return b, c.strip()
    except Exception:
        return "", "000"


def farben(html_text, basis):
    """Markenfarben: gesättigte Farben aus HTML + verlinkten Stylesheets."""
    quellen = [html_text]
    for href in re.findall(r'<link[^>]+rel=["\']stylesheet["\'][^>]*href=["\']([^"\']+)', html_text)[:4]:
        u = href if href.startswith("http") else (
            basis.rstrip("/") + "/" + href.lstrip("/") if not href.startswith("//") else "https:" + href)
        css, _ = hol(u, 20)
        quellen.append(css[:400000])
    treffer = {}
    for q in quellen:
        for c in re.findall(r"#([0-9a-fA-F]{6}|[0-9a-fA-F]{3})\b", q):
            c = c.lower()
            if len(c) == 3:
                c = "".join(ch * 2 for ch in c)
            r_, g_, b_ = (int(c[i:i + 2], 16) / 255 for i in (0, 2, 4))
            h, l, s = colorsys.rgb_to_hls(r_, g_, b_)
            # Grautöne, fast-Weiß und fast-Schwarz sind keine Markenfarben
            if s < 0.32 or l < 0.14 or l > 0.90:
                continue
            treffer["#" + c] = treffer.get("#" + c, 0) + 1
    top = sorted(treffer.items(), key=lambda x: -x[1])[:14]
    # ähnliche Farbtöne zusammenfassen, damit nicht 5 Nuancen desselben Rots kommen
    gewaehlt = []
    for hexv, _ in top:
        r_, g_, b_ = (int(hexv[i:i + 2], 16) / 255 for i in (1, 3, 5))
        h = colorsys.rgb_to_hls(r_, g_, b_)[0]
        if all(min(abs(h - h2), 1 - abs(h - h2)) > 0.06 for h2 in gewaehlt_h(gewaehlt)):
            gewaehlt.append(hexv)
        if len(gewaehlt) == 3:
            break
    return gewaehlt


def gewaehlt_h(lst):
    out = []
    for hexv in lst:
        r_, g_, b_ = (int(hexv[i:i + 2], 16) / 255 for i in (1, 3, 5))
        out.append(colorsys.rgb_to_hls(r_, g_, b_)[0])
    return out


def text_von(h):
    t = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", h, flags=re.S | re.I)
    t = re.sub(r"<[^>]+>", " ", t)
    return re.sub(r"\s+", " ", t)


def preise(txt):
    """€-Beträge mit Kontext einsammeln."""
    found = []
    for m in re.finditer(r"(.{0,85}?)(\d{1,4}(?:[.,]\d{2})?)\s*(?:€|EUR|Euro)(.{0,55})", txt):
        vor, betrag, nach = m.group(1).strip(), m.group(2), m.group(3).strip()
        try:
            v = float(betrag.replace(",", "."))
        except ValueError:
            continue
        if not (5 <= v <= 900):
            continue
        found.append({"betrag": v, "kontext": (vor[-70:] + " ⟨" + betrag + " €⟩ " + nach[:45]).strip()})
    # nach Betrag entdoppeln
    seen, out = set(), []
    for f in sorted(found, key=lambda x: x["betrag"]):
        if f["betrag"] in seen:
            continue
        seen.add(f["betrag"])
        out.append(f)
    return out[:14]


def kurse(txt):
    stile = ["Discofox", "Salsa", "Bachata", "Kizomba", "Hip Hop", "HipHop", "Hip-Hop", "Breakdance",
             "Zumba", "Linedance", "Line Dance", "West Coast Swing", "Tango", "Boogie",
             "Standard", "Latein", "Wiener Walzer", "Walzer", "Foxtrott", "Rumba", "Cha-Cha",
             "Jive", "Samba", "Ballett", "Contemporary", "Jazz", "Modern", "Pilates", "Yoga",
             "Kindertanz", "Hochzeit", "Brautpaar", "Twerk", "Dancehall", "Streetdance",
             "Welttanzprogramm", "Medaillen", "Privatstunde", "Merengue", "Tai Chi", "Burlesque"]
    return sorted({s for s in stile if re.search(r"\b" + re.escape(s), txt, re.I)})


def eine(dom):
    name, seg, ort = DOMAINS[dom]
    basis = None
    home, code = "", "000"
    for h in (f"https://www.{dom}", f"https://{dom}"):
        home, code = hol(h, 35)
        if code.startswith("2") and len(home) > 500:
            basis = h
            break
    if not basis:
        return dom, {"name": name, "segment": seg, "ort": ort, "erreichbar": False}

    d = {"name": name, "segment": seg, "ort": ort, "erreichbar": True, "basis": basis}
    t = re.search(r"<title>(.*?)</title>", home, re.S | re.I)
    d["titel"] = re.sub(r"\s+", " ", t.group(1)).strip() if t else ""
    m = re.search(r'<meta[^>]+name=["\']description["\'][^>]+content=["\'](.*?)["\']', home, re.S | re.I)
    d["desc"] = re.sub(r"\s+", " ", m.group(1)).strip() if m else ""
    d["desc_len"] = len(d["desc"])
    d["h1"] = len(re.findall(r"<h1", home, re.I))
    d["h2"] = len(re.findall(r"<h2", home, re.I))
    d["ld"] = len(re.findall(r"application/ld\+json", home, re.I))
    d["og"] = len(re.findall(r'property=["\']og:', home, re.I))
    d["webp"] = len(re.findall(r"\.webp", home, re.I))
    d["kb"] = round(len(home.encode()) / 1024)
    d["farben"] = farben(home, basis)

    # Zeitmessung getrennt, damit die CSS-Abrufe sie nicht verfälschen
    r = subprocess.run(["curl", "-sSL", "--max-time", "35", "-A", UA, "-o", "/dev/null",
                        "-w", "%{time_starttransfer}", basis], capture_output=True, text=True)
    try:
        d["ttfb"] = round(float(r.stdout), 2)
    except ValueError:
        d["ttfb"] = None

    # Unterseiten für Kurse und Preise
    volltext = text_von(home)
    besucht = []
    for p in PFADE[1:]:
        b, c = hol(basis + p, 22)
        if c.startswith("2") and len(b) > 800:
            volltext += " " + text_von(b)
            besucht.append(p)
    d["geprueft"] = besucht
    d["kurse"] = kurse(volltext)
    d["preise"] = preise(volltext)

    # Seitenzahl
    sm, c = hol(basis + "/sitemap.xml", 22)
    n = 0
    if "<loc>" in sm:
        subs = re.findall(r"<loc>([^<]+\.xml[^<]*)</loc>", sm)
        if subs:
            for s in subs[:12]:
                s2, _ = hol(s, 20)
                n += len(re.findall(r"<loc>(?![^<]*\.xml)", s2))
        else:
            n = len(re.findall(r"<loc>", sm))
    d["seiten"] = n
    return dom, d


if __name__ == "__main__":
    res = {}
    with cf.ThreadPoolExecutor(max_workers=6) as ex:
        for dom, d in ex.map(eine, DOMAINS):
            res[dom] = d
            if d.get("erreichbar"):
                print(f"{dom:<24} {str(d['farben']):<34} Kurse:{len(d['kurse']):<3} "
                      f"Preise:{len(d['preise']):<3} Seiten:{d['seiten']:<5} TTFB:{d['ttfb']}")
            else:
                print(f"{dom:<24} NICHT ERREICHBAR")
    (SP / "markt.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    print("\ngespeichert:", SP / "markt.json")
