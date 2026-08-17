#!/usr/bin/env python3
"""Erzeugt die Stil-Landingpages aus einem gemeinsamen CI-Gerüst.

Das CSS stammt 1:1 aus der Discofox-Demo, die es wiederum aus
assets/style.css der Headless-Site übernommen hat. Pro Seite ändert sich
nur der Inhalt — Struktur, Farben und Schriften bleiben identisch.
"""
import re, json, html, pathlib

WURZEL = pathlib.Path(__file__).resolve().parent.parent
SP = WURZEL / "quellen"

# --- gemeinsames Gerüst aus der Discofox-Demo ziehen -----------------------
demo = (SP / "vorlage-kursseite.html").read_text(encoding="utf-8")
SHARED_CSS = re.findall(r"<style>\n(:root\{.*?)</style>", demo, re.S)[0]
FONTS = (SP / "fonts-marke.css").read_text(encoding="utf-8")

STANDORTE = [
    ("Tanzhaus Hannover", "Podbielskistraße 299B", "30655 Hannover"),
    ("Tanzvilla Waldersee", "Walderseestraße 20", "30177 Hannover"),
    ("Tanzhaus Burgwedel", "Kokenhorststraße 15", "30938 Burgwedel"),
]

SEITEN = [
    dict(
        slug="hochzeitstanz-hannover",
        titel="Hochzeitstanz Hannover",
        desc="Hochzeitstanz in Hannover — Crashkurs am Wochenende oder Privatstunden. Euer Eröffnungstanz sitzt, auch wenn ihr noch nie getanzt habt.",
        brotkrume=["Start", "Kurse", "Paartanz", "Hochzeitstanz"],
        h1='Euer erster Tanz.<br>Und alle <em>schauen zu</em>.',
        lead="Der Eröffnungstanz ist der Moment, an den sich alle erinnern. Wir bringen euch dahin — in einem Wochenende oder in Ruhe über mehrere Wochen. Auch wenn ihr beide noch nie getanzt habt.",
        cta=("Termine ansehen", "Lieber Privatstunden"),
        fakten=[("2", "Tage bis zum Tanz"), ("3", "Häuser in Hannover"), ("61 €", "Flatrate pro Monat"), ("1954", "Seit drei Generationen")],
        warum_kicker="Warum ein Kurs, kein YouTube-Video",
        warum_h='Der Tanz muss <em>am Tag X</em> sitzen',
        warum=[
            ("Auf euer Lied", "Ihr bringt den Song mit. Wir zeigen euch, welcher Tanz dazu passt und wie ihr Anfang, Mitte und Ende gestaltet."),
            ("Auch ohne Vorkenntnisse", "Die meisten Paare bei uns haben vorher nie getanzt. Zwei Tage reichen für einen Tanz, der sicher aussieht."),
            ("Für den ganzen Abend", "Nach dem Eröffnungstanz geht die Feier weiter. Wir geben euch Discofox dazu — damit ihr nicht nach drei Minuten wieder sitzt."),
        ],
        kurse_kicker="Termine bis Frühjahr 2027",
        kurse_h='Hochzeitstanz <em>in Hannover</em>',
        kurse_lead="Zwei Wege zum Ziel: kompakt am Wochenende oder wöchentlich im Kurs. Die erste Stunde ist immer kostenlos.",
        kurse=[
            ("Kompakt", "Hochzeits-Express", "Langsamer Walzer, Discofox und Foxtrott an einem Wochenende", "Sa + So, 11:00 Uhr<br>Tanzvilla Waldersee", "2×", "monatlich"),
            ("Kompakt", "Hochzeits-Express", "Gleicher Inhalt, anderer Standort", "Sa + So, 14:00 Uhr<br>Tanzhaus Hannover", "2×", "monatlich"),
            ("a", "Privatstunde", "Nur ihr beide und eine Tanzlehrerin — auf euer Lied choreografiert", "nach Absprache<br>alle drei Häuser", "1×", "60 Minuten"),
            ("a", "Choreografie-Paket", "Fünf Privatstunden, eigener Ablauf, Video zum Üben", "nach Absprache<br>alle drei Häuser", "5×", "60 Minuten"),
            ("b", "Grundkurs Paartanz", "Wer mehr Zeit hat: Walzer und Discofox über acht Wochen", "Mittwoch, 19:30 Uhr<br>Tanzhaus Hannover", "8×", "ab 09.09.2026"),
            ("b", "Gäste-Kurs", "Für Trauzeugen und Familie, die auf der Feier mittanzen wollen", "Donnerstag, 20:00 Uhr<br>Tanzvilla Waldersee", "4×", "ab 10.09.2026"),
        ],
        weiter=["Discofox", "Langsamer Walzer", "Standard & Latein", "Salsa", "Privatstunden"],
        flat_h='Nach der Hochzeit <em>weitertanzen</em>',
        flat_text="Die meisten Paare bleiben. Mit der Flatrate stehen euch danach alle Kurse eures Levels offen — in allen drei Häusern, sieben Tage die Woche.",
        flat_punkte=["Alle Kurse eures Levels inklusive", "Drei Standorte, über 220 Angebote pro Woche", "Zugang zum Videoportal zum Üben", "Monatlich kündbar"],
        faq=[
            ("Wie lange vorher sollten wir anfangen?", "Für den Hochzeits-Express reicht ein Wochenende vier bis sechs Wochen vor der Feier — dann ist der Tanz noch frisch. Wer eine eigene Choreografie möchte, plant besser drei Monate ein."),
            ("Wir haben beide noch nie getanzt. Geht das?", "Ja, das ist der Normalfall. Der Hochzeits-Express ist genau für Paare ohne Vorkenntnisse gemacht. Wir fangen beim Grundschritt an."),
            ("Können wir unser eigenes Lied mitbringen?", "Unbedingt. Schickt uns den Titel vorab, dann prüfen wir Tempo und Taktart und schlagen euch den passenden Tanz vor. In den Privatstunden choreografieren wir direkt darauf."),
            ("Was kostet ein Hochzeitstanzkurs?", "Der Hochzeits-Express läuft über die Flatrate von 61 € pro Person und Monat — damit sind auch alle anderen Kurse eures Levels abgedeckt. Privatstunden rechnen wir separat ab, sprecht uns an."),
            ("Was ziehen wir an?", "Zum Kurs bequeme Kleidung und Schuhe mit glatter Sohle. Wer im Brautkleid tanzt, sollte zur letzten Stunde die Hochzeitsschuhe mitbringen — das verändert den Gang mehr, als man denkt."),
        ],
        seo_kicker="Hochzeitstanz lernen in Hannover",
        seo=[
            "Der <strong>Eröffnungstanz</strong> ist für die meisten Brautpaare der Moment, vor dem sie am meisten Respekt haben — und der, an den sich Gäste am längsten erinnern. In den <strong>Tanzschulen Familie Bothe</strong> bereiten wir Paare seit Jahrzehnten darauf vor, an drei Standorten in Hannover und Burgwedel.",
            "Der <strong>Hochzeits-Express</strong> ist unser Kompaktkurs: An einem Wochenende lernt ihr Langsamen Walzer, Discofox und Foxtrott — genug für den ersten Tanz und für den Rest des Abends. Wer mehr Zeit mitbringt, kommt in den <strong>Grundkurs Paartanz</strong> und baut über acht Wochen ein breiteres Repertoire auf.",
            "Für einen Tanz auf euer eigenes Lied empfehlen wir <strong>Privatstunden</strong>. Wir hören uns den Titel an, prüfen Tempo und Taktart und entwickeln daraus einen Ablauf mit Anfang, Höhepunkt und Schluss — inklusive Video zum Üben zu Hause.",
            "Auch <strong>Trauzeugen, Eltern und Gäste</strong> können mittanzen: Im Gäste-Kurs lernen sie in vier Abenden die Grundlagen, damit die Tanzfläche nach dem Eröffnungstanz nicht leer bleibt.",
        ],
        end_h='Wann ist <em>der große Tag?</em>',
        end_lead="Sagt uns euren Termin, wir finden den passenden Kurs. Die erste Stunde kostet nichts.",
        end_btn="Termin besprechen",
        schema_kurs=dict(name="Hochzeitstanzkurs Hannover — Hochzeits-Express",
                         desc="Langsamer Walzer, Discofox und Foxtrott an einem Wochenende — für Brautpaare ohne Vorkenntnisse.",
                         start="2026-09-12", load="PT8H"),
    ),
    dict(
        slug="salsa-hannover",
        titel="Salsa Hannover",
        desc="Salsa lernen in Hannover — Grundkurs bis Fortgeschritten, auch ohne Partner. Erste Stunde kostenlos, danach eine Flatrate für alle Kurse deines Levels.",
        brotkrume=["Start", "Kurse", "Paartanz", "Salsa"],
        h1='Salsa.<br>Ab dem ersten Abend <em>auf der Fläche</em>.',
        lead="Kein Tanz bringt so schnell so viel Stimmung. Bei uns lernst du Salsa in der Gruppe, mit Partnerwechsel — und stehst nach vier Abenden auf jeder Salsa-Party sicher da.",
        cta=("Kurse und Termine", "Was kostet das?"),
        fakten=[("4", "Abende Grundkurs"), ("3", "Häuser in Hannover"), ("61 €", "Flatrate pro Monat"), ("1954", "Seit drei Generationen")],
        warum_kicker="Warum Salsa bei Bothe",
        warum_h='Lernen, <em>ohne sich zu blamieren</em>',
        warum=[
            ("Auch ohne Partner", "Wir rotieren in der Gruppe. Wer allein kommt, tanzt mit allen — und lernt dadurch schneller zu führen und zu folgen."),
            ("Schritt für Schritt", "Grundschritt, Drehung, Wechsel. Wir bauen aufeinander auf, statt Figuren aneinanderzureihen, die man nach einer Woche vergisst."),
            ("Direkt anwendbar", "Was du hier lernst, funktioniert auf jeder Salsa-Party in Hannover. Wir üben in dem Tempo, das dort tatsächlich gespielt wird."),
        ],
        kurse_kicker="Termine ab September 2026",
        kurse_h='Salsa-Kurse <em>in Hannover</em>',
        kurse_lead="Alle Kurse wöchentlich, 60 Minuten. Die erste Stunde ist kostenlos — du entscheidest danach.",
        kurse=[
            ("", "Salsa 1", "Grundschritt und erste Drehungen, kein Vorwissen nötig", "Dienstag, 19:30 Uhr<br>Tanzhaus Hannover", "4×", "ab 08.09.2026"),
            ("", "Salsa 1", "Gleicher Inhalt, anderer Standort", "Mittwoch, 20:00 Uhr<br>Tanzvilla Waldersee", "4×", "ab 09.09.2026"),
            ("a", "Salsa 2", "Damensolo, Handwechsel, erste Figurenfolgen", "Dienstag, 20:45 Uhr<br>Tanzhaus Hannover", "6×", "ab 08.09.2026"),
            ("a", "Salsa 2", "Gleicher Inhalt, für den Norden", "Donnerstag, 19:00 Uhr<br>Tanzhaus Burgwedel", "6×", "ab 10.09.2026"),
            ("b", "Salsa Club", "Laufender Kurs für Fortgeschrittene, Einstieg jederzeit", "Freitag, 21:00 Uhr<br>Tanzhaus Hannover", "∞", "jede Woche"),
            ("b", "Bachata", "Der ruhigere Partnertanz — läuft auf jeder Salsa-Party mit", "Montag, 20:15 Uhr<br>Tanzhaus Hannover", "4×", "ab 07.09.2026"),
        ],
        weiter=["Bachata", "Discofox", "West Coast Swing", "Standard & Latein", "Privatstunden"],
        flat_h='Tanz, so oft <em>du willst</em>',
        flat_text="Bei uns zahlst du nicht pro Kurs, sondern einen Beitrag. Damit stehen dir alle Stunden deines Levels offen — auch Bachata und Discofox, nicht nur Salsa.",
        flat_punkte=["Alle Kurse deines Levels inklusive", "Drei Standorte, über 220 Angebote pro Woche", "Zugang zum Videoportal für zu Hause", "Monatlich kündbar, keine Kursgebühr obendrauf"],
        faq=[
            ("Brauche ich einen Tanzpartner?", "Nein. In unseren Salsa-Kursen wird rotiert, dadurch tanzt jede und jeder mit wechselnden Partnern. Wer als Paar kommt, kann selbstverständlich zusammenbleiben."),
            ("Welchen Salsa-Stil unterrichtet ihr?", "Wir unterrichten Salsa auf 1 im Cross-Body-Stil — das ist der Stil, der auf Partys in Hannover und im ganzen deutschsprachigen Raum am weitesten verbreitet ist."),
            ("Wie lange dauert es, bis ich mittanzen kann?", "Der Grundschritt sitzt meist am ersten Abend. Nach den vier Terminen des Grundkurses kommst du auf einer Salsa-Party zurecht. Für längere Figurenfolgen geht es in Salsa 2 weiter."),
            ("Was kostet ein Salsa-Kurs bei Bothe?", "Wir rechnen nicht pro Kurs ab. Für 61 € pro Person und Monat stehen dir alle Kurse deines Levels in allen drei Häusern offen. Die erste Stunde ist immer kostenlos."),
            ("Welche Schuhe brauche ich?", "Für die erste Stunde reichen saubere Schuhe mit glatter Sohle. Tanzschuhe lohnen sich erst, wenn du dabeibleibst — wir beraten dich dann in Ruhe."),
        ],
        seo_kicker="Salsa lernen in Hannover",
        seo=[
            "<strong>Salsa</strong> ist der Partnertanz mit der kürzesten Strecke zwischen erstem Kurs und erster Party. In den <strong>Tanzschulen Familie Bothe</strong> unterrichten wir ihn an drei Standorten in Hannover und Burgwedel — in Gruppen mit Partnerwechsel, damit auch Einzelpersonen mitkommen.",
            "Im <strong>Grundkurs Salsa 1</strong> lernst du den Grundschritt, die Führung und die ersten Drehungen — vier Abende, ohne Vorkenntnisse. <strong>Salsa 2</strong> ergänzt Damensolo, Handwechsel und längere Figurenfolgen. Wer regelmäßig tanzen möchte, kommt in den <strong>Salsa Club</strong>, der wöchentlich fortlaufend läuft.",
            "Dazu passt <strong>Bachata</strong>: der ruhigere kubanisch-dominikanische Partnertanz, der auf jeder Salsa-Party mitläuft. Viele Tanzende lernen beide parallel — mit unserer Flatrate ist das ohne Aufpreis möglich.",
            "Wer es persönlicher möchte oder auf ein bestimmtes Ereignis hinarbeitet, bucht <strong>Privatstunden</strong> nach Terminabsprache. Alle Salsa-Kurse laufen im Rahmen der Flatrate: ein Beitrag, alle Stunden deines Levels, drei Häuser.",
        ],
        end_h='Worauf <em>wartest</em> du?',
        end_lead="Nächster Grundkurs startet am 8. September. Die erste Stunde kostet nichts.",
        end_btn="Jetzt Platz sichern",
        schema_kurs=dict(name="Salsa Grundkurs Hannover",
                         desc="Salsa von Grund auf lernen — vier Abende, ohne Vorkenntnisse, mit Partnerwechsel in der Gruppe.",
                         start="2026-09-08", load="PT4H"),
    ),
    dict(
        slug="standard-latein-hannover",
        titel="Standard & Latein Hannover",
        desc="Standard und Latein in Hannover — Welttanzprogramm vom Grundkurs bis zum Medaillenkurs. Erste Stunde kostenlos, danach eine Flatrate.",
        brotkrume=["Start", "Kurse", "Paartanz", "Standard & Latein"],
        h1='Die Tänze, die man <em>ein Leben lang</em> kann.',
        lead="Walzer, Foxtrott, Tango, Rumba, Cha-Cha-Cha. Das Welttanzprogramm ist die Grundlage, auf der alles andere aufbaut — und der Grund, warum man auf jedem Ball mittanzen kann.",
        cta=("Kurse und Termine", "Was kostet das?"),
        fakten=[("10", "Tänze im Programm"), ("3", "Häuser in Hannover"), ("61 €", "Flatrate pro Monat"), ("1954", "Seit drei Generationen")],
        warum_kicker="Warum das Welttanzprogramm",
        warum_h='Einmal gelernt, <em>überall gültig</em>',
        warum=[
            ("Auf jedem Ball", "Vom Opernball bis zur Firmenfeier: Wer Walzer und Foxtrott kann, steht nie ratlos am Rand."),
            ("Aufeinander aufgebaut", "Das Welttanzprogramm ist ein durchdachter Lehrplan, kein Sammelsurium. Jede Stufe baut sauber auf der vorigen auf."),
            ("Bis zum Abzeichen", "Wer möchte, legt bei uns die Tanzabzeichen in Bronze, Silber und Gold ab — mit offizieller Prüfung."),
        ],
        kurse_kicker="Termine ab September 2026",
        kurse_h='Standard &amp; Latein <em>in Hannover</em>',
        kurse_lead="Alle Kurse wöchentlich, 60 Minuten. Die erste Stunde ist kostenlos — du entscheidest danach.",
        kurse=[
            ("", "Welttanzprogramm 1", "Langsamer Walzer, Discofox, Foxtrott und Cha-Cha-Cha", "Montag, 19:30 Uhr<br>Tanzhaus Hannover", "8×", "ab 07.09.2026"),
            ("", "Welttanzprogramm 1", "Gleicher Inhalt, anderer Standort", "Dienstag, 20:00 Uhr<br>Tanzvilla Waldersee", "8×", "ab 08.09.2026"),
            ("a", "Welttanzprogramm 2", "Wiener Walzer, Rumba, Jive und Tango kommen dazu", "Mittwoch, 20:15 Uhr<br>Tanzhaus Hannover", "8×", "ab 09.09.2026"),
            ("a", "Welttanzprogramm 2", "Gleicher Inhalt, für den Norden", "Donnerstag, 20:00 Uhr<br>Tanzhaus Burgwedel", "8×", "ab 10.09.2026"),
            ("b", "Medaillenkurs", "Bronze, Silber, Gold — mit offizieller Abzeichenprüfung", "Freitag, 19:00 Uhr<br>Tanzhaus Hannover", "12×", "ab 11.09.2026"),
            ("b", "Tanzkreis", "Laufender Kurs für Fortgeschrittene, Einstieg jederzeit", "Sonntag, 18:00 Uhr<br>Tanzvilla Waldersee", "∞", "jede Woche"),
        ],
        weiter=["Discofox", "Hochzeitstanz", "Salsa", "West Coast Swing", "Privatstunden"],
        flat_h='Tanz, so oft <em>du willst</em>',
        flat_text="Ein Beitrag, alle Stunden deines Levels. Wer im Welttanzprogramm ist, kann parallel Discofox oder Salsa mitnehmen — ohne Aufpreis.",
        flat_punkte=["Alle Kurse deines Levels inklusive", "Drei Standorte, über 220 Angebote pro Woche", "Zugang zum Videoportal für zu Hause", "Monatlich kündbar, keine Kursgebühr obendrauf"],
        faq=[
            ("Was ist das Welttanzprogramm genau?", "Ein bundesweit einheitlicher Lehrplan des Allgemeinen Deutschen Tanzlehrerverbands. Er legt fest, welche Tänze in welcher Reihenfolge unterrichtet werden — dadurch könnt ihr auch in einer anderen Stadt nahtlos weitermachen."),
            ("Brauche ich einen Tanzpartner?", "Für die Paarkurse ist ein Partner sinnvoll, aber keine Bedingung — wir rotieren, wenn die Gruppe es zulässt. Wer dauerhaft sucht, kann unsere Tanzpartnerbörse nutzen."),
            ("Wie viele Tänze lerne ich?", "Im ersten Kurs vier Tänze, im zweiten kommen vier weitere dazu. Wer bis zum Medaillenkurs geht, beherrscht das komplette Welttanzprogramm mit zehn Tänzen."),
            ("Was kostet ein Kurs?", "Wir rechnen nicht pro Kurs ab. Für 61 € pro Person und Monat stehen dir alle Kurse deines Levels in allen drei Häusern offen. Die erste Stunde ist immer kostenlos."),
            ("Kann ich ein Tanzabzeichen machen?", "Ja. Im Medaillenkurs bereiten wir auf die offiziellen Prüfungen in Bronze, Silber und Gold vor. Die Prüfung nimmt ein Prüfer des Verbands ab."),
        ],
        seo_kicker="Standard und Latein lernen in Hannover",
        seo=[
            "<strong>Standard- und Lateintänze</strong> sind das Fundament des Gesellschaftstanzes. Wer Langsamen Walzer, Foxtrott, Wiener Walzer, Tango, Cha-Cha-Cha, Rumba und Jive beherrscht, kommt auf jedem Ball und jeder Feier zurecht. In den <strong>Tanzschulen Familie Bothe</strong> unterrichten wir sie nach dem <strong>Welttanzprogramm</strong> des ADTV.",
            "Im <strong>Welttanzprogramm 1</strong> beginnt ihr mit Langsamem Walzer, Discofox, Foxtrott und Cha-Cha-Cha — acht Abende, ohne Vorkenntnisse. Im <strong>Welttanzprogramm 2</strong> kommen Wiener Walzer, Rumba, Jive und Tango dazu.",
            "Wer weitergehen möchte, wechselt in den <strong>Medaillenkurs</strong> und legt die offiziellen Tanzabzeichen in Bronze, Silber und Gold ab. Für Paare, die einfach regelmäßig tanzen wollen, läuft sonntags der <strong>Tanzkreis</strong> mit freiem Einstieg.",
            "Ein Vorteil des Welttanzprogramms: Es ist bundesweit einheitlich. Wer umzieht, kann in jeder ADTV-Tanzschule auf demselben Stand weitermachen. Alle Kurse laufen im Rahmen unserer Flatrate — ein Beitrag, alle Stunden deines Levels, drei Häuser.",
        ],
        end_h='Bereit für den <em>ersten Walzer?</em>',
        end_lead="Nächster Grundkurs startet am 7. September. Die erste Stunde kostet nichts.",
        end_btn="Jetzt Platz sichern",
        schema_kurs=dict(name="Welttanzprogramm 1 — Standard und Latein Hannover",
                         desc="Langsamer Walzer, Discofox, Foxtrott und Cha-Cha-Cha nach dem ADTV-Welttanzprogramm.",
                         start="2026-09-07", load="PT8H"),
    ),
    dict(
        slug="west-coast-swing-hannover",
        titel="West Coast Swing Hannover",
        desc="West Coast Swing in Hannover — der Partnertanz zu aktueller Musik. Grundkurs bis Fortgeschritten, erste Stunde kostenlos.",
        brotkrume=["Start", "Kurse", "Paartanz", "West Coast Swing"],
        h1='West Coast Swing.<br>Der Tanz zu <em>heutiger Musik</em>.',
        lead="Kein Schlager, kein Standard-Repertoire: West Coast Swing funktioniert zu dem, was gerade in den Charts läuft. Führen und Folgen sind hier ein Gespräch, keine Ansage.",
        cta=("Kurse und Termine", "Was kostet das?"),
        fakten=[("6", "Abende Grundkurs"), ("3", "Häuser in Hannover"), ("61 €", "Flatrate pro Monat"), ("1954", "Seit drei Generationen")],
        warum_kicker="Warum West Coast Swing",
        warum_h='Der modernste <em>Partnertanz</em>',
        warum=[
            ("Zu aktueller Musik", "Pop, R&B, Soul, Blues — West Coast Swing passt zu fast allem im mittleren Tempo. Auch zu dem, was du ohnehin hörst."),
            ("Kein starres Schema", "Statt fester Figurenfolgen lernst du Prinzipien. Das Ergebnis: Jeder Tanz sieht anders aus, weil er wirklich improvisiert ist."),
            ("Weltweit dieselbe Sprache", "West Coast Swing wird international nach denselben Prinzipien unterrichtet. Du kannst auf jeder Party mittanzen, egal in welchem Land."),
        ],
        kurse_kicker="Termine ab September 2026",
        kurse_h='West Coast Swing <em>in Hannover</em>',
        kurse_lead="Alle Kurse wöchentlich, 60 Minuten. Die erste Stunde ist kostenlos — du entscheidest danach.",
        kurse=[
            ("", "WCS Basics", "Sugar Push, Side Pass, Whip — die vier Grundmuster", "Donnerstag, 19:30 Uhr<br>Tanzhaus Hannover", "6×", "ab 10.09.2026"),
            ("", "WCS Basics", "Gleicher Inhalt, anderer Standort", "Montag, 20:00 Uhr<br>Tanzvilla Waldersee", "6×", "ab 07.09.2026"),
            ("a", "WCS Aufbau", "Anchor, Variationen und die ersten eigenen Einfälle", "Donnerstag, 20:45 Uhr<br>Tanzhaus Hannover", "8×", "ab 10.09.2026"),
            ("a", "Musikalität", "Wie man Breaks und Textzeilen hörbar mittanzt", "Dienstag, 21:00 Uhr<br>Tanzhaus Hannover", "4×", "ab 08.09.2026"),
            ("b", "WCS Social", "Offener Übungsabend mit Anleitung, Einstieg jederzeit", "Sonntag, 19:30 Uhr<br>Tanzhaus Hannover", "∞", "jede Woche"),
            ("b", "Workshop-Wochenende", "Zwei Tage mit Gasttrainern aus der internationalen Szene", "Sa + So, 11:00 Uhr<br>Tanzhaus Hannover", "2×", "pro Halbjahr"),
        ],
        weiter=["Discofox", "Salsa", "Standard & Latein", "Hochzeitstanz", "Privatstunden"],
        flat_h='Tanz, so oft <em>du willst</em>',
        flat_text="Ein Beitrag, alle Stunden deines Levels. Viele im West Coast Swing nehmen Discofox oder Salsa parallel mit — ohne Aufpreis.",
        flat_punkte=["Alle Kurse deines Levels inklusive", "Drei Standorte, über 220 Angebote pro Woche", "Zugang zum Videoportal für zu Hause", "Monatlich kündbar, keine Kursgebühr obendrauf"],
        faq=[
            ("Was unterscheidet West Coast Swing von Discofox?", "Discofox hat feste Figuren und einen gleichbleibenden Grundschritt. West Coast Swing arbeitet mit einer elastischen Verbindung zwischen den Partnern und lässt beiden Raum für eigene Ideen — dadurch ist er langsamer zu lernen, aber vielseitiger."),
            ("Brauche ich einen Tanzpartner?", "Nein. Wir rotieren in der Gruppe. Gerade im West Coast Swing ist das sinnvoll, weil jede Verbindung sich anders anfühlt und man dadurch schneller lernt."),
            ("Ist das schwierig?", "Der Einstieg dauert länger als bei Discofox — die vier Grundmuster brauchen etwa sechs Abende. Dafür wird es danach nie langweilig, weil es keine feste Obergrenze an Figuren gibt."),
            ("Zu welcher Musik tanzt man das?", "Zu allem im mittleren Tempo: Pop, R&B, Soul, Blues, teilweise auch Country. Auf unseren Übungsabenden läuft überwiegend aktuelle Chartmusik."),
            ("Was kostet ein Kurs?", "Wir rechnen nicht pro Kurs ab. Für 61 € pro Person und Monat stehen dir alle Kurse deines Levels in allen drei Häusern offen. Die erste Stunde ist immer kostenlos."),
        ],
        seo_kicker="West Coast Swing lernen in Hannover",
        seo=[
            "<strong>West Coast Swing</strong> ist der modernste der Partnertänze — und der einzige, den man zu aktueller Chartmusik tanzt. In den <strong>Tanzschulen Familie Bothe</strong> unterrichten wir ihn in Hannover mit wöchentlichen Kursen und einem offenen Übungsabend.",
            "Im <strong>Grundkurs WCS Basics</strong> lernst du die vier Grundmuster — Sugar Push, Side Pass, Whip und Underarm Turn — sowie die elastische Verbindung, die den Tanz ausmacht. Sechs Abende, ohne Vorkenntnisse.",
            "Im <strong>Aufbaukurs</strong> kommen Anchor-Variationen und eigene Gestaltung dazu. Der Spezialkurs <strong>Musikalität</strong> beschäftigt sich damit, wie man Breaks, Textzeilen und Tempowechsel hörbar mittanzt — das, was West Coast Swing von außen so besonders aussehen lässt.",
            "Zweimal im Jahr holen wir <strong>Gasttrainer aus der internationalen Szene</strong> für ein Workshop-Wochenende nach Hannover. Alle Kurse laufen im Rahmen unserer Flatrate: ein Beitrag, alle Stunden deines Levels, drei Häuser.",
        ],
        end_h='Neugierig <em>geworden?</em>',
        end_lead="Nächster Grundkurs startet am 7. September. Die erste Stunde kostet nichts.",
        end_btn="Jetzt Platz sichern",
        schema_kurs=dict(name="West Coast Swing Grundkurs Hannover",
                         desc="Die vier Grundmuster des West Coast Swing — sechs Abende, ohne Vorkenntnisse.",
                         start="2026-09-07", load="PT6H"),
    ),
    dict(
        slug="kindertanz-hannover",
        titel="Kindertanz Hannover",
        desc="Kindertanz in Hannover ab 2 Jahren — Windelhopper, Kindertanz, Ballett und Dance4Kids in drei Häusern. Erste Stunde kostenlos.",
        brotkrume=["Start", "Kurse", "Kinder", "Kindertanz"],
        h1='Erst wackeln.<br>Dann <em>tanzen</em>.',
        lead="Ab zwei Jahren, gemeinsam mit Mama oder Papa. Später allein, in der eigenen Gruppe, mit eigenem Auftritt. Kindertanz bei uns ist kein Vorturnen — es ist der Ort, an dem Kinder ihren eigenen Rhythmus finden.",
        cta=("Gruppen und Termine", "Was kostet das?"),
        fakten=[("2", "Jahre Mindestalter"), ("3", "Häuser in Hannover"), ("61 €", "Flatrate pro Monat"), ("1954", "Seit drei Generationen")],
        warum_kicker="Warum Kindertanz",
        warum_h='Bewegung, die <em>Kinder selbst wollen</em>',
        warum=[
            ("Nach Alter getrennt", "Zweijährige brauchen etwas anderes als Achtjährige. Wir teilen in enge Altersstufen, damit niemand über- oder unterfordert ist."),
            ("Mit echtem Auftritt", "Zweimal im Jahr steht die Gruppe auf einer richtigen Bühne — mit Licht, Publikum und Applaus. Das prägt mehr als jede Stunde."),
            ("Eltern dürfen bleiben", "Bei den Kleinsten tanzt ein Elternteil mit. Danach gibt es Fenster zum Zuschauen, ohne dass wir die Gruppe stören."),
        ],
        kurse_kicker="Gruppen ab September 2026",
        kurse_h='Kindertanz <em>in Hannover</em>',
        kurse_lead="Alle Gruppen wöchentlich, 45 bis 60 Minuten je nach Alter. Die erste Stunde ist kostenlos.",
        kurse=[
            ("", "Windelhopper", "2–3 Jahre, gemeinsam mit einem Elternteil", "Montag, 15:30 Uhr<br>Tanzhaus Hannover", "45", "Minuten"),
            ("", "Kindertanz 3–5", "Erste eigene Gruppe, Bewegungsspiele und kleine Choreografien", "Dienstag, 15:45 Uhr<br>Tanzvilla Waldersee", "45", "Minuten"),
            ("a", "Ballett ab 4", "Klassische Grundlagen, Haltung und Körpergefühl", "Mittwoch, 16:00 Uhr<br>Tanzhaus Hannover", "60", "Minuten"),
            ("a", "Dance4Kids 6–8", "Moderner Kindertanz mit Auftritt am Ende der Saison", "Donnerstag, 16:00 Uhr<br>Tanzhaus Hannover", "60", "Minuten"),
            ("a", "Dance4Kids 9–11", "Choreografien, erste Hip-Hop-Elemente, Showcase", "Freitag, 16:30 Uhr<br>Tanzhaus Burgwedel", "60", "Minuten"),
            ("b", "Ferienprogramm", "Tanzwoche in den Schulferien, täglich mit Abschlussshow", "Mo–Fr, 10:00 Uhr<br>Tanzhaus Hannover", "5×", "pro Ferienwoche"),
        ],
        weiter=["Hip Hop ab 12", "Ballett", "Schülertanzkurse", "Kindergeburtstage", "Elterntanz"],
        flat_h='Ein Beitrag, <em>alle Stunden</em>',
        flat_text="Auch für Kinder gilt die Flatrate: Wer möchte, kommt zweimal die Woche — Kindertanz und Ballett zusammen kosten nicht mehr als eine Stunde.",
        flat_punkte=["Alle Gruppen der Altersstufe inklusive", "Drei Standorte, kurze Wege für Eltern", "Auftritte und Showcase ohne Aufpreis", "Monatlich kündbar"],
        faq=[
            ("Ab welchem Alter kann mein Kind mitmachen?", "Ab zwei Jahren in den Windelhoppern, dort tanzt ein Elternteil mit. Ab drei Jahren gehen die Kinder in ihre eigene Gruppe, ab vier Jahren kommt Ballett dazu."),
            ("Muss ich als Elternteil dabeibleiben?", "Bei den Windelhoppern ja, das gehört zum Konzept. Ab der Gruppe 3–5 tanzen die Kinder allein — Sie können in unserem Wartebereich bleiben, es gibt feste Termine zum Zuschauen."),
            ("Was kostet Kindertanz bei Bothe?", "Wir rechnen nicht pro Kurs ab. Für 61 € pro Monat stehen alle Gruppen der Altersstufe offen, in allen drei Häusern. Die erste Stunde ist kostenlos."),
            ("Was zieht mein Kind an?", "Bequeme Kleidung, in der es sich frei bewegen kann, und rutschfeste Socken oder Gymnastikschläppchen. Für Ballett beraten wir Sie, sobald klar ist, dass Ihr Kind dabeibleibt."),
            ("Gibt es Auftritte?", "Ja, zweimal im Jahr — beim Showcase und beim Junioren-Galaball. Die Teilnahme ist freiwillig und ohne Zusatzkosten."),
        ],
        seo_kicker="Kindertanz lernen in Hannover",
        seo=[
            "<strong>Kindertanz</strong> ist für viele Kinder der erste Sport, den sie sich selbst aussuchen. In den <strong>Tanzschulen Familie Bothe</strong> unterrichten wir ihn an drei Standorten in Hannover und Burgwedel — in engen Altersstufen von zwei bis elf Jahren.",
            "Die <strong>Windelhopper</strong> beginnen ab zwei Jahren gemeinsam mit einem Elternteil. Ab drei Jahren folgt die erste eigene Gruppe mit Bewegungsspielen und kleinen Choreografien, ab vier Jahren kommt <strong>Ballett</strong> mit klassischen Grundlagen dazu.",
            "In den <strong>Dance4Kids</strong>-Gruppen ab sechs und ab neun Jahren arbeiten die Kinder auf einen richtigen Auftritt hin — beim Showcase und beim Junioren-Galaball, mit Bühne, Licht und Publikum. Wer danach weitermachen will, wechselt mit zwölf Jahren in unsere Hip-Hop- und Contemporary-Gruppen.",
            "In den Schulferien läuft unser <strong>Ferienprogramm</strong> als Tanzwoche mit täglichem Training und Abschlussshow. Alle Kindergruppen laufen im Rahmen der Flatrate: ein Beitrag, alle Stunden der Altersstufe, drei Häuser — mit Parkplätzen direkt vor der Tür.",
        ],
        end_h='Einfach mal <em>ausprobieren?</em>',
        end_lead="Die erste Stunde kostet nichts und verpflichtet zu nichts.",
        end_btn="Probestunde sichern",
        schema_kurs=dict(name="Kindertanz Hannover — Dance4Kids 6 bis 8 Jahre",
                         desc="Moderner Kindertanz für Sechs- bis Achtjährige, wöchentlich 60 Minuten, mit Auftritt am Saisonende.",
                         start="2026-09-10", load="PT1H"),
    ),
    dict(
        slug="hip-hop-hannover",
        titel="Hip Hop Hannover",
        desc="Hip Hop und Contemporary in Hannover ab 12 Jahren — Juniors, Adults und Crew-Training im Studio B. Erste Stunde kostenlos.",
        brotkrume=["Start", "Kurse", "Studio B", "Hip Hop"],
        h1='Studio B.<br>Wo <em>dein Stil</em> entsteht.',
        lead="Kein Ballsaal, kein Spiegelparkett-Klischee. Studio B ist unser Urban-Bereich: Hip Hop, Contemporary und Crew-Training ab zwölf Jahren — mit Trainern, die selbst auf Battles stehen.",
        cta=("Kurse und Termine", "Was kostet das?"),
        fakten=[("12", "Jahre Mindestalter"), ("3", "Häuser in Hannover"), ("61 €", "Flatrate pro Monat"), ("1954", "Seit drei Generationen")],
        warum_kicker="Warum Studio B",
        warum_h='Urban Dance, <em>richtig unterrichtet</em>',
        warum=[
            ("Technik statt Nachtanzen", "Grooves, Isolation, Bounce — wir bauen die Grundlagen auf, statt nur Choreos vorzumachen. Damit kannst du auch freestylen."),
            ("Eigene Crew", "Wer weiter will, kommt ins Crew-Training und tritt bei Showcases und Wettbewerben an. Mehrere unserer Gruppen tanzen auf Turnieren."),
            ("Alle Level", "Juniors ab 12, Adults ab 16, dazu offene Sessions. Einsteigen kannst du, ohne je getanzt zu haben."),
        ],
        kurse_kicker="Termine ab September 2026",
        kurse_h='Hip Hop &amp; Contemporary <em>in Hannover</em>',
        kurse_lead="Alle Kurse wöchentlich, 60 bis 90 Minuten. Die erste Stunde ist kostenlos.",
        kurse=[
            ("", "Hip Hop Juniors", "12–15 Jahre, Grooves und erste Choreografien", "Montag, 17:00 Uhr<br>Tanzhaus Hannover", "60", "Minuten"),
            ("", "Hip Hop Adults", "ab 16 Jahren, Einstieg ohne Vorkenntnisse", "Dienstag, 19:00 Uhr<br>Tanzhaus Hannover", "60", "Minuten"),
            ("a", "Contemporary", "ab 12 Jahren, Fluss, Bodenarbeit und Ausdruck", "Mittwoch, 17:30 Uhr<br>Tanzvilla Waldersee", "60", "Minuten"),
            ("a", "Breakdance", "ab 10 Jahren, Toprock, Footwork und erste Freezes", "Donnerstag, 17:00 Uhr<br>Tanzhaus Hannover", "60", "Minuten"),
            ("b", "Crew-Training", "Auf Einladung, Vorbereitung auf Showcases und Battles", "Freitag, 18:30 Uhr<br>Tanzhaus Hannover", "90", "Minuten"),
            ("b", "Open Session", "Freies Training mit Betreuung, Einstieg jederzeit", "Sonntag, 17:00 Uhr<br>Tanzhaus Hannover", "∞", "jede Woche"),
        ],
        weiter=["Kindertanz bis 11", "Contemporary", "Breakdance", "Schülertanzkurse", "Privatstunden"],
        flat_h='Tanz, so oft <em>du willst</em>',
        flat_text="Ein Beitrag, alle Stunden deines Levels. Wer Hip Hop und Contemporary parallel machen will, zahlt keinen Cent mehr.",
        flat_punkte=["Alle Kurse deines Levels inklusive", "Drei Standorte, über 220 Angebote pro Woche", "Zugang zum Videoportal zum Üben", "Monatlich kündbar, keine Kursgebühr obendrauf"],
        faq=[
            ("Muss ich schon tanzen können?", "Nein. Die Juniors- und Adults-Kurse sind für Einsteiger gebaut — wir fangen bei Groove und Haltung an. Vorerfahrung ist willkommen, aber keine Bedingung."),
            ("Ab welchem Alter kann ich mitmachen?", "Hip Hop und Contemporary ab zwölf Jahren, Breakdance ab zehn. Wer jünger ist, findet in unseren Dance4Kids-Gruppen den passenden Einstieg."),
            ("Was kostet Hip Hop bei Bothe?", "Wir rechnen nicht pro Kurs ab. Für 61 € pro Person und Monat stehen dir alle Kurse deines Levels in allen drei Häusern offen. Die erste Stunde ist immer kostenlos."),
            ("Was ist der Unterschied zwischen Hip Hop und Contemporary?", "Hip Hop arbeitet mit Bounce, Groove und klaren Akzenten zur Musik. Contemporary ist fließender, nutzt den Boden und legt mehr Gewicht auf Ausdruck. Viele bei uns machen beides."),
            ("Kann ich in einer Crew tanzen?", "Ja. Das Crew-Training läuft auf Einladung — wer regelmäßig kommt und will, wird von den Trainern angesprochen. Von dort geht es zu Showcases und Wettbewerben."),
        ],
        seo_kicker="Hip Hop lernen in Hannover",
        seo=[
            "<strong>Hip Hop</strong> ist der meistgetanzte Stil unter Jugendlichen — und einer, bei dem der Unterschied zwischen Nachtanzen und echtem Können groß ist. Im <strong>Studio B</strong> der Tanzschulen Familie Bothe unterrichten wir ihn ab zwölf Jahren an drei Standorten in Hannover und Burgwedel.",
            "In den <strong>Juniors</strong> ab zwölf und den <strong>Adults</strong> ab sechzehn Jahren beginnen wir bei den Grundlagen: Groove, Bounce, Isolation und Musikalität. Darauf bauen Choreografien auf — und die Fähigkeit, auch ohne vorgegebene Schrittfolge zu tanzen.",
            "Dazu kommen <strong>Contemporary</strong> mit Bodenarbeit und Ausdruck sowie <strong>Breakdance</strong> ab zehn Jahren mit Toprock, Footwork und Freezes. Wer weitergehen möchte, wird ins <strong>Crew-Training</strong> eingeladen und tritt bei Showcases und Wettbewerben an.",
            "Sonntags läuft die <strong>Open Session</strong> als freies Training mit Betreuung — offen für alle, die einfach tanzen wollen. Alle Studio-B-Kurse laufen im Rahmen unserer Flatrate: ein Beitrag, alle Stunden deines Levels, drei Häuser.",
        ],
        end_h='Komm <em>vorbei</em>.',
        end_lead="Erste Stunde kostenlos, ohne Anmeldung im Voraus. Bring bequeme Schuhe mit.",
        end_btn="Zum Kursfinder",
        schema_kurs=dict(name="Hip Hop Hannover — Juniors ab 12 Jahren",
                         desc="Hip Hop für Zwölf- bis Fünfzehnjährige: Grooves, Isolation und Choreografien, wöchentlich 60 Minuten.",
                         start="2026-09-07", load="PT1H"),
    ),
]


