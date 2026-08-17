/**
 * Prozedurale Materialien – alle Texturen entstehen per Canvas, damit das
 * Modell ohne externe Bilddateien auskommt. Zu jeder Farbtextur wird aus
 * deren Helligkeit eine Normalmap abgeleitet; erst dadurch bekommen
 * Parkettfugen, Fliesenraster und Putzkorn im Streiflicht Relief.
 *
 * Die Fassadenfarbe ist aus den Originalfotos gemittelt (Straßenansicht
 * und Luftbilder liegen je nach Belichtung zwischen #b12628 und #f5582b;
 * als Albedo unter direkter Sonne trägt der mittlere, tiefere Wert).
 */
import * as THREE from 'three';

const canvasCache = new Map();
const texCache = new Map();

function makeCanvas(key, w, h, draw) {
  if (canvasCache.has(key)) return canvasCache.get(key);
  const c = document.createElement('canvas');
  c.width = w; c.height = h;
  draw(c.getContext('2d'), w, h);
  canvasCache.set(key, c);
  return c;
}

function farbTex(key, canvas, repeat) {
  const k = `f:${key}:${repeat}`;
  if (texCache.has(k)) return texCache.get(k);
  const t = new THREE.CanvasTexture(canvas);
  t.wrapS = t.wrapT = THREE.RepeatWrapping;
  t.repeat.set(repeat[0], repeat[1]);
  t.anisotropy = 8;
  t.colorSpace = THREE.SRGBColorSpace;
  texCache.set(k, t);
  return t;
}

/** Normalmap per Sobel-Filter über die Helligkeit der Farbtextur. */
function normalTex(key, canvas, staerke, repeat) {
  const k = `n:${key}:${staerke}:${repeat}`;
  if (texCache.has(k)) return texCache.get(k);
  const w = canvas.width, h = canvas.height;
  const src = canvas.getContext('2d').getImageData(0, 0, w, h).data;
  const hoehe = new Float32Array(w * h);
  for (let i = 0; i < w * h; i++)
    hoehe[i] = (src[i * 4] * 0.299 + src[i * 4 + 1] * 0.587 + src[i * 4 + 2] * 0.114) / 255;

  const out = new Uint8ClampedArray(w * h * 4);
  const at = (x, y) => hoehe[((y + h) % h) * w + ((x + w) % w)];
  for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
    const dx = (at(x - 1, y - 1) + 2 * at(x - 1, y) + at(x - 1, y + 1))
             - (at(x + 1, y - 1) + 2 * at(x + 1, y) + at(x + 1, y + 1));
    const dy = (at(x - 1, y - 1) + 2 * at(x, y - 1) + at(x + 1, y - 1))
             - (at(x - 1, y + 1) + 2 * at(x, y + 1) + at(x + 1, y + 1));
    const nx = dx * staerke, ny = dy * staerke, nz = 1;
    const len = Math.hypot(nx, ny, nz);
    const i = (y * w + x) * 4;
    out[i]     = (nx / len * 0.5 + 0.5) * 255;
    out[i + 1] = (ny / len * 0.5 + 0.5) * 255;
    out[i + 2] = (nz / len * 0.5 + 0.5) * 255;
    out[i + 3] = 255;
  }
  const t = new THREE.DataTexture(out, w, h, THREE.RGBAFormat);
  t.wrapS = t.wrapT = THREE.RepeatWrapping;
  t.repeat.set(repeat[0], repeat[1]);
  t.anisotropy = 4;
  t.needsUpdate = true;
  texCache.set(k, t);
  return t;
}

const rnd = (seed => () => (seed = (seed * 16807) % 2147483647) / 2147483647)(20220705);

/* ------------------------------------------------------------- Texturen */

function parkettDraw(ctx, w, h) {
  ctx.fillStyle = '#c39257'; ctx.fillRect(0, 0, w, h);
  const bw = w / 4, bh = h / 16;
  for (let r = 0; r < 16; r++) {
    for (let c = 0; c < 4; c++) {
      const off = (r % 2) * bw / 2;
      const x = (c * bw + off) % w, y = r * bh;
      const v = 0.88 + rnd() * 0.22;
      for (const dx of [0, -w]) {
        ctx.fillStyle = `rgb(${Math.min(255, 199 * v)},${Math.min(255, 148 * v)},${Math.min(255, 89 * v)})`;
        ctx.fillRect(x + dx, y, bw - 2.2, bh - 2.2);
      }
      ctx.globalAlpha = 0.10;
      for (let g = 0; g < 5; g++) {
        ctx.fillStyle = '#6d4a22';
        ctx.fillRect(x + rnd() * bw, y + rnd() * bh, bw * 0.5, 0.8);
      }
      ctx.globalAlpha = 1;
    }
  }
}

