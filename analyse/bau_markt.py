#!/usr/bin/env python3
"""Baut die vollumfängliche Marktanalyse Hannover."""
import html, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "analyse"))
from markt_daten import ANBIETER, SICHTBARKEIT, PORTALE

WURZEL = pathlib.Path(__file__).resolve().parent.parent
SP = WURZEL / "quellen"
FONTS = (SP / "fonts-marke.css").read_text(encoding="utf-8")

E = lambda s: html.escape(str(s), quote=True)
WIR = next(a for a in ANBIETER if a["wir"])

# Alle Stile, die mindestens zwei Anbieter führen — sonst wird die Matrix unlesbar
ALLE_STILE = ["Standard", "Latein", "Discofox", "Salsa", "Bachata", "West Coast Swing",
              "Hip Hop", "Breakdance", "Contemporary", "Ballett", "Kindertanz",
              "Linedance", "Hochzeit", "Privatstunde"]


def kriterien(a):
    """Zehn objektiv prüfbare Basissignale. None-Werte zählen als nicht erfüllt."""
    if a["desc"] is None:
        return None
    return sum([
        0 < (a["desc"] or 0) <= 165,
        a["h1"] == 1,
        (a["h2"] or 0) > 0,
        (a["ld"] or 0) > 0,
        (a["og"] or 0) > 0,
        (a["ttfb"] or 9) < 1.0,
        0 < (a["kb"] or 0) < 150,
        (a["webp"] or 0) > 0,
        (a["seiten"] or 0) >= 20,
        a["voll"] is not None,
    ])


# ---------------------------------------------------------------- Preisgrafik
def preisgrafik():
    rows = sorted([a for a in ANBIETER if a["voll"]], key=lambda x: x["voll"])
    mx = max(r["voll"] for r in rows)
    out = ['<div class="chart" role="img" aria-label="Monatspreis für Vollzugang je Anbieter, '
           'von 15,50 € bis 90,00 €. Familie Bothe liegt mit 61,00 € auf Platz vier von sieben.">']
    for r in rows:
        w = r["voll"] / mx * 100
        cls = " ist-wir" if r["wir"] else ""
        out.append(
            f'<div class="crow{cls}">'
            f'<div class="cname">{E(r["kurz"])}<small>{E(r["voll_label"])}</small></div>'
            f'<div class="ctrack"><div class="cbar" style="width:{w:.1f}%"></div>'
            f'<span class="cval">{r["voll"]:.2f} €</span></div>'
            f'<div class="cbind">{E(r["bindung"])}</div></div>')
    out.append("</div>")
    return "\n".join(out)


# ------------------------------------------------------------- Anbieterprofil
def profil(a):
    c1 = a["farben"][0]
    c2 = a["farben"][1] if len(a["farben"]) > 1 else c1
    swat = "".join(f'<span class="sw" style="background:{c}" title="{c}">{c}</span>'
                   for c in a["farben"])
    preise = "".join(
        f'<tr><td>{E(n)}</td><td class="n">{p:.2f} €</td><td>{E(d)}</td>'
        f'<td><span class="q q-{"w" if q == "Website" else "s"}">{E(q)}</span></td></tr>'
        for n, p, d, q in a["preise"]) or \
        '<tr><td colspan="4" class="leer">Keine Preise auf der Website veröffentlicht.</td></tr>'
    stile = "".join(f'<span class="st">{E(s)}</span>' for s in a["stile"])
    k = kriterien(a)
    kbadge = f'{k}/10' if k is not None else '—'
    mess = ("<dl class='mess'>"
            f"<div><dt>Antwortzeit</dt><dd>{a['ttfb']:.2f} s</dd></div>"
            f"<div><dt>Seitengewicht</dt><dd>{a['kb']} kB</dd></div>"
            f"<div><dt>Seiten</dt><dd>{a['seiten']}</dd></div>"
            f"<div><dt>Beschreibung</dt><dd>{a['desc']} Z.</dd></div>"
            f"<div><dt>H1</dt><dd>{a['h1']}×</dd></div>"
            f"<div><dt>Schema</dt><dd>{a['ld']}</dd></div>"
            "</dl>") if a["ttfb"] is not None else \
           "<p class='leer'>Während der gesamten Erhebung nicht erreichbar — keine Messwerte.</p>"

    return f"""
<article class="prof{' prof-wir' if a['wir'] else ''}" style="--c1:{c1};--c2:{c2}">
  <div class="pbar"></div>
  <div class="pin">
    <div class="phead">
      <div>
        <div class="pseg">{E(a['seg'])} · {E(a['ort'])}{' · seit ' + str(a['gegruendet']) if a['gegruendet'] else ''}</div>
        <h3>{E(a['name'])}</h3>
        <div class="pdom">{E(a['dom'])}</div>
      </div>
      <div class="pscore"><b>{kbadge}</b><span>Basissignale</span></div>
    </div>
    <div class="pfarben"><span class="plabel">Markenfarben</span>{swat}
      <span class="pquelle">{E(a['farbquelle'])}</span></div>
    {mess}
    <div class="pcols">
      <div><span class="plabel">Stärke</span><p>{E(a['staerke'])}</p></div>
      <div><span class="plabel">Schwäche</span><p>{E(a['schwaeche'])}</p></div>
    </div>
    <span class="plabel">Tanzangebot</span><div class="stile">{stile}</div>
    <span class="plabel">Preise</span>
    <div class="scroller"><table class="ptab">
      <thead><tr><th>Tarif</th><th>Preis</th><th>Bedingungen</th><th>Quelle</th></tr></thead>
      <tbody>{preise}</tbody></table></div>
  </div>
</article>"""


