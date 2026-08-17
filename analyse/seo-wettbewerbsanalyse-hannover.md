# SEO- und Wettbewerbsanalyse Hannover

**Objekt:** tanzschule-bothe.de (Tanzschulen Familie Bothe)
**Erhebung:** 17.08.2026, eigener Live-Crawl
**Umfang:** 26 eigene Seiten, 6 Wettbewerber

Visueller Report: [`wertungsbogen-hannover.html`](./wertungsbogen-hannover.html)

---

## Kurzurteil

Die Tanzschule ist inhaltlich die breiteste in Hannover — drei Standorte, sieben Tage
die Woche, rund 220 Angebote. Technisch ist sie die schwächste im Testfeld: 1 von 10
Basiskriterien erfüllt. Der Wettbewerb gewinnt nicht mit besseren Kursen, sondern mit
besser gebauten Seiten.

| Kernbefund | Wert |
|---|---|
| Meta-Descriptions auf Unterseiten | **0 von 10** geprüften |
| Strukturierte Daten (JSON-LD) | **0** Blöcke, site-weit |
| Test-/Altseiten live + indexierbar + in Sitemap | **15 von 15** geprüften |

---

## 1. Befunde eigene Website

System: WordPress 6.8.8, Divi-Child-Theme, Events Calendar Pro 7.6.3, WP-Optimize.

| Signal | Befund | Soll | Bewertung |
|---|---|---|---|
| Meta-Description Startseite | 748 Zeichen | ≤ 165 | abgeschnitten |
| Meta-Description Unterseiten | 0 von 10 | 10 von 10 | kritisch |
| H1-Überschriften Startseite | 8× | 1× | kritisch |
| H2-Ebene Startseite | 0× | vorhanden | fehlt |
| JSON-LD strukturierte Daten | 0 | LocalBusiness, Event, Course | fehlt |
| Open-Graph-Tags | 0 | 4–6 | fehlt |
| Bilder ohne Alt-Text (Startseite) | 10 von 15 | 0 | kritisch |
| WebP-Bilder | 0 | durchgängig | veraltet |
| HTML-Gewicht Startseite | 327 kB | < 150 kB | schwer |
| Sichtbarer Text Startseite | 424 Wörter | > 600 | dünn |
| Inline-CSS im HTML | 223 kB | ausgelagert | blockiert Rendering |
| CSS- / JS-Dateien | 20 / 33 | < 10 / < 12 | aufgebläht |
| TTFB `/kids2bis11/` | 2,89 s | < 1,0 s | kritisch |
| TTFB `/hiphopundco/` | 3,08 s | < 1,0 s | kritisch |
| Preise auf der Website | nicht auffindbar | eigene Seite | Lücke |

**Zwei Zahlen erklären den Rest:** 327 kB HTML für 424 sichtbare Wörter. Über 99 % der
ausgelieferten Startseite ist Divi-Gerüst und Inline-CSS.

Die beiden langsamsten Seiten im gesamten Test sind die Kinder- und Teenager-Seiten —
also die Seiten, die Eltern mobil und nebenbei aufrufen. Die schnellsten Seiten sind
Impressum und Kontakt. Der Cache greift dort, wo es nicht zählt.

### Titel-Muster (alle 10 geprüften Seiten)

Alle Titel beginnen mit dem Markennamen und verschenken damit die wertvollste Position.
Keiner enthält „Hannover".

```
Tanzschule Familie Bothe - Paartanz Erwachsene
Tanzschule Familie Bothe - KIDS 2 bis 11
Tanzschule Familie Bothe - Tanzangebot Hip Hop & Co
Tanzschule Familie Bothe - DANCE & FITNESS
Tanzschule Familie Bothe - Privatstunden
```

### Index-Müll (alle HTTP 200, kein noindex, in der Sitemap)

```
/test/               Tanzschule Familie Bothe | Test
/testseite/          Tanzschule Familie Bothe | 222 Testseite
/xxx_start2/         Tanzschule Familie Bothe | XXX_Start2
/dd/                 Tanzschule Familie Bothe | Dongsineu
/slider/  /voting/  /gw/  /funday/  /summerdance/  /coronahelden/
/_blog/  /_style/  /_links/  /_menufinder/  /bwschuelerkursealt/
```

---

## 2. Wettbewerbsfeld, technisch vermessen

Alle Startseiten am selben Tag mit identischer Methode gecrawlt.

| Anbieter | Standort | System | Desc. | H1 | H2 | JSON-LD | OG | TTFB | kB |
|---|---|---|---|---|---|---|---|---|---|
| **tanzschule-bothe.de** | Hannover ×3 | WordPress/Divi | 748\* | 8 | 0 | 0 | 0 | 0,73 s | 327 |
| bothe.de *(namensgleich)* | Hannover | TYPO3 | 155 | 1 | 3 | 0 | 6 | 2,32 s | 93 |
| tanzschulemeiners.de | Hannover Mitte | WordPress | 289 | 1 | 2 | 1 | 6 | 1,86 s | 129 |
| move-dance.de | Hannover | WordPress | 95 | 3 | 3 | 0 | 0 | 0,99 s | 40 |
| tanzschule-graeper.de | Langenhagen | Baukasten | 166 | 0 | 5 | 2 | 5 | 0,31 s | 509 |
| jegella.de | Lehrte | WordPress | 89 | 6 | 13 | 0 | 0 | 1,02 s | 81 |
| happyhours.de | Hannover | Joomla | Preisführer-Positionierung | | | | | | |