function dieleDraw(ctx, w, h) {
  ctx.fillStyle = '#4a3226'; ctx.fillRect(0, 0, w, h);
  const bh = h / 10;
  for (let r = 0; r < 10; r++) {
    const v = 0.78 + rnd() * 0.42;
    ctx.fillStyle = `rgb(${Math.min(255, 74 * v)},${Math.min(255, 50 * v)},${Math.min(255, 38 * v)})`;
    ctx.fillRect(0, r * bh, w, bh - 1.8);
    ctx.globalAlpha = 0.12;
    for (let g = 0; g < 14; g++) {
      ctx.fillStyle = '#2a1a12';
      ctx.fillRect(rnd() * w, r * bh + rnd() * bh, 30 + rnd() * 90, 0.9);
    }
    ctx.globalAlpha = 1;
  }
}

function fliesenDraw(ctx, w, h) {
  ctx.fillStyle = '#5e646d'; ctx.fillRect(0, 0, w, h);
  const n = 8, s = w / n;
  for (let y = 0; y < n; y++) for (let x = 0; x < n; x++) {
    const v = 0.93 + rnd() * 0.14;
    ctx.fillStyle = `rgb(${Math.min(255, 144 * v)},${Math.min(255, 152 * v)},${Math.min(255, 162 * v)})`;
    ctx.fillRect(x * s + 2, y * s + 2, s - 4, s - 4);
  }
}

function rasenDraw(ctx, w, h) {
  ctx.fillStyle = '#5a7a3c'; ctx.fillRect(0, 0, w, h);
  for (let i = 0; i < 7000; i++) {
    const v = rnd();
    ctx.fillStyle = `rgba(${62 + v * 52 | 0},${104 + v * 52 | 0},${36 + v * 34 | 0},.5)`;
    ctx.fillRect(rnd() * w, rnd() * h, 2.2, 3.4);
  }
  // größere, unscharfe Flecken – sonst wirkt der Rasen wie ein Teppich
  for (let i = 0; i < 160; i++) {
    ctx.fillStyle = `rgba(${70 + rnd() * 40 | 0},${100 + rnd() * 40 | 0},${44 + rnd() * 26 | 0},.16)`;
    ctx.beginPath(); ctx.arc(rnd() * w, rnd() * h, 12 + rnd() * 34, 0, 7); ctx.fill();
  }
}

/** Verband aus Steinen; `ton` gibt die Grundfarbe (Klinker vs. Betonplatte). */
function pflasterDraw(ctx, w, h, ton) {
  ctx.fillStyle = ton.fuge; ctx.fillRect(0, 0, w, h);
  const bw = w / 8, bh = h / 16;
  for (let r = 0; r < 16; r++) for (let c = 0; c < 8; c++) {
    const off = (r % 2) * bw / 2;
    const v = 0.84 + rnd() * 0.3;
    for (const dx of [0, -w]) {
      ctx.fillStyle = `rgb(${Math.min(255, ton.rgb[0] * v) | 0},${Math.min(255, ton.rgb[1] * v) | 0},${Math.min(255, ton.rgb[2] * v) | 0})`;
      ctx.fillRect((c * bw + off) % w + dx, r * bh, bw - 2.4, bh - 2.4);
    }
  }
}

function putzDraw(ctx, w, h, base) {
  ctx.fillStyle = base; ctx.fillRect(0, 0, w, h);
  for (let i = 0; i < 14000; i++) {
    ctx.fillStyle = `rgba(0,0,0,${rnd() * 0.09})`;
    ctx.fillRect(rnd() * w, rnd() * h, 2, 2);
    ctx.fillStyle = `rgba(255,255,255,${rnd() * 0.07})`;
    ctx.fillRect(rnd() * w, rnd() * h, 2, 2);
  }
}

function dachDraw(ctx, w, h) {
  ctx.fillStyle = '#b9bcc0'; ctx.fillRect(0, 0, w, h);
  for (let i = 0; i < 5000; i++) {
    ctx.fillStyle = `rgba(0,0,0,${rnd() * 0.12})`;
    ctx.fillRect(rnd() * w, rnd() * h, 3, 3);
  }
  ctx.strokeStyle = 'rgba(88,93,99,.55)'; ctx.lineWidth = 2.5;
  for (let y = 0; y < h; y += h / 6) { ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(w, y); ctx.stroke(); }
}