# ------------------------------------------------------------------ Matrix
def matrix():
    kopf = "".join(f"<th>{E(s)}</th>" for s in ALLE_STILE)
    zeilen = []
    for a in sorted(ANBIETER, key=lambda x: (not x["wir"], -len(x["stile"]))):
        zellen = "".join(
            f'<td class="{"ja" if s in a["stile"] else "nein"}">'
            f'{"●" if s in a["stile"] else "·"}</td>' for s in ALLE_STILE)
        zeilen.append(f'<tr class="{"us" if a["wir"] else ""}">'
                      f'<td class="mname">{E(a["kurz"])}</td>{zellen}'
                      f'<td class="n">{len(a["stile"])}</td></tr>')
    return (f'<div class="scroller"><table class="matrix"><thead><tr><th>Anbieter</th>{kopf}'
            f'<th>Σ</th></tr></thead><tbody>{"".join(zeilen)}</tbody></table></div>')


# ------------------------------------------------------------- Sichtbarkeit
def sicht():
    tag = {"ja": ("t-ok", "sichtbar"), "teil": ("t-mid", "nur Sammelseite"),
           "falsch": ("t-mid", "falscher Titel"), "nein": ("t-no", "nicht sichtbar")}
    out = ['<div class="vis">']
    for s in SICHTBARKEIT:
        cls, lbl = tag[s["status"]]
        andere = " · ".join(E(x) for x in s["andere"])
        out.append(
            f'<div class="vrow"><div class="vq">{E(s["q"])}<small>{E(s["note"])}</small></div>'
            f'<div><span class="tag {cls}">{lbl}</span></div>'
            f'<div class="vwho"><b>Familie Bothe:</b> {E(s["wir"])}<br>'
            f'<span class="vand">Ebenfalls dort: {andere}</span></div></div>')
    out.append("</div>")
    return "\n".join(out)


# ------------------------------------------------------------------- Technik
def technik():
    rows = sorted([a for a in ANBIETER if a["ttfb"] is not None],
                  key=lambda x: -(kriterien(x) or 0))
    tr = []
    for a in rows:
        k = kriterien(a)
        cls = "t-ok" if k >= 7 else "t-mid" if k >= 4 else "t-no"
        tr.append(
            f'<tr class="{"us" if a["wir"] else ""}"><td>{E(a["kurz"])}</td>'
            f'<td>{E(a["seg"])}</td>'
            f'<td class="n">{a["desc"]}</td><td class="n">{a["h1"]}</td><td class="n">{a["h2"]}</td>'
            f'<td class="n">{a["ld"]}</td><td class="n">{a["og"]}</td><td class="n">{a["webp"]}</td>'
            f'<td class="n">{a["ttfb"]:.2f} s</td><td class="n">{a["kb"]} kB</td>'
            f'<td class="n">{a["seiten"]}</td>'
            f'<td><span class="tag {cls}">{k}/10</span></td></tr>')
    return ('<div class="scroller"><table><thead><tr><th>Anbieter</th><th>Segment</th>'
            '<th>Beschr.</th><th>H1</th><th>H2</th><th>Schema</th><th>Social</th><th>WebP</th>'
            '<th>Antwort</th><th>Gewicht</th><th>Seiten</th><th>Erfüllt</th></tr></thead>'
            f'<tbody>{"".join(tr)}</tbody></table></div>')


