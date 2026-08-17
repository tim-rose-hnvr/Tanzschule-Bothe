/**
 * Gebäude-Generator: erzeugt aus den Raum-Rechtecken automatisch
 * Wände (mit Tür-, Fenster- und Glasöffnungen), Böden, Decken und Dach.
 */
import * as THREE from 'three';
import { H, RAEUME, OEFFNUNGEN, MOEBEL, BODEN } from './data.js';
import { buildMoebel, boxMesh } from './props.js';

const EPS = 0.06;
const key = v => v.toFixed(2);

/* ---------------------------------------------------------- Geometrie-Hilfen */

function levelRooms(level) {
  return RAEUME.filter(r => r.level === level && r.kat !== 'aussen');
}

/**
 * Liefert die Raum-ID an einer Grundrissposition – oder null im Freien.
 *
 * Die Toleranz fängt Abtastpunkte ab, die exakt auf einer gemeinsamen
 * Raumkante liegen (etwa y = 20.05 zwischen zwei aneinandergrenzenden
 * Sälen). Ohne sie lägen sie in *keinem* Rechteck, und die Wandsuche hielte
 * die Stelle für Freiraum. Der Wert bleibt deutlich unter dem Sondenabstand
 * von 6 cm, die Zuordnung zu einem Raum bleibt also eindeutig.
 */
const RAUM_TOLERANZ = 0.02;

function makeRoomAt(rooms) {
  const rects = rooms.flatMap(r => r.rects.map(q => [...q, r.id]));
  const t = RAUM_TOLERANZ;
  return (x, y) => {
    for (const [x1, y1, x2, y2, id] of rects)
      if (x > x1 - t && x < x2 + t && y > y1 - t && y < y2 + t) return id;
    return null;
  };
}

function mergeIntervals(list) {
  const s = list.slice().sort((a, b) => a[0] - b[0]);
  const out = [];
  for (const iv of s) {
    const last = out[out.length - 1];
    if (last && iv[0] <= last[1] + 1e-6) last[1] = Math.max(last[1], iv[1]);
    else out.push([iv[0], iv[1]]);
  }
  return out;
}

/** Sammelt alle Wandachsen einer Ebene und klassifiziert sie als außen/innen. */
function wandAchsen(level) {
  const rooms = levelRooms(level);
  const raumAn = makeRoomAt(rooms);
  const vert = new Map(), horiz = new Map();
  const push = (m, k, iv) => { const a = m.get(k) || []; a.push(iv); m.set(k, a); };

  for (const r of rooms) for (const [x1, y1, x2, y2] of r.rects) {
    push(vert,  key(x1), [y1, y2]); push(vert,  key(x2), [y1, y2]);
    push(horiz, key(y1), [x1, x2]); push(horiz, key(y2), [x1, x2]);
  }

  const segs = [];
  const scan = (map, ax) => {
    for (const [k, ivs] of map) {
      const at = parseFloat(k);
      for (const [s0, s1] of mergeIntervals(ivs)) {
        const step = 0.10;
        let cur = null, curStart = 0;
        for (let s = s0; s < s1 - 1e-9; s += step) {
          const mid = Math.min(s + step / 2, s1);
          const a = ax === 'x' ? raumAn(at - EPS, mid) : raumAn(mid, at - EPS);
          const b = ax === 'x' ? raumAn(at + EPS, mid) : raumAn(mid, at + EPS);
          // Gleicher Raum auf beiden Seiten → nur eine Teilflächen-Naht,
          // dort darf keine Wand entstehen (z. B. quer durch die Lounge).
          const kind = (a && b) ? (a === b ? null : 'int') : (a || b) ? 'ext' : null;
          const dir  = (a && b) ? 0 : a ? +1 : -1;   // Außenrichtung
          const tag  = kind ? kind + dir : null;
          if (tag !== cur) {
            if (cur) segs.push({ ax, at, s0: curStart, s1: s, kind: cur.slice(0, 3), dir: +cur.slice(3) });
            cur = tag; curStart = s;
          }
        }
        if (cur) segs.push({ ax, at, s0: curStart, s1, kind: cur.slice(0, 3), dir: +cur.slice(3) });
      }
    }
  };
  scan(vert, 'x'); scan(horiz, 'y');
  return segs.filter(s => s.s1 - s.s0 > 0.12);
}

