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
