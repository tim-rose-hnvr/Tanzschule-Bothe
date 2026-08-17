/**
 * Tanzhaus Hannover – interaktives 3D-Modell
 * Einstiegspunkt: Szene, Beleuchtung, Interaktion, Tour.
 */
import * as THREE from 'three';
import { RAEUME, HIGHLIGHTS, TOUR, H, KATEGORIEN } from './data.js';
import { makeMaterials } from './materials.js';
import { buildBuilding } from './building.js';
import { buildSite } from './site.js';
import { Steuerung } from './controls.js';
import { initUI, flaeche } from './ui.js';
import { baueHimmel, sonnenRichtung, Bildkette, Leistungswaechter } from './render.js';

/* ------------------------------------------------------------- Renderer */

const canvas = document.getElementById('scene');
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, powerPreference: 'high-performance' });
// Auf 1x-Displays leicht überabtasten: das Gebäude besteht aus vielen
// aneinanderstoßenden Quadern, deren Stoßkanten sonst als feine helle
// Striche im Putz aliasen. Auf hochauflösenden Displays reicht 2x.
const PIXELRATIO = Math.min(Math.max(devicePixelRatio, 1.5), 2);
renderer.setPixelRatio(PIXELRATIO);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 0.82;
renderer.outputColorSpace = THREE.SRGBColorSpace;

const scene = new THREE.Scene();
scene.fog = new THREE.FogExp2(0xc6d6e4, 0.0013);

const camera = new THREE.PerspectiveCamera(48, 1, 0.25, 700);

baueHimmel(scene, renderer);

/* ---------------------------------------------------------- Beleuchtung */

// Himmelslicht schwächer als früher: die Umgebungsreflexion aus der
// Himmels-Cubemap übernimmt jetzt den größten Teil der diffusen Aufhellung.
scene.add(new THREE.HemisphereLight(0xcfe3ff, 0x6b6a55, 0.38));

const sonne = new THREE.DirectionalLight(0xfff1d9, 2.6);
sonne.position.copy(sonnenRichtung(95)).add(new THREE.Vector3(15, 0, -15));
sonne.castShadow = true;
sonne.shadow.mapSize.set(4096, 4096);
sonne.shadow.camera.left = -34; sonne.shadow.camera.right = 46;
sonne.shadow.camera.top = 44;   sonne.shadow.camera.bottom = -38;
sonne.shadow.camera.near = 20;  sonne.shadow.camera.far = 190;
sonne.shadow.bias = -0.0006;
sonne.shadow.normalBias = 0.03;
sonne.shadow.radius = 2.2;
sonne.target.position.set(15, 2, -15);
scene.add(sonne, sonne.target);

// Schwaches Gegenlicht aus Nordost, damit die Schattenseiten nicht
// vollständig in der Umgebungsfarbe absaufen.
const fuell = new THREE.DirectionalLight(0xbfd6f5, 0.45);
fuell.position.set(70, 26, -70);
scene.add(fuell);

/* -------------------------------------------------------------- Aufbau */

const M = makeMaterials();
const bau = buildBuilding(M);
const site = buildSite(M);
scene.add(bau.root, site);

/* Kleinteile werfen keinen Schatten – spart einen Großteil der Draw-Calls */
const _box = new THREE.Box3(), _size = new THREE.Vector3();
bau.root.traverse(o => {
  if (!o.isMesh || !o.geometry) return;
  o.geometry.computeBoundingBox();
  o.geometry.boundingBox.getSize(_size);
  if (Math.max(_size.x, _size.y, _size.z) < 0.9) o.castShadow = false;
});

/* ------------------------------------------------------- Bildaufbereitung */

const kette = new Bildkette(renderer, scene, camera);
const waechter = new Leistungswaechter(kette, stufe => {
  const sel = document.getElementById('qualitaet');
  if (sel) {
    sel.value = stufe;
    sel.title = 'automatisch heruntergestuft, weil die Bildrate eingebrochen ist';
  }
});

