#!/usr/bin/env python3
"""Erzeugt die strukturierten Daten, die der Website komplett fehlen.

Auf tanzschule-bothe.de steht kein einziger JSON-LD-Block. Gleichzeitig liegen
alle nötigen Angaben längst gepflegt vor: 24 Termine im Veranstaltungskalender,
drei Standorte mit Adresse, ein volles Kursprogramm.

Besonders lohnend ist das Event-Markup. In der gesamten Erhebung über 16
Anbieter in Hannover nutzt es niemand — Termine mit Datum und Ort direkt im
Suchergebnis wären also ein Alleinstellungsmerkmal, kein Aufholen.

    python3 schema_bauen.py            # alles erzeugen
    python3 schema_bauen.py --zeigen   # zusätzlich auf der Konsole ausgeben

Ergebnis liegt in `schema/`. Jede Datei ist ein fertiger Block, der in den
<head> der jeweiligen Seite gehört — eingefasst in
<script type="application/ld+json"> … </script>.
"""
import argparse, html, json, pathlib, re, subprocess, sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from vorgaben import VORGABEN

HIER = pathlib.Path(__file__).parent
ZIEL = HIER / "schema"
UA = "Mozilla/5.0 (compatible; BotheSEOWaechter/1.0)"

KONFIG = json.loads((HIER / "konfig.json").read_text(encoding="utf-8"))
BASIS = KONFIG.get("basis", "https://www.tanzschule-bothe.de")

# Aus den Veranstaltungsdaten der Website. Die Schreibweise dort ist uneinheitlich
# ("Podbielskistr. 299 b"), hier steht sie einmal sauber — genau so gehört sie in
# alle Google-Unternehmensprofile und auf jede Seite.
STANDORTE = {
    "TANZHAUS HANNOVER": dict(
        name="Tanzhaus Hannover", strasse="Podbielskistraße 299B",
        plz="30655", ort="Hannover"),
    "TANZVILLA WALDERSEE": dict(
        name="Tanzvilla Waldersee", strasse="Walderseestraße 20",
        plz="30177", ort="Hannover"),
    "TANZHAUS BURGWEDEL": dict(
        name="Tanzhaus Burgwedel", strasse="Kokenhorststraße 15",
        plz="30938", ort="Burgwedel"),
}

# Säle, in denen Bothe Gast ist. Der Kuppelsaal traegt im Kalender keine
# Adresse — hier steht sie, damit die Galaball-Termine vollstaendig sind.
FREMDE_ORTE = {
    "KUPPELSAAL / HCC": dict(name="Kuppelsaal im HCC Hannover",
                             strasse="Theodor-Heuss-Platz 1-3",
                             plz="30175", ort="Hannover"),
    "KUPPELSAAL": dict(name="Kuppelsaal im HCC Hannover",
                       strasse="Theodor-Heuss-Platz 1-3",
                       plz="30175", ort="Hannover"),
}

TELEFON = "+49-511-663766"
EMAIL = "tanzen@tanzschulen-bothe.de"

# Kursseiten, für die sich Course-Markup lohnt: Pfad -> (Bezeichnung, Zielgruppe)
KURSSEITEN = {
    "/paartanz/": ("Paartanz für Erwachsene", "Erwachsene"),
    "/bwpaartanz/": ("Paartanz Burgwedel", "Erwachsene"),
    "/kids2bis11/": ("Kindertanz 2 bis 11 Jahre", "Kinder"),
    "/bwkids/": ("Kindertanz Burgwedel", "Kinder"),
    "/hiphopundco/": ("Hip Hop und Contemporary ab 12", "Jugendliche"),
    "/schuelertanzkurse/": ("Schülertanzkurse", "Jugendliche"),
    "/bwschuelertanzkurse/": ("Schülertanzkurse Burgwedel", "Jugendliche"),
    "/danceandfitness/": ("Dance und Fitness ab 18", "Erwachsene"),
    "/bwdanceandfitness/": ("Linedance und Fitness Burgwedel", "Erwachsene"),
    "/tanzfit/": ("TANZFIT ab 60", "Erwachsene ab 60"),
    "/privatstunden/": ("Privatstunden", "alle Altersgruppen"),
}

PREIS = {"@type": "Offer", "price": "61", "priceCurrency": "EUR",
         "category": "Monatsbeitrag Worlddancing Complete"}