\* Nur Startseite. Auf allen zehn geprüften Unterseiten: 0 Zeichen.

### Erfüllte Basiskriterien

Zehn objektiv prüfbare Kriterien: Description vorhanden und in Länge, Description auf
Unterseiten, genau eine H1, H2-Ebene, JSON-LD, Open Graph, TTFB < 1 s, HTML < 150 kB,
WebP, thematische URL-Struktur.

| Anbieter | Erfüllt |
|---|---|
| tanzschulemeiners.de | 7/10 |
| bothe.de | 7/10 |
| tanzschule-graeper.de | 6/10 |
| move-dance.de | 5/10 |
| jegella.de | 3/10 |
| **tanzschule-bothe.de** | **1/10** |

---

## 3. Warum bothe.de vor uns steht

Susanne Bothe hat an mehreren Stellen **schlechtere** Technik als wir — langsamer
(2,32 s TTFB), älteres CMS, ebenfalls kein JSON-LD. Und rankt trotzdem für die
Kurs-Suchbegriffe. Der Grund ist die Seitenarchitektur.

**bothe.de — thematisches Silo, 12 Kurs-Landingpages:**

```
/tanzkurse/
  /tanzkurse-fuer-erwachsene/
    /discofox/            /salsa/          /baelle-und-hochzeiten/
    /solo-tanz/           /tanzfit-60-plus/ /bestager60plus/
  /tanzkurse-fuer-jugendliche/
    /hip-hop-und-contemporary/  /gesellschaftszertifikat/  /ferienkurse/
  /tanzkurse-fuer-kinder/
    /windellini/  /dance4kids-ab-6-jahre/  /dance4kids-ab-8-jahre/
```

**tanzschule-bothe.de — flach, kryptisch, mit Leichen:**

```
/paartanz/          ← alle Paartänze auf einer einzigen Seite, 9× H1, 0 Description
/kids2bis11/  /hiphopundco/  /danceandfitness/  /tanzfit/
/bwpaartanz/  /bwkids/
/dd/  /gw/  /xxx_start2/  /testseite/  /_blog/  /_style/  /_links/
```

Wer in Hannover „Discofox Kurs" sucht, findet bei bothe.de eine Seite, die genau so
heißt: **„Discofox tanzen lernen in unserer Tanzschule in Hannover"** — eigene URL,
eigene 153-Zeichen-Beschreibung, saubere H1. Bei uns führt derselbe Suchbegriff
bestenfalls auf `/paartanz/`.

### Zwei weitere Marktfaktoren

**Markenkonflikt.** Es gibt zwei Bothes in Hannover, beide aus demselben
Gründungsstammbaum, beide mit „Bothe" in Domain und Name. Jede unspezifische
Markensuche wird zwischen beiden aufgeteilt — aktuell gewinnt die Seite mit der
besseren Struktur. Susanne Bothe baut zusätzlich bis 2027 das „Bothe Loft"
(1.600 m², Bischofsholer Damm 14) und dokumentiert den Bau seit September 2025
laufend auf einer eigenen Domain — eine Content-Maschine mit kontinuierlich
frischen Signalen.

**Preisdruck von unten.** happyhours.de positioniert sich offensiv als „Hannovers
günstigste Tanzkurs-Preise", der TTC Gelb-Weiss bietet Discofox-Anfängerkurse als
Verein deutlich unter Tanzschul-Niveau. Auf unserer Website steht zu Preisen nichts.

---

## 4. Maßnahmen, nach Wirkung pro Aufwand

| # | Maßnahme | Aufwand | Wirkung |
|---|---|---|---|
| 1 | **Titles und Descriptions für jede Kursseite.** Muster umdrehen: Suchbegriff + Hannover + Marke. SEO-Plugin (RankMath/Yoast) erzwingt Pflichtfelder. | gering | sehr hoch |
| 2 | **Eine Landingpage pro Tanzstil** statt Sammelseite: Discofox, Hochzeitstanz, Salsa, Standard & Latein, West Coast Swing, Kindertanz, Hip Hop, 60+ — je mit Terminen, Preis, Trainer, Standort, FAQ. | mittel | sehr hoch |
| 3 | **Index-Müll entfernen.** 15 Seiten auf noindex oder 410, raus aus der Sitemap. | gering | hoch |
| 4 | **Strukturierte Daten.** LocalBusiness ×3, Event für die 24 Kalendereinträge, Course je Kursseite, FAQPage. Kein Wettbewerber aus Hannover nutzt Event-Markup — freies Feld. | mittel | sehr hoch |
| 5 | **Ladezeit der Kursseiten.** Caching ausweiten, WebP, 223 kB Inline-CSS auslagern, 20 CSS/33 JS bündeln. | mittel | hoch |
| 6 | **Lokale Sichtbarkeit für 3 Standorte.** Je ein Google-Unternehmensprofil, je eine eigene Standortseite, einheitliche NAP-Schreibweise. | gering | hoch |
| 7 | **Preise sichtbar machen.** Antwort auf „Tanzkurs Hannover Preise" ist die Flatrate — Wert-Argument statt Preis-Argument. | gering | mittel |
| 8 | **Überschriften und Open Graph.** 1 H1 pro Seite, echte H2-Ebene, OG-Tags für Instagram/TikTok/Facebook/YouTube. | gering | mittel |

