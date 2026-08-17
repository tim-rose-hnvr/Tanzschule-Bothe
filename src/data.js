/**
 * Tanzhaus Hannover – Datenmodell
 * ------------------------------------------------------------------
 * Alle Geometrien wurden aus den sechs Grundriss-Renderings der
 * Tanzschule Bothe (Google-Drive-Ordner "Fotos Tanzhaus") ausgemessen:
 * die beiden Draufsichten "03. Tanzhaus 1. Etage" und
 * "03. Tanzhaus 1/2 Etage" dienten als Vermessungsgrundlage, die vier
 * perspektivischen Renderings zur Kontrolle von Möblierung und Details.
 * Die Außenanlagen (Garten, Terrasse, Balkon, Dach, Fassade, Beschilderung)
 * stammen aus den sechs Fotos von Filipp Romanovskij.
 *
 * Koordinatensystem (Meter, Grundriss):
 *   x: 0 = Westfassade      →  30.0 = Ostfassade (Gartenseite)
 *   y: 0 = Südfassade       →  31.16 = Nordfassade
 *      (Süd = Straße/Haupteingang, Ost = Garten)
 * In der 3D-Szene gilt: worldX = x, worldZ = -y, worldY = Höhe.
 *
 * Maßstab: die Renderings sind unbemaßt. Der Maßstab ist auf eine
 * Gebäudebreite von 30 m kalibriert (Abschätzung aus dem Luftbild).
 * Alle Flächenangaben sind daher gerundete Näherungswerte.
 */

/* ---------------------------------------------------------------- Höhen */
export const H = {
  egFloor:   0.00,   // OK Fertigfußboden EG
  egClear:   4.10,   // lichte Höhe EG
  slab:      0.40,   // Deckenstärke
  ogFloor:   4.50,   // OK Fertigfußboden 1. OG
  ogClear:   3.70,   // lichte Höhe 1. OG
  roof:      8.20,   // OK Dachdecke
  parapet:   0.75,   // Attika
  wallExt:   0.34,   // Außenwandstärke
  wallInt:   0.15,   // Innenwandstärke
};
H.levelBase = [H.egFloor, H.ogFloor];
H.levelClear = [H.egClear, H.ogClear];

/* --------------------------------------------------------- Bodenbeläge */
export const BODEN = {
  parkett:  { label: 'Tanzparkett',            farbe: 0xc79a63 },
  diele:    { label: 'dunkle Holzdiele',       farbe: 0x4a3226 },
  fliesen:  { label: 'Fliesen / Estrich',      farbe: 0x8a8f99 },
  aussen:   { label: 'Außenbelag',             farbe: 0x6f7a6a },
};

/* ------------------------------------------------------- Raumkategorien */
export const KATEGORIEN = {
  saal:          { label: 'Tanzsäle',                 farbe: 0xd8392a, css: '#d8392a' },
  gastro:        { label: 'Gastronomie & Empfang',    farbe: 0xf4b32a, css: '#f4b32a' },
  umkleide:      { label: 'Umkleiden & Garderobe',    farbe: 0x4aa3d8, css: '#4aa3d8' },
  sanitaer:      { label: 'Sanitär',                  farbe: 0x7d8fa8, css: '#7d8fa8' },
  erschliessung: { label: 'Erschließung',             farbe: 0x9c7bd8, css: '#9c7bd8' },
  service:       { label: 'Neben- & Technikräume',    farbe: 0x5f6672, css: '#5f6672' },
  aussen:        { label: 'Außenbereiche',            farbe: 0x8cc63e, css: '#8cc63e' },
};

/* ============================================================== RÄUME */
/* rects: [x1, y1, x2, y2] in Metern. Mehrere Rechtecke = zusammenhängender Raum. */

