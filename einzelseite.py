#!/usr/bin/env python3
"""Packt die komplette Marktanalyse in eine einzige HTML-Datei.

Die Website unter `site/` ist zum Durchklicken. Diese Fassung ist zum
Weitergeben: ein Dokument, das man anhängen, doppelklicken oder ausdrucken
kann. Schriften und Stylesheet stecken darin — es lädt nichts nach und
funktioniert auch ohne Internet und ohne Server.

    python3 einzelseite.py
"""
import pathlib, sys

HIER = pathlib.Path(__file__).parent
sys.path.insert(0, str(HIER))
import site_bauen as S

FONTS = (HIER / "quellen" / "fonts.css").read_text(encoding="utf-8") \
    if (HIER / "quellen" / "fonts.css").exists() else ""

E = S.E
ZIEL = HIER / "Marktanalyse-Tanzschulen-Hannover.html"

GLIEDERUNG = [
    ("lage", "Ausgangslage"), ("markt", "Der Markt"), ("angebot", "Angebot"),
    ("preise", "Preise"), ("nachfrage", "Nachfrage"), ("position", "Position"),
    ("anbieter", "Anbieterprofile"), ("relaunch", "Anforderungen"),
    ("methodik", "Methodik"),
]


def profil(a):
    """Anbieterprofil, in der Einzelseite kompakter als auf der Website."""
    c1 = a["farben"][0]
    c2 = a["farben"][1] if len(a["farben"]) > 1 else c1
    swat = "".join(f'<span class="sw" style="background:{c}">{c}</span>' for c in a["farben"])
    preise = "".join(
        f'<tr><td>{E(n)}</td><td class="n">{p:.2f} €</td><td>{E(d)}</td>'
        f'<td><span class="q q-{"w" if q == "Website" else "s"}">{E(q)}</span></td></tr>'
        for n, p, d, q in a["preise"]) or \
        '<tr><td colspan="4" class="leer">Kein Preis auf der Website veröffentlicht.</td></tr>'
    stile = "".join(f'<span class="st">{E(s)}<small>{S.VERBREITUNG[s]}/16</small></span>'
                    for s in sorted(a["stile"], key=lambda s: S.VERBREITUNG[s]))
    if a["ttfb"] is not None:
        mess = ('<dl class="messwerte">'
                f'<div><dt>Antwortzeit</dt><dd>{a["ttfb"]:.2f} s</dd></div>'
                f'<div><dt>Gewicht</dt><dd>{a["kb"]} kB</dd></div>'
                f'<div><dt>Seiten</dt><dd>{a["seiten"]}</dd></div>'
                f'<div><dt>Beschreibung</dt><dd>{a["desc"]} Z.</dd></div>'
                f'<div><dt>H1</dt><dd>{a["h1"]}×</dd></div>'
                f'<div><dt>Schema</dt><dd>{a["ld"]}</dd></div>'
                f'<div><dt>Open Graph</dt><dd>{a["og"]}</dd></div>'
                f'<div><dt>WebP</dt><dd>{a["webp"]}</dd></div></dl>')
    else:
        mess = ('<p class="hinweis">Während der gesamten Erhebung nicht erreichbar. '
                'Angaben aus Suchergebnissen, Markenfarben geschätzt.</p>')
    return f"""
<article class="prof{' ist-wir' if a['wir'] else ''}" style="--c1:{c1};--c2:{c2}">
  <span class="pstreif"></span>
  <div class="pin">
    <p class="pseg">{E(a['seg'])} · {E(a['ort'])}{' · seit ' + str(a['gegruendet']) if a['gegruendet'] else ''}</p>
    <h3>{E(a['name'])}</h3>
    <p class="pdom">{E(a['dom'])}</p>
    <div class="farbleiste">{swat}<span class="klein">{E(a['farbquelle'])}</span></div>
    {mess}
    <div class="zweispalt">
      <div><h4>Stärke</h4><p>{E(a['staerke'])}</p></div>
      <div><h4>Schwäche</h4><p>{E(a['schwaeche'])}</p></div>
    </div>
    <h4>Tanzangebot <span class="klein">({len(a['stile'])} Richtungen)</span></h4>
    <div class="stilliste">{stile}</div>
    <h4>Preise</h4>
    <div class="scroll"><table><thead><tr><th>Tarif</th><th>Preis</th>
      <th>Bedingungen</th><th>Quelle</th></tr></thead><tbody>{preise}</tbody></table></div>
  </div>
</article>"""


