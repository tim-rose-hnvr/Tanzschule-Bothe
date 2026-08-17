# SEO-Wächter

Ein Werkzeug, das die Website der Tanzschulen Familie Bothe täglich prüft und
technische Fehler zur Freigabe vorlegt.

Der Wächter ist die vierte Phase aus der
[Marktanalyse](../analyse/marktanalyse-hannover-vollerhebung.html). Er existiert,
weil der heutige Zustand über Jahre entstanden ist — nicht durch eine Fehl­ent­schei­dung,
sondern weil niemand regelmäßig hingeschaut hat.

## Was er nicht tut

Er ändert nichts an der Website. Er schreibt Vorschläge in eine Datei, die ein
Mensch freigibt.

Das ist keine technische Einschränkung, sondern eine bewusste Grenze: Automatisch
in großer Zahl erzeugte oder umgeschriebene Inhalte sind seit Googles Richtlinie
gegen *Scaled Content Abuse* (März 2024) ein Abstrafungsrisiko. Die belastbare
Trennlinie lautet:

| darf automatisch laufen | braucht menschliche Freigabe |
|---|---|
| Beschreibungen aus vorhandenem Seiteninhalt | Werbetexte und Tonalität |
| Schema.org-Auszeichnung | Positionierung |
| Alt-Texte, Sitemap-Pflege, Weiterleitungen | Preise |
| Prüfung auf Fehlerseiten und Ladezeit | alles, was eine Aussage über das Angebot trifft |

## Die drei Stufen

```
python3 waechter.py sensor      # 1 — crawlen, Momentaufnahme speichern
python3 waechter.py pruefen     # 2 — Regelwerk anwenden, mit Vortag vergleichen
python3 waechter.py vorschlag   # 3 — Korrekturen ausarbeiten, nicht anwenden
python3 waechter.py bericht     # Zusammenfassung als Markdown
```

**Stufe 1 — Sensor.** Liest alle Adressen aus der Sitemap und ruft jede einzeln
ab. Erfasst werden Status, Antwortzeit, Seitengewicht, Titel, Beschreibung,
Canonical, noindex, Anzahl H1 und H2, Schema-Blöcke, Open-Graph-Tags, Bilder ohne
Alt-Text und Wortzahl. Das Ergebnis landet als eine JSON-Datei pro Tag unter
`momentaufnahmen/`. Weil die in Git liegen, ist jede Veränderung der Website
rückwirkend nachvollziehbar — auch eine, die niemand angekündigt hat.

**Stufe 2 — Prüfen.** Wendet das Regelwerk aus `regeln.py` an und vergleicht mit
der Momentaufnahme des Vortags. Gemeldet werden nicht nur Regelverstöße, sondern
auch Veränderungen: neue Seiten, verschwundene Seiten, geänderte Statuscodes,
entfernte Beschreibungen, neu gesetztes noindex, geänderte Titel. Der Rückgabewert
ist 1, wenn kritische Befunde vorliegen — damit lässt sich der Lauf in eine
Pipeline hängen.

**Stufe 3 — Vorschlag.** Baut aus den fixbaren Befunden konkrete Korrekturen:
Titel nach dem Muster *Suchbegriff + Ort + Marke*, Beschreibungen aus dem
vorhandenen Seitentext auf Satzgrenze gekürzt, Kennzeichnung der Test- und
Altseiten, die aus dem Index gehören. Ergebnis ist `vorschlaege.json` mit
Vorher/Nachher je Adresse.

## Arbeitsliste — aus 727 Vorschlägen wird eine Reihenfolge

```
python3 arbeitsliste.py            # Übersicht
python3 arbeitsliste.py --stufe 1  # nur die Geldseiten
python3 arbeitsliste.py --csv      # arbeitsliste.csv für Excel
```

730 Korrekturen sind keine Arbeitsliste, sondern ein Haufen. `arbeitsliste.py`
sortiert nach dem einzigen Kriterium, das zählt — ob die Seite Anmeldungen
bringt:

| Stufe | Was | Umfang |
|---|---|---|
| 1 | Kurs- und Angebotsseiten | 33 Seiten |
| 2 | Standort, Kontakt, Service | 15 Seiten |
| 3 | kommende Veranstaltungen | |
| 4 | sonstige Seiten | |
| 5 | Archiv, Galerien, alte Beiträge | |

