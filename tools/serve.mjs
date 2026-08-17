/**
 * Kleiner Entwicklungsserver ohne Abhängigkeiten.
 *
 *   node tools/serve.mjs             → http://localhost:8080
 *   node tools/serve.mjs 3000        → anderer Port
 *   node tools/serve.mjs --open      → öffnet zusätzlich den Browser
 *   node tools/serve.mjs --host      → auch aus dem lokalen Netz erreichbar
 *
 * Warum überhaupt ein Server: das Modell besteht aus ES-Modulen, die der
 * Browser über `file://` aus Sicherheitsgründen nicht laden darf. Außerdem
 * bettet das Standortfenster eine Google-Karte ein – die kommt nur über
 * http(s) an, nicht über eine lokal geöffnete Datei.
 */
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { spawn } from 'node:child_process';

// fileURLToPath statt new URL(...).pathname: unter Windows liefert pathname
// "/C:/Users/…", woraus path.resolve "\C:\Users\…" macht – ein Pfad ohne
// Laufwerk, unter dem keine einzige Datei gefunden wird. Der Server lieferte
// dann für alles 404, die Seite blieb leer.
const ROOT = path.resolve(fileURLToPath(new URL('..', import.meta.url)));

const args = process.argv.slice(2);
const OPEN = args.includes('--open');
const HOST_OFFEN = args.includes('--host');
const START_PORT = Number(args.find(a => /^\d+$/.test(a))) || 8080;
const BIND = HOST_OFFEN ? '0.0.0.0' : '127.0.0.1';

const TYPEN = {
  '.html': 'text/html; charset=utf-8',
  '.js':   'text/javascript; charset=utf-8',
  '.mjs':  'text/javascript; charset=utf-8',
  '.css':  'text/css; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.svg':  'image/svg+xml',
  '.jpg':  'image/jpeg', '.jpeg': 'image/jpeg',
  '.png':  'image/png',  '.webp': 'image/webp',
  '.ico':  'image/x-icon',
  '.woff2':'font/woff2',
  '.map':  'application/json; charset=utf-8',
};

/* --------------------------------------------- Vorabprüfung des Ordners */

if (!fs.existsSync(path.join(ROOT, 'index.html'))) {
  console.error(`\n  Fehler: in ${ROOT} liegt keine index.html.`);
  console.error(`  Das Skript erwartet, dass es unter <Projekt>/tools/ liegt.`);
  console.error(`  Node-Version: ${process.version}\n`);
  process.exit(1);
}

/* ------------------------------------------------------------- Server */

const server = http.createServer((req, res) => {
  let rel;
  try {
    rel = decodeURIComponent(new URL(req.url, 'http://localhost').pathname);
  } catch {
    res.writeHead(400).end('ungültige Adresse');
    return;
  }
  if (rel.endsWith('/')) rel += 'index.html';

  const datei = path.resolve(ROOT, '.' + rel);
  const melde = code => console.log(`  ${code}  ${rel}`);

  // Ausbruch aus dem Projektordner verhindern (…/../etc/passwd)
  if (datei !== ROOT && !datei.startsWith(ROOT + path.sep)) {
    melde(403);
    res.writeHead(403, { 'content-type': 'text/plain; charset=utf-8' })
       .end('außerhalb des Projektordners');
    return;
  }
  if (!fs.existsSync(datei) || fs.statSync(datei).isDirectory()) {
    melde(404);
    res.writeHead(404, { 'content-type': 'text/plain; charset=utf-8' });
    res.end(`404 – ${rel} nicht gefunden\nProjektordner: ${ROOT}`);
    return;
  }

  melde(200);
  res.writeHead(200, {
    'content-type': TYPEN[path.extname(datei).toLowerCase()] || 'application/octet-stream',
    'cache-control': 'no-store',          // im Entwicklungsbetrieb nie cachen
  });
  fs.createReadStream(datei).pipe(res);
});

// Genau einmal melden, und zwar mit dem Port, auf dem der Server wirklich
// hängt. Ein an `listen()` übergebener Rückruf bliebe nach einem
// fehlgeschlagenen Versuch registriert – dann würde die Meldung mehrfach
// und mit dem falschen, weil belegten Port erscheinen.
server.once('listening', () => {
  const url = `http://localhost:${server.address().port}/`;
  console.log(`\n  Tanzhaus Hannover – 3D-Modell`);
  console.log(`  ${url}`);
  if (HOST_OFFEN) console.log(`  im Netz erreichbar (Bindung 0.0.0.0)`);
  console.log(`\n  Ordner: ${ROOT}`);
  console.log(`  Node:   ${process.version}\n`);
  console.log(`  Beenden mit Strg+C\n`);
  if (OPEN) oeffne(url);
});

/** Belegten Port überspringen statt mit EADDRINUSE abzubrechen. */
function starte(port, versuche = 12) {
  server.once('error', err => {
    if (err.code === 'EADDRINUSE' && versuche > 0) {
      console.log(`  Port ${port} ist belegt – versuche ${port + 1} …`);
      starte(port + 1, versuche - 1);
    } else {
      console.error(`\n  ${err.message}\n`);
      process.exit(1);
    }
  });
  server.listen(port, BIND);
}

function oeffne(url) {
  const [befehl, argumente] =
      process.platform === 'darwin' ? ['open', [url]]
    : process.platform === 'win32'  ? ['cmd', ['/c', 'start', '', url]]
    : ['xdg-open', [url]];
  // `spawn` meldet ein fehlendes Programm über ein 'error'-Ereignis, nicht
  // über eine Ausnahme. Ohne diesen Zuhörer beendet sich der Server auf
  // Systemen ohne xdg-open mit einem Absturz, statt einfach weiterzulaufen.
  const kind = spawn(befehl, argumente, { stdio: 'ignore', detached: true });
  kind.on('error', () => console.log('  (Browser ließ sich nicht öffnen – Adresse oben aufrufen)\n'));
  kind.unref();
}

starte(START_PORT);
