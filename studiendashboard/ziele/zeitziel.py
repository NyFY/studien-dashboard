"""Studienziel 1: Abschluss innerhalb der geplanten Studiendauer."""

from __future__ import annotations

from datetime import date

from ..dto import Ampel, Kennzahlen, Zielbewertung
from .studienziel import Studienziel


class Zeitziel(Studienziel):
    """Ueberwacht den Abstand zum Sollstand und die Abschlussprognose.

    Bewertet wird nicht die verstrichene Zeit, sondern die Abweichung der
    bestandenen ECTS vom Sollstand am Stichtag. Die Zieldauer haengt am
    gewaehlten Zeitmodell und wird deshalb im Ziel gespeichert, nicht
    fest verdrahtet.
    """

    def __init__(self, zielmonate: int = 48, toleranz_ects: float = 5.0) -> None:
        super().__init__(zielmonate, toleranz_ects)

    @property
    def titel(self) -> str:
        return f"Abschluss in {self.zielmonate} Monaten"

    @property
    def zielmonate(self) -> int:
        return int(self.zielwert)

    @property
    def toleranz_ects(self) -> float:
        return self.toleranz

    def bewerte(self, kennzahlen: Kennzahlen) -> Zielbewertung:
        abweichung = kennzahlen.ects_abweichung

        if abweichung >= -self.toleranz_ects:
            ampel = Ampel.GRUEN
        elif abweichung >= -3 * self.toleranz_ects:
            ampel = Ampel.GELB
        else:
            ampel = Ampel.ROT

        if abweichung >= 0:
            lage = f"{abweichung:.1f}".replace(".", ",") + " ECTS Vorsprung"
        else:
            lage = f"{abs(abweichung):.1f}".replace(".", ",") + " ECTS Rückstand"

        prognose = self.prognostiziertes_ende(kennzahlen)
        if prognose is None:
            hinweis = f"{lage}, Prognose noch nicht möglich"
        elif kennzahlen.tage_verzug > 0:
            hinweis = (
                f"{lage}, Prognose {prognose:%d.%m.%Y} "
                f"({kennzahlen.tage_verzug} Tage nach Ziel)"
            )
        else:
            hinweis = f"{lage}, Prognose {prognose:%d.%m.%Y} (im Ziel)"

        return Zielbewertung(
            titel=self.titel,
            kennwert=f"{kennzahlen.ects_ist}",
            zusatz=f"von {kennzahlen.ects_gesamt} ECTS",
            hinweis=hinweis,
            ampel=ampel,
        )

    # -- Fachliche Ausgabe des Ziels --------------------------------------

    def prognostiziertes_ende(self, kennzahlen: Kennzahlen) -> date | None:
        """Datum, an dem der Abschluss beim bisherigen Tempo erreicht waere.

        Die Ampel sagt nur, ob der Rueckstand noch im Rahmen liegt; erst
        diese Zahl sagt, worauf er hinauslaeuft. Sie gehoert deshalb zum
        Zeitziel und steht auch im Klassendiagramm an dieser Klasse. Die
        Hochrechnung selbst macht der FortschrittsService einmal fuer alle.

        Returns:
            Das prognostizierte Abschlussdatum, oder None, solange noch kein
            Modul bestanden ist und sich kein Tempo ableiten laesst.
        """
        return kennzahlen.prognose_datum
