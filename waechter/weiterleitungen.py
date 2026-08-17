#!/usr/bin/env python3
"""Erzeugt die Weiterleitungs- und Sperrregeln für Dubletten und Index-Müll.

Zwei Dinge lassen sich nicht durch einen besseren Titel lösen:

  Dubletten    Fünf Adressen für Schülertanzkurse konkurrieren in der Suche
               gegeneinander. Eine behalten, die übrigen mit 301 darauf zeigen
               lassen — dann bündelt sich die Kraft statt sich zu teilen.
  Index-Müll   Test- und Altseiten wie „XXX_Start2“ oder „Dongsineu“ gehören
               gar nicht in den Index. Status 410 sagt Google deutlicher als
               404, dass die Seite absichtlich weg ist.

    python3 weiterleitungen.py           # Übersicht
    python3 weiterleitungen.py --dateien # .htaccess und CSV schreiben

Wichtig: Nichts davon wird automatisch scharf geschaltet. Die Dateien sind
Vorlagen — eine Weiterleitung ist eine dauerhafte Entscheidung und gehört
vorher angesehen.
"""
import argparse, csv, json, pathlib, sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from regeln import MUELL

HIER = pathlib.Path(__file__).parent
KONFIG = json.loads((HIER / "konfig.json").read_text(encoding="utf-8"))
BASIS = KONFIG.get("basis", "https://www.tanzschule-bothe.de")

# Welche Adresse bleibt, und was auf sie zeigt. Die Auswahl folgt einer Regel:
# Es bleibt die Adresse mit dem klarsten Namen — nicht die mit dem meisten Inhalt.
# Inhalt lässt sich verschieben, eine gute Adresse nicht nachträglich erfinden.
ZUSAMMENLEGEN = [
    dict(ziel="/schuelertanzkurse/",
         quellen=["/schuelertanzkurse4/", "/schuelertanzkurse_a/",
                  "/schuelertanzkurse2027/"],
         grund="Vier Adressen für dasselbe Angebot in Hannover. Vor dem Umlegen "
               "prüfen, ob auf den Altseiten Inhalte stehen, die auf die "
               "Zielseite gehören.",
         achtung="/bwschuelertanzkurse/ NICHT hierher umlegen — die bewirbt "
                 "Burgwedel und bleibt eigenständig."),
    dict(ziel="/bwschuelertanzkurse/",
         quellen=["/bwschuelerkursealt/"],
         grund="Alte Burgwedeler Schülerkursseite. Gehört auf die aktuelle "
               "Burgwedel-Seite, nicht auf die Hannoveraner.",
         achtung=""),
    dict(ziel="/kindergartenprojekte/",
         quellen=["/kita/"],
         grund="Beide Seiten beschreiben das Tanzprojekt für Kindergärten.",
         achtung=""),
    dict(ziel="/summerdance-erwachsene/",
         quellen=["/summerdance/"],
         grund="/summerdance/ trägt noch die Termine von 2019. Wenn das "
               "Ferienprogramm weiterläuft, stattdessen aktualisieren.",
         achtung="Nur umlegen, wenn kein eigenes Kinder-Ferienprogramm mehr "
                 "beworben wird — sonst braucht es zwei gepflegte Seiten."),
]

# Wird nicht weitergeleitet, sondern abgeschaltet: Es gibt kein sinnvolles Ziel.
SPERREN = [
    "/test/", "/testseite/", "/xxx_start2/", "/slider/", "/voting/",
    "/_blog/", "/_style/", "/_links/", "/_menufinder/", "/dd/", "/gw/",
    "/coronahelden/", "/funday/",
]

# Braucht eine Entscheidung, keine Regel.
KLAEREN = [
    ("/schulprojekte/", "/schulkooperation/",
     "Beide zum Thema Schule, aber inhaltlich verschieden: /schulprojekte/ ist "
     "inzwischen ein reiner Downloadbereich. Entweder klar trennen und passend "
     "betiteln oder zusammenlegen."),
]


