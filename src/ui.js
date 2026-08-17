/**
 * Bedienoberfläche: Seitenleiste, Detailfenster, Lightbox, Tour-Leiste.
 * Kommuniziert ausschließlich über das von main.js übergebene `app`-Objekt.
 */
import { RAEUME, HIGHLIGHTS, KATEGORIEN, BODEN, FOTOS, PLAENE, INFO, TOUR, STANDORT } from './data.js';
import { standortHtml, karteNachladen } from './standort.js';

const $ = s => document.querySelector(s);
const el = (t, cls, html) => {
  const n = document.createElement(t);
  if (cls) n.className = cls;
  if (html != null) n.innerHTML = html;
  return n;
};
const esc = s => String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));

export function flaeche(room) {
  return room.rects.reduce((s, [x1, y1, x2, y2]) => s + (x2 - x1) * (y2 - y1), 0);
}
function abmessung(room) {
  let x1 = Infinity, y1 = Infinity, x2 = -Infinity, y2 = -Infinity;
  for (const r of room.rects) {
    x1 = Math.min(x1, r[0]); y1 = Math.min(y1, r[1]);
    x2 = Math.max(x2, r[2]); y2 = Math.max(y2, r[3]);
  }
  return `${(x2 - x1).toFixed(1)} × ${(y2 - y1).toFixed(1)} m`;
}