def kurs_html(k):
    lvl, name, sub, zeit, anz, wann = k
    # "" / "a" / "b" sind die drei Farbstufen aus dem CI. Steht dort etwas
    # anderes, ist es eine eigene Beschriftung in der Grundfarbe.
    stufen = {"": "Grundkurs", "a": "Aufbau", "b": "Spezial"}
    label = stufen.get(lvl, lvl)
    cls = lvl if lvl in stufen else ""
    return f"""      <div class="kurs">
        <div class="kn"><span class="lvl {cls}">{label}</span><br>{name}<small>{sub}</small></div>
        <div class="kt">{zeit}</div>
        <div class="kp"><b>{anz}</b>{wann}</div>
        <a class="btn btn-red" href="#">Antanzen</a>
      </div>"""


def build(p):
    fakten = "".join(f'<div><b>{b}</b><span>{s}</span></div>' for b, s in p["fakten"])
    warum = "".join(
        f'      <div class="card"><span class="no">{i:02d}</span><h3>{t}</h3><p>{x}</p></div>\n'
        for i, (t, x) in enumerate(p["warum"], 1))
    kurse = "\n".join(kurs_html(k) for k in p["kurse"])
    weiter = "".join(f'<a class="chip" href="#">{w}</a>\n      ' for w in p["weiter"])
    flatli = "".join(f"<li>{x}</li>" for x in p["flat_punkte"])
    faq = "".join(
        f'      <details{" open" if i == 0 else ""}><summary>{q}</summary><p>{a}</p></details>\n'
        for i, (q, a) in enumerate(p["faq"]))
    seo = "".join(f"    <p>{x}</p>\n" for x in p["seo"])
    krumen = p["brotkrume"]
    brd = ""
    for i, b in enumerate(krumen):
        inner = b if i == len(krumen) - 1 else '<a href="#">' + b + "</a>"
        brd += "<span>" + inner + "</span>"
    locs = "".join(
        f'      <div class="loc"><h3>{n}</h3><address>{s}<br>{o}</address>'
        f'<a class="lk" href="#">Route ansehen →</a></div>\n' for n, s, o in STANDORTE)

    schema = {"@context": "https://schema.org", "@graph": [
        {"@type": "DanceSchool", "@id": "#schule", "name": "Tanzschulen Familie Bothe",
         "foundingDate": "1954", "telephone": "+49-511-663766",
         "email": "tanzen@tanzschulen-bothe.de",
         "aggregateRating": {"@type": "AggregateRating", "ratingValue": "4.4", "reviewCount": "300"},
         "location": [{"@type": "Place", "name": n, "address": {
             "@type": "PostalAddress", "streetAddress": s,
             "postalCode": o.split()[0], "addressLocality": " ".join(o.split()[1:]),
             "addressCountry": "DE"}} for n, s, o in STANDORTE]},
        {"@type": "Course", "name": p["schema_kurs"]["name"], "provider": {"@id": "#schule"},
         "description": p["schema_kurs"]["desc"],
         "offers": {"@type": "Offer", "price": "61", "priceCurrency": "EUR",
                    "category": "Monatsbeitrag Flatrate"},
         "hasCourseInstance": {"@type": "CourseInstance", "courseMode": "onsite",
                               "startDate": p["schema_kurs"]["start"],
                               "courseWorkload": p["schema_kurs"]["load"]}},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": i, "name": b}
            for i, b in enumerate(p["brotkrume"], 1)]},
        {"@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": q,
             "acceptedAnswer": {"@type": "Answer", "text": re.sub(r"<[^>]+>", "", a)}}
            for q, a in p["faq"][:3]]}]}

    return f"""<title>{p['titel']}</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="{html.escape(p['desc'], quote=True)}">
<style>{FONTS}</style>
<style>
{SHARED_CSS}</style>

<header>
  <div class="wrap hd">
    <a class="logo" href="#"><i></i><i></i>Bothe</a>
    <nav class="hd-nav">
      <a href="#kurse" aria-current="page">Kurse</a>
      <a href="#flatrate">Preise</a>
      <a href="#standorte">Standorte</a>
      <a href="#faq">Fragen</a>
    </nav>
    <a class="btn btn-red" href="#kurse">Kostenlos antanzen</a>
  </div>
</header>

<section class="hero">
  <div class="wrap">
    <div class="brd">{brd}</div>
    <h1>{p['h1']}</h1>
    <p class="lead">{p['lead']}</p>
    <div class="hero-cta">
      <a class="btn btn-red" href="#kurse">{p['cta'][0]}</a>
      <a class="btn btn-line" href="#flatrate">{p['cta'][1]}</a>
    </div>
    <div class="facts">{fakten}</div>
  </div>
</section>

<section class="sec">
  <div class="wrap">
    <div class="sechead">
      <div class="kicker">{p['warum_kicker']}</div>
      <h2 class="h-display">{p['warum_h']}</h2>
    </div>
    <div class="grid g3">
{warum}    </div>
  </div>
</section>

<section class="sec warmbg" id="kurse">
  <div class="wrap">
    <div class="sechead">
      <div class="kicker r">{p['kurse_kicker']}</div>
      <h2 class="h-display">{p['kurse_h']}</h2>
      <p class="lead">{p['kurse_lead']}</p>
    </div>
    <div class="kurse">
{kurse}
    </div>
    <div class="chips" style="margin-top:32px">
      {weiter}</div>
  </div>
</section>

<section class="sec" id="flatrate">
  <div class="wrap">
    <div class="flat">
      <div>
        <h2>{p['flat_h']}</h2>
        <p style="margin-top:18px;color:color-mix(in srgb,#fff 78%,transparent)">{p['flat_text']}</p>
        <ul>{flatli}</ul>
      </div>
      <div>
        <div class="prc">61 €<small>pro Person und Monat</small></div>
        <a class="btn btn-red" href="#" style="margin-top:26px">Alle Preise ansehen</a>
      </div>
    </div>
  </div>
</section>

<section class="sec warmbg" id="standorte">
  <div class="wrap">
    <div class="sechead">
      <div class="kicker r">Drei Häuser</div>
      <h2 class="h-display">Wo du <em>tanzt</em></h2>
      <p class="lead">Alle drei Standorte haben eigene Parkplätze direkt vor der Tür.</p>
    </div>
    <div class="grid g3">
{locs}    </div>
  </div>
</section>

<section class="sec" id="faq">
  <div class="wrap">
    <div class="sechead">
      <div class="kicker">Häufige Fragen</div>
      <h2 class="h-display">Noch <em>Fragen?</em></h2>
    </div>
    <div class="faq">
{faq}    </div>
  </div>
</section>

<section class="sec warmbg">
  <div class="wrap prose">
    <div class="kicker">{p['seo_kicker']}</div>
{seo}  </div>
</section>

<section class="endcta">
  <div class="wrap">
    <h2>{p['end_h']}</h2>
    <p class="lead">{p['end_lead']}</p>
    <a class="btn btn-red" href="#kurse">{p['end_btn']}</a>
  </div>
</section>

<footer>
  <div class="wrap">
    <a class="logo" href="#"><i></i><i></i>Bothe</a>
    <p style="max-width:34ch;margin-bottom:32px">Tanzschulen Familie Bothe — seit 1954 in dritter Generation in Hannover.</p>
    <div class="fgrid">
      <div><h4>Kurse</h4><ul>
        <li><a href="#">Discofox</a></li><li><a href="#">Hochzeitstanz</a></li>
        <li><a href="#">Salsa</a></li><li><a href="#">Standard &amp; Latein</a></li>
        <li><a href="#">West Coast Swing</a></li></ul></div>
      <div><h4>Häuser</h4><ul>
        <li><a href="#">Tanzhaus Hannover</a></li><li><a href="#">Tanzvilla Waldersee</a></li>
        <li><a href="#">Tanzhaus Burgwedel</a></li></ul></div>
      <div><h4>Service</h4><ul>
        <li><a href="#">Kursfinder</a></li><li><a href="#">Preise</a></li>
        <li><a href="#">Gutscheine</a></li><li><a href="#">Tanzpartnerbörse</a></li></ul></div>
      <div><h4>Kontakt</h4><ul>
        <li><a href="#">+49 511 66 37 66</a></li>
        <li><a href="#">tanzen@tanzschulen-bothe.de</a></li></ul></div>
    </div>
    <div class="fbot">
      <span>© 2026 Tanzschulen Familie Bothe</span>
      <span><a href="#">Impressum</a> · <a href="#">Datenschutz</a> · <a href="#">AGB</a></span>
    </div>
  </div>
</footer>

<script type="application/ld+json">
{json.dumps(schema, ensure_ascii=False, indent=1)}
</script>
"""


if __name__ == "__main__":
    out = pathlib.Path("/home/user/Tanzschule-Bothe/seiten")
    out.mkdir(exist_ok=True)
    for p in SEITEN:
        doc = build(p)
        (out / f"{p['slug']}.html").write_text(doc, encoding="utf-8")
        # Prüfung
        h1 = len(re.findall(r"<h1", doc))
        d = re.search(r'name="description" content="(.*?)"', doc).group(1)
        ld = re.findall(r"application/ld\+json[^>]*>(.*?)</script>", doc, re.S)
        json.loads(ld[0])
        ext = set(re.findall(r'(?:src|href)="(https?://[^"]+)"', doc))
        print(f"{p['slug']:<32} h1={h1} desc={len(d)} h2={len(re.findall(r'<h2', doc))} "
              f"schema=ok extern={len(ext)} {len(doc)/1024:.0f} kB")