/* ------------------------------------------------------------------ Wände */

/**
 * Außenwände tragen den Putz auf der Außenseite – und zusätzlich auf den
 * beiden Stirnseiten. Diese Stirnflächen sind einerseits die Laibungen der
 * Fenster, andererseits stoßen benachbarte Wandstücke dort aneinander:
 * bliebe dort das weiße Innenwandmaterial stehen, zeichnete jede Stoßfuge
 * als heller Strich durch die Fassade.
 */
function wandMaterialien(M, ax, dir, aussen) {
  if (!aussen) return M.wandInnen;
  const mats = [M.wandInnen, M.wandInnen, M.wandInnen, M.wandInnen, M.wandInnen, M.wandInnen];
  if (ax === 'x') { mats[dir > 0 ? 0 : 1] = M.fassade; mats[4] = mats[5] = M.fassade; }
  else            { mats[dir > 0 ? 5 : 4] = M.fassade; mats[0] = mats[1] = M.fassade; }
  return mats;
}

/**
 * Setzt einen Wandquader; s = Achsrichtung, t = Wandstärke, [h0,h1] = Höhe.
 *
 * Die Quader werden um wenige Millimeter über ihre rechnerischen Kanten
 * hinaus gebaut. Stießen zwei Stücke exakt aneinander – etwa der Sturz über
 * einem Fenster an das anschließende Wandstück –, ließ die Fuge unter
 * flachem Blickwinkel einen haarfeinen Spalt offen; in der Fassade zeigte
 * sich das als gestrichelte helle Linien.
 */
const FUGE = 0.004;

function wandQuader(g, mat, ax, at, sA, sB, h0, h1, t) {
  const len = sB - sA + 2 * FUGE, hh = h1 - h0 + 2 * FUGE;
  if (sB - sA <= 0.01 || h1 - h0 <= 0.01) return;
  const geo = ax === 'x' ? new THREE.BoxGeometry(t, hh, len) : new THREE.BoxGeometry(len, hh, t);
  const m = new THREE.Mesh(geo, mat);
  if (ax === 'x') m.position.set(at, h0 + hh / 2, -(sA + sB) / 2);
  else            m.position.set((sA + sB) / 2, h0 + hh / 2, -at);
  m.castShadow = true; m.receiveShadow = true;
  g.add(m);
}

function verglasung(g, M, ax, at, sA, sB, h0, h1, typ) {
  const len = sB - sA, hh = h1 - h0;
  if (len <= 0.05 || hh <= 0.05) return;
  // Die Scheibe füllt die Öffnung vollständig aus. Ein kleineres Glasfeld
  // ließ ringsum einen Schlitz frei, durch den man auf die hell erleuchtete
  // Innenwand sah – als feine helle Striche neben jedem Fenster.
  const pane = ax === 'x'
    ? new THREE.BoxGeometry(0.03, hh, len)
    : new THREE.BoxGeometry(len, hh, 0.03);
  const pm = new THREE.Mesh(pane, M.glas);
  if (ax === 'x') pm.position.set(at, h0 + hh / 2, -(sA + sB) / 2);
  else            pm.position.set((sA + sB) / 2, h0 + hh / 2, -at);
  g.add(pm);

  const pf = 0.07;                                  // Profilstärke
  const rail = (a, b, hy, ht) => wandQuader(g, M.rahmen, ax, at, a, b, hy, hy + ht, pf);
  rail(sA, sB, h0, pf); rail(sA, sB, h1 - pf, pf);
  const n = Math.max(1, Math.round(len / (typ === 'glass' ? 1.35 : 1.9)));
  for (let i = 0; i <= n; i++) {
    const s = sA + len * i / n;
    const a = Math.max(sA, s - pf / 2), b = Math.min(sB, s + pf / 2);
    const geo = ax === 'x' ? new THREE.BoxGeometry(pf, hh, b - a) : new THREE.BoxGeometry(b - a, hh, pf);
    const m = new THREE.Mesh(geo, M.rahmen);
    if (ax === 'x') m.position.set(at, h0 + hh / 2, -(a + b) / 2);
    else            m.position.set((a + b) / 2, h0 + hh / 2, -at);
    g.add(m);
  }
}

