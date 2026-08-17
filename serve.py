#!/usr/bin/env python3
"""Liefert die Marktanalyse aus — lokal oder im eigenen Netzwerk.

    python3 serve.py              # nur diese Maschine, http://localhost:8000
    python3 serve.py --netz       # auch für Geräte im selben WLAN/LAN
    python3 serve.py --netz 8080  # eigener Port

Ohne --netz lauscht der Server auf 127.0.0.1 und ist von außen unerreichbar.
Mit --netz lauscht er auf allen Schnittstellen: Jedes Gerät im selben Netz kann
die Analyse dann über die angezeigte Adresse aufrufen — praktisch, um sie auf
dem Handy zu zeigen oder im Termin auf einen fremden Laptop zu holen.

Der Server ist rein lesend und liefert ausschließlich Dateien aus `site/`.
"""
import argparse, functools, http.server, pathlib, socket, subprocess, sys, webbrowser

HIER = pathlib.Path(__file__).parent
SITE = HIER / "site"


class Handler(http.server.SimpleHTTPRequestHandler):
    extensions_map = {**http.server.SimpleHTTPRequestHandler.extensions_map,
                      ".css": "text/css; charset=utf-8",
                      ".html": "text/html; charset=utf-8"}

    def log_message(self, format, *args):
        # Nur Fehler melden — sonst rauscht jede Schrift und jedes Stylesheet durch.
        status = str(args[1]) if len(args) > 1 else ""
        if not status.startswith("2"):
            sys.stderr.write("  %s %s\n" % (self.address_string(), format % args))

    def end_headers(self):
        # Beim Weiterentwickeln nerven zwischengespeicherte Fassungen.
        self.send_header("Cache-Control", "no-store")
        super().end_headers()


def lan_adresse():
    """Die eigene Adresse im lokalen Netz.

    Der Umweg über einen UDP-Socket ist der zuverlässigste Weg: Er verrät, welche
    Schnittstelle das Betriebssystem nach außen benutzen würde. Gesendet wird
    dabei nichts — UDP baut keine Verbindung auf.
    """
    def brauchbar(ip):
        # Loopback und Link-Local bringen anderen Geräten nichts.
        return bool(ip) and not ip.startswith(("127.", "169.254.", "0."))

    for ziel in ("192.0.2.1", "8.8.8.8"):   # erst reservierter Testbereich, dann Notnagel
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.settimeout(0.4)
                s.connect((ziel, 9))
                ip = s.getsockname()[0]
            if brauchbar(ip):
                return ip
        except OSError:
            continue
    try:
        ip = socket.gethostbyname(socket.gethostname())
        return ip if brauchbar(ip) else None
    except OSError:
        return None


def frei(host, port):
    with socket.socket() as s:
        return s.connect_ex(("127.0.0.1", port)) != 0


def main():
    ap = argparse.ArgumentParser(add_help=True, description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("port", nargs="?", type=int, default=8000, help="Port (Standard 8000)")
    ap.add_argument("--netz", "--lan", action="store_true", dest="netz",
                    help="auch für andere Geräte im selben Netzwerk erreichbar machen")
    a = ap.parse_args()

    if not (SITE / "index.html").exists():
        print("site/ fehlt — wird erzeugt …")
        subprocess.run([sys.executable, str(HIER / "site_bauen.py")], check=True)

    host = "0.0.0.0" if a.netz else "127.0.0.1"
    port = a.port
    while not frei(host, port) and port < a.port + 100:
        port += 1

    handler = functools.partial(Handler, directory=str(SITE))
    try:
        srv = http.server.ThreadingHTTPServer((host, port), handler)
    except OSError as e:
        sys.exit(f"Server konnte nicht starten: {e}\n"
                 f"Anderen Port versuchen, z. B.: python3 serve.py {port + 1}")

    seiten = len(list(SITE.rglob("*.html")))
    print(f"\n  Marktanalyse Tanzschulen Hannover — {seiten} Seiten")
    print(f"  Auf diesem Rechner:  http://localhost:{port}/")

    if a.netz:
        ip = lan_adresse()
        if ip:
            print(f"  Im Netzwerk:         http://{ip}:{port}/")
            print(f"\n  Andere Geräte im selben WLAN erreichen die Analyse unter der")
            print(f"  zweiten Adresse. Beim ersten Start fragt die Firewall von macOS")
            print(f"  oder Windows nach — die Verbindung muss erlaubt werden.")
        else:
            print("  Im Netzwerk:         Adresse nicht ermittelbar.")
            print("                       IP mit `ipconfig` (Windows) bzw. `ip addr`"
                  " oder `ifconfig` (macOS/Linux) nachsehen.")
        print(f"\n  Hinweis: Der Server ist jetzt für alle im selben Netz sichtbar.")
        print(f"  Er liefert nur die Dateien aus site/ aus und nimmt nichts entgegen —")
        print(f"  trotzdem nach dem Termin mit Strg+C beenden.")
    else:
        print(f"  Nur auf diesem Rechner erreichbar."
              f" Für andere Geräte: python3 serve.py --netz")

    print("\n  Übersicht /  Markt /  Angebot /  Preise /  Nachfrage /"
          "  Position /  Anbieter /  Anforderungen /  Methodik")
    print("\n  Beenden mit Strg+C\n")

    try:
        webbrowser.open(f"http://localhost:{port}/")
    except Exception:
        pass
    with srv:
        try:
            srv.serve_forever()
        except KeyboardInterrupt:
            print("\n  Beendet.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
