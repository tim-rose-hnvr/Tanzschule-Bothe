#!/usr/bin/env python3
"""Regelwerk des SEO-Wächters.

Jede Regel prüft genau ein Signal und liefert entweder None (in Ordnung) oder
einen Befund. Die Trennung nach Schwere ist bewusst:

  kritisch  — kostet unmittelbar Sichtbarkeit oder blamiert die Marke
  hoch      — deutlicher Nachteil gegenüber dem Wettbewerb
  mittel    — sollte behoben werden, drängt aber nicht

Was hier NICHT geprüft wird: ob ein Text gut ist. Der Wächter bewertet
Struktur und Technik. Inhalt, Positionierung und Preise bleiben beim Menschen —
automatisch erzeugte Texte in großer Zahl sind seit Googles Richtlinie gegen
"Scaled Content Abuse" (März 2024) ein Abstrafungsrisiko.
"""
from dataclasses import dataclass, asdict, field

TITEL_MAX = 60
TITEL_MIN = 20
DESC_MAX = 165
DESC_MIN = 70
TTFB_WARN = 1.0
KB_WARN = 200

# Seiten, die nie in den Index gehören. Treffer als Teilstring der Adresse.
MUELL = ["/test", "/testseite", "/xxx_", "/_blog", "/_style", "/_links",
         "/_menufinder", "/slider", "/voting", "/dd/", "/gw/", "alt/"]

# Marke am Titelanfang verschenkt die wertvollste Position an ein Wort,
# nach dem ohnehin niemand sucht, der die Schule noch nicht kennt.
MARKE_PRAEFIXE = ["tanzschule familie bothe", "tanzschulen familie bothe",
                  "tanzschule bothe", "bothe"]


@dataclass
class Befund:
    url: str
    regel: str
    schwere: str          # kritisch | hoch | mittel
    text: str
    ist: str = ""
    soll: str = ""
    fixbar: bool = False   # kann Stufe 3 daraus einen Vorschlag bauen?

    def dict(self):
        return asdict(self)


def _hat(seite, feld):
    return seite.get(feld) is not None