export const RAEUME = [

  /* ------------------------------- ERDGESCHOSS ------------------------------- */
  {
    id: 'eg-saal-ost', level: 0, kat: 'saal', boden: 'parkett', sicher: true,
    name: 'Großer Saal Ost',
    kurz: 'Der größte Saal des Hauses – volle Glasfront zum Garten.',
    rects: [[17.00, 9.50, 30.00, 28.45]],
    text: 'Der größte Tanzsaal im Erdgeschoss nimmt die komplette Gartenseite ein. '
        + 'Über die gesamte Ostfassade läuft eine raumhohe Pfosten-Riegel-Verglasung, die den Saal '
        + 'direkt an Terrasse und Garten anbindet – auf den Luftbildern ist genau diese Glasfront '
        + 'hinter den roten Sonnenschirmen zu erkennen. An der Nordwand sitzt eine durchgehende '
        + 'Spiegelwand, davor stehen Musikanlage und Lautsprecher.',
    merkmale: [
      'Raumhohe Glasfassade nach Osten zum Garten',
      'Durchgehende Spiegelwand an der Nordseite',
      'Direkter Übergang zur Lounge im Süden (breite Öffnung)',
      'Stehtische an der Fensterseite, Bestuhlung an den Rändern',
    ],
    fotos: ['luftbild-garten', 'garten-terrasse'],
    quelle: '03. Tanzhaus 1. Etage (Draufsicht) + 01./02. Perspektive',
  },
  {
    id: 'eg-saal-mitte', level: 0, kat: 'saal', boden: 'parkett', sicher: true,
    name: 'Saal Mitte',
    kurz: 'Schmaler Kurssaal zwischen den beiden großen Sälen.',
    rects: [[10.20, 9.50, 17.00, 28.45]],
    text: 'Der mittlere der drei Erdgeschoss-Säle ist deutlich schmaler und dadurch der klassische '
        + 'Kursraum für kleinere Gruppen. Er liegt zwischen Saal West und Saal Ost und ist zu beiden '
        + 'Seiten über Türen erschlossen, sodass sich die Ebene bei Bedarf zu einer durchgehenden '
        + 'Fläche verbinden lässt.',
    merkmale: [
      'Spiegelwand und Ballettstange an der Nordwand',
      'Türen zu Saal West und Saal Ost – Säle koppelbar',
      'Sitzbank-Zeile entlang der Westwand',
    ],
    fotos: [],
    quelle: '03. Tanzhaus 1. Etage (Draufsicht)',
  },
  {
    id: 'eg-saal-west', level: 0, kat: 'saal', boden: 'parkett', sicher: true,
    name: 'Saal West',
    kurz: 'Tanzsaal an der Westfassade mit Fensterband.',
    rects: [[0.00, 9.50, 10.20, 28.45]],
    text: 'Der westliche Saal wird über ein hohes Fensterband in der Westfassade belichtet. '
        + 'Im Rendering hängt an der Nordwand ein großformatiges Tänzer-Motiv, davor stehen '
        + 'Technikmöbel und ein Stehtisch – der Saal ist damit auch als Veranstaltungs- und '
        + 'Übungsraum möbliert.',
    merkmale: [
      'Hohes Fensterband nach Westen',
      'Wandgrafik / Tänzer-Motiv an der Stirnwand',
      'Eigener Zugang aus der Lounge',
    ],
    fotos: [],
    quelle: '03. Tanzhaus 1. Etage (Draufsicht) + 02. Perspektive',
  },
  {
    id: 'eg-lounge', level: 0, kat: 'gastro', boden: 'diele', sicher: true,
    name: 'Lounge, Bar & Bistro',
    kurz: 'Durchgehende Gastro-Zone über die gesamte Südseite.',
    rects: [
      [0.00, 4.90, 30.00, 9.50],
      [8.80, 0.00, 10.20, 4.90],
      [13.15, 0.00, 19.15, 4.90],
      [19.15, 3.75, 26.65, 4.90],
      [26.65, 0.00, 27.35, 4.90],
      [27.35, 3.15, 30.00, 4.90],
    ],
    text: 'Die gesamte Südhälfte des Erdgeschosses ist eine offene Gastronomie-Ebene mit dunklem '
        + 'Dielenboden – der optische Gegenpol zum hellen Tanzparkett der Säle. Sie verbindet '
        + 'Haupteingang, Empfang, Bar und alle drei Säle miteinander. Die Möblierung im Rendering '
        + 'reicht von Sitzgruppen mit Bänken über Stehtische bis zu einer Bistro-Zeile im Westteil.',
    merkmale: [
      'Offene Verbindung zu allen drei Sälen',
      'Sitzbank-Nischen entlang der Ostwand',
      'Stehtische und Bistro-Tischgruppen',
      'Tresen mit Zapfanlage im Westteil',
      'Dunkler Dielenboden als durchgehendes Gestaltungsmerkmal',
    ],
    fotos: [],
    quelle: '03. Tanzhaus 1. Etage (Draufsicht) + 01./02. Perspektive',
  },
  {
    id: 'eg-empfang', level: 0, kat: 'gastro', boden: 'diele', sicher: true,
    name: 'Empfang & Tresen',
    kurz: 'Anlaufpunkt direkt gegenüber dem Haupteingang.',
    rects: [[19.15, 0.00, 26.65, 3.75]],
    text: 'Gleich rechts vom Haupteingang liegt der lange Tresen mit Rückbuffet, Spüle und '
        + 'Sitzgelegenheit. Er funktioniert im Rendering gleichzeitig als Empfang der Tanzschule '
        + 'und als Bar für den Gastrobereich.',
    merkmale: [
      'Langer Tresen mit Rückwand-Buffet',
      'Sitzgruppe / Sofa im Anschluss',
      'Blickbeziehung zum Haupteingang',
    ],
    fotos: [],
    quelle: '03. Tanzhaus 1. Etage (Draufsicht), Detail Südost',
  },
  {
    id: 'eg-windfang', level: 0, kat: 'erschliessung', boden: 'fliesen', sicher: true,
    name: 'Windfang / Haupteingang',
    kurz: 'Verglaster Vorbau an der Straßenfassade.',
    rects: [[15.90, -1.80, 18.75, 0.00]],
    text: 'Der Haupteingang liegt an der Südseite zur Straße und springt als verglaster Windfang '
        + 'aus der Fassade vor. Auf den Fotos ist darüber die Leuchtwerbung "TANZHAUS HANNOVER" '
        + 'mit dem BOTHE!-Logo montiert; davor stehen Fahrradbügel und Pflanzkübel.',
    merkmale: [
      'Verglaster Vorbau mit zwei Türflügeln',
      'Leuchtschrift "TANZHAUS HANNOVER" + BOTHE!-Logo darüber',
      'Fahrradbügel und Pflanzkübel im Vorfeld',
    ],
    fotos: ['aussen-strasse', 'aussen-eingang-stele'],
    quelle: '03. Tanzhaus 1. Etage + Fotos 3/54 und 14/54',
  },
  {
    id: 'eg-treppenhaus', level: 0, kat: 'erschliessung', boden: 'diele', sicher: true,
    name: 'Treppenhaus (verglast)',
    kurz: 'Vollverglaste Treppenhalle in der Straßenfassade.',
    rects: [[4.20, 0.00, 8.80, 4.90]],
    text: 'Die Verbindung zwischen Erdgeschoss und Obergeschoss liegt im Westteil der Südfassade. '
        + 'Auf den Fotos ist sie als große, raumhoch verglaste Halle deutlich zu erkennen: '
        + 'ein heller Glaskörper links neben dem Haupteingang, in dem die Treppe frei sichtbar '
        + 'nach oben läuft.',
    merkmale: [
      'Raumhohe Verglasung über beide Geschosse',
      'Frei sichtbarer Treppenlauf in der Fassade',
      'Direkter Anschluss an die Lounge',
    ],
    fotos: ['aussen-strasse', 'aussen-eingang-stele'],
    quelle: '03. Tanzhaus 1. Etage + Fotos 3/54 und 14/54',
  },
  {
    id: 'eg-wc-damen', level: 0, kat: 'sanitaer', boden: 'fliesen', sicher: false,
    name: 'Sanitärbereich West',
    kurz: 'Gefliester Sanitärblock in der Südwestecke.',
    rects: [[0.00, 0.00, 4.20, 4.90]],
    text: 'Geschlossener, komplett geflieste Raum in der Südwestecke. Boden und Zuschnitt sprechen '
        + 'eindeutig für einen Sanitärbereich; die genaue Zuordnung ist aus dem Rendering nicht '
        + 'ablesbar.',
    merkmale: ['Durchgehender Fliesenboden', 'Zugang aus der Lounge', 'Kein Tageslicht von Süden'],
    fotos: [],
    quelle: '03. Tanzhaus 1. Etage (Draufsicht), Detail Südwest',
  },
  {
    id: 'eg-wc-vorraum', level: 0, kat: 'sanitaer', boden: 'fliesen', sicher: false,
    name: 'Sanitär-Vorraum',
    kurz: 'Vorgelagerter Waschraum.',
    rects: [[10.20, 2.75, 13.15, 4.90]],
    text: 'Vorraum zwischen Lounge und dem dahinter liegenden Sanitärraum – im Rendering als eigener '
        + 'kleiner, geflieste Zelle abgesetzt.',
    merkmale: ['Fliesenboden', 'Schleuse zur Lounge'],
    fotos: [],
    quelle: '03. Tanzhaus 1. Etage (Draufsicht)',
  },
  {
    id: 'eg-wc-herren', level: 0, kat: 'sanitaer', boden: 'fliesen', sicher: false,
    name: 'Sanitärbereich Mitte',
    kurz: 'Sanitärzelle hinter dem Vorraum.',
    rects: [[10.20, 0.00, 13.15, 2.75]],
    text: 'Der hintere Sanitärraum an der Südfassade. Im Rendering ist ein gerastertes Bodenmuster '
        + 'mit mehreren Sanitärobjekten entlang der Wand zu sehen.',
    merkmale: ['Sanitärobjekte entlang der Südwand', 'Zugang nur über den Vorraum'],
    fotos: [],
    quelle: '03. Tanzhaus 1. Etage (Draufsicht)',
  },
  {
    id: 'eg-buero', level: 0, kat: 'service', boden: 'fliesen', sicher: false,
    name: 'Nebenraum Südost',
    kurz: 'Kleiner geschlossener Raum neben dem Tresen.',
    rects: [[27.35, 0.00, 30.00, 3.15]],
    text: 'Abgetrennte Zelle in der Südostecke, direkt an den Tresen angeschlossen – der Lage nach '
        + 'ein Back-Office- bzw. Lagerraum der Gastronomie.',
    merkmale: ['Direkt hinter dem Tresen', 'Kein öffentlicher Zugang erkennbar'],
    fotos: [],
    quelle: '03. Tanzhaus 1. Etage (Draufsicht)',
  },
  {
    id: 'eg-nord-1', level: 0, kat: 'service', boden: 'fliesen', sicher: false,
    name: 'Nebenraum Nord 1',
    kurz: 'Rückwärtiger Raum hinter Saal Mitte.',
    rects: [[10.20, 28.45, 14.71, 31.16]],
    text: 'Teil des rückwärtigen Raumbandes an der Nordfassade. Diese Räume liegen hinter den Sälen '
        + 'und sind im Rendering unmöbliert mit hartem Bodenbelag dargestellt – typisch für '
        + 'Lager-, Technik- oder Umkleideräume.',
    merkmale: ['Harter Bodenbelag', 'Zugang vom Saal Mitte'],
    fotos: [],
    quelle: '03. Tanzhaus 1. Etage (Draufsicht), Nordband',
  },
  {
    id: 'eg-nord-2', level: 0, kat: 'service', boden: 'fliesen', sicher: false,
    name: 'Nebenraum Nord 2',
    kurz: 'Schmale Zelle im Nordband.',
    rects: [[14.71, 28.45, 17.00, 31.16]],
    text: 'Schmaler Raum im rückwärtigen Band an der Nordfassade.',
    merkmale: ['Harter Bodenbelag', 'Kleinster Raum des Nordbandes'],
    fotos: [],
    quelle: '03. Tanzhaus 1. Etage (Draufsicht), Nordband',
  },
  {
    id: 'eg-nord-3', level: 0, kat: 'service', boden: 'fliesen', sicher: false,
    name: 'Nebenraum Nord 3',
    kurz: 'Zelle im Nordband hinter Saal Ost.',
    rects: [[17.00, 28.45, 19.15, 31.16]],
    text: 'Weiterer Raum des rückwärtigen Bandes, hinter dem Großen Saal Ost gelegen.',
    merkmale: ['Harter Bodenbelag', 'Zugang vom Großen Saal Ost'],
    fotos: [],
    quelle: '03. Tanzhaus 1. Etage (Draufsicht), Nordband',
  },
  {
    id: 'eg-nord-4', level: 0, kat: 'service', boden: 'fliesen', sicher: false,
    name: 'Technik- / Lagerraum Nord',
    kurz: 'Großer rückwärtiger Raum an der Nordostecke.',
    rects: [[19.15, 28.45, 30.00, 31.16]],
    text: 'Der größte Raum des rückwärtigen Bandes zieht sich über die ganze Nordostecke. '
        + 'Im Rendering ist er unmöbliert – der Größe und Lage nach der zentrale Lager- und '
        + 'Technikraum des Erdgeschosses.',
    merkmale: ['Größter Nebenraum der Ebene', 'Fenster in der Nordfassade', 'Zugang vom Großen Saal Ost'],
    fotos: [],
    quelle: '03. Tanzhaus 1. Etage (Draufsicht), Nordband',
  },

  /* ------------------------------ 1. OBERGESCHOSS ---------------------------- */
  {
    id: 'og-saal-ost', level: 1, kat: 'saal', boden: 'parkett', sicher: true,
    name: 'Großer Saal Ost (OG)',
    kurz: 'Hauptsaal des Obergeschosses mit Balkonzugang.',
    rects: [[17.00, 9.50, 30.00, 28.70]],
    text: 'Der Hauptsaal im Obergeschoss liegt genau über dem großen Saal des Erdgeschosses und '
        + 'öffnet sich ebenfalls mit einer durchgehenden Glasfront nach Osten. Dahinter liegt der '
        + 'Balkon, der auf den Luftbildern über die ganze Gartenfassade läuft. An der Nordseite '
        + 'schließt eine Bar-/Tresenzeile an, an der Südseite eine Bistro-Reihe mit Hochtischen.',
    merkmale: [
      'Glasfront nach Osten mit Zugang zum Balkon',
      'Tresenzeile an der Nordwand',
      'Bistro-Hochtische an der Südkante',
      'Spiegel- und Technikwand im Norden',
    ],
    fotos: ['luftbild-balkon', 'luftbild-garten'],
    quelle: '03. Tanzhaus 1/2 Etage (Draufsicht) + Fotos 49/54 und 50/54',
  },
  {
    id: 'og-saal-sued', level: 1, kat: 'saal', boden: 'parkett', sicher: true,
    name: 'Saal Südost (OG)',
    kurz: 'Querliegender Saal an der Straßenfassade.',
    rects: [[14.71, 0.00, 30.00, 9.50]],
    text: 'Quer über die Südostecke gelegter Saal mit Fensterband zur Straße und zur Gartenseite. '
        + 'Er ist über den Mittelflur und direkt aus dem großen Saal erschlossen.',
    merkmale: [
      'Fensterband nach Süden zur Straße',
      'Fenster nach Osten zum Garten',
      'Direkte Verbindung zum Großen Saal Ost',
    ],
    fotos: ['aussen-strasse'],
    quelle: '03. Tanzhaus 1/2 Etage (Draufsicht)',
  },
  {
    id: 'og-saal-nw', level: 1, kat: 'saal', boden: 'parkett', sicher: true,
    name: 'Saal Nordwest (OG)',
    kurz: 'Kompakter Kurssaal in der Nordwestecke.',
    rects: [[0.00, 20.05, 10.20, 28.45]],
    text: 'Kompakter Saal in der Nordwestecke mit Fensterband nach Westen. An der Stirnwand hängt '
        + 'im Rendering wieder ein Tänzer-Motiv, daneben steht ein Technikmöbel für die Musikanlage.',
    merkmale: ['Fensterband nach Westen', 'Wandgrafik an der Nordwand', 'Eigene Musikanlage'],
    fotos: [],
    quelle: '03. Tanzhaus 1/2 Etage (Draufsicht)',
  },
  {
    id: 'og-saal-west', level: 1, kat: 'saal', boden: 'parkett', sicher: true,
    name: 'Saal West (OG)',
    kurz: 'Langgestreckter Saal an der Westfassade.',
    rects: [[0.00, 5.50, 10.20, 20.05]],
    text: 'Der langgestreckte Saal an der Westfassade ist der zweitgrößte Raum des Obergeschosses. '
        + 'Er wird über ein durchgehendes Fensterband belichtet; an der Westwand steht im Rendering '
        + 'eine Waschtisch-/Technikzeile.',
    merkmale: [
      'Durchgehendes Fensterband nach Westen',
      'Wand-/Technikzeile an der Westseite',
      'Verbindungstür zum Saal Nordwest',
    ],
    fotos: [],
    quelle: '03. Tanzhaus 1/2 Etage (Draufsicht)',
  },
  {
    id: 'og-flur', level: 1, kat: 'erschliessung', boden: 'diele', sicher: true,
    name: 'Mittelflur',
    kurz: 'Rückgrat des Obergeschosses – verbindet alle Säle.',
    rects: [[14.71, 9.50, 17.00, 31.16], [12.80, 9.50, 14.71, 14.71]],
    text: 'Der Mittelflur läuft in Nord-Süd-Richtung durch das gesamte Obergeschoss und erschließt '
        + 'sämtliche Säle sowie die Umkleidezeile. Er hat – wie die Lounge im Erdgeschoss – einen '
        + 'dunklen Dielenboden und ist an den Wänden mit Stehtischen als Wartezone möbliert.',
    merkmale: [
      'Durchgehende Nord-Süd-Achse über die ganze Ebene',
      'Dunkler Dielenboden wie in der Lounge',
      'Stehtische als Wartezone entlang der Wand',
      'Erschließt alle fünf Umkleiden',
    ],
    fotos: [],
    quelle: '03. Tanzhaus 1/2 Etage (Draufsicht)',
  },
  {
    id: 'og-umkleide-1', level: 1, kat: 'umkleide', boden: 'fliesen', sicher: false,
    name: 'Umkleide 1',
    kurz: 'Nördlichste Kabine der Umkleidezeile.',
    rects: [[10.20, 25.79, 14.71, 31.16]],
    text: 'Erste Kabine der fünfteiligen Zeile zwischen Mittelflur und den Westsälen. Alle Kabinen '
        + 'haben im Rendering denselben harten, gerasterten Bodenbelag und je eine Tür zum Flur '
        + 'und zum angrenzenden Saal.',
    merkmale: ['Tür zum Mittelflur', 'Tür zum Saal Nordwest', 'Harter, gerasterter Bodenbelag'],
    fotos: [],
    quelle: '03. Tanzhaus 1/2 Etage (Draufsicht), Mittelband',
  },
  {
    id: 'og-umkleide-2', level: 1, kat: 'umkleide', boden: 'fliesen', sicher: false,
    name: 'Umkleide 2',
    kurz: 'Zweite Kabine der Umkleidezeile.',
    rects: [[10.20, 22.11, 14.71, 25.79]],
    text: 'Zweite Kabine der Zeile, beidseitig erschlossen.',
    merkmale: ['Tür zum Mittelflur', 'Tür zum Saal Nordwest'],
    fotos: [],
    quelle: '03. Tanzhaus 1/2 Etage (Draufsicht), Mittelband',
  },
  {
    id: 'og-umkleide-3', level: 1, kat: 'umkleide', boden: 'fliesen', sicher: false,
    name: 'Umkleide 3',
    kurz: 'Mittlere Kabine der Umkleidezeile.',
    rects: [[10.20, 18.18, 14.71, 22.11]],
    text: 'Mittlere Kabine der Zeile, zwischen Mittelflur und Saal West.',
    merkmale: ['Tür zum Mittelflur', 'Tür zum Saal West'],
    fotos: [],
    quelle: '03. Tanzhaus 1/2 Etage (Draufsicht), Mittelband',
  },
  {
    id: 'og-umkleide-4', level: 1, kat: 'umkleide', boden: 'fliesen', sicher: false,
    name: 'Umkleide 4',
    kurz: 'Vierte Kabine der Umkleidezeile.',
    rects: [[10.20, 14.71, 14.71, 18.18]],
    text: 'Vierte Kabine der Zeile, zwischen Mittelflur und Saal West.',
    merkmale: ['Tür zum Mittelflur', 'Tür zum Saal West'],
    fotos: [],
    quelle: '03. Tanzhaus 1/2 Etage (Draufsicht), Mittelband',
  },
  {
    id: 'og-umkleide-5', level: 1, kat: 'umkleide', boden: 'fliesen', sicher: false,
    name: 'Umkleide 5',
    kurz: 'Südlichste, schmalere Kabine.',
    rects: [[10.20, 9.50, 12.80, 14.71]],
    text: 'Die südlichste Kabine ist schmaler als die übrigen – hier weitet sich der Mittelflur nach '
        + 'Westen auf und bildet die Wartezone vor den Sälen.',
    merkmale: ['Schmalste Kabine der Zeile', 'Flur weitet sich davor auf'],
    fotos: [],
    quelle: '03. Tanzhaus 1/2 Etage (Draufsicht), Mittelband',
  },
  {
    id: 'og-warte', level: 1, kat: 'gastro', boden: 'diele', sicher: true,
    name: 'Wartebereich & Kinderecke',
    kurz: 'Aufenthaltszone am Treppenaustritt.',
    rects: [[10.20, 0.00, 14.71, 9.50]],
    text: 'Direkt am Treppenaustritt im Obergeschoss liegt eine Aufenthaltszone mit Sitzgruppen und '
        + 'Stehtischen. Im Rendering sind dort außerdem Spielzeug und niedrige Sitzelemente '
        + 'dargestellt – der Wartebereich für begleitende Eltern ist also bewusst mit einer '
        + 'Kinderecke ausgestattet.',
    merkmale: [
      'Sitzgruppen und Stehtische am Treppenaustritt',
      'Spielecke für Kinder',
      'Verteiler zwischen Treppenhaus, Flur und Saal Südost',
    ],
    fotos: [],
    quelle: '03. Tanzhaus 1/2 Etage (Draufsicht), Detail Süd',
  },
  {
    id: 'og-garderobe', level: 1, kat: 'umkleide', boden: 'diele', sicher: true,
    name: 'Garderobe (OG)',
    kurz: 'Garderobenzeile am Kopf des großen Saals.',
    rects: [[17.00, 28.70, 25.70, 31.16]],
    text: 'Am nördlichen Kopfende des großen Saals liegt eine offene Garderobenzone mit einer Reihe '
        + 'beleuchteter Garderobenschränke an der Rückwand. Sie ist zum Saal hin offen und über '
        + 'den Mittelflur erreichbar.',
    merkmale: [
      'Reihe beleuchteter Garderobenschränke',
      'Zum Großen Saal Ost offen',
      'Dunkler Dielenboden',
    ],
    fotos: [],
    quelle: '03. Tanzhaus 1/2 Etage (Draufsicht), Detail Nord',
  },
  {
    id: 'og-lager-no', level: 1, kat: 'service', boden: 'fliesen', sicher: false,
    name: 'Nebenraum Nordost (OG)',
    kurz: 'Abgetrennter Raum in der Nordostecke.',
    rects: [[25.70, 28.70, 30.00, 31.16]],
    text: 'Abgeschlossener, unmöblierter Raum in der Nordostecke hinter der Garderobe – der Lage '
        + 'nach Lager oder Technik.',
    merkmale: ['Unmöbliert im Rendering', 'Zugang über die Garderobe'],
    fotos: [],
    quelle: '03. Tanzhaus 1/2 Etage (Draufsicht)',
  },
  {
    id: 'og-treppenhaus', level: 1, kat: 'erschliessung', boden: 'diele', sicher: true,
    name: 'Treppenhaus (OG)',
    kurz: 'Oberer Treppenaustritt in der Glasfassade.',
    rects: [[4.20, 0.00, 10.20, 5.50]],
    text: 'Der obere Teil der verglasten Treppenhalle. Von hier aus verteilt sich der Verkehr in den '
        + 'Wartebereich und weiter in den Mittelflur.',
    merkmale: ['Anschluss an die verglaste Fassade', 'Austritt in den Wartebereich'],
    fotos: ['aussen-strasse'],
    quelle: '03. Tanzhaus 1/2 Etage (Draufsicht) + Foto 3/54',
  },
  {
    id: 'og-lager-sw', level: 1, kat: 'service', boden: 'diele', sicher: false,
    name: 'Nebenraum Südwest (OG)',
    kurz: 'Raum in der Südwestecke neben der Treppe.',
    rects: [[0.00, 0.00, 4.20, 5.50]],
    text: 'Unmöblierter Raum in der Südwestecke direkt neben dem Treppenhaus, mit kleinem Fenster '
        + 'zur Straße.',
    merkmale: ['Kleines Fenster nach Süden', 'Zugang über das Treppenhaus'],
    fotos: [],
    quelle: '03. Tanzhaus 1/2 Etage (Draufsicht)',
  },
  {
    id: 'og-balkon', level: 1, kat: 'aussen', boden: 'aussen', sicher: true,
    name: 'Balkon über dem Garten',
    kurz: 'Umlaufender Stahlbalkon an der Gartenfassade.',
    rects: [[30.00, 2.00, 32.60, 24.00]],
    text: 'Auf den Luftbildern läuft ein Stahlbalkon mit filigranem Geländer über die gesamte '
        + 'Gartenfassade des Obergeschosses und zieht sich um die Südwestecke herum. Er liegt '
        + 'direkt über der Terrasse mit den roten Sonnenschirmen und ist aus dem großen Saal '
        + 'zugänglich.',
    merkmale: [
      'Stahlkonstruktion mit Seil-/Stabgeländer',
      'Über die gesamte Gartenfassade',
      'Direkter Austritt aus dem Großen Saal Ost',
      'Liegt über der überdachten Terrasse',
    ],
    fotos: ['luftbild-balkon', 'luftbild-garten', 'garten-terrasse'],
    quelle: 'Fotos 49/54, 50/54 und 20/54 (nicht in den Renderings enthalten)',
  },
];

