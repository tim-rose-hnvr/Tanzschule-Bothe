/**
 * Prüft das Datenmodell in src/data.js auf innere Widersprüche.
 *
 *   node tools/pruefe-daten.mjs          → Bericht, Exitcode 1 bei Fehlern
 *   node tools/pruefe-daten.mjs --warn   → Warnungen ebenfalls als Fehler werten
 *
 * Der Generator in src/building.js leitet Wände, Böden und Öffnungen
 * vollständig aus den Rechtecken ab. Ein Tippfehler in einer Koordinate
 * erzeugt deshalb keinen Absturz, sondern still eine falsche Wand. Diese
 * Prüfungen fangen genau solche Fälle ab.
 */
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(fileURLToPath(new URL('..', import.meta.url)));
const D = await import(path.join(ROOT, 'src/data.js'));
const { RAEUME, OEFFNUNGEN, MOEBEL, HIGHLIGHTS, TOUR, FOTOS, KATEGORIEN, BODEN, H } = D;

const fehler = [];
const warnung = [];
const fehl = (bereich, text) => fehler.push({ bereich, text });
const warn = (bereich, text) => warnung.push({ bereich, text });

const nah = (a, b, tol = 0.001) => Math.abs(a - b) < tol;
const flaeche = r => r.rects.reduce((s, [x1, y1, x2, y2]) => s + (x2 - x1) * (y2 - y1), 0);
const grenzen = r => {
  let x1 = Infinity, y1 = Infinity, x2 = -Infinity, y2 = -Infinity;
  for (const q of r.rects) {
    x1 = Math.min(x1, q[0]); y1 = Math.min(y1, q[1]);
    x2 = Math.max(x2, q[2]); y2 = Math.max(y2, q[3]);
  }
  return { x1, y1, x2, y2 };
};

/* ------------------------------------------------- 1 Rechtecke plausibel */

for (const r of RAEUME) {
  if (!r.rects?.length) { fehl('rects', `${r.id}: keine Rechtecke`); continue; }
  for (const [i, q] of r.rects.entries()) {
    if (q.length !== 4) fehl('rects', `${r.id}[${i}]: erwartet 4 Werte, hat ${q.length}`);
    const [x1, y1, x2, y2] = q;
    if (!(x2 > x1)) fehl('rects', `${r.id}[${i}]: x2 (${x2}) nicht größer als x1 (${x1})`);
    if (!(y2 > y1)) fehl('rects', `${r.id}[${i}]: y2 (${y2}) nicht größer als y1 (${y1})`);
    if (x2 - x1 < 0.4 || y2 - y1 < 0.4)
      warn('rects', `${r.id}[${i}]: sehr schmal (${(x2 - x1).toFixed(2)} × ${(y2 - y1).toFixed(2)} m)`);
  }
  if (!KATEGORIEN[r.kat]) fehl('kategorie', `${r.id}: unbekannte Kategorie "${r.kat}"`);
  if (!BODEN[r.boden]) fehl('boden', `${r.id}: unbekannter Bodenbelag "${r.boden}"`);
  if (![0, 1].includes(r.level)) fehl('level', `${r.id}: unerwartete Ebene ${r.level}`);
}

const ids = RAEUME.map(r => r.id);
const doppelt = ids.filter((id, i) => ids.indexOf(id) !== i);
if (doppelt.length) fehl('id', `doppelte Raum-IDs: ${[...new Set(doppelt)].join(', ')}`);

/* ------------------------------------------------ 2 Überlappende Räume */

const ueberlappt = (a, b) => a[0] < b[2] - 0.001 && a[2] > b[0] + 0.001
                          && a[1] < b[3] - 0.001 && a[3] > b[1] + 0.001;

for (const lv of [0, 1]) {
  const paare = RAEUME.filter(r => r.level === lv && r.kat !== 'aussen')
    .flatMap(r => r.rects.map(q => ({ id: r.id, q })));
  for (let i = 0; i < paare.length; i++) for (let j = i + 1; j < paare.length; j++) {
    if (paare[i].id === paare[j].id) continue;
    if (ueberlappt(paare[i].q, paare[j].q)) {
      const ax = Math.min(paare[i].q[2], paare[j].q[2]) - Math.max(paare[i].q[0], paare[j].q[0]);
      const ay = Math.min(paare[i].q[3], paare[j].q[3]) - Math.max(paare[i].q[1], paare[j].q[1]);
      fehl('ueberlappung',
        `Ebene ${lv}: ${paare[i].id} und ${paare[j].id} überschneiden sich um ${ax.toFixed(2)} × ${ay.toFixed(2)} m`);
    }
  }
}

/* --------------------------------------- 3 Öffnungen auf echten Wänden */

