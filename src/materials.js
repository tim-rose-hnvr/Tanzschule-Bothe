/**
 * Prozedurale Materialien – erzeugt alle Texturen per Canvas,
 * damit das Modell ohne externe Bilddateien auskommt.
 */
import * as THREE from 'three';

const cache = new Map();

function canvas(w, h, draw) {
  const c = document.createElement('canvas');
  c.width = w; c.height = h;
  draw(c.getContext('2d'), w, h);
  return c;
}

function tex(key, w, h, repeat, draw) {
  if (cache.has(key)) return cache.get(key);
  const t = new THREE.CanvasTexture(canvas(w, h, draw));
  t.wrapS = t.wrapT = THREE.RepeatWrapping;
  t.repeat.set(repeat[0], repeat[1]);
  t.anisotropy = 8;
  t.colorSpace = THREE.SRGBColorSpace;
  cache.set(key, t);
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
      const v = 0.86 + rnd() * 0.26;
      ctx.fillStyle = `rgb(${Math.min(255, 199 * v)},${Math.min(255, 148 * v)},${Math.min(255, 89 * v)})`;
      ctx.fillRect(x, y, bw - 1.5, bh - 1.5);
      ctx.fillRect(x - w, y, bw - 1.5, bh - 1.5);
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
    ctx.fillRect(0, r * bh, w, bh - 1.2);
    ctx.globalAlpha = 0.12;
    for (let g = 0; g < 14; g++) {
      ctx.fillStyle = '#2a1a12';
      ctx.fillRect(rnd() * w, r * bh + rnd() * bh, 30 + rnd() * 90, 0.9);
    }
    ctx.globalAlpha = 1;
  }
}

function fliesenDraw(ctx, w, h) {
  ctx.fillStyle = '#9098a2'; ctx.fillRect(0, 0, w, h);
  const n = 8, s = w / n;
  for (let y = 0; y < n; y++) for (let x = 0; x < n; x++) {
    const v = 0.92 + rnd() * 0.16;
    ctx.fillStyle = `rgb(${Math.min(255, 144 * v)},${Math.min(255, 152 * v)},${Math.min(255, 162 * v)})`;
    ctx.fillRect(x * s + 1.2, y * s + 1.2, s - 2.4, s - 2.4);
  }
  ctx.fillStyle = 'rgba(40,46,54,.35)';
  for (let i = 0; i <= n; i++) { ctx.fillRect(i * s - 1, 0, 2, h); ctx.fillRect(0, i * s - 1, w, 2); }
}

function rasenDraw(ctx, w, h) {
  ctx.fillStyle = '#5f8f34'; ctx.fillRect(0, 0, w, h);
  for (let i = 0; i < 5000; i++) {
    const v = rnd();
    ctx.fillStyle = `rgba(${60 + v * 70 | 0},${120 + v * 70 | 0},${30 + v * 45 | 0},.55)`;
    ctx.fillRect(rnd() * w, rnd() * h, 2.2, 3.4);
  }
}

function pflasterDraw(ctx, w, h) {
  ctx.fillStyle = '#8b8d92'; ctx.fillRect(0, 0, w, h);
  const bw = w / 8, bh = h / 16;
  for (let r = 0; r < 16; r++) for (let c = 0; c < 8; c++) {
    const off = (r % 2) * bw / 2;
    const v = 0.86 + rnd() * 0.26;
    ctx.fillStyle = `rgb(${Math.min(255, 139 * v)},${Math.min(255, 141 * v)},${Math.min(255, 146 * v)})`;
    ctx.fillRect((c * bw + off) % w, r * bh, bw - 1.6, bh - 1.6);
    ctx.fillRect(((c * bw + off) % w) - w, r * bh, bw - 1.6, bh - 1.6);
  }
}

