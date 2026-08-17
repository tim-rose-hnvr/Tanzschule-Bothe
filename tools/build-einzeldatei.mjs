/**
 * Baut das gesamte Modell in eine einzige, vollständig eigenständige
 * HTML-Datei: three.js, alle Module, das Stylesheet sowie sämtliche Fotos
 * und Pläne werden eingebettet. Die Datei läuft danach ohne Server und
 * ohne Netzwerkzugriff – auch als Anhang oder auf einem USB-Stick.
 *
 *   node tools/build-einzeldatei.mjs [ziel.html]
 */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { build } from 'esbuild';

// fileURLToPath: unter Windows liefert new URL(...).pathname "/C:/…"
const ROOT = path.resolve(fileURLToPath(new URL('..', import.meta.url)));
const ZIEL = process.argv[2] || path.join(ROOT, 'dist', 'tanzhaus-3d.html');

/* 1 – Module inklusive three.js zu einem Bundle zusammenfassen */
const res = await build({
  entryPoints: [path.join(ROOT, 'src/main.js')],
  bundle: true, format: 'iife', minify: true, write: false,
  target: ['es2022'], legalComments: 'none',
  alias: { three: path.join(ROOT, 'vendor/three.module.min.js') },
});
let js = res.outputFiles[0].text;

/* 2 – Bilddateien als data:-URI einsetzen */
const mime = e => (e === '.png' ? 'image/png' : 'image/jpeg');
let eingebettet = 0, bytes = 0;
for (const ordner of ['assets/fotos', 'assets/plaene']) {
  for (const datei of fs.readdirSync(path.join(ROOT, ordner))) {
    const rel = `${ordner}/${datei}`;
    if (!js.includes(rel)) continue;
    const buf = fs.readFileSync(path.join(ROOT, rel));
    js = js.split(rel).join(`data:${mime(path.extname(datei))};base64,${buf.toString('base64')}`);
    eingebettet++; bytes += buf.length;
  }
}

/* 3 – HTML-Gerüst mit eingebettetem CSS und Skript */
const html = fs.readFileSync(path.join(ROOT, 'index.html'), 'utf8');
const css = fs.readFileSync(path.join(ROOT, 'src/styles.css'), 'utf8');

// Ersetzungen als Funktion übergeben: der minifizierte Code enthält
// $-Sequenzen, die String.replace sonst als Rückverweise interpretiert.
const out = html
  .replace('<link rel="stylesheet" href="src/styles.css">', () => `<style>\n${css}\n</style>`)
  .replace(/<script type="importmap">[\s\S]*?<\/script>\s*/, '')
  .replace('<script type="module" src="src/main.js"></script>',
           () => `<script>\n${js}\n</script>`);

fs.mkdirSync(path.dirname(ZIEL), { recursive: true });
fs.writeFileSync(ZIEL, out);

/* 4 – Variante ohne Dokumentgerüst (für Hosting-Umgebungen, die
       <!doctype>/<html>/<head>/<body> selbst beisteuern) */
const kopf = out.match(/<head>([\s\S]*?)<\/head>/)[1]
  .replace(/<meta charset[^>]*>\s*/, '')
  .replace(/<meta name="viewport"[^>]*>\s*/, '');
const rumpf = out.match(/<body>([\s\S]*?)<\/body>/)[1];
const frag = path.join(path.dirname(ZIEL), 'tanzhaus-3d.fragment.html');
fs.writeFileSync(frag, kopf.trim() + '\n' + rumpf.trim() + '\n');

const mb = n => (n / 1048576).toFixed(2) + ' MB';
console.log(`${path.relative(ROOT, ZIEL)}  ${mb(Buffer.byteLength(out))}`);
console.log(`${path.relative(ROOT, frag)}  ${mb(fs.statSync(frag).size)}`);
console.log(`  Skript ${mb(Buffer.byteLength(js))} · ${eingebettet} Bilder (${mb(bytes)} unkodiert)`);
