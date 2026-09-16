"""Beispieldatensatz fuer den Prototyp.

WICHTIG: Dies ist die einzige Datei mit Studieninhalten. Wer das Dashboard
mit eigenen Daten nutzen moechte, aendert nur hier etwas oder legt die Module
ueber die Oberflaeche neu an. Die Modulkuerzel der Semester 1 bis 4 stammen
aus dem Modulhandbuch des Studiengangs, die der Wahlpflichtmodule in den
Semestern 5 und 6 entsprechen einer vorlaeufigen Schwerpunktwahl.

Die Punktzahlen sind so gewaehlt, dass sich daraus die tatsaechlich erzielten
Noten ergeben; die Umrechnung uebernimmt ``Note.aus_punkten``.
"""

from __future__ import annotations

from datetime import date

from ..domain import (
    Fallstudie, Klausur, Modul, Modulstatus, Portfolio, Studiengang, Versuch,
)

STUDIENBEGINN = date(2024, 10, 1)

# (Semester, Kuerzel, Bezeichnung, ECTS, Pruefungsart, Termin(e), Punkte, begonnen_am)
_BESTANDEN: tuple[tuple, ...] = (
    (1, "DLBIBRVS", "Betriebssysteme, Rechnernetze und verteilte Systeme", 5, "klausur", date(2024, 12, 14), 87),
    (1, "DLBINGEDS", "Einfuehrung in Datenschutz und IT-Sicherheit", 5, "klausur", date(2024, 11, 16), 82),
    (1, "DLBDSIPWP_D", "Einfuehrung in die Programmierung mit Python", 5, "klausur", date(2024, 11, 30), 98),
    (1, "DLBWIR-01", "Einfuehrung in das wissenschaftliche Arbeiten", 5, "fallstudie", date(2025, 1, 20), 92),
    (1, "DLBBIMD", "Mathematik: Analysis", 5, "klausur", date(2025, 2, 15), 77),
    (1, "DLBDSSPDS_D", "Statistik: Wahrscheinlichkeit und deskriptive Statistik", 5, "klausur", date(2025, 3, 15), 82),

    (2, "DLBINGOPJ", "Grundlagen der objektorientierten Programmierung mit Java", 5, "klausur", date(2025, 5, 17), 86),
    (2, "DLBKA", "Kollaboratives Arbeiten", 5, "fallstudie", date(2025, 6, 10), 91),
    (2, "DLBCSEINF_D", "Einfuehrung in die Netzwerkforensik", 5, "klausur", date(2025, 7, 19), 83),
    (2, "IREN", "Requirements Engineering", 5, "klausur", date(2025, 8, 16), 88),
    (2, "DLBCSESPB_D", "Grundzuege des System-Pentestings", 5, "portfolio", date(2025, 9, 22), 93),
    (2, "DLBBIM", "Mathematik: Lineare Algebra", 5, "klausur", date(2025, 9, 13), 71),

    (3, "DLBIHK", "Interkulturelle und ethische Handlungskompetenzen", 5, "fallstudie", date(2025, 11, 10), 85),
    (3, "DLBINGEIT", "Einfuehrung in das Internet of Things", 5, "klausur", date(2025, 12, 13), 76),
    (3, "DLBIADPS", "Algorithmen, Datenstrukturen und Programmiersprachen", 5, "klausur", date(2026, 1, 24), 80),
    (3, "IPMG-01", "IT-Projektmanagement", 5, "klausur", date(2026, 2, 21), 89),
    (3, "DLBITIML", "Theoretische Informatik und Mathematische Logik", 5, "klausur", date(2026, 3, 14), 70),
    (3, "DLBCSEDCSW_D", "DevSecOps und gaengige Software-Schwachstellen", 5, "portfolio", date(2026, 3, 23), 90),

    (4, "IWSM1", "IT-Servicemanagement", 5, "klausur", date(2026, 5, 16), 82),
    (4, "DLBISIC2", "Kryptografische Verfahren", 5, "klausur", date(2026, 6, 20), 87),
    (4, "DLBIITR", "IT-Recht", 5, "klausur", date(2026, 7, 11), 78),
)

