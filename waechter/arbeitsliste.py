#!/usr/bin/env python3
"""Macht aus 727 Vorschlägen eine Reihenfolge, die man abarbeiten kann.

727 Korrekturen sind keine Arbeitsliste, sondern ein Haufen. Entscheidend ist,
welche Seiten überhaupt Geld verdienen: eine Kursseite ohne Beschreibung kostet
Anmeldungen, eine Bildergalerie von 2019 kostet nichts.

    python3 arbeitsliste.py            # Übersicht auf der Konsole
    python3 arbeitsliste.py --csv      # zusätzlich arbeitsliste.csv
    python3 arbeitsliste.py --stufe 1  # nur die oberste Stufe
"""
import argparse, csv, json, pathlib, re, sys, datetime
from vorgaben import hole, DUBLETTEN

HIER = pathlib.Path(__file__).parent
HEUTE = datetime.date.today()

# Stufe 1 — Geldseiten. Hier entscheidet sich, ob jemand einen Kurs bucht.
GELD = [
    "paartanz", "kids2bis11", "hiphopundco", "danceandfitness", "tanzfit",
    "schuelertanzkurse", "privatstunden", "elterntanz", "debuetanten",
    "firmenkurse", "bwpaartanz", "bwkids", "bwdanceandfitness", "bwschuelerkurse",
    "kindergartenprojekte", "schulkooperation", "schulprojekte", "kita",
    "tanzpartner", "gutschein", "summerdance", "summerdance-erwachsene",
]
# Stufe 2 — Seiten, die den Abschluss stützen: Standort, Kontakt, Vertrauen.
STUETZE = [
    "locations", "kontakt", "tickets", "shop", "faq", "community", "vermietung",
    "team", "dassindwir", "traditionverpflichtet", "partner", "preise",
]
# Stufe 5 — Archiv. Wird nur angefasst, wenn oben nichts mehr offen ist.
ARCHIV = ["bildergalerie", "galerie", "coronahelden", "/category/", "/author/", "/tag/"]

ART_GEWICHT = {"Beschreibung": 3, "Titel": 2, "aus dem Index nehmen": 3}


def stufe(url: str) -> tuple:
    """(Stufennummer, Begründung) für eine Adresse."""
    p = url.lower().rstrip("/").split("/")[-1]
    voll = url.lower()

    if any(a in voll for a in ARCHIV):
        return 5, "Archiv oder Galerie"
    if any(g == p or g in p for g in GELD):
        return 1, "Kurs- und Angebotsseite"
    if any(s == p or s in p for s in STUETZE):
        return 2, "Standort, Kontakt oder Service"
    if "/event/" in voll:
        m = re.search(r"/(20\d\d)-(\d\d)-(\d\d)/?$", voll)
        if m:
            d = datetime.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
            return (3, "kommender Termin") if d >= HEUTE else (5, "vergangener Termin")
        return 3, "Veranstaltung"
    if re.search(r"20(1\d|2[0-4])", voll):
        return 5, "Beitrag aus einem Vorjahr"
    if voll.rstrip("/").endswith(".de") or voll.count("/") <= 3:
        return 1, "Startseite"
    return 4, "sonstige Seite"


def laden():
    v = HIER / "vorschlaege.json"
    if not v.exists():
        sys.exit("vorschlaege.json fehlt — erst 'waechter.py vorschlag' laufen lassen.")
    vorschlaege = json.loads(v.read_text(encoding="utf-8"))["vorschlaege"]

    b = HIER / "befunde.json"
    befunde = {}
    if b.exists():
        for f in json.loads(b.read_text(encoding="utf-8"))["befunde"]:
            befunde.setdefault(f["url"], []).append(f)
    return vorschlaege, befunde