function zargen(g, M, ax, at, sA, sB, h0, h1, t) {
  const p = 0.06;
  wandQuader(g, M.weiss, ax, at, sA, sA + p, h0, h1, t + 0.02);
  wandQuader(g, M.weiss, ax, at, sB - p, sB, h0, h1, t + 0.02);
  wandQuader(g, M.weiss, ax, at, sA, sB, h1 - p, h1, t + 0.02);
}

function bauWand(g, M, seg, level, base) {
  const aussen = seg.kind === 'ext';
  const t = aussen ? H.wallExt : H.wallInt;
  const wandHoehe = aussen
    ? (level === 0 ? H.ogFloor - H.egFloor : H.roof - H.ogFloor)
    : H.levelClear[level];
  const mat = wandMaterialien(M, seg.ax, seg.dir, aussen);

  const ops = OEFFNUNGEN
    .filter(o => o.level === level && o.ax === seg.ax && Math.abs(o.at - seg.at) < 0.30)
    .map(o => ({ a: Math.max(o.a, seg.s0), b: Math.min(o.b, seg.s1), sill: o.sill, top: o.top, t: o.t }))
    .filter(o => o.b - o.a > 0.10)
    .sort((x, y) => x.a - y.a);

  let cursor = seg.s0;
  for (const o of ops) {
    if (o.a > cursor) wandQuader(g, mat, seg.ax, seg.at, cursor, o.a, base, base + wandHoehe, t);
    if (o.sill > 0.02) wandQuader(g, mat, seg.ax, seg.at, o.a, o.b, base, base + o.sill, t);
    const oberkante = Math.min(base + o.top, base + wandHoehe);
    if (oberkante < base + wandHoehe - 0.02)
      wandQuader(g, mat, seg.ax, seg.at, o.a, o.b, oberkante, base + wandHoehe, t);
    if (o.t === 'glass' || o.t === 'window')
      verglasung(g, M, seg.ax, seg.at, o.a, o.b, base + o.sill, base + o.top, o.t);
    else
      zargen(g, M, seg.ax, seg.at, o.a, o.b, base + o.sill, base + o.top, t);
    cursor = o.b;
  }
  if (cursor < seg.s1) wandQuader(g, mat, seg.ax, seg.at, cursor, seg.s1, base, base + wandHoehe, t);

  return aussen ? seg : null;
}

/* -------------------------------------------------------- Böden & Decken */

function bodenMesh(M, rect, base, art) {
  const [x1, y1, x2, y2] = rect;
  const w = x2 - x1, d = y2 - y1;
  const mat = M.boden[art] ? M.boden[art]([Math.max(1, w / 2.4), Math.max(1, d / 2.4)])
                           : M.boden.fliesen([w / 2.4, d / 2.4]);
  const m = boxMesh(w, 0.08, d, mat, (x1 + x2) / 2, base - 0.04, -(y1 + y2) / 2);
  m.castShadow = false; m.receiveShadow = true;
  return m;
}

/* -------------------------------------------------------------- Dach etc. */

