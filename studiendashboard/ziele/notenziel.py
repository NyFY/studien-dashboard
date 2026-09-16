"""Studienziel 2: Abschlussnote."""

from __future__ import annotations

from ..dto import Ampel, Kennzahlen, Zielbewertung
from .studienziel import Studienziel


class Notenziel(Studienziel):
    """Ueberwacht den gewichteten Notendurchschnitt.

    Neben dem Ist-Wert wird der Schnitt genannt, den die verbleibenden Module
    hoechstens haben duerfen. Erst diese Rueckwaertsrechnung enthaelt eine
    Handlungsanweisung.
    """

    def __init__(self, zielnote: float = 2.0, toleranz: float = 0.2) -> None:
        super().__init__(zielnote, toleranz)

    @property
    def titel(self) -> str:
        return "Abschlussnote " + f"{self.zielnote:.1f}".replace(".", ",") + " oder besser"

    @property
    def zielnote(self) -> float:
        return self.zielwert

    def bewerte(self, kennzahlen: Kennzahlen) -> Zielbewertung:
        schnitt = kennzahlen.notendurchschnitt

        if schnitt is None:
            return Zielbewertung(
                titel=self.titel, kennwert="-", zusatz="noch keine Note",
                hinweis="Sobald das erste Modul bestanden ist, erscheint hier der Schnitt.",
                ampel=Ampel.GELB,
            )

        if schnitt <= self.zielnote:
            ampel = Ampel.GRUEN
        elif schnitt <= self.zielnote + self.toleranz:
            ampel = Ampel.GELB
        else:
            ampel = Ampel.ROT

        rest = kennzahlen.benoetigter_restschnitt
        if rest is None:
            hinweis = "Alle Module sind bewertet."
        elif rest >= 4.0:
            hinweis = "Das Ziel ist mit jeder bestandenen Restnote noch erreichbar."
        elif rest < 1.0:
            hinweis = "Das Ziel ist rechnerisch nicht mehr erreichbar."
        else:
            wert = f"{rest:.1f}".replace(".", ",")
            hinweis = f"Restmodule dürfen im Schnitt {wert} sein."

        return Zielbewertung(
            titel=self.titel,
            kennwert=f"{schnitt:.1f}".replace(".", ","),
            zusatz="gewichteter Schnitt",
            hinweis=hinweis,
            ampel=ampel,
        )