def htaccess() -> str:
    z = ["# Weiterleitungen Tanzschulen Familie Bothe",
         "# Erzeugt von waechter/weiterleitungen.py — vor dem Einspielen prüfen.",
         "",
         "<IfModule mod_rewrite.c>",
         "RewriteEngine On", ""]
    for g in ZUSAMMENLEGEN:
        z.append(f"  # {g['grund'].splitlines()[0]}")
        if g["achtung"]:
            z.append(f"  # ACHTUNG: {g['achtung']}")
        for q in g["quellen"]:
            muster = q.strip("/")
            z.append(f"  RewriteRule ^{muster}/?$ {g['ziel']} [R=301,L]")
        z.append("")
    z += ["</IfModule>", "",
          "# Endgültig entfernt — 410 sagt deutlicher als 404, dass das Absicht ist.",
          "<IfModule mod_rewrite.c>", "RewriteEngine On", ""]
    for s in SPERREN:
        z.append(f"  RewriteRule ^{s.strip('/')}/?$ - [G,L]")
    z += ["", "</IfModule>", ""]
    return "\n".join(z)


def robots_hinweis() -> str:
    return ("# Ergänzung für robots.txt\n"
            "# Hinweis: robots.txt verhindert das CRAWLEN, nicht das Indexieren.\n"
            "# Eine bereits indexierte Seite verschwindet dadurch NICHT — dafür\n"
            "# braucht es 410 oder noindex. Diese Zeilen sind nur die Ergänzung,\n"
            "# damit Crawl-Budget nicht weiter verschwendet wird.\n\n"
            "User-agent: *\n"
            + "".join(f"Disallow: {s}\n" for s in SPERREN)
            + "\n# Aktuell stehen in der robots.txt zwei getrennte 'User-agent: *'-Blöcke.\n"
              "# Beim Aufräumen zu einem zusammenfassen.\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dateien", action="store_true", help="Vorlagen schreiben")
    a = ap.parse_args()

    n_um = sum(len(g["quellen"]) for g in ZUSAMMENLEGEN)
    print(f"\nWEITERLEITUNGEN — {n_um} Umleitungen, {len(SPERREN)} Sperrungen, "
          f"{len(KLAEREN)} offene Entscheidung\n" + "=" * 72)

    print("\n■ ZUSAMMENLEGEN (301)")
    for g in ZUSAMMENLEGEN:
        print(f"\n  Ziel: {g['ziel']}")
        for q in g["quellen"]:
            print(f"    {q:<30} → {g['ziel']}")
        print(f"    Grund: {g['grund']}")
        if g["achtung"]:
            print(f"    ACHTUNG: {g['achtung']}")

    print(f"\n\n■ ABSCHALTEN (410) — {len(SPERREN)} Seiten")
    for s in SPERREN:
        print(f"    {s}")
    print("\n    Diese Seiten haben kein sinnvolles Ziel. 410 statt 301, weil eine\n"
          "    Weiterleitung auf die Startseite Google eher verwirrt als hilft.")

    print("\n\n■ ENTSCHEIDUNG NÖTIG")
    for a1, a2, hinweis in KLAEREN:
        print(f"    {a1} ↔ {a2}")
        print(f"      {hinweis}")

    print("\n\n■ VOR DEM EINSPIELEN")
    print("    1. Prüfen, ob auf den Altseiten Inhalte stehen, die auf die Zielseite gehören.")
    print("    2. Interne Links auf die alten Adressen suchen und auf das Ziel umbiegen —")
    print("       eine Weiterleitung ist kein Ersatz für einen richtigen Link.")
    print("    3. Nach dem Einspielen alle betroffenen Adressen einmal aufrufen.")
    print("    4. Sitemap neu erzeugen lassen, damit die alten Adressen verschwinden.")

    if a.dateien:
        (HIER / "weiterleitungen.htaccess").write_text(htaccess(), encoding="utf-8")
        (HIER / "robots-ergaenzung.txt").write_text(robots_hinweis(), encoding="utf-8")
        p = HIER / "weiterleitungen.csv"
        with p.open("w", newline="", encoding="utf-8-sig") as f:
            w = csv.writer(f, delimiter=";")
            w.writerow(["Quelle", "Ziel", "Typ", "Hinweis"])
            for g in ZUSAMMENLEGEN:
                for q in g["quellen"]:
                    w.writerow([q, g["ziel"], "301", g["grund"].replace("\n", " ")])
            for s in SPERREN:
                w.writerow([s, "", "410", "Test- oder Altseite, kein Ziel"])
        print(f"\n\nGeschrieben:")
        print(f"  weiterleitungen.htaccess   Apache-Regeln")
        print(f"  weiterleitungen.csv        Import für das Redirection-Plugin")
        print(f"  robots-ergaenzung.txt      Ergänzung samt Warnung zur Wirkung")
    return 0


if __name__ == "__main__":
    sys.exit(main())
