# Tanzhaus Hannover – interaktives 3D-Modell

Ein im Browser begehbares 3D-Modell des Tanzhauses der Tanzschule Bothe,
rekonstruiert aus den zwölf Dateien des Drive-Ordners **„Fotos Tanzhaus“**:
sechs Grundriss-Renderings und sechs Fotos von Filipp Romanovskij.

Jeder Raum lässt sich anklicken und liefert Fläche, Abmessung, Bodenbelag,
Ausstattung und die zugehörigen Fotos. Acht Highlights erschließen zusätzlich
die Außenanlagen, die nur auf den Fotos zu sehen sind.

## Lokal starten

Ein Befehl, keine Abhängigkeiten – Node.js ab Version 18 genügt:

```bash
npm start                  # startet den Server und öffnet den Browser
```

Danach läuft das Modell unter **http://localhost:8080**. Ist der Port belegt,
sucht der Server selbst den nächsten freien und nennt die Adresse. Ohne
automatischen Browserstart:

```bash
npm run serve              # nur starten, Adresse steht in der Ausgabe
node tools/serve.mjs 3000  # eigener Port
```

Der Server bindet bewusst nur auf `127.0.0.1`, ist also ausschließlich vom
eigenen Rechner erreichbar. Wer lieber etwas Vorhandenes nimmt, kommt mit
jedem statischen Server ans Ziel:

```bash
python3 -m http.server 8000
npx serve .
```

**Warum überhaupt ein Server?** Das Modell besteht aus ES-Modulen, die
Browser aus Sicherheitsgründen nicht über `file://` laden. Und die
eingebettete Google-Karte im Standortfenster kommt nur über `http(s)` an.

### Wenn localhost nicht lädt

Der Server schreibt beim Start den ausgelieferten Ordner und die
Node-Version in die Konsole und protokolliert jede Anfrage mit Statuscode.
Diese Ausgabe beantwortet die meisten Fälle unmittelbar:

| Beobachtung | Ursache | Abhilfe |
| --- | --- | --- |
| Gar keine Serverausgabe, `node` unbekannt | Node.js fehlt | [nodejs.org](https://nodejs.org) installieren – oder ganz ohne Node: `dist/tanzhaus-3d.html` doppelklicken |
| „in … liegt keine index.html“ | falscher Ordner | im Projektordner starten, dort wo `index.html` liegt |
| Browser zeigt „nicht erreichbar“ | anderer Port als erwartet | die in der Konsole genannte Adresse verwenden – bei belegtem Port zählt der Server hoch |
| Seite bleibt weiß, Konsole meldet 404 | Dateien fehlen | `git status` prüfen, ggf. `git pull` |
| Zugriff von Handy/Tablet scheitert | Server hört nur auf 127.0.0.1 | mit `node tools/serve.mjs --host` starten und die IP des Rechners aufrufen |

Ohne Node.js tut es jeder statische Server:

```bash
python3 -m http.server 8000    # Python 3
php -S localhost:8000          # PHP
npx serve .                    # Node vorhanden, aber ohne Projektinstallation
```

### Einzeldatei ohne Server

Wenn es keine Rolle spielt, dass die Live-Karte fehlt, tut es auch die
eigenständige Fassung per Doppelklick – three.js, alle Module und sämtliche
Bilder sind eingebettet, es wird kein Netz benötigt:

```
dist/tanzhaus-3d.html          (2,7 MB)
```

Neu erzeugen lässt sie sich mit:

```bash
npm install                # esbuild
npm run build
```

## Bedienung

| Eingabe | Wirkung |
| --- | --- |
| Ziehen | Modell drehen |
| Rechte Maustaste / Shift + Ziehen | Ansicht verschieben |
| Scrollen | Zoomen |
| Klick auf einen Raum | Auswahl + Infofenster |
| `W A S D` | im Modus „Begehen“ laufen |
| `Q` / `E` | tiefer / höher |
| `Shift` | schneller laufen |
| `Esc` | Auswahl aufheben |

Werkzeuge in der Fußleiste: Etagenwahl (EG / 1. OG / beide), Dach ein- und
ausblenden, Röntgenmodus (transparente Wände), Explosionsansicht
(Geschosse auseinanderziehen), Raumnamen, Highlight-Marker und eine
geführte Tour mit 13 Stationen.

## Aufbau

```
index.html                 Grundgerüst der Oberfläche
src/data.js                Datenmodell: Räume, Öffnungen, Möblierung,
                           Highlights, Tour, Fotos, Standort, Quellenangaben
src/building.js            erzeugt Wände, Böden, Decken und Dach aus den
                           Raum-Rechtecken – inklusive Tür-/Fensteröffnungen
src/props.js               Möblierung (Tresen, Spiegelwände, Treppen, …)
src/site.js                Außenanlagen: Garten, Terrasse, Zaun, Bäume,
                           Beschilderung, Außentreppe
src/materials.js           prozedurale Texturen samt abgeleiteten Normalmaps
                           (Parkett, Diele, Fliesen, Rasen, Putz, Pflaster)
src/render.js              Himmel, Umgebungsreflexion, Umgebungsverdeckung,
                           Qualitätsstufen und Leistungsüberwachung
src/standort.js            Lageplan, Google-Maps-Einbettung, Kartenlinks
src/controls.js            Kamerasteuerung (Umkreisen und Begehen)
src/ui.js                  Seitenleiste, Detailfenster, Lightbox, Tour
src/main.js                Szene, Licht, Auswahl, Beschriftungen
assets/fotos               die sechs Originalfotos
assets/plaene              die sechs Grundriss-Renderings
vendor/three.module.min.js three.js r169 (MIT, siehe THREE.LICENSE)
vendor/three-addons/       Sky, EffectComposer, GTAO (three.js-Beispiele, MIT)
tools/                     Build- und Testskripte
```

`tools/pruefe-daten.mjs` prüft das Datenmodell gegen sich selbst: überlappende
Räume, Öffnungen ohne zugehörige Wandkante, Möbel außerhalb ihres Raums,
unbekannte Foto- oder Tour-Verweise, Kameraziele die nicht auf ihren Raum
zeigen, und Obergeschossflächen ohne Auflager im Erdgeschoss. Das ist kein
Luxus: der Generator wirft bei einem Zahlendreher keinen Fehler, sondern
baut still eine falsche Wand.

Die Wandgeometrie wird nicht von Hand modelliert, sondern aus den
Raum-Rechtecken abgeleitet: gemeinsame Kanten zweier Räume werden zu einer
Innenwand, Kanten zum Freien zu einer Außenwand, und die in `OEFFNUNGEN`
hinterlegten Türen, Fenster und Glasfronten werden aus den Wandscheiben
herausgeschnitten. Ein neuer Raum in `data.js` genügt also, damit Wände,
Boden, Decke, Beschriftung, Trefferfläche und Listeneintrag entstehen.

## Bildqualität

Der Himmel wird mit dem Preetham-Modell aus `Sky` berechnet, einmalig in
eine Cubemap gerendert und dient danach als Hintergrund *und* als
Umgebungsreflexion – daher die Spiegelungen in Glas, Metall und im
versiegelten Tanzparkett. Dazu kommen Schattenwurf der Sonne aus Südwesten
und eine Umgebungsverdeckung (GTAO), die Raumecken und Anschlüsse abdunkelt.
Alle Texturen entstehen prozedural im Canvas; die Normalmaps werden per
Sobel-Filter aus der Helligkeit derselben Textur abgeleitet.

Über **Qualität** in der Fußleiste lässt sich das abstufen:

| Stufe | Umgebungsverdeckung | Mehrfachabtastung | Auflösung |
| --- | --- | --- | --- |
| Hoch | ja | 4× | bis 2× überabgetastet |
| Mittel | nein | 4× | bis 2× überabgetastet |
| Schnell | nein | – | 1× |

Bricht die Bildrate in den ersten Sekunden ein, stuft das Modell selbst
herunter und stellt die Auswahl entsprechend um.

## Quellen und Belastbarkeit

Grundlage ist ausschließlich der Drive-Ordner
[„Fotos Tanzhaus“](https://drive.google.com/drive/folders/1hVKhEqwfFCyG4Bs2DLtbEPebkY3r9zAI):

* `01./02./03. Tanzhaus 1. Etage` – drei Renderings des Erdgeschosses
* `01./02./03. Tanzhaus 1/2 Etage` – drei Renderings des Obergeschosses
* sechs Fotos (Straßenansicht, Werbestele, Garten, Terrasse, zwei Luftbilder)

Vermessungsgrundlage sind die beiden Draufsichten `03. …`; die
perspektivischen Renderings dienten der Kontrolle von Möblierung und Details.

Einschränkungen, die auch in der Anwendung unter **Quellen & Methodik**
dokumentiert sind:

* **Maßstab geschätzt.** Die Renderings sind unbemaßt. Der Maßstab ist auf
  eine Gebäudebreite von rund 30 m kalibriert (Abschätzung anhand des
  Luftbildes). Alle Maß- und Flächenangaben sind Näherungswerte.
* **Raster begradigt.** Die Draufsichten haben eine leichte Zentralprojektion;
  die Wände wurden zu einem rechtwinkligen Raster begradigt. Wandstärken und
  Achsmaße sind idealisiert.
* **Zwei Raumgruppen sind Deutung.** Räume ohne eindeutige Zuordnung –
  im Wesentlichen das rückwärtige Nordband im EG und die Kabinenzeile im OG –
  tragen im Detailfenster die Kennzeichnung „Nutzung abgeleitet“. Namen und
  Nutzung sind dort aus Bodenbelag, Zuschnitt und Lage erschlossen.
* **Etagenzuordnung aus dem Bild.** Welches Rendering welches Geschoss zeigt,
  geht aus den Dateinamen nicht eindeutig hervor. Die Zuordnung stützt sich
  darauf, dass die Serie „1. Etage“ ebenerdig an den Rasen anschließt und
  Eingang, Empfang und Küche enthält, während die Serie „1/2 Etage“ auf einer
  aufgeständerten Decke sitzt und den Treppenaustritt zeigt.
* **Außenanlagen nur aus den Fotos.** Garten, Terrasse, Balkon, Dachaufbauten,
  Fassadenfarbe, Beschilderung und Außentreppe kommen in den Renderings nicht
  vor und stammen ausschließlich aus den sechs Fotos. Der Putzton ist aus den
  Fotos gemittelt (je nach Belichtung #b12628 bis #f5582b).
* **Feine Fugenlinien.** Die Wände bestehen aus vielen aneinanderstoßenden
  Quadern. Auf 1×-Bildschirmen können deren Stoßkanten als haarfeine helle
  Striche im Putz aliasen; deshalb wird dort leicht überabgetastet. Ganz
  verschwinden sie nur mit zusammengeführter Wandgeometrie.

## Standort

Adresse, Koordinaten und Kartenlinks stehen in der Anwendung unter
**Standort & Karte**. Sie stammen *nicht* aus dem Drive-Ordner, sondern aus
öffentlichen Quellen: die Tanzschule nennt „Podbielskistr. 299 B“,
OpenStreetMap führt an derselben Stelle den Knoten „Tanzhaus Bothe, 299b“
(52.405503, 9.794793, 30655 Hannover-Groß-Buchholz).

Die Google-Karte wird als `<iframe>` nachgeladen und erscheint, sobald die
Seite über `http(s)` läuft – also unter `npm start` auf localhost. Lädt sie
nicht, bleibt der selbst gezeichnete Lageplan stehen und das Fenster nennt
den Grund: aus einer per Doppelklick geöffneten Datei (`file://`) lässt
Google Maps sich nicht einbetten, in eingebetteten Seiten mit strenger
Content-Security-Policy – etwa einer veröffentlichten Artifact-Seite – sind
Fremd-Hosts generell gesperrt. Die Kartenlinks funktionieren in jedem Fall.

Ohne Schlüssel wird `https://www.google.com/maps/embed?origin=mfe&pb=…`
angesprochen. Das ist das Ziel der Weiterleitung von
`maps.google.com/maps?…&output=embed`; direkt angesprochen, weil die
Weiterleitung selbst `X-Frame-Options: SAMEORIGIN` trägt. Die Endantwort
setzt kein `frame-ancestors`, die Einbettung ist also erlaubt. Ein Schlüssel
für die offizielle Maps Embed API lässt sich in `src/standort.js` unter
`MAPS_API_KEY` eintragen.

**Gegenprobe zur Größe:** OpenStreetMap zeichnet an dieser Adresse ein
Rechteck von rund 33 × 22 m (722 m², Weg 98115512). Das Modell folgt den
Renderings und misst 30 × 31 m. Welche Angabe stimmt, lässt sich aus den
vorliegenden Dateien nicht entscheiden – der OSM-Umriss ist aus Luftbildern
abgezeichnet, die Renderings können einen Planungsstand zeigen. Beides ist
so dokumentiert und nicht stillschweigend angeglichen.

## Entwicklung

```bash
npm start                      # lokaler Server + Browser
npm run pruefe                 # Datenmodell auf Widersprüche prüfen
node tools/screenshot.mjs      # Screenshots aller Ansichten nach .shots/
node tools/look.mjs            # feste Kamerastandpunkte nach .look/ (Bildkontrolle)
node tools/debug.mjs           # Funktionstest der Zustandslogik
node tools/fassadencheck.mjs   # Einzelbild der Südfassade für Kantenprüfung
node tools/build-einzeldatei.mjs
```

Die Testskripte brauchen `playwright` und nutzen das im Container
vorinstallierte Chromium (`CHROMIUM_PATH` überschreibt den Pfad).

---

three.js steht unter der MIT-Lizenz (`vendor/THREE.LICENSE`). Fotos und
Grundriss-Renderings gehören der Tanzschule Bothe bzw. Filipp Romanovskij und
sind hier nur zur Darstellung des Modells eingebunden.
