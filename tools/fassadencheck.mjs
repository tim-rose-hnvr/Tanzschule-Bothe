/** Zählt helle Ausreißer auf der Südfassade – Maß für Fugen-/Kantenartefakte. */
import http from 'node:http'; import fs from 'node:fs'; import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { chromium } from 'playwright';
// fileURLToPath: unter Windows liefert new URL(...).pathname "/C:/…"
const ROOT = path.resolve(fileURLToPath(new URL('..', import.meta.url)));
const TY={'.html':'text/html','.js':'text/javascript','.css':'text/css','.jpg':'image/jpeg','.png':'image/png'};
const s=http.createServer((q,r)=>{let p=decodeURIComponent(q.url.split('?')[0]);if(p==='/')p='/index.html';
 const f=path.join(ROOT,p); if(!f.startsWith(ROOT)||!fs.existsSync(f)||fs.statSync(f).isDirectory()){r.writeHead(404);return r.end();}
 r.writeHead(200,{'content-type':TY[path.extname(f)]||'application/octet-stream','cache-control':'no-store'});
 fs.createReadStream(f).pipe(r);});
await new Promise(r=>s.listen(0,r));
const b=await chromium.launch({executablePath:process.env.CHROMIUM_PATH||'/opt/pw-browsers/chromium-1194/chrome-linux/chrome',
 args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--no-sandbox']});
const p=await b.newPage({viewport:{width:900,height:600}});
await p.goto(`http://127.0.0.1:${s.address().port}`,{waitUntil:'load'}); await p.waitForTimeout(9000);
await p.addStyleTag({content:'#topbar,#sidebar,#toolbar,#labels,#hint,#detail,#tourbar{display:none!important}'});
await p.evaluate(()=>TANZHAUS.steuerung.flyTo([2,12,40],[16,4,-6],1)); await p.waitForTimeout(1400);
await p.screenshot({path:'/tmp/check.png'});
console.log('bild: /tmp/check.png');
await b.close(); s.close();