/* --------------------------------------------------------- Beschilderung */

function schildDraw(ctx, w, h) {
  ctx.clearRect(0, 0, w, h);
  ctx.fillStyle = '#e9eaec';
  ctx.fillRect(0, h * 0.06, w, h * 0.52);
  ctx.fillStyle = '#1b1d21';
  ctx.font = `800 ${h * 0.30}px "Arial Black", Impact, sans-serif`;
  ctx.textBaseline = 'middle';
  ctx.fillText('TANZHAUS', w * 0.035, h * 0.24);
  const g = ctx.createLinearGradient(0, 0, w, 0);
  g.addColorStop(0, '#f4b32a'); g.addColorStop(1, '#d8392a');
  ctx.fillStyle = g;
  ctx.fillRect(w * 0.035, h * 0.375, w * 0.60, h * 0.03);
  ctx.fillStyle = '#5d6068';
  ctx.font = `800 ${h * 0.22}px "Arial Black", Impact, sans-serif`;
  ctx.fillText('HANNOVER', w * 0.035, h * 0.48);
  ctx.fillStyle = '#ffffff';
  ctx.fillRect(w * 0.035, h * 0.64, w * 0.34, h * 0.30);
  ctx.beginPath(); ctx.fillStyle = '#8cc63e'; ctx.arc(w * 0.085, h * 0.79, h * 0.10, 0, 7); ctx.fill();
  ctx.beginPath(); ctx.fillStyle = '#f4b32a'; ctx.arc(w * 0.115, h * 0.79, h * 0.10, 0, 7); ctx.fill();
  ctx.fillStyle = '#15171b';
  ctx.font = `800 ${h * 0.21}px "Arial Black", Impact, sans-serif`;
  ctx.fillText('BOTHE!', w * 0.075, h * 0.79);
}

function steleDraw(ctx, w, h) {
  ctx.fillStyle = '#c31f18'; ctx.fillRect(0, 0, w, h);
  ctx.fillStyle = '#e9eaec'; ctx.fillRect(w * 0.05, h * 0.06, w * 0.90, h * 0.30);
  ctx.fillStyle = '#1b1d21'; ctx.textBaseline = 'middle';
  ctx.font = `800 ${h * 0.14}px "Arial Black", Impact, sans-serif`;
  ctx.fillText('TANZHAUS', w * 0.09, h * 0.15);
  ctx.fillStyle = '#5d6068';
  ctx.font = `800 ${h * 0.11}px "Arial Black", Impact, sans-serif`;
  ctx.fillText('HANNOVER', w * 0.09, h * 0.28);
  ctx.fillStyle = '#ffffff'; ctx.fillRect(w * 0.10, h * 0.50, w * 0.80, h * 0.22);
  ctx.beginPath(); ctx.fillStyle = '#8cc63e'; ctx.arc(w * 0.24, h * 0.61, h * 0.075, 0, 7); ctx.fill();
  ctx.beginPath(); ctx.fillStyle = '#f4b32a'; ctx.arc(w * 0.31, h * 0.61, h * 0.075, 0, 7); ctx.fill();
  ctx.fillStyle = '#15171b';
  ctx.font = `800 ${h * 0.15}px "Arial Black", Impact, sans-serif`;
  ctx.fillText('BOTHE!', w * 0.20, h * 0.61);
}

function tanzbildDraw(ctx, w, h) {
  ctx.fillStyle = '#f4f5f7'; ctx.fillRect(0, 0, w, h);
  ctx.strokeStyle = '#20242b'; ctx.lineWidth = w * 0.02; ctx.strokeRect(0, 0, w, h);
  ctx.fillStyle = '#20242b';
  ctx.save(); ctx.translate(w * 0.5, h * 0.58); ctx.scale(w / 100, h / 100);
  ctx.beginPath(); ctx.arc(-11, -26, 5, 0, 7); ctx.fill();
  ctx.beginPath(); ctx.moveTo(-13, -21); ctx.lineTo(-6, 2); ctx.lineTo(-14, 24); ctx.lineTo(-19, 22);
  ctx.lineTo(-12, 2); ctx.lineTo(-18, -20); ctx.closePath(); ctx.fill();
  ctx.beginPath(); ctx.arc(12, -30, 5, 0, 7); ctx.fill();
  ctx.beginPath(); ctx.moveTo(9, -25); ctx.lineTo(20, -6); ctx.lineTo(30, 22); ctx.lineTo(24, 24);
  ctx.lineTo(14, -2); ctx.lineTo(4, -20); ctx.closePath(); ctx.fill();
  ctx.lineWidth = 3; ctx.strokeStyle = '#20242b';
  ctx.beginPath(); ctx.moveTo(-14, -18); ctx.lineTo(8, -22); ctx.stroke();
  ctx.restore();
}