function putzDraw(ctx, w, h, base) {
  ctx.fillStyle = base; ctx.fillRect(0, 0, w, h);
  for (let i = 0; i < 9000; i++) {
    ctx.fillStyle = `rgba(0,0,0,${rnd() * 0.07})`;
    ctx.fillRect(rnd() * w, rnd() * h, 2, 2);
    ctx.fillStyle = `rgba(255,255,255,${rnd() * 0.06})`;
    ctx.fillRect(rnd() * w, rnd() * h, 2, 2);
  }
}

function dachDraw(ctx, w, h) {
  ctx.fillStyle = '#b9bcc0'; ctx.fillRect(0, 0, w, h);
  for (let i = 0; i < 4000; i++) {
    ctx.fillStyle = `rgba(0,0,0,${rnd() * 0.10})`;
    ctx.fillRect(rnd() * w, rnd() * h, 3, 3);
  }
  ctx.strokeStyle = 'rgba(90,95,100,.5)'; ctx.lineWidth = 2;
  for (let y = 0; y < h; y += h / 6) { ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(w, y); ctx.stroke(); }
}

/* --------------------------------------------------------- Beschilderung */

function schildDraw(ctx, w, h) {
  ctx.clearRect(0, 0, w, h);
  // Grundplatte
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
  // BOTHE!-Logo
  ctx.fillStyle = '#ffffff';
  ctx.fillRect(w * 0.035, h * 0.64, w * 0.34, h * 0.30);
  ctx.beginPath();
  ctx.fillStyle = '#8cc63e'; ctx.arc(w * 0.085, h * 0.79, h * 0.10, 0, 7); ctx.fill();
  ctx.beginPath();
  ctx.fillStyle = '#f4b32a'; ctx.arc(w * 0.115, h * 0.79, h * 0.10, 0, 7); ctx.fill();
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
  // stilisiertes Tanzpaar
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

export const T = {
  parkett: () => tex('parkett', 512, 512, [1, 1], parkettDraw),
  diele:   () => tex('diele',   512, 512, [1, 1], dieleDraw),
  fliesen: () => tex('fliesen', 512, 512, [1, 1], fliesenDraw),
  rasen:   () => tex('rasen',   512, 512, [1, 1], rasenDraw),
  pflaster:() => tex('pflaster',512, 512, [1, 1], pflasterDraw),
  dach:    () => tex('dach',    512, 512, [1, 1], dachDraw),
  putzRot: () => tex('putzRot', 256, 256, [1, 1], (c, w, h) => putzDraw(c, w, h, '#cf3a24')),
  putzHell:() => tex('putzHell',256, 256, [1, 1], (c, w, h) => putzDraw(c, w, h, '#e8eaed')),
};

export function schildTextur()  { return new THREE.CanvasTexture(canvas(1024, 320, schildDraw)); }
export function steleTextur()   { return new THREE.CanvasTexture(canvas(512, 768, steleDraw)); }
export function tanzbildTextur(){ return new THREE.CanvasTexture(canvas(384, 512, tanzbildDraw)); }

/* ------------------------------------------------------------ Materialien */

function bodenMat(t, rep, farbe) {
  const map = t.clone();
  map.needsUpdate = true;
  map.wrapS = map.wrapT = THREE.RepeatWrapping;
  map.repeat.set(rep[0], rep[1]);
  map.colorSpace = THREE.SRGBColorSpace;
  return new THREE.MeshStandardMaterial({ map, color: farbe || 0xffffff, roughness: 0.72, metalness: 0.02 });
}

export function makeMaterials() {
  const wandInnen = new THREE.MeshStandardMaterial({ color: 0xf2f3f5, roughness: 0.92, metalness: 0 });
  const M = {
    wandInnen,
    wandInnenXray: new THREE.MeshStandardMaterial({
      color: 0xdfe4ec, roughness: 0.9, transparent: true, opacity: 0.16,
      depthWrite: false, side: THREE.DoubleSide,
    }),
    fassade: new THREE.MeshStandardMaterial({ map: T.putzRot(), color: 0xffffff, roughness: 0.94, metalness: 0 }),
    attika:  new THREE.MeshStandardMaterial({ color: 0xf0f1f3, roughness: 0.9 }),
    decke:   new THREE.MeshStandardMaterial({ color: 0xf7f8fa, roughness: 0.95, side: THREE.DoubleSide }),
    slab:    new THREE.MeshStandardMaterial({ color: 0xe2e5ea, roughness: 0.9 }),
    // bewusst ohne `transmission`: das wäre pro Bild ein zusätzlicher
    // Renderdurchgang und bei über hundert Scheiben deutlich zu teuer.
    glas: new THREE.MeshPhysicalMaterial({
      color: 0xa8c8d4, roughness: 0.05, metalness: 0.1,
      transparent: true, opacity: 0.30, side: THREE.DoubleSide,
      envMapIntensity: 1.6, depthWrite: false,
    }),
    rahmen: new THREE.MeshStandardMaterial({ color: 0x2c3138, roughness: 0.45, metalness: 0.6 }),
    stahl:  new THREE.MeshStandardMaterial({ color: 0xa9b0b8, roughness: 0.35, metalness: 0.85 }),
    stahlRot: new THREE.MeshStandardMaterial({ color: 0xc22a1c, roughness: 0.5, metalness: 0.4 }),
    spiegel: new THREE.MeshStandardMaterial({ color: 0xdfe8ee, roughness: 0.03, metalness: 0.98 }),
    holz:    new THREE.MeshStandardMaterial({ color: 0x8a6134, roughness: 0.62 }),
    holzDunkel: new THREE.MeshStandardMaterial({ color: 0x4a3226, roughness: 0.7 }),
    weiss:   new THREE.MeshStandardMaterial({ color: 0xf4f5f7, roughness: 0.6 }),
    grau:    new THREE.MeshStandardMaterial({ color: 0x8d939c, roughness: 0.7 }),
    grauDunkel: new THREE.MeshStandardMaterial({ color: 0x40454d, roughness: 0.7 }),
    schwarz: new THREE.MeshStandardMaterial({ color: 0x1d2026, roughness: 0.55 }),
    rot:     new THREE.MeshStandardMaterial({ color: 0xd8392a, roughness: 0.6 }),
    gelb:    new THREE.MeshStandardMaterial({ color: 0xf4b32a, roughness: 0.6 }),
    gruen:   new THREE.MeshStandardMaterial({ color: 0x4f8f36, roughness: 0.8 }),
    gruenD:  new THREE.MeshStandardMaterial({ color: 0x2f6a24, roughness: 0.85 }),
    stamm:   new THREE.MeshStandardMaterial({ color: 0x6b5334, roughness: 0.9 }),
    lampe:   new THREE.MeshStandardMaterial({ color: 0xfff6e2, emissive: 0xffe9bd, emissiveIntensity: 0.9, roughness: 0.4 }),
    rasen:   bodenMat(T.rasen(), [70, 70]),
    pflaster:bodenMat(T.pflaster(), [12, 12]),
    dach:    bodenMat(T.dach(), [10, 10]),
    asphalt: new THREE.MeshStandardMaterial({ color: 0x5b6068, roughness: 0.95 }),
  };

  M.boden = {
    parkett: r => bodenMat(T.parkett(), r),
    diele:   r => bodenMat(T.diele(), r),
    fliesen: r => bodenMat(T.fliesen(), r),
    aussen:  r => bodenMat(T.pflaster(), r),
  };

  M.highlight = new THREE.MeshStandardMaterial({
    color: 0xf4b32a, emissive: 0xf4b32a, emissiveIntensity: 0.55,
    transparent: true, opacity: 0.34, depthWrite: false, side: THREE.DoubleSide,
  });
  M.select = new THREE.MeshStandardMaterial({
    color: 0xd8392a, emissive: 0xd8392a, emissiveIntensity: 0.7,
    transparent: true, opacity: 0.42, depthWrite: false, side: THREE.DoubleSide,
  });
  return M;
}
