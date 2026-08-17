#!/usr/bin/env python3
"""Baut die Marktanalyse als lokale Website in `site/`.

Anders als die Einzeldokumente ist das hier zum Durchklicken gedacht: Übersicht,
Markt, Angebot, Preise, Nachfrage, Position, Anforderungen — und je eine
Detailseite pro Anbieter.

Gestaltung bewusst neutral. Die Kundendokumente laufen im Bothe-CI; eine
Marktanalyse, die auch den Wettbewerb bewertet, soll nicht aussehen, als käme
sie von einer der bewerteten Parteien.

    python3 site_bauen.py      # Seiten erzeugen
    python3 serve.py           # lokal ausliefern
"""
import html, json, pathlib, re, shutil, sys
from collections import Counter

HIER = pathlib.Path(__file__).parent
QUELLEN = HIER / "quellen"
sys.path.insert(0, str(HIER / "analyse"))
try:
    from markt_daten import ANBIETER, SICHTBARKEIT, PORTALE
except ImportError:
    sys.exit("analyse/markt_daten.py fehlt — bitte das vollständige Repository verwenden.")

ZIEL = HIER / "site"
E = lambda s: html.escape(str(s), quote=True)
WIR = next(a for a in ANBIETER if a["wir"])
STAND = "17. August 2026"

VERBREITUNG = Counter()
for a in ANBIETER:
    for s in a["stile"]:
        VERBREITUNG[s] += 1
