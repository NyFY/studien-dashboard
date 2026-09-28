"""Tests der Zielbewertung.

Die Ziele arbeiten ausschliesslich auf Kennzahlen. Deshalb laesst sich hier
ohne Datenbank und ohne Objektgeflecht pruefen, ob die Ampeln stimmen.
"""

from __future__ import annotations

import unittest
from datetime import date

from studiendashboard.dto import Kennzahlen
from studiendashboard.ziele import Ampel, Notenziel, Studienziel, WipZiel, Zeitziel


def kennzahlen(**abweichungen) -> Kennzahlen:
    """Baut einen Kennzahlensatz mit sinnvollen Vorgabewerten."""
    vorgabe = dict(
        ects_ist=75, ects_soll=88.2, ects_gesamt=180,
        notendurchschnitt=1.80, benoetigter_restschnitt=2.14,
        offene_module=4, aeltestes_modul_tage=96, aeltestes_modul_kuerzel="DLBITIML",
        prognose_datum=date(2029, 6, 13), zieldatum=date(2028, 9, 30), tage_verzug=256,
    )
    vorgabe.update(abweichungen)
    return Kennzahlen(**vorgabe)      # type: ignore[arg-type]


class TestZeitziel(unittest.TestCase):
    def test_gruen_bei_geringem_rueckstand(self) -> None:
        ziel = Zeitziel()
        self.assertEqual(ziel.bewerte(kennzahlen(ects_ist=85)).ampel, Ampel.GRUEN)

    def test_gelb_bei_mittlerem_rueckstand(self) -> None:
        self.assertEqual(Zeitziel().bewerte(kennzahlen()).ampel, Ampel.GELB)

    def test_rot_bei_grossem_rueckstand(self) -> None:
        self.assertEqual(Zeitziel().bewerte(kennzahlen(ects_ist=60)).ampel, Ampel.ROT)

    def test_hinweis_nennt_prognose_und_verzug(self) -> None:
        hinweis = Zeitziel().bewerte(kennzahlen()).hinweis
        self.assertIn("13.06.2029", hinweis)
        self.assertIn("256", hinweis)
        self.assertIn("Rückstand", hinweis)


class TestNotenziel(unittest.TestCase):
    def test_gruen_wenn_ziel_eingehalten(self) -> None:
        self.assertEqual(Notenziel(2.0).bewerte(kennzahlen()).ampel, Ampel.GRUEN)

    def test_gelb_innerhalb_der_toleranz(self) -> None:
        self.assertEqual(
            Notenziel(2.0).bewerte(kennzahlen(notendurchschnitt=2.15)).ampel, Ampel.GELB
        )

    def test_rot_ausserhalb_der_toleranz(self) -> None:
        self.assertEqual(
            Notenziel(2.0).bewerte(kennzahlen(notendurchschnitt=2.5)).ampel, Ampel.ROT
        )

    def test_ohne_note_gelb_und_hinweis(self) -> None:
        bewertung = Notenziel().bewerte(kennzahlen(notendurchschnitt=None))
        self.assertEqual(bewertung.ampel, Ampel.GELB)
        self.assertEqual(bewertung.kennwert, "-")

    def test_unerreichbares_ziel_wird_benannt(self) -> None:
        hinweis = Notenziel(2.0).bewerte(kennzahlen(benoetigter_restschnitt=0.6)).hinweis
        self.assertIn("nicht mehr erreichbar", hinweis)


class TestWipZiel(unittest.TestCase):
    def test_gruen_im_limit(self) -> None:
        bewertung = WipZiel(3).bewerte(kennzahlen(offene_module=3, aeltestes_modul_tage=20))
        self.assertEqual(bewertung.ampel, Ampel.GRUEN)

    def test_gelb_bei_einem_modul_zu_viel(self) -> None:
        bewertung = WipZiel(3).bewerte(kennzahlen(offene_module=4, aeltestes_modul_tage=20))
        self.assertEqual(bewertung.ampel, Ampel.GELB)

    def test_rot_bei_zu_altem_modul(self) -> None:
        self.assertEqual(WipZiel(3).bewerte(kennzahlen()).ampel, Ampel.ROT)

    def test_rot_bei_deutlicher_ueberschreitung(self) -> None:
        bewertung = WipZiel(3).bewerte(kennzahlen(offene_module=5, aeltestes_modul_tage=10))
        self.assertEqual(bewertung.ampel, Ampel.ROT)


class TestZielwerteUndSpeicherung(unittest.TestCase):
    """Die Ziele tragen ihre Schwellenwerte selbst, damit sie speicherbar sind."""

    def test_titel_folgt_dem_zielwert(self) -> None:
        ziel = Notenziel(zielnote=2.0)
        self.assertEqual(ziel.titel, "Abschlussnote 2,0 oder besser")
        ziel.zielwert = 1.7
        self.assertEqual(ziel.titel, "Abschlussnote 1,7 oder besser")

    def test_zielart_ist_der_speicherschluessel(self) -> None:
        self.assertEqual(Zeitziel().art, "zeitziel")
        self.assertEqual(Notenziel().art, "notenziel")
        self.assertEqual(WipZiel().art, "wipziel")

    def test_fabrik_erzeugt_die_richtige_unterklasse(self) -> None:
        from studiendashboard.ziele import erzeuge_ziel

        self.assertIsInstance(erzeuge_ziel("zeitziel", 36, 5, True), Zeitziel)
        self.assertIsInstance(erzeuge_ziel("notenziel", 2.0, 0.2, True), Notenziel)
        wip = erzeuge_ziel("wipziel", 3, 90, False)
        self.assertIsInstance(wip, WipZiel)
        self.assertFalse(wip.ist_aktiv)
        with self.assertRaises(ValueError):
            erzeuge_ziel("unbekannt", 1, 1, True)

    def test_werte_ueberleben_den_umweg_ueber_die_fabrik(self) -> None:
        from studiendashboard.ziele import erzeuge_ziel, standardziele

        for original in standardziele(48):
            kopie = erzeuge_ziel(
                original.art, original.zielwert, original.toleranz, original.ist_aktiv
            )
            with self.subTest(art=original.art):
                self.assertEqual(type(kopie), type(original))
                self.assertEqual(kopie.zielwert, original.zielwert)
                self.assertEqual(kopie.toleranz, original.toleranz)
                self.assertEqual(kopie.titel, original.titel)

    def test_ohne_startdatum_kein_falsches_alter(self) -> None:
        bewertung = WipZiel(3).bewerte(
            kennzahlen(offene_module=2, aeltestes_modul_tage=0, aeltestes_modul_kuerzel=None)
        )
        self.assertIn("ohne hinterlegtes Startdatum", bewertung.hinweis)


