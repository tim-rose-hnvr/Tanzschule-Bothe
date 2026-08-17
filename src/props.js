/**
 * Möblierung – übersetzt die deklarativen Einträge aus data.js in Geometrie.
 * Alle Angaben in Grundriss-Metern; die Umrechnung in Weltkoordinaten
 * (worldZ = -y) passiert ausschließlich hier.
 */
import * as THREE from 'three';
import { tanzbildTextur } from './materials.js';

const DEG = Math.PI / 180;

/* ------------------------------------------------------------- Helfer */

export function boxMesh(w, h, d, mat, x, y, z, ry = 0) {
  const m = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), mat);
  m.position.set(x, y, z);
  if (ry) m.rotation.y = ry;
  m.castShadow = true; m.receiveShadow = true;
  return m;
}
function cyl(r, h, mat, x, y, z, seg = 14) {
  const m = new THREE.Mesh(new THREE.CylinderGeometry(r, r, h, seg), mat);
  m.position.set(x, y, z);
  m.castShadow = true; m.receiveShadow = true;
  return m;
}
/** Grundriss (x,y) + Höhe → Weltkoordinaten */
const P = (x, y, h) => [x, h, -y];

function bounds(room) {
  let x1 = Infinity, y1 = Infinity, x2 = -Infinity, y2 = -Infinity;
  for (const r of room.rects) {
    x1 = Math.min(x1, r[0]); y1 = Math.min(y1, r[1]);
    x2 = Math.max(x2, r[2]); y2 = Math.max(y2, r[3]);
  }
  return { x1, y1, x2, y2 };
}

/* --------------------------------------------------------- Einzelmöbel */

function stehtisch(g, M, x, y, base) {
  g.add(cyl(0.05, 1.05, M.grau, ...P(x, y, base + 0.53)));
  g.add(cyl(0.34, 0.05, M.weiss, ...P(x, y, base + 1.07), 20));
  g.add(cyl(0.26, 0.03, M.grauDunkel, ...P(x, y, base + 0.03), 16));
}

function stuhl(g, M, x, y, base, rot = 0) {
  const s = new THREE.Group();
  s.add(boxMesh(0.44, 0.05, 0.44, M.holz, 0, base + 0.45, 0));
  s.add(boxMesh(0.44, 0.48, 0.05, M.holz, 0, base + 0.70, -0.20));
  for (const [dx, dz] of [[-0.18, -0.18], [0.18, -0.18], [-0.18, 0.18], [0.18, 0.18]])
    s.add(boxMesh(0.04, 0.45, 0.04, M.grauDunkel, dx, base + 0.225, dz));
  s.position.set(x, 0, -y); s.rotation.y = rot * DEG;
  g.add(s);
}

function tischgruppe(g, M, x, y, base) {
  g.add(boxMesh(1.30, 0.06, 0.75, M.holz, ...P(x, y, base + 0.75)));
  for (const [dx, dz] of [[-0.55, -0.3], [0.55, -0.3], [-0.55, 0.3], [0.55, 0.3]])
    g.add(boxMesh(0.06, 0.75, 0.06, M.grauDunkel, x + dx, base + 0.375, -y - dz));
  stuhl(g, M, x - 0.42, y + 0.68, base, 180);
  stuhl(g, M, x + 0.42, y + 0.68, base, 180);
  stuhl(g, M, x - 0.42, y - 0.68, base, 0);
  stuhl(g, M, x + 0.42, y - 0.68, base, 0);
}

/** Bank-Tisch-Kombination (wie in der Lounge / im Saal OG) */
function bank4(g, M, x, y, base) {
  g.add(boxMesh(0.85, 0.06, 1.60, M.holz, ...P(x, y, base + 0.76)));
  g.add(boxMesh(0.10, 0.72, 1.40, M.grauDunkel, ...P(x, y, base + 0.38)));
  for (const dx of [-0.72, 0.72]) {
    g.add(boxMesh(0.36, 0.05, 1.55, M.holz, x + dx, base + 0.46, -y));
    g.add(boxMesh(0.06, 0.44, 1.35, M.grauDunkel, x + dx, base + 0.23, -y));
  }
}