def text(roh: str, grenze: int = 400) -> str:
    """HTML aus den Kalendereinträgen zu sauberem Fließtext."""
    if not roh:
        return ""
    t = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", roh, flags=re.S | re.I)
    t = html.unescape(re.sub(r"<[^>]+>", " ", t))
    return re.sub(r"\s+", " ", t).strip()[:grenze]


def _platz(s: dict) -> dict:
    return {"@type": "Place", "name": s["name"],
            "address": {"@type": "PostalAddress", "streetAddress": s["strasse"],
                        "postalCode": s["plz"], "addressLocality": s["ort"],
                        "addressCountry": "DE"}}


def ort_block(venue: dict):
    """Veranstaltungsort auf die saubere Schreibweise bringen.

    Drei Fälle: eines unserer Häuser, ein Termin in allen dreien (Schema.org
    erlaubt dafür eine Liste), oder ein fremder Saal.
    """
    roh = (venue.get("venue") or "").strip().upper()
    if roh in STANDORTE:
        return _platz(STANDORTE[roh])
    if "ALLE DREI" in roh or "ALLEN DREI" in roh:
        return [_platz(s) for s in STANDORTE.values()]
    if roh in FREMDE_ORTE:
        return _platz(FREMDE_ORTE[roh])
    # Unbekannt — mit den Kalenderangaben arbeiten. Fehlt dort die Adresse,
    # meldet der Lauf das, damit es im Kalender nachgetragen werden kann.
    return _platz(dict(name=venue.get("venue") or "Tanzschulen Familie Bothe",
                       strasse=venue.get("address") or "", plz=venue.get("zip") or "",
                       ort=venue.get("city") or "Hannover"))


def hol_events():
    """Alle kommenden Termine über die Schnittstelle des Kalenders."""
    alle, seite = [], 1
    while True:
        u = f"{BASIS}/wp-json/tribe/events/v1/events?per_page=50&page={seite}"
        r = subprocess.run(["curl", "-sSL", "--max-time", "30", "-A", UA, u],
                           capture_output=True, text=True).stdout
        try:
            d = json.loads(r)
        except json.JSONDecodeError:
            break
        alle += d.get("events", [])
        if seite >= d.get("total_pages", 1):
            break
        seite += 1
    return alle


def event_schema(e: dict) -> dict:
    s = {
        "@context": "https://schema.org", "@type": "Event",
        "name": text(e.get("title"), 110),
        "startDate": (e.get("start_date") or "").replace(" ", "T"),
        "endDate": (e.get("end_date") or "").replace(" ", "T"),
        "eventStatus": "https://schema.org/EventScheduled",
        "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
        "url": e.get("url"),
        "location": ort_block(e.get("venue") or {}),
        "organizer": {"@type": "Organization", "name": "Tanzschulen Familie Bothe",
                      "url": BASIS + "/", "telephone": TELEFON},
    }
    b = text(e.get("description"))
    if b:
        s["description"] = b
    bild = (e.get("image") or {}).get("url") if isinstance(e.get("image"), dict) else None
    if bild:
        s["image"] = bild
    kosten = (e.get("cost") or "").strip()
    # Ohne Preisangabe im Kalender lieber kein Angebot behaupten. Ein falsches
    # Preis-Markup ist schlimmer als gar keines.
    if kosten:
        s["offers"] = {"@type": "Offer", "price": re.sub(r"[^\d,.]", "", kosten) or "0",
                       "priceCurrency": "EUR", "url": e.get("url"),
                       "availability": "https://schema.org/InStock"}
    return s


def organisation() -> dict:
    return {
        "@context": "https://schema.org", "@type": "DanceSchool",
        "@id": BASIS + "/#organisation",
        "name": "Tanzschulen Familie Bothe",
        "alternateName": "Tanzschule Bothe",
        "url": BASIS + "/",
        "foundingDate": "1954",
        "telephone": TELEFON, "email": EMAIL,
        "description": "Tanzschule in Hannover und Burgwedel mit drei Häusern, "
                       "elf Sälen und rund 220 Tanzangeboten pro Woche.",
        "areaServed": [{"@type": "City", "name": "Hannover"},
                       {"@type": "City", "name": "Burgwedel"}],
        "aggregateRating": {"@type": "AggregateRating", "ratingValue": "4.4",
                            "reviewCount": "300"},
        "location": [{
            "@type": "Place", "name": s["name"],
            "address": {"@type": "PostalAddress", "streetAddress": s["strasse"],
                        "postalCode": s["plz"], "addressLocality": s["ort"],
                        "addressCountry": "DE"},
        } for s in STANDORTE.values()],
        "sameAs": ["https://www.facebook.com/TanzschuleBothe/",
                   "https://www.instagram.com/tanzschulebothe/"],
    }