def matrix_ohne_links():
    """Dieselbe Matrix, aber ohne Verweise auf einzelne Anbieterdateien.

    Auf der Website führt jeder Name zu seiner Profilseite. In der Einzeldatei
    gibt es diese Dateien nicht — dort steht alles im Abschnitt Anbieterprofile.
    """
    import re
    return re.sub(r'<a href="anbieter/[^"]+">(.*?)</a>', r"\1", S.matrix())


def swot():
    out = ""
    for cls, titel, punkte in S.SWOT:
        li = "".join(f"<li><b>{E(t)}</b><span>{E(x)}</span></li>" for t, x in punkte)
        out += f'<section class="swot {cls}"><h3>{E(titel)}</h3><ul>{li}</ul></section>'
    return f'<div class="swotgrid">{out}</div>'


def anforderungen():
    rang = {"muss": ("a-muss", "Pflicht"), "soll": ("a-soll", "Wichtig"),
            "kann": ("a-kann", "Sinnvoll")}
    out = ""
    for i, (titel, stufe, text, fuss) in enumerate(S.ANFORDERUNGEN, 1):
        cls, lbl = rang[stufe]
        out += (f'<article class="anf"><div class="anr">{i:02d}</div><div>'
                f'<div class="anh"><h3>{E(titel)}</h3>'
                f'<span class="tag {cls}">{lbl}</span></div>'
                f'<p>{text}</p><p class="anfuss">{E(fuss)}</p></div></article>')
    return f'<div class="anfliste">{out}</div>'


def portale():
    return '<div class="portale">' + "".join(
        f'<article class="portal"><h3>{E(n)}</h3><p class="klein">{E(t)}</p>'
        f'<p>{E(b)}</p></article>' for n, t, b in S.PORTALE) + "</div>"


ZUSATZ_CSS = """
/* Nur für die Einzelseite: Inhaltsverzeichnis, Abschnittstrenner, Druck. */
.deckblatt{padding:clamp(46px,6vw,84px) 0 clamp(30px,4vw,48px)}
.deckblatt h1{font-size:clamp(2rem,5vw,3.4rem);max-width:19ch;letter-spacing:-.014em}
.inhalt{background:var(--flaeche);border:1px solid var(--linie);padding:22px 26px;
  margin-top:34px;max-width:560px}
.inhalt h2{font-size:1.05rem;margin-bottom:12px}
.inhalt ol{list-style:none;counter-reset:iv;display:flex;flex-direction:column;gap:5px}
.inhalt li{counter-increment:iv}
.inhalt li::before{content:counter(iv,decimal-leading-zero) " ";
  font-family:var(--daten);font-size:.74rem;color:var(--gedaempft);margin-right:9px}
.inhalt a{text-decoration:none;border-bottom:1px solid var(--linie)}
.inhalt a:hover{border-color:var(--akzent)}
.abschnitt{padding:clamp(34px,4.4vw,60px) 0;border-top:1px solid var(--linie)}
.abschnitt>.wrap>h2{font-size:clamp(1.5rem,3.2vw,2.1rem);letter-spacing:-.01em}
.abschnitt .kicker{margin-bottom:10px}
.abschnitt>.wrap>.lead{margin:12px 0 24px}
.profile{display:flex;flex-direction:column;gap:16px;margin-top:8px}
.prof{background:var(--flaeche);border:1px solid var(--linie);display:grid;
  grid-template-columns:6px 1fr;overflow:hidden}
.prof.ist-wir{border-color:var(--akzent);border-width:2px}
.pstreif{background:linear-gradient(180deg,var(--c1) 0 55%,var(--c2) 55% 100%)}
.pin{padding:20px clamp(16px,2.4vw,26px)}
.pseg{font-family:var(--daten);font-size:.65rem;letter-spacing:.13em;
  text-transform:uppercase;color:var(--gedaempft)}
.prof h3{font-size:1.22rem;margin-top:4px}
.prof h4{font-family:var(--daten);font-weight:600;font-size:.68rem;letter-spacing:.13em;
  text-transform:uppercase;color:var(--gedaempft);margin:18px 0 7px}
.pdom{font-family:var(--daten);font-size:.8rem;color:var(--gedaempft);margin-top:2px}
.zurueck-oben{position:fixed;right:18px;bottom:18px;background:var(--akzent);color:#fff;
  text-decoration:none;font-family:var(--daten);font-size:.72rem;letter-spacing:.09em;
  text-transform:uppercase;padding:9px 14px;border-radius:2px;opacity:.9}
.zurueck-oben:hover{opacity:1}
@media print{
  .zurueck-oben{display:none}
  .abschnitt{break-before:page;padding-top:0}
  .prof,.swot,.anf,.kachel{break-inside:avoid}
  body{font-size:10.5pt}
  .scroll{overflow:visible}
  table{min-width:0}
}
"""