/* ================================================ ÖFFNUNGEN (Türen/Glas) */
/* ax:'x' → Wand verläuft in y-Richtung bei x=at;  ax:'y' → Wand in x-Richtung bei y=at */

export const OEFFNUNGEN = [
  /* --- EG: Fassade --- */
  { level:0, ax:'x', at:30.00, a: 9.80, b:28.10, sill:0.05, top:3.70, t:'glass'  },
  { level:0, ax:'x', at:30.00, a: 5.30, b: 9.20, sill:0.05, top:2.90, t:'glass'  },
  { level:0, ax:'x', at: 0.00, a:10.60, b:27.60, sill:0.85, top:3.10, t:'window' },
  { level:0, ax:'x', at: 0.00, a: 5.40, b: 9.10, sill:0.85, top:2.60, t:'window' },
  { level:0, ax:'x', at: 0.00, a: 0.60, b: 3.60, sill:1.40, top:2.40, t:'window' },
  { level:0, ax:'y', at: 0.00, a:19.60, b:26.20, sill:0.85, top:2.80, t:'window' },
  { level:0, ax:'y', at: 0.00, a:15.90, b:18.75, sill:0.00, top:2.90, t:'glass'  },
  { level:0, ax:'y', at:-1.80, a:16.30, b:18.35, sill:0.00, top:2.40, t:'door'   },
  { level:0, ax:'y', at: 0.00, a: 4.40, b: 8.60, sill:0.00, top:3.80, t:'glass'  },
  { level:0, ax:'y', at: 0.00, a: 0.60, b: 3.40, sill:1.30, top:2.40, t:'window' },
  { level:0, ax:'y', at: 0.00, a:27.60, b:29.40, sill:1.30, top:2.40, t:'window' },
  { level:0, ax:'y', at:31.16, a:20.20, b:23.20, sill:1.60, top:2.60, t:'window' },
  { level:0, ax:'y', at:31.16, a:25.20, b:28.60, sill:1.60, top:2.60, t:'window' },
  /* --- EG: innen --- */
  { level:0, ax:'y', at: 9.50, a: 2.20, b: 3.60, sill:0, top:2.30, t:'door'    },
  { level:0, ax:'y', at: 9.50, a:12.00, b:13.40, sill:0, top:2.30, t:'door'    },
  { level:0, ax:'y', at: 9.50, a:19.60, b:22.40, sill:0, top:2.70, t:'opening' },
  { level:0, ax:'y', at: 9.50, a:26.00, b:28.40, sill:0, top:2.70, t:'opening' },
  { level:0, ax:'x', at:10.20, a:12.00, b:13.60, sill:0, top:2.30, t:'door'    },
  { level:0, ax:'x', at:10.20, a:24.00, b:25.60, sill:0, top:2.30, t:'door'    },
  { level:0, ax:'x', at:17.00, a:12.00, b:13.60, sill:0, top:2.30, t:'door'    },
  { level:0, ax:'x', at:17.00, a:24.00, b:25.60, sill:0, top:2.30, t:'door'    },
  { level:0, ax:'y', at:28.45, a:11.40, b:12.30, sill:0, top:2.10, t:'door'    },
  { level:0, ax:'y', at:28.45, a:15.30, b:16.20, sill:0, top:2.10, t:'door'    },
  { level:0, ax:'y', at:28.45, a:17.60, b:18.50, sill:0, top:2.10, t:'door'    },
  { level:0, ax:'y', at:28.45, a:21.00, b:22.00, sill:0, top:2.10, t:'door'    },
  { level:0, ax:'y', at: 4.90, a: 1.20, b: 2.20, sill:0, top:2.10, t:'door'    },
  { level:0, ax:'y', at: 4.90, a:11.20, b:12.20, sill:0, top:2.10, t:'door'    },
  { level:0, ax:'y', at: 2.75, a:11.20, b:12.20, sill:0, top:2.10, t:'door'    },
  { level:0, ax:'x', at: 8.80, a: 1.60, b: 2.80, sill:0, top:2.10, t:'door'    },
  { level:0, ax:'y', at: 3.75, a:21.00, b:24.80, sill:0, top:2.70, t:'opening' },
  { level:0, ax:'y', at: 3.15, a:28.20, b:29.20, sill:0, top:2.10, t:'door'    },

  /* --- OG: Fassade --- */
  { level:1, ax:'x', at:30.00, a:10.00, b:28.20, sill:0.05, top:3.30, t:'glass'  },
  { level:1, ax:'x', at:30.00, a: 1.20, b: 9.00, sill:0.90, top:2.90, t:'window' },
  { level:1, ax:'x', at: 0.00, a: 6.20, b:19.60, sill:0.90, top:2.80, t:'window' },
  { level:1, ax:'x', at: 0.00, a:20.60, b:27.80, sill:0.90, top:2.80, t:'window' },
  { level:1, ax:'x', at: 0.00, a: 1.00, b: 4.60, sill:1.30, top:2.30, t:'window' },
  { level:1, ax:'y', at: 0.00, a:15.60, b:29.00, sill:0.90, top:2.80, t:'window' },
  { level:1, ax:'y', at: 0.00, a: 4.40, b: 8.60, sill:0.00, top:3.30, t:'glass'  },
  { level:1, ax:'y', at: 0.00, a:11.00, b:13.60, sill:0.90, top:2.60, t:'window' },
  { level:1, ax:'y', at: 0.00, a: 0.60, b: 3.40, sill:1.30, top:2.30, t:'window' },
  { level:1, ax:'y', at:31.16, a:18.00, b:24.00, sill:1.60, top:2.50, t:'window' },
  /* --- OG: innen --- */
  { level:1, ax:'y', at: 9.50, a:15.10, b:16.60, sill:0, top:2.30, t:'door'    },
  { level:1, ax:'y', at: 9.50, a:18.00, b:20.60, sill:0, top:2.70, t:'opening' },
  { level:1, ax:'y', at: 9.50, a:11.00, b:12.40, sill:0, top:2.30, t:'door'    },
  { level:1, ax:'x', at:14.71, a: 2.00, b: 3.40, sill:0, top:2.30, t:'door'    },
  { level:1, ax:'x', at:10.20, a: 1.60, b: 3.20, sill:0, top:2.70, t:'opening' },
  { level:1, ax:'x', at: 4.20, a: 1.40, b: 2.40, sill:0, top:2.10, t:'door'    },
  { level:1, ax:'y', at: 5.50, a: 6.00, b: 7.40, sill:0, top:2.30, t:'door'    },
  { level:1, ax:'y', at:20.05, a: 3.00, b: 4.60, sill:0, top:2.30, t:'door'    },
  { level:1, ax:'x', at:10.20, a:27.40, b:28.30, sill:0, top:2.10, t:'door'    },
  { level:1, ax:'x', at:10.20, a:23.20, b:24.10, sill:0, top:2.10, t:'door'    },
  { level:1, ax:'x', at:10.20, a:19.40, b:20.30, sill:0, top:2.10, t:'door'    },
  { level:1, ax:'x', at:10.20, a:15.80, b:16.70, sill:0, top:2.10, t:'door'    },
  { level:1, ax:'x', at:10.20, a:11.60, b:12.50, sill:0, top:2.10, t:'door'    },
  { level:1, ax:'x', at:14.71, a:27.00, b:27.90, sill:0, top:2.10, t:'door'    },
  { level:1, ax:'x', at:14.71, a:23.60, b:24.50, sill:0, top:2.10, t:'door'    },
  { level:1, ax:'x', at:14.71, a:19.80, b:20.70, sill:0, top:2.10, t:'door'    },
  { level:1, ax:'x', at:14.71, a:16.10, b:17.00, sill:0, top:2.10, t:'door'    },
  { level:1, ax:'x', at:12.80, a:11.60, b:12.50, sill:0, top:2.10, t:'door'    },
  { level:1, ax:'x', at:17.00, a:12.00, b:13.60, sill:0, top:2.30, t:'door'    },
  { level:1, ax:'x', at:17.00, a:22.00, b:23.60, sill:0, top:2.30, t:'door'    },
  { level:1, ax:'x', at:17.00, a:29.30, b:30.60, sill:0, top:2.70, t:'opening' },
  { level:1, ax:'y', at:28.70, a:18.50, b:24.50, sill:0, top:2.70, t:'opening' },
  { level:1, ax:'x', at:25.70, a:29.40, b:30.30, sill:0, top:2.10, t:'door'    },
];