function bankzeile(g, M, a, b, base) {
  const dx = b[0] - a[0], dy = b[1] - a[1];
  const len = Math.hypot(dx, dy);
  const mid = [(a[0] + b[0]) / 2, (a[1] + b[1]) / 2];
  const ry = Math.atan2(dx, -dy) + Math.PI / 2;
  g.add(boxMesh(0.46, 0.10, len, M.holz, ...P(mid[0], mid[1], base + 0.46), ry));
  g.add(boxMesh(0.36, 0.42, len, M.grauDunkel, ...P(mid[0], mid[1], base + 0.21), ry));
}

function nische(g, M, x, y, base, rot) {
  const n = new THREE.Group();
  n.add(boxMesh(1.55, 0.10, 0.55, M.holz, 0, base + 0.46, 0));
  n.add(boxMesh(1.55, 0.95, 0.10, M.holzDunkel, 0, base + 0.72, -0.30));
  n.add(boxMesh(1.35, 0.06, 0.45, M.grauDunkel, 0, base + 0.42, 0.02));
  n.position.set(x, 0, -y); n.rotation.y = rot * DEG;
  g.add(n);
}

function sofa(g, M, x, y, base, rot) {
  const s = new THREE.Group();
  s.add(boxMesh(2.05, 0.42, 0.85, M.grauDunkel, 0, base + 0.21, 0));
  s.add(boxMesh(2.05, 0.14, 0.80, M.grau, 0, base + 0.49, 0.02));
  s.add(boxMesh(2.05, 0.52, 0.18, M.grauDunkel, 0, base + 0.68, -0.34));
  s.position.set(x, 0, -y); s.rotation.y = rot * DEG;
  g.add(s);
}

function tresen(g, M, rect, base, rueck) {
  const [x1, y1, x2, y2] = rect;
  const w = x2 - x1, d = y2 - y1, cx = (x1 + x2) / 2, cy = (y1 + y2) / 2;
  g.add(boxMesh(w, 1.05, d, M.holzDunkel, ...P(cx, cy, base + 0.525)));
  g.add(boxMesh(w + 0.14, 0.07, d + 0.14, M.weiss, ...P(cx, cy, base + 1.09)));
  g.add(boxMesh(w - 0.1, 0.04, d + 0.10, M.gelb, ...P(cx, cy, base + 0.30)));
  if (rueck) {
    const rd = 0.42;
    g.add(boxMesh(w, 1.90, rd, M.holzDunkel, ...P(cx, y2 + 0.75, base + 0.95)));
    for (let i = 0; i < 3; i++)
      g.add(boxMesh(w - 0.30, 0.04, rd - 0.12, M.weiss, ...P(cx, y2 + 0.75, base + 0.65 + i * 0.42)));
  }
}

function musikmoebel(g, M, x, y, base, rot) {
  const m = new THREE.Group();
  m.add(boxMesh(1.50, 0.90, 0.55, M.grau, 0, base + 0.45, 0));
  m.add(boxMesh(1.55, 0.06, 0.60, M.holzDunkel, 0, base + 0.93, 0));
  m.add(boxMesh(1.10, 0.30, 0.35, M.schwarz, 0, base + 1.12, 0));
  m.position.set(x, 0, -y); m.rotation.y = rot * DEG;
  g.add(m);
}

function boxen(g, M, x, y, base) {
  g.add(boxMesh(0.30, 0.52, 0.28, M.schwarz, ...P(x, y, base + 2.55)));
  g.add(boxMesh(0.06, 0.30, 0.06, M.grauDunkel, ...P(x, y, base + 2.96)));
}

function pendel(g, M, x, y, base, clear, n) {
  for (let i = 0; i < n; i++) {
    const yy = y + (i - (n - 1) / 2) * 3.2;
    g.add(cyl(0.006, 0.9, M.grauDunkel, ...P(x, yy, base + clear - 0.45)));
    const s = new THREE.Mesh(new THREE.SphereGeometry(0.24, 18, 14), M.lampe);
    s.position.set(...P(x, yy, base + clear - 1.0));
    g.add(s);
  }
}