**Stufe 1 und 2 zusammen sind 48 Seiten mit 94 Korrekturen.** Das ist der Teil,
der sich an einem Tag erledigen lässt und den Unterschied macht. Der Rest darf
warten.

### Handvorgaben schlagen den Automaten

Für die Kernseiten stehen Titel und Beschreibung von Hand in `vorgaben.py` und
haben Vorrang. Grund: Auf diesen Seiten ist die Hauptüberschrift oft ein
Werbeslogan — „Wir bringen Bewegung in euer Leben“ — und daraus wird kein guter
Titel. In der Ausgabe sind Handvorgaben mit `✎` markiert, in der CSV steht die
Spalte *Quelle*.

### Dubletten

Beim Durchsehen sind vier Gruppen aufgefallen, die dasselbe Thema doppelt
belegen — am auffälligsten **fünf Adressen für Schülertanzkurse**. Solche
Seiten konkurrieren in der Suche gegeneinander, und keine gewinnt. Das lässt
sich nicht durch einen besseren Titel lösen, sondern nur durch eine
Entscheidung: eine behalten, die übrigen per 301 darauf weiterleiten.
`arbeitsliste.py` gibt sie am Ende aus.

## Strukturierte Daten erzeugen

```
python3 schema_bauen.py            # alles nach schema/ schreiben
python3 weiterleitungen.py --dateien
```

`schema_bauen.py` holt die 24 Termine über die Schnittstelle des
Veranstaltungskalenders (`/wp-json/tribe/events/v1/events`) und baut daraus
fertige JSON-LD-Blöcke — dazu die Organisation mit allen drei Standorten und
Course-Markup für elf Kursseiten. Ergebnis liegt in `schema/je-seite/` als
fertige `<script>`-Blöcke zum Einsetzen in den `<head>`.

**Warum das der lohnendste Einzelschritt ist:** In der Erhebung über 16 Anbieter
in Hannover nutzt Event-Markup **niemand**. Termine mit Datum und Ort direkt im
Suchergebnis wären kein Aufholen, sondern ein Vorsprung.

Der Lauf meldet nebenbei zwei Pflegelücken im Kalender: ein Termin ohne
hinterlegten Veranstaltungsort und **alle 24 ohne Preisangabe**. Ohne Preis wird
bewusst kein Angebots-Markup erzeugt — ein falscher Preis im Suchergebnis
schadet mehr, als er nützt.

Sonderfälle, die der Generator kennt: Termine „in allen drei Häusern“ bekommen
eine Ortsliste statt eines Ortes, und der Kuppelsaal im HCC ist mit Adresse
hinterlegt, weil sie im Kalender fehlt.

## Weiterleitungen für Dubletten und Index-Müll

`weiterleitungen.py` erzeugt drei Vorlagen: `weiterleitungen.htaccess` für
Apache, `weiterleitungen.csv` zum Import ins Redirection-Plugin und
`robots-ergaenzung.txt`.

- **4 Umleitungen (301)** legen die Schülertanzkurs-Dubletten zusammen, plus
  Kita und Summerdance
- **13 Sperrungen (410)** schalten Test- und Altseiten ab. 410 statt 301, weil
  eine Weiterleitung auf die Startseite Google eher verwirrt
- **1 offene Entscheidung**: /schulprojekte/ und /schulkooperation/ sind
  inhaltlich verschieden — das muss ein Mensch klären

Die robots-Ergänzung enthält ausdrücklich den Hinweis, dass robots.txt nur das
**Crawlen** verhindert, nicht das **Indexieren**: Eine bereits indexierte Seite
verschwindet dadurch nicht. Dafür braucht es 410 oder noindex.

Nichts davon wird automatisch scharf geschaltet — eine Weiterleitung ist eine
dauerhafte Entscheidung.

## Search Console — was Google zurückmeldet

```
python3 searchconsole.py abrufen     # letzte 28 Tage holen
python3 searchconsole.py vergleich   # Positionsverluste seit dem letzten Abruf
python3 searchconsole.py chancen     # Suchbegriffe auf Seite 2
```

`chancen` ist der praktisch nützlichste Befehl: Er zeigt Suchbegriffe auf den
Positionen 11 bis 20. Die werden bereits gefunden, nur zu weit hinten — von dort
ist der Weg auf Seite 1 am kürzesten. Dazu listet er Seiten mit vielen
Impressionen und schwacher Klickrate; das ist fast immer ein Titel- oder
Beschreibungsproblem, kein Ranking-Problem.