/* ============================================================ MÖBLIERUNG */
/* Deklarative Einrichtung je Raum. Wird von props.js in Geometrie übersetzt. */

export const MOEBEL = [
  /* --- EG --- */
  { room:'eg-saal-ost',   type:'spiegelwand', wand:'n', von:18.0, bis:29.0 },
  { room:'eg-saal-ost',   type:'stange',      wand:'n', von:18.0, bis:29.0 },
  { room:'eg-saal-ost',   type:'musikmoebel', at:[19.6, 28.0], rot:0 },
  { room:'eg-saal-ost',   type:'boxen',       at:[18.2, 27.9] },
  { room:'eg-saal-ost',   type:'boxen',       at:[29.0, 27.9] },
  { room:'eg-saal-ost',   type:'stehtisch',   at:[29.0, 26.6] },
  { room:'eg-saal-ost',   type:'stehtisch',   at:[29.0, 14.0] },
  { room:'eg-saal-ost',   type:'stuhlreihe',  von:[17.6, 10.4], bis:[17.6, 16.0], n:6, rot:90 },
  { room:'eg-saal-ost',   type:'pendel',      at:[23.5, 19.0], n:2 },

  { room:'eg-saal-mitte', type:'spiegelwand', wand:'n', von:10.7, bis:16.5 },
  { room:'eg-saal-mitte', type:'stange',      wand:'n', von:10.7, bis:16.5 },
  { room:'eg-saal-mitte', type:'musikmoebel', at:[13.6, 28.0], rot:0 },
  { room:'eg-saal-mitte', type:'bankzeile',   von:[10.6, 12.0], bis:[10.6, 22.0], rot:90 },
  { room:'eg-saal-mitte', type:'pendel',      at:[13.6, 19.0], n:2 },

  { room:'eg-saal-west',  type:'spiegelwand', wand:'n', von:0.6,  bis:9.6 },
  { room:'eg-saal-west',  type:'stange',      wand:'n', von:0.6,  bis:9.6 },
  { room:'eg-saal-west',  type:'wandbild',    wand:'n', at:4.5,   w:1.6 },
  { room:'eg-saal-west',  type:'musikmoebel', at:[8.6, 28.0], rot:0 },
  { room:'eg-saal-west',  type:'stehtisch',   at:[6.4, 27.4] },
  { room:'eg-saal-west',  type:'pendel',      at:[5.1, 19.0], n:2 },

  { room:'eg-lounge',     type:'tresen',      rect:[4.9, 6.0, 8.6, 6.9], rueck:true },
  { room:'eg-lounge',     type:'tischgruppe', at:[1.9, 8.2] },
  { room:'eg-lounge',     type:'tischgruppe', at:[1.9, 6.3] },
  { room:'eg-lounge',     type:'tischgruppe', at:[3.9, 8.2] },
  { room:'eg-lounge',     type:'tischgruppe', at:[3.9, 6.3] },
  { room:'eg-lounge',     type:'stehtisch',   at:[9.5, 6.6] },
  { room:'eg-lounge',     type:'stehtisch',   at:[12.4, 6.6] },
  { room:'eg-lounge',     type:'stehtisch',   at:[16.2, 6.9] },
  { room:'eg-lounge',     type:'stehtisch',   at:[21.5, 6.6] },
  { room:'eg-lounge',     type:'stehtisch',   at:[24.5, 6.6] },
  { room:'eg-lounge',     type:'bank4',       at:[18.6, 8.5] },
  { room:'eg-lounge',     type:'bank4',       at:[20.6, 8.5] },
  { room:'eg-lounge',     type:'bank4',       at:[22.6, 8.5] },
  { room:'eg-lounge',     type:'nische',      at:[28.9, 8.4], rot:90 },
  { room:'eg-lounge',     type:'nische',      at:[28.9, 6.9], rot:90 },
  { room:'eg-lounge',     type:'nische',      at:[28.9, 5.5], rot:90 },
  { room:'eg-lounge',     type:'pflanze',     at:[14.0, 5.4] },
  { room:'eg-lounge',     type:'pendel',      at:[15.0, 7.4], n:3 },

  { room:'eg-empfang',    type:'tresen',      rect:[19.6, 2.4, 26.2, 3.4], rueck:true },
  { room:'eg-empfang',    type:'sofa',        at:[22.8, 0.9], rot:0 },
  { room:'eg-empfang',    type:'sofa',        at:[25.6, 1.8], rot:90 },

  { room:'eg-treppenhaus',type:'treppe',      rect:[5.2, 0.6, 7.8, 4.3], richtung:'n' },
  { room:'eg-wc-damen',   type:'sanitaer',    wand:'s', von:0.6, bis:3.6 },
  { room:'eg-wc-herren',  type:'sanitaer',    wand:'s', von:10.6, bis:12.8 },
  { room:'eg-wc-vorraum', type:'waschtisch',  wand:'e', at:3.9,  w:1.6 },
  { room:'eg-nord-4',     type:'regal',       wand:'n', von:20.0, bis:24.0 },
  { room:'eg-windfang',   type:'pflanze',     at:[16.3, -1.3] },
  { room:'eg-windfang',   type:'pflanze',     at:[18.4, -1.3] },

  /* --- OG --- */
  { room:'og-saal-ost',   type:'tresen',      rect:[17.6, 27.6, 24.4, 28.4], rueck:false },
  { room:'og-saal-ost',   type:'musikmoebel', at:[25.6, 28.0], rot:0 },
  { room:'og-saal-ost',   type:'spiegelwand', wand:'n', von:25.9, bis:29.4 },
  { room:'og-saal-ost',   type:'stange',      wand:'w', von:11.0, bis:27.0 },
  { room:'og-saal-ost',   type:'stehtisch',   at:[29.0, 26.6] },
  { room:'og-saal-ost',   type:'stehtisch',   at:[29.0, 13.0] },
  { room:'og-saal-ost',   type:'bank4',       at:[19.8, 10.4] },
  { room:'og-saal-ost',   type:'bank4',       at:[22.0, 10.4] },
  { room:'og-saal-ost',   type:'bank4',       at:[24.2, 10.4] },
  { room:'og-saal-ost',   type:'pendel',      at:[23.5, 19.0], n:2 },
  { room:'og-saal-ost',   type:'pflanze',     at:[29.3, 10.2] },

  { room:'og-saal-sued',  type:'spiegelwand', wand:'n', von:17.6, bis:29.4 },
  { room:'og-saal-sued',  type:'stange',      wand:'n', von:17.6, bis:29.4 },
  { room:'og-saal-sued',  type:'musikmoebel', at:[15.6, 1.2], rot:90 },
  { room:'og-saal-sued',  type:'pendel',      at:[22.0, 4.7], n:2 },

  { room:'og-saal-nw',    type:'spiegelwand', wand:'n', von:0.6, bis:9.6 },
  { room:'og-saal-nw',    type:'stange',      wand:'n', von:0.6, bis:9.6 },
  { room:'og-saal-nw',    type:'wandbild',    wand:'n', at:4.5, w:1.6 },
  { room:'og-saal-nw',    type:'musikmoebel', at:[8.6, 28.0], rot:0 },
  { room:'og-saal-nw',    type:'stehtisch',   at:[6.4, 27.4] },
  { room:'og-saal-nw',    type:'pendel',      at:[5.1, 24.2], n:1 },

  { room:'og-saal-west',  type:'stange',      wand:'w', von:7.0, bis:19.0 },
  { room:'og-saal-west',  type:'waschtisch',  wand:'w', at:8.4, w:2.2 },
  { room:'og-saal-west',  type:'musikmoebel', at:[1.4, 6.4], rot:90 },
  { room:'og-saal-west',  type:'pendel',      at:[5.1, 13.0], n:2 },

  { room:'og-flur',       type:'stehtisch',   at:[15.6, 27.4] },
  { room:'og-flur',       type:'stehtisch',   at:[15.6, 24.2] },
  { room:'og-flur',       type:'stehtisch',   at:[15.6, 20.6] },
  { room:'og-flur',       type:'stehtisch',   at:[15.6, 17.0] },
  { room:'og-flur',       type:'stehtisch',   at:[15.6, 13.4] },
  { room:'og-flur',       type:'stehtisch',   at:[15.6, 10.4] },
  { room:'og-flur',       type:'pendel',      at:[15.9, 20.0], n:3 },

  { room:'og-garderobe',  type:'spinde',      von:[18.0, 30.4], bis:[24.6, 30.4], n:5 },
  { room:'og-warte',      type:'sofa',        at:[13.4, 3.6], rot:270 },
  { room:'og-warte',      type:'stehtisch',   at:[13.2, 5.6] },
  { room:'og-warte',      type:'spielecke',   at:[12.0, 1.0] },
  { room:'og-warte',      type:'pflanze',     at:[10.7, 1.0] },
  { room:'og-treppenhaus',type:'treppenauge', rect:[5.2, 0.6, 7.8, 4.3] },

  { room:'og-umkleide-1', type:'umkleidebank', wand:'n' },
  { room:'og-umkleide-2', type:'umkleidebank', wand:'n' },
  { room:'og-umkleide-3', type:'umkleidebank', wand:'n' },
  { room:'og-umkleide-4', type:'umkleidebank', wand:'n' },
  { room:'og-umkleide-5', type:'umkleidebank', wand:'n' },
];

