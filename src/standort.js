/**
 * Standortfenster: Lageplan, Google-Maps-Einbettung und Kartenlinks.
 *
 * Die Einbettung ist bewusst als Zusatz gebaut, nicht als Voraussetzung.
 * In eingebetteten Umgebungen (etwa einer veröffentlichten Artifact-Seite)
 * verbietet die Content-Security-Policy jeden Fremd-Host, die Karte kann
 * dort also gar nicht laden. Der Lageplan ist deshalb selbst gezeichnet und
 * immer verfügbar; die Karte schiebt sich nur darüber, wenn sie wirklich
 * ankommt. Die Links funktionieren in beiden Fällen.
 */
import { STANDORT as S, RAEUME } from './data.js';

/** Optionaler Schlüssel für die offizielle Maps Embed API. */
export const MAPS_API_KEY = '';

const esc = s => String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));

export const KARTEN_LINKS = {
  karte:  `https://www.google.com/maps/search/?api=1&query=${S.lat},${S.lon}`,
  suche:  `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(S.suchbegriff)}`,
  route:  `https://www.google.com/maps/dir/?api=1&destination=${S.lat},${S.lon}`,
  street: `https://www.google.com/maps/@?api=1&map_action=pano&viewpoint=${S.lat},${S.lon}`,
  satellit: `https://www.google.com/maps/@${S.lat},${S.lon},19z/data=!3m1!1e3`,
};

function embedUrl() {
  return MAPS_API_KEY
    ? `https://www.google.com/maps/embed/v1/place?key=${MAPS_API_KEY}`
      + `&q=${encodeURIComponent(S.suchbegriff)}&zoom=18&maptype=satellite`
    : `https://maps.google.com/maps?q=${S.lat},${S.lon}&z=18&t=k&output=embed`;
}

/* ------------------------------------------------------------ Lageplan */

/** Schematischer Lageplan aus den Modelldaten – ohne Netzzugriff. */
function lageplanSvg() {
  const W = 340, Hh = 250;
  const mx = 12, my = 10;
  // Modellbereich: x -2..52, y -14..37  (Meter)
  const sx = v => mx + (v + 2) / 54 * (W - 2 * mx);
  const sy = v => Hh - my - (v + 14) / 51 * (Hh - 2 * my);

  const umriss = [[0, 0], [30, 0], [30, 31.16], [10.2, 31.16], [10.2, 28.45], [0, 28.45]];
  const pfad = umriss.map(([x, y], i) => `${i ? 'L' : 'M'}${sx(x).toFixed(1)},${sy(y).toFixed(1)}`).join(' ') + ' Z';

  const saele = RAEUME.filter(r => r.level === 0 && r.kat === 'saal')
    .map(r => r.rects[0])
    .map(([x1, y1, x2, y2]) =>
      `<rect x="${sx(x1).toFixed(1)}" y="${sy(y2).toFixed(1)}" width="${(sx(x2) - sx(x1)).toFixed(1)}"
             height="${(sy(y1) - sy(y2)).toFixed(1)}" fill="rgba(216,57,42,.18)" stroke="rgba(216,57,42,.5)"/>`)
    .join('');

  // Kein Nordpfeil: die Himmelsrichtungen im Modell sind aus den Renderings
  // erschlossen (Straße im Süden, Garten im Osten), nicht eingemessen. Die
  // beiden beschrifteten Flächen sagen dasselbe, ohne Genauigkeit
  // vorzutäuschen, die die Vorlagen nicht hergeben.
  return `
  <svg viewBox="0 0 ${W} ${Hh}" class="lageplan" role="img"
       aria-label="Schematischer Lageplan: Gebäude mit Garten im Osten und Straße im Süden">
    <rect x="0" y="0" width="${W}" height="${Hh}" fill="rgba(140,198,62,.10)"/>
    <rect x="${sx(30)}" y="${sy(31)}" width="${sx(50) - sx(30)}" height="${sy(1) - sy(31)}"
          fill="rgba(140,198,62,.22)"/>
    <text x="${sx(41)}" y="${sy(16)}" class="lp-t lp-c">Garten</text>
    <rect x="${sx(-2)}" y="${sy(-2.5)}" width="${sx(38) - sx(-2)}" height="${sy(-13) - sy(-2.5)}"
          fill="rgba(255,255,255,.07)"/>
    <text x="${sx(16)}" y="${sy(-9)}" class="lp-t lp-c">Podbielskistraße</text>
    ${saele}
    <path d="${pfad}" fill="rgba(255,255,255,.06)" stroke="#d8392a" stroke-width="1.6"/>
    <circle cx="${sx(17.3)}" cy="${sy(-0.9)}" r="3.6" fill="#f4b32a"/>
    <text x="${sx(20.4)}" y="${sy(-1.9)}" class="lp-t">Haupteingang</text>
    <text x="${sx(6)}" y="${sy(18)}" class="lp-t lp-c">Tanzsäle</text>
    <g class="lp-mass">
      <line x1="${sx(0)}" y1="${sy(33.5)}" x2="${sx(30)}" y2="${sy(33.5)}"/>
      <text x="${sx(15)}" y="${sy(34.6)}" class="lp-t lp-c">30 m (Modellmaß)</text>
    </g>
  </svg>`;
}

