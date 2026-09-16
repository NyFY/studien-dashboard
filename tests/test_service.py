"""Tests der fachlichen Berechnungen."""

from __future__ import annotations

import unittest
from datetime import date

from studiendashboard.repository import erzeuge_beispielstudiengang
from studiendashboard.service import FortschrittsService, NotenService

STICHTAG = date(2026, 9, 16)


class TestFortschrittsService(unittest.TestCase):
    def setUp(self) -> None:
        self.studiengang = erzeuge_beispielstudiengang()
        self.service = FortschrittsService()

    def test_beispieldatensatz_ist_stimmig(self) -> None:
        self.assertEqual(self.studiengang.erreichte_ects, 75)
        self.assertEqual(sum(m.ects for m in self.studiengang.module), 180)
        self.assertEqual(len(self.studiengang.offene_module), 4)
        self.assertEqual(self.studiengang.geplante_dauer_monate, 48)

    def test_sollstand_am_stichtag(self) -> None:
        self.assertAlmostEqual(
            self.service.soll_ects(self.studiengang, STICHTAG), 88.2, places=1
        )

    def test_sollstand_am_studienbeginn_ist_null(self) -> None:
        self.assertEqual(
            self.service.soll_ects(self.studiengang, self.studiengang.studienbeginn), 0.0
        )

    def test_sollstand_wird_bei_180_gedeckelt(self) -> None:
        self.assertEqual(
            self.service.soll_ects(self.studiengang, date(2030, 1, 1)), 180.0
        )

    def test_prognose_und_verzug(self) -> None:
        self.assertEqual(self.service.prognose(self.studiengang, STICHTAG), date(2029, 6, 13))
        self.assertEqual(self.service.tage_verzug(self.studiengang, STICHTAG), 256)

    def test_ohne_bestandene_module_keine_prognose(self) -> None:
        from studiendashboard.domain import Studiengang

        leer = Studiengang("Test", "B.Sc.", 180, 48, date(2024, 10, 1))
        self.assertIsNone(self.service.prognose(leer, STICHTAG))

    def test_verlauf_steigt_monoton(self) -> None:
        verlauf = self.service.verlauf(self.studiengang, STICHTAG)
        werte = [punkt.ects for punkt in verlauf]
        self.assertEqual(werte, sorted(werte))
        self.assertEqual(werte[0], 0)
        self.assertEqual(werte[-1], 75)


class TestNotenService(unittest.TestCase):
    def setUp(self) -> None:
        self.studiengang = erzeuge_beispielstudiengang()
        self.service = NotenService()

    def test_gewichteter_durchschnitt(self) -> None:
        self.assertAlmostEqual(self.service.durchschnitt(self.studiengang), 1.80, places=4)

    def test_benoetigter_restschnitt(self) -> None:
        rest = self.service.benoetigter_restschnitt(self.studiengang, zielnote=2.0)
        self.assertAlmostEqual(rest, 2.14, places=2)

    def test_restschnitt_haelt_die_gleichung_ein(self) -> None:
        """Gegenprobe: Mit dem errechneten Schnitt kommt genau die Zielnote heraus."""
        rest = self.service.benoetigter_restschnitt(self.studiengang, zielnote=2.0)
        erreicht = self.studiengang.erreichte_ects
        gesamt = self.studiengang.gesamt_ects
        schnitt = self.service.durchschnitt(self.studiengang)
        ergebnis = (erreicht * schnitt + (gesamt - erreicht) * rest) / gesamt
        self.assertAlmostEqual(ergebnis, 2.0, places=6)

    def test_verteilung_zaehlt_alle_bewerteten_module(self) -> None:
        verteilung = self.service.verteilung(self.studiengang)
        self.assertEqual(sum(anzahl for _, anzahl in verteilung), 15)
        self.assertEqual(dict(verteilung)["1,4-1,7"], 4)

    def test_gueltige_notenstufen(self) -> None:
        self.assertTrue(NotenService.ist_gueltige_note(2.3))
        self.assertFalse(NotenService.ist_gueltige_note(2.4))


if __name__ == "__main__":
    unittest.main()


class TestRandfaelle(unittest.TestCase):
    """Randfaelle, die ein Review aufgedeckt hat."""

    def setUp(self) -> None:
        self.studiengang = erzeuge_beispielstudiengang()
        self.fortschritt = FortschrittsService()
        self.noten = NotenService()

    def test_prognose_stuerzt_bei_fernem_stichtag_nicht_ab(self) -> None:
        self.assertIsNone(self.fortschritt.prognose(self.studiengang, date(9999, 12, 31)))

    def test_verlauf_laeuft_zeitlich_nicht_rueckwaerts(self) -> None:
        for stichtag in (date(2025, 6, 1), STICHTAG, date(2027, 12, 1)):
            with self.subTest(stichtag=stichtag):
                tage = [punkt.tag for punkt in self.fortschritt.verlauf(self.studiengang, stichtag)]
                self.assertEqual(tage, sorted(tage))

    def test_ist_ects_folgen_dem_stichtag(self) -> None:
        self.assertEqual(self.fortschritt.ist_ects(self.studiengang, date(2025, 6, 1)), 30)
        self.assertEqual(self.fortschritt.ist_ects(self.studiengang, STICHTAG), 75)

    def test_notenband_wird_richtig_zugeordnet(self) -> None:
        self.assertEqual(NotenService.band_index(1.0), 0)
        self.assertEqual(NotenService.band_index(1.80), 2)
        self.assertEqual(NotenService.band_index(4.0), 5)
        self.assertEqual(NotenService.band_index(None), -1)