const RAUM = new Map(RAEUME.map(r => [r.id, r]));
const POI = new Map(HIGHLIGHTS.map(h => [h.id, h]));

/* --------------------------------------------------------- POI-Marker */

const poiGroup = new THREE.Group();
scene.add(poiGroup);
const poiMeshes = [];
for (const h of HIGHLIGHTS) {
  const g = new THREE.Group();
  const kugel = new THREE.Mesh(
    new THREE.SphereGeometry(0.42, 20, 14),
    new THREE.MeshStandardMaterial({ color: 0xf4b32a, emissive: 0xf4b32a, emissiveIntensity: 0.75, roughness: 0.35 }));
  const ring = new THREE.Mesh(
    new THREE.TorusGeometry(0.9, 0.05, 8, 32),
    new THREE.MeshBasicMaterial({ color: 0xf4b32a, transparent: true, opacity: 0.6 }));
  ring.rotation.x = Math.PI / 2;
  const stiel = new THREE.Mesh(
    new THREE.CylinderGeometry(0.035, 0.035, 1.2, 8),
    new THREE.MeshBasicMaterial({ color: 0xf4b32a, transparent: true, opacity: 0.45 }));
  stiel.position.y = -0.75;
  g.add(kugel, ring, stiel);
  g.position.set(h.pos[0], h.pos[2], -h.pos[1]);
  g.userData = { poiId: h.id, level: h.level, ring };
  poiGroup.add(g);
  poiMeshes.push(kugel);
  kugel.userData.poiId = h.id;
}

/* ------------------------------------------------------------- Zustand */

const S = {
  level: 'all',
  roof: false,
  xray: false,
  labels: true,
  pois: true,
  explode: 0,
  sel: null,
  hov: null,
  tour: null,
};

const steuerung = new Steuerung(camera, canvas);
const ui = initUI({
  select: (id, fly) => waehle(id, fly),
  flyTo: id => kamera(id),
  setLevel: v => setLevel(v),
  setModus: m => { steuerung.setModus(m); hinweisAus(); },
  toggle: (n, on) => setToggle(n, on),
  setExplode: v => { S.explode = v; },
  setQualitaet: v => { kette.setStufe(v); waechter.fertig = true; },
  tour: cmd => tour(cmd),
});

/* --------------------------------------------------------- Sichtbarkeit */

function setLevel(v) {
  S.level = v;
  bau.levels[0].visible = v !== 1;
  bau.levels[1].visible = v !== 0;
  bau.slab.visible = v !== 0;
  // Bei Einzeletagen ist das Dach immer im Weg – dann grundsätzlich aus.
  bau.roof.visible = S.roof && v === 'all';
  steuerung.etageBasis = v === 1 ? H.ogFloor : 0;
  if (S.sel) {
    const r = RAUM.get(S.sel);
    if (r && v !== 'all' && r.level !== v) waehle(null);
  }
}

function setToggle(n, on) {
  if (n === 'roof') { S.roof = on; bau.roof.visible = on && S.level === 'all'; }
  if (n === 'labels') S.labels = on;
  if (n === 'pois') { S.pois = on; poiGroup.visible = on; }
  if (n === 'walls') {
    S.xray = on;
    for (const m of [M.wandInnen, M.fassade, M.slab, M.attika]) {
      m.transparent = on;
      m.opacity = on ? 0.20 : 1;
      m.depthWrite = !on;
      m.needsUpdate = true;
    }
  }
}
setLevel('all');
setToggle('roof', true);
document.querySelector('[data-toggle="roof"]').classList.add('active');

/* ------------------------------------------------------------- Auswahl */

function setOverlay(id, mat) {
  const ov = bau.overlays.get(id);
  if (!ov) return;
  for (const m of ov) { m.visible = !!mat; if (mat) m.material = mat; }
}