function spiegelwand(g, M, room, wand, von, bis, base, clear) {
  const b = bounds(room);
  const h = Math.min(2.4, clear - 0.5), yc = base + 0.15 + h / 2;
  if (wand === 'n' || wand === 's') {
    const y = wand === 'n' ? b.y2 - 0.09 : b.y1 + 0.09;
    g.add(boxMesh(bis - von, h, 0.04, M.spiegel, (von + bis) / 2, yc, -y));
  } else {
    const x = wand === 'w' ? b.x1 + 0.09 : b.x2 - 0.09;
    g.add(boxMesh(0.04, h, bis - von, M.spiegel, x, yc, -(von + bis) / 2));
  }
}

function stange(g, M, room, wand, von, bis, base) {
  const b = bounds(room);
  if (wand === 'n' || wand === 's') {
    const y = wand === 'n' ? b.y2 - 0.20 : b.y1 + 0.20;
    const bar = cyl(0.025, bis - von, M.stahl, (von + bis) / 2, base + 1.0, -y, 10);
    bar.rotation.z = Math.PI / 2; g.add(bar);
    for (const x of [von + 0.3, (von + bis) / 2, bis - 0.3])
      g.add(boxMesh(0.05, 0.05, 0.22, M.stahl, x, base + 1.0, -y - 0.06));
  } else {
    const x = wand === 'w' ? b.x1 + 0.20 : b.x2 - 0.20;
    const bar = cyl(0.025, bis - von, M.stahl, x, base + 1.0, -(von + bis) / 2, 10);
    bar.rotation.x = Math.PI / 2; g.add(bar);
    for (const y of [von + 0.3, (von + bis) / 2, bis - 0.3])
      g.add(boxMesh(0.22, 0.05, 0.05, M.stahl, x + 0.06, base + 1.0, -y));
  }
}

function wandbild(g, M, room, wand, at, w, base) {
  const b = bounds(room);
  const mat = new THREE.MeshStandardMaterial({ map: tanzbildTextur(), roughness: 0.8 });
  const h = w * 1.3;
  if (wand === 'n') g.add(boxMesh(w, h, 0.05, mat, at, base + 2.15, -(b.y2 - 0.11)));
  else g.add(boxMesh(0.05, h, w, mat, b.x1 + 0.11, base + 2.15, -at));
}

function treppe(g, M, rect, base, richtung, hoehe) {
  const [x1, y1, x2, y2] = rect;
  const n = 20, w = x2 - x1, len = y2 - y1;
  const sh = hoehe / n, sd = len / n;
  for (let i = 0; i < n; i++) {
    const y = richtung === 'n' ? y1 + i * sd + sd / 2 : y2 - i * sd - sd / 2;
    g.add(boxMesh(w - 0.5, 0.06, sd, M.holzDunkel, (x1 + x2) / 2, base + (i + 1) * sh, -y));
    g.add(boxMesh(w - 0.5, sh, 0.05, M.grau, (x1 + x2) / 2,
      base + (i + 0.5) * sh, -(y + (richtung === 'n' ? -sd / 2 : sd / 2))));
  }
  // Wange + Handlauf
  for (const s of [-1, 1]) {
    const x = (x1 + x2) / 2 + s * (w - 0.5) / 2;
    const rail = new THREE.Mesh(new THREE.BoxGeometry(0.05, 0.05, Math.hypot(len, hoehe)), M.stahl);
    rail.position.set(x, base + hoehe / 2 + 0.95, -(y1 + y2) / 2);
    rail.rotation.x = (richtung === 'n' ? 1 : -1) * Math.atan2(hoehe, len);
    g.add(rail);
  }
}