/* -------------------------------------------------------------- Zugriff */

const C = {
  parkett:  () => makeCanvas('parkett', 512, 512, parkettDraw),
  diele:    () => makeCanvas('diele',   512, 512, dieleDraw),
  fliesen:  () => makeCanvas('fliesen', 512, 512, fliesenDraw),
  rasen:    () => makeCanvas('rasen',   512, 512, rasenDraw),
  pflaster: () => makeCanvas('pflaster', 512, 512,
    (c, w, h) => pflasterDraw(c, w, h, { fuge: '#4c4842', rgb: [150, 143, 134] })),
  klinker:  () => makeCanvas('klinker', 512, 512,
    (c, w, h) => pflasterDraw(c, w, h, { fuge: '#4a413c', rgb: [150, 122, 106] })),
  dach:     () => makeCanvas('dach',    512, 512, dachDraw),
  putzRot:  () => makeCanvas('putzRot', 256, 256, (c, w, h) => putzDraw(c, w, h, '#c5341f')),
  putzHell: () => makeCanvas('putzHell',256, 256, (c, w, h) => putzDraw(c, w, h, '#e6e8ea')),
};

export function schildTextur()  { return new THREE.CanvasTexture(makeCanvas('schild', 1024, 320, schildDraw)); }
export function steleTextur()   { return new THREE.CanvasTexture(makeCanvas('stele', 512, 768, steleDraw)); }
export function tanzbildTextur(){ return new THREE.CanvasTexture(makeCanvas('tanzbild', 384, 512, tanzbildDraw)); }

/* ------------------------------------------------------------ Materialien */

function belag(key, canvasFn, rep, extra = {}) {
  const c = canvasFn();
  return new THREE.MeshPhysicalMaterial({
    map: farbTex(key, c, rep),
    normalMap: normalTex(key, c, extra._nStaerke ?? 1.4, rep),
    normalScale: new THREE.Vector2(extra._nSkala ?? 0.55, extra._nSkala ?? 0.55),
    roughness: 0.7, metalness: 0.0,
    ...Object.fromEntries(Object.entries(extra).filter(([k]) => !k.startsWith('_'))),
  });
}