function waehle(id, fly = false) {
  if (S.sel && S.sel !== id) setOverlay(S.sel, null);
  S.sel = id;
  ui.markActive(id);
  if (!id) { ui.closeDetail(); return; }

  const r = RAUM.get(id);
  if (r) {
    // Beim gezielten Anspringen die passende Etage freistellen – sonst
    // verdeckt das Obergeschoss den angewählten Raum im Erdgeschoss.
    if (fly ? S.level !== r.level : (S.level !== 'all' && S.level !== r.level))
      document.querySelector(`.level-switch button[data-level="${r.level}"]`).click();
    setOverlay(id, M.select);
    ui.showRaum(r);
  } else if (POI.has(id)) {
    if (fly && S.level !== 'all')
      document.querySelector('.level-switch button[data-level="all"]').click();
    ui.showHighlight(POI.get(id));
  }
  if (fly) kamera(id);
  hinweisAus();
}

/** Kamerafahrt auf einen Raum oder ein Highlight */
function kamera(id) {
  const r = RAUM.get(id);
  if (r) {
    let x1 = Infinity, y1 = Infinity, x2 = -Infinity, y2 = -Infinity;
    for (const q of r.rects) {
      x1 = Math.min(x1, q[0]); y1 = Math.min(y1, q[1]);
      x2 = Math.max(x2, q[2]); y2 = Math.max(y2, q[3]);
    }
    const cx = (x1 + x2) / 2, cy = (y1 + y2) / 2;
    const base = H.levelBase[r.level] + S.explode * (r.level === 1 ? 9 : 0);
    // Steiler Einblickwinkel (~60°), sonst verdeckt die 4,5 m hohe
    // Außenwand den Raum, in den man hineinschauen will.
    const d = Math.max(11, Math.hypot(x2 - x1, y2 - y1) * 1.2);
    steuerung.flyTo([cx - d * 0.36, base + d * 0.98, -cy + d * 0.52], [cx, base + 1.4, -cy]);
    return;
  }
  const h = POI.get(id);
  if (h) {
    // Kamera nach außen versetzen: Richtung von der Gebäudemitte zum Marker,
    // damit sie nicht im Baukörper landet.
    const p = [h.pos[0], h.pos[2] + (h.level === 1 ? S.explode * 9 : 0), -h.pos[1]];
    let dx = p[0] - 15, dz = p[2] + 15;
    const l = Math.hypot(dx, dz) || 1;
    dx /= l; dz /= l;
    const d = 17;
    steuerung.flyTo([p[0] + dx * d, p[1] + d * 0.5, p[2] + dz * d], p, 1300);
  }
}

/* ---------------------------------------------------------------- Tour */

function tour(cmd) {
  if (cmd === 'stop') { S.tour = null; ui.setTour(null); waehle(null); return; }
  if (cmd === 'start') S.tour = 0;
  else if (cmd === 'next') S.tour = (S.tour + 1) % TOUR.length;
  else if (cmd === 'prev') S.tour = (S.tour - 1 + TOUR.length) % TOUR.length;
  const t = TOUR[S.tour];
  ui.setTour(S.tour);

  const btn = document.querySelector(`.level-switch button[data-level="${t.level}"]`);
  if (btn && !btn.classList.contains('active')) btn.click();
  const dachBtn = document.querySelector('[data-toggle="roof"]');
  if (dachBtn.classList.contains('active') !== !!t.dach) dachBtn.click();

  if (S.sel) setOverlay(S.sel, null);
  S.sel = t.id;
  ui.markActive(t.id);
  if (RAUM.has(t.id)) { setOverlay(t.id, M.select); ui.showRaum(RAUM.get(t.id)); }
  else ui.showHighlight(POI.get(t.id));
  steuerung.flyTo(t.cam, t.ziel, 1500);
  hinweisAus();
}

/* --------------------------------------------------------------- Picking */

const ray = new THREE.Raycaster();
const maus = new THREE.Vector2();

