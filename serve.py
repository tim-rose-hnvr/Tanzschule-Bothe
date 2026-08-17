#!/usr/bin/env python3
"""Liefert die Marktanalyse lokal aus.

    python3 serve.py            # http://localhost:8000
    python3 serve.py 8080       # anderer Port

Rein lesend, nur auf der eigenen Maschine erreichbar (127.0.0.1). Wenn `site/`
noch nicht existiert, wird es vorher erzeugt.
"""
import http.server, functools, pathlib, socket, subprocess, sys, webbrowser

HIER = pathlib.Path(__file__).parent
SITE = HIER / "site"


class Handler(http.server.SimpleHTTPRequestHandler):
    extensions_map = {**http.server.SimpleHTTPRequestHandler.extensions_map,
                      ".css": "text/css; charset=utf-8",
                      ".html": "text/html; charset=utf-8"}

    def log_message(self, format, *args):
        # Nur Fehler melden — sonst rauscht jede Schrift und jedes Stylesheet durch.
        if not str(args[1] if len(args) > 1 else "").startswith("2"):
            sys.stderr.write("  %s %s\n" % (self.address_string(), format % args))

    def end_headers(self):
        # Beim Weiterentwickeln nerven zwischengespeicherte Fassungen.
        self.send_header("Cache-Control", "no-store")
        super().end_headers()


def frei(port):
    with socket.socket() as s:
        return s.connect_ex(("127.0.0.1", port)) != 0


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000

    if not (SITE / "index.html").exists():
        print("site/ fehlt — wird erzeugt …")
        subprocess.run([sys.executable, str(HIER / "site_bauen.py")], check=True)

    while not frei(port) and port < 8100:
        port += 1

    handler = functools.partial(Handler, directory=str(SITE))
    with http.server.ThreadingHTTPServer(("127.0.0.1", port), handler) as srv:
        url = f"http://localhost:{port}/"
        seiten = len(list(SITE.rglob("*.html")))
        print(f"\n  Marktanalyse Tanzschulen Hannover — {seiten} Seiten")
        print(f"  {url}\n")
        print("  Übersicht     /index.html")
        print("  Markt         /markt.html")
        print("  Angebot       /angebot.html")
        print("  Preise        /preise.html")
        print("  Nachfrage     /nachfrage.html")
        print("  Position      /position.html")
        print("  Anbieter      /anbieter/index.html")
        print("  Anforderungen /relaunch.html")
        print("  Methodik      /methodik.html")
        print("\n  Beenden mit Strg+C\n")
        try:
            webbrowser.open(url)
        except Exception:
            pass
        try:
            srv.serve_forever()
        except KeyboardInterrupt:
            print("\n  Beendet.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
