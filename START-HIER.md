# Marktanalyse lokal öffnen

## Schnellster Weg

**Windows** — Doppelklick auf `start.cmd`
**macOS / Linux** — im Terminal:

```
./start.sh
```

Der Browser öffnet sich mit <http://localhost:8000>. Beenden mit `Strg+C`.

Wer lieber selbst tippt:

```
python3 serve.py        # oder: python serve.py  /  py serve.py
```

## Im eigenen Netzwerk zeigen

Damit Handy, Tablet oder ein fremder Laptop im selben WLAN die Analyse
aufrufen können:

```
./start.sh --netz          # macOS / Linux
start.cmd --netz           # Windows
python3 serve.py --netz    # direkt
```

Die Ausgabe nennt dann zwei Adressen — die zweite (`http://192.168.x.x:8000/`)
ist die für die anderen Geräte. Beim ersten Start fragt die Firewall von macOS
oder Windows nach; die Verbindung muss erlaubt werden, sonst bleibt der Server
für andere unsichtbar.

Zu beachten:

- Alle Geräte müssen im **selben** Netz sein. Gäste-WLAN ist meist getrennt und
  funktioniert nicht.
- Der Server ist während der Laufzeit für jeden im Netz sichtbar. Er liefert nur
  die Dateien aus `site/` aus und nimmt nichts entgegen — nach dem Termin
  trotzdem mit `Strg+C` beenden.
- Wird keine Adresse angezeigt, die eigene IP nachsehen: `ipconfig` unter
  Windows, `ip addr` oder `ifconfig` unter macOS und Linux.

## Wenn nichts passiert

**„python3: command not found" / „Python wurde nicht gefunden"**
Python 3 fehlt. Auf Windows heißt der Befehl meist `py`, auf manchen Systemen
`python`. Die Startskripte probieren alle drei durch. Falls keiner greift:
[python.org/downloads](https://www.python.org/downloads/).

**„Address already in use" oder die Seite bleibt leer**
Port 8000 ist belegt. `serve.py` sucht sich automatisch den nächsten freien Port
bis 8100 — schau in die Ausgabe, dort steht die tatsächliche Adresse. Oder gib
einen Port vor: `python3 serve.py 8080`.

**Der Browser öffnet sich nicht von allein**
Kein Problem, die Adresse steht in der Ausgabe. Einfach von Hand aufrufen.

**Seiten sehen unformatiert aus**
Dann wurde `site/index.html` per Doppelklick über `file://` geöffnet statt über
den Server. Bitte den Server benutzen — nur so werden Stylesheet und Schriften
geladen.

**Es kommt eine Dateiliste statt der Analyse**
Dann läuft der Server im falschen Ordner. `serve.py` muss aus dem
Repository-Hauptverzeichnis gestartet werden, nicht aus `site/`.

Wenn etwas anderes passiert: die vollständige Fehlermeldung aus dem Terminal
kopieren — daraus lässt sich die Ursache meist direkt ablesen.

## Was zu sehen ist

25 Seiten: Übersicht, Markt, Angebot, Preise, Nachfrage, Position,
Anforderungen, Methodik und je ein Detailprofil für alle 16 Anbieter.
Aufbau und Gestaltung erklärt `site/README.md`.

## Ohne Python

Jeder statische Server tut es, etwa `npx serve site`. Die Dateien in `site/`
sind fertig gebaut und liegen im Repository — es muss nichts erzeugt werden.
