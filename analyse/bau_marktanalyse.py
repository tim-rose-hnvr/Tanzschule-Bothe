#!/usr/bin/env python3
"""Marktanalyse Tanzschulen Familie Bothe — die zusammengeführte Fassung.

Anders als die bisherigen Dokumente ist diese nicht auf die Reparatur der alten
Website ausgerichtet. Die Website entsteht neu; der Befund über sie ist deshalb
nur noch Beleg dafür, dass der Relaunch richtig ist. Das Ergebnis dieser Analyse
sind die Anforderungen an die neue Seite.
"""
import html, pathlib, sys
from collections import Counter
sys.path.insert(0, "/tmp/claude-0/-home-user-Tanzschule-Bothe/76620a5d-636d-5dae-843e-8166f0dd9d56/scratchpad")
from markt_daten import ANBIETER, SICHTBARKEIT, PORTALE

SP = pathlib.Path("/tmp/claude-0/-home-user-Tanzschule-Bothe/76620a5d-636d-5dae-843e-8166f0dd9d56/scratchpad")
FONTS = (SP / "fonts-inline.css").read_text(encoding="utf-8")
E = lambda s: html.escape(str(s), quote=True)
WIR = next(a for a in ANBIETER if a["wir"])

VERBREITUNG = Counter()
for a in ANBIETER:
    for s in a["stile"]:
        VERBREITUNG[s] += 1