def bauen():
    vorschlaege, befunde = laden()
    nach_url = {}
    for v in vorschlaege:
        nach_url.setdefault(v["url"], []).append(v)

    zeilen = []
    for url, vs in nach_url.items():
        v = hole(url)
        if v:
            titel, desc = v
            vs = [x for x in vs if x["art"] not in ("Titel", "Beschreibung")]
            vs = [{"art": "Titel", "quelle": "Hand", "hinweis": "kuratiert",
                   "vorher": "", "nachher": titel},
                  {"art": "Beschreibung", "quelle": "Hand", "hinweis": "kuratiert",
                   "vorher": "", "nachher": desc}] + vs
        for x in vs:
            x.setdefault("quelle", "Automat")
        st, grund = stufe(url)
        kritisch = sum(1 for f in befunde.get(url, []) if f["schwere"] == "kritisch")
        hoch = sum(1 for f in befunde.get(url, []) if f["schwere"] == "hoch")
        # Innerhalb einer Stufe zuerst das, was am meisten kaputt ist.
        gewicht = sum(ART_GEWICHT.get(v["art"], 1) for v in vs) + kritisch * 4 + hoch
        zeilen.append({
            "stufe": st, "grund": grund, "url": url,
            "kritisch": kritisch, "hoch": hoch, "gewicht": gewicht,
            "aufgaben": vs,
            "hand": bool(hole(url)),
        })
    zeilen.sort(key=lambda z: (z["stufe"], -z["gewicht"], z["url"]))
    return zeilen


def _umbruch(text, breite):
    """Einfacher Zeilenumbruch für die Konsolenausgabe."""
    zeilen, akt = [], ""
    for wort in text.split():
        if len(akt) + len(wort) + 1 > breite:
            zeilen.append(akt); akt = wort
        else:
            akt = (akt + " " + wort).strip()
    if akt:
        zeilen.append(akt)
    return zeilen


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", action="store_true", help="arbeitsliste.csv zusätzlich schreiben")
    ap.add_argument("--stufe", type=int, help="nur diese Stufe ausgeben")
    a = ap.parse_args()

    zeilen = bauen()
    if a.stufe:
        zeilen = [z for z in zeilen if z["stufe"] == a.stufe]

    namen = {1: "Geldseiten", 2: "Stützseiten", 3: "Veranstaltungen",
             4: "Sonstige", 5: "Archiv"}
    print(f"\nARBEITSLISTE — Stand {HEUTE.isoformat()}")
    print("=" * 74)
    for st in sorted({z["stufe"] for z in zeilen}):
        gruppe = [z for z in zeilen if z["stufe"] == st]
        aufgaben = sum(len(z["aufgaben"]) for z in gruppe)
        print(f"\n■ STUFE {st} — {namen[st]}: {len(gruppe)} Seiten, {aufgaben} Korrekturen")
        print("-" * 74)
        for z in gruppe[:40 if st <= 2 else 12]:
            pfad = z["url"].split(".de")[-1] or "/"
            marker = "!" * min(z["kritisch"], 3)
            print(f"  {pfad:<42} {marker:<3} {len(z['aufgaben'])} Korr. ({z['grund']})")
            for auf in z["aufgaben"]:
                q = "✎" if auf.get("quelle") == "Hand" else " "
                print(f"     {q} {auf['art']:<20} {auf['nachher'][:76]}")
        if len(gruppe) > (40 if st <= 2 else 12):
            print(f"  … und {len(gruppe) - (40 if st <= 2 else 12)} weitere Seiten")

    ges_seiten = len(zeilen)
    ges_auf = sum(len(z["aufgaben"]) for z in zeilen)
    oben = [z for z in zeilen if z["stufe"] <= 2]
    print(f"\n{'=' * 74}")
    print(f"Gesamt: {ges_seiten} Seiten, {ges_auf} Korrekturen.")
    print(f"Stufe 1 und 2 zusammen: {len(oben)} Seiten, "
          f"{sum(len(z['aufgaben']) for z in oben)} Korrekturen — das ist der Teil, "
          f"der Anmeldungen bringt.")

    print(f"\n{'=' * 74}")
    print("DUBLETTEN — lassen sich nicht durch einen Titel lösen, nur durch eine Entscheidung\n")
    for adressen, hinweis in DUBLETTEN:
        print("  " + ", ".join(adressen))
        for zeile in _umbruch(hinweis, 68):
            print("      " + zeile)
        print()

    if a.csv:
        p = HIER / "arbeitsliste.csv"
        with p.open("w", newline="", encoding="utf-8-sig") as f:
            w = csv.writer(f, delimiter=";")
            w.writerow(["Stufe", "Begründung", "Adresse", "Art", "Quelle",
                        "Vorher", "Nachher"])
            for z in zeilen:
                for auf in z["aufgaben"]:
                    w.writerow([z["stufe"], z["grund"], z["url"], auf["art"],
                                auf.get("quelle", "Automat"),
                                auf["vorher"], auf["nachher"]])
        print(f"\nCSV geschrieben: {p.name} (Semikolon-getrennt, für Excel)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