def kurs_schema(pfad: str, bezeichnung: str, zielgruppe: str) -> dict:
    vor = VORGABEN.get(pfad)
    return {
        "@context": "https://schema.org", "@type": "Course",
        "name": bezeichnung,
        "description": vor[1] if vor else f"{bezeichnung} bei den Tanzschulen Familie Bothe.",
        "url": BASIS + pfad,
        "provider": {"@type": "DanceSchool", "@id": BASIS + "/#organisation",
                     "name": "Tanzschulen Familie Bothe"},
        "audience": {"@type": "EducationalAudience", "audienceType": zielgruppe},
        "offers": PREIS,
        "hasCourseInstance": {
            "@type": "CourseInstance", "courseMode": "onsite",
            "location": [{"@type": "Place", "name": s["name"]} for s in STANDORTE.values()],
        },
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--zeigen", action="store_true", help="Blöcke auch ausgeben")
    a = ap.parse_args()
    ZIEL.mkdir(exist_ok=True)

    org = organisation()
    (ZIEL / "organisation.json").write_text(
        json.dumps(org, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"organisation.json      DanceSchool mit {len(org['location'])} Standorten")

    events = hol_events()
    blocks = [event_schema(e) for e in events]
    (ZIEL / "events.json").write_text(
        json.dumps(blocks, ensure_ascii=False, indent=1), encoding="utf-8")
    def hat_adresse(b):
        o = b["location"]
        o = o[0] if isinstance(o, list) else o
        return bool(o["address"]["streetAddress"])
    ohne_ort = sum(1 for b in blocks if not hat_adresse(b))
    mehrfach = sum(1 for b in blocks if isinstance(b["location"], list))
    print(f"events.json            {len(blocks)} Termine, davon {mehrfach} in allen drei Häusern"
          + (f"  ({ohne_ort} ohne Adresse — im Kalender nachpflegen)" if ohne_ort else ""))
    ohne_preis = sum(1 for b in blocks if not b.get("offers"))
    if ohne_preis:
        print(f"                       {ohne_preis} Termine ohne Preisangabe im Kalender. "
              f"Ohne Preis kein Angebots-Markup —\n"
              f"                       fuer Ticket-Termine lohnt sich das Nachtragen.")

    kurse = [kurs_schema(p, b, z) for p, (b, z) in KURSSEITEN.items()]
    (ZIEL / "kurse.json").write_text(
        json.dumps(kurse, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"kurse.json             {len(kurse)} Kursseiten")

    # Ein Block pro Seite, direkt zum Einsetzen.
    schnipsel = ZIEL / "je-seite"
    schnipsel.mkdir(exist_ok=True)
    def schreib(pfad, daten):
        name = (pfad.strip("/").replace("/", "_") or "startseite") + ".html"
        (schnipsel / name).write_text(
            '<script type="application/ld+json">\n'
            + json.dumps(daten, ensure_ascii=False, indent=1)
            + "\n</script>\n", encoding="utf-8")
    schreib("/", org)
    for k, (pfad, _) in zip(kurse, KURSSEITEN.items()):
        schreib(pfad, k)
    for b, e in zip(blocks, events):
        schreib("event_" + (e.get("slug") or str(e.get("id"))), b)
    print(f"je-seite/              {len(list(schnipsel.glob('*.html')))} fertige Blöcke")

    if a.zeigen:
        print("\n--- Beispiel Event ---")
        print(json.dumps(blocks[0], ensure_ascii=False, indent=1)[:900])

    print(f"\nHinweis: Event-Markup nutzt in Hannover kein einziger Wettbewerber.\n"
          f"Die {len(blocks)} Termine sind der schnellste Weg zu Suchergebnissen,\n"
          f"die sonst niemand hat.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