/* -------------------------------------------------------------- Fenster */

export function standortHtml() {
  const o = S.osmGrundflaeche;
  return `
    <h2>Standort</h2>
    <p class="adresse">
      <strong>${esc(S.name)}</strong><br>
      ${esc(S.strasse)}<br>
      ${esc(S.ort)} · ${esc(S.stadtteil)}<br>
      <span class="koord">${S.lat.toFixed(6)}, ${S.lon.toFixed(6)}</span>
    </p>

    <div class="kartenfeld" id="kartenfeld">
      <div class="karte-fallback">
        ${lageplanSvg()}
        <p class="karte-hinweis" id="karte-hinweis">Google-Karte wird geladen …</p>
      </div>
    </div>

    <div class="kartenlinks">
      <a href="${KARTEN_LINKS.suche}" target="_blank" rel="noopener">In Google Maps öffnen ↗</a>
      <a href="${KARTEN_LINKS.satellit}" target="_blank" rel="noopener">Satellitenbild ↗</a>
      <a href="${KARTEN_LINKS.street}" target="_blank" rel="noopener">Street View ↗</a>
      <a href="${KARTEN_LINKS.route}" target="_blank" rel="noopener">Route planen ↗</a>
    </div>

    <h3>Modell und Wirklichkeit</h3>
    <ul>
      <li>Die Ausrichtung im Modell folgt den Renderings: Straße und Haupteingang
        im Süden, Garten und Glasfassade im Osten. Sie ist nicht eingemessen.</li>
      <li>OpenStreetMap zeichnet an dieser Adresse ein Rechteck von rund
        <b>${o.breite} × ${o.tiefe} m</b> (${o.flaeche} m²). Das Modell folgt den
        Grundriss-Renderings und misst <b>30 × 31 m</b>. Welche Angabe stimmt,
        lässt sich aus den vorliegenden Dateien nicht entscheiden – der
        OSM-Umriss ist aus Luftbildern abgezeichnet, die Renderings können
        einen Planungsstand zeigen.</li>
      <li>Adresse und Koordinaten stammen nicht aus dem Drive-Ordner, sondern
        aus öffentlichen Quellen: ${esc(S.quelle)}.</li>
    </ul>`;
}

/**
 * Versucht, die Google-Karte nachzuladen. Meldet sie sich nicht innerhalb
 * weniger Sekunden, bleibt der gezeichnete Lageplan stehen.
 */
export function karteNachladen() {
  const feld = document.getElementById('kartenfeld');
  const hinweis = document.getElementById('karte-hinweis');
  if (!feld) return;

  const frame = document.createElement('iframe');
  frame.className = 'karte';
  frame.loading = 'lazy';
  frame.referrerPolicy = 'no-referrer-when-downgrade';
  frame.title = 'Google-Karte des Standorts';
  frame.allowFullscreen = true;

  let erledigt = false;
  const aufgeben = () => {
    if (erledigt) return;
    erledigt = true;
    frame.remove();
    if (hinweis) hinweis.textContent =
      'Live-Karte hier nicht verfügbar – der Lageplan oben stammt aus dem Modell. '
      + 'Die Links darunter öffnen den Standort in Google Maps.';
  };
  const geschafft = () => {
    if (erledigt) return;
    erledigt = true;
    feld.classList.add('hat-karte');
  };

  frame.addEventListener('load', geschafft);
  frame.addEventListener('error', aufgeben);
  setTimeout(aufgeben, 4500);

  frame.src = embedUrl();
  feld.append(frame);
}