function pickListe() {
  const l = bau.pick.filter(p => S.level === 'all' || p.userData.level === S.level);
  if (S.pois) l.push(...poiMeshes.filter(m => S.level === 'all' || POI.get(m.userData.poiId).level === S.level));
  return l;
}

function treffer(ev) {
  const rect = canvas.getBoundingClientRect();
  maus.x = ((ev.clientX - rect.left) / rect.width) * 2 - 1;
  maus.y = -((ev.clientY - rect.top) / rect.height) * 2 + 1;
  ray.setFromCamera(maus, camera);
  const hits = ray.intersectObjects(pickListe(), false);
  return hits.length ? (hits[0].object.userData.roomId || hits[0].object.userData.poiId) : null;
}

steuerung.onKlick = ev => {
  const id = treffer(ev);
  if (id) waehle(id);
  else waehle(null);
};

canvas.addEventListener('pointermove', ev => {
  if (ev.pointerType === 'touch') return;
  const id = treffer(ev);
  if (id === S.hov) return;
  if (S.hov && S.hov !== S.sel) setOverlay(S.hov, null);
  S.hov = id;
  if (id && id !== S.sel && bau.overlays.has(id)) setOverlay(id, M.highlight);
  canvas.style.cursor = id ? 'pointer' : 'grab';
});

/* ------------------------------------------------------- Beschriftungen */

const labelRoot = document.getElementById('labels');
const labels = [];
for (const r of RAEUME) {
  const gross = r.rects.reduce((a, b) =>
    (b[2] - b[0]) * (b[3] - b[1]) > (a[2] - a[0]) * (a[3] - a[1]) ? b : a);
  const d = document.createElement('div');
  d.className = 'lbl';
  d.textContent = r.name;
  labelRoot.append(d);
  labels.push({
    el: d, id: r.id, level: r.level, poi: false,
    p: new THREE.Vector3((gross[0] + gross[2]) / 2, H.levelBase[r.level] + 1.3, -(gross[1] + gross[3]) / 2),
    min: flaeche(r) > 60 ? 0 : 34,
  });
}
for (const h of HIGHLIGHTS) {
  const d = document.createElement('div');
  d.className = 'lbl poi';
  d.innerHTML = `<span class="n">${h.nr}</span>${h.name}`;
  d.onclick = () => waehle(h.id, true);
  labelRoot.append(d);
  labels.push({
    el: d, id: h.id, level: h.level, poi: true,
    p: new THREE.Vector3(h.pos[0], h.pos[2] + 1.1, -h.pos[1]), min: 0,
  });
}

const _v = new THREE.Vector3();
const belegt = [];   // bereits platzierte Beschriftungen (Bildschirmrechtecke)

