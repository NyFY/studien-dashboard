"""Tests der Speicherung.

Der wichtigste Test ist der Rundlauf: schreiben, Verbindung schliessen,
neu oeffnen, lesen. Nur wenn das Objektgeflecht danach unveraendert ist,
funktioniert die Persistenz wirklich.
"""

from __future__ import annotations

import sqlite3
import tempfile
import unittest
from datetime import date
from pathlib import Path

from studiendashboard.domain import Klausur, Modul, Modulstatus, Versuch
from studiendashboard.repository import (
    SQLiteStudiengangRepository, SpeicherStudiengangRepository,
    erzeuge_beispielstudiengang,
)


class TestSpeicherRepository(unittest.TestCase):
    def test_leeres_repository_meldet_sich(self) -> None:
        repository = SpeicherStudiengangRepository()
        self.assertTrue(repository.ist_leer())
        with self.assertRaises(LookupError):
            repository.lade()

    def test_speichern_und_laden(self) -> None:
        repository = SpeicherStudiengangRepository()
        repository.speichere(erzeuge_beispielstudiengang())
        self.assertFalse(repository.ist_leer())
        self.assertEqual(repository.lade().erreichte_ects, 75)


class TestSQLiteRepository(unittest.TestCase):
    def setUp(self) -> None:
        self._ordner = tempfile.TemporaryDirectory()
        self.pfad = Path(self._ordner.name) / "test.db"

    def tearDown(self) -> None:
        self._ordner.cleanup()

    def test_rundlauf_erhaelt_alle_daten(self) -> None:
        original = erzeuge_beispielstudiengang()
        SQLiteStudiengangRepository(self.pfad).speichere(original)

        # Bewusst ein neues Objekt auf derselben Datei, damit nichts aus dem
        # Arbeitsspeicher stammen kann.
        geladen = SQLiteStudiengangRepository(self.pfad).lade()

        self.assertEqual(geladen.bezeichnung, original.bezeichnung)
        self.assertEqual(geladen.studienbeginn, original.studienbeginn)
        self.assertEqual(len(geladen.module), len(original.module))
        self.assertEqual(geladen.erreichte_ects, original.erreichte_ects)
        self.assertEqual(geladen.notendurchschnitt, original.notendurchschnitt)

    def test_pruefungsarten_bleiben_erhalten(self) -> None:
        SQLiteStudiengangRepository(self.pfad).speichere(erzeuge_beispielstudiengang())
        geladen = SQLiteStudiengangRepository(self.pfad).lade()

        arten = {
            leistung.art()
            for modul in geladen.module
            for leistung in modul.pruefungsleistungen
        }
        self.assertEqual(arten, {"Klausur", "Portfolio", "Fallstudie"})

    def test_portfolio_phasenfristen_bleiben_erhalten(self) -> None:
        SQLiteStudiengangRepository(self.pfad).speichere(erzeuge_beispielstudiengang())
        geladen = SQLiteStudiengangRepository(self.pfad).lade()

        portfolio = next(
            leistung
            for modul in geladen.module
            if modul.kuerzel == "DLBDSOOFPP01_D"
            for leistung in modul.pruefungsleistungen
        )
        self.assertEqual(portfolio.anzahl_phasen, 3)
        self.assertEqual(portfolio.naechste_frist(date(2026, 9, 16)), date(2026, 9, 22))

    def test_komposition_wird_in_der_datenbank_durchgesetzt(self) -> None:
        """Mit dem Modul verschwinden Pruefungsleistung und Versuch (ON DELETE CASCADE)."""
        repository = SQLiteStudiengangRepository(self.pfad)
        repository.speichere(erzeuge_beispielstudiengang())

        with sqlite3.connect(self.pfad) as verbindung:
            verbindung.execute("PRAGMA foreign_keys = ON")
            (vorher,) = verbindung.execute("SELECT COUNT(*) FROM versuch").fetchone()
            verbindung.execute("DELETE FROM modul WHERE kuerzel = 'DLBIBRVS'")
            (nachher,) = verbindung.execute("SELECT COUNT(*) FROM versuch").fetchone()
            (leistungen,) = verbindung.execute(
                "SELECT COUNT(*) FROM pruefungsleistung WHERE modul_kuerzel = 'DLBIBRVS'"
            ).fetchone()

        self.assertEqual(vorher - nachher, 1)
        self.assertEqual(leistungen, 0)

    def test_leere_datenbank_meldet_sich(self) -> None:
        repository = SQLiteStudiengangRepository(self.pfad)
        self.assertTrue(repository.ist_leer())
        with self.assertRaises(LookupError):
            repository.lade()

    def test_erneutes_speichern_verdoppelt_nichts(self) -> None:
        repository = SQLiteStudiengangRepository(self.pfad)
        studiengang = erzeuge_beispielstudiengang()
        repository.speichere(studiengang)
        repository.speichere(studiengang)
        self.assertEqual(len(repository.lade().module), len(studiengang.module))

    def test_neues_modul_wird_mitgespeichert(self) -> None:
        repository = SQLiteStudiengangRepository(self.pfad)
        studiengang = erzeuge_beispielstudiengang()

        modul = Modul("NEU-01", "Zusatzmodul", 5, Modulstatus.BESTANDEN)
        klausur = Klausur("Klausur Zusatzmodul", date(2026, 4, 4))
        klausur.trage_versuch_ein(Versuch(1, date(2026, 4, 4), 95))
        modul.verlange(klausur)
        studiengang.semester_mit_nummer(3).belege(modul)

        repository.speichere(studiengang)
        geladen = SQLiteStudiengangRepository(self.pfad).lade()
        kuerzel = {m.kuerzel for m in geladen.module}
        self.assertIn("NEU-01", kuerzel)
        self.assertEqual(geladen.erreichte_ects, 80)