CSS = """
:root{
 --lime:#9BBE00; --red:#D8063A; --red-text:#CA0636;
 --ink:#000; --gray:#5f5e58; --line:rgba(0,0,0,.15);
 --paper:#fff; --warm:#EFECE3; --panel:#fff; --chart:#fcfcfb;
 --grad:linear-gradient(115deg,#FFE9A0 0%,#FFD9AE 46%,#F2EFD4 78%,#E7EDCF 100%);
 --onwarm:#000; --warmsub:rgba(0,0,0,.64);
 --ok:#37702A; --okbg:#E9F2E2; --mid:#7E5600; --midbg:#F9EFD7; --no:#A80B2E; --nobg:#FBE3E9;
 --disp:'Anton',Impact,'Arial Black',sans-serif;
 --sub:'Bricolage Grotesque','Hanken Grotesk',system-ui,sans-serif;
 --body:'Hanken Grotesk',system-ui,-apple-system,sans-serif;
 --maxw:1220px; --ease:cubic-bezier(.22,.9,.24,1);
}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){
 --lime:#C9F73C; --red:#FF2E63; --red-text:#FF87A3;
 --ink:#F5F5F2; --gray:#A3A29D; --line:rgba(255,255,255,.17);
 --paper:#0A0A0B; --warm:#131315; --panel:#141416; --chart:#111113;
 --grad:linear-gradient(115deg,#241F14 0%,#2A1E18 46%,#1B1F16 78%,#12140F 100%);
 --onwarm:#F5F5F2; --warmsub:rgba(245,245,242,.68);
 --ok:#8FD07A; --okbg:#17250F; --mid:#E2B44F; --midbg:#2B2210; --no:#FF87A3; --nobg:#2F121C;
}}
:root[data-theme="dark"]{
 --lime:#C9F73C; --red:#FF2E63; --red-text:#FF87A3;
 --ink:#F5F5F2; --gray:#A3A29D; --line:rgba(255,255,255,.17);
 --paper:#0A0A0B; --warm:#131315; --panel:#141416; --chart:#111113;
 --grad:linear-gradient(115deg,#241F14 0%,#2A1E18 46%,#1B1F16 78%,#12140F 100%);
 --onwarm:#F5F5F2; --warmsub:rgba(245,245,242,.68);
 --ok:#8FD07A; --okbg:#17250F; --mid:#E2B44F; --midbg:#2B2210; --no:#FF87A3; --nobg:#2F121C;
}
*{margin:0;padding:0;box-sizing:border-box}
html{scroll-behavior:smooth;scroll-padding-top:70px}
body{font-family:var(--body);color:var(--ink);background:var(--paper);line-height:1.62;
 -webkit-font-smoothing:antialiased;overflow-x:clip}
h1,h2,h3,h4{font-weight:400;text-wrap:balance}
a{color:var(--red-text)}
:focus-visible{outline:3px solid var(--red);outline-offset:3px}
.wrap{max-width:var(--maxw);margin:0 auto;padding:0 clamp(18px,4vw,40px)}
.sec{padding:clamp(50px,6vw,84px) 0}
.sec.warmbg{background:var(--warm)}
.kick{display:inline-flex;align-items:center;gap:12px;font-family:var(--sub);font-weight:600;
 font-size:.78rem;letter-spacing:.2em;text-transform:uppercase;color:var(--gray);margin-bottom:15px}
.kick::before{content:'';width:32px;height:9px;background:var(--lime);flex:none}
.kick.r::before{background:var(--red)}
.hd2{font-family:var(--disp);text-transform:uppercase;line-height:1.01;
 font-size:clamp(1.85rem,4.3vw,3rem)}
.hd2 em{font-style:normal;color:var(--red-text)}
.lead{font-size:clamp(1rem,1.3vw,1.14rem);color:var(--gray);max-width:68ch}
.shead{margin-bottom:clamp(26px,3.4vw,42px);max-width:820px}
.shead .lead{margin-top:13px}
p+p{margin-top:13px}

/* Nav */
nav.toc{position:sticky;top:0;z-index:60;background:color-mix(in srgb,var(--paper) 92%,transparent);
 backdrop-filter:blur(14px);border-bottom:1px solid var(--line)}
nav.toc .wrap{display:flex;gap:22px;overflow-x:auto;height:56px;align-items:center;
 font-family:var(--sub);font-weight:600;font-size:.76rem;letter-spacing:.09em;text-transform:uppercase}
nav.toc a{color:var(--gray);white-space:nowrap;text-decoration:none;padding:5px 0;
 border-bottom:2px solid transparent}
nav.toc a:hover{color:var(--red-text);border-color:var(--red)}

/* Titel */
.hero{background:var(--grad);padding:clamp(56px,7vw,88px) 0 clamp(40px,5vw,60px)}
.eyeb{font-family:var(--sub);font-weight:600;font-size:.76rem;letter-spacing:.2em;
 text-transform:uppercase;color:var(--warmsub);margin-bottom:20px}
.hero h1{font-family:var(--disp);text-transform:uppercase;line-height:.95;
 font-size:clamp(2.3rem,6.6vw,4.7rem);color:var(--onwarm);max-width:18ch}
.hero h1 em{font-style:normal;color:var(--red)}
.hero .lead{color:var(--warmsub);margin-top:20px;font-size:clamp(1.02rem,1.45vw,1.22rem)}
.meta{display:flex;flex-wrap:wrap;margin-top:32px;padding-top:17px;
 border-top:1px solid color-mix(in srgb,var(--onwarm) 24%,transparent)}
.meta div{padding-right:26px;margin-right:26px;
 border-right:1px solid color-mix(in srgb,var(--onwarm) 24%,transparent)}
.meta div:last-child{border:0;margin:0;padding:0}
.meta b{font-family:var(--disp);font-size:1.6rem;display:block;line-height:1;color:var(--onwarm)}
.meta span{font-family:var(--sub);font-size:.7rem;letter-spacing:.14em;text-transform:uppercase;
 color:var(--warmsub)}

/* Kernbefunde */
.punch{background:var(--ink);color:#fff;padding:clamp(30px,4vw,50px)}
.punch .big{font-family:var(--disp);text-transform:uppercase;line-height:.99;
 font-size:clamp(1.8rem,4.6vw,3.1rem)}
.punch .big em{font-style:normal;color:var(--lime)}
.punch>p{color:rgba(255,255,255,.8);max-width:66ch;margin-top:18px}
.kb{display:grid;gap:24px;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));
 margin-top:32px;padding-top:26px;border-top:1px solid rgba(255,255,255,.22)}
.kb b{font-family:var(--disp);font-size:2.5rem;line-height:1;color:var(--lime);display:block}
.kb span{color:rgba(255,255,255,.78);font-size:.93rem;display:block;margin-top:7px}

/* Tabellen */
.scroller{overflow-x:auto;border:1.5px solid var(--line);background:var(--panel)}
table{border-collapse:collapse;width:100%;font-size:.9rem;min-width:680px}
th,td{text-align:left;padding:10px 13px;border-bottom:1px solid var(--line);vertical-align:top}
thead th{font-family:var(--sub);font-weight:600;font-size:.66rem;letter-spacing:.12em;
 text-transform:uppercase;color:var(--gray);background:var(--warm);
 border-bottom:1.5px solid var(--ink);white-space:nowrap;position:sticky;top:0}
tbody tr:last-child td{border-bottom:0}
td.n{font-variant-numeric:tabular-nums;white-space:nowrap;font-family:var(--sub)}
tr.us{background:color-mix(in srgb,var(--lime) 17%,transparent)}
tr.us td{font-weight:600}
tr.us td:first-child::before{content:'▸ ';color:var(--red-text)}
.leer{color:var(--gray);font-style:italic}
.tag{display:inline-block;font-family:var(--sub);font-weight:600;font-size:.65rem;
 letter-spacing:.07em;text-transform:uppercase;padding:3px 8px;border-radius:3px;white-space:nowrap}
.t-ok{background:var(--okbg);color:var(--ok)} .t-mid{background:var(--midbg);color:var(--mid)}
.t-no{background:var(--nobg);color:var(--no)}

/* Sichtbarkeit */
.vis{border-top:1.5px solid var(--ink)}
.vrow{display:grid;grid-template-columns:1fr;gap:6px 20px;padding:20px 0;
 border-bottom:1.5px solid var(--line)}
@media(min-width:880px){.vrow{grid-template-columns:230px 132px 1fr;align-items:start}}
.vq{font-family:var(--disp);text-transform:uppercase;font-size:1.1rem;line-height:1.12}
.vq small{display:block;font-family:var(--body);text-transform:none;font-size:.8rem;
 color:var(--gray);margin-top:4px}
.vwho{font-size:.92rem;color:var(--ink)}
.vwho b{color:var(--red-text)}
.vand{color:var(--gray);font-size:.86rem;display:block;margin-top:6px}

/* Preisgrafik */
.chart{background:var(--chart);border:1.5px solid var(--line);padding:26px 24px;
 display:flex;flex-direction:column;gap:2px}
.crow{display:grid;grid-template-columns:1fr;gap:4px 16px;padding:11px 0}
.crow+.crow{border-top:1px solid var(--line)}
@media(min-width:760px){.crow{grid-template-columns:190px 1fr 168px;align-items:center}}
.cname{font-family:var(--sub);font-weight:600;font-size:.93rem}
.cname small{display:block;font-family:var(--body);font-weight:400;color:var(--gray);
 font-size:.79rem;margin-top:2px}
.ctrack{display:flex;align-items:center;gap:11px;min-height:22px}
.cbar{height:14px;background:color-mix(in srgb,var(--ink) 26%,transparent);
 border-radius:0 4px 4px 0;flex:none}
.crow.ist-wir .cbar{background:var(--red)}
.cval{font-family:var(--sub);font-weight:600;font-size:.9rem;font-variant-numeric:tabular-nums;
 color:var(--ink);white-space:nowrap}
.crow.ist-wir .cval{color:var(--red-text)}
.crow.ist-wir .cname{color:var(--red-text)}
.cbind{font-size:.8rem;color:var(--gray);font-family:var(--sub)}

/* Matrix */
.matrix td{text-align:center;padding:8px 6px}
.matrix td.mname{text-align:left;font-family:var(--sub);font-weight:600;white-space:nowrap}
.matrix td.ja{color:var(--lime);font-size:1.1rem;
 text-shadow:0 0 0 var(--ink);-webkit-text-stroke:.4px var(--ink)}
.matrix td.nein{color:var(--line)}
.matrix thead th{writing-mode:vertical-rl;transform:rotate(180deg);padding:12px 5px;
 font-size:.62rem;letter-spacing:.08em;height:118px;position:static}
.matrix thead th:first-child,.matrix thead th:last-child{writing-mode:horizontal-tb;
 transform:none;height:auto}

/* Profile */
.profs{display:flex;flex-direction:column;gap:22px}
.prof{border:1.5px solid var(--line);background:var(--panel);display:grid;
 grid-template-columns:8px 1fr;overflow:hidden}
.prof-wir{border-color:var(--red);border-width:2px}
.pbar{background:linear-gradient(180deg,var(--c1) 0%,var(--c1) 55%,var(--c2) 55%,var(--c2) 100%)}
.pin{padding:24px clamp(18px,2.6vw,30px)}
.phead{display:flex;gap:18px;justify-content:space-between;align-items:flex-start;flex-wrap:wrap}
.pseg{font-family:var(--sub);font-weight:600;font-size:.68rem;letter-spacing:.13em;
 text-transform:uppercase;color:var(--gray)}
.prof h3{font-family:var(--disp);text-transform:uppercase;font-size:1.5rem;line-height:1.06;
 margin-top:5px}
.pdom{font-family:var(--sub);font-size:.83rem;color:var(--c1);font-weight:600;margin-top:3px;
 filter:contrast(1.4)}
.pscore{text-align:right;flex:none}
.pscore b{font-family:var(--disp);font-size:1.9rem;line-height:1;display:block;color:var(--ink)}
.pscore span{font-family:var(--sub);font-size:.62rem;letter-spacing:.11em;text-transform:uppercase;
 color:var(--gray)}
.plabel{font-family:var(--sub);font-weight:600;font-size:.65rem;letter-spacing:.14em;
 text-transform:uppercase;color:var(--gray);display:block;margin:20px 0 8px}
.pfarben{display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin-top:16px}
.pfarben .plabel{margin:0 6px 0 0}
.sw{font-family:var(--sub);font-size:.66rem;font-weight:600;padding:4px 9px;border-radius:3px;
 color:#fff;text-shadow:0 1px 2px rgba(0,0,0,.55);letter-spacing:.04em}
.pquelle{font-size:.74rem;color:var(--gray);font-style:italic}
.mess{display:grid;grid-template-columns:repeat(auto-fit,minmax(96px,1fr));gap:14px;
 margin-top:18px;padding:14px 0;border-top:1px solid var(--line);border-bottom:1px solid var(--line)}
.mess dt{font-family:var(--sub);font-size:.62rem;letter-spacing:.1em;text-transform:uppercase;
 color:var(--gray)}
.mess dd{font-family:var(--sub);font-weight:600;font-size:1rem;font-variant-numeric:tabular-nums;
 margin-top:2px}
.pcols{display:grid;gap:18px;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));margin-top:6px}
.pcols p{font-size:.93rem;color:var(--gray)}
.stile{display:flex;flex-wrap:wrap;gap:6px}
.st{font-family:var(--sub);font-size:.73rem;font-weight:600;padding:4px 10px;
 border:1.5px solid var(--c1);border-radius:999px;color:var(--ink)}
.ptab{min-width:520px;font-size:.86rem}
.ptab thead th{background:transparent;border-bottom:1px solid var(--line);position:static}
.q{font-family:var(--sub);font-size:.6rem;letter-spacing:.08em;text-transform:uppercase;
 padding:2px 7px;border-radius:3px;font-weight:600}
.q-w{background:var(--okbg);color:var(--ok)} .q-s{background:var(--midbg);color:var(--mid)}

/* Portale */
.port{display:grid;gap:16px;grid-template-columns:repeat(auto-fit,minmax(285px,1fr))}
.pcard{border:1.5px solid var(--line);border-left:5px solid var(--red);background:var(--panel);
 padding:20px 22px}
.pcard h4{font-family:var(--disp);text-transform:uppercase;font-size:1.05rem}
.pcard .pk{font-family:var(--sub);font-size:.66rem;letter-spacing:.12em;text-transform:uppercase;
 color:var(--gray);margin:5px 0 9px}
.pcard p{font-size:.9rem;color:var(--gray)}

/* Plan */
.ph{display:grid;grid-template-columns:1fr;gap:14px 26px;padding:26px 0;
 border-bottom:1.5px solid var(--line)}
.ph:first-of-type{border-top:1.5px solid var(--ink)}
@media(min-width:880px){.ph{grid-template-columns:186px 1fr}}
.pn{font-family:var(--disp);text-transform:uppercase;font-size:1.4rem;line-height:1;
 color:var(--red-text)}
.pw{font-family:var(--sub);font-weight:600;font-size:.74rem;letter-spacing:.12em;
 text-transform:uppercase;color:var(--gray);margin-top:7px}
.pe{display:inline-block;margin-top:9px;font-family:var(--sub);font-weight:600;font-size:.68rem;
 letter-spacing:.08em;text-transform:uppercase;background:var(--lime);color:#000;
 padding:4px 10px;border-radius:3px}
.phb h3{font-family:var(--disp);text-transform:uppercase;font-size:1.28rem;margin-bottom:9px}
.phb ul{list-style:none;display:flex;flex-direction:column;gap:7px;margin-top:11px}
.phb li{display:flex;gap:10px;font-size:.95rem;color:var(--gray)}
.phb li::before{content:'';width:7px;height:7px;background:var(--lime);flex:none;margin-top:8px}
.phb li b{color:var(--ink);font-weight:600}
.pout{margin-top:12px;font-size:.91rem;border-left:3px solid var(--red);padding-left:13px}

footer{border-top:3px solid var(--ink);padding:32px 0 60px;color:var(--gray);font-size:.88rem}
footer h4{font-family:var(--disp);text-transform:uppercase;font-size:1rem;color:var(--ink);
 margin-bottom:9px}
footer p{max-width:82ch}
@media (prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}
 html{scroll-behavior:auto}}
"""