export function makeMaterials() {
  const M = {
    wandInnen: new THREE.MeshStandardMaterial({ color: 0xeef0f3, roughness: 0.93, metalness: 0 }),
    fassade: belag('putzRot', C.putzRot, [16, 16], { roughness: 0.95, _nStaerke: 1.5, _nSkala: 0.42 }),
    attika:  belag('putzHell', C.putzHell, [16, 16], { roughness: 0.86, _nStaerke: 1.2, _nSkala: 0.3 }),
    decke:   new THREE.MeshStandardMaterial({ color: 0xf5f6f8, roughness: 0.96, side: THREE.DoubleSide }),
    slab:    new THREE.MeshStandardMaterial({ color: 0xdfe2e7, roughness: 0.92 }),

    // Flachglas: kaum Deckkraft, dafür kräftige Umgebungsspiegelung – so
    // spiegeln sich Himmel und Bäume wie auf den Fotos in der Saalfassade.
    glas: new THREE.MeshPhysicalMaterial({
      color: 0x93b3c2, roughness: 0.035, metalness: 0.18,
      transparent: true, opacity: 0.22, side: THREE.DoubleSide,
      envMapIntensity: 2.4, depthWrite: false,
      clearcoat: 1.0, clearcoatRoughness: 0.03,
    }),
    rahmen: new THREE.MeshStandardMaterial({ color: 0x2a2f36, roughness: 0.38, metalness: 0.7 }),
    stahl:  new THREE.MeshStandardMaterial({ color: 0xa6adb5, roughness: 0.3, metalness: 0.9 }),
    stahlRot: new THREE.MeshStandardMaterial({ color: 0xba2a1c, roughness: 0.45, metalness: 0.35 }),
    spiegel: new THREE.MeshStandardMaterial({ color: 0xe6eef3, roughness: 0.02, metalness: 1.0, envMapIntensity: 1.6 }),
    holz:    new THREE.MeshStandardMaterial({ color: 0x8a6134, roughness: 0.58 }),
    holzDunkel: new THREE.MeshStandardMaterial({ color: 0x46301f, roughness: 0.66 }),
    weiss:   new THREE.MeshStandardMaterial({ color: 0xf2f4f6, roughness: 0.55 }),
    grau:    new THREE.MeshStandardMaterial({ color: 0x8d939c, roughness: 0.66 }),
    grauDunkel: new THREE.MeshStandardMaterial({ color: 0x3c414a, roughness: 0.66 }),
    schwarz: new THREE.MeshStandardMaterial({ color: 0x191c21, roughness: 0.5 }),
    rot:     new THREE.MeshStandardMaterial({ color: 0xc9341f, roughness: 0.55 }),
    gelb:    new THREE.MeshStandardMaterial({ color: 0xf4b32a, roughness: 0.55 }),
    gruen:   new THREE.MeshStandardMaterial({ color: 0x4a7a30, roughness: 0.85 }),
    gruenD:  new THREE.MeshStandardMaterial({ color: 0x33591f, roughness: 0.88 }),
    laub1:   new THREE.MeshStandardMaterial({ color: 0x5c8438, roughness: 0.9 }),
    laub2:   new THREE.MeshStandardMaterial({ color: 0x3f6425, roughness: 0.92 }),
    schirm:  new THREE.MeshStandardMaterial({ color: 0xb32217, roughness: 0.72, side: THREE.DoubleSide }),
    stoff:   new THREE.MeshStandardMaterial({ color: 0xc0301c, roughness: 0.8, side: THREE.DoubleSide }),
    stamm:   new THREE.MeshStandardMaterial({ color: 0x6b5334, roughness: 0.92 }),
    lampe:   new THREE.MeshStandardMaterial({ color: 0xfff6e2, emissive: 0xffe6b4, emissiveIntensity: 1.1, roughness: 0.35 }),
    rasen:   belag('rasen', C.rasen, [70, 70], { roughness: 0.94, _nStaerke: 0.9, _nSkala: 0.35 }),
    pflaster:belag('pflaster', C.pflaster, [10, 10], { roughness: 0.84, _nStaerke: 2.2, _nSkala: 0.7 }),
    klinker: belag('klinker', C.klinker, [16, 16], { roughness: 0.88, _nStaerke: 2.4, _nSkala: 0.75 }),
    dach:    belag('dach', C.dach, [10, 10], { roughness: 0.88, _nStaerke: 1.6, _nSkala: 0.5 }),
    asphalt: new THREE.MeshStandardMaterial({ color: 0x4e535b, roughness: 0.96 }),
  };

  // Tanzparkett ist versiegelt – deshalb Klarlackschicht statt matter
  // Oberfläche; das ergibt die typischen langen Reflexe der Saalfotos.
  M.boden = {
    parkett: r => belag('parkett', C.parkett, r,
      { roughness: 0.34, clearcoat: 0.62, clearcoatRoughness: 0.16, _nStaerke: 1.2, _nSkala: 0.45 }),
    diele:   r => belag('diele', C.diele, r,
      { roughness: 0.58, clearcoat: 0.25, clearcoatRoughness: 0.4, _nStaerke: 1.6, _nSkala: 0.6 }),
    fliesen: r => belag('fliesen', C.fliesen, r,
      { roughness: 0.28, clearcoat: 0.4, clearcoatRoughness: 0.15, _nStaerke: 2.4, _nSkala: 0.75 }),
    aussen:  r => belag('pflaster', C.pflaster, r, { roughness: 0.84, _nStaerke: 2.2, _nSkala: 0.7 }),
  };

  // Zurückhaltender als früher: mit der neuen Belichtung überstrahlte die
  // Auswahlfläche den ganzen Saal und verdeckte Boden und Möblierung.
  M.highlight = new THREE.MeshStandardMaterial({
    color: 0xf4b32a, emissive: 0xf4b32a, emissiveIntensity: 0.3,
    transparent: true, opacity: 0.2, depthWrite: false, side: THREE.DoubleSide,
  });
  M.select = new THREE.MeshStandardMaterial({
    color: 0xd8392a, emissive: 0xd8392a, emissiveIntensity: 0.38,
    transparent: true, opacity: 0.26, depthWrite: false, side: THREE.DoubleSide,
  });
  M.sockel = new THREE.MeshStandardMaterial({ color: 0xdfe3e8, roughness: 0.7 });
  return M;
}
