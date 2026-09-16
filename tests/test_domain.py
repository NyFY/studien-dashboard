"""Tests der Fachklassen."""

from __future__ import annotations

import unittest
from dataclasses import FrozenInstanceError
from datetime import date

from studiendashboard.domain import (
    Fallstudie, Klausur, Modul, Modulstatus, Note, Portfolio, Semester,
    Studiengang, Versuch, addiere_monate,
)


class TestNote(unittest.TestCase):
    def test_gueltige_stufe_wird_angenommen(self) -> None:
        self.assertEqual(Note(1.7).wert, 1.7)

    def test_ungueltige_stufe_wird_abgelehnt(self) -> None:
        with self.assertRaises(ValueError):
            Note(1.5)

    def test_punkte_werden_richtig_umgerechnet(self) -> None:
        self.assertEqual(Note.aus_punkten(98), Note(1.0))
        self.assertEqual(Note.aus_punkten(87), Note(1.7))
        self.assertEqual(Note.aus_punkten(50), Note(4.0))
        self.assertEqual(Note.aus_punkten(49), Note(5.0))

    def test_punkte_ausserhalb_des_bereichs(self) -> None:
        with self.assertRaises(ValueError):
            Note.aus_punkten(120)

    def test_note_ist_unveraenderlich(self) -> None:
        note = Note(2.0)
        with self.assertRaises(FrozenInstanceError):
            note.wert = 1.0        # type: ignore[misc]

    def test_sortierung_und_darstellung(self) -> None:
        self.assertEqual(sorted([Note(2.3), Note(1.0)]), [Note(1.0), Note(2.3)])
        self.assertEqual(str(Note(1.7)), "1,7")

    def test_bestehensgrenze(self) -> None:
        self.assertTrue(Note(4.0).ist_bestanden)
        self.assertFalse(Note(5.0).ist_bestanden)


class TestVersuch(unittest.TestCase):
    def test_hoechstens_drei_versuche(self) -> None:
        with self.assertRaises(ValueError):
            Versuch(nummer=4, datum=date(2026, 1, 1), erreichte_punkte=80)

    def test_note_wird_abgeleitet(self) -> None:
        versuch = Versuch(nummer=1, datum=date(2026, 1, 1), erreichte_punkte=92)
        self.assertEqual(versuch.note, Note(1.3))
        self.assertTrue(versuch.ist_bestanden)


class TestPruefungsleistung(unittest.TestCase):
    def test_abstrakte_klasse_nicht_erzeugbar(self) -> None:
        from studiendashboard.domain import Pruefungsleistung

        with self.assertRaises(TypeError):
            Pruefungsleistung("Test")      # type: ignore[abstract]

    def test_klausur_liefert_termin_als_frist(self) -> None:
        klausur = Klausur("Klausur", pruefungstermin=date(2026, 9, 12))
        self.assertEqual(klausur.naechste_frist(date(2026, 8, 18)), date(2026, 9, 12))
        self.assertIsNone(klausur.naechste_frist(date(2026, 10, 1)))

    def test_portfolio_liefert_naechste_offene_phase(self) -> None:
        portfolio = Portfolio(
            "Portfolio",
            phasenfristen=[date(2026, 8, 25), date(2026, 10, 6), date(2026, 11, 24)],
        )
        self.assertEqual(portfolio.naechste_frist(date(2026, 8, 18)), date(2026, 8, 25))
        self.assertEqual(portfolio.naechste_frist(date(2026, 9, 1)), date(2026, 10, 6))
        self.assertEqual(portfolio.aktuelle_phase(date(2026, 9, 1)), 2)

    def test_polymorphie_ueber_die_oberklasse(self) -> None:
        stichtag = date(2026, 8, 18)
        leistungen = [
            Klausur("Klausur", date(2026, 9, 12)),
            Portfolio("Portfolio", [date(2026, 8, 25)]),
            Fallstudie("Fallstudie", date(2026, 9, 30)),
        ]
        fristen = [leistung.naechste_frist(stichtag) for leistung in leistungen]
        self.assertEqual(sorted(fristen)[0], date(2026, 8, 25))

    def test_bester_versuch_wird_gewaehlt(self) -> None:
        klausur = Klausur("Klausur", date(2026, 1, 10))
        klausur.trage_versuch_ein(Versuch(1, date(2026, 1, 10), 48))
        klausur.trage_versuch_ein(Versuch(2, date(2026, 3, 10), 84))
        self.assertEqual(klausur.bester_versuch.note, Note(2.0))
        self.assertTrue(klausur.ist_bestanden)

    def test_versuchsnummer_nur_einmal(self) -> None:
        klausur = Klausur("Klausur", date(2026, 1, 10))
        klausur.trage_versuch_ein(Versuch(1, date(2026, 1, 10), 80))
        with self.assertRaises(ValueError):
            klausur.trage_versuch_ein(Versuch(1, date(2026, 2, 10), 90))