/* ============================================================= HIGHLIGHTS */
/* Interaktive Marker mit Bezug zu den Fotos. pos = [x, y, höhe] in Metern. */

export const HIGHLIGHTS = [
  {
    id: 'poi-fassade', nr: 1, name: 'Rote Fassade & Leuchtwerbung',
    pos: [17.4, -3.4, 6.6], level: 0,
    kurz: 'Das Erkennungszeichen: kräftig rot verputzter Baukörper.',
    text: 'Das Tanzhaus ist ein zweigeschossiger Flachdachbau mit kräftig rot-orange verputzter '
        + 'Fassade. Über dem Eingang sitzt die Leuchtschrift "TANZHAUS HANNOVER", darunter das '
        + 'BOTHE!-Logo. An der Straße steht zusätzlich eine hohe rote Werbestele mit demselben '
        + 'Schriftzug. Auffällig sind die schmalen, hochformatigen Fensterschlitze im Kontrast zu '
        + 'den großen Glasflächen von Treppenhaus und Saalfassade.',
    merkmale: [
      'Zweigeschossiger Flachdachbau, roter Putz',
      'Leuchtschrift "TANZHAUS HANNOVER" über dem Eingang',
      'Freistehende Werbestele an der Zufahrt',
      'Vorgelagerter Parkplatz mit Pflasterbelag',
    ],
    fotos: ['aussen-strasse', 'aussen-eingang-stele'],
    quelle: 'Fotos 3/54 und 14/54 (Filipp Romanovskij)',
  },
  {
    id: 'poi-eingang', nr: 2, name: 'Haupteingang & Treppenhalle',
    pos: [8.0, -2.6, 3.2], level: 0,
    kurz: 'Verglaste Treppenhalle neben dem Eingang.',
    text: 'Der Haupteingang liegt mittig in der Straßenfassade. Links davon öffnet sich die über '
        + 'beide Geschosse verglaste Treppenhalle – von außen ist der Treppenlauf komplett '
        + 'sichtbar. Rechts vom Eingang steht auf den Fotos der BOTHE!-Firmenwagen, davor '
        + 'Fahrradbügel und Pflanzkübel.',
    merkmale: [
      'Vollverglaste Treppenhalle über zwei Geschosse',
      'Zweiflügelige Eingangstür mit Vordach',
      'Fahrradbügel und Pflanzkübel im Vorfeld',
    ],
    fotos: ['aussen-strasse', 'aussen-eingang-stele'],
    quelle: 'Fotos 3/54 und 14/54',
  },
  {
    id: 'poi-garten', nr: 3, name: 'Garten mit Liegestühlen',
    pos: [37.5, 14.0, 1.6], level: 0,
    kurz: 'Große Rasenfläche mit roten Liegestühlen und Biertischen.',
    text: 'Östlich des Gebäudes liegt ein großzügiger Garten: Rasenfläche mit roten Liegestühlen, '
        + 'Holzkisten als Beistelltische, langen Bank-Tisch-Kombinationen und einer Reihe hoher '
        + 'Palmen entlang der Terrasse. Der Garten ist zur Nachbarschaft hin mit einem '
        + 'Metallzaun eingefasst und von altem Baumbestand gerahmt.',
    merkmale: [
      'Rote Liegestühle auf der Rasenfläche',
      'Bank-Tisch-Kombinationen für größere Gruppen',
      'Palmen und Kübelpflanzen entlang der Terrasse',
      'Metallzaun als Einfassung, alter Baumbestand',
    ],
    fotos: ['garten-liegestuehle', 'garten-terrasse', 'luftbild-garten'],
    quelle: 'Fotos 18/54, 20/54 und 49/54',
  },
  {
    id: 'poi-terrasse', nr: 4, name: 'Terrasse mit Sonnenschirmen',
    pos: [32.4, 12.0, 2.9], level: 0,
    kurz: 'Gepflasterte Terrasse direkt an der Saalfassade.',
    text: 'Zwischen Glasfassade und Rasen liegt eine gepflasterte Terrasse, die mit großen roten '
        + 'Sonnenschirmen überdeckt ist. Bestuhlung und Tische stehen direkt vor den Glastüren '
        + 'des großen Saals – Saal und Außenbereich lassen sich damit zu einer Fläche verbinden.',
    merkmale: [
      'Große rote Sonnenschirme über der Sitzfläche',
      'Direkt an der Glasfassade des großen Saals',
      'Palmen als Raumteiler zum Rasen',
    ],
    fotos: ['luftbild-garten', 'garten-terrasse', 'luftbild-balkon'],
    quelle: 'Fotos 49/54, 20/54 und 50/54',
  },
  {
    id: 'poi-balkon', nr: 5, name: 'Balkon im 1. OG',
    pos: [32.4, 20.0, 6.0], level: 1,
    kurz: 'Stahlbalkon über die ganze Gartenfassade.',
    text: 'Im Obergeschoss läuft ein schmaler Stahlbalkon über die gesamte Gartenfassade und um die '
        + 'Ecke weiter. Das Geländer ist filigran ausgeführt, der Balkon liegt direkt über der '
        + 'Terrasse und dient dem großen Saal des Obergeschosses als Außenfläche.',
    merkmale: [
      'Durchlaufender Stahlbalkon mit Stabgeländer',
      'Zugang aus dem Großen Saal Ost (OG)',
      'Über der überdachten Terrasse',
    ],
    fotos: ['luftbild-balkon', 'luftbild-garten'],
    quelle: 'Fotos 50/54 und 49/54',
  },
  {
    id: 'poi-dach', nr: 6, name: 'Flachdach & Lichtkuppeln',
    pos: [15.0, 20.0, 9.6], level: 1,
    kurz: 'Lichtkuppeln, Lüftung und Fluchtleiter auf dem Dach.',
    text: 'Das Luftbild zeigt das Flachdach mit umlaufender Attika, mehreren quadratischen '
        + 'Lichtkuppeln über den Sälen, Lüftungsaufbauten, einer Satellitenschüssel auf hohem '
        + 'Mast und einer weißen Steigleiter an der Gartenfassade.',
    merkmale: [
      'Flachdach mit umlaufender Attika',
      'Quadratische Lichtkuppeln über den Sälen',
      'Lüftungsaufbauten und Satellitenmast',
      'Weiße Steigleiter an der Ostfassade',
    ],
    fotos: ['luftbild-garten', 'luftbild-balkon'],
    quelle: 'Fotos 49/54 und 50/54',
  },
  {
    id: 'poi-glasfront', nr: 7, name: 'Glasfront zum Garten',
    pos: [30.6, 19.0, 2.4], level: 0,
    kurz: 'Pfosten-Riegel-Fassade über die gesamte Ostseite.',
    text: 'Die Gartenseite ist über beide Geschosse großflächig verglast. Im Erdgeschoss öffnet sich '
        + 'der große Saal raumhoch zur Terrasse, im Obergeschoss setzt sich die Verglasung als '
        + 'Fensterband hinter dem Balkon fort. Auf dem Luftbild ist die dunkle Pfosten-Riegel-'
        + 'Konstruktion mit den Spiegelungen der Bäume gut zu erkennen.',
    merkmale: [
      'Pfosten-Riegel-Fassade über beide Geschosse',
      'Raumhohe Türen vom Saal auf die Terrasse',
      'Dunkle Rahmenprofile',
    ],
    fotos: ['luftbild-garten', 'luftbild-balkon', 'garten-terrasse'],
    quelle: 'Fotos 49/54, 50/54 und 20/54',
  },
  {
    id: 'poi-aussentreppe', nr: 8, name: 'Außentreppe an der Nordseite',
    pos: [27.0, 33.2, 2.6], level: 0,
    kurz: 'Rote Stahltreppe als zweiter Rettungsweg.',
    text: 'An der Nordostecke ist auf dem Straßenfoto eine rote Stahltreppe zu sehen, die vom '
        + 'Obergeschoss ins Freie führt – der zweite bauliche Rettungsweg des Hauses.',
    merkmale: ['Rote Stahlkonstruktion', 'Verbindet 1. OG mit dem Außenbereich'],
    fotos: ['aussen-strasse'],
    quelle: 'Foto 3/54 (rechter Bildrand)',
  },
];

