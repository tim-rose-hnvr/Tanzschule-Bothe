# Marktanalyse als lokale Website

25 Seiten zum Durchklicken. Diese Dateien werden von `site_bauen.py` erzeugt —
Änderungen hier gehen beim nächsten Lauf verloren. Inhalte stehen in
`analyse/markt_daten.py`.

## Starten

```
python3 serve.py          # http://localhost:8000
python3 serve.py 8080     # anderer Port
```

Der Server ist rein lesend und nur auf der eigenen Maschine erreichbar
(127.0.0.1). Ist `site/` noch nicht vorhanden, wird es automatisch erzeugt.

Ohne Python geht auch jeder andere statische Server, etwa
`npx serve site` — oder `site/index.html` direkt im Browser öffnen. Beim
direkten Öffnen über `file://` funktionieren die Links, die Schriften werden
je nach Browser aber nicht geladen; der Server ist der zuverlässigere Weg.

## Aufbau

| Seite | Inhalt |
|---|---|
| `index.html` | Übersicht und Einstieg |
| `markt.html` | 16 Anbieter in fünf Segmenten, dazu sechs Portale |
| `angebot.html` | Kursmatrix über 14 Richtungen, Verbreitung je Richtung |
| `preise.html` | Preisvergleich und alle 31 erhobenen Tarife |
| `nachfrage.html` | Sieben Suchbegriffe und wer sie besetzt |
| `position.html` | Stärken, Schwächen, Chancen, Risiken |
| `anbieter/` | Je ein Detailprofil für alle 16 Anbieter |
| `relaunch.html` | Neun Anforderungen an die neue Website |
| `methodik.html` | Erhebungsmethode und Grenzen |

## Gestaltung

Bewusst neutral gehalten, nicht im Bothe-CI. Eine Analyse, die auch den
Wettbewerb bewertet, soll nicht aussehen, als käme sie von einer der bewerteten
Parteien. Die Kundendokumente unter `analyse/` laufen weiterhin im Bothe-Design.

Die farbigen Streifen auf den Anbieterprofilen sind keine Gestaltung, sondern
Daten: die aus dem Quelltext der jeweiligen Website gewonnenen Markenfarben.
