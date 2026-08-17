#!/usr/bin/env python3
"""Von Hand geschriebene Titel und Beschreibungen für die Kernseiten.

Der Wächter kann Beschreibungen aus dem Seitentext ableiten — für 700 Seiten
ist das die einzig sinnvolle Methode. Für die drei Dutzend Seiten, an denen
tatsächlich Anmeldungen hängen, ist es zu wenig: dort steht als Überschrift
oft ein Werbeslogan ("Wir bringen Bewegung in euer Leben"), kein Suchbegriff.

Deshalb diese Datei. Was hier steht, hat Vorrang vor dem automatischen
Vorschlag. Alles andere bleibt automatisch.

Regeln, nach denen die Einträge gebaut sind:
  Titel        Suchbegriff zuerst, Ort dazu, Marke zuletzt, höchstens 60 Zeichen
  Beschreibung 110–160 Zeichen, ein konkreter Nutzen, kein Superlativ
"""

# Pfad (ohne Domain) -> (Titel, Beschreibung)
VORGABEN = {
 "/": (
  "Tanzschule Hannover & Burgwedel | Tanzschulen Bothe",
  "Über 220 Tanzangebote pro Woche in drei Häusern: Paartanz, Kindertanz, "
  "Hip Hop und Dance & Fitness. Eine Flatrate, erste Stunde kostenlos."),

 # --- Paartanz und Erwachsene ---------------------------------------------
 "/paartanz/": (
  "Paartanz für Erwachsene in Hannover | Tanzschule Bothe",
  "Standard, Latein, Discofox, Salsa und Hochzeitstanz in drei Häusern. Erste "
  "Stunde kostenlos, danach eine Flatrate für alle Kurse deines Levels."),
 "/bwpaartanz/": (
  "Paartanz in Burgwedel für Erwachsene | Tanzschule Bothe",
  "Standard, Latein und Discofox im Tanzhaus Burgwedel. Erste Stunde kostenlos, "
  "danach eine Flatrate für alle drei Häuser."),
 "/privatstunden/": (
  "Privatstunden Tanzen in Hannover | Tanzschule Bothe",
  "Einzelunterricht nach Terminabsprache — für Hochzeitspaare, Auffrischer und "
  "alle, die schneller vorankommen wollen. In allen drei Häusern."),
 "/tanzpartner/": (
  "Tanzpartnerbörse Hannover | Tanzschule Bothe",
  "Kostenlose Vermittlung für alle, die einen Tanzpartner suchen. Eintrag über "
  "die Bothe-Community, Vermittlung durch unser Team."),

 # --- Kinder und Jugendliche ----------------------------------------------
 "/kids2bis11/": (
  "Kindertanz in Hannover: 2 bis 11 Jahre | Tanzschule Bothe",
  "Von Windelhoppern ab 2 über Kindertanz und Ballett bis Dance4Kids. Kleine "
  "Gruppen nach Alter, eigene Auftritte, erste Stunde kostenlos."),
 "/bwkids/": (
  "Kindertanz in Burgwedel: Kids & Teens | Tanzschule Bothe",
  "Kindertanz, Ballett und Teenkurse im Tanzhaus Burgwedel — nach Alter "
  "getrennt, mit eigenen Auftritten. Erste Stunde kostenlos."),
 "/hiphopundco/": (
  "Hip Hop & Contemporary ab 12 in Hannover | Bothe",
  "Studio B: Hip Hop, Contemporary und Breakdance für Juniors ab 12 und Adults "
  "ab 16. Von Old School bis New Style, erste Stunde kostenlos."),
 "/schuelertanzkurse/": (
  "Schülertanzkurse in Hannover ab 2026 | Tanzschule Bothe",
  "30 Unterrichtseinheiten über zehn Monate: Standard, Latein und Discofox, "
  "dazu Schülerpartys, Diplomprüfung und Junioren-Galaball."),
 "/bwschuelertanzkurse/": (
  "Schülertanzkurse in Burgwedel | Tanzschule Bothe",
  "Standard, Latein und Discofox für Jugendliche im Tanzhaus Burgwedel, mit "
  "Schülerpartys und Diplomprüfung zum Abschluss."),
 "/elterntanz/": (
  "Elterntanz in Hannover und Burgwedel | Tanzschule Bothe",
  "Tanzstunden für Eltern unserer Schülerinnen und Schüler — während die Kinder "
  "tanzen, lernen Sie selbst. Eigene Gruppe, eigenes Tempo."),

 # --- Fitness und 60+ ------------------------------------------------------
 "/danceandfitness/": (
  "Dance & Fitness in Hannover ab 18 | Tanzschule Bothe",
  "Strength & Conditioning, Zumba und Solotanz für Erwachsene in drei Häusern. "
  "Ohne Partner, ohne Vorkenntnisse, erste Stunde kostenlos."),
 "/bwdanceandfitness/": (
  "Linedance & Fitness in Burgwedel | Tanzschule Bothe",
  "Linedance und Solotanz für Erwachsene im Tanzhaus Burgwedel — ohne Partner, "
  "ohne Vorkenntnisse, erste Stunde kostenlos."),
 "/tanzfit/": (
  "Tanzen ab 60 in Hannover: TANZFIT | Tanzschule Bothe",
  "Beweglichkeit, Rhythmus und Geselligkeit in der eigenen Altersgruppe. "
  "Ruhiges Tempo, feste Gruppen, erste Stunde kostenlos."),

 # --- Anlässe und Zusatzgeschäft -------------------------------------------
 "/debuetanten/": (
  "Opernball Debütanten Hannover: Training | Bothe",
  "Vorbereitung auf den Hannoverschen Opernball: Polonaise, Walzer und "
  "Umgangsformen. Anmeldung für den Opernball 2027 läuft."),
 "/gutschein/": (
  "Tanzgutscheine für Hannover verschenken | Bothe",
  "Gutscheine für alle Kurse in allen drei Tanzhäusern — zu Geburtstag, "
  "Konfirmation oder einfach so. Frei wählbarer Betrag."),
 "/firmenkurse/": (
  "Firmen-Tanzkurse in Hannover buchen | Tanzschule Bothe",
  "Tanz und Fitness als Teamevent oder festes Angebot für Mitarbeitende. "
  "Termine nach Absprache, auf Wunsch in Ihren Räumen."),
 "/kita/": (
  "Tanzen im Kindergarten: Projekte in Hannover | Bothe",
  "Wir kommen in Ihre Kita: Tanzeinheiten für Vorschulkinder, mit Kindershow "
  "als Abschluss. Termine und Umfang nach Absprache."),
 "/kindergartenprojekte/": (
  "Tanzprojekte für Kitas in Hannover | Tanzschule Bothe",
  "Kulturelle Bildung im Kita-Alltag: Tanzeinheiten in Ihrer Einrichtung, mit "
  "Kindershow zum Abschluss des Projekts."),
 "/schulkooperation/": (
  "Tanzprojekte für Schulen in Hannover | Tanzschule Bothe",
  "Kooperationen mit Schulen: Jugendliche erleben Gesellschaftstanz in "
  "parallelen Gruppen, im Unterricht oder als Projektwoche."),
 "/summerdance-erwachsene/": (
  "Summer Dance für Erwachsene in Hannover | Bothe",
  "Tanzen in den Sommerferien: offene Kurse für Erwachsene ohne feste Bindung, "
  "in Hannover und Burgwedel."),

 # --- Stützseiten ----------------------------------------------------------
 "/locations/": (
  "Tanzschulen in Hannover und Burgwedel: 3 Häuser | Bothe",
  "Tanzhaus Hannover, Tanzvilla Waldersee und Tanzhaus Burgwedel — mit Anfahrt, "
  "Parkplätzen direkt vor der Tür und Öffnungszeiten."),
 "/kontakt/": (
  "Kontakt zur Tanzschule Bothe in Hannover",
  "Telefon, E-Mail und Anfahrt zu allen drei Tanzhäusern. Persönliche Beratung "
  "Montag bis Freitag, telefonisch oder vor Ort."),
 "/faq/": (
  "Häufige Fragen zu Tanzkursen in Hannover | Bothe",
  "Antworten zu Anmeldung, Flatrate, Kündigung, Tanzpartner und passender "
  "Kleidung — die häufigsten Fragen auf einen Blick."),
 "/team/": (
  "Das Team der Tanzschulen Bothe in Hannover",
  "Unsere Tanzlehrerinnen und Tanzlehrer — alle im eigenen Haus ausgebildet, "
  "seit 1954 in dritter Generation."),
 "/vermietung/": (
  "Tanzsaal mieten in Hannover: 11 Säle | Bothe",
  "Räume für Feiern, Tagungen und Veranstaltungen in drei Häusern, bis "
  "1.800 m². Mit Technik, Bar und Catering auf Wunsch."),
 "/tickets/": (
  "Tickets für Bälle und Partys in Hannover | Bothe",
  "Karten für Winter-Galaball, Junioren-Galaball, Friday Night Party und "
  "Schülerdiscos — online buchen."),
 "/community/": (
  "Bothe Community App für Kurse und Termine",
  "Kurstermine, Anmeldung und Videoportal in einer App — die Tanzschule immer "
  "dabei, rund um die Uhr."),
 "/dassindwir/": (
  "Über die Tanzschulen Familie Bothe in Hannover",
  "Seit 1954 in dritter Generation: drei Häuser, elf Säle und rund 220 "
  "Tanzangebote pro Woche in Hannover und Burgwedel."),
 "/traditionverpflichtet/": (
  "70 Jahre Tanzschule Bothe in Hannover",
  "Von der Gründung 1954 durch Winfried Bothe bis heute — die Geschichte der "
  "Tanzschulen Familie Bothe in dritter Generation."),
 "/partner/": (
  "Partner der Tanzschulen Bothe in Hannover",
  "Mit wem wir zusammenarbeiten: Vereine, Schulen, Veranstalter und Ausstatter "
  "rund um das Tanzen in Hannover."),
 "/shop/": (
  "Tanzshop Hannover: Schuhe und Zubehör | Bothe",
  "Tanzschuhe, Pflege und Zubehör in unseren Tanzhäusern — mit Beratung und "
  "Anprobe vor Ort."),
}