function dachAufbauten(g, M) {
  const kuppeln = [[5.0, 24.0], [5.0, 14.0], [13.5, 24.0], [13.5, 14.0],
                   [22.0, 24.0], [22.0, 14.0], [22.0, 5.0], [13.5, 5.0]];
  for (const [x, y] of kuppeln) {
    g.add(boxMesh(1.5, 0.28, 1.5, M.weiss, x, H.roof + 0.14, -y));
    const dome = new THREE.Mesh(
      new THREE.SphereGeometry(0.75, 18, 10, 0, Math.PI * 2, 0, Math.PI / 2.6),
      new THREE.MeshPhysicalMaterial({ color: 0xdfe9ee, roughness: 0.25,
        transparent: true, opacity: 0.62, side: THREE.DoubleSide }));
    dome.position.set(x, H.roof + 0.26, -y);
    g.add(dome);
  }
  for (const [x, y] of [[9.0, 29.5], [17.5, 29.5], [26.0, 29.5], [3.0, 8.0]]) {
    g.add(boxMesh(1.5, 0.75, 1.1, M.grau, x, H.roof + 0.38, -y));
    g.add(boxMesh(1.6, 0.10, 1.2, M.stahl, x, H.roof + 0.80, -y));
  }
  // Satellitenmast
  const mast = new THREE.Mesh(new THREE.CylinderGeometry(0.07, 0.07, 3.4, 10), M.stahlRot);
  mast.position.set(11.5, H.roof + 1.7, -29.0); g.add(mast);
  const sat = new THREE.Mesh(new THREE.SphereGeometry(0.85, 20, 12, 0, 6.3, 0, 1.0), M.rot);
  sat.position.set(11.5, H.roof + 3.1, -29.0); sat.rotation.x = 2.2; g.add(sat);
  // Steigleiter an der Ostfassade
  const lx = 30.15;
  for (const s of [-0.28, 0.28]) {
    const r = new THREE.Mesh(new THREE.CylinderGeometry(0.035, 0.035, 8.6, 8), M.weiss);
    r.position.set(lx, 4.3, -(21.0 + s)); g.add(r);
  }
  for (let i = 0; i < 26; i++)
    g.add(boxMesh(0.06, 0.04, 0.6, M.weiss, lx, 0.6 + i * 0.32, -21.0));
  for (let i = 0; i < 10; i++) {
    const ring = new THREE.Mesh(new THREE.TorusGeometry(0.38, 0.025, 6, 14, Math.PI), M.weiss);
    ring.position.set(lx - 0.30, 5.0 + i * 0.38, -21.0);
    ring.rotation.set(0, Math.PI / 2, Math.PI / 2);
    g.add(ring);
  }
}

/* ================================================================ Aufbau */

