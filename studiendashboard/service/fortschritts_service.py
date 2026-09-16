"""Berechnungen rund um den zeitlichen Studienfortschritt."""

from __future__ import annotations

from datetime import date, timedelta

from ..domain import Studiengang
from ..dto import Verlaufspunkt


class FortschrittsService:
    """Rechnet Sollstand, Verlauf und Abschlussprognose.

    Die Methoden sind bewusst als reine Funktionen der uebergebenen Werte
    geschrieben: gleiche Eingabe, gleiches Ergebnis, kein gespeicherter
    Zustand im Service. Das macht sie ohne Vorbereitung testbar.
    """

    def soll_ects(self, studiengang: Studiengang, stichtag: date) -> float:
        """Wie viele ECTS zum Stichtag bei gleichmaessigem Fortschritt faellig waeren."""
        tage_bisher = (stichtag - studiengang.studienbeginn).days
        tage_gesamt = studiengang.tage_geplante_dauer
        if tage_gesamt <= 0:
            return 0.0
        anteil = min(max(tage_bisher / tage_gesamt, 0.0), 1.0)
        return studiengang.gesamt_ects * anteil

    def ist_ects(self, studiengang: Studiengang, stichtag: date) -> int:
        """Zum Stichtag tatsaechlich erreichte ECTS."""
        return studiengang.erreichte_ects_bis(stichtag)

    def tempo_ects_pro_tag(self, studiengang: Studiengang, stichtag: date) -> float:
        """Bisher erreichte ECTS je Tag seit Studienbeginn."""
        tage_bisher = (stichtag - studiengang.studienbeginn).days
        if tage_bisher <= 0:
            return 0.0
        return self.ist_ects(studiengang, stichtag) / tage_bisher

    def prognose(self, studiengang: Studiengang, stichtag: date) -> date | None:
        """Voraussichtliches Abschlussdatum bei gleichbleibendem Tempo.

        Returns:
            Das errechnete Datum oder None, solange noch kein Modul
            bestanden ist und sich damit kein Tempo bestimmen laesst.
        """
        tempo = self.tempo_ects_pro_tag(studiengang, stichtag)
        if tempo <= 0:
            return None
        benoetigte_tage = round(studiengang.gesamt_ects / tempo)
        # Bei sehr geringem Tempo laege das Ergebnis ausserhalb des
        # darstellbaren Datumsbereichs. Dann gibt es keine sinnvolle Prognose.
        if benoetigte_tage > (date.max - studiengang.studienbeginn).days:
            return None
        return studiengang.studienbeginn + timedelta(days=benoetigte_tage)

    def tage_verzug(self, studiengang: Studiengang, stichtag: date) -> int:
        """Abweichung der Prognose vom Zieldatum in Tagen.

        Ein positiver Wert bedeutet Verzug, ein negativer einen Vorsprung.
        """
        prognose = self.prognose(studiengang, stichtag)
        if prognose is None:
            return 0
        return (prognose - studiengang.zieldatum).days

    def verlauf(self, studiengang: Studiengang, stichtag: date) -> tuple[Verlaufspunkt, ...]:
        """Aufsummierter ECTS-Verlauf seit Studienbeginn.

        Als Zeitpunkt eines Moduls gilt das Datum, an dem es vollstaendig
        bestanden war. Module, die zum Stichtag noch nicht bestanden waren,
        bleiben unberuecksichtigt, damit die Kurve zeitlich nicht zurueck-
        laeuft.
        """
        ereignisse: list[tuple[date, int]] = [
            (modul.bestanden_am, modul.ects)
            for modul in studiengang.bestandene_module_bis(stichtag)
            if modul.bestanden_am is not None
        ]

        punkte = [Verlaufspunkt(tag=0, datum=studiengang.studienbeginn, ects=0)]
        summe = 0
        for datum, ects in sorted(ereignisse):
            summe += ects
            punkte.append(
                Verlaufspunkt(
                    tag=(datum - studiengang.studienbeginn).days, datum=datum, ects=summe
                )
            )
        if punkte[-1].datum != stichtag:
            punkte.append(
                Verlaufspunkt(
                    tag=(stichtag - studiengang.studienbeginn).days,
                    datum=stichtag,
                    ects=summe,
                )
            )
        return tuple(punkte)