export function initUI(app) {
  const roomList = $('#room-list');
  const detail = $('#detail');
  const detailBody = $('#detail-body');
  let galerie = [], galerieIndex = 0;

  /* ------------------------------------------------------- Seitenleiste */
  function buildList(filter = '') {
    roomList.innerHTML = '';
    const f = filter.trim().toLowerCase();
    const passt = t => !f || t.toLowerCase().includes(f);

    const highlights = HIGHLIGHTS.filter(h => passt(h.name + ' ' + h.kurz));
    if (highlights.length) {
      roomList.append(gruppe('Highlights'));
      for (const h of highlights) {
        const b = el('button', 'room-item poi');
        b.dataset.id = h.id;
        b.innerHTML = `<span class="swatch"></span><span class="nm">${esc(h.nr + '. ' + h.name)}</span>`;
        b.onclick = () => app.select(h.id, true);
        roomList.append(b);
      }
    }

    for (const lv of [0, 1]) {
      const raeume = RAEUME.filter(r => r.level === lv && passt(r.name + ' ' + r.kurz));
      if (!raeume.length) continue;
      roomList.append(gruppe(lv === 0 ? 'Erdgeschoss' : '1. Obergeschoss'));
      raeume.sort((a, b) => flaeche(b) - flaeche(a));
      for (const r of raeume) {
        const b = el('button', 'room-item');
        b.dataset.id = r.id;
        b.innerHTML =
          `<span class="swatch" style="background:${KATEGORIEN[r.kat].css}"></span>` +
          `<span class="nm">${esc(r.name)}</span>` +
          `<span class="qm">${Math.round(flaeche(r))} m²</span>`;
        b.onclick = () => app.select(r.id, true);
        roomList.append(b);
      }
    }
    if (!roomList.children.length)
      roomList.append(el('div', 'group-head', 'Kein Treffer'));
  }
  const gruppe = t => el('div', 'group-head', `${esc(t)}<span class="rule"></span>`);

  $('#search').addEventListener('input', e => buildList(e.target.value));

  function markActive(id) {
    roomList.querySelectorAll('.room-item').forEach(b =>
      b.classList.toggle('active', b.dataset.id === id));
  }

  /* ----------------------------------------------------- Detailfenster */
  function fotoGrid(keys) {
    if (!keys || !keys.length) return '';
    return `<div class="d-h">Fotos</div><div class="thumbs">` +
      keys.map(k => FOTOS[k] ? `<button data-foto="${k}"><img src="${FOTOS[k].src}" alt="${esc(FOTOS[k].titel)}" loading="lazy"></button>` : '').join('') +
      `</div>`;
  }

  function showRaum(r) {
    galerie = (r.fotos || []).map(k => FOTOS[k]).filter(Boolean);
    const kat = KATEGORIEN[r.kat];
    detailBody.innerHTML = `
      <div class="d-kicker">${esc(r.level === 0 ? 'Erdgeschoss' : '1. Obergeschoss')} · ${esc(kat.label)}</div>
      <h2 class="d-title">${esc(r.name)}</h2>
      <div class="d-sub">${esc(r.kurz)}</div>
      <div class="facts">
        <div class="fact"><b>${Math.round(flaeche(r))} m²</b><span>Grundfläche</span></div>
        <div class="fact"><b>${abmessung(r)}</b><span>Ausdehnung</span></div>
        <div class="fact"><b>${esc(BODEN[r.boden].label)}</b><span>Bodenbelag</span></div>
        <div class="fact"><b>${r.level === 0 ? '4,10 m' : '3,70 m'}</b><span>lichte Höhe</span></div>
      </div>
      <p>${esc(r.text)}</p>
      ${r.merkmale?.length ? `<div class="d-h">Im Modell erkennbar</div><ul class="merkmale">${
        r.merkmale.map(m => `<li>${esc(m)}</li>`).join('')}</ul>` : ''}
      ${fotoGrid(r.fotos)}
      <button class="btn-fly" data-fly="${r.id}">▶ Kamera auf diesen Raum</button>
      <div style="margin-top:16px">${r.sicher
        ? '<span class="badge sure">aus dem Plan gesichert</span>'
        : '<span class="badge assumed">Nutzung abgeleitet</span>'}</div>
      ${!r.sicher ? `<div class="note">Der Raum ist im Rendering unbeschriftet. Name und Nutzung
        sind aus Bodenbelag, Zuschnitt und Lage erschlossen – sie können abweichen.</div>` : ''}
      <div class="src">Quelle: ${esc(r.quelle)}</div>`;
    openDetail();
  }

  function showHighlight(h) {
    galerie = (h.fotos || []).map(k => FOTOS[k]).filter(Boolean);
    detailBody.innerHTML = `
      <div class="d-kicker">Highlight ${h.nr} · aus den Fotos</div>
      <h2 class="d-title">${esc(h.name)}</h2>
      <div class="d-sub">${esc(h.kurz)}</div>
      <p>${esc(h.text)}</p>
      ${h.merkmale?.length ? `<div class="d-h">Details</div><ul class="merkmale">${
        h.merkmale.map(m => `<li>${esc(m)}</li>`).join('')}</ul>` : ''}
      ${fotoGrid(h.fotos)}
      <button class="btn-fly" data-fly="${h.id}">▶ Kamera auf dieses Highlight</button>
      <div class="src">Quelle: ${esc(h.quelle)}</div>`;
    openDetail();
  }

  detailBody.addEventListener('click', e => {
    const f = e.target.closest('[data-foto]');
    if (f) { openLightbox(galerie, galerie.findIndex(g => g.src === FOTOS[f.dataset.foto].src)); return; }
    const fl = e.target.closest('[data-fly]');
    if (fl) app.flyTo(fl.dataset.fly);
  });

  // closeDetail schließt nur das Panel; das Abwählen läuft immer über
  // app.select(null) – sonst rufen sich beide gegenseitig endlos auf.
  const openDetail = () => detail.classList.add('open');
  const closeDetail = () => detail.classList.remove('open');
  $('#detail-close').onclick = () => app.select(null);

  /* --------------------------------------------------------- Lightbox */
  const lb = $('#lightbox'), lbImg = $('#lb-img'), lbCap = $('#lb-cap');
  function openLightbox(list, idx = 0) {
    if (!list.length) return;
    galerie = list; galerieIndex = Math.max(0, idx);
    renderLightbox(); lb.hidden = false;
  }
  function renderLightbox() {
    const g = galerie[galerieIndex];
    lbImg.src = g.src; lbImg.alt = g.titel;
    lbCap.innerHTML = `<strong>${esc(g.titel)}</strong><br>${esc(g.cap)}`;
  }
  const step = d => { galerieIndex = (galerieIndex + d + galerie.length) % galerie.length; renderLightbox(); };
  $('#lb-prev').onclick = () => step(-1);
  $('#lb-next').onclick = () => step(1);
  $('#lb-close').onclick = () => { lb.hidden = true; };
  lb.addEventListener('click', e => { if (e.target === lb) lb.hidden = true; });

  /* ------------------------------------------------------------ Modal */
  const modal = $('#modal'), modalBody = $('#modal-body');
  const openModal = html => { modalBody.innerHTML = html; modal.hidden = false; };
  $('#modal-close').onclick = () => { modal.hidden = true; };
  modal.addEventListener('click', e => { if (e.target === modal) modal.hidden = true; });

  $('#btn-standort').onclick = () => { openModal(standortHtml()); karteNachladen(); };

  $('#btn-help').onclick = () => openModal(`
    <h2>So funktioniert das Modell</h2>
    <p>Ein aus den Grundriss-Renderings und Fotos der Tanzschule Bothe rekonstruiertes,
       begehbares 3D-Modell des Tanzhauses Hannover.</p>
    <h3>Steuerung</h3>
    <div class="keys">
      <kbd>Ziehen</kbd><span>Modell drehen</span>
      <kbd>Rechts&nbsp;/&nbsp;Shift+Ziehen</kbd><span>Ansicht verschieben</span>
      <kbd>Scrollen</kbd><span>Zoomen</span>
      <kbd>Klick</kbd><span>Raum auswählen und Infos öffnen</span>
      <kbd>W A S D</kbd><span>im Modus „Begehen“ laufen</span>
      <kbd>Q&nbsp;/&nbsp;E</kbd><span>im Modus „Begehen“ tiefer / höher</span>
      <kbd>Shift</kbd><span>schneller laufen</span>
      <kbd>Esc</kbd><span>Auswahl aufheben</span>
    </div>
    <h3>Werkzeuge</h3>
    <ul>
      <li><b>EG / 1. OG / Beide</b> – Etage ein- und ausblenden.</li>
      <li><b>Dach</b> – Flachdach mit Lichtkuppeln ein- und ausblenden.</li>
      <li><b>Röntgen</b> – Wände transparent schalten, um in alle Räume zu sehen.</li>
      <li><b>Explosion</b> – die beiden Geschosse auseinanderziehen.</li>
      <li><b>Qualität</b> – Umgebungsverdeckung und Auflösung abstufen, falls es ruckelt.
          Das Modell stuft bei niedriger Bildrate auch selbst herunter.</li>
      <li><b>Tour</b> – geführter Rundgang durch ${TOUR.length} Stationen.</li>
    </ul>
    <h3>Pläne, Fotos &amp; Standort</h3>
    <p>Die Originaldateien liegen hinter <b>Quellen &amp; Methodik</b>, Adresse und
       Karte hinter <b>Standort &amp; Karte</b> – beides unten in der Seitenleiste.</p>`);

  $('#btn-sources').onclick = () => openModal(`
    <h2>Quellen &amp; Methodik</h2>
    <p>Grundlage ist ausschließlich der Drive-Ordner
       <b>${esc(INFO.quellordner)}</b> mit zwölf Dateien:</p>
    <ul>${INFO.dateien.map(d => `<li>${esc(d)}</li>`).join('')}</ul>
    <h3>Originalpläne ansehen</h3>
    <div class="thumbs" id="plan-thumbs">${PLAENE.map((p, i) =>
      `<button data-plan="${i}"><img src="${p.src}" alt="${esc(p.titel)}" loading="lazy"></button>`).join('')}</div>
    <h3>Originalfotos ansehen</h3>
    <div class="thumbs" id="foto-thumbs">${Object.entries(FOTOS).map(([k, f]) =>
      `<button data-galfoto="${k}"><img src="${f.src}" alt="${esc(f.titel)}" loading="lazy"></button>`).join('')}</div>
    <h3>Wie belastbar ist das Modell?</h3>
    <ul>${INFO.hinweise.map(h => `<li>${esc(h)}</li>`).join('')}</ul>
    <p style="margin-top:16px"><a href="${INFO.quellLink}" target="_blank" rel="noopener"
       style="color:var(--rot-hell)">Drive-Ordner öffnen ↗</a></p>`);

  modalBody.addEventListener('click', e => {
    const p = e.target.closest('[data-plan]');
    if (p) { modal.hidden = true; openLightbox(PLAENE, +p.dataset.plan); return; }
    const f = e.target.closest('[data-galfoto]');
    if (f) {
      const list = Object.values(FOTOS);
      modal.hidden = true;
      openLightbox(list, list.findIndex(x => x.src === FOTOS[f.dataset.galfoto].src));
    }
  });

  /* --------------------------------------------------------- Werkzeuge */
  document.querySelectorAll('.level-switch button').forEach(b => {
    b.onclick = () => {
      document.querySelectorAll('.level-switch button').forEach(x => x.classList.remove('active'));
      b.classList.add('active');
      app.setLevel(b.dataset.level === 'all' ? 'all' : +b.dataset.level);
    };
  });
  document.querySelectorAll('[data-mode]').forEach(b => {
    b.onclick = () => {
      document.querySelectorAll('[data-mode]').forEach(x => x.classList.remove('active'));
      b.classList.add('active');
      app.setModus(b.dataset.mode);
    };
  });
  document.querySelectorAll('[data-toggle]').forEach(b => {
    b.onclick = () => {
      b.classList.toggle('active');
      app.toggle(b.dataset.toggle, b.classList.contains('active'));
    };
  });
  $('#explode').addEventListener('input', e => app.setExplode(+e.target.value / 100));
  $('#qualitaet').addEventListener('change', e => { e.target.title = ''; app.setQualitaet(e.target.value); });
  $('#btn-menu').onclick = () => $('#sidebar').classList.toggle(
    innerWidth <= 900 ? 'open' : 'hidden');

  /* -------------------------------------------------------------- Tour */
  const tourbar = $('#tourbar');
  $('#btn-tour').onclick = () => app.tour('start');
  $('#tour-prev').onclick = () => app.tour('prev');
  $('#tour-next').onclick = () => app.tour('next');
  $('#tour-stop').onclick = () => app.tour('stop');

  function setTour(i) {
    if (i == null) { tourbar.hidden = true; return; }
    tourbar.hidden = false;
    $('#tour-title').textContent = TOUR[i].titel;
    $('#tour-step').textContent = `Station ${i + 1} von ${TOUR.length}`;
  }

  /* ------------------------------------------------------------ Tasten */
  addEventListener('keydown', e => {
    if (e.target.tagName === 'INPUT') return;
    if (e.key === 'Escape') {
      if (!lb.hidden) lb.hidden = true;
      else if (!modal.hidden) modal.hidden = true;
      else app.select(null);
    }
    if (!lb.hidden) { if (e.key === 'ArrowRight') step(1); if (e.key === 'ArrowLeft') step(-1); }
  });

  buildList();
  return { buildList, markActive, showRaum, showHighlight, closeDetail, setTour, openLightbox };
}
