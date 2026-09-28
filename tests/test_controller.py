"""Tests der Ablaufsteuerung und des Zusammenspiels der Schichten."""

from __future__ import annotations

import unittest
from datetime import date

from studiendashboard.controller import DashboardController
from studiendashboard.repository import (
    SpeicherStudiengangRepository, erzeuge_beispielstudiengang,
)
from studiendashboard.service import FortschrittsService, NotenService
from studiendashboard.view import KonsolenView
from studiendashboard.ziele import Ampel, Notenziel, WipZiel, Zeitziel

STICHTAG = date(2026, 9, 16)


class TestDashboardController(unittest.TestCase):
    def setUp(self) -> None:
        self.controller = DashboardController(
            repository=SpeicherStudiengangRepository(erzeuge_beispielstudiengang()),
            fortschritts_service=FortschrittsService(),
            noten_service=NotenService(),
            ziele=[Zeitziel(), Notenziel(), WipZiel()],
        )
        self.daten = self.controller.lade_dashboard_daten(STICHTAG)

    def test_kennzahlen_stimmen(self) -> None:
        kennzahlen = self.daten.kennzahlen
        self.assertEqual(kennzahlen.ects_ist, 75)
        self.assertAlmostEqual(kennzahlen.ects_soll, 88.2, places=1)
        self.assertEqual(kennzahlen.offene_module, 4)
        self.assertEqual(kennzahlen.aeltestes_modul_tage, 96)
        self.assertEqual(kennzahlen.aeltestes_modul_kuerzel, "DLBITIML")

    def test_drei_bewertungen_in_der_richtigen_reihenfolge(self) -> None:
        ampeln = [bewertung.ampel for bewertung in self.daten.bewertungen]
        self.assertEqual(ampeln, [Ampel.GELB, Ampel.GRUEN, Ampel.ROT])

    def test_modultabelle_beginnt_mit_dem_aeltesten(self) -> None:
        zeilen = self.daten.offene_module
        self.assertEqual(len(zeilen), 4)
        self.assertEqual(zeilen[0].kuerzel, "DLBITIML")
        self.assertEqual(zeilen[0].ampel, "rot")
        self.assertEqual(zeilen[-1].ampel, "gruen")

    def test_fristen_werden_je_pruefungsart_gebildet(self) -> None:
        fristen = {zeile.kuerzel: zeile.naechste_frist for zeile in self.daten.offene_module}
        self.assertEqual(fristen["DLBITIML"], "Klausur 10.10.2026")
        self.assertEqual(fristen["DLBDSOOFPP01_D"], "Portfolio 22.09.2026")
        self.assertEqual(fristen["IPMG-01"], "Klausur 14.11.2026")

    def test_deaktiviertes_ziel_wird_uebersprungen(self) -> None:
        ziele = [Zeitziel(), Notenziel(), WipZiel()]
        ziele[1].ist_aktiv = False
        controller = DashboardController(
            repository=SpeicherStudiengangRepository(erzeuge_beispielstudiengang()),
            fortschritts_service=FortschrittsService(),
            noten_service=NotenService(),
            ziele=ziele,
        )
        self.assertEqual(len(controller.lade_dashboard_daten(STICHTAG).bewertungen), 2)

    def test_konsolenansicht_laeuft_durch(self) -> None:
        """Die Ansicht darf keine Berechnung mehr brauchen."""
        import io
        from contextlib import redirect_stdout

        puffer = io.StringIO()
        with redirect_stdout(puffer):
            KonsolenView().zeige(self.daten)
        ausgabe = puffer.getvalue()
        self.assertIn("STUDIEN-DASHBOARD", ausgabe)
        self.assertIn("DLBITIML", ausgabe)
        self.assertIn("75 von 180 ECTS", ausgabe)


if __name__ == "__main__":
    unittest.main()


class TestKonsolenausgabe(unittest.TestCase):
    """Die Konsolenfassung muss auf jeder westlichen Windows-Codepage laufen."""

    def test_ausgabe_ist_in_cp850_darstellbar(self) -> None:
        import io
        from contextlib import redirect_stdout

        daten = DashboardController(
            repository=SpeicherStudiengangRepository(erzeuge_beispielstudiengang()),
            fortschritts_service=FortschrittsService(),
            noten_service=NotenService(),
            ziele=[Zeitziel(), Notenziel(), WipZiel()],
        ).lade_dashboard_daten(STICHTAG)

        puffer = io.StringIO()
        with redirect_stdout(puffer):
            KonsolenView().zeige(daten)
        ausgabe = puffer.getvalue()

        for codepage in ("cp850", "cp1252", "cp437"):
            with self.subTest(codepage=codepage):
                try:
                    ausgabe.encode(codepage)
                except UnicodeEncodeError as fehler:
                    self.fail(f"{codepage} kann {fehler.object[fehler.start:fehler.end]!r} nicht")

    def test_umlaute_bleiben_erhalten(self) -> None:
        """Umlaute sind erlaubt, weil jede westliche Codepage sie kennt."""
        self.assertIn("ä".encode("cp850").decode("cp850"), "ä")


class TestFristdarstellung(unittest.TestCase):
    """Die Frist muss zur angezeigten Pruefungsart gehoeren."""

    def _daten(self, stichtag: date):
        return DashboardController(
            repository=SpeicherStudiengangRepository(erzeuge_beispielstudiengang()),
            fortschritts_service=FortschrittsService(),
            noten_service=NotenService(),
            ziele=[Zeitziel(), Notenziel(), WipZiel()],
        ).lade_dashboard_daten(stichtag)

    def test_verstrichene_frist_wird_als_solche_benannt(self) -> None:
        zeilen = {z.kuerzel: z.naechste_frist for z in self._daten(date(2027, 3, 1)).offene_module}
        self.assertEqual(zeilen["DLBITIML"], "Klausur 10.10.2026 verstrichen")
        self.assertNotIn("kein Termin hinterlegt", zeilen.values())

    def test_art_und_datum_gehoeren_zusammen(self) -> None:
        from studiendashboard.domain import Klausur, Modul, Modulstatus, Portfolio

        studiengang = erzeuge_beispielstudiengang()
        modul = Modul("MEHR-01", "Modul mit zwei Leistungen", 5,
                      Modulstatus.IN_BEARBEITUNG, begonnen_am=date(2026, 6, 1))
        modul.verlange(Klausur(date(2026, 12, 1), gewichtung=0.5))
        modul.verlange(Portfolio([date(2026, 10, 1)], gewichtung=0.5))
        studiengang.semester_mit_nummer(5).belege(modul)

        daten = DashboardController(
            repository=SpeicherStudiengangRepository(studiengang),
            fortschritts_service=FortschrittsService(),
            noten_service=NotenService(),
            ziele=[Zeitziel()],
        ).lade_dashboard_daten(date(2026, 8, 18))

        zeile = next(z for z in daten.offene_module if z.kuerzel == "MEHR-01")
        self.assertEqual(zeile.naechste_frist, "Portfolio 01.10.2026")

    def test_stichtag_vor_studienbeginn_bleibt_widerspruchsfrei(self) -> None:
        daten = self._daten(date(2024, 10, 15))
        self.assertEqual(daten.kennzahlen.ects_ist, 0)
        self.assertEqual(daten.kennzahlen.offene_module, 0)
        self.assertEqual(daten.offene_module, ())
