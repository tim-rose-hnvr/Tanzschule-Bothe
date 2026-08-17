# Tanzhaus Hannover – interaktives 3D-Modell

Ein im Browser begehbares 3D-Modell des Tanzhauses der Tanzschule Bothe,
rekonstruiert aus den zwölf Dateien des Drive-Ordners **„Fotos Tanzhaus“**:
sechs Grundriss-Renderings und sechs Fotos von Filipp Romanovskij.

Jeder Raum lässt sich anklicken und liefert Fläche, Abmessung, Bodenbelag,
Ausstattung und die zugehörigen Fotos. Acht Highlights erschließen zusätzlich
die Außenanlagen, die nur auf den Fotos zu sehen sind.

## Starten

Das Projekt braucht keinen Build-Schritt, aber wegen der ES-Module einen
lokalen Server:

```bash
python3 -m http.server 8000     # danach http://localhost:8000 öffnen
```

Alternativ gibt es eine vollständig eigenständige Einzeldatei, die sich
direkt per Doppelklick öffnen lässt – three.js, alle Module und sämtliche
Bilder sind darin eingebettet, es wird kein Netz benötigt:

```
dist/tanzhaus-3d.html          (2,5 MB)
```

Neu erzeugen lässt sie sich mit:

```bash
npm install esbuild
node tools/build-einzeldatei.mjs
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
                           Highlights, Tour, Fotos, Quellenangaben
src/building.js            erzeugt Wände, Böden, Decken und Dach aus den
                           Raum-Rechtecken – inklusive Tür-/Fensteröffnungen
src/props.js               Möblierung (Tresen, Spiegelwände, Treppen, …)
src/site.js                Außenanlagen: Garten, Terrasse, Zaun, Bäume,
                           Beschilderung, Außentreppe
src/materials.js           prozedurale Texturen (Parkett, Diele, Fliesen,
                           Rasen, Putz, Beschilderung) – ohne Bilddateien
src/controls.js            Kamerasteuerung (Umkreisen und Begehen)
src/ui.js                  Seitenleiste, Detailfenster, Lightbox, Tour
src/main.js                Szene, Licht, Auswahl, Beschriftungen
assets/fotos               die sechs Originalfotos
assets/plaene              die sechs Grundriss-Renderings
vendor/three.module.min.js three.js r169 (MIT, siehe THREE.LICENSE)
tools/                     Build- und Testskripte
```

Die Wandgeometrie wird nicht von Hand modelliert, sondern aus den
Raum-Rechtecken abgeleitet: gemeinsame Kanten zweier Räume werden zu einer
Innenwand, Kanten zum Freien zu einer Außenwand, und die in `OEFFNUNGEN`
hinterlegten Türen, Fenster und Glasfronten werden aus den Wandscheiben
herausgeschnitten. Ein neuer Raum in `data.js` genügt also, damit Wände,
Boden, Decke, Beschriftung, Trefferfläche und Listeneintrag entstehen.

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
  vor und stammen ausschließlich aus den sechs Fotos.

## Entwicklung

```bash
node tools/screenshot.mjs      # Screenshots aller Ansichten nach .shots/
node tools/debug.mjs           # Funktionstest der Zustandslogik
node tools/build-einzeldatei.mjs
```

Die Testskripte brauchen `playwright` und nutzen das im Container
vorinstallierte Chromium (`CHROMIUM_PATH` überschreibt den Pfad).

---

three.js steht unter der MIT-Lizenz (`vendor/THREE.LICENSE`). Fotos und
Grundriss-Renderings gehören der Tanzschule Bothe bzw. Filipp Romanovskij und
sind hier nur zur Darstellung des Modells eingebunden.