function wandKanten(level) {
  // (ax, at) -> Liste der Intervalle, auf denen dort eine Raumkante liegt
  const karte = new Map();
  const zu = (ax, at, s0, s1) => {
    const k = `${ax}@${at.toFixed(2)}`;
    (karte.get(k) || karte.set(k, []).get(k)).push([s0, s1]);
  };
  for (const r of RAEUME.filter(x => x.level === level && x.kat !== 'aussen'))
    for (const [x1, y1, x2, y2] of r.rects) {
      zu('x', x1, y1, y2); zu('x', x2, y1, y2);
      zu('y', y1, x1, x2); zu('y', y2, x1, x2);
    }
  return karte;
}

const kanten = { 0: wandKanten(0), 1: wandKanten(1) };

for (const [i, o] of OEFFNUNGEN.entries()) {
  const wo = `Öffnung #${i} (${o.ax}@${o.at}, ${o.a}–${o.b}, Ebene ${o.level})`;
  if (!(o.b > o.a)) { fehl('oeffnung', `${wo}: b nicht größer als a`); continue; }
  if (o.sill >= o.top) fehl('oeffnung', `${wo}: sill (${o.sill}) nicht kleiner als top (${o.top})`);
  const lichte = H.levelClear[o.level];
  if (o.top > lichte + 0.001 && o.t !== 'glass')
    warn('oeffnung', `${wo}: top ${o.top} über lichter Höhe ${lichte}`);

  // Windfang liegt bewusst außerhalb (y < 0)
  const intervalle = kanten[o.level].get(`${o.ax}@${o.at.toFixed(2)}`);
  if (!intervalle) {
    fehl('oeffnung', `${wo}: an dieser Achse existiert keine Raumkante – die Öffnung wird nie ausgeschnitten`);
    continue;
  }
  const abgedeckt = intervalle.some(([s0, s1]) => s0 <= o.a + 0.02 && s1 >= o.b - 0.02);
  if (!abgedeckt) {
    const teilweise = intervalle.some(([s0, s1]) => s0 < o.b && s1 > o.a);
    (teilweise ? warn : fehl)('oeffnung',
      `${wo}: ${teilweise ? 'ragt über die Wandkante hinaus' : 'liegt neben jeder Wandkante dieser Achse'}` +
      ` (vorhanden: ${intervalle.map(v => v.map(n => n.toFixed(1)).join('–')).join(', ')})`);
  }
}

/* --------------------------------------------- 4 Möbel innerhalb ihres Raums */

const raumNach = new Map(RAEUME.map(r => [r.id, r]));
const imRaum = (r, x, y, tol = 0.35) =>
  r.rects.some(([x1, y1, x2, y2]) => x >= x1 - tol && x <= x2 + tol && y >= y1 - tol && y <= y2 + tol);

for (const [i, m] of MOEBEL.entries()) {
  const r = raumNach.get(m.room);
  if (!r) { fehl('moebel', `Möbel #${i} (${m.type}): Raum "${m.room}" existiert nicht`); continue; }
  // at/von/bis sind je nach Möbeltyp entweder ein Punkt [x,y] oder ein
  // Skalar entlang der Wand – beide Formen kommen in MOEBEL vor.
  const punkte = [];
  if (Array.isArray(m.at)) punkte.push(m.at);
  if (Array.isArray(m.von)) punkte.push(m.von);
  if (Array.isArray(m.bis)) punkte.push(m.bis);
  if (m.rect) punkte.push([m.rect[0], m.rect[1]], [m.rect[2], m.rect[3]]);
  for (const [x, y] of punkte)
    if (!imRaum(r, x, y))
      fehl('moebel', `Möbel #${i} (${m.type} in ${m.room}): Punkt ${x}/${y} liegt außerhalb des Raums`);

  // wandgebundene Möbel: Skalare laufen entlang der jeweiligen Wand
  if (m.wand) {
    const g = grenzen(r);
    const waagerecht = m.wand === 'n' || m.wand === 's';
    const [lo, hi] = waagerecht ? [g.x1, g.x2] : [g.y1, g.y2];
    const spanne = [];
    if (typeof m.von === 'number') spanne.push(m.von);
    if (typeof m.bis === 'number') spanne.push(m.bis);
    if (typeof m.at === 'number') spanne.push(m.at);
    for (const v of spanne)
      if (v < lo - 0.35 || v > hi + 0.35)
        fehl('moebel', `Möbel #${i} (${m.type} in ${m.room}, Wand ${m.wand}): ${v} liegt außerhalb der Wandspanne ${lo.toFixed(1)}–${hi.toFixed(1)}`);
  }
}

/* ------------------------------------------------- 5 Verweise und Texte */