---

## 5. Zur Frage nach dem automatischen SEO-Wächter

Ja, solche Tools gibt es — in drei Kategorien:

**Monitoring (meldet, ändert nichts).** Sistrix, Ahrefs, Google Search Console,
Screaming Frog. Sagen, was kaputt ist. Reparieren nichts.

**Auto-Optimierer (ändern die Seite wirklich).** SearchPilot, Alli AI und ähnliche
schalten sich als Schicht vor die Website und schreiben Titel, Descriptions, Schema
und Links beim Ausliefern um — ohne WordPress anzufassen. SearchPilot testet dabei
A/B: Hälfte der Seiten Variante A, Hälfte B, danach steht messbar fest, was mehr
Klicks bringt. Kosten vierstellig pro Monat, lohnt ab einigen tausend Seiten —
tanzschule-bothe.de hat gut sechzig.

**CMS-seitig (Regeln, die Fehler verhindern).** RankMath oder Yoast Premium:
automatische Titel-Muster, Schema-Generierung, Redirect-Verwaltung,
404-Überwachung. Lassen eine Seite ohne Description gar nicht erst live gehen.
Für diese Größe der wirtschaftlich richtige Hebel — deckt Maßnahme 1, 4 und 8
weitgehend ab.

### Wichtige Einschränkung

Ein Wächter, der **eigenständig Inhalte umschreibt**, ist seit Googles Richtlinie
gegen „Scaled Content Abuse" (März 2024) ein echtes Risiko: automatisch in Masse
erzeugte oder umgeschriebene Texte können zu einer manuellen Abstrafung führen.

Die belastbare Trennlinie:

- **Automatisierbar:** Descriptions aus vorhandenem Seiteninhalt, Schema.org,
  Alt-Texte, Sitemaps, Redirects, Broken-Link-Prüfung, Ladezeit-Überwachung.
- **Menschliche Freigabe:** Inhalt, Positionierung, Preise.

### Vorschlag: eigener Wächter in diesem Repository

| Stufe | Funktion |
|---|---|
| **1 — Sensor** | Täglicher Crawl aller Seiten, Search-Console-API, Core Web Vitals. Snapshot als Commit in Git — jede Veränderung rückwirkend nachvollziehbar. |
| **2 — Diff & Alarm** | Vergleich zum Vortag gegen festen Regelsatz: Description fehlt, H1 ≠ 1, TTFB > 1 s, neue 404, Seite aus dem Index gefallen, neue Wettbewerberseite. Meldung per Mail/Slack. |
| **3 — Auto-Fix mit Freigabe** | Für technische Punkte erzeugt der Wächter den Fix und legt ihn als Pull Request vor. Mensch prüft und merged. Dauerhafte Optimierung ohne unkontrollierten Text auf der Website. |

### Hinweis zum Wix-Prototypen

Im Konto liegt bereits ein Wix-Studio-Prototyp mit aktiver **Promote SEO**-App, dessen
Navigation `Kurse & Angebote`, `Preise` und `Kursfinder` enthält — also genau die
Seiten, die auf der Live-Website fehlen. Falls ein Relaunch ohnehin ansteht, sollten
die Maßnahmen 1, 2, 7 und 8 dort direkt mitgebaut werden statt zweimal gemacht.

---

## Methodik und Grenzen

Alle Zahlen stammen aus einem eigenen Live-Crawl am 17.08.2026: HTTP-Header,
HTML-Quelltext, robots.txt und XML-Sitemaps von tanzschule-bothe.de sowie den
Startseiten und je einer Unterseite der Wettbewerber. Antwortzeiten sind
Einzelmessungen (TTFB, eine Messung pro URL) und schwanken tageszeitabhängig.

**Nicht enthalten:** echte Ranking-Positionen, Suchvolumen, Klickzahlen. Dafür ist
Zugriff auf die Google Search Console des Kontos oder ein Sistrix-/Ahrefs-Abo nötig —
beides lag nicht vor. Die Analyse bewertet, welche Signale Google ausgeliefert
bekommt, nicht, wie Google darauf reagiert.

Marktbeobachtungen zu Preispositionierung und Bauvorhaben stammen aus öffentlichen
Websites und Suchergebnissen.

Rohdaten der Erhebung: [`rohdaten/`](./rohdaten/)