# (Semester, Kuerzel, Bezeichnung, ECTS, Art, Termin(e), begonnen_am)
_IN_BEARBEITUNG: tuple[tuple, ...] = (
    (4, "DLBCSEHSF_D", "Host- und Softwareforensik", 5, "klausur",
     date(2026, 9, 12), date(2026, 5, 14)),
    (4, "DLBDSOOFPP01_D", "Objektorientierte und funktionale Programmierung mit Python", 5, "portfolio",
     [date(2026, 8, 25), date(2026, 10, 6), date(2026, 11, 24)], date(2026, 7, 15)),
    (4, "DLBDSEAIS1_D", "Artificial Intelligence", 5, "klausur",
     date(2026, 10, 3), date(2026, 7, 28)),
    # Aus dem fuenften Semester vorgezogen. Genau dieser Vorgang war in der
    # Konzeptionsphase das Argument fuer eine Aggregation zwischen Semester
    # und Modul: Das Modul laesst sich ohne Datenverlust umhaengen.
    (4, "DLBCSEISS_D", "Standards der Informationssicherheit", 5, "fallstudie",
     date(2026, 9, 30), date(2026, 8, 6)),
)

# (Semester, Kuerzel, Bezeichnung, ECTS, Art, geplanter Termin)
_GEPLANT: tuple[tuple, ...] = (
    (5, "DLBCSECC_D", "Cloud Computing", 5, "klausur", date(2026, 12, 12)),
    (5, "DLBCSESE_D", "Social Engineering", 5, "fallstudie", date(2027, 1, 15)),
    (5, "DLBCSEITSB_D", "IT-Sicherheitsberatung", 5, "klausur", date(2027, 2, 13)),
    (5, "DLBCSESMS_D", "Sicherheit mobiler Systeme", 5, "klausur", date(2027, 3, 13)),
    (5, "DLBCSEPITS_D", "Projekt: IT-Sicherheitskonzept", 5, "portfolio", date(2027, 3, 29)),
    (6, "DLBCSEFT_D", "Future Threats", 5, "klausur", date(2027, 5, 15)),
    (6, "DLBCSECS_D", "Cloud Security", 5, "klausur", date(2027, 6, 12)),
    (6, "DLBCSESAT_D", "Seminar: Aktuelle Themen der Cyber Security", 5, "fallstudie", date(2027, 6, 28)),
    (6, "BBAK", "Bachelorarbeit", 12, "fallstudie", date(2027, 9, 10)),
    (6, "BBAK-01", "Kolloquium", 3, "fallstudie", date(2027, 9, 24)),
)


def _erzeuge_leistung(art: str, bezeichnung: str, termin):
    """Erzeugt die zur Art passende Pruefungsleistung."""
    if art == "klausur":
        return Klausur(f"Klausur {bezeichnung}", pruefungstermin=termin)
    if art == "fallstudie":
        return Fallstudie(f"Schriftliche Ausarbeitung {bezeichnung}", abgabefrist=termin)
    if art == "portfolio":
        fristen = termin if isinstance(termin, list) else [termin]
        return Portfolio(f"Portfolio {bezeichnung}", phasenfristen=fristen)
    raise ValueError(f"Unbekannte Pruefungsart: {art}")


def erzeuge_beispielstudiengang() -> Studiengang:
    """Baut den vollstaendigen Beispieldatensatz auf."""
    studiengang = Studiengang(
        bezeichnung="B.Sc. Cyber Security",
        abschluss="Bachelor of Science",
        gesamt_ects=180,
        regelstudienzeit_monate=36,
        studienbeginn=STUDIENBEGINN,
        anzahl_semester=6,
    )

    for nummer, kuerzel, bezeichnung, ects, art, termin, punkte in _BESTANDEN:
        modul = Modul(kuerzel, bezeichnung, ects, Modulstatus.BESTANDEN)
        leistung = _erzeuge_leistung(art, bezeichnung, termin)
        leistung.trage_versuch_ein(
            Versuch(nummer=1, datum=termin if not isinstance(termin, list) else termin[-1],
                    erreichte_punkte=punkte)
        )
        modul.verlange(leistung)
        studiengang.semester_mit_nummer(nummer).belege(modul)

    for nummer, kuerzel, bezeichnung, ects, art, termin, begonnen in _IN_BEARBEITUNG:
        modul = Modul(kuerzel, bezeichnung, ects, Modulstatus.IN_BEARBEITUNG, begonnen_am=begonnen)
        modul.verlange(_erzeuge_leistung(art, bezeichnung, termin))
        studiengang.semester_mit_nummer(nummer).belege(modul)

    for nummer, kuerzel, bezeichnung, ects, art, termin in _GEPLANT:
        modul = Modul(kuerzel, bezeichnung, ects, Modulstatus.OFFEN)
        modul.verlange(_erzeuge_leistung(art, bezeichnung, termin))
        studiengang.semester_mit_nummer(nummer).belege(modul)

    return studiengang