/* ================================================================== FOTOS */

export const FOTOS = {
  'aussen-strasse': {
    src: 'assets/fotos/aussen-strasse.jpg',
    titel: 'Straßenansicht von Südwesten',
    cap: 'Das Tanzhaus von der Zufahrt: roter Baukörper, verglaste Treppenhalle links, '
       + 'Haupteingang mit Leuchtschrift rechts daneben, rote Außentreppe am rechten Bildrand.',
  },
  'aussen-eingang-stele': {
    src: 'assets/fotos/aussen-eingang-stele.jpg',
    titel: 'Werbestele & Eingang',
    cap: 'Die rote Werbestele „TANZHAUS HANNOVER / BOTHE!" an der Zufahrt, dahinter der '
       + 'Haupteingang mit dem verglasten Treppenhaus.',
  },
  'garten-liegestuehle': {
    src: 'assets/fotos/garten-liegestuehle.jpg',
    titel: 'Garten mit Liegestühlen',
    cap: 'Rasenfläche mit roten Liegestühlen und Bank-Tisch-Kombinationen; im Hintergrund '
       + 'die Terrasse und der Balkon des Obergeschosses.',
  },
  'garten-terrasse': {
    src: 'assets/fotos/garten-terrasse.jpg',
    titel: 'Terrasse & Gartenfassade',
    cap: 'Blick auf die Gartenfassade: Sonnenschirme über der Terrasse, Palmen, rechts die '
       + 'große Pfosten-Riegel-Verglasung des Saals.',
  },
  'luftbild-garten': {
    src: 'assets/fotos/luftbild-garten.jpg',
    titel: 'Luftbild – Garten und Terrasse',
    cap: 'Von oben: Flachdach mit Lichtkuppeln und Satellitenmast, Balkon über der Terrasse, '
       + 'rote Sonnenschirme, Rasen mit Liegestühlen und Biertischgarnituren.',
  },
  'luftbild-balkon': {
    src: 'assets/fotos/luftbild-balkon.jpg',
    titel: 'Luftbild – Balkon & Glasfassade',
    cap: 'Der Balkon läuft über die gesamte Gartenfassade und um die Ecke; rechts die '
       + 'zweigeschossige Glasfront, links die schmalen Fensterschlitze.',
  },
};