class TestModul(unittest.TestCase):
    def _modul_mit_note(self, punkte: int) -> Modul:
        modul = Modul("TEST", "Testmodul", 5, Modulstatus.BESTANDEN)
        klausur = Klausur("Klausur", date(2026, 1, 10))
        klausur.trage_versuch_ein(Versuch(1, date(2026, 1, 10), punkte))
        modul.verlange(klausur)
        return modul

    def test_note_kommt_aus_der_pruefungsleistung(self) -> None:
        self.assertEqual(self._modul_mit_note(87).note, Note(1.7))

    def test_komposition_gibt_nur_lesende_sicht(self) -> None:
        modul = self._modul_mit_note(87)
        self.assertIsInstance(modul.pruefungsleistungen, tuple)
        with self.assertRaises(AttributeError):
            modul.pruefungsleistungen.append(None)     # type: ignore[attr-defined]

    def test_alter_offener_module(self) -> None:
        modul = Modul("TEST", "Testmodul", 5, Modulstatus.IN_BEARBEITUNG,
                      begonnen_am=date(2026, 5, 14))
        self.assertEqual(modul.offen_seit_tagen(date(2026, 8, 18)), 96)

    def test_bestandenes_modul_hat_kein_alter(self) -> None:
        self.assertIsNone(self._modul_mit_note(87).offen_seit_tagen(date(2026, 8, 18)))


class TestSemesterUndStudiengang(unittest.TestCase):
    def setUp(self) -> None:
        self.studiengang = Studiengang(
            "B.Sc. Test", "Bachelor of Science", 180, 36, date(2024, 10, 1)
        )

    def test_komposition_semester_wird_selbst_erzeugt(self) -> None:
        self.assertEqual(len(self.studiengang.semester), 6)
        self.assertIsInstance(self.studiengang.semester, tuple)

    def test_zieldatum_und_dauer(self) -> None:
        self.assertEqual(self.studiengang.zieldatum, date(2027, 9, 30))
        self.assertEqual(self.studiengang.tage_regelstudienzeit, 1094)

    def test_aggregation_modul_ueberlebt_das_semester(self) -> None:
        modul = Modul("TEST", "Testmodul", 5)
        semester = self.studiengang.semester_mit_nummer(4)
        semester.belege(modul)
        freigegeben = semester.gib_frei("TEST")
        self.assertIs(freigegeben, modul)
        self.assertEqual(freigegeben.kuerzel, "TEST")
        self.assertEqual(len(semester.module), 0)

    def test_modul_nicht_doppelt_belegbar(self) -> None:
        semester = self.studiengang.semester_mit_nummer(1)
        semester.belege(Modul("TEST", "Testmodul", 5))
        with self.assertRaises(ValueError):
            semester.belege(Modul("TEST", "Testmodul", 5))

    def test_addiere_monate_kuerzt_auf_monatsende(self) -> None:
        self.assertEqual(addiere_monate(date(2026, 1, 31), 1), date(2026, 2, 28))
        self.assertEqual(addiere_monate(date(2024, 10, 1), 36), date(2027, 10, 1))