erfuellt = kriterien(WIR)
schnitt = [kriterien(a) for a in ANBIETER if kriterien(a) is not None]
n_unsichtbar = sum(1 for s in SICHTBARKEIT if s["status"] in ("nein", "falsch"))

DOC = f"""<title>Marktanalyse Tanzschulen Hannover</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="Vollerhebung des Tanzschulmarkts Hannover: 16 Anbieter, Preise, Kursangebot, SEO-Platzierung und Zukunftsplan für die Tanzschulen Familie Bothe.">
<style>{FONTS}</style>
<style>{CSS}</style>

<nav class="toc"><div class="wrap">
  <a href="#befund">Kernbefunde</a><a href="#sichtbar">SEO-Platzierung</a>
  <a href="#preise">Preise</a><a href="#angebot">Kursangebot</a>
  <a href="#technik">Technik</a><a href="#profile">Anbieterprofile</a>
  <a href="#portale">Portale</a><a href="#plan">Zukunftsplan</a>
</div></nav>

<section class="hero"><div class="wrap">
  <div class="eyeb">Vollerhebung Tanzschulmarkt · Region Hannover · 17. August 2026</div>
  <h1>16 Anbieter. 7 Suchbegriffe.<br>Und <em>ein blinder Fleck</em>.</h1>
  <p class="lead">Wer in Hannover Tanzen lernen will, hat die Wahl zwischen klassischen Tanzschulen,
  Preisführern, Urban-Studios, Vereinen — und sechs Portalen, die selbst keinen Kurs anbieten.
  Diese Erhebung vermisst alle: Preise, Kursangebot, Technik und Auffindbarkeit.</p>
  <div class="meta">
    <div><b>16</b><span>Anbieter erhoben</span></div>
    <div><b>7</b><span>Suchbegriffe geprüft</span></div>
    <div><b>{n_unsichtbar}</b><span>davon ohne uns</span></div>
    <div><b>31</b><span>Preisangaben</span></div>
    <div><b>{erfuellt}/10</b><span>Basissignale bei Bothe</span></div>
  </div>
</div></section>

<section class="sec" id="befund"><div class="wrap">
  <div class="punch">
    <div class="big">Das Angebot ist Marktführer.<br>Die <em>Auffindbarkeit</em> ist Schlusslicht.</div>
    <p>Die Tanzschulen Familie Bothe haben das mit Abstand breiteste Programm der Region:
    drei Häuser, elf Säle, rund 220 Angebote pro Woche und 17 Tanzrichtungen — mehr als
    jeder andere Anbieter im Test. Bei den messbaren Auffindbarkeits-Signalen liegen sie
    mit {erfuellt} von 10 erfüllten Basiskriterien auf dem letzten Platz.</p>
    <div class="kb">
      <div><b>17</b><span>Tanzrichtungen im Programm — Höchstwert im gesamten Feld</span></div>
      <div><b>{erfuellt}/10</b><span>erfüllte Basissignale — niedrigster Wert im Feld</span></div>
      <div><b>391</b><span>Seiten in der Sitemap, aber keine einzige Seite pro Tanzstil</span></div>
      <div><b>61 €</b><span>Monatspreis — Platz 4 von 7, also Mittelfeld, nicht teuer</span></div>
    </div>
  </div>
</div></section>

<section class="sec warmbg" id="sichtbar"><div class="wrap">
  <div class="shead">
    <div class="kick r">SEO-Platzierung</div>
    <h2 class="hd2">Sieben Suchbegriffe, <em>mit denen Kunden suchen</em></h2>
    <p class="lead">Geprüft wurde, welche Anbieter zu diesen Suchanfragen überhaupt mit
    einer eigenen Seite erscheinen. Das ist eine Anwesenheitsprüfung, kein Positions-Tracking —
    aber wer gar nicht auftaucht, steht auf keinem Platz.</p>
  </div>
  {sicht()}
  <p class="lead" style="margin-top:24px">Bei <b>{n_unsichtbar} von 7</b> Suchbegriffen erscheint
  Familie Bothe nicht oder mit einer falsch betitelten Seite. Der einzige klare Treffer ist
  <b>/schuelertanzkurse/</b> — bezeichnenderweise die einzige Seite im ganzen Auftritt, die
  wie eine richtige Kursseite gebaut ist.</p>
</div></section>

<section class="sec" id="preise"><div class="wrap">
  <div class="shead">
    <div class="kick">Preislandschaft</div>
    <h2 class="hd2">Was ein Monat Tanzen <em>tatsächlich kostet</em></h2>
    <p class="lead">Vergleichbar gemacht: der Monatspreis für den jeweils größten Zugang, den
    ein Anbieter verkauft. Wochenpreise wurden mit 52 ÷ 12 auf Monate umgerechnet.
    Sieben der 16 Anbieter veröffentlichen überhaupt einen Preis.</p>
  </div>
  {preisgrafik()}
  <p class="lead" style="margin-top:22px"><b>Das Ergebnis widerlegt eine verbreitete Annahme:</b>
  Bothe ist nicht der teure Anbieter. Mit 61 € liegt die Schule auf Platz 4 von 7 — günstiger
  als Move &amp; Style Unlimited (71,46 €), Salsa del Alma (rund 73,50 €) und Meiners (90 €).
  Dazu kommt der eigentliche Vorteil: Move &amp; Style bindet 52 Wochen, Happy Hours verlangt
  bis zu 90 Tage Kündigungsfrist, Meiners rechnet über 12 Monate. Nur dass all das nirgends
  steht — auf der Website der Tanzschulen Familie Bothe ist kein einziger Preis zu finden.</p>
</div></section>

<section class="sec warmbg" id="angebot"><div class="wrap">
  <div class="shead">
    <div class="kick">Kursangebot</div>
    <h2 class="hd2">Wer <em>was</em> unterrichtet</h2>
    <p class="lead">Vierzehn Tanzrichtungen, sechzehn Anbieter. Die Matrix zeigt, wo Bothe
    tatsächlich allein steht — und wo der Wettbewerb dicht ist.</p>
  </div>
  {matrix()}
  <p class="lead" style="margin-top:20px">Bothe führt als einziger Anbieter alle vierzehn
  geprüften Richtungen. Das ist das stärkste Verkaufsargument im Markt — und es ist auf der
  Website nirgends als solches formuliert.</p>
</div></section>

<section class="sec" id="technik"><div class="wrap">
  <div class="shead">
    <div class="kick r">Technische Platzierung</div>
    <h2 class="hd2">Wie die Seiten <em>gebaut</em> sind</h2>
    <p class="lead">Zehn objektiv prüfbare Basissignale: Beschreibung vorhanden und in Länge,
    genau eine H1, H2-Ebene, strukturierte Daten, Open Graph, Antwortzeit unter einer Sekunde,
    Seitengewicht unter 150 kB, WebP-Bilder, mindestens 20 Seiten, veröffentlichter Preis.</p>
  </div>
  {technik()}
  <p class="lead" style="margin-top:20px">Bemerkenswert: <b>Happy Hours hat technisch eine der
  schwächsten Seiten im Feld</b> — keine Beschreibung, keine H1, kein Schema — und besetzt
  Discofox trotzdem mit drei eigenen Adressen. Struktur schlägt Technik.</p>
</div></section>

<section class="sec warmbg" id="profile"><div class="wrap">
  <div class="shead">
    <div class="kick">Anbieterprofile</div>
    <h2 class="hd2">Jeder Wettbewerber <em>in seinen eigenen Farben</em></h2>
    <p class="lead">Die Farbstreifen stammen aus dem Quelltext der jeweiligen Website —
    aus theme-color-Angaben, benannten Marken-Variablen und den Regeln für Kopf, Navigation
    und Schaltflächen. Bootstrap- und WordPress-Standardpaletten wurden herausgefiltert,
    damit hier wirklich Marke steht und nicht Framework.</p>
  </div>
  <div class="profs">
{"".join(profil(a) for a in sorted(ANBIETER, key=lambda x: (not x["wir"], -(kriterien(x) or 0))))}
  </div>
</div></section>

<section class="sec" id="portale"><div class="wrap">
  <div class="shead">
    <div class="kick r">Der unterschätzte Gegner</div>
    <h2 class="hd2">Sechs Portale, die <em>keinen Kurs anbieten</em></h2>
    <p class="lead">Sie unterrichten nichts, haben keinen Saal und keinen Trainer — und stehen
    trotzdem bei fast jedem Suchbegriff vorn. Weil sie exakt die Seiten gebaut haben, die den
    Suchanfragen entsprechen.</p>
  </div>
  <div class="port">
{"".join(f'<div class="pcard"><h4>{E(n)}</h4><div class="pk">{E(t)}</div><p>{E(b)}</p></div>' for n, t, b in PORTALE)}
  </div>
</div></section>

<section class="sec warmbg" id="plan"><div class="wrap">
  <div class="shead">
    <div class="kick">Zukunftsplan</div>
    <h2 class="hd2">Vier Phasen <em>bis zur Marktführerschaft</em></h2>
    <p class="lead">Die Reihenfolge ist bewusst gewählt: zuerst das, was in Tagen wirkt,
    dann das, was den Abstand dauerhaft aufbaut.</p>
  </div>

  <div class="ph"><div><div class="pn">Phase 1</div><div class="pw">Woche 1–2</div>
    <span class="pe">≈ 3 Tage</span></div>
    <div class="phb"><h3>Blutung stoppen</h3>
      <p style="color:var(--gray)">Nichts Neues bauen — nur reparieren, was aktiv schadet.</p>
      <ul>
        <li><b>Titel und Beschreibungen für alle Kursseiten.</b> Muster umdrehen: Suchbegriff zuerst, Ort dazu, Marke zuletzt.</li>
        <li><b>Den Titelfehler auf /bwkids/ korrigieren</b> — eine Kinderseite mit dem Titel „Tanzangebot Erwachsene Paartanz“.</li>
        <li><b>15 Test- und Altseiten aus dem Index nehmen</b>, darunter „XXX_Start2“ und „Dongsineu“.</li>
        <li><b>SEO-Plugin mit Pflichtfeldern</b>, damit keine Seite ohne Beschreibung live geht.</li>
      </ul>
      <div class="pout">Wirkung sichtbar nach zwei bis sechs Wochen.</div></div></div>

  <div class="ph"><div><div class="pn">Phase 2</div><div class="pw">Monat 1–2</div>
    <span class="pe">Kernstück</span></div>
    <div class="phb"><h3>Die fehlenden Seiten bauen</h3>
      <p style="color:var(--gray)">Hier entsteht der eigentliche Vorsprung. Fünf Seiten sind bereits gebaut.</p>
      <ul>
        <li><b>Priorität 1: Hochzeitstanz.</b> Höchster Kundenwert, aktuell komplett unbesetzt.</li>
        <li><b>Priorität 2: Discofox.</b> Happy Hours besetzt drei Adressen, obwohl Bothe mehr Kurse anbietet.</li>
        <li><b>Priorität 3: Kindertanz und Hip Hop</b> — dort steht die eigene Seite mit falschem Titel bzw. gar nicht.</li>
        <li><b>Eigene Preisseite.</b> Das stärkste ungenutzte Argument: 61 € sind Mittelfeld bei größtem Angebot und monatlicher Kündbarkeit.</li>
        <li><b>Drei Standortseiten</b> statt einer gemeinsamen — drei Häuser hat sonst niemand.</li>
      </ul>
      <div class="pout">Ziel: bei allen sieben geprüften Suchbegriffen mit einer eigenen Seite vertreten sein.</div></div></div>

  <div class="ph"><div><div class="pn">Phase 3</div><div class="pw">Monat 2–4</div>
    <span class="pe">Technik</span></div>
    <div class="phb"><h3>Auszeichnung und Tempo</h3>
      <ul>
        <li><b>Strukturierte Daten:</b> drei Standorte, 24 gepflegte Events, jede Kursseite, die Fragenliste. Nur vier Anbieter im Feld nutzen überhaupt Schema — Event-Auszeichnung nutzt keiner.</li>
        <li><b>Ladezeit:</b> die Kinder- und Teenseiten brauchen bis zu drei Sekunden bis zum ersten Byte.</li>
        <li><b>Bildformat:</b> nur Gräper liefert WebP aus. Ein einfacher, messbarer Vorsprung.</li>
        <li><b>Drei Google-Unternehmensprofile</b>, je Standort eines.</li>
      </ul>
      <div class="pout">Ziel: technischer Gleichstand mit Meiners und Feeling, plus Alleinstellung bei Event-Auszeichnung.</div></div></div>

  <div class="ph"><div><div class="pn">Phase 4</div><div class="pw">ab Monat 3, dauerhaft</div>
    <span class="pe">Der Wächter</span></div>
    <div class="phb"><h3>Nicht wieder zurückfallen</h3>
      <p style="color:var(--gray)">Der heutige Zustand ist über Jahre entstanden, weil niemand hingeschaut hat.</p>
      <ul>
        <li><b>Täglicher Crawl</b> aller Seiten als nachvollziehbarer Verlauf.</li>
        <li><b>Alarm bei Regelverstoß:</b> fehlende Beschreibung, mehrere H1, neue Fehlerseite, Ladezeit über einer Sekunde.</li>
        <li><b>Technische Fehler repariert der Wächter selbst</b> und legt die Korrektur zur Freigabe vor. Inhalte und Preise bleiben beim Menschen — automatisch erzeugte Texte sind seit 2024 ein Abstrafungsrisiko.</li>
        <li><b>Monatliche Wettbewerbsbeobachtung</b> über alle 16 Anbieter.</li>
      </ul>
      <div class="pout">Deutlich unter den Kosten von Profi-Werkzeugen wie SearchPilot, die vierstellig im Monat beginnen.</div></div></div>
</div></section>

<footer><div class="wrap">
  <h4>Methodik und Grenzen</h4>
  <p>Alle technischen Werte stammen aus einem eigenen Live-Abruf am 17. August 2026: Quelltext,
  HTTP-Kopfzeilen, robots.txt und XML-Sitemaps von 16 Anbietern. Antwortzeiten sind
  Einzelmessungen (Time to First Byte) und schwanken tageszeitabhängig. Markenfarben wurden aus
  theme-color-Angaben, benannten CSS-Marken-Variablen und Komponentenregeln gewonnen; bekannte
  Bootstrap- und WordPress-Standardpaletten sind ausgeschlossen. Für die Tanzschulen Familie
  Bothe wurde das dokumentierte CI aus der eigenen Stylesheet-Datei verwendet.</p>
  <p style="margin-top:11px"><b style="color:var(--ink)">Der Sichtbarkeitstest ist kein
  Positions-Tracking.</b> Geprüft wurde, welche Anbieter zu sieben Suchanfragen überhaupt mit
  einer Seite erscheinen — nicht, auf welchem Platz. Für echte Positionen, Suchvolumen und
  Klickzahlen ist Zugriff auf die Google Search Console des Kontos oder ein Sistrix-Abo nötig;
  beides lag nicht vor. Die Aussage „bei {n_unsichtbar} von 7 Suchbegriffen nicht sichtbar“ ist
  belastbar, eine Aussage wie „Platz 14“ wäre es nicht.</p>
  <p style="margin-top:11px">Preise sind als <b style="color:var(--ink)">Website</b> gekennzeichnet,
  wenn sie auf der Anbieterseite gelesen wurden, und als <b style="color:var(--ink)">Snippet</b>,
  wenn sie nur aus einem Suchergebnis-Auszug stammen und nicht auf der Seite verifiziert werden
  konnten. Vor einer Preisdiskussion mit dem Kunden sollten die Snippet-Werte einzeln geprüft
  werden. u-dance.de war während der gesamten Erhebung nicht erreichbar; die Angaben dort
  beruhen auf Suchergebnissen.</p>
  <p style="margin-top:11px">Gründungsjahre stammen aus Selbstauskünften der Anbieter auf ihren
  Websites und sind teilweise gerundet.</p>
</div></footer>
"""

if __name__ == "__main__":
    p = SP / "marktanalyse-hannover.html"
    p.write_text(DOC, encoding="utf-8")
    print(f"{p} — {len(DOC)/1024:.0f} kB")