class TestZielpersistenz(unittest.TestCase):
    """Die Studienziele werden mitgespeichert und kommen als Unterklasse zurueck."""

    def setUp(self) -> None:
        self._ordner = tempfile.TemporaryDirectory()
        self.pfad = Path(self._ordner.name) / "ziele.db"

    def tearDown(self) -> None:
        self._ordner.cleanup()

    def test_rundlauf_der_ziele(self) -> None:
        from studiendashboard.ziele import Notenziel, WipZiel, Zeitziel, standardziele

        repository = SQLiteStudiengangRepository(self.pfad)
        self.assertEqual(repository.lade_ziele(), [])

        repository.speichere_ziele(standardziele(48))
        geladen = SQLiteStudiengangRepository(self.pfad).lade_ziele()

        self.assertEqual([type(z) for z in geladen], [Zeitziel, Notenziel, WipZiel])
        self.assertEqual(geladen[0].zielmonate, 48)
        self.assertEqual(geladen[1].zielnote, 2.0)
        self.assertEqual(geladen[2].hoechstzahl, 3)
        self.assertEqual(geladen[2].hoechstalter_tage, 90)

    def test_geaenderter_zielwert_bleibt_erhalten(self) -> None:
        from studiendashboard.ziele import Notenziel

        repository = SQLiteStudiengangRepository(self.pfad)
        repository.speichere_ziele([Notenziel(zielnote=1.7)])
        geladen = SQLiteStudiengangRepository(self.pfad).lade_ziele()
        self.assertEqual(geladen[0].zielnote, 1.7)
        self.assertEqual(geladen[0].titel, "Abschlussnote 1,7 oder besser")

    def test_deaktiviertes_ziel_bleibt_deaktiviert(self) -> None:
        from studiendashboard.ziele import standardziele

        ziele = standardziele(48)
        ziele[1].ist_aktiv = False
        repository = SQLiteStudiengangRepository(self.pfad)
        repository.speichere_ziele(ziele)
        geladen = SQLiteStudiengangRepository(self.pfad).lade_ziele()
        self.assertEqual([z.ist_aktiv for z in geladen], [True, False, True])

    def test_erneutes_speichern_verdoppelt_die_ziele_nicht(self) -> None:
        from studiendashboard.ziele import standardziele

        repository = SQLiteStudiengangRepository(self.pfad)
        repository.speichere_ziele(standardziele(48))
        repository.speichere_ziele(standardziele(48))
        self.assertEqual(len(repository.lade_ziele()), 3)


if __name__ == "__main__":
    unittest.main()