def main():
    kz = "".join(f"<div><dd>{E(w)}</dd><dt>{E(l)}</dt></div>" for w, l in [
        ("16", "Anbieter erhoben"), ("17", "Richtungen bei Bothe"),
        (str(S.MEDIAN), "Median im Markt"), ("31", "Preisangaben"),
        ("7", "Suchbegriffe geprüft")])
    iv = "".join(f'<li><a href="#{a}">{E(t)}</a></li>' for a, t in GLIEDERUNG)

    doc = f"""<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Marktanalyse Tanzschulen Hannover</title>
<meta name="description" content="Vollerhebung des Tanzschulmarkts Hannover: 16 Anbieter mit Preisen, Kursangebot und Nachfrage — mit den Anforderungen an die neue Website.">
<style>{FONTS}</style>
<style>{S.STIL}{ZUSATZ_CSS}</style>
</head>
<body>
<a class="skip" href="#lage">Zum Inhalt springen</a>

<section class="titel deckblatt" id="oben"><div class="wrap">
  <p class="kicker">Marktanalyse · Raum Hannover · Erhebung {S.STAND}</p>
  <h1>Das größte Angebot der Stadt. Und kaum jemand weiß&nbsp;es.</h1>
  <p class="lead">Eine Vollerhebung des Tanzschulmarkts Hannover: 16 Anbieter, ihre
  Preise, ihr Kursprogramm, ihre Websites. Und die Frage, was die neue Website der
  Tanzschulen Familie Bothe leisten muss, damit aus dem größten Angebot auch die
  stärkste Position wird.</p>
  <dl class="kennzahlen">{kz}</dl>
  <nav class="inhalt"><h2>Inhalt</h2><ol>{iv}</ol></nav>
</div></section>

<section class="abschnitt" id="lage"><div class="wrap">
  <p class="kicker">01 · Ausgangslage</p>
  <h2>Marktführer im Angebot. Mitläufer in der Wahrnehmung.</h2>
  <div class="befund" style="margin-top:20px">
    <p>Die Tanzschulen Familie Bothe führen 17 Tanzrichtungen — mehr als doppelt so
    viele wie der Median im Feld ({S.MEDIAN}). Drei Häuser mit elf Sälen hat sonst
    niemand, und mit Gründung 1954 ist es die älteste Schule im Test. Nichts davon
    erreicht potenzielle Kundinnen und Kunden dort, wo sie suchen: Bei
    {S.UNBESETZT} von 7 geprüften Suchbegriffen ist Bothe nicht oder falsch vertreten.</p>
    <p>Das ist keine Frage des Marketings, sondern der Struktur. Wer 17 Tanzrichtungen
    anbietet, aber keine einzige Seite hat, die nach einer davon benannt ist, wird
    dafür nicht gefunden. Deshalb endet diese Analyse nicht mit einer Mängelliste,
    sondern mit neun Anforderungen an die neue Website.</p>
  </div>
</div></section>

<section class="abschnitt" id="markt"><div class="wrap">
  <p class="kicker">02 · Der Markt</p>
  <h2>Der Wettbewerb sind nicht nur Tanzschulen</h2>
  <p class="lead">Fünf Anbietertypen kämpfen um dieselben Kundinnen und Kunden — und
  dazu sechs Portale, die selbst keinen einzigen Kurs anbieten.</p>
  {portale()}
</div></section>

<section class="abschnitt" id="angebot"><div class="wrap">
  <p class="kicker">03 · Angebot</p>
  <h2>Wo Bothe allein steht</h2>
  <p class="lead">Vierzehn verbreitete Tanzrichtungen, sechzehn Anbieter. Bothe ist
  der einzige, der alle vierzehn führt — und der einzige mit Swing im Programm.</p>
  {matrix_ohne_links()}
  <p class="hinweis">Das ist das stärkste Verkaufsargument im gesamten Markt:
  <b>Wer einmal anfängt, kann bei Bothe alles lernen, ohne die Schule zu wechseln.</b></p>
  <h3 style="margin-top:34px">Verbreitung jeder Tanzrichtung</h3>
  <p class="lead">Je seltener eine Richtung im Markt ist, desto weniger Wettbewerb —
  und desto eher lohnt eine eigene Seite dafür.</p>
  {S.verbreitung()}
</div></section>

<section class="abschnitt" id="preise"><div class="wrap">
  <p class="kicker">04 · Preise</p>
  <h2>Bothe ist nicht teuer</h2>
  <p class="lead">Monatspreis für den größten Zugang, den ein Anbieter verkauft.
  Wochenpreise mit 52 ÷ 12 umgerechnet. Sieben der 16 Anbieter veröffentlichen
  überhaupt einen Preis — Bothe gehört nicht dazu.</p>
  {S.preistabelle()}
  <p class="hinweis">Mit 61 € liegt Bothe auf <b>Platz 4 von 7</b> — günstiger als
  Move &amp; Style Unlimited, Salsa del Alma und Meiners. Dazu die Vertragsform:
  Move &amp; Style bindet <b>52 Wochen</b>, Happy Hours verlangt bis zu 90 Tage
  Kündigungsfrist. Mittelfeld beim Preis, vorn beim Angebot, flexibel beim Vertrag —
  <b>nur steht das nirgends.</b></p>
  <h3 style="margin-top:34px">Alle erhobenen Tarife</h3>
  <p class="lead"><span class="q q-w">Website</span> heißt auf der Anbieterseite
  gelesen, <span class="q q-s">Snippet</span> nur aus einem Suchergebnis-Auszug —
  diese Werte vor einer Preisdiskussion einzeln prüfen.</p>
  {S.alle_preise()}
</div></section>

<section class="abschnitt" id="nachfrage"><div class="wrap">
  <p class="kicker">05 · Nachfrage</p>
  <h2>Wonach gesucht wird — und wer dort steht</h2>
  <p class="lead">Geprüft wurde, welche Anbieter zu diesen sieben Suchanfragen
  überhaupt mit einer eigenen Seite erscheinen. Eine Anwesenheitsprüfung, kein
  Positions-Tracking — aber wer gar nicht auftaucht, steht auf keinem Platz.</p>
  {S.sichtbarkeit()}
</div></section>

<section class="abschnitt" id="position"><div class="wrap">
  <p class="kicker">06 · Position</p>
  <h2>Stärken, Schwächen, Chancen, Risiken</h2>
  <p class="lead">Jeder Punkt stammt aus den erhobenen Daten, nicht aus Einschätzung.</p>
  {swot()}
</div></section>

<section class="abschnitt" id="anbieter"><div class="wrap">
  <p class="kicker">07 · Anbieterprofile</p>
  <h2>Alle 16 im Detail</h2>
  <p class="lead">Die Farbstreifen stammen aus dem Quelltext der jeweiligen Website —
  aus theme-color-Angaben, benannten Marken-Variablen und den Regeln für Kopf,
  Navigation und Schaltflächen. Bootstrap- und WordPress-Standardpaletten sind
  herausgefiltert, damit hier Marke steht und nicht Framework.</p>
  <div class="profile">
{"".join(profil(a) for a in sorted(S.ANBIETER, key=lambda x: (not x["wir"], -len(x["stile"]))))}
  </div>
</div></section>

<section class="abschnitt" id="relaunch"><div class="wrap">
  <p class="kicker">08 · Anforderungen</p>
  <h2>Neun Anforderungen an die neue Website</h2>
  <p class="lead">Abgeleitet aus dem, was der Markt tatsächlich tut. Die Reihenfolge
  folgt der Wirkung, die Kennzeichnung dem Verbindlichkeitsgrad.</p>
  {anforderungen()}
  <p class="hinweis stark"><b>Der wichtigste Satz dieser Analyse:</b> Punkt 3
  entscheidet über alle anderen. Eine neue Website, die die 396 bestehenden Adressen
  nicht weiterleitet, startet bei null — egal wie gut sie gebaut ist. Der
  Weiterleitungsplan gehört vor die Gestaltung, nicht danach.</p>
</div></section>

<section class="abschnitt" id="methodik"><div class="wrap">
  <p class="kicker">09 · Methodik</p>
  <h2>Wie erhoben wurde — und wo die Grenzen liegen</h2>
  <div class="text" style="margin-top:18px">
    <h3>Erhebung</h3>
    <p>Alle technischen Werte stammen aus einem eigenen Live-Abruf am {S.STAND}:
    Quelltext, HTTP-Kopfzeilen, robots.txt und XML-Sitemaps von 16 Anbietern im Raum
    Hannover. Antwortzeiten sind Einzelmessungen und schwanken tageszeitabhängig. Das
    Kursangebot wurde aus den Websites ausgelesen und bildet ab, was dort beworben
    wird — nicht zwingend jeden tatsächlich laufenden Kurs.</p>
    <h3>Was diese Analyse nicht ist</h3>
    <p><b>Die Nachfrageprüfung ist kein Positions-Tracking.</b> Geprüft wurde, welche
    Anbieter zu sieben Suchanfragen überhaupt mit einer Seite erscheinen — nicht, auf
    welchem Platz. Für echte Positionen, Suchvolumen und Klickzahlen ist Zugriff auf
    die Google Search Console des Kontos oder ein Sistrix-Abo nötig; beides lag nicht
    vor. Die Aussage „bei {S.UNBESETZT} von 7 Suchbegriffen nicht besetzt“ ist damit
    belastbar, eine Aussage wie „Platz 14“ wäre es nicht.</p>
    <h3>Preise</h3>
    <p>Als <span class="q q-w">Website</span> gekennzeichnete Preise wurden auf der
    Anbieterseite gelesen, als <span class="q q-s">Snippet</span> gekennzeichnete
    stammen nur aus einem Suchergebnis-Auszug und konnten nicht auf der Seite
    verifiziert werden. Vor einer Preisdiskussion einzeln prüfen.</p>
    <h3>Markenfarben</h3>
    <p>Gewonnen aus theme-color-Angaben, benannten CSS-Marken-Variablen und
    Komponentenregeln. Ein erster Durchlauf zählte schlicht alle Hex-Werte und
    lieferte dadurch Bootstrap- und WordPress-Standardpaletten — also Framework statt
    Marke. Diese Werte sind ausgeschlossen.</p>
    <h3>Lücken</h3>
    <p>u-dance.de war während der gesamten Erhebung nicht erreichbar; die Angaben dort
    beruhen auf Suchergebnissen, die Farben sind geschätzt. Gründungsjahre stammen aus
    Selbstauskünften der Anbieter und sind teilweise gerundet.</p>
  </div>
</div></section>

<footer class="fuss"><div class="wrap">
  <p><b>Marktanalyse Tanzschulen Familie Bothe</b> · Erhebung {S.STAND} ·
  16 Anbieter im Raum Hannover</p>
  {S.impressum()}
</div></footer>
<a class="zurueck-oben" href="#oben">↑ Inhalt</a>
</body>
</html>
"""
    ZIEL.write_text(doc, encoding="utf-8")
    print(f"{ZIEL.name} — {len(doc)/1024:.0f} kB, eine Datei, nichts wird nachgeladen")
    return 0


if __name__ == "__main__":
    sys.exit(main())