/** Treppenauge im OG: Öffnung mit umlaufendem Geländer */
function treppenauge(g, M, rect, base) {
  const [x1, y1, x2, y2] = rect;
  const kanten = [
    [x1, y1, x2, y1], [x1, y2, x2, y2],
    [x1, y1, x1, y2], [x2, y1, x2, y2],
  ];
  for (const [ax, ay, bx, by] of kanten) {
    const len = Math.hypot(bx - ax, by - ay);
    const cx = (ax + bx) / 2, cy = (ay + by) / 2;
    const ry = Math.atan2(bx - ax, -(by - ay)) + Math.PI / 2;
    g.add(boxMesh(0.05, 0.05, len, M.stahl, cx, base + 1.05, -cy, ry));
    g.add(boxMesh(0.04, 0.04, len, M.stahl, cx, base + 0.62, -cy, ry));
    const n = Math.max(2, Math.round(len / 1.1));
    for (let i = 0; i <= n; i++) {
      const t = i / n;
      g.add(boxMesh(0.05, 1.05, 0.05, M.stahl, ax + (bx - ax) * t, base + 0.52, -(ay + (by - ay) * t)));
    }
  }
}

function spinde(g, M, a, b, n, base) {
  const w = (b[0] - a[0]) / n;
  for (let i = 0; i < n; i++) {
    const x = a[0] + w * (i + 0.5);
    g.add(boxMesh(w - 0.12, 2.05, 0.55, M.weiss, x, base + 1.03, -a[1]));
    g.add(boxMesh(w - 0.30, 1.70, 0.03, M.lampe, x, base + 1.05, -(a[1] - 0.29)));
  }
  g.add(boxMesh(b[0] - a[0] + 0.2, 0.10, 0.62, M.holzDunkel, (a[0] + b[0]) / 2, base + 2.13, -a[1]));
}

function umkleidebank(g, M, room, base) {
  const b = bounds(room);
  const cx = (b.x1 + b.x2) / 2, len = Math.min(2.4, b.y2 - b.y1 - 0.8);
  g.add(boxMesh(0.42, 0.08, len, M.holz, cx, base + 0.45, -(b.y1 + b.y2) / 2));
  g.add(boxMesh(0.10, 0.42, len - 0.4, M.grauDunkel, cx, base + 0.22, -(b.y1 + b.y2) / 2));
  for (let i = 0; i < 4; i++)
    g.add(boxMesh(0.06, 0.06, 0.10, M.stahl, b.x2 - 0.14, base + 1.65,
      -((b.y1 + b.y2) / 2 + (i - 1.5) * 0.45)));
}

function sanitaer(g, M, room, wand, von, bis, base) {
  const b = bounds(room);
  const y = wand === 's' ? b.y1 + 0.28 : b.y2 - 0.28;
  const n = Math.max(2, Math.round((bis - von) / 0.75));
  for (let i = 0; i < n; i++) {
    const x = von + (bis - von) * (i + 0.5) / n;
    g.add(boxMesh(0.36, 0.55, 0.34, M.weiss, x, base + 0.72, -y));
    g.add(boxMesh(0.30, 0.28, 0.12, M.weiss, x, base + 1.14, -(y - 0.13)));
  }
}

function waschtisch(g, M, room, wand, at, w, base) {
  const b = bounds(room);
  if (wand === 'w' || wand === 'e') {
    const x = wand === 'w' ? b.x1 + 0.28 : b.x2 - 0.28;
    g.add(boxMesh(0.52, 0.18, w, M.weiss, x, base + 0.88, -at));
    g.add(boxMesh(0.48, 0.70, w - 0.12, M.grau, x, base + 0.44, -at));
    g.add(boxMesh(0.04, 0.90, w - 0.2, M.spiegel, x - 0.24, base + 1.62, -at));
  } else {
    const y = wand === 'n' ? b.y2 - 0.28 : b.y1 + 0.28;
    g.add(boxMesh(w, 0.18, 0.52, M.weiss, at, base + 0.88, -y));
    g.add(boxMesh(w - 0.12, 0.70, 0.48, M.grau, at, base + 0.44, -y));
  }
}

function regal(g, M, room, wand, von, bis, base) {
  const b = bounds(room);
  const y = wand === 'n' ? b.y2 - 0.28 : b.y1 + 0.28;
  g.add(boxMesh(bis - von, 2.10, 0.50, M.grau, (von + bis) / 2, base + 1.05, -y));
  for (let i = 1; i < 5; i++)
    g.add(boxMesh(bis - von - 0.06, 0.04, 0.54, M.grauDunkel, (von + bis) / 2, base + i * 0.42, -y));
}