class TestErweiterbarkeit(unittest.TestCase):
    """Belegt das Open-Closed-Prinzip: ein neues Ziel aendert nichts Bestehendes."""

    def test_neues_ziel_fuegt_sich_ein(self) -> None:
        class EctsProMonatZiel(Studienziel):
            def __init__(self, mindesttempo: float = 5.0) -> None:
                super().__init__(zielwert=mindesttempo, toleranz=0.0)

            @property
            def titel(self) -> str:
                return f"Mindestens {self.zielwert:.0f} ECTS je Monat"

            def bewerte(self, k: Kennzahlen) -> "Zielbewertung":  # type: ignore[name-defined]
                from studiendashboard.ziele import Zielbewertung

                tempo = k.ects_ist / 23.5
                return Zielbewertung(
                    titel=self.titel, kennwert=f"{tempo:.1f}", zusatz="ECTS je Monat",
                    hinweis="Testziel", ampel=Ampel.GRUEN if tempo >= self.zielwert else Ampel.ROT,
                )

        alle: list[Studienziel] = [Zeitziel(), Notenziel(), WipZiel(), EctsProMonatZiel()]
        ampeln = [ziel.bewerte(kennzahlen()).ampel for ziel in alle]
        self.assertEqual(len(ampeln), 4)
        self.assertEqual(ampeln[3], Ampel.ROT)

    def test_unvollstaendiges_ziel_wird_abgelehnt(self) -> None:
        class Unvollstaendig(Studienziel):
            pass

        with self.assertRaises(TypeError):
            Unvollstaendig(1.0, 0.0)     # type: ignore[abstract]


class TestFachlicheAusgaben(unittest.TestCase):
    """Jedes Ziel liefert neben der Ampel die Zahl, die zu ihm gehoert."""

    def test_zeitziel_nennt_das_prognostizierte_ende(self) -> None:
        self.assertEqual(
            Zeitziel().prognostiziertes_ende(kennzahlen()), date(2029, 6, 13)
        )

    def test_zeitziel_ohne_tempo_liefert_keine_prognose(self) -> None:
        self.assertIsNone(
            Zeitziel().prognostiziertes_ende(kennzahlen(prognose_datum=None))
        )

    def test_notenziel_nennt_den_hoechsten_restschnitt(self) -> None:
        self.assertAlmostEqual(
            Notenziel().hoechster_restschnitt(kennzahlen()), 2.14
        )

    def test_wipziel_nennt_das_alter_des_aeltesten_moduls(self) -> None:
        self.assertEqual(WipZiel().alter_aeltestes_modul(kennzahlen()), 96)


class TestSchwellenwerteSindTrennscharf(unittest.TestCase):
    """Die Grenzwerte selbst gehoeren zur besseren Stufe.

    Genau an diesen Punkten war die Beschreibung in Phase 1 zunaechst
    mehrdeutig. Die Tests halten die Auslegung fest.
    """

    def test_zeitziel_an_den_grenzen(self) -> None:
        faelle = [
            (80.0, Ampel.GRUEN),      # Abweichung genau -5
            (80.1, Ampel.GELB),       # knapp schlechter als -5
            (90.0, Ampel.GELB),       # Abweichung genau -15
            (90.1, Ampel.ROT),        # knapp schlechter als -15
        ]
        for soll, erwartet in faelle:
            with self.subTest(ects_soll=soll):
                bewertung = Zeitziel().bewerte(kennzahlen(ects_ist=75, ects_soll=soll))
                self.assertEqual(bewertung.ampel, erwartet)

    def test_notenziel_an_den_grenzen(self) -> None:
        faelle = [(2.0, Ampel.GRUEN), (2.1, Ampel.GELB), (2.2, Ampel.GELB), (2.3, Ampel.ROT)]
        for schnitt, erwartet in faelle:
            with self.subTest(schnitt=schnitt):
                bewertung = Notenziel().bewerte(kennzahlen(notendurchschnitt=schnitt))
                self.assertEqual(bewertung.ampel, erwartet)

    def test_wipziel_an_den_grenzen(self) -> None:
        faelle = [
            (3, 90, Ampel.GRUEN),     # im Limit, Alter genau an der Grenze
            (3, 91, Ampel.ROT),       # ein Tag darueber
            (4, 90, Ampel.GELB),      # eins zu viel, Alter noch im Rahmen
            (5, 90, Ampel.ROT),       # zwei zu viel
        ]
        for anzahl, alter, erwartet in faelle:
            with self.subTest(offene_module=anzahl, alter=alter):
                bewertung = WipZiel().bewerte(
                    kennzahlen(offene_module=anzahl, aeltestes_modul_tage=alter)
                )
                self.assertEqual(bewertung.ampel, erwartet)


if __name__ == "__main__":
    unittest.main()
