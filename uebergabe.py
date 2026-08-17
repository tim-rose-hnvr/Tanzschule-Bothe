#!/usr/bin/env python3
"""Packt die Marktanalyse als eigenständiges Paket zur Weitergabe.

Ergebnis ist ein Ordner `uebergabe/` mit der fertigen Website, einem
Startskript und einer kurzen Anleitung — ohne Repository, ohne Versionsverlauf,
ohne Generatoren. Genau das, was man einem Kunden schickt oder auf einen
Webspace legt.

    python3 uebergabe.py           # Ordner erzeugen
    python3 uebergabe.py --zip     # zusätzlich als ZIP-Archiv

Die Dateien in `site/` sind statisches HTML mit eingebetteten Schriften. Sie
laufen auf jedem Webspace, brauchen kein PHP, keine Datenbank und keine
Internetverbindung.
"""
import argparse, pathlib, shutil, sys, zipfile

HIER = pathlib.Path(__file__).parent
SITE = HIER / "site"
ZIEL = HIER / "uebergabe"

ANLEITUNG = """# Marktanalyse Tanzschulen Hannover

Statische Website, 25 Seiten. Kein Server nötig, keine Datenbank, keine
Internetverbindung.

## Ansehen

**Am einfachsten:** `start.cmd` (Windows) oder `./start.sh` (macOS, Linux)
doppelklicken beziehungsweise im Terminal ausführen. Der Browser öffnet sich
mit der Übersicht.

**Für andere Geräte im selben WLAN** — etwa um die Analyse auf dem Tablet zu
zeigen:

```
./start.sh --netz
```

Die Ausgabe nennt dann eine zweite Adresse (`http://192.168.x.x:8000/`), die
jedes Gerät im selben Netz aufrufen kann. Beim ersten Start fragt die Firewall
nach; die Verbindung muss erlaubt werden.

## Auf einen Webspace legen

Den Inhalt des Ordners `site/` hochladen — fertig. Es gibt nichts zu
konfigurieren. Soll die Analyse nicht öffentlich sein, gehört ein
Verzeichnisschutz davor; die Seiten selbst bringen keinen mit.

## Inhalt

| Seite | Was drin steht |
|---|---|
| Übersicht | Einstieg und Kernbefund |
| Markt | 16 Anbieter in fünf Segmenten, dazu sechs Portale |
| Angebot | Kursmatrix über 14 Richtungen, Verbreitung je Richtung |
| Preise | Preisvergleich und alle 31 erhobenen Tarife |
| Nachfrage | Sieben Suchbegriffe und wer sie besetzt |
| Position | Stärken, Schwächen, Chancen, Risiken |
| Anbieter | Je ein Detailprofil für alle 16 Anbieter |
| Anforderungen | Neun Anforderungen an die neue Website |
| Methodik | Erhebungsmethode und Grenzen |

Die Methodikseite gehört dazu: Dort steht, wie erhoben wurde und was die
Analyse ausdrücklich **nicht** belegt. Bitte nicht weglassen.
"""

START_SH = """#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
for p in python3 python py; do
  if command -v "$p" >/dev/null 2>&1; then exec "$p" serve.py "$@"; fi
done
echo "Python wurde nicht gefunden: https://www.python.org/downloads/" >&2
exit 1
"""

START_CMD = """@echo off
cd /d "%~dp0"
where py >nul 2>nul && (py serve.py %* & goto :eof)
where python >nul 2>nul && (python serve.py %* & goto :eof)
echo Python wurde nicht gefunden: https://www.python.org/downloads/
pause
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--zip", action="store_true", help="zusätzlich ZIP-Archiv erzeugen")
    a = ap.parse_args()

    if not (SITE / "index.html").exists():
        sys.exit("site/ fehlt — erst `python3 site_bauen.py` ausführen.")

    if ZIEL.exists():
        shutil.rmtree(ZIEL)
    ZIEL.mkdir()

    shutil.copytree(SITE, ZIEL / "site")
    # Die Bauanleitung gehört nicht in die Übergabe.
    (ZIEL / "site" / "README.md").unlink(missing_ok=True)

    shutil.copy(HIER / "serve.py", ZIEL / "serve.py")
    (ZIEL / "LIESMICH.md").write_text(ANLEITUNG, encoding="utf-8")
    sh = ZIEL / "start.sh"
    sh.write_text(START_SH, encoding="utf-8")
    sh.chmod(0o755)
    (ZIEL / "start.cmd").write_text(START_CMD, encoding="utf-8")

    dateien = sorted(p for p in ZIEL.rglob("*") if p.is_file())
    groesse = sum(p.stat().st_size for p in dateien)
    print(f"uebergabe/ — {len(dateien)} Dateien, {groesse/1024/1024:.1f} MB")
    print("  site/           die 25 Seiten")
    print("  serve.py        lokaler Server")
    print("  start.sh        Start für macOS und Linux")
    print("  start.cmd       Start für Windows")
    print("  LIESMICH.md     Kurzanleitung")

    if a.zip:
        archiv = HIER / "marktanalyse-hannover.zip"
        with zipfile.ZipFile(archiv, "w", zipfile.ZIP_DEFLATED) as z:
            for p in dateien:
                z.write(p, p.relative_to(ZIEL))
        print(f"\n{archiv.name} — {archiv.stat().st_size/1024/1024:.1f} MB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