for (const r of RAEUME)
  for (const k of r.fotos || [])
    if (!FOTOS[k]) fehl('foto', `${r.id}: unbekannter Fotoschlüssel "${k}"`);
for (const h of HIGHLIGHTS)
  for (const k of h.fotos || [])
    if (!FOTOS[k]) fehl('foto', `${h.id}: unbekannter Fotoschlüssel "${k}"`);

const alleIds = new Set([...RAEUME.map(r => r.id), ...HIGHLIGHTS.map(h => h.id)]);
for (const t of TOUR)
  if (!alleIds.has(t.id)) fehl('tour', `Tour-Station "${t.titel}": unbekannte ID "${t.id}"`);

const nrn = HIGHLIGHTS.map(h => h.nr);
if (new Set(nrn).size !== nrn.length) fehl('highlight', 'doppelte Highlight-Nummern');

/* --------------------------------- 6 Tourkameras zeigen auf ihr Ziel */

for (const t of TOUR) {
  const r = raumNach.get(t.id);
  if (!r) continue;
  const g = grenzen(r);
  const [zx, , zz] = t.ziel;
  const zy = -zz;
  if (zx < g.x1 - 3 || zx > g.x2 + 3 || zy < g.y1 - 3 || zy > g.y2 + 3)
    warn('tour', `"${t.titel}": Blickziel ${zx}/${zy} liegt weit außerhalb von ${t.id} (${g.x1}–${g.x2} / ${g.y1}–${g.y2})`);
  if (t.level !== 'all' && t.level !== r.level)
    fehl('tour', `"${t.titel}": zeigt Ebene ${t.level}, Raum ${t.id} liegt auf Ebene ${r.level}`);
  const basis = H.levelBase[r.level];
  if (t.cam[1] < basis) warn('tour', `"${t.titel}": Kamera unter dem Fußboden der Ebene`);
}

/* -------------------------------------------- 7 Geschosse stapelbar */

const grundriss = lv => RAEUME.filter(r => r.level === lv && r.kat !== 'aussen').flatMap(r => r.rects);
const inFlaeche = (rects, x, y) =>
  rects.some(([x1, y1, x2, y2]) => x > x1 + 0.01 && x < x2 - 0.01 && y > y1 + 0.01 && y < y2 - 0.01);
const eg = grundriss(0), og = grundriss(1);
// Rasterversatz .13/.63: keine Raumkante im Modell endet auf diesen
// Nachkommastellen. Ohne den Versatz landen Abtastpunkte auf gemeinsamen
// Kanten zweier Räume, gelten dort als "in keinem Raum" und melden
// Geschosse als schwebend, die in Wahrheit sauber aufeinanderstehen.
const schwebend = [];
for (let x = 0.13; x < 30; x += 0.5) for (let y = 0.13; y < 31.2; y += 0.5)
  if (inFlaeche(og, x, y) && !inFlaeche(eg, x, y)) schwebend.push([x, y]);
if (schwebend.length > 4) {
  const xs = schwebend.map(p => p[0]), ys = schwebend.map(p => p[1]);
  warn('stapel', `${schwebend.length} Rasterpunkte des Obergeschosses stehen über keinem Erdgeschossraum `
     + `(Bereich x ${Math.min(...xs).toFixed(1)}–${Math.max(...xs).toFixed(1)}, `
     + `y ${Math.min(...ys).toFixed(1)}–${Math.max(...ys).toFixed(1)})`);
}

/* -------------------------------------------------------------- Bericht */

const zeig = (titel, liste) => {
  if (!liste.length) return;
  console.log(`\n${titel} (${liste.length})`);
  const nachBereich = {};
  for (const e of liste) (nachBereich[e.bereich] ||= []).push(e.text);
  for (const [b, texte] of Object.entries(nachBereich)) {
    console.log(`  ${b}:`);
    for (const t of texte) console.log(`    · ${t}`);
  }
};

console.log(`Datenmodell: ${RAEUME.length} Räume, ${OEFFNUNGEN.length} Öffnungen, `
          + `${MOEBEL.length} Möbel, ${HIGHLIGHTS.length} Highlights, ${TOUR.length} Tour-Stationen`);
for (const lv of [0, 1]) {
  const rs = RAEUME.filter(r => r.level === lv && r.kat !== 'aussen');
  console.log(`  Ebene ${lv}: ${rs.length} Räume, ${Math.round(rs.reduce((s, r) => s + flaeche(r), 0))} m²`);
}
zeig('WARNUNGEN', warnung);
zeig('FEHLER', fehler);
console.log(fehler.length ? `\n${fehler.length} Fehler` : '\nkeine Fehler');

const streng = process.argv.includes('--warn');
process.exit(fehler.length || (streng && warnung.length) ? 1 : 0);
