/** Kurzer Funktionstest ohne Screenshots – prüft DOM-Zustände nach Interaktionen. */
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { chromium } from 'playwright';

const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..');
const TYPES = { '.html':'text/html', '.js':'text/javascript', '.mjs':'text/javascript',
                '.css':'text/css', '.jpg':'image/jpeg', '.png':'image/png' };
const server = http.createServer((req, res) => {
  let p = decodeURIComponent(req.url.split('?')[0]);
  if (p === '/') p = '/index.html';
  const f = path.join(ROOT, p);
  if (!f.startsWith(ROOT) || !fs.existsSync(f) || fs.statSync(f).isDirectory()) { res.writeHead(404); return res.end(); }
  res.writeHead(200, { 'content-type': TYPES[path.extname(f)] || 'application/octet-stream' });
  fs.createReadStream(f).pipe(res);
});
await new Promise(r => server.listen(0, r));
const base = `http://127.0.0.1:${server.address().port}`;

const browser = await chromium.launch({
  executablePath: process.env.CHROMIUM_PATH || '/opt/pw-browsers/chromium-1194/chrome-linux/chrome',
  args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--no-sandbox'],
});
const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
const errs = [];
page.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
page.on('pageerror', e => errs.push('pageerror: ' + e.message));
page.on('requestfailed', r => errs.push('404/failed: ' + r.url()));
await page.goto(base, { waitUntil: 'load' });
await page.waitForTimeout(5000);

const zustand = () => page.evaluate(() => ({
  level: [...document.querySelectorAll('.level-switch button')].find(b => b.classList.contains('active'))?.dataset.level,
  aktivListe: document.querySelector('.room-item.active')?.textContent.trim(),
  detailTitel: document.querySelector('.d-title')?.textContent.trim(),
  tour: document.querySelector('#tour-step')?.textContent,
  S: { level: TANZHAUS.S.level, sel: TANZHAUS.S.sel, roof: TANZHAUS.S.roof },
  sichtbar: { l0: TANZHAUS.bau.levels[0].visible, l1: TANZHAUS.bau.levels[1].visible,
              slab: TANZHAUS.bau.slab.visible, roof: TANZHAUS.bau.roof.visible },
}));

console.log('start        ', JSON.stringify(await zustand()));
await page.click('.level-switch button[data-level="0"]'); await page.waitForTimeout(300);
console.log('nach EG      ', JSON.stringify(await zustand()));
await page.click('.level-switch button[data-level="1"]'); await page.waitForTimeout(300);
console.log('nach 1.OG    ', JSON.stringify(await zustand()));
await page.click('.level-switch button[data-level="all"]'); await page.waitForTimeout(300);
console.log('nach Beide   ', JSON.stringify(await zustand()));

await page.evaluate(() => document.querySelector('.room-item[data-id="eg-saal-ost"]').click());
await page.waitForTimeout(600);
console.log('Saal Ost EG  ', JSON.stringify(await zustand()));

await page.click('#btn-tour'); await page.waitForTimeout(600);
console.log('Tour 1       ', JSON.stringify(await zustand()));
for (let i = 0; i < 6; i++) { await page.click('#tour-next'); await page.waitForTimeout(450); }
console.log('Tour 7       ', JSON.stringify(await zustand()));
await page.click('#tour-next'); await page.waitForTimeout(450);
console.log('Tour 8       ', JSON.stringify(await zustand()));

console.log(errs.length ? 'FEHLER: ' + [...new Set(errs)].join(' | ') : 'keine Fehler');
await browser.close(); server.close();