# Beim Durchsehen der Seiten aufgefallen: mehrere Adressen behandeln dasselbe
# Thema. Solche Dubletten konkurrieren in der Suche gegeneinander — Google muss
# raten, welche gemeint ist, und keine gewinnt. Das lässt sich nicht durch einen
# besseren Titel lösen, sondern nur durch eine Entscheidung.
DUBLETTEN = [
 (["/schuelertanzkurse/", "/schuelertanzkurse4/", "/schuelertanzkurse_a/",
   "/schuelertanzkurse2027/", "/bwschuelerkursealt/"],
  "Fünf Adressen für Schülertanzkurse. Eine behalten, die übrigen per "
  "301-Weiterleitung darauf zeigen lassen — die Burgwedeler Variante bleibt "
  "eigenständig, weil sie einen anderen Standort bewirbt."),
 (["/kita/", "/kindergartenprojekte/"],
  "Beide Seiten beschreiben das Tanzprojekt für Kindergärten. Eine behalten, "
  "die andere weiterleiten."),
 (["/schulkooperation/", "/schulprojekte/"],
  "Beide zum Thema Schule, inhaltlich aber verschieden: /schulprojekte/ ist "
  "inzwischen ein reiner Downloadbereich. Entweder klar trennen und passend "
  "betiteln oder zusammenlegen."),
 (["/summerdance/", "/summerdance-erwachsene/"],
  "/summerdance/ trägt noch die Termine von 2019. Entweder aktualisieren oder "
  "auf die Erwachsenen-Seite weiterleiten."),
]


def hole(url: str):
    """Vorgabe für eine vollständige Adresse, falls vorhanden."""
    pfad = url.split(".de", 1)[-1] or "/"
    if not pfad.startswith("/"):
        pfad = "/" + pfad
    return VORGABEN.get(pfad)
