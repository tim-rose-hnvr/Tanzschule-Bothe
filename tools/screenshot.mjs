/**
 * Entwicklungs-Hilfsskript: startet einen kleinen Static-Server, lädt das
 * Modell in Chromium und legt Screenshots ab. Aufruf:
 *   node tools/screenshot.mjs [ausgabeVerzeichnis]
 */
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { chromium } from 'playwright';

const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..');
const OUT = process.argv[2] || path.join(ROOT, '.shots');
const TYPES = {
  '.html': 'text/html', '.js': 'text/javascript', '.mjs': 'text/javascript',
  '.css': 'text/css', '.jpg': 'image/jpeg', '.png': 'image/png', '.json': 'application/json',
};

const server = http.createServer((req, res) => {
  let p = decodeURIComponent(req.url.split('?')[0]);
  if (p === '/') p = '/index.html';
  const file = path.join(ROOT, p);
  if (!file.startsWith(ROOT) || !fs.existsSync(file) || fs.statSync(file).isDirectory()) {
    res.writeHead(404); return res.end('not found');
  }
  res.writeHead(200, { 'content-type': TYPES[path.extname(file)] || 'application/octet-stream' });
  fs.createReadStream(file).pipe(res);
});

await new Promise(r => server.listen(0, r));
const base = `http://127.0.0.1:${server.address().port}`;
fs.mkdirSync(OUT, { recursive: true });

const browser = await chromium.launch({
  executablePath: process.env.CHROMIUM_PATH || '/opt/pw-browsers/chromium-1194/chrome-linux/chrome',
  args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--no-sandbox'],
});
const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
const fehler = [];
page.on('console', m => { if (m.type() === 'error') fehler.push('console: ' + m.text()); });
page.on('pageerror', e => fehler.push('pageerror: ' + e.message));
page.on('requestfailed', r => fehler.push('request: ' + r.url() + ' ' + r.failure()?.errorText));

await page.goto(base, { waitUntil: 'load' });
await page.waitForTimeout(6500);

const shots = [
  ['01-uebersicht', async () => {}],
  ['02-eg', async () => { await page.click('.level-switch button[data-level="0"]'); await page.waitForTimeout(700); }],
  ['03-og', async () => { await page.click('.level-switch button[data-level="1"]'); await page.waitForTimeout(700); }],
  ['04-explosion', async () => {
      await page.click('.level-switch button[data-level="all"]');
      await page.$eval('#explode', e => { e.value = 70; e.dispatchEvent(new Event('input')); });
      await page.waitForTimeout(1400);
  }],
  ['05-dach', async () => {
      await page.$eval('#explode', e => { e.value = 0; e.dispatchEvent(new Event('input')); });
      await page.click('[data-toggle="roof"]');
      await page.waitForTimeout(1200);
  }],
  ['06-raum-detail', async () => {
      await page.click('[data-toggle="roof"]');
      await page.evaluate(() => document.querySelector('.room-item[data-id="eg-saal-ost"]').click());
      await page.waitForTimeout(2200);
  }],
  ['07-tour', async () => { await page.click('#btn-tour'); await page.waitForTimeout(2400); }],
  ['08-tour-lounge', async () => {
      for (let i = 0; i < 2; i++) { await page.click('#tour-next'); await page.waitForTimeout(1500); }
  }],
  ['09-tour-saal', async () => {
      for (let i = 0; i < 2; i++) { await page.click('#tour-next'); await page.waitForTimeout(1500); }
  }],
  ['10-tour-garten', async () => {
      for (let i = 0; i < 3; i++) { await page.click('#tour-next'); await page.waitForTimeout(1500); }
  }],
  ['11-tour-og', async () => {
      for (let i = 0; i < 2; i++) { await page.click('#tour-next'); await page.waitForTimeout(1500); }
  }],
  ['12-begehen', async () => {
      await page.click('#tour-stop'); await page.waitForTimeout(300);
      await page.click('.level-switch button[data-level="0"]'); await page.waitForTimeout(300);
      await page.evaluate(() => {
        TANZHAUS.steuerung.setModus('walk');
        TANZHAUS.steuerung.pos.set(17.5, 1.65, -6);
        TANZHAUS.steuerung.yaw = 0.35;
      });
      await page.click('[data-mode="walk"]');
      await page.waitForTimeout(900);
  }],
  ['13-roentgen', async () => {
      await page.click('[data-mode="orbit"]');
      await page.click('.level-switch button[data-level="all"]');
      await page.click('[data-toggle="walls"]');
      await page.waitForTimeout(1400);
  }],
];

for (const [name, act] of shots) {
  await act();
  await page.waitForTimeout(900);   // Headless-Renderer braucht einen Moment, bis das UI neu gemalt ist
  await page.screenshot({ path: path.join(OUT, name + '.png') });
  console.log('→', name);
}

const stats = await page.evaluate(() => ({
  calls: TANZHAUS.scene.children.length,
  meshes: (() => { let n = 0; TANZHAUS.scene.traverse(o => { if (o.isMesh) n++; }); return n; })(),
}));
console.log('Meshes:', stats.meshes);
console.log(fehler.length ? 'FEHLER:\n' + [...new Set(fehler)].join('\n') : 'keine Konsolenfehler');

await browser.close();
server.close();