STILZAHL = sorted(len(a["stile"]) for a in ANBIETER)
MEDIAN = STILZAHL[len(STILZAHL) // 2]

MATRIX_STILE = ["Standard", "Latein", "Discofox", "Salsa", "Bachata", "Hip Hop",
                "Breakdance", "Contemporary", "Ballett", "Kindertanz", "Linedance",
                "Hochzeit", "Privatstunde", "Welttanzprogramm"]


def preisgrafik():
    rows = sorted([a for a in ANBIETER if a["voll"]], key=lambda x: x["voll"])
    mx = max(r["voll"] for r in rows)
    out = ['<div class="chart" role="img" aria-label="Monatspreis für Vollzugang je Anbieter, '
           'von 15,50 Euro bis 90,00 Euro. Familie Bothe liegt mit 61,00 Euro auf Platz vier von sieben.">']
    for r in rows:
        out.append(
            f'<div class="crow{" ist-wir" if r["wir"] else ""}">'
            f'<div class="cname">{E(r["kurz"])}<small>{E(r["voll_label"])}</small></div>'
            f'<div class="ctrack"><div class="cbar" style="width:{r["voll"] / mx * 100:.1f}%"></div>'
            f'<span class="cval">{r["voll"]:.2f} €</span></div>'
            f'<div class="cbind">{E(r["bindung"])}</div></div>')
    return "\n".join(out) + "</div>"


def matrix():
    kopf = "".join(f"<th>{E(s)}</th>" for s in MATRIX_STILE)
    zeilen = []
    for a in sorted(ANBIETER, key=lambda x: (not x["wir"], -len(x["stile"]))):
        z = "".join(f'<td class="{"ja" if s in a["stile"] else "nein"}">'
                    f'{"●" if s in a["stile"] else "·"}</td>' for s in MATRIX_STILE)
        zeilen.append(f'<tr class="{"us" if a["wir"] else ""}">'
                      f'<td class="mname">{E(a["kurz"])}</td>{z}'
                      f'<td class="n">{len(a["stile"])}</td></tr>')
    return (f'<div class="scroller"><table class="matrix"><thead><tr><th>Anbieter</th>{kopf}'
            f'<th>Σ</th></tr></thead><tbody>{"".join(zeilen)}</tbody></table></div>')


def profil(a):
    c1 = a["farben"][0]
    c2 = a["farben"][1] if len(a["farben"]) > 1 else c1
    swat = "".join(f'<span class="sw" style="background:{c}">{c}</span>' for c in a["farben"])
    preise = "".join(
        f'<tr><td>{E(n)}</td><td class="n">{p:.2f} €</td><td>{E(d)}</td>'
        f'<td><span class="q q-{"w" if q == "Website" else "s"}">{E(q)}</span></td></tr>'
        for n, p, d, q in a["preise"]) or \
        '<tr><td colspan="4" class="leer">Kein Preis auf der Website veröffentlicht.</td></tr>'
    stile = "".join(f'<span class="st">{E(s)}</span>' for s in a["stile"])
    mess = (f'<dl class="mess">'
            f'<div><dt>Antwortzeit</dt><dd>{a["ttfb"]:.2f} s</dd></div>'
            f'<div><dt>Seiten</dt><dd>{a["seiten"]}</dd></div>'
            f'<div><dt>Tanzrichtungen</dt><dd>{len(a["stile"])}</dd></div>'
            f'<div><dt>Gegründet</dt><dd>{a["gegruendet"]}</dd></div></dl>'
            if a["ttfb"] is not None else
            '<p class="leer">Website war während der Erhebung nicht erreichbar.</p>')
    return f"""
<article class="prof{' prof-wir' if a['wir'] else ''}" style="--c1:{c1};--c2:{c2}">
  <div class="pbar"></div>
  <div class="pin">
    <div class="phead"><div>
      <div class="pseg">{E(a['seg'])} · {E(a['ort'])}</div>
      <h3>{E(a['name'])}</h3><div class="pdom">{E(a['dom'])}</div>
    </div><div class="pfarben">{swat}</div></div>
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


def sicht():
    tag = {"ja": ("t-ok", "besetzt"), "teil": ("t-mid", "nur Sammelseite"),
           "falsch": ("t-mid", "falscher Titel"), "nein": ("t-no", "nicht besetzt")}
    out = ['<div class="vis">']
    for s in SICHTBARKEIT:
        cls, lbl = tag[s["status"]]
        out.append(
            f'<div class="vrow"><div class="vq">{E(s["q"])}<small>{E(s["note"])}</small></div>'
            f'<div><span class="tag {cls}">{lbl}</span></div>'
            f'<div class="vwho"><b>Bothe:</b> {E(s["wir"])}<br>'
            f'<span class="vand">Dort vertreten: {" · ".join(E(x) for x in s["andere"])}</span>'
            f'</div></div>')
    return "\n".join(out) + "</div>"


SWOT = [
 ("staerke", "Stärken", "Was im Markt sonst niemand hat", [
   ("17 Tanzrichtungen", f"Mehr als doppelt so viele wie der Median im Feld ({MEDIAN}). Als einziger Anbieter deckt Bothe alle 14 verbreiteten Richtungen ab."),
   ("Drei Häuser, elf Säle", "Kein anderer Anbieter in Hannover hat mehr als einen Standort. Das ist ein struktureller Vorteil, kein Marketingversprechen."),
   ("Seit 1954, dritte Generation", "Älteste Tanzschule im Feld — vier Jahre vor dem TTC Gelb-Weiss, 26 Jahre vor Meiners."),
   ("Eigene Ausbildung", "Tanzlehrerinnen und Tanzlehrer werden im Haus ausgebildet. Kein Wettbewerber im Feld wirbt damit."),
   ("Alleinstellung im Programm", "Welttanzprogramm und Medaillenkurse führen nur zwei von 16 Anbietern, Swing nur Bothe."),
   ("24 gepflegte Termine", "Ein laufendes Veranstaltungsprogramm in dieser Dichte hat kein anderer Anbieter."),
 ]),
 ("schwaeche", "Schwächen", "Wo der Markt uns gerade überholt", [
   ("Kein Preis nach außen", "Sieben Anbieter veröffentlichen Preise, Bothe nicht. Wer schweigt, überlässt die Preiswahrnehmung dem, der am lautesten „günstig“ ruft."),
   ("Keine Seite pro Tanzstil", "Das Angebot ist das größte im Markt, aber es gibt keine Adresse, die „Discofox“ oder „Hochzeitstanz“ heißt. Deshalb ist es in der Suche unsichtbar."),
   ("Bei 5 von 7 Suchbegriffen nicht besetzt", "Darunter Hochzeitstanz, Discofox und Hip Hop — alle drei mit hohem Kundenwert."),
   ("Markenname doppelt belegt", "Zwei Bothes in Hannover. Jede unspezifische Markensuche teilt sich auf, und aktuell gewinnt die besser strukturierte Seite."),
   ("Technisch Schlusslicht", "1 von 10 Basissignalen erfüllt — der niedrigste Wert im gesamten Feld, bei größtem Angebot."),
 ]),
 ("chance", "Chancen", "Freies Feld, das jetzt besetzt werden kann", [
   ("Event-Markup nutzt niemand", "Von 16 Anbietern zeichnet keiner seine Termine strukturiert aus. Die 24 gepflegten Termine könnten mit Datum und Ort direkt im Suchergebnis stehen — ein Vorsprung, kein Aufholen."),
   ("Hochzeitstanz ist unbesetzt", "Höchster Kundenwert im ganzen Geschäft: Paare planen Monate im Voraus, zahlen gut und bleiben oft. Zehn Anbieter im Markt haben etwas dazu, Bothe erscheint nicht."),
   ("Der Preis ist ein Argument, kein Problem", "61 € sind Platz 4 von 7 — günstiger als Move & Style Unlimited, Salsa del Alma und Meiners, dazu ohne 52-Wochen-Bindung. Das muss nur jemand sagen."),
   ("Drei Standorte, drei lokale Profile", "Drei gepflegte Google-Unternehmensprofile mit je eigener Standortseite kann im Markt sonst niemand aufbieten."),
   ("Portale als Kanal statt Gegner", "citysports.de, heiraten.de und tanzkurs.com stehen überall vorn. Ein gepflegter Eintrag dort ist billiger als jeder Versuch, sie zu verdrängen."),
 ]),
 ("risiko", "Risiken", "Was sich gerade gegen uns aufbaut", [
   ("Bothe Loft ab 2027", "Susanne Bothe baut 1.600 m² am Bischofsholer Damm und dokumentiert den Bau seit September 2025 laufend auf eigener Domain. Das erzeugt fortlaufend frische Signale — und verschärft die Namensverwechslung genau dann, wenn eröffnet wird."),
   ("Preisdruck von unten", "Happy Hours ab 29,90 €, der TTC Gelb-Weiss ab 15,50 € im Monat. Beide werben offensiv mit dem Preis."),
   ("Move & Style beansprucht den Titel", "„Die beste Tanzschule in Hannover“ steht wörtlich in deren Seitentitel — und greift mit 14 Urban-Richtungen genau Studio B an."),
   ("Spezialisten schneiden Segmente heraus", "Salsa del Alma mit Weltmeister-Trainer im Hip Hop, dafunk.dance als reine Streetdance-Schule, Physicalpark mit Kindertanz für 9,90 € pro Woche."),
   ("Sichtbarkeit beim Relaunch", "Die 396 bestehenden Adressen tragen die heutige Sichtbarkeit. Ohne vollständigen Weiterleitungsplan geht sie beim Umzug verloren — das ist das größte technische Risiko des Projekts."),
 ]),
]

ANFORDERUNGEN = [
 ("Eine Seite pro Tanzstil", "muss",
  "Discofox, Hochzeitstanz, Salsa, Standard & Latein, West Coast Swing, Hip Hop, "
  "Kindertanz, Tanzen ab 60 — je mit Terminen, Preis, Trainer, Standort und Fragen. "
  "Das ist der strukturelle Grund, warum kleinere Anbieter heute vor Bothe stehen.",
  "Sechs dieser Seiten sind bereits gebaut und liegen im Repository."),
 ("Preise sichtbar, mit Argument", "muss",
  "Nicht nur die 61 € nennen, sondern einordnen: alle Kurse des Levels, drei Häuser, "
  "220 Angebote, monatlich kündbar. Gegen „Hannovers günstigste Preise“ hilft kein "
  "niedrigerer Preis, sondern ein besserer Vergleich.",
  "Die Preisdaten aller Wettbewerber liegen in dieser Analyse."),
 ("Weiterleitungsplan für 396 Adressen", "muss",
  "Jede heute indexierte Adresse braucht ein Ziel auf der neuen Seite. Ohne das "
  "beginnt die neue Website bei null — unabhängig davon, wie gut sie gebaut ist.",
  "Das größte Risiko des Relaunches. Regeln für Dubletten und Altseiten liegen vor."),
 ("Strukturierte Daten ab Tag eins", "muss",
  "DanceSchool mit drei Standorten, Event für alle Termine, Course je Kursseite, "
  "FAQPage. Beim Neubau kostet das fast nichts — nachträglich ist es ein eigenes Projekt.",
  "Generator vorhanden, erzeugt 31 fertige Blöcke aus dem Veranstaltungskalender."),
 ("Drei echte Standortseiten", "muss",
  "Je eigene Seite mit Anfahrt, Parkplätzen, Sälen und den dort laufenden Kursen, "
  "dazu je ein Google-Unternehmensprofil mit identischer Schreibweise.",
  "Drei Standorte hat im Markt sonst niemand — heute liegen sie auf einer Sammelseite."),
 ("Titel nach dem Muster Suchbegriff + Ort + Marke", "muss",
  "Nicht „Tanzschule Familie Bothe – Paartanz“, sondern „Paartanz für Erwachsene in "
  "Hannover“. Der Markenname gehört ans Ende.",
  "Vorgaben für 32 Kernseiten sind formuliert."),
 ("Marke gegen die Verwechslung schärfen", "soll",
  "„Tanzschulen Familie Bothe“ konsequent ausschreiben, Standorte immer mitnennen, "
  "die Geschichte seit 1954 sichtbar führen. Spätestens zur Eröffnung des Bothe Loft "
  "2027 wird das entscheidend.",
  "Zwei gleichnamige Tanzschulen in einer Stadt sind ein Dauerthema, kein Einmalprojekt."),
 ("Tempo als Anforderung, nicht als Hoffnung", "soll",
  "Die alte Seite liefert 327 kB für 424 sichtbare Wörter. Beim Neubau gehört ein "
  "Zielwert ins Lastenheft — sonst wiederholt sich das.",
  "Der schnellste Anbieter im Feld liefert in 0,31 s aus."),
 ("Einträge in den Portalen pflegen", "kann",
  "citysports.de, heiraten.de, tanzkurs.com und vuvivi.de stehen bei fast jedem "
  "Suchbegriff vorn. Ein gepflegter Eintrag ist billiger als der Versuch, sie zu verdrängen.",
  "Sechs Portale sind in dieser Analyse benannt."),
]


def swot():
    out = []
    for cls, titel, unter, punkte in SWOT:
        li = "".join(f'<li><b>{E(t)}</b><span>{E(x)}</span></li>' for t, x in punkte)
        out.append(f'<div class="sw-box {cls}"><div class="sw-h"><h3>{E(titel)}</h3>'
                   f'<p>{E(unter)}</p></div><ul>{li}</ul></div>')
    return f'<div class="swot">{"".join(out)}</div>'


def anforderungen():
    rang = {"muss": ("a-muss", "Pflicht"), "soll": ("a-soll", "Wichtig"),
            "kann": ("a-kann", "Sinnvoll")}
    out = []
    for i, (titel, stufe, text, fussnote) in enumerate(ANFORDERUNGEN, 1):
        cls, lbl = rang[stufe]
        out.append(
            f'<div class="anf"><div class="anr">{i:02d}</div><div class="anb">'
            f'<div class="anh"><h3>{E(titel)}</h3><span class="tag {cls}">{lbl}</span></div>'
            f'<p>{E(text)}</p><p class="anf-fuss">{E(fussnote)}</p></div></div>')
    return "".join(out)


CSS = """
:root{
 --lime:#9BBE00;--red:#D8063A;--red-text:#CA0636;--ink:#000;--gray:#5f5e58;
 --line:rgba(0,0,0,.15);--paper:#fff;--warm:#EFECE3;--panel:#fff;--chart:#fcfcfb;
 --grad:linear-gradient(115deg,#FFE9A0 0%,#FFD9AE 46%,#F2EFD4 78%,#E7EDCF 100%);
 --onwarm:#000;--warmsub:rgba(0,0,0,.64);
 --ok:#37702A;--okbg:#E9F2E2;--mid:#7E5600;--midbg:#F9EFD7;--no:#A80B2E;--nobg:#FBE3E9;
 --disp:'Anton',Impact,'Arial Black',sans-serif;
 --sub:'Bricolage Grotesque','Hanken Grotesk',system-ui,sans-serif;
 --body:'Hanken Grotesk',system-ui,-apple-system,sans-serif;
 --maxw:1220px;}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){
 --lime:#C9F73C;--red:#FF2E63;--red-text:#FF87A3;--ink:#F5F5F2;--gray:#A3A29D;
 --line:rgba(255,255,255,.17);--paper:#0A0A0B;--warm:#131315;--panel:#141416;--chart:#111113;
 --grad:linear-gradient(115deg,#241F14 0%,#2A1E18 46%,#1B1F16 78%,#12140F 100%);
 --onwarm:#F5F5F2;--warmsub:rgba(245,245,242,.68);
 --ok:#8FD07A;--okbg:#17250F;--mid:#E2B44F;--midbg:#2B2210;--no:#FF87A3;--nobg:#2F121C;}}
:root[data-theme="dark"]{
 --lime:#C9F73C;--red:#FF2E63;--red-text:#FF87A3;--ink:#F5F5F2;--gray:#A3A29D;
 --line:rgba(255,255,255,.17);--paper:#0A0A0B;--warm:#131315;--panel:#141416;--chart:#111113;
 --grad:linear-gradient(115deg,#241F14 0%,#2A1E18 46%,#1B1F16 78%,#12140F 100%);
 --onwarm:#F5F5F2;--warmsub:rgba(245,245,242,.68);
 --ok:#8FD07A;--okbg:#17250F;--mid:#E2B44F;--midbg:#2B2210;--no:#FF87A3;--nobg:#2F121C;}
*{margin:0;padding:0;box-sizing:border-box}
html{scroll-behavior:smooth;scroll-padding-top:66px}
body{font-family:var(--body);color:var(--ink);background:var(--paper);line-height:1.62;
 -webkit-font-smoothing:antialiased;overflow-x:clip}
h1,h2,h3{font-weight:400;text-wrap:balance}
a{color:var(--red-text)}
:focus-visible{outline:3px solid var(--red);outline-offset:3px}
.wrap{max-width:var(--maxw);margin:0 auto;padding:0 clamp(18px,4vw,40px)}
.sec{padding:clamp(50px,6vw,86px) 0}
.sec.warmbg{background:var(--warm)}
.kick{display:inline-flex;align-items:center;gap:12px;font-family:var(--sub);font-weight:600;
 font-size:.78rem;letter-spacing:.2em;text-transform:uppercase;color:var(--gray);margin-bottom:15px}
.kick::before{content:'';width:32px;height:9px;background:var(--lime);flex:none}
.kick.r::before{background:var(--red)}
.hd2{font-family:var(--disp);text-transform:uppercase;line-height:1.01;
 font-size:clamp(1.85rem,4.3vw,3rem)}
.hd2 em{font-style:normal;color:var(--red-text)}
.lead{font-size:clamp(1rem,1.3vw,1.14rem);color:var(--gray);max-width:70ch}
.shead{margin-bottom:clamp(26px,3.4vw,42px);max-width:840px}
.shead .lead{margin-top:13px}
nav.toc{position:sticky;top:0;z-index:60;background:color-mix(in srgb,var(--paper) 92%,transparent);
 backdrop-filter:blur(14px);border-bottom:1px solid var(--line)}
nav.toc .wrap{display:flex;gap:22px;overflow-x:auto;height:54px;align-items:center;
 font-family:var(--sub);font-weight:600;font-size:.75rem;letter-spacing:.09em;text-transform:uppercase}
nav.toc a{color:var(--gray);white-space:nowrap;text-decoration:none;padding:5px 0;
 border-bottom:2px solid transparent}
nav.toc a:hover{color:var(--red-text);border-color:var(--red)}
.hero{background:var(--grad);padding:clamp(56px,7vw,90px) 0 clamp(40px,5vw,60px)}
.eyeb{font-family:var(--sub);font-weight:600;font-size:.76rem;letter-spacing:.2em;
 text-transform:uppercase;color:var(--warmsub);margin-bottom:20px}
.hero h1{font-family:var(--disp);text-transform:uppercase;line-height:.95;
 font-size:clamp(2.3rem,6.6vw,4.7rem);color:var(--onwarm);max-width:17ch}
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
.punch{background:var(--ink);color:#fff;padding:clamp(30px,4vw,52px)}
.punch .big{font-family:var(--disp);text-transform:uppercase;line-height:.99;
 font-size:clamp(1.8rem,4.6vw,3.1rem)}
.punch .big em{font-style:normal;color:var(--lime)}
.punch>p{color:rgba(255,255,255,.8);max-width:68ch;margin-top:18px}
.kb{display:grid;gap:24px;grid-template-columns:repeat(auto-fit,minmax(175px,1fr));
 margin-top:32px;padding-top:26px;border-top:1px solid rgba(255,255,255,.22)}
.kb b{font-family:var(--disp);font-size:2.4rem;line-height:1;color:var(--lime);display:block}
.kb span{color:rgba(255,255,255,.78);font-size:.92rem;display:block;margin-top:7px}
.scroller{overflow-x:auto;border:1.5px solid var(--line);background:var(--panel)}
table{border-collapse:collapse;width:100%;font-size:.9rem;min-width:680px}
th,td{text-align:left;padding:10px 13px;border-bottom:1px solid var(--line);vertical-align:top}
thead th{font-family:var(--sub);font-weight:600;font-size:.66rem;letter-spacing:.12em;
 text-transform:uppercase;color:var(--gray);background:var(--warm);
 border-bottom:1.5px solid var(--ink);white-space:nowrap}
tbody tr:last-child td{border-bottom:0}
td.n{font-variant-numeric:tabular-nums;white-space:nowrap;font-family:var(--sub)}
tr.us{background:color-mix(in srgb,var(--lime) 17%,transparent)}
tr.us td{font-weight:600}
tr.us td:first-child::before{content:'▸ ';color:var(--red-text)}
.leer{color:var(--gray);font-style:italic}
.tag{display:inline-block;font-family:var(--sub);font-weight:600;font-size:.65rem;
 letter-spacing:.07em;text-transform:uppercase;padding:3px 8px;border-radius:3px;white-space:nowrap}
.t-ok{background:var(--okbg);color:var(--ok)}.t-mid{background:var(--midbg);color:var(--mid)}
.t-no{background:var(--nobg);color:var(--no)}
.matrix td{text-align:center;padding:8px 6px}
.matrix td.mname{text-align:left;font-family:var(--sub);font-weight:600;white-space:nowrap}
.matrix td.ja{color:var(--lime);font-size:1.1rem;-webkit-text-stroke:.4px var(--ink)}
.matrix td.nein{color:var(--line)}
.matrix thead th{writing-mode:vertical-rl;transform:rotate(180deg);padding:12px 5px;
 font-size:.62rem;letter-spacing:.08em;height:120px}
.matrix thead th:first-child,.matrix thead th:last-child{writing-mode:horizontal-tb;
 transform:none;height:auto}
.vis{border-top:1.5px solid var(--ink)}
.vrow{display:grid;grid-template-columns:1fr;gap:6px 20px;padding:20px 0;
 border-bottom:1.5px solid var(--line)}
@media(min-width:880px){.vrow{grid-template-columns:236px 132px 1fr;align-items:start}}
.vq{font-family:var(--disp);text-transform:uppercase;font-size:1.1rem;line-height:1.12}
.vq small{display:block;font-family:var(--body);text-transform:none;font-size:.8rem;
 color:var(--gray);margin-top:4px}
.vwho{font-size:.92rem}.vwho b{color:var(--red-text)}
.vand{color:var(--gray);font-size:.86rem;display:block;margin-top:6px}
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
 white-space:nowrap}
.crow.ist-wir .cval,.crow.ist-wir .cname{color:var(--red-text)}
.cbind{font-size:.8rem;color:var(--gray);font-family:var(--sub)}
.swot{display:grid;gap:20px;grid-template-columns:repeat(auto-fit,minmax(320px,1fr))}
.sw-box{border:1.5px solid var(--line);background:var(--panel);padding:24px 26px}
.sw-box.staerke{border-left:6px solid var(--lime)}
.sw-box.schwaeche{border-left:6px solid var(--red)}
.sw-box.chance{border-left:6px solid var(--ok)}
.sw-box.risiko{border-left:6px solid var(--mid)}
.sw-h h3{font-family:var(--disp);text-transform:uppercase;font-size:1.5rem;line-height:1}
.sw-h p{font-family:var(--sub);font-size:.72rem;letter-spacing:.12em;text-transform:uppercase;
 color:var(--gray);margin-top:7px}
.sw-box ul{list-style:none;margin-top:20px;display:flex;flex-direction:column;gap:15px}
.sw-box li{display:flex;flex-direction:column;gap:4px;padding-left:15px;position:relative}
.sw-box li::before{content:'';position:absolute;left:0;top:9px;width:6px;height:6px;
 background:var(--ink)}
.sw-box li b{font-weight:600;font-size:.97rem}
.sw-box li span{color:var(--gray);font-size:.91rem}
.anf{display:grid;grid-template-columns:44px 1fr;gap:20px;padding:24px 0;
 border-bottom:1.5px solid var(--line)}
.anf:first-of-type{border-top:1.5px solid var(--ink)}
.anr{font-family:var(--disp);font-size:1.5rem;line-height:1;color:var(--red-text);
 font-variant-numeric:tabular-nums}
.anh{display:flex;gap:12px;align-items:center;flex-wrap:wrap;margin-bottom:8px}
.anb h3{font-family:var(--disp);text-transform:uppercase;font-size:1.24rem;line-height:1.08}
.anb p{color:var(--gray);font-size:.97rem}
.anf-fuss{margin-top:9px;font-size:.88rem;border-left:3px solid var(--lime);padding-left:12px}
.a-muss{background:var(--nobg);color:var(--no)}
.a-soll{background:var(--midbg);color:var(--mid)}
.a-kann{background:var(--okbg);color:var(--ok)}
.profs{display:flex;flex-direction:column;gap:20px}
.prof{border:1.5px solid var(--line);background:var(--panel);display:grid;
 grid-template-columns:8px 1fr;overflow:hidden}
.prof-wir{border-color:var(--red);border-width:2px}
.pbar{background:linear-gradient(180deg,var(--c1) 0%,var(--c1) 55%,var(--c2) 55%,var(--c2) 100%)}
.pin{padding:22px clamp(18px,2.6vw,28px)}
.phead{display:flex;gap:18px;justify-content:space-between;align-items:flex-start;flex-wrap:wrap}
.pseg{font-family:var(--sub);font-weight:600;font-size:.68rem;letter-spacing:.13em;
 text-transform:uppercase;color:var(--gray)}
.prof h3{font-family:var(--disp);text-transform:uppercase;font-size:1.45rem;line-height:1.06;
 margin-top:5px}
.pdom{font-family:var(--sub);font-size:.83rem;color:var(--c1);font-weight:600;margin-top:3px;
 filter:contrast(1.4)}
.pfarben{display:flex;gap:6px;flex-wrap:wrap}
.sw{font-family:var(--sub);font-size:.64rem;font-weight:600;padding:4px 9px;border-radius:3px;
 color:#fff;text-shadow:0 1px 2px rgba(0,0,0,.55);letter-spacing:.04em}
.plabel{font-family:var(--sub);font-weight:600;font-size:.65rem;letter-spacing:.14em;
 text-transform:uppercase;color:var(--gray);display:block;margin:18px 0 8px}
.mess{display:grid;grid-template-columns:repeat(auto-fit,minmax(96px,1fr));gap:14px;
 margin-top:16px;padding:13px 0;border-top:1px solid var(--line);border-bottom:1px solid var(--line)}
.mess dt{font-family:var(--sub);font-size:.62rem;letter-spacing:.1em;text-transform:uppercase;
 color:var(--gray)}
.mess dd{font-family:var(--sub);font-weight:600;font-size:1rem;font-variant-numeric:tabular-nums;
 margin-top:2px}
.pcols{display:grid;gap:18px;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));margin-top:6px}
.pcols p{font-size:.93rem;color:var(--gray)}
.stile{display:flex;flex-wrap:wrap;gap:6px}
.st{font-family:var(--sub);font-size:.73rem;font-weight:600;padding:4px 10px;
 border:1.5px solid var(--c1);border-radius:999px}
.ptab{min-width:520px;font-size:.86rem}
.ptab thead th{background:transparent;border-bottom:1px solid var(--line)}
.q{font-family:var(--sub);font-size:.6rem;letter-spacing:.08em;text-transform:uppercase;
 padding:2px 7px;border-radius:3px;font-weight:600}
.q-w{background:var(--okbg);color:var(--ok)}.q-s{background:var(--midbg);color:var(--mid)}
.port{display:grid;gap:16px;grid-template-columns:repeat(auto-fit,minmax(285px,1fr))}
.pcard{border:1.5px solid var(--line);border-left:5px solid var(--red);background:var(--panel);
 padding:20px 22px}
.pcard h4{font-family:var(--disp);text-transform:uppercase;font-size:1.05rem}
.pcard .pk{font-family:var(--sub);font-size:.66rem;letter-spacing:.12em;text-transform:uppercase;
 color:var(--gray);margin:5px 0 9px}
.pcard p{font-size:.9rem;color:var(--gray)}
footer{border-top:3px solid var(--ink);padding:32px 0 60px;color:var(--gray);font-size:.88rem}
footer h4{font-family:var(--disp);text-transform:uppercase;font-size:1rem;color:var(--ink);
 margin-bottom:9px}
footer p{max-width:84ch;margin-bottom:11px}
@media (prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}
 html{scroll-behavior:auto}}
"""

n_unbesetzt = sum(1 for s in SICHTBARKEIT if s["status"] in ("nein", "falsch"))

DOC = f"""<title>Marktanalyse Tanzschule Bothe</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="Marktanalyse für die Tanzschulen Familie Bothe: 16 Anbieter im Raum Hannover, Preise, Kursangebot, Nachfrage und die Anforderungen an die neue Website.">
<style>{FONTS}</style>
<style>{CSS}</style>

<nav class="toc"><div class="wrap">
  <a href="#lage">Ausgangslage</a><a href="#markt">Der Markt</a>
  <a href="#angebot">Angebot</a><a href="#preise">Preise</a>
  <a href="#nachfrage">Nachfrage</a><a href="#profile">Wettbewerber</a>
  <a href="#swot">Position</a><a href="#relaunch">Anforderungen</a>
</div></nav>

<section class="hero"><div class="wrap">
  <div class="eyeb">Marktanalyse · Tanzschulen Familie Bothe · Raum Hannover · August 2026</div>
  <h1>Das größte Angebot <em>der Stadt</em>. Und kaum jemand weiß es.</h1>
  <p class="lead">Eine Vollerhebung des Tanzschulmarkts Hannover: 16 Anbieter, ihre Preise,
  ihr Kursprogramm, ihre Websites. Und die Frage, was die neue Bothe-Website leisten muss,
  damit aus dem größten Angebot auch die stärkste Position wird.</p>
  <div class="meta">
    <div><b>16</b><span>Anbieter erhoben</span></div>
    <div><b>17</b><span>Tanzrichtungen bei Bothe</span></div>
    <div><b>{MEDIAN}</b><span>Median im Markt</span></div>
    <div><b>31</b><span>Preisangaben</span></div>
    <div><b>7</b><span>Suchbegriffe geprüft</span></div>
  </div>
</div></section>

<section class="sec" id="lage"><div class="wrap">
  <div class="punch">
    <div class="big">Marktführer im Angebot.<br>Mitläufer in der <em>Wahrnehmung</em>.</div>
    <p>Die Tanzschulen Familie Bothe führen 17 Tanzrichtungen — mehr als doppelt so viele
    wie der Median im Feld. Drei Häuser mit elf Sälen hat sonst niemand, und mit Gründung
    1954 ist es die älteste Schule im Test. Nichts davon erreicht potenzielle Kundinnen und
    Kunden dort, wo sie suchen: Bei {n_unbesetzt} von 7 geprüften Suchbegriffen ist Bothe
    nicht oder falsch vertreten.</p>
    <p>Das ist keine Frage des Marketings, sondern der Struktur. Wer 17 Tanzrichtungen
    anbietet, aber keine einzige Seite hat, die nach einer davon benannt ist, wird für
    diese Richtungen nicht gefunden. Genau hier setzt der Relaunch an — und deshalb endet
    diese Analyse nicht mit einer Mängelliste, sondern mit neun Anforderungen an die neue
    Website.</p>
    <div class="kb">
      <div><b>17</b><span>Tanzrichtungen — Höchstwert im Feld, bei einem Median von {MEDIAN}</span></div>
      <div><b>3</b><span>Standorte — kein anderer Anbieter in Hannover hat mehr als einen</span></div>
      <div><b>0</b><span>von 16 Anbietern nutzen Event-Markup. Freies Feld.</span></div>
      <div><b>61 €</b><span>im Monat — Platz 4 von 7, also Mittelfeld, nicht teuer</span></div>
    </div>
  </div>
</div></section>

<section class="sec warmbg" id="markt"><div class="wrap">
  <div class="shead">
    <div class="kick">Marktstruktur</div>
    <h2 class="hd2">Der Wettbewerb sind <em>nicht nur Tanzschulen</em></h2>
    <p class="lead">Im Raum Hannover kämpfen fünf sehr verschiedene Anbietertypen um dieselben
    Kundinnen und Kunden — und dazu sechs Portale, die selbst keinen einzigen Kurs anbieten.</p>
  </div>
  <div class="scroller"><table>
    <thead><tr><th>Segment</th><th>Anbieter</th><th>Womit sie angreifen</th></tr></thead>
    <tbody>
      <tr class="us"><td>Vollsortiment</td><td><b>Familie Bothe</b></td>
        <td>17 Richtungen, drei Häuser, Flatrate — das breiteste Angebot der Region</td></tr>
      <tr><td>Klassische Tanzschulen</td><td>Susanne Bothe, Meiners, Feeling, Move &amp; Dance, Gräper, Jegella, Kressler</td>
        <td>Paartanz und Schülerkurse; Susanne Bothe zusätzlich über den gleichen Namen</td></tr>
      <tr><td>Preis- und Spezialanbieter</td><td>Happy Hours, Salsa del Alma, U-Dance</td>
        <td>Einzelne Tanzstile in der Tiefe, dazu offensive Preiswerbung</td></tr>
      <tr><td>Urban-Studios</td><td>Move &amp; Style, dafunk.dance, Physicalpark</td>
        <td>Hip Hop, Streetdance und Kindertanz — greifen direkt Studio B an</td></tr>
      <tr><td>Vereine</td><td>TTC Gelb-Weiss, TSC Phoenix</td>
        <td>Beiträge ab 15,50 € im Monat, Turnier- und Vereinsstruktur</td></tr>
      <tr><td>Portale</td><td>citysports, heiraten.de, tanzkurs.com, vuvivi, myweddingdance, superprof</td>
        <td>Bieten keinen Kurs an und stehen trotzdem bei fast jedem Suchbegriff vorn</td></tr>
    </tbody>
  </table></div>
  <div class="port" style="margin-top:30px">
{"".join(f'<div class="pcard"><h4>{E(n)}</h4><div class="pk">{E(t)}</div><p>{E(b)}</p></div>' for n, t, b in PORTALE)}
  </div>
</div></section>

<section class="sec" id="angebot"><div class="wrap">
  <div class="shead">
    <div class="kick">Angebotstiefe</div>
    <h2 class="hd2">Wo Bothe <em>allein steht</em></h2>
    <p class="lead">Vierzehn verbreitete Tanzrichtungen, sechzehn Anbieter. Bothe ist der
    einzige, der alle vierzehn führt — und der einzige mit Swing im Programm. Welttanzprogramm
    und Medaillenkurse bieten nur zwei von sechzehn.</p>
  </div>
  {matrix()}
  <p class="lead" style="margin-top:20px">Das ist das stärkste Verkaufsargument im gesamten
  Markt: <b>Wer einmal anfängt, kann bei Bothe alles lernen, ohne die Schule zu wechseln.</b>
  Auf der bisherigen Website ist dieser Gedanke nirgends formuliert.</p>
</div></section>

<section class="sec warmbg" id="preise"><div class="wrap">
  <div class="shead">
    <div class="kick r">Preislandschaft</div>
    <h2 class="hd2">Bothe ist <em>nicht teuer</em></h2>
    <p class="lead">Vergleichbar gemacht: Monatspreis für den größten Zugang, den ein Anbieter
    verkauft. Wochenpreise wurden mit 52 ÷ 12 umgerechnet. Sieben der 16 Anbieter
    veröffentlichen überhaupt einen Preis — Bothe gehört nicht dazu.</p>
  </div>
  {preisgrafik()}
  <p class="lead" style="margin-top:22px">Mit 61 € liegt Bothe auf <b>Platz 4 von 7</b> —
  günstiger als Move &amp; Style Unlimited, Salsa del Alma und Meiners. Dazu kommt die
  Vertragsform: Move &amp; Style bindet <b>52 Wochen</b>, Happy Hours verlangt bis zu 90 Tage
  Kündigungsfrist, Meiners rechnet über zwölf Monate. Bothe ist also im Mittelfeld beim Preis,
  vorn beim Angebot und flexibel beim Vertrag. <b>Nur steht das nirgends.</b></p>
</div></section>

<section class="sec" id="nachfrage"><div class="wrap">
  <div class="shead">
    <div class="kick">Nachfrage</div>
    <h2 class="hd2">Wonach gesucht wird — und <em>wer dort steht</em></h2>
    <p class="lead">Geprüft wurde, welche Anbieter zu diesen sieben Suchanfragen überhaupt mit
    einer eigenen Seite erscheinen. Das ist eine Anwesenheitsprüfung, kein Positions-Tracking —
    aber wer gar nicht auftaucht, steht auf keinem Platz.</p>
  </div>
  {sicht()}
  <p class="lead" style="margin-top:22px">Der einzige klare Treffer ist
  <b>/schuelertanzkurse/</b> — bezeichnenderweise die einzige Seite im ganzen Auftritt, die
  wie eine richtige Kursseite aufgebaut ist, mit eigenem Thema, Preis und Ablauf. Sie ist
  damit der beste vorhandene Beleg dafür, dass das Muster funktioniert.</p>
</div></section>

<section class="sec warmbg" id="swot"><div class="wrap">
  <div class="shead">
    <div class="kick r">Position</div>
    <h2 class="hd2">Stärken, Schwächen, <em>Chancen, Risiken</em></h2>
    <p class="lead">Jeder Punkt hier stammt aus den erhobenen Daten, nicht aus Einschätzung.</p>
  </div>
  {swot()}
</div></section>

<section class="sec" id="profile"><div class="wrap">
  <div class="shead">
    <div class="kick">Wettbewerberprofile</div>
    <h2 class="hd2">Jeder Anbieter <em>in seinen eigenen Farben</em></h2>
    <p class="lead">Die Farbstreifen stammen aus dem Quelltext der jeweiligen Website — aus
    theme-color-Angaben, benannten Marken-Variablen und den Regeln für Kopf, Navigation und
    Schaltflächen. Bootstrap- und WordPress-Standardpaletten sind herausgefiltert, damit hier
    Marke steht und nicht Framework.</p>
  </div>
  <div class="profs">
{"".join(profil(a) for a in sorted(ANBIETER, key=lambda x: (not x["wir"], -len(x["stile"]))))}
  </div>
</div></section>

<section class="sec warmbg" id="relaunch"><div class="wrap">
  <div class="shead">
    <div class="kick r">Ergebnis</div>
    <h2 class="hd2">Neun Anforderungen an <em>die neue Website</em></h2>
    <p class="lead">Abgeleitet aus dem, was der Markt tatsächlich tut — nicht aus allgemeinen
    Empfehlungen. Die Reihenfolge folgt der Wirkung, die Kennzeichnung dem Verbindlichkeitsgrad.</p>
  </div>
  {anforderungen()}
  <p class="lead" style="margin-top:30px"><b>Der wichtigste Satz dieser Analyse:</b>
  Punkt 3 entscheidet über alle anderen. Eine neue Website, die die 396 bestehenden Adressen
  nicht weiterleitet, startet bei null — egal wie gut sie gebaut ist. Der Weiterleitungsplan
  gehört deshalb vor die Gestaltung, nicht danach.</p>
</div></section>

<footer><div class="wrap">
  <h4>Methodik und Grenzen</h4>
  <p>Alle technischen Werte stammen aus einem eigenen Live-Abruf am 17. August 2026: Quelltext,
  HTTP-Kopfzeilen, robots.txt und XML-Sitemaps von 16 Anbietern im Raum Hannover. Antwortzeiten
  sind Einzelmessungen und schwanken tageszeitabhängig. Das Kursangebot wurde aus den Websites
  der Anbieter ausgelesen; es bildet ab, was dort beworben wird — nicht zwingend jeden
  tatsächlich laufenden Kurs.</p>
  <p><b style="color:var(--ink)">Die Nachfrageprüfung ist kein Positions-Tracking.</b> Geprüft
  wurde, welche Anbieter zu sieben Suchanfragen überhaupt mit einer Seite erscheinen — nicht,
  auf welchem Platz. Für echte Positionen, Suchvolumen und Klickzahlen ist Zugriff auf die
  Google Search Console des Kontos oder ein Sistrix-Abo nötig; beides lag nicht vor. Die
  Aussage „bei {n_unbesetzt} von 7 Suchbegriffen nicht besetzt“ ist belastbar, eine Aussage wie
  „Platz 14“ wäre es nicht.</p>
  <p>Preise sind als <b style="color:var(--ink)">Website</b> gekennzeichnet, wenn sie auf der
  Anbieterseite gelesen wurden, und als <b style="color:var(--ink)">Snippet</b>, wenn sie nur
  aus einem Suchergebnis-Auszug stammen. Vor einer Preisdiskussion sollten die Snippet-Werte
  einzeln geprüft werden. u-dance.de war während der gesamten Erhebung nicht erreichbar.</p>
  <p>Markenfarben wurden aus theme-color-Angaben, benannten CSS-Marken-Variablen und
  Komponentenregeln gewonnen; bekannte Bootstrap- und WordPress-Standardpaletten sind
  ausgeschlossen. Für die Tanzschulen Familie Bothe wurde das dokumentierte CI aus der eigenen
  Stylesheet-Datei verwendet. Gründungsjahre stammen aus Selbstauskünften der Anbieter.</p>
</div></footer>
"""

if __name__ == "__main__":
    p = SP / "marktanalyse-bothe.html"
    p.write_text(DOC, encoding="utf-8")
    print(f"{p.name} — {len(DOC) / 1024:.0f} kB")