STILZAHL = sorted(len(a["stile"]) for a in ANBIETER)
MEDIAN = STILZAHL[len(STILZAHL) // 2]
UNBESETZT = sum(1 for s in SICHTBARKEIT if s["status"] in ("nein", "falsch"))
MATRIX_STILE = ["Standard", "Latein", "Discofox", "Salsa", "Bachata", "Hip Hop",
                "Breakdance", "Contemporary", "Ballett", "Kindertanz", "Linedance",
                "Hochzeit", "Privatstunde", "Welttanzprogramm"]

NAV = [("index.html", "Übersicht"), ("markt.html", "Markt"),
       ("angebot.html", "Angebot"), ("preise.html", "Preise"),
       ("nachfrage.html", "Nachfrage"), ("position.html", "Position"),
       ("anbieter/index.html", "Anbieter"), ("relaunch.html", "Anforderungen"),
       ("methodik.html", "Methodik")]


def slug(dom):
    return re.sub(r"[^a-z0-9]+", "-", dom.lower()).strip("-")


def seite(datei, titel, beschreibung, inhalt, tiefe=0):
    """Ein Dokument mit gemeinsamem Kopf, Navigation und Fuß."""
    auf = "../" * tiefe
    nav = "".join(
        f'<a href="{auf}{h}"{" aria-current=page" if h == datei else ""}>{E(t)}</a>'
        for h, t in NAV)
    doc = f"""<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{E(titel)} — Marktanalyse Tanzschulen Hannover</title>
<meta name="description" content="{E(beschreibung)}">
<link rel="stylesheet" href="{auf}assets/fonts.css">
<link rel="stylesheet" href="{auf}assets/stil.css">
</head>
<body>
<a class="skip" href="#inhalt">Zum Inhalt springen</a>
<header class="kopf">
  <div class="wrap kopfin">
    <a class="marke" href="{auf}index.html">
      <span class="mtitel">Marktanalyse</span>
      <span class="muntertitel">Tanzschulen Hannover</span>
    </a>
    <nav class="nav">{nav}</nav>
  </div>
</header>
<main id="inhalt">
{inhalt}
</main>
<footer class="fuss">
  <div class="wrap">
    <p><b>Marktanalyse Tanzschulen Familie Bothe</b> · Erhebung {STAND} ·
    16 Anbieter im Raum Hannover</p>
    <p>Alle technischen Werte aus einem eigenen Live-Abruf. Die Nachfrageprüfung ist
    eine Anwesenheitsprüfung, kein Positions-Tracking —
    <a href="{auf}methodik.html">Methodik und Grenzen</a>.</p>
  </div>
</footer>
</body>
</html>
"""
    p = ZIEL / datei
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(doc, encoding="utf-8")


def kopfzeile(kicker, titel, lead, kennzahlen=None):
    kz = ""
    if kennzahlen:
        kz = '<dl class="kennzahlen">' + "".join(
            f"<div><dt>{E(l)}</dt><dd>{E(w)}</dd></div>" for w, l in kennzahlen) + "</dl>"
    return f"""<section class="titel">
  <div class="wrap">
    <p class="kicker">{E(kicker)}</p>
    <h1>{titel}</h1>
    <p class="lead">{lead}</p>
    {kz}
  </div>
</section>"""


# ----------------------------------------------------------------- Bausteine
def preistabelle():
    rows = sorted([a for a in ANBIETER if a["voll"]], key=lambda x: x["voll"])
    mx = max(r["voll"] for r in rows)
    balken = "".join(
        f'<div class="prow{" ist-wir" if r["wir"] else ""}">'
        f'<div class="pname">{E(r["kurz"])}<small>{E(r["voll_label"])}</small></div>'
        f'<div class="ptrack"><span class="pbar" style="width:{r["voll"] / mx * 100:.1f}%"></span>'
        f'<span class="pval">{r["voll"]:.2f}&nbsp;€</span></div>'
        f'<div class="pbind">{E(r["bindung"])}</div></div>' for r in rows)
    return (f'<figure class="chart" role="img" aria-label="Monatspreis für Vollzugang je '
            f'Anbieter, von 15,50 bis 90,00 Euro. Familie Bothe liegt mit 61,00 Euro auf '
            f'Platz vier von sieben.">{balken}</figure>')


def alle_preise():
    zeilen = []
    for a in sorted(ANBIETER, key=lambda x: (not x["wir"], x["kurz"])):
        if not a["preise"]:
            zeilen.append(f'<tr class="{"us" if a["wir"] else ""}">'
                          f'<td>{E(a["kurz"])}</td>'
                          f'<td colspan="4" class="leer">Kein Preis veröffentlicht</td></tr>')
            continue
        for i, (n, p, d, q) in enumerate(a["preise"]):
            name = E(a["kurz"]) if i == 0 else ""
            zeilen.append(
                f'<tr class="{"us" if a["wir"] else ""}{" folge" if i else ""}">'
                f'<td>{name}</td><td>{E(n)}</td><td class="n">{p:.2f} €</td>'
                f'<td>{E(d)}</td>'
                f'<td><span class="q q-{"w" if q == "Website" else "s"}">{E(q)}</span></td></tr>')
    return ('<div class="scroll"><table><thead><tr><th>Anbieter</th><th>Tarif</th>'
            '<th>Preis</th><th>Bedingungen</th><th>Quelle</th></tr></thead>'
            f'<tbody>{"".join(zeilen)}</tbody></table></div>')


def matrix():
    kopf = "".join(f"<th><span>{E(s)}</span></th>" for s in MATRIX_STILE)
    zeilen = []
    for a in sorted(ANBIETER, key=lambda x: (not x["wir"], -len(x["stile"]))):
        z = "".join(
            f'<td class="{"ja" if s in a["stile"] else "nein"}" '
            f'title="{E(a["kurz"])} — {E(s)}: {"ja" if s in a["stile"] else "nein"}">'
            f'{"●" if s in a["stile"] else "·"}</td>' for s in MATRIX_STILE)
        zeilen.append(f'<tr class="{"us" if a["wir"] else ""}">'
                      f'<td class="mname"><a href="anbieter/{slug(a["dom"])}.html">'
                      f'{E(a["kurz"])}</a></td>{z}<td class="n">{len(a["stile"])}</td></tr>')
    return (f'<div class="scroll"><table class="matrix"><thead><tr><th>Anbieter</th>{kopf}'
            f'<th>Σ</th></tr></thead><tbody>{"".join(zeilen)}</tbody></table></div>')


def verbreitung():
    zeilen = "".join(
        f'<tr class="{"us" if s in WIR["stile"] else ""}"><td>{E(s)}</td>'
        f'<td class="n">{n}</td>'
        f'<td><span class="mini" style="width:{n / 16 * 100:.0f}%"></span></td>'
        f'<td>{"im Programm" if s in WIR["stile"] else "—"}</td></tr>'
        for s, n in VERBREITUNG.most_common())
    return ('<div class="scroll"><table><thead><tr><th>Tanzrichtung</th>'
            '<th>Anbieter</th><th>Verbreitung</th><th>Bothe</th></tr></thead>'
            f'<tbody>{zeilen}</tbody></table></div>')


def sichtbarkeit():
    tag = {"ja": ("t-ok", "besetzt"), "teil": ("t-mid", "nur Sammelseite"),
           "falsch": ("t-mid", "falscher Titel"), "nein": ("t-no", "nicht besetzt")}
    out = []
    for s in SICHTBARKEIT:
        cls, lbl = tag[s["status"]]
        out.append(
            f'<article class="such"><div class="such-k">'
            f'<h3>{E(s["q"])}</h3><p class="klein">{E(s["note"])}</p>'
            f'<span class="tag {cls}">{lbl}</span></div>'
            f'<div class="such-b"><p><b>Bothe:</b> {E(s["wir"])}</p>'
            f'<p class="klein">Dort vertreten: {" · ".join(E(x) for x in s["andere"])}</p>'
            f'</div></article>')
    return f'<div class="suchliste">{"".join(out)}</div>'


SWOT = [
 ("staerke", "Stärken", [
   ("17 Tanzrichtungen", f"Mehr als doppelt so viele wie der Median im Feld ({MEDIAN}). Einziger Anbieter, der alle 14 verbreiteten Richtungen abdeckt."),
   ("Drei Häuser, elf Säle", "Kein anderer Anbieter in Hannover hat mehr als einen Standort."),
   ("Seit 1954, dritte Generation", "Älteste Schule im Feld — vier Jahre vor dem TTC Gelb-Weiss, 26 Jahre vor Meiners."),
   ("Eigene Ausbildung", "Tanzlehrerinnen und Tanzlehrer werden im Haus ausgebildet. Kein Wettbewerber wirbt damit."),
   ("Alleinstellung im Programm", "Welttanzprogramm und Medaillenkurse führen nur zwei von 16, Swing nur Bothe."),
   ("24 gepflegte Termine", "Ein laufendes Veranstaltungsprogramm in dieser Dichte hat sonst niemand."),
 ]),
 ("schwaeche", "Schwächen", [
   ("Kein Preis nach außen", "Sieben Anbieter veröffentlichen Preise, Bothe nicht."),
   ("Keine Seite pro Tanzstil", "Größtes Angebot im Markt, aber keine Adresse, die „Discofox“ oder „Hochzeitstanz“ heißt."),
   (f"Bei {UNBESETZT} von 7 Suchbegriffen nicht besetzt", "Darunter Hochzeitstanz, Discofox und Hip Hop — alle drei mit hohem Kundenwert."),
   ("Markenname doppelt belegt", "Zwei Bothes in Hannover; jede unspezifische Markensuche teilt sich auf."),
   ("Technisch Schlusslicht", "1 von 10 Basissignalen erfüllt — der niedrigste Wert im Feld."),
 ]),
 ("chance", "Chancen", [
   ("Event-Markup nutzt niemand", "Von 16 Anbietern zeichnet keiner Termine strukturiert aus. 24 gepflegte Termine liegen bereit."),
   ("Hochzeitstanz ist unbesetzt", "Höchster Kundenwert: Paare planen früh, zahlen gut, bleiben oft. Bothe erscheint dort nicht."),
   ("Der Preis ist ein Argument", "61 € sind Platz 4 von 7 — günstiger als Move & Style Unlimited, Salsa del Alma und Meiners, ohne 52-Wochen-Bindung."),
   ("Drei lokale Profile", "Drei gepflegte Google-Unternehmensprofile kann sonst niemand im Markt aufbieten."),
   ("Portale als Kanal", "citysports.de, heiraten.de und tanzkurs.com stehen überall vorn. Ein Eintrag ist billiger als Verdrängung."),
 ]),
 ("risiko", "Risiken", [
   ("Bothe Loft ab 2027", "1.600 m² am Bischofsholer Damm, seit September 2025 laufend dokumentiert. Frische Signale plus verschärfte Namensverwechslung zur Eröffnung."),
   ("Preisdruck von unten", "Happy Hours ab 29,90 €, TTC Gelb-Weiss ab 15,50 € im Monat — beide werben offensiv damit."),
   ("Move & Style beansprucht den Titel", "„Die beste Tanzschule in Hannover“ steht wörtlich im Seitentitel, dazu 14 Urban-Richtungen gegen Studio B."),
   ("Spezialisten schneiden Segmente heraus", "Salsa del Alma mit Weltmeister im Hip Hop, dafunk.dance als reine Streetdance-Schule, Physicalpark mit Kindertanz ab 9,90 €/Woche."),
   ("Sichtbarkeit beim Relaunch", "Die 396 bestehenden Adressen tragen die heutige Sichtbarkeit. Ohne Weiterleitungsplan geht sie beim Umzug verloren."),
 ]),
]

ANFORDERUNGEN = [
 ("Eine Seite pro Tanzstil", "muss",
  "Discofox, Hochzeitstanz, Salsa, Standard &amp; Latein, West Coast Swing, Hip Hop, "
  "Kindertanz, Tanzen ab 60 — je mit Terminen, Preis, Trainer, Standort und Fragen. "
  "Das ist der strukturelle Grund, warum kleinere Anbieter heute vor Bothe stehen.",
  "Sechs dieser Seiten sind bereits gebaut."),
 ("Preise sichtbar, mit Argument", "muss",
  "Nicht nur 61 € nennen, sondern einordnen: alle Kurse des Levels, drei Häuser, "
  "220 Angebote, monatlich kündbar. Gegen „günstigste Preise“ hilft kein niedrigerer "
  "Preis, sondern ein besserer Vergleich.",
  "Die Preisdaten aller Wettbewerber liegen vor."),
 ("Weiterleitungsplan für 396 Adressen", "muss",
  "Jede heute indexierte Adresse braucht ein Ziel auf der neuen Seite. Ohne das "
  "beginnt die neue Website bei null — unabhängig davon, wie gut sie gebaut ist.",
  "Größtes Risiko des Relaunches. Regeln für Dubletten und Altseiten liegen vor."),
 ("Strukturierte Daten ab Tag eins", "muss",
  "DanceSchool mit drei Standorten, Event für alle Termine, Course je Kursseite, "
  "FAQPage. Beim Neubau kostet das fast nichts, nachträglich ist es ein eigenes Projekt.",
  "Generator vorhanden, erzeugt 31 fertige Blöcke."),
 ("Drei echte Standortseiten", "muss",
  "Je eigene Seite mit Anfahrt, Parkplätzen, Sälen und laufenden Kursen, dazu je ein "
  "Google-Unternehmensprofil mit identischer Schreibweise.",
  "Drei Standorte hat im Markt sonst niemand."),
 ("Titel: Suchbegriff + Ort + Marke", "muss",
  "Nicht „Tanzschule Familie Bothe – Paartanz“, sondern „Paartanz für Erwachsene in "
  "Hannover“. Der Markenname gehört ans Ende.",
  "Vorgaben für 32 Kernseiten sind formuliert."),
 ("Marke gegen die Verwechslung schärfen", "soll",
  "„Tanzschulen Familie Bothe“ konsequent ausschreiben, Standorte mitnennen, die "
  "Geschichte seit 1954 sichtbar führen. Spätestens zur Eröffnung des Bothe Loft "
  "2027 wird das entscheidend.",
  "Zwei gleichnamige Schulen in einer Stadt sind ein Dauerthema."),
 ("Tempo als Anforderung", "soll",
  "Die alte Seite liefert 327 kB für 424 sichtbare Wörter. Beim Neubau gehört ein "
  "Zielwert ins Lastenheft, sonst wiederholt sich das.",
  "Der schnellste Anbieter im Feld liefert in 0,31 s aus."),
 ("Portaleinträge pflegen", "kann",
  "citysports.de, heiraten.de, tanzkurs.com und vuvivi.de stehen bei fast jedem "
  "Suchbegriff vorn. Ein gepflegter Eintrag ist billiger als der Versuch zu verdrängen.",
  "Sechs Portale sind benannt."),
]


STIL = r'''
/* Marktanalyse Tanzschulen Hannover — neutrales Beraterlayout.
   Bewusst ohne Bothe-CI: Ein Dokument, das auch den Wettbewerb bewertet,
   soll nicht aussehen, als käme es von einer der bewerteten Parteien.
   Ein Akzent (Schieferblau), sonst Grauwerte und Typografie. */
:root{
  --grund:#F5F5F4; --flaeche:#fff; --flaeche2:#EFEFED;
  --tinte:#191B1D; --tinte2:#3C4145; --gedaempft:#5E6367;
  --linie:rgba(0,0,0,.13); --linie2:rgba(0,0,0,.07);
  --akzent:#2A4A61; --akzent-hell:#E4EAEF; --akzent-text:#234156;
  --ok:#2C6A4A; --ok-bg:#E4EFE7; --warn:#7E5A11; --warn-bg:#F6EEDA;
  --bad:#9B2B33; --bad-bg:#F7E3E4;
  --display:Georgia,"Iowan Old Style","Palatino Linotype",Palatino,serif;
  --text:'Hanken Grotesk',system-ui,-apple-system,"Segoe UI",sans-serif;
  --daten:'Bricolage Grotesque','Hanken Grotesk',system-ui,sans-serif;
  --breit:1180px; --schmal:70ch;
}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){
  --grund:#121315; --flaeche:#1A1C1F; --flaeche2:#212429;
  --tinte:#EDEEEF; --tinte2:#C3C7CB; --gedaempft:#9BA1A6;
  --linie:rgba(255,255,255,.15); --linie2:rgba(255,255,255,.08);
  --akzent:#7FA8C4; --akzent-hell:#1D2A34; --akzent-text:#9DC2DB;
  --ok:#7FC79C; --ok-bg:#17281D; --warn:#DCB35C; --warn-bg:#2A2312;
  --bad:#E58A90; --bad-bg:#2C1719;
}}
:root[data-theme="dark"]{
  --grund:#121315; --flaeche:#1A1C1F; --flaeche2:#212429;
  --tinte:#EDEEEF; --tinte2:#C3C7CB; --gedaempft:#9BA1A6;
  --linie:rgba(255,255,255,.15); --linie2:rgba(255,255,255,.08);
  --akzent:#7FA8C4; --akzent-hell:#1D2A34; --akzent-text:#9DC2DB;
  --ok:#7FC79C; --ok-bg:#17281D; --warn:#DCB35C; --warn-bg:#2A2312;
  --bad:#E58A90; --bad-bg:#2C1719;
}
*{margin:0;padding:0;box-sizing:border-box}
html{scroll-behavior:smooth;scroll-padding-top:88px}
body{font-family:var(--text);color:var(--tinte);background:var(--grund);
  line-height:1.65;font-size:16.5px;-webkit-font-smoothing:antialiased;overflow-x:clip}
h1,h2,h3,h4{font-family:var(--display);font-weight:400;text-wrap:balance;line-height:1.18}
a{color:var(--akzent-text)}
:focus-visible{outline:2.5px solid var(--akzent);outline-offset:3px;border-radius:2px}
.skip{position:absolute;left:-9999px;top:0;background:var(--akzent);color:#fff;
  padding:11px 18px;z-index:100}
.skip:focus{left:10px;top:10px}
.wrap{max-width:var(--breit);margin:0 auto;padding:0 clamp(18px,4vw,40px)}
.klein{font-size:.86rem;color:var(--gedaempft)}
.lead{font-size:1.06rem;color:var(--tinte2);max-width:var(--schmal)}
p+p{margin-top:12px}

/* Kopf */
.kopf{position:sticky;top:0;z-index:50;background:color-mix(in srgb,var(--grund) 94%,transparent);
  backdrop-filter:blur(12px);border-bottom:1px solid var(--linie)}
.kopfin{display:flex;align-items:center;gap:26px;min-height:64px;flex-wrap:wrap}
.marke{text-decoration:none;color:var(--tinte);display:flex;flex-direction:column;
  line-height:1.15;flex:none;padding:8px 0}
.mtitel{font-family:var(--display);font-size:1.08rem}
.muntertitel{font-family:var(--daten);font-size:.62rem;letter-spacing:.17em;
  text-transform:uppercase;color:var(--gedaempft)}
.nav{display:flex;gap:2px;flex-wrap:wrap;margin-left:auto}
.nav a{font-family:var(--daten);font-weight:500;font-size:.79rem;color:var(--gedaempft);
  text-decoration:none;padding:7px 11px;border-radius:3px}
.nav a:hover{background:var(--flaeche2);color:var(--tinte)}
.nav a[aria-current]{background:var(--akzent-hell);color:var(--akzent-text);font-weight:600}

/* Titelbereich */
.titel{padding:clamp(42px,5.5vw,74px) 0 clamp(26px,3vw,38px);
  border-bottom:1px solid var(--linie)}
.kicker{font-family:var(--daten);font-weight:600;font-size:.7rem;letter-spacing:.19em;
  text-transform:uppercase;color:var(--akzent-text);margin-bottom:14px}
.titel h1{font-size:clamp(1.9rem,4.4vw,3.05rem);max-width:20ch;letter-spacing:-.012em}
.titel .lead{margin-top:16px}
.kennzahlen{display:flex;flex-wrap:wrap;gap:0;margin-top:28px;padding-top:18px;
  border-top:1px solid var(--linie)}
.kennzahlen div{padding-right:28px;margin-right:28px;border-right:1px solid var(--linie);
  margin-bottom:10px}
.kennzahlen div:last-child{border:0;margin-right:0;padding-right:0}
.kennzahlen dt{font-family:var(--daten);font-size:.66rem;letter-spacing:.14em;
  text-transform:uppercase;color:var(--gedaempft);order:2;margin-top:4px}
.kennzahlen div{display:flex;flex-direction:column}
.kennzahlen dd{font-family:var(--display);font-size:1.75rem;line-height:1;order:1;
  font-variant-numeric:tabular-nums}

.block{padding:clamp(34px,4.4vw,58px) 0}
.ueber{font-size:1.45rem;margin:44px 0 10px}
.ueber+.lead{margin-bottom:18px}
.hinweis{margin-top:20px;padding:16px 20px;background:var(--flaeche);
  border:1px solid var(--linie);border-left:3px solid var(--akzent);
  max-width:var(--schmal);font-size:.97rem}
.hinweis.stark{border-left-color:var(--bad);background:var(--bad-bg)}
.text{max-width:var(--schmal)}
.text h2{font-size:1.35rem;margin:30px 0 8px}
.text h2:first-child{margin-top:0}

/* Befundkasten */
.befund{background:var(--flaeche);border:1px solid var(--linie);padding:clamp(22px,3vw,34px);
  max-width:var(--schmal)}
.befund h2{font-size:clamp(1.3rem,2.6vw,1.75rem);margin-bottom:14px}
.befund p{color:var(--tinte2)}

/* Kacheln */
.kacheln{display:grid;gap:14px;grid-template-columns:repeat(auto-fill,minmax(255px,1fr));
  margin-top:34px}
.kachel{display:block;text-decoration:none;color:inherit;background:var(--flaeche);
  border:1px solid var(--linie);padding:20px 22px;transition:border-color .18s,transform .18s}
.kachel:hover{border-color:var(--akzent);transform:translateY(-2px)}
.kachel.stark{border-left:3px solid var(--akzent)}
.kn{font-family:var(--daten);font-size:.68rem;letter-spacing:.15em;color:var(--gedaempft)}
.kachel h3{font-size:1.18rem;margin:7px 0 6px}
.kachel p{font-size:.9rem;color:var(--gedaempft)}

/* Tabellen */
.scroll{overflow-x:auto;border:1px solid var(--linie);background:var(--flaeche);margin-top:6px}
table{border-collapse:collapse;width:100%;font-size:.9rem;min-width:640px}
th,td{text-align:left;padding:9px 13px;border-bottom:1px solid var(--linie2);vertical-align:top}
thead th{font-family:var(--daten);font-weight:600;font-size:.65rem;letter-spacing:.12em;
  text-transform:uppercase;color:var(--gedaempft);background:var(--flaeche2);
  border-bottom:1px solid var(--linie);white-space:nowrap;position:sticky;top:0}
tbody tr:last-child td{border-bottom:0}
tr.folge td{border-top:0}
td.n{font-variant-numeric:tabular-nums;white-space:nowrap;font-family:var(--daten)}
tr.us{background:var(--akzent-hell)}
tr.us td{font-weight:600}
.leer{color:var(--gedaempft);font-style:italic}
.mini{display:block;height:7px;background:var(--akzent);opacity:.55;min-width:2px}

.matrix td{text-align:center;padding:7px 5px}
.matrix td.mname{text-align:left;font-family:var(--daten);font-weight:600;white-space:nowrap}
.matrix td.mname a{color:inherit;text-decoration:none;border-bottom:1px solid var(--linie)}
.matrix td.mname a:hover{color:var(--akzent-text);border-color:var(--akzent)}
.matrix td.ja{color:var(--akzent);font-size:1.05rem}
.matrix td.nein{color:var(--linie)}
.matrix thead th{writing-mode:vertical-rl;transform:rotate(180deg);padding:11px 4px;
  font-size:.6rem;height:120px;position:static}
.matrix thead th:first-child,.matrix thead th:last-child{writing-mode:horizontal-tb;
  transform:none;height:auto}

.tag{display:inline-block;font-family:var(--daten);font-weight:600;font-size:.64rem;
  letter-spacing:.07em;text-transform:uppercase;padding:3px 8px;border-radius:2px;
  white-space:nowrap}
.t-ok,.a-kann{background:var(--ok-bg);color:var(--ok)}
.t-mid,.a-soll{background:var(--warn-bg);color:var(--warn)}
.t-no,.a-muss{background:var(--bad-bg);color:var(--bad)}
.q{font-family:var(--daten);font-size:.6rem;letter-spacing:.08em;text-transform:uppercase;
  padding:2px 7px;border-radius:2px;font-weight:600;white-space:nowrap}
.q-w{background:var(--ok-bg);color:var(--ok)}
.q-s{background:var(--warn-bg);color:var(--warn)}

/* Preisgrafik */
.chart{background:var(--flaeche);border:1px solid var(--linie);padding:22px 20px;
  display:flex;flex-direction:column;margin:0}
.prow{display:grid;grid-template-columns:1fr;gap:4px 16px;padding:10px 0}
.prow+.prow{border-top:1px solid var(--linie2)}
@media(min-width:760px){.prow{grid-template-columns:186px 1fr 164px;align-items:center}}
.pname{font-family:var(--daten);font-weight:600;font-size:.92rem}
.pname small{display:block;font-family:var(--text);font-weight:400;color:var(--gedaempft);
  font-size:.78rem;margin-top:1px}
.ptrack{display:flex;align-items:center;gap:10px;min-height:20px}
.pbar{height:13px;background:color-mix(in srgb,var(--tinte) 24%,transparent);
  border-radius:0 3px 3px 0;flex:none}
.prow.ist-wir .pbar{background:var(--akzent)}
.pval{font-family:var(--daten);font-weight:600;font-size:.89rem;
  font-variant-numeric:tabular-nums;white-space:nowrap}
.prow.ist-wir .pval,.prow.ist-wir .pname{color:var(--akzent-text)}
.pbind{font-size:.79rem;color:var(--gedaempft);font-family:var(--daten)}

/* Suchbegriffe */
.suchliste{display:flex;flex-direction:column;border-top:1px solid var(--tinte)}
.such{display:grid;grid-template-columns:1fr;gap:8px 24px;padding:18px 0;
  border-bottom:1px solid var(--linie)}
@media(min-width:820px){.such{grid-template-columns:270px 1fr;align-items:start}}
.such h3{font-size:1.1rem}
.such-k .tag{margin-top:7px}
.such-b p{font-size:.94rem}
.such-b b{color:var(--akzent-text)}

/* SWOT */
.swotgrid{display:grid;gap:16px;grid-template-columns:repeat(auto-fit,minmax(320px,1fr))}
.swot{background:var(--flaeche);border:1px solid var(--linie);padding:22px 24px;
  border-top:3px solid var(--akzent)}
.swot.schwaeche{border-top-color:var(--bad)}
.swot.chance{border-top-color:var(--ok)}
.swot.risiko{border-top-color:var(--warn)}
.swot h2{font-size:1.3rem;margin-bottom:16px}
.swot ul{list-style:none;display:flex;flex-direction:column;gap:14px}
.swot li{display:flex;flex-direction:column;gap:3px}
.swot li b{font-family:var(--daten);font-weight:600;font-size:.94rem}
.swot li span{color:var(--gedaempft);font-size:.9rem}

/* Anforderungen */
.anfliste{display:flex;flex-direction:column;border-top:1px solid var(--tinte)}
.anf{display:grid;grid-template-columns:40px 1fr;gap:18px;padding:20px 0;
  border-bottom:1px solid var(--linie)}
.anr{font-family:var(--display);font-size:1.25rem;color:var(--gedaempft);
  font-variant-numeric:tabular-nums}
.anh{display:flex;gap:11px;align-items:center;flex-wrap:wrap;margin-bottom:6px}
.anh h3{font-size:1.15rem}
.anf p{color:var(--tinte2);font-size:.96rem;max-width:var(--schmal)}
.anfuss{margin-top:8px;font-size:.86rem;color:var(--gedaempft);
  border-left:2px solid var(--linie);padding-left:11px}

/* Portale */
.portale{display:grid;gap:14px;grid-template-columns:repeat(auto-fit,minmax(275px,1fr));
  margin-top:8px}
.portal{background:var(--flaeche);border:1px solid var(--linie);padding:18px 20px}
.portal h3{font-size:1.05rem}
.portal p{font-size:.9rem;color:var(--gedaempft);margin-top:6px}

/* Anbieterkacheln */
.akacheln{display:grid;gap:14px;grid-template-columns:repeat(auto-fill,minmax(280px,1fr))}
.akachel{display:block;text-decoration:none;color:inherit;background:var(--flaeche);
  border:1px solid var(--linie);padding:0 0 16px;overflow:hidden;
  transition:border-color .18s,transform .18s}
.akachel:hover{border-color:var(--akzent);transform:translateY(-2px)}
.akachel.ist-wir{border-color:var(--akzent);border-width:2px}
.astreif{display:block;height:5px;background:var(--c1)}
.aseg{display:block;font-family:var(--daten);font-size:.64rem;letter-spacing:.13em;
  text-transform:uppercase;color:var(--gedaempft);padding:15px 20px 0}
.akachel h3{font-size:1.1rem;padding:5px 20px 0}
.adom{display:block;font-family:var(--daten);font-size:.79rem;color:var(--gedaempft);
  padding:3px 20px 0}
.amini{display:flex;gap:22px;padding:13px 20px 0;margin-top:11px;
  border-top:1px solid var(--linie2)}
.amini dt{font-family:var(--daten);font-size:.62rem;letter-spacing:.11em;
  text-transform:uppercase;color:var(--gedaempft)}
.amini dd{font-family:var(--daten);font-weight:600;font-size:.94rem;
  font-variant-numeric:tabular-nums;margin-top:1px}

/* Anbieterprofil */
.aprofil{border-bottom:3px solid var(--c1)}
.adomgross{font-family:var(--daten);font-size:.95rem;color:var(--gedaempft);margin-top:6px}
.farbleiste{display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin-top:20px}
.sw{font-family:var(--daten);font-size:.66rem;font-weight:600;padding:4px 10px;
  border-radius:2px;color:#fff;text-shadow:0 1px 2px rgba(0,0,0,.6);letter-spacing:.04em}
.zweispalt{display:grid;gap:24px;grid-template-columns:repeat(auto-fit,minmax(280px,1fr))}
.zweispalt h2{font-size:1.15rem;margin-bottom:7px}
.zweispalt p{color:var(--tinte2);font-size:.96rem}
.stilliste{display:flex;flex-wrap:wrap;gap:7px}
.st{font-family:var(--daten);font-size:.8rem;font-weight:600;padding:5px 11px;
  border:1px solid var(--linie);border-radius:2px;display:inline-flex;gap:7px;
  align-items:baseline}
.st small{font-weight:400;color:var(--gedaempft);font-size:.72rem}
.messwerte{display:grid;gap:14px;grid-template-columns:repeat(auto-fit,minmax(130px,1fr));
  background:var(--flaeche);border:1px solid var(--linie);padding:20px}
.messwerte dt{font-family:var(--daten);font-size:.63rem;letter-spacing:.12em;
  text-transform:uppercase;color:var(--gedaempft)}
.messwerte dd{font-family:var(--daten);font-weight:600;font-size:1.05rem;
  font-variant-numeric:tabular-nums;margin-top:2px}
.zurueck{margin-top:34px;padding-top:18px;border-top:1px solid var(--linie)}

/* Fuß */
.fuss{border-top:1px solid var(--linie);padding:26px 0 54px;margin-top:34px;
  color:var(--gedaempft);font-size:.85rem}
.fuss p{max-width:78ch}
.fuss p+p{margin-top:7px}
@media (prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}
  html{scroll-behavior:auto}}
@media print{.kopf,.nav{position:static}.kachel,.akachel{break-inside:avoid}}
'''


# ------------------------------------------------------------------- Seiten
def bau_index():
    inhalt = kopfzeile(
        f"Erhebung {STAND}",
        "Das größte Angebot der Stadt.<br>Und kaum jemand weiß&nbsp;es.",
        "Eine Vollerhebung des Tanzschulmarkts Hannover: 16 Anbieter, ihre Preise, ihr "
        "Kursprogramm, ihre Websites. Und die Frage, was die neue Bothe-Website leisten "
        "muss, damit aus dem größten Angebot auch die stärkste Position wird.",
        [("16", "Anbieter erhoben"), ("17", "Richtungen bei Bothe"),
         (str(MEDIAN), "Median im Markt"), ("31", "Preisangaben"),
         ("7", "Suchbegriffe geprüft")])

    inhalt += f"""
<section class="block"><div class="wrap">
  <div class="befund">
    <h2>Marktführer im Angebot. Mitläufer in der Wahrnehmung.</h2>
    <p>Die Tanzschulen Familie Bothe führen 17 Tanzrichtungen — mehr als doppelt so viele
    wie der Median im Feld. Drei Häuser mit elf Sälen hat sonst niemand, und mit Gründung
    1954 ist es die älteste Schule im Test. Nichts davon erreicht potenzielle Kundinnen
    und Kunden dort, wo sie suchen: Bei {UNBESETZT} von 7 geprüften Suchbegriffen ist
    Bothe nicht oder falsch vertreten.</p>
    <p>Das ist keine Frage des Marketings, sondern der Struktur. Wer 17 Tanzrichtungen
    anbietet, aber keine einzige Seite hat, die nach einer davon benannt ist, wird dafür
    nicht gefunden.</p>
  </div>
  <div class="kacheln">
    <a class="kachel" href="markt.html"><span class="kn">01</span><h3>Der Markt</h3>
      <p>16 Anbieter in fünf Segmenten — plus sechs Portale, die selbst keinen Kurs anbieten.</p></a>
    <a class="kachel" href="angebot.html"><span class="kn">02</span><h3>Angebot</h3>
      <p>Wo Bothe allein steht: 17 Richtungen gegen einen Median von {MEDIAN}.</p></a>
    <a class="kachel" href="preise.html"><span class="kn">03</span><h3>Preise</h3>
      <p>31 Preisangaben, vergleichbar gemacht. Bothe liegt auf Platz 4 von 7.</p></a>
    <a class="kachel" href="nachfrage.html"><span class="kn">04</span><h3>Nachfrage</h3>
      <p>Sieben Suchbegriffe und wer sie besetzt. Bothe fehlt bei {UNBESETZT}.</p></a>
    <a class="kachel" href="position.html"><span class="kn">05</span><h3>Position</h3>
      <p>Stärken, Schwächen, Chancen und Risiken — vollständig aus den Daten abgeleitet.</p></a>
    <a class="kachel" href="anbieter/index.html"><span class="kn">06</span><h3>Anbieter</h3>
      <p>Je ein Detailprofil für alle 16 Anbieter: Programm, Preise, Technik.</p></a>
    <a class="kachel stark" href="relaunch.html"><span class="kn">07</span><h3>Anforderungen</h3>
      <p>Neun Anforderungen an die neue Website — das Ergebnis dieser Analyse.</p></a>
    <a class="kachel" href="methodik.html"><span class="kn">08</span><h3>Methodik</h3>
      <p>Wie erhoben wurde und wo die Grenzen dieser Analyse liegen.</p></a>
  </div>
</div></section>"""
    seite("index.html", "Übersicht",
          "Marktanalyse Tanzschulen Familie Bothe: 16 Anbieter im Raum Hannover.", inhalt)


def bau_markt():
    zeilen = [
      ("Vollsortiment", "<b>Familie Bothe</b>",
       "17 Richtungen, drei Häuser, Flatrate — das breiteste Angebot der Region", True),
      ("Klassische Tanzschulen",
       "Susanne Bothe, Meiners, Feeling, Move &amp; Dance, Gräper, Jegella, Kressler",
       "Paartanz und Schülerkurse; Susanne Bothe zusätzlich über den gleichen Namen", False),
      ("Preis- und Spezialanbieter", "Happy Hours, Salsa del Alma, U-Dance",
       "Einzelne Tanzstile in der Tiefe, dazu offensive Preiswerbung", False),
      ("Urban-Studios", "Move &amp; Style, dafunk.dance, Physicalpark",
       "Hip Hop, Streetdance und Kindertanz — greifen direkt Studio B an", False),
      ("Vereine", "TTC Gelb-Weiss, TSC Phoenix",
       "Beiträge ab 15,50 € im Monat, Turnier- und Vereinsstruktur", False),
      ("Portale", "citysports, heiraten.de, tanzkurs.com, vuvivi, myweddingdance, superprof",
       "Bieten keinen Kurs an und stehen trotzdem bei fast jedem Suchbegriff vorn", False),
    ]
    tab = "".join(f'<tr class="{"us" if u else ""}"><td>{s}</td><td>{a}</td><td>{b}</td></tr>'
                  for s, a, b, u in zeilen)
    port = "".join(f'<article class="portal"><h3>{E(n)}</h3>'
                   f'<p class="klein">{E(t)}</p><p>{E(b)}</p></article>'
                   for n, t, b in PORTALE)
    inhalt = kopfzeile("Marktstruktur", "Der Wettbewerb sind nicht nur Tanzschulen",
        "Im Raum Hannover kämpfen fünf sehr verschiedene Anbietertypen um dieselben "
        "Kundinnen und Kunden — und dazu sechs Portale, die selbst keinen einzigen "
        "Kurs anbieten.")
    inhalt += f"""
<section class="block"><div class="wrap">
  <div class="scroll"><table><thead><tr><th>Segment</th><th>Anbieter</th>
    <th>Womit sie angreifen</th></tr></thead><tbody>{tab}</tbody></table></div>
  <h2 class="ueber">Die Portale im Einzelnen</h2>
  <p class="lead">Sie unterrichten nichts, haben keinen Saal und keinen Trainer — und
  stehen trotzdem bei fast jedem Suchbegriff vorn. Weil sie exakt die Seiten gebaut
  haben, die den Suchanfragen entsprechen.</p>
  <div class="portale">{port}</div>
</div></section>"""
    seite("markt.html", "Der Markt",
          "16 Anbieter in fünf Segmenten plus sechs Portale.", inhalt)


def bau_angebot():
    allein = [s for s in WIR["stile"] if VERBREITUNG[s] <= 2]
    inhalt = kopfzeile("Angebotstiefe", "Wo Bothe allein steht",
        f"Vierzehn verbreitete Tanzrichtungen, sechzehn Anbieter. Bothe ist der einzige, "
        f"der alle vierzehn führt — und der einzige mit Swing im Programm.",
        [("17", "Richtungen bei Bothe"), (str(MEDIAN), "Median im Feld"),
         (str(len(allein)), "davon fast exklusiv")])
    inhalt += f"""
<section class="block"><div class="wrap">
  {matrix()}
  <p class="hinweis">Das ist das stärkste Verkaufsargument im gesamten Markt:
  <b>Wer einmal anfängt, kann bei Bothe alles lernen, ohne die Schule zu wechseln.</b>
  Auf der bisherigen Website ist dieser Gedanke nirgends formuliert.</p>
  <h2 class="ueber">Verbreitung jeder Tanzrichtung</h2>
  <p class="lead">Wie viele der 16 Anbieter führen eine Richtung überhaupt? Je seltener,
  desto weniger Wettbewerb — und desto eher lohnt eine eigene Seite dafür.</p>
  {verbreitung()}
</div></section>"""
    seite("angebot.html", "Angebot", "Kursangebot im Vergleich über 16 Anbieter.", inhalt)


def bau_preise():
    inhalt = kopfzeile("Preislandschaft", "Bothe ist nicht teuer",
        "Vergleichbar gemacht: Monatspreis für den größten Zugang, den ein Anbieter "
        "verkauft. Wochenpreise wurden mit 52&nbsp;÷&nbsp;12 umgerechnet. Sieben der 16 "
        "Anbieter veröffentlichen überhaupt einen Preis — Bothe gehört nicht dazu.",
        [("61,00 €", "Bothe im Monat"), ("4 von 7", "Platz im Preisfeld"),
         ("15,50–90 €", "Spanne im Markt")])
    inhalt += f"""
<section class="block"><div class="wrap">
  {preistabelle()}
  <p class="hinweis">Mit 61 € liegt Bothe auf <b>Platz 4 von 7</b> — günstiger als
  Move &amp; Style Unlimited, Salsa del Alma und Meiners. Dazu kommt die Vertragsform:
  Move &amp; Style bindet <b>52 Wochen</b>, Happy Hours verlangt bis zu 90 Tage
  Kündigungsfrist, Meiners rechnet über zwölf Monate. Bothe ist also Mittelfeld beim
  Preis, vorn beim Angebot und flexibel beim Vertrag. <b>Nur steht das nirgends.</b></p>
  <h2 class="ueber">Alle erhobenen Tarife</h2>
  <p class="lead">31 Angaben. <span class="q q-w">Website</span> bedeutet auf der
  Anbieterseite gelesen, <span class="q q-s">Snippet</span> nur aus einem
  Suchergebnis-Auszug — diese Werte vor einer Preisdiskussion einzeln prüfen.</p>
  {alle_preise()}
</div></section>"""
    seite("preise.html", "Preise", "31 erhobene Preisangaben im Vergleich.", inhalt)


def bau_nachfrage():
    inhalt = kopfzeile("Nachfrage", "Wonach gesucht wird — und wer dort steht",
        "Geprüft wurde, welche Anbieter zu diesen sieben Suchanfragen überhaupt mit einer "
        "eigenen Seite erscheinen. Das ist eine Anwesenheitsprüfung, kein "
        "Positions-Tracking — aber wer gar nicht auftaucht, steht auf keinem Platz.",
        [(f"{UNBESETZT} von 7", "ohne Bothe"), ("1", "klarer Treffer")])
    inhalt += f"""
<section class="block"><div class="wrap">
  {sichtbarkeit()}
  <p class="hinweis">Der einzige klare Treffer ist <b>/schuelertanzkurse/</b> —
  bezeichnenderweise die einzige Seite im ganzen Auftritt, die wie eine richtige
  Kursseite aufgebaut ist, mit eigenem Thema, Preis und Ablauf. Sie ist damit der beste
  vorhandene Beleg dafür, dass das Muster funktioniert.</p>
</div></section>"""
    seite("nachfrage.html", "Nachfrage", "Sieben Suchbegriffe und wer sie besetzt.", inhalt)


def bau_position():
    boxen = ""
    for cls, titel, punkte in SWOT:
        li = "".join(f"<li><b>{E(t)}</b><span>{E(x)}</span></li>" for t, x in punkte)
        boxen += f'<section class="swot {cls}"><h2>{E(titel)}</h2><ul>{li}</ul></section>'
    inhalt = kopfzeile("Position", "Stärken, Schwächen, Chancen, Risiken",
        "Jeder Punkt stammt aus den erhobenen Daten, nicht aus Einschätzung.")
    inhalt += f'<section class="block"><div class="wrap"><div class="swotgrid">{boxen}</div></div></section>'
    seite("position.html", "Position", "SWOT auf Basis der erhobenen Marktdaten.", inhalt)


def bau_relaunch():
    rang = {"muss": ("a-muss", "Pflicht"), "soll": ("a-soll", "Wichtig"),
            "kann": ("a-kann", "Sinnvoll")}
    items = ""
    for i, (titel, stufe, text, fuss) in enumerate(ANFORDERUNGEN, 1):
        cls, lbl = rang[stufe]
        items += (f'<article class="anf"><div class="anr">{i:02d}</div><div>'
                  f'<div class="anh"><h3>{E(titel)}</h3>'
                  f'<span class="tag {cls}">{lbl}</span></div>'
                  f'<p>{text}</p><p class="anfuss">{E(fuss)}</p></div></article>')
    inhalt = kopfzeile("Ergebnis", "Neun Anforderungen an die neue Website",
        "Abgeleitet aus dem, was der Markt tatsächlich tut — nicht aus allgemeinen "
        "Empfehlungen. Die Reihenfolge folgt der Wirkung, die Kennzeichnung dem "
        "Verbindlichkeitsgrad.",
        [("6", "Pflicht"), ("2", "Wichtig"), ("1", "Sinnvoll")])
    inhalt += f"""
<section class="block"><div class="wrap">
  <div class="anfliste">{items}</div>
  <p class="hinweis stark"><b>Der wichtigste Satz dieser Analyse:</b> Punkt 3 entscheidet
  über alle anderen. Eine neue Website, die die 396 bestehenden Adressen nicht
  weiterleitet, startet bei null — egal wie gut sie gebaut ist. Der Weiterleitungsplan
  gehört deshalb vor die Gestaltung, nicht danach.</p>
</div></section>"""
    seite("relaunch.html", "Anforderungen",
          "Neun Anforderungen an die neue Website, aus dem Markt abgeleitet.", inhalt)


def bau_anbieter():
    karten = ""
    for a in sorted(ANBIETER, key=lambda x: (not x["wir"], -len(x["stile"]))):
        c1 = a["farben"][0]
        preis = f'{a["voll"]:.2f} €' if a["voll"] else "nicht veröffentlicht"
        karten += (
            f'<a class="akachel{" ist-wir" if a["wir"] else ""}" '
            f'href="{slug(a["dom"])}.html" style="--c1:{c1}">'
            f'<span class="astreif"></span>'
            f'<span class="aseg">{E(a["seg"])} · {E(a["ort"])}</span>'
            f'<h3>{E(a["name"])}</h3>'
            f'<span class="adom">{E(a["dom"])}</span>'
            f'<dl class="amini"><div><dt>Richtungen</dt><dd>{len(a["stile"])}</dd></div>'
            f'<div><dt>Vollzugang</dt><dd>{preis}</dd></div></dl></a>')
    inhalt = kopfzeile("Anbieter", "Alle 16 im Detail",
        "Je ein Profil mit Programm, Preisen, Technik und Markenfarben. Die Farbstreifen "
        "stammen aus dem Quelltext der jeweiligen Website — Bootstrap- und "
        "WordPress-Standardpaletten sind herausgefiltert, damit hier Marke steht und "
        "nicht Framework.")
    inhalt += f'<section class="block"><div class="wrap"><div class="akacheln">{karten}</div></div></section>'
    seite("anbieter/index.html", "Anbieter", "Alle 16 erhobenen Anbieter im Überblick.",
          inhalt, tiefe=1)

    for a in ANBIETER:
        bau_anbieter_seite(a)


def bau_anbieter_seite(a):
    c1 = a["farben"][0]
    c2 = a["farben"][1] if len(a["farben"]) > 1 else c1
    swat = "".join(f'<span class="sw" style="background:{c}">{c}</span>' for c in a["farben"])
    preise = "".join(
        f'<tr><td>{E(n)}</td><td class="n">{p:.2f} €</td><td>{E(d)}</td>'
        f'<td><span class="q q-{"w" if q == "Website" else "s"}">{E(q)}</span></td></tr>'
        for n, p, d, q in a["preise"]) or \
        '<tr><td colspan="4" class="leer">Kein Preis auf der Website veröffentlicht.</td></tr>'
    stile = "".join(
        f'<span class="st">{E(s)}<small>{VERBREITUNG[s]}/16</small></span>'
        for s in sorted(a["stile"], key=lambda s: VERBREITUNG[s]))
    if a["ttfb"] is not None:
        mess = ("<dl class='messwerte'>"
                f"<div><dt>Antwortzeit</dt><dd>{a['ttfb']:.2f} s</dd></div>"
                f"<div><dt>Seitengewicht</dt><dd>{a['kb']} kB</dd></div>"
                f"<div><dt>Seiten in der Sitemap</dt><dd>{a['seiten']}</dd></div>"
                f"<div><dt>Beschreibung</dt><dd>{a['desc']} Zeichen</dd></div>"
                f"<div><dt>H1-Überschriften</dt><dd>{a['h1']}×</dd></div>"
                f"<div><dt>H2-Ebene</dt><dd>{a['h2']}×</dd></div>"
                f"<div><dt>Schema-Blöcke</dt><dd>{a['ld']}</dd></div>"
                f"<div><dt>Open Graph</dt><dd>{a['og']}</dd></div>"
                f"<div><dt>WebP-Bilder</dt><dd>{a['webp']}</dd></div>"
                "</dl>")
    else:
        mess = ('<p class="hinweis">Die Website war während der gesamten Erhebung nicht '
                'erreichbar. Angaben auf dieser Seite stammen aus Suchergebnissen, die '
                'Markenfarben sind geschätzt.</p>')

    inhalt = f"""<section class="titel aprofil" style="--c1:{c1};--c2:{c2}">
  <div class="wrap">
    <p class="kicker">{E(a['seg'])} · {E(a['ort'])}{' · seit ' + str(a['gegruendet']) if a['gegruendet'] else ''}</p>
    <h1>{E(a['name'])}</h1>
    <p class="adomgross">{E(a['dom'])}</p>
    <div class="farbleiste">{swat}
      <span class="klein">Quelle: {E(a['farbquelle'])}</span></div>
  </div>
</section>
<section class="block"><div class="wrap">
  <div class="zweispalt">
    <div><h2>Stärke</h2><p>{E(a['staerke'])}</p></div>
    <div><h2>Schwäche</h2><p>{E(a['schwaeche'])}</p></div>
  </div>
  <h2 class="ueber">Tanzangebot <span class="klein">({len(a['stile'])} Richtungen)</span></h2>
  <p class="lead">Die Zahl hinter jeder Richtung sagt, wie viele der 16 Anbieter sie
  führen — je kleiner, desto seltener im Markt.</p>
  <div class="stilliste">{stile}</div>
  <h2 class="ueber">Preise</h2>
  <div class="scroll"><table><thead><tr><th>Tarif</th><th>Preis</th>
    <th>Bedingungen</th><th>Quelle</th></tr></thead><tbody>{preise}</tbody></table></div>
  <h2 class="ueber">Messwerte der Website</h2>
  {mess}
  <p class="zurueck"><a href="index.html">← Alle Anbieter</a></p>
</div></section>"""
    seite(f"anbieter/{slug(a['dom'])}.html", a["name"],
          f"Profil {a['name']}: Programm, Preise und Messwerte.", inhalt, tiefe=1)


def bau_methodik():
    inhalt = kopfzeile("Methodik", "Wie erhoben wurde — und wo die Grenzen liegen",
        "Damit jede Zahl in dieser Analyse nachvollziehbar bleibt.")
    inhalt += f"""
<section class="block"><div class="wrap"><div class="text">
  <h2>Erhebung</h2>
  <p>Alle technischen Werte stammen aus einem eigenen Live-Abruf am {STAND}: Quelltext,
  HTTP-Kopfzeilen, robots.txt und XML-Sitemaps von 16 Anbietern im Raum Hannover.
  Antwortzeiten sind Einzelmessungen (Time to First Byte) und schwanken tageszeitabhängig.</p>
  <p>Das Kursangebot wurde aus den Websites der Anbieter ausgelesen. Es bildet ab, was
  dort beworben wird — nicht zwingend jeden tatsächlich laufenden Kurs.</p>

  <h2>Was diese Analyse nicht ist</h2>
  <p><b>Die Nachfrageprüfung ist kein Positions-Tracking.</b> Geprüft wurde, welche
  Anbieter zu sieben Suchanfragen überhaupt mit einer Seite erscheinen — nicht, auf
  welchem Platz. Für echte Positionen, Suchvolumen und Klickzahlen ist Zugriff auf die
  Google Search Console des Kontos oder ein Sistrix-Abo nötig; beides lag nicht vor.</p>
  <p>Die Aussage „bei {UNBESETZT} von 7 Suchbegriffen nicht besetzt“ ist damit belastbar.
  Eine Aussage wie „Platz 14“ wäre es nicht.</p>

  <h2>Preise</h2>
  <p>Preise sind als <span class="q q-w">Website</span> gekennzeichnet, wenn sie auf der
  Anbieterseite gelesen wurden, und als <span class="q q-s">Snippet</span>, wenn sie nur
  aus einem Suchergebnis-Auszug stammen und nicht auf der Seite verifiziert werden
  konnten. Vor einer Preisdiskussion sollten die Snippet-Werte einzeln geprüft werden.</p>
  <p>Für den Vergleich wurde jeweils der Monatspreis des größten Zugangs herangezogen,
  den ein Anbieter verkauft. Wochenpreise wurden mit 52 ÷ 12 auf Monate umgerechnet.</p>

  <h2>Markenfarben</h2>
  <p>Gewonnen aus theme-color-Angaben, benannten CSS-Marken-Variablen und den Regeln für
  Kopf, Navigation und Schaltflächen. Ein erster Durchlauf zählte schlicht alle Hex-Werte
  und lieferte dadurch Bootstrap- und WordPress-Standardpaletten — also Framework statt
  Marke. Diese Werte sind ausgeschlossen.</p>

  <h2>Lücken</h2>
  <p>u-dance.de war während der gesamten Erhebung nicht erreichbar; die Angaben dort
  beruhen auf Suchergebnissen, die Farben sind geschätzt. Gründungsjahre stammen aus
  Selbstauskünften der Anbieter auf ihren Websites und sind teilweise gerundet.</p>
</div></div></section>"""
    seite("methodik.html", "Methodik", "Erhebungsmethode und Grenzen der Analyse.", inhalt)


def main():
    if ZIEL.exists():
        shutil.rmtree(ZIEL)
    (ZIEL / "assets").mkdir(parents=True)
    (ZIEL / "assets" / "stil.css").write_text(STIL, encoding="utf-8")

    # Die eingebetteten Schriften sind hübsch, aber nicht notwendig. Fehlen sie,
    # greift der Systemschrift-Rückfall aus stil.css — die Seiten bleiben lesbar.
    schrift = QUELLEN / "fonts.css"
    if schrift.exists():
        shutil.copy(schrift, ZIEL / "assets" / "fonts.css")
    else:
        (ZIEL / "assets" / "fonts.css").write_text(
            "/* quellen/fonts.css nicht gefunden — Systemschriften werden verwendet. */\n",
            encoding="utf-8")
        print("Hinweis: quellen/fonts.css fehlt, Seiten laufen mit Systemschriften.")

    bau_index(); bau_markt(); bau_angebot(); bau_preise()
    bau_nachfrage(); bau_position(); bau_relaunch(); bau_anbieter(); bau_methodik()

    seiten = sorted(ZIEL.rglob("*.html"))
    gesamt = sum(p.stat().st_size for p in ZIEL.rglob("*") if p.is_file())
    print(f"{len(seiten)} Seiten in {ZIEL.relative_to(HIER)}/ — insgesamt {gesamt/1024:.0f} kB")
    for p in seiten:
        print(f"  {p.relative_to(ZIEL)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