def pruefe_seite(seite: dict) -> list:
    """Alle Regeln auf eine gecrawlte Seite anwenden."""
    b, url = [], seite["url"]
    muell = any(m in url.lower() for m in MUELL)

    # --- Erreichbarkeit ---------------------------------------------------
    code = seite.get("code", "000")
    if code.startswith("5") or code == "000":
        b.append(Befund(url, "nicht erreichbar", "kritisch",
                        f"Die Seite antwortet mit Status {code}.", code, "200"))
        return b
    if code.startswith("4"):
        b.append(Befund(url, "Fehlerseite", "kritisch",
                        f"Die Seite antwortet mit Status {code}, steht aber in der Sitemap.",
                        code, "200 oder aus der Sitemap entfernen"))
        return b

    # --- Index-Müll -------------------------------------------------------
    if muell and not seite.get("noindex"):
        b.append(Befund(url, "Index-Müll", "kritisch",
                        "Test- oder Altseite ist erreichbar und indexierbar.",
                        "indexierbar", "noindex oder Status 410", fixbar=True))

    # --- Titel ------------------------------------------------------------
    titel = (seite.get("titel") or "").strip()
    if not titel:
        b.append(Befund(url, "Titel fehlt", "kritisch",
                        "Ohne Titel entscheidet Google selbst, was in der Suche steht.",
                        "leer", "Suchbegriff + Ort + Marke", fixbar=True))
    else:
        tl = titel.lower()
        if len(titel) > TITEL_MAX:
            b.append(Befund(url, "Titel zu lang", "mittel",
                            "Der Titel wird in der Suche abgeschnitten.",
                            f"{len(titel)} Zeichen", f"höchstens {TITEL_MAX}"))
        if len(titel) < TITEL_MIN:
            b.append(Befund(url, "Titel zu kurz", "hoch",
                            "Zu kurze Titel verschenken Platz für Suchbegriff und Ort.",
                            f"{len(titel)} Zeichen", f"mindestens {TITEL_MIN}"))
        if any(tl.startswith(p) for p in MARKE_PRAEFIXE) and not muell:
            b.append(Befund(url, "Marke steht vorn", "hoch",
                            "Der Titel beginnt mit dem Markennamen statt mit dem Suchbegriff.",
                            titel[:52], "Suchbegriff + Ort + Marke", fixbar=True))
        if "hannover" not in tl and "burgwedel" not in tl and not muell:
            b.append(Befund(url, "Ort fehlt im Titel", "hoch",
                            "Ohne Ortsbezug konkurriert die Seite bundesweit statt lokal.",
                            titel[:52], "Ort im Titel nennen", fixbar=True))

    # --- Beschreibung -----------------------------------------------------
    desc = (seite.get("desc") or "").strip()
    if not desc and not muell:
        b.append(Befund(url, "Beschreibung fehlt", "kritisch",
                        "Google baut sich den Suchergebnis-Text selbst zusammen.",
                        "leer", f"{DESC_MIN}–{DESC_MAX} Zeichen", fixbar=True))
    elif desc:
        if len(desc) > DESC_MAX:
            b.append(Befund(url, "Beschreibung zu lang", "hoch",
                            "Der Text wird in der Suche abgeschnitten.",
                            f"{len(desc)} Zeichen", f"höchstens {DESC_MAX}", fixbar=True))
        elif len(desc) < DESC_MIN:
            b.append(Befund(url, "Beschreibung zu kurz", "mittel",
                            "Kurze Beschreibungen nutzen den verfügbaren Platz nicht.",
                            f"{len(desc)} Zeichen", f"mindestens {DESC_MIN}", fixbar=True))

    # --- Überschriften ----------------------------------------------------
    h1 = seite.get("h1", 0)
    if h1 == 0 and not muell:
        b.append(Befund(url, "H1 fehlt", "hoch",
                        "Der Seite fehlt die Hauptüberschrift.", "0×", "genau 1×"))
    elif h1 > 1:
        b.append(Befund(url, "Mehrere H1", "hoch",
                        "Mehrere Hauptüberschriften verwischen das Thema der Seite.",
                        f"{h1}×", "genau 1×"))
    if seite.get("h2", 0) == 0 and h1 and not muell:
        b.append(Befund(url, "H2-Ebene fehlt", "mittel",
                        "Ohne Zwischenüberschriften fehlt der Seite eine Gliederung.",
                        "0×", "mindestens 1×"))

    # --- Auszeichnung -----------------------------------------------------
    if seite.get("ld", 0) == 0 and not muell:
        b.append(Befund(url, "Kein Schema", "hoch",
                        "Ohne strukturierte Daten entstehen keine Rich Results.",
                        "0 Blöcke", "Course, Event oder LocalBusiness", fixbar=True))
    if seite.get("og", 0) == 0 and not muell:
        b.append(Befund(url, "Kein Open Graph", "mittel",
                        "Geteilte Links erscheinen in sozialen Netzen ohne Bild und Text.",
                        "0 Tags", "mindestens 4", fixbar=True))

    # --- Bilder -----------------------------------------------------------
    ohne_alt = seite.get("img_ohne_alt", 0)
    if ohne_alt > 0:
        b.append(Befund(url, "Bilder ohne Alt-Text", "mittel",
                        "Bilder ohne Alternativtext sind für Suchmaschinen und "
                        "Screenreader unsichtbar.",
                        f"{ohne_alt} von {seite.get('img_gesamt', '?')}", "0", fixbar=True))

    # --- Tempo ------------------------------------------------------------
    ttfb = seite.get("ttfb")
    if ttfb is not None and ttfb > TTFB_WARN:
        b.append(Befund(url, "Langsame Antwort", "hoch" if ttfb > 2 else "mittel",
                        "Lange Wartezeit bis zum ersten Byte kostet Besucher und Ranking.",
                        f"{ttfb:.2f} s", f"unter {TTFB_WARN:.1f} s"))
    kb = seite.get("kb")
    if kb and kb > KB_WARN:
        b.append(Befund(url, "Seite zu schwer", "mittel",
                        "Großes HTML verzögert die Darstellung besonders mobil.",
                        f"{kb} kB", f"unter {KB_WARN} kB"))

    # --- Sonstiges --------------------------------------------------------
    if seite.get("noindex") and not muell:
        b.append(Befund(url, "Auf noindex gesetzt", "kritisch",
                        "Diese Seite ist von der Suche ausgeschlossen — beabsichtigt?",
                        "noindex", "indexierbar"))
    if not seite.get("canonical"):
        b.append(Befund(url, "Kein Canonical", "mittel",
                        "Ohne Canonical-Angabe können doppelte Adressen entstehen.",
                        "fehlt", "gesetzt"))
    return b


def vergleiche(alt: dict, neu: dict) -> list:
    """Was hat sich seit dem letzten Lauf verändert?"""
    aus, ein = set(alt), set(neu)
    v = []
    for u in sorted(ein - aus):
        v.append({"art": "neu", "url": u, "text": "Neue Seite aufgetaucht."})
    for u in sorted(aus - ein):
        v.append({"art": "weg", "url": u,
                  "text": "Seite ist aus der Sitemap verschwunden — Weiterleitung gesetzt?"})
    for u in sorted(aus & ein):
        a, n = alt[u], neu[u]
        if a.get("code") != n.get("code"):
            v.append({"art": "status", "url": u,
                      "text": f"Status geändert: {a.get('code')} → {n.get('code')}"})
        if bool(a.get("desc")) and not n.get("desc"):
            v.append({"art": "verlust", "url": u, "text": "Beschreibung wurde entfernt."})
        if not a.get("noindex") and n.get("noindex"):
            v.append({"art": "verlust", "url": u, "text": "Seite wurde auf noindex gesetzt."})
        at, nt = (a.get("titel") or ""), (n.get("titel") or "")
        if at and nt and at != nt:
            v.append({"art": "titel", "url": u, "text": f"Titel geändert: „{at[:44]}“ → „{nt[:44]}“"})
    return v
