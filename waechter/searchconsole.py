#!/usr/bin/env python3
"""Vierte Stufe: was Google tatsächlich zurückmeldet.

Der Wächter misst bisher nur, was die Website aussendet. Diese Datei holt die
Gegenrichtung — echte Positionen, Klicks und Impressionen aus der Google Search
Console.

    python3 searchconsole.py abrufen     # letzte 28 Tage holen und ablegen
    python3 searchconsole.py vergleich   # Positionsverluste gegenüber dem letzten Abruf
    python3 searchconsole.py chancen     # Suchbegriffe auf Seite 2 — die schnellsten Gewinne

STATUS: Diese Datei ist geschrieben, aber noch nicht gegen ein echtes Konto
gelaufen — für die Erhebung im August 2026 lag kein Search-Console-Zugang vor.
Die Abfragen folgen der dokumentierten Searchanalytics-Schnittstelle; erwarte
beim ersten Lauf trotzdem Kleinigkeiten (Berechtigung, exakte Property-URL).

Einrichtung
-----------
1. In der Google Cloud Console ein Projekt anlegen und die
   "Google Search Console API" aktivieren.
2. Ein Dienstkonto (Service Account) erstellen und einen JSON-Schlüssel
   herunterladen. Die Datei nach `waechter/dienstkonto.json` legen —
   sie steht in .gitignore und gehört NICHT ins Repository.
3. In der Search Console unter Einstellungen → Nutzer und Berechtigungen die
   E-Mail-Adresse des Dienstkontos als Nutzer mit Leserecht hinzufügen.
4. `pip install -r requirements.txt`

Die Property-URL in `konfig.json` unter "gsc_property" eintragen, exakt so, wie
sie in der Search Console steht — mit Schrägstrich am Ende, oder als
`sc-domain:tanzschule-bothe.de` bei einer Domain-Property.
"""
import argparse, json, pathlib, sys, datetime

HIER = pathlib.Path(__file__).parent
DATEN = HIER / "suchdaten"
SCHLUESSEL = HIER / "dienstkonto.json"
BEREICH = ["https://www.googleapis.com/auth/webmasters.readonly"]

KONFIG = json.loads((HIER / "konfig.json").read_text(encoding="utf-8")) \
    if (HIER / "konfig.json").exists() else {}
PROPERTY = KONFIG.get("gsc_property", "https://www.tanzschule-bothe.de/")
TAGE = KONFIG.get("gsc_tage", 28)


def dienst():
    """Verbindung aufbauen — mit klarer Ansage, was fehlt."""
    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
    except ImportError:
        sys.exit("Die Google-Bibliotheken fehlen.\n"
                 "  pip install -r requirements.txt")
    if not SCHLUESSEL.exists():
        sys.exit(f"Schlüsseldatei fehlt: {SCHLUESSEL.name}\n"
                 "Siehe Einrichtung im Kopf dieser Datei — Punkt 2 und 3.")
    anmeldung = service_account.Credentials.from_service_account_file(
        str(SCHLUESSEL), scopes=BEREICH)
    return build("searchconsole", "v1", credentials=anmeldung, cache_discovery=False)


def _abfrage(api, dimensionen, start, ende, zeilen=5000):
    antwort = api.searchanalytics().query(siteUrl=PROPERTY, body={
        "startDate": start.isoformat(),
        "endDate": ende.isoformat(),
        "dimensions": dimensionen,
        "rowLimit": zeilen,
        "dataState": "final",
    }).execute()
    return antwort.get("rows", [])