**Noch nicht gegen ein echtes Konto gelaufen.** Für die Erhebung im August 2026
lag kein Search-Console-Zugang vor. Die Datei ist geschrieben, scheitert ohne
Zugangsdaten mit einer verständlichen Meldung und folgt der dokumentierten
Schnittstelle — beim ersten echten Lauf sind trotzdem Kleinigkeiten zu erwarten
(Berechtigung des Dienstkontos, exakte Schreibweise der Property).

Die Einrichtung steht im Kopf von `searchconsole.py`. Kurzfassung: Projekt in
der Google Cloud Console, Search Console API aktivieren, Dienstkonto anlegen,
JSON-Schlüssel als `dienstkonto.json` ablegen (steht in `.gitignore`), das
Dienstkonto in der Search Console als Leser eintragen.

## Regelwerk

Definiert in `regeln.py`, nach Schwere getrennt:

- **kritisch** — Fehlerseite in der Sitemap, Titel fehlt, Beschreibung fehlt,
  indexierbare Test- oder Altseite, unerwartetes noindex
- **hoch** — Marke steht vorn im Titel, Ort fehlt im Titel, mehrere oder keine H1,
  kein Schema, Beschreibung zu lang, Antwortzeit über zwei Sekunden
- **mittel** — H2-Ebene fehlt, kein Open Graph, Bilder ohne Alt-Text,
  Seitengewicht über 200 kB, kein Canonical

Schwellenwerte stehen als Konstanten oben in `regeln.py`. Die Liste der
Müll-Adressen (`MUELL`) enthält die Muster der Test- und Altseiten, die bei der
Erhebung im August 2026 gefunden wurden.

## Einstellungen

`konfig.json`:

```json
{
  "basis": "https://www.tanzschule-bothe.de",
  "max_seiten": 400,
  "parallel": 6
}
```

Bei einem Relaunch auf die Headless-Site wird hier nur `basis` getauscht.

## Automatischer Lauf

`.github/workflows/waechter.yml` startet den Wächter täglich um 05:20 UTC und
öffnet einen Pull Request mit Momentaufnahme, Befunden und Vorschlägen. Der
Bericht wird zur Beschreibung des Pull Requests — man sieht die Lage also, bevor
man etwas anklickt.

Voraussetzung: In den Repository-Einstellungen muss unter *Actions → General →
Workflow permissions* das Öffnen von Pull Requests erlaubt sein.

## Wie die Zahlen zu lesen sind

**Antwortzeiten sind Messwerte unter eigener Last.** Der Sensor ruft mehrere
Seiten gleichzeitig ab und belastet den Server dabei selbst. Die gemessene Zeit
bis zum ersten Byte liegt dadurch systematisch über dem, was ein einzelner
Besucher erlebt. Der Effekt ist gemessen: derselbe Seitenbestand meldete mit
sechs parallelen Abrufen **286** Seiten über zwei Sekunden, mit vier Abrufen nur
noch **14**. `parallel` steht deshalb auf 4. Für belastbare Aussagen zur Ladezeit
gegenüber dem Kunden zählt die Einzelmessung, nicht der Crawl-Wert — der Wächter
ist hier gut für den *Trend*, nicht für den Absolutwert.

**Beschreibungsvorschläge kommen aus dem Seitentext, nicht aus einem Modell.**
Stufe 3 nimmt den Fließtext nach der ersten H1, wirft Kopf-, Navigations- und
Fußzeilentext heraus und kürzt auf Satzgrenze. Kommt dabei kein brauchbarer Satz
zustande, macht der Wächter **keinen** Vorschlag — eine leere Beschreibung ist
besser als eine, die Gerüsttext einträgt.

## Was noch fehlt

Der Wächter misst, was die Website aussendet — nicht, wie Google darauf reagiert.
Für echte Positionen, Suchvolumen und Klickzahlen braucht es Zugriff auf die
Google Search Console des Kontos. Sobald der vorliegt, gehört ein vierter Befehl
dazu, der die API abfragt und Positionsverluste ebenso meldet wie heute die
technischen Fehler.

Ebenfalls offen: die monatliche Wettbewerbsbeobachtung. Die Erhebung dafür liegt
bereits als `../analyse/crawl.py` vor und müsste nur auf denselben Takt gesetzt
werden.