export const PLAENE = [
  { src:'assets/plaene/eg-draufsicht.jpg', titel:'Erdgeschoss – Draufsicht',
    cap:'"03. Tanzhaus 1. Etage" – Hauptgrundlage für die Vermessung des Erdgeschosses.' },
  { src:'assets/plaene/eg-persp-1.jpg', titel:'Erdgeschoss – Perspektive 1',
    cap:'"01. Tanzhaus 1. Etage" – Blick von Nordwesten auf Säle und Lounge.' },
  { src:'assets/plaene/eg-persp-2.jpg', titel:'Erdgeschoss – Perspektive 2',
    cap:'"02. Tanzhaus 1. Etage" – Blick von Norden, Möblierung der Gastro-Zone.' },
  { src:'assets/plaene/og-draufsicht.jpg', titel:'1. Obergeschoss – Draufsicht',
    cap:'"03. Tanzhaus 1/2 Etage" – Hauptgrundlage für die Vermessung des Obergeschosses.' },
  { src:'assets/plaene/og-persp-1.jpg', titel:'1. Obergeschoss – Perspektive 1',
    cap:'"01. Tanzhaus 1/2 Etage" – Umkleidezeile und Mittelflur.' },
  { src:'assets/plaene/og-persp-2.jpg', titel:'1. Obergeschoss – Perspektive 2',
    cap:'"02. Tanzhaus 1/2 Etage" – Blick von Nordwesten, Säle und Garderobe.' },
];