def abrufen(args):
    api = dienst()
    ende = datetime.date.today() - datetime.timedelta(days=3)   # Google liefert verzögert
    start = ende - datetime.timedelta(days=TAGE)
    print(f"Hole {PROPERTY} für {start} bis {ende} …")

    daten = {"stand": datetime.date.today().isoformat(),
             "property": PROPERTY, "von": start.isoformat(), "bis": ende.isoformat()}

    for name, dims in (("suchbegriffe", ["query"]),
                       ("seiten", ["page"]),
                       ("begriff_je_seite", ["query", "page"])):
        rohe = _abfrage(api, dims, start, ende)
        daten[name] = [{
            "schluessel": r["keys"],
            "klicks": r.get("clicks", 0),
            "impressionen": r.get("impressions", 0),
            "ctr": round(r.get("ctr", 0) * 100, 2),
            "position": round(r.get("position", 0), 1),
        } for r in rohe]
        print(f"  {name:<18} {len(rohe)} Zeilen")

    DATEN.mkdir(exist_ok=True)
    ziel = DATEN / f"{daten['stand']}.json"
    ziel.write_text(json.dumps(daten, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"Gespeichert: {ziel.relative_to(HIER)}")
    return 0


def _laden(n=0):
    if not DATEN.exists():
        return None
    dateien = sorted(DATEN.glob("*.json"), reverse=True)
    return json.loads(dateien[n].read_text(encoding="utf-8")) if len(dateien) > n else None


def vergleich(args):
    neu, alt = _laden(0), _laden(1)
    if not neu:
        sys.exit("Noch keine Suchdaten. Erst 'abrufen' laufen lassen.")
    if not alt:
        sys.exit("Nur ein Abruf vorhanden — Vergleich ab dem zweiten Lauf.")

    a = {tuple(r["schluessel"]): r for r in alt["suchbegriffe"]}
    verluste, gewinne, weg = [], [], []
    for r in neu["suchbegriffe"]:
        k = tuple(r["schluessel"])
        if k not in a:
            continue
        d = r["position"] - a[k]["position"]      # positiv = schlechter geworden
        if d >= 3 and a[k]["impressionen"] >= 30:
            verluste.append((d, k[0], a[k]["position"], r["position"], r["impressionen"]))
        elif d <= -3 and r["impressionen"] >= 30:
            gewinne.append((d, k[0], a[k]["position"], r["position"], r["impressionen"]))
    n = {tuple(r["schluessel"]) for r in neu["suchbegriffe"]}
    for k, r in a.items():
        if k not in n and r["klicks"] >= 3:
            weg.append((k[0], r["klicks"], r["position"]))

    print(f"\nVERGLEICH {alt['stand']} → {neu['stand']}")
    print("=" * 72)
    print(f"\nVERLUSTE ({len(verluste)}) — mindestens 3 Plätze schlechter")
    for d, q, vor, jetzt, imp in sorted(verluste, key=lambda x: -x[0])[:20]:
        print(f"  {d:+5.1f}  {q[:44]:<44} {vor:.1f} → {jetzt:.1f}  ({imp} Impr.)")
    print(f"\nGEWINNE ({len(gewinne)})")
    for d, q, vor, jetzt, imp in sorted(gewinne, key=lambda x: x[0])[:10]:
        print(f"  {d:+5.1f}  {q[:44]:<44} {vor:.1f} → {jetzt:.1f}  ({imp} Impr.)")
    if weg:
        print(f"\nGANZ VERSCHWUNDEN ({len(weg)}) — hatten zuletzt noch Klicks")
        for q, kl, pos in sorted(weg, key=lambda x: -x[1])[:12]:
            print(f"  {q[:52]:<52} zuletzt {kl} Klicks auf {pos:.1f}")
    return 1 if verluste else 0


def chancen(args):
    """Suchbegriffe auf Seite 2. Von dort ist der Weg nach vorn am kürzesten."""
    d = _laden(0)
    if not d:
        sys.exit("Noch keine Suchdaten. Erst 'abrufen' laufen lassen.")

    seite2 = [r for r in d["begriff_je_seite"]
              if 10.5 <= r["position"] <= 20.5 and r["impressionen"] >= 20]
    seite2.sort(key=lambda r: -r["impressionen"])

    print(f"\nCHANCEN — Suchbegriffe auf Seite 2 ({d['von']} bis {d['bis']})")
    print("=" * 78)
    print("Diese Begriffe werden bereits gefunden, nur zu weit hinten. Ein besserer\n"
          "Titel, eine Beschreibung oder ein Absatz mehr reichen hier oft aus.\n")
    print(f"{'Suchbegriff':<38}{'Pos.':>6}{'Impr.':>8}{'Klicks':>8}  Seite")
    print("-" * 78)
    for r in seite2[:30]:
        begriff, seite = r["schluessel"]
        pfad = seite.split(".de", 1)[-1] or "/"
        print(f"{begriff[:37]:<38}{r['position']:>6.1f}{r['impressionen']:>8}"
              f"{r['klicks']:>8}  {pfad[:26]}")
    if not seite2:
        print("  Keine Begriffe im Bereich Position 11–20 mit genug Impressionen.")

    schwach = [r for r in d["seiten"] if r["impressionen"] >= 100 and r["ctr"] < 1.5]
    if schwach:
        print(f"\n\nVIEL GESEHEN, WENIG GEKLICKT ({len(schwach)} Seiten)")
        print("Meist ein Titel- oder Beschreibungsproblem, kein Ranking-Problem.\n")
        for r in sorted(schwach, key=lambda x: -x["impressionen"])[:15]:
            pfad = r["schluessel"][0].split(".de", 1)[-1] or "/"
            print(f"  {pfad[:46]:<46} {r['impressionen']:>7} Impr.  {r['ctr']:>5.2f} % CTR")
    return 0


def main():
    ap = argparse.ArgumentParser(description="Search-Console-Daten für den Wächter")
    sub = ap.add_subparsers(dest="befehl", required=True)
    sub.add_parser("abrufen", help="Zeitraum holen und als Momentaufnahme ablegen")
    sub.add_parser("vergleich", help="Positionsverluste gegenüber dem letzten Abruf")
    sub.add_parser("chancen", help="Suchbegriffe auf Seite 2 und schwache Klickraten")
    a = ap.parse_args()
    return {"abrufen": abrufen, "vergleich": vergleich, "chancen": chancen}[a.befehl](a)


if __name__ == "__main__":
    sys.exit(main())