function updateLabels() {
  const w = canvas.clientWidth, hgt = canvas.clientHeight;
  const kandidaten = [];

  for (const l of labels) {
    // In der Gesamtansicht verdeckt erst das Dach, dann die Geschossdecke
    // die darunter liegenden Räume – deren Namen wären reine Geisterschrift.
    const raumSichtbar = S.labels && (S.level !== 'all'
      ? true
      : !S.roof && (l.level === 1 || explodeIst > 0.15 || S.xray));
    const sichtbar = (l.poi ? S.pois : raumSichtbar) &&
                     (S.level === 'all' || l.level === S.level);
    if (!sichtbar) { l.el.style.display = 'none'; continue; }
    _v.copy(l.p);
    if (l.level === 1) _v.y += explodeIst * 9;
    const welt = _v.clone();
    _v.project(camera);
    const dist = camera.position.distanceTo(welt);
    if (_v.z > 1 || Math.abs(_v.x) > 1.05 || Math.abs(_v.y) > 1.05 ||
        dist > 150 || (l.min && dist > 60)) {
      l.el.style.display = 'none'; continue;
    }
    kandidaten.push({ l, dist, x: (_v.x * 0.5 + 0.5) * w, y: (-_v.y * 0.5 + 0.5) * hgt });
  }

  // Highlights zuerst, dann nach Kameranähe – so verdrängen wichtige
  // Marker die weiter entfernten Raumnamen und nicht umgekehrt.
  kandidaten.sort((a, b) => (b.l.poi - a.l.poi) || (a.dist - b.dist));
  belegt.length = 0;

  for (const k of kandidaten) {
    const el = k.l.el;
    if (!k.l.w) {                       // Größe einmalig messen und merken
      el.style.display = '';
      k.l.w = el.offsetWidth || 90;
      k.l.h = el.offsetHeight || 20;
    }
    const x1 = k.x - k.l.w / 2, y1 = k.y - k.l.h / 2;
    const x2 = x1 + k.l.w, y2 = y1 + k.l.h;
    let frei = true;
    for (const b of belegt)
      if (x1 < b[2] + 4 && x2 > b[0] - 4 && y1 < b[3] + 3 && y2 > b[1] - 3) { frei = false; break; }
    if (!frei) { el.style.display = 'none'; continue; }
    belegt.push([x1, y1, x2, y2]);
    el.style.display = '';
    el.style.left = k.x + 'px';
    el.style.top = k.y + 'px';
    el.style.opacity = String(Math.max(0.3, 1 - k.dist / 170));
  }
}

/* ------------------------------------------------------------ Hinweise */

const hinweis = document.getElementById('hint');
let hinweisTimer = setTimeout(() => hinweis.classList.add('gone'), 8000);
function hinweisAus() { clearTimeout(hinweisTimer); hinweis.classList.add('gone'); }

/* -------------------------------------------------------- Renderschleife */

function resize() {
  const w = canvas.clientWidth || innerWidth, h = canvas.clientHeight || innerHeight;
  if (canvas.width !== w * renderer.getPixelRatio() || canvas.height !== h * renderer.getPixelRatio()) {
    renderer.setSize(w, h, false);
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
    kette?.setGroesse(w, h);
  }
}
addEventListener('resize', resize);

let last = performance.now();
let explodeIst = 0;
function loop(now) {
  const dt = Math.min(0.05, (now - last) / 1000); last = now;
  resize();
  steuerung.update(dt);

  explodeIst += (S.explode - explodeIst) * Math.min(1, dt * 7);
  bau.levels[1].position.y = explodeIst * 9;
  bau.roof.position.y = explodeIst * 13;

  const t = now * 0.0016;
  for (const g of poiGroup.children) {
    g.userData.ring.scale.setScalar(1 + Math.sin(t + g.position.x) * 0.13);
    g.userData.ring.rotation.z = t * 0.6;
    g.visible = S.level === 'all' || g.userData.level === S.level;
    if (g.userData.level === 1) g.position.y = POI.get(g.userData.poiId).pos[2] + explodeIst * 9;
  }

  updateLabels();
  kette.render();
  waechter.tick(dt);
  requestAnimationFrame(loop);
}

/* ------------------------------------------------------------- Start */

resize();
renderer.compile(scene, camera);
requestAnimationFrame(loop);
setTimeout(() => document.getElementById('loader').classList.add('gone'), 260);
setTimeout(() => document.getElementById('loader').remove(), 1200);

// Eröffnungsfahrt: Anflug von Südost – zeigt Eingangsseite und Garten,
// danach wird das Dach abgenommen und der Blick ins Haus freigegeben.
steuerung.radius = 165; steuerung.theta = 0.85; steuerung.phi = 0.52;
steuerung.flyTo([62, 34, 44], [16, 3, -14], 2600);
setTimeout(() => {
  document.querySelector('[data-toggle="roof"]').click();
  steuerung.flyTo([48, 42, 34], [16, 3, -15], 1700);
}, 3000);

// Für Debug/Konsole
globalThis.TANZHAUS = { THREE, scene, camera, renderer, bau, site, M, S, steuerung, kette, KATEGORIEN };
