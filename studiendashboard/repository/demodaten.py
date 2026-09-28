"""Beispieldatensatz fuer den Prototyp.

WICHTIG: Dies ist die einzige Datei mit Studieninhalten. Wer das Dashboard
mit eigenen Daten nutzen moechte, aendert nur hier etwas. Die Modulkuerzel der Semester 1 bis 4 stammen
aus dem Modulhandbuch des Studiengangs, die der Wahlpflichtmodule in den
Semestern 5 und 6 entsprechen einer vorlaeufigen Schwerpunktwahl.

Der Datensatz bildet das Zeitmodell Teilzeit I ab: 180 ECTS in 48 Monaten,
sechs Lehrplansemester zu je acht Monaten. Die Punktzahlen sind so gewaehlt,
dass sich daraus die ausgewiesenen Noten ergeben; die Umrechnung uebernimmt
``Note.aus_punkten``.
"""

from __future__ import annotations

from datetime import date

from ..domain import (
    Abschluss, Fallstudie, Klausur, Modul, Modulstatus, Portfolio, Studiengang,
    Versuch,
)

STUDIENBEGINN = date(2024, 10, 1)
GEPLANTE_DAUER_MONATE = 48

# (Semester, Kuerzel, Bezeichnung, ECTS, Pruefungsart, Termin, Punkte)
_BESTANDEN: tuple[tuple, ...] = (
    # Erstes Semester, Oktober 2024 bis Juni 2025
    (1, "DLBIBRVS", "Betriebssysteme, Rechnernetze und verteilte Systeme", 5, "klausur", date(2024, 11, 16), 87),
    (1, "DLBINGEDS", "Einführung in Datenschutz und IT-Sicherheit", 5, "klausur", date(2024, 12, 14), 82),
    (1, "DLBDSIPWP_D", "Einführung in die Programmierung mit Python", 5, "klausur", date(2025, 1, 18), 98),
    (1, "DLBWIR-01", "Einführung in das wissenschaftliche Arbeiten", 5, "fallstudie", date(2025, 2, 20), 92),
    (1, "DLBBIMD", "Mathematik: Analysis", 5, "klausur", date(2025, 3, 15), 77),
    (1, "DLBDSSPDS_D", "Statistik: Wahrscheinlichkeit und deskriptive Statistik", 5, "klausur", date(2025, 5, 17), 82),

    # Zweites Semester, Juni 2025 bis Februar 2026
    (2, "DLBINGOPJ", "Grundlagen der objektorientierten Programmierung mit Java", 5, "klausur", date(2025, 6, 21), 86),
    (2, "DLBKA", "Kollaboratives Arbeiten", 5, "fallstudie", date(2025, 8, 12), 91),
    (2, "DLBCSEINF_D", "Einführung in die Netzwerkforensik", 5, "klausur", date(2025, 9, 20), 83),
    (2, "IREN", "Requirements Engineering", 5, "klausur", date(2025, 10, 18), 88),
    (2, "DLBCSESPB_D", "Grundzüge des System-Pentestings", 5, "portfolio", date(2025, 11, 24), 93),
    (2, "DLBBIM", "Mathematik: Lineare Algebra", 5, "klausur", date(2026, 1, 17), 71),

    # Drittes Semester, Februar bis Oktober 2026, laeuft noch
    (3, "DLBIHK", "Interkulturelle und ethische Handlungskompetenzen", 5, "fallstudie", date(2026, 2, 16), 85),
    (3, "DLBINGEIT", "Einführung in das Internet of Things", 5, "klausur", date(2026, 4, 18), 76),
    (3, "DLBIADPS", "Algorithmen, Datenstrukturen und Programmiersprachen", 5, "klausur", date(2026, 6, 20), 80),
)

# (Semester, Kuerzel, Bezeichnung, ECTS, Art, Termin(e), begonnen_am)
_IN_BEARBEITUNG: tuple[tuple, ...] = (
    (3, "DLBITIML", "Theoretische Informatik und Mathematische Logik", 5, "klausur",
     date(2026, 10, 10), date(2026, 6, 12)),
    # Aus dem vierten Semester vorgezogen. Genau dieser Vorgang war in der
    # Konzeptionsphase das Argument fuer eine Aggregation zwischen Semester
    # und Modul: Das Modul laesst sich ohne Datenverlust umhaengen.
    (3, "DLBDSOOFPP01_D", "Objektorientierte und funktionale Programmierung mit Python", 5, "portfolio",
     [date(2026, 9, 22), date(2026, 11, 3), date(2026, 12, 15)], date(2026, 7, 22)),
    (3, "IPMG-01", "IT-Projektmanagement", 5, "klausur",
     date(2026, 11, 14), date(2026, 8, 13)),
    (3, "DLBCSEDCSW_D", "DevSecOps und gängige Software-Schwachstellen", 5, "portfolio",
     [date(2026, 10, 20), date(2026, 12, 1), date(2027, 1, 19)], date(2026, 9, 4)),
)

