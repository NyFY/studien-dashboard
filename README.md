# Studien-Dashboard

Prototyp eines Dashboards zur Überwachung des eigenen Studienfortschritts.
Entstanden als Portfolio im Kurs **Objektorientierte und funktionale
Programmierung mit Python (DLBDSOOFPP01_D)** an der IU Internationalen
Hochschule.

Das Programm beantwortet drei Fragen auf einen Blick:

| Ziel | Kennzahl | Ampel |
|------|----------|-------|
| Abschluss in 36 Monaten | Abweichung der bestandenen ECTS vom Sollstand, dazu die Abschlussprognose | gruen ab -5 ECTS, gelb bis -15, rot darunter |
| Abschlussnote 2,0 oder besser | ECTS-gewichteter Durchschnitt und der Schnitt, den die Restmodule höchstens haben dürfen | grün bis 2,0, gelb bis 2,2, rot darüber |
| Höchstens drei Module gleichzeitig | Anzahl begonnener Module und Alter des ältesten | grün im Limit, gelb bei einem zu viel, rot ab zwei zu viel oder über 90 Tagen |

## Installation

Voraussetzung ist **Python 3.10 oder neuer**, unter Windows ab Windows 8.1.
Weitere Bibliotheken werden nicht benötigt, alles kommt aus der
Standardbibliothek.

```bash
git clone https://github.com/NyFY/studien-dashboard.git
cd studien-dashboard
python main.py
```

Unter Windows genügt alternativ ein Doppelklick auf `start_windows.bat`.

Beim ersten Start legt das Programm die Datei `daten/studium.db` an und füllt
sie mit einem Beispieldatensatz.

## Aufruf

```bash
python main.py                          # Fenster, Stichtag ist heute
python main.py --konsole                # Ausgabe auf der Kommandozeile
python main.py --stichtag 2026-08-18    # fester Bewertungsstichtag
python main.py --im-speicher            # ohne Datenbankdatei, nichts wird gespeichert
python main.py --zuruecksetzen          # Beispieldaten neu anlegen
python main.py --zielnote 1.7 --wip-grenze 2   # überschreibt die gespeicherten Ziele
python main.py -h                       # alle Schalter
```

Alternativ: `python -m studiendashboard`

## Tests

```bash
python -m unittest discover -s tests -t .
```

80 Tests, Laufzeit unter einer Sekunde. Sie prüfen unter anderem, ob der
Rundlauf durch die Datenbank alle Daten erhält und ob die Ampeln an den
Schwellenwerten richtig umschlagen.

## Datengrundlage

Der Prototyp läuft mit einem **Beispieldatensatz**, der den Aufbau des
Studiengangs B.Sc. Cyber Security nachbildet (180 ECTS, sechs Semester,
Studienbeginn 01.10.2024). Er dient als Testgrundlage und ist kein Auszug aus
myCampus.

## Eigene Daten verwenden

Alle Studieninhalte stehen in einer einzigen Datei:
`studiendashboard/repository/demodaten.py`. Dort die Module, Kürzel, ECTS,
Termine und Punktzahlen ersetzen und anschließend `python main.py
--zuruecksetzen` aufrufen.

Die drei Studienziele liegen in der Tabelle `studienziel` der Datenbank und
lassen sich dort ändern, ohne den Code anzufassen.

## Aufbau

Der Code folgt einem Schichtenmodell. Jede Schicht kennt nur die Schicht
unter sich, nie umgekehrt.

```
studiendashboard/
  app.py            Composition Root: erzeugt und verdrahtet alle Objekte
  controller/       stellt aus Repository, Services und Zielen die Anzeigedaten zusammen
  view/             zwei austauschbare Ansichten (tkinter und Konsole) plus Bausteine
  dto/              Datentransportobjekte samt Ergebnisklassen Zielbewertung und Ampel
  ziele/            Studienziele und ihre Bewertungsregeln
  service/          fachliche Berechnungen ueber mehrere Objekte hinweg
  repository/       Speicherung (SQLite und Arbeitsspeicher) sowie Beispieldaten
  domain/           Fachklassen: Studiengang, Semester, Modul, Pruefungsleistung, Versuch, Note
tests/              80 Tests mit unittest
```

Umgesetzte objektorientierte Konzepte:

- **Vererbung und Abstraktion**: `Pruefungsleistung` ist abstrakt, `Klausur`,
  `Portfolio` und `Fallstudie` beantworten `naechste_frist()` unterschiedlich.
  Dasselbe Muster tragen `Studienziel`, `StudiengangRepository` und `DashboardView`.
- **Komposition**: `Studiengang` erzeugt seine `Semester` selbst und gibt sie
  nur als Tupel heraus. In der Datenbank sorgt `ON DELETE CASCADE` dafür, dass
  mit einem Modul auch seine Prüfungsleistungen und Versuche verschwinden.
- **Aggregation**: Ein `Modul` wird einem `Semester` übergeben und überlebt es.
  `Semester.gib_frei()` gibt das Modul unversehrt zurück.
- **Kapselung**: Abgeleitete Attribute des Klassendiagramms sind Properties
  ohne Setter, etwa `Studiengang.erreichte_ects` oder `Modul.note`.
- **Abhängigkeitsrichtung**: Die Pakete kennen sich nur in eine Richtung.
  Deshalb liegen `Zielbewertung` und `Ampel` in `dto` und nicht in `ziele`,
  denn beide Schichten brauchen sie.
- **Unveränderlichkeit**: `Note` und `Versuch` sind eingefrorene Dataclasses.
  `Note` prüft beim Erzeugen, ob der Wert eine zulässige Notenstufe ist.
- **Polymorphie**: Der Controller ruft `bewerte()` auf allen Zielen auf, ohne
  ihre Typen zu kennen. Ein viertes Ziel ist eine neue Unterklasse.

## Lizenz

MIT, siehe [LICENSE](LICENSE).
