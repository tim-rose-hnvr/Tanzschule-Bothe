/** Schnelle Bildkontrolle: rendert feste Kamerastandpunkte nach .look/ */
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { chromium } from 'playwright';

const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..');
const OUT = path.join(ROOT, '.look');
const TYPES = { '.html':'text/html', '.js':'text/javascript', '.css':'text/css',
                '.jpg':'image/jpeg', '.png':'image/png' };
const server = http.createServer((req, res) => {
  let p = decodeURIComponent(req.url.split('?')[0]);
  if (p === '/') p = '/index.html';
  const f = path.join(ROOT, p);
  if (!f.startsWith(ROOT) || !fs.existsSync(f) || fs.statSync(f).isDirectory()) { res.writeHead(404); return res.end(); }
  res.writeHead(200, { 'content-type': TYPES[path.extname(f)] || 'application/octet-stream', 'cache-control': 'no-store' });
  fs.createReadStream(f).pipe(res);
});
await new Promise(r => server.listen(0, r));
fs.mkdirSync(OUT, { recursive: true });

const browser = await chromium.launch({
  executablePath: process.env.CHROMIUM_PATH || '/opt/pw-browsers/chromium-1194/chrome-linux/chrome',
  args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--no-sandbox'],
});
const page = await browser.newPage({ viewport: { width: 1100, height: 700 } });
const fehler = [];
page.on('pageerror', e => fehler.push('pageerror: ' + e.message));
page.on('console', m => { if (m.type() === 'error') fehler.push('console: ' + m.text()); });
await page.goto(`http://127.0.0.1:${server.address().port}`, { waitUntil: 'load' });
await page.waitForTimeout(9000);

// Oberfläche ausblenden – hier zählt nur das gerenderte Bild
await page.addStyleTag({ content: '#topbar,#sidebar,#toolbar,#labels,#hint,#detail,#tourbar{display:none!important}' });

const blicke = [
  ['a-aussen-sued',  [ 2, 12, 40], [16, 4, -6],  'all', true],
  ['b-strasse',      [22, 3.5, 22], [14, 4, 1],  'all', true],
  ['c-garten',       [46, 6, -6],  [31, 3, -16], 'all', true],
  ['d-eg-innen',     [ 8, 26, 20], [15, 1, -4],  0,     false],
  ['e-saal',         [18.5, 1.7, -12],[27, 2.4, -24], 0, false],
  ['f-og',           [12, 31, 10], [23.5, 5.5, -19], 1, false],
  ['g-luftbild',     [50, 40, 28], [15, 4, -15], 'all', true],
];

for (const [name, cam, ziel, level, dach] of blicke) {
  await page.evaluate(([cam, ziel, level, dach]) => {
    const T = globalThis.TANZHAUS;
    const btn = document.querySelector(`.level-switch button[data-level="${level}"]`);
    if (btn && !btn.classList.contains('active')) btn.click();
    const d = document.querySelector('[data-toggle="roof"]');
    if (d.classList.contains('active') !== !!dach) d.click();
    T.steuerung.flyTo(cam, ziel, 1);
  }, [cam, ziel, level, dach]);
  await page.waitForTimeout(1400);
  await page.screenshot({ path: path.join(OUT, name + '.png') });
  console.log('→', name);
}

const perf = await page.evaluate(() => new Promise(res => {
  let n = 0; const t0 = performance.now();
  const f = () => { if (++n < 40) requestAnimationFrame(f); else res(Math.round(1000 * n / (performance.now() - t0))); };
  requestAnimationFrame(f);
}));
console.log('fps (SwiftShader, nur Anhaltspunkt):', perf);
console.log(fehler.length ? 'FEHLER: ' + [...new Set(fehler)].slice(0, 3).join(' | ') : 'keine Fehler');
await browser.close(); server.close();