# (Semester, Kuerzel, Bezeichnung, ECTS, Art, geplanter Termin)
_GEPLANT: tuple[tuple, ...] = (
    (4, "IWSM1", "IT-Servicemanagement", 5, "klausur", date(2026, 12, 12)),
    (4, "DLBISIC2", "Kryptografische Verfahren", 5, "klausur", date(2027, 1, 16)),
    (4, "DLBIITR", "IT-Recht", 5, "klausur", date(2027, 2, 20)),
    (4, "DLBCSEHSF_D", "Host- und Softwareforensik", 5, "klausur", date(2027, 3, 20)),
    (4, "DLBDSEAIS1_D", "Artificial Intelligence", 5, "klausur", date(2027, 5, 15)),

    (5, "DLBCSEISS_D", "Standards der Informationssicherheit", 5, "fallstudie", date(2027, 6, 19)),
    (5, "DLBCSECC_D", "Cloud Computing", 5, "klausur", date(2027, 8, 14)),
    (5, "DLBCSESE_D", "Social Engineering", 5, "fallstudie", date(2027, 9, 18)),
    (5, "DLBCSEITSB_D", "IT-Sicherheitsberatung", 5, "klausur", date(2027, 10, 16)),
    (5, "DLBCSESMS_D", "Sicherheit mobiler Systeme", 5, "klausur", date(2027, 11, 20)),
    (5, "DLBCSEPITS_D", "Projekt: IT-Sicherheitskonzept", 5, "portfolio", date(2028, 1, 15)),

    (6, "DLBCSEFT_D", "Future Threats", 5, "klausur", date(2028, 3, 18)),
    (6, "DLBCSECS_D", "Cloud Security", 5, "klausur", date(2028, 4, 15)),
    (6, "DLBCSESAT_D", "Seminar: Aktuelle Themen der Cyber Security", 5, "fallstudie", date(2028, 5, 20)),
    (6, "BBAK", "Bachelorarbeit", 12, "fallstudie", date(2028, 8, 25)),
    (6, "BBAK-01", "Kolloquium", 3, "fallstudie", date(2028, 9, 15)),
)


def _erzeuge_leistung(art: str, termin):
    """Erzeugt die zur Art passende Pruefungsleistung."""
    if art == "klausur":
        return Klausur(pruefungstermin=termin)
    if art == "fallstudie":
        return Fallstudie(abgabefrist=termin)
    if art == "portfolio":
        fristen = termin if isinstance(termin, list) else [termin]
        return Portfolio(phasenfristen=fristen)
    raise ValueError(f"Unbekannte Pruefungsart: {art}")


def erzeuge_beispielstudiengang() -> Studiengang:
    """Baut den vollstaendigen Beispieldatensatz auf."""
    studiengang = Studiengang(
        bezeichnung="B.Sc. Cyber Security",
        abschluss=Abschluss.BACHELOR_OF_SCIENCE,
        gesamt_ects=180,
        geplante_dauer_monate=GEPLANTE_DAUER_MONATE,
        studienbeginn=STUDIENBEGINN,
        anzahl_semester=6,
    )

    for nummer, kuerzel, bezeichnung, ects, art, termin, punkte in _BESTANDEN:
        modul = Modul(kuerzel, bezeichnung, ects, Modulstatus.BESTANDEN)
        leistung = _erzeuge_leistung(art, termin)
        leistung.trage_versuch_ein(Versuch(nummer=1, datum=termin, erreichte_punkte=punkte))
        modul.verlange(leistung)
        studiengang.semester_mit_nummer(nummer).belege(modul)

    for nummer, kuerzel, bezeichnung, ects, art, termin, begonnen in _IN_BEARBEITUNG:
        modul = Modul(kuerzel, bezeichnung, ects, Modulstatus.IN_BEARBEITUNG, begonnen_am=begonnen)
        modul.verlange(_erzeuge_leistung(art, termin))
        studiengang.semester_mit_nummer(nummer).belege(modul)

    for nummer, kuerzel, bezeichnung, ects, art, termin in _GEPLANT:
        modul = Modul(kuerzel, bezeichnung, ects, Modulstatus.OFFEN)
        modul.verlange(_erzeuge_leistung(art, termin))
        studiengang.semester_mit_nummer(nummer).belege(modul)

    return studiengang