function pflanze(g, M, x, y, base) {
  g.add(cyl(0.20, 0.34, M.holzDunkel, ...P(x, y, base + 0.17), 12));
  const leaf = new THREE.Mesh(new THREE.IcosahedronGeometry(0.38, 0), M.gruen);
  leaf.position.set(...P(x, y, base + 0.62)); leaf.castShadow = true;
  g.add(leaf);
  const leaf2 = new THREE.Mesh(new THREE.IcosahedronGeometry(0.26, 0), M.gruenD);
  leaf2.position.set(...P(x + 0.16, y - 0.1, base + 0.86));
  g.add(leaf2);
}

function spielecke(g, M, x, y, base) {
  const cols = [M.rot, M.gelb, M.gruen, M.stahl];
  for (let i = 0; i < 9; i++) {
    const s = 0.16 + (i % 3) * 0.05;
    g.add(boxMesh(s, s, s, cols[i % 4],
      x + ((i * 7) % 5) * 0.28 - 0.5, base + s / 2, -(y + ((i * 3) % 4) * 0.30 - 0.4)));
  }
  g.add(boxMesh(1.30, 0.06, 1.30, M.gelb, x, base + 0.02, -y));
}

function stuhlreihe(g, M, a, b, n, base, rot) {
  for (let i = 0; i < n; i++) {
    const t = n === 1 ? 0.5 : i / (n - 1);
    stuhl(g, M, a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, base, rot);
  }
}

/* ------------------------------------------------------------- Verteiler */

export function buildMoebel(group, M, room, eintrag, base, clear) {
  const e = eintrag, g = group;
  switch (e.type) {
    case 'stehtisch':   stehtisch(g, M, e.at[0], e.at[1], base); break;
    case 'tischgruppe': tischgruppe(g, M, e.at[0], e.at[1], base); break;
    case 'bank4':       bank4(g, M, e.at[0], e.at[1], base); break;
    case 'bankzeile':   bankzeile(g, M, e.von, e.bis, base); break;
    case 'nische':      nische(g, M, e.at[0], e.at[1], base, e.rot || 0); break;
    case 'sofa':        sofa(g, M, e.at[0], e.at[1], base, e.rot || 0); break;
    case 'tresen':      tresen(g, M, e.rect, base, e.rueck); break;
    case 'musikmoebel': musikmoebel(g, M, e.at[0], e.at[1], base, e.rot || 0); break;
    case 'boxen':       boxen(g, M, e.at[0], e.at[1], base); break;
    case 'pendel':      pendel(g, M, e.at[0], e.at[1], base, clear, e.n || 1); break;
    case 'spiegelwand': spiegelwand(g, M, room, e.wand, e.von, e.bis, base, clear); break;
    case 'stange':      stange(g, M, room, e.wand, e.von, e.bis, base); break;
    case 'wandbild':    wandbild(g, M, room, e.wand, e.at, e.w, base); break;
    case 'treppe':      treppe(g, M, e.rect, base, e.richtung, 4.50); break;
    case 'treppenauge': treppenauge(g, M, e.rect, base); break;
    case 'spinde':      spinde(g, M, e.von, e.bis, e.n, base); break;
    case 'umkleidebank':umkleidebank(g, M, room, base); break;
    case 'sanitaer':    sanitaer(g, M, room, e.wand, e.von, e.bis, base); break;
    case 'waschtisch':  waschtisch(g, M, room, e.wand, e.at, e.w, base); break;
    case 'regal':       regal(g, M, room, e.wand, e.von, e.bis, base); break;
    case 'pflanze':     pflanze(g, M, e.at[0], e.at[1], base); break;
    case 'spielecke':   spielecke(g, M, e.at[0], e.at[1], base); break;
    case 'stuhlreihe':  stuhlreihe(g, M, e.von, e.bis, e.n, base, e.rot || 0); break;
  }
}

export { bounds, cyl, P };