export function buildBuilding(M) {
  const root = new THREE.Group();
  const levels = [new THREE.Group(), new THREE.Group()];
  const slab = new THREE.Group();          // Geschossdecke EG → OG
  const roof = new THREE.Group();
  const pick = [];                          // unsichtbare Trefferkörper
  const overlays = new Map();               // roomId → Mesh[]
  levels[0].name = 'EG'; levels[1].name = 'OG';

  for (let lv = 0; lv < 2; lv++) {
    const g = levels[lv];
    const base = H.levelBase[lv];
    const clear = H.levelClear[lv];
    const rooms = RAEUME.filter(r => r.level === lv);

    /* Böden + Trefferkörper + Highlight-Flächen */
    for (const room of rooms) {
      const ov = [];
      for (const rect of room.rects) {
        const [x1, y1, x2, y2] = rect;
        const fm = bodenMesh(M, rect, base, room.boden);
        fm.userData.roomId = room.id;
        g.add(fm);

        const pm = new THREE.Mesh(
          new THREE.BoxGeometry(x2 - x1 - 0.05, clear * 0.9, y2 - y1 - 0.05),
          new THREE.MeshBasicMaterial());
        pm.position.set((x1 + x2) / 2, base + clear * 0.45, -(y1 + y2) / 2);
        pm.visible = false;
        pm.userData.roomId = room.id;
        pm.userData.level = lv;
        g.add(pm); pick.push(pm);

        const hm = boxMesh(x2 - x1 - 0.06, 0.05, y2 - y1 - 0.06, M.highlight,
          (x1 + x2) / 2, base + 0.05, -(y1 + y2) / 2);
        hm.visible = false; hm.castShadow = false; hm.receiveShadow = false;
        g.add(hm); ov.push(hm);
      }
      overlays.set(room.id, ov);
    }

    /* Wände */
    const aussenSegs = [];
    for (const seg of wandAchsen(lv)) {
      const ext = bauWand(g, M, seg, lv, base);
      if (ext) aussenSegs.push(ext);
    }

    /* Decke / Attika */
    if (lv === 0) {
      // Oberkante bewusst 10 cm unter OK Fertigfußboden OG, damit die
      // Bodenplatten des Obergeschosses nicht mit der Decke z-fighten.
      const top = H.ogFloor - 0.10, unten = H.egClear;
      for (const room of levelRooms(0)) for (const [x1, y1, x2, y2] of room.rects)
        slab.add(boxMesh(x2 - x1 + 0.02, top - unten, y2 - y1 + 0.02, M.slab,
          (x1 + x2) / 2, (unten + top) / 2, -(y1 + y2) / 2));
    } else {
      for (const room of levelRooms(1)) for (const [x1, y1, x2, y2] of room.rects)
        roof.add(boxMesh(x2 - x1 + 0.02, 0.42, y2 - y1 + 0.02, M.slab,
          (x1 + x2) / 2, H.roof - 0.21, -(y1 + y2) / 2));
      // Attika: außen weiter verputzt wie die Fassade, oben eine schmale
      // helle Abdeckung – so liest sich der Dachrand wie auf den Fotos.
      for (const seg of aussenSegs) {
        wandQuader(roof, wandMaterialien(M, seg.ax, seg.dir, true),
          seg.ax, seg.at, seg.s0, seg.s1, H.roof, H.roof + H.parapet - 0.09, H.wallExt);
        wandQuader(roof, M.attika,
          seg.ax, seg.at, seg.s0, seg.s1, H.roof + H.parapet - 0.09, H.roof + H.parapet, H.wallExt + 0.07);
      }
      for (const room of levelRooms(1)) for (const [x1, y1, x2, y2] of room.rects) {
        const m = boxMesh(x2 - x1, 0.04, y2 - y1, M.dach, (x1 + x2) / 2, H.roof + 0.03, -(y1 + y2) / 2);
        m.castShadow = false; roof.add(m);
      }
      dachAufbauten(roof, M);
    }

    /* Möblierung */
    for (const e of MOEBEL) {
      const room = rooms.find(r => r.id === e.room);
      if (!room) continue;
      const sub = new THREE.Group();
      buildMoebel(sub, M, room, e, base, clear);
      sub.traverse(o => { if (o.isMesh) o.userData.roomId = room.id; });
      g.add(sub);
    }
  }

  /* Balkon (aus den Fotos, nicht in den Renderings) */
  const balkon = new THREE.Group();
  const bx1 = 30.0, bx2 = 32.6, by1 = 2.0, by2 = 24.0, bh = H.ogFloor - 0.12;
  balkon.add(boxMesh(bx2 - bx1, 0.14, by2 - by1, M.stahl, (bx1 + bx2) / 2, bh, -(by1 + by2) / 2));
  for (let i = 0; i <= 14; i++) {
    const y = by1 + (by2 - by1) * i / 14;
    balkon.add(boxMesh(0.06, 1.05, 0.06, M.stahl, bx2 - 0.08, bh + 0.60, -y));
    if (i < 14) balkon.add(boxMesh(0.14, 0.14, 0.14, M.stahl, bx2 - 0.08, bh - 1.9, -y));
  }
  for (const hgt of [0.35, 0.65, 0.95, 1.08]) {
    const r = new THREE.Mesh(new THREE.BoxGeometry(0.045, 0.045, by2 - by1), M.stahl);
    r.position.set(bx2 - 0.08, bh + hgt, -(by1 + by2) / 2); balkon.add(r);
  }
  for (let i = 0; i <= 11; i++) {                        // Stützen
    const y = by1 + (by2 - by1) * i / 11;
    balkon.add(boxMesh(0.10, H.ogFloor - 0.2, 0.10, M.stahl, bx2 - 0.30, (H.ogFloor - 0.2) / 2, -y));
  }
  balkon.traverse(o => { if (o.isMesh) o.userData.roomId = 'og-balkon'; });
  levels[1].add(balkon);
  {
    const ov = boxMesh(bx2 - bx1, 0.06, by2 - by1, M.highlight,
      (bx1 + bx2) / 2, bh + 0.12, -(by1 + by2) / 2);
    ov.visible = false; levels[1].add(ov);
    overlays.set('og-balkon', [ov]);
    const pm = new THREE.Mesh(new THREE.BoxGeometry(bx2 - bx1, 1.6, by2 - by1), new THREE.MeshBasicMaterial());
    pm.position.set((bx1 + bx2) / 2, bh + 0.8, -(by1 + by2) / 2);
    pm.visible = false; pm.userData.roomId = 'og-balkon'; pm.userData.level = 1;
    levels[1].add(pm); pick.push(pm);
  }

  levels[0].add(slab);
  root.add(levels[0], levels[1], roof);
  return { root, levels, slab, roof, pick, overlays };
}

export { levelRooms, wandQuader };