if __name__ == "__main__":
    unittest.main()


class TestStichtagsbezug(unittest.TestCase):
    """Die Ist-Seite muss sich genauso am Stichtag orientieren wie die Sollseite.

    Diese Tests sind nach einem Review entstanden: Zuvor zaehlte
    ``erreichte_ects`` alle bestandenen Module, auch solche, die zum
    Stichtag noch gar nicht bestanden waren.
    """

    def setUp(self) -> None:
        self.studiengang = Studiengang("B.Sc. Test", "B.Sc.", 180, 36, date(2024, 10, 1))
        for kuerzel, tag in (("A", date(2025, 3, 1)), ("B", date(2026, 3, 1))):
            modul = Modul(kuerzel, f"Modul {kuerzel}", 5, Modulstatus.BESTANDEN)
            klausur = Klausur("Klausur", tag)
            klausur.trage_versuch_ein(Versuch(1, tag, 85))
            modul.verlange(klausur)
            self.studiengang.semester_mit_nummer(1).belege(modul)

    def test_ects_werden_am_stichtag_abgeschnitten(self) -> None:
        self.assertEqual(self.studiengang.erreichte_ects, 10)
        self.assertEqual(self.studiengang.erreichte_ects_bis(date(2025, 6, 1)), 5)
        self.assertEqual(self.studiengang.erreichte_ects_bis(date(2024, 12, 1)), 0)

    def test_offene_module_beruecksichtigen_den_startzeitpunkt(self) -> None:
        modul = Modul("C", "Modul C", 5, Modulstatus.IN_BEARBEITUNG,
                      begonnen_am=date(2026, 5, 14))
        self.studiengang.semester_mit_nummer(2).belege(modul)
        self.assertEqual(len(self.studiengang.offene_module_am(date(2026, 8, 18))), 1)
        self.assertEqual(len(self.studiengang.offene_module_am(date(2025, 6, 1))), 0)

    def test_kein_negatives_alter(self) -> None:
        modul = Modul("C", "Modul C", 5, Modulstatus.IN_BEARBEITUNG,
                      begonnen_am=date(2026, 5, 14))
        self.assertIsNone(modul.offen_seit_tagen(date(2025, 6, 1)))


class TestRobustheit(unittest.TestCase):
    def test_studiengang_prueft_seine_eckdaten(self) -> None:
        for ects, monate, semester in ((0, 36, 6), (180, 0, 6), (180, 36, 0)):
            with self.subTest(ects=ects, monate=monate, semester=semester):
                with self.assertRaises(ValueError):
                    Studiengang("Test", "B.Sc.", ects, monate, date(2024, 10, 1), semester)

    def test_versuch_prueft_die_punktzahl(self) -> None:
        for punkte in (-1, 101):
            with self.subTest(punkte=punkte):
                with self.assertRaises(ValueError):
                    Versuch(1, date(2026, 1, 1), punkte)

    def test_modul_ohne_bestandene_teilleistung_hat_keine_note(self) -> None:
        modul = Modul("TEST", "Testmodul", 5, Modulstatus.IN_BEARBEITUNG)
        klausur = Klausur("Klausur", date(2026, 1, 10))
        klausur.trage_versuch_ein(Versuch(1, date(2026, 1, 10), 30))
        modul.verlange(klausur)
        self.assertFalse(modul.ist_bestanden)
        self.assertIsNone(modul.note)

    def test_endfrist_ist_unabhaengig_vom_stichtag(self) -> None:
        portfolio = Portfolio("Portfolio", [date(2026, 8, 25), date(2026, 11, 24)])
        self.assertIsNone(portfolio.naechste_frist(date(2026, 12, 1)))
        self.assertEqual(portfolio.endfrist, date(2026, 11, 24))