/* ================================================================== TOUR */

/* Kamerapositionen in Weltkoordinaten: x = Grundriss-x, z = −Grundriss-y.
   Süden (Straße) liegt also bei z > 0, der Garten bei x > 30. */
export const TOUR = [
  { id:'poi-fassade',    titel:'Ankommen an der Straße',
    cam:[ 0, 13, 34],   ziel:[16, 4, -4],    level:'all', dach:true },
  { id:'poi-eingang',    titel:'Haupteingang & Treppenhalle',
    cam:[13, 6.5, 17],  ziel:[10, 3.5, -1],  level:'all', dach:true },
  { id:'eg-lounge',      titel:'Lounge, Bar & Bistro',
    cam:[ 8, 26, 20],   ziel:[15, 1, -4],    level:0,     dach:false },
  { id:'eg-empfang',     titel:'Empfang & Tresen',
    cam:[17, 17, 14],   ziel:[23, 1.2, -2],  level:0,     dach:false },
  { id:'eg-saal-ost',    titel:'Der große Saal im Erdgeschoss',
    cam:[12, 27, 10],   ziel:[23.5, 1, -19], level:0,     dach:false },
  { id:'poi-glasfront',  titel:'Glasfront zum Garten',
    cam:[49, 9, -19],   ziel:[30, 3, -19],   level:'all', dach:true },
  { id:'poi-terrasse',   titel:'Terrasse unter den Schirmen',
    cam:[43, 6, -4],    ziel:[32, 2, -14],   level:'all', dach:true },
  { id:'poi-garten',     titel:'Garten mit Liegestühlen',
    cam:[53, 11, -4],   ziel:[36, 2, -16],   level:'all', dach:true },
  { id:'og-saal-ost',    titel:'Hauptsaal im Obergeschoss',
    cam:[12, 31, 10],   ziel:[23.5, 5.5, -19], level:1,   dach:false },
  { id:'og-flur',        titel:'Mittelflur & Umkleiden',
    cam:[ 3, 30, 10],   ziel:[15, 5.5, -20], level:1,     dach:false },
  { id:'og-warte',       titel:'Wartebereich & Kinderecke',
    cam:[21, 21, 17],   ziel:[12.5, 5, -4],  level:1,     dach:false },
  { id:'poi-balkon',     titel:'Balkon über dem Garten',
    cam:[47, 13, -10],  ziel:[31.5, 5.5, -16], level:'all', dach:true },
  { id:'poi-dach',       titel:'Blick über das Flachdach',
    cam:[-8, 36, 24],   ziel:[16, 6, -16],   level:'all', dach:true },
];

/* ============================================================== STANDORT */

/**
 * Adresse und Koordinaten sind nicht aus den Drive-Dateien, sondern
 * öffentlich recherchiert und gegengeprüft: die Tanzschule nennt auf ihrer
 * Website „Podbielskistr. 299 B“, OpenStreetMap führt an derselben Stelle
 * den Eintrag „Tanzhaus Bothe, 299b“ mit der Postleitzahl 30655.
 */
export const STANDORT = {
  name: 'Tanzhaus Hannover',
  strasse: 'Podbielskistraße 299 b',
  ort: '30655 Hannover',
  stadtteil: 'Groß-Buchholz',
  lat: 52.405503,
  lon: 9.794793,
  suchbegriff: 'Tanzhaus Bothe, Podbielskistraße 299b, 30655 Hannover',
  quelle: 'tanzschule-bothe.de · OpenStreetMap (Knoten 430176521)',

  /**
   * Gegenprobe zum Modell: OpenStreetMap zeichnet an dieser Stelle ein
   * Rechteck von rund 33 × 22 m. Das Modell folgt dagegen den Renderings
   * und misst 30 × 31 m. Beides ist dokumentiert, nicht stillschweigend
   * angeglichen – siehe Hinweis im Standortfenster.
   */
  osmGrundflaeche: { breite: 33.1, tiefe: 21.8, flaeche: 722, weg: 98115512 },
};

/* ============================================================= METADATEN */

export const INFO = {
  titel: 'Tanzhaus Hannover',
  untertitel: 'Tanzschule Bothe – interaktives 3D-Modell',
  quellordner: 'Google Drive · „Fotos Tanzhaus"',
  quellLink: 'https://drive.google.com/drive/folders/1hVKhEqwfFCyG4Bs2DLtbEPebkY3r9zAI',
  dateien: [
    '01./02./03. Tanzhaus 1. Etage (PNG-Renderings, Erdgeschoss)',
    '01./02./03. Tanzhaus 1/2 Etage (PNG-Renderings, Obergeschoss)',
    '6 Fotos von Filipp Romanovskij (Außenansichten, Garten, Luftbilder)',
  ],
  hinweise: [
    'Die Renderings sind unbemaßt. Der Maßstab wurde auf eine Gebäudebreite von rund 30 m '
    + 'kalibriert (Abschätzung anhand des Luftbildes). Alle Maß- und Flächenangaben sind '
    + 'daher Näherungswerte.',
    'Die perspektivischen Draufsichten haben eine leichte Zentralprojektion. Die Wände wurden '
    + 'zu einem rechtwinkligen Raster begradigt – Wandstärken und Achsmaße sind idealisiert.',
    'Raumnamen sind aus Bodenbelag, Zuschnitt und Möblierung abgeleitet. Räume ohne eindeutige '
    + 'Zuordnung sind im Detailfenster mit „abgeleitet" gekennzeichnet.',
    'Balkon, Garten, Terrasse, Dachaufbauten und die Fassadengestaltung stammen aus den Fotos '
    + 'und sind in den Grundriss-Renderings nicht enthalten.',
  ],
};
