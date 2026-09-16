"""Studienziel 3: Begrenzung gleichzeitig offener Module."""

from __future__ import annotations

from ..dto import Ampel, Kennzahlen, Zielbewertung
from .studienziel import Studienziel


class WipZiel(Studienziel):
    """Uebertraegt das Work-in-Progress-Limit aus Kanban auf das Studium.

    Bewertet werden zwei Groessen: die Anzahl gleichzeitig begonnener Module
    und das Alter des aeltesten davon. Ein einzelnes lange liegen gebliebenes
    Modul ist das eigentliche Warnsignal.
    """

    def __init__(self, hoechstzahl: int = 3, hoechstalter_tage: int = 90) -> None:
        super().__init__(hoechstzahl, hoechstalter_tage)

    @property
    def titel(self) -> str:
        return f"Höchstens {self.hoechstzahl} Module gleichzeitig"

    @property
    def hoechstzahl(self) -> int:
        return int(self.zielwert)

    @property
    def hoechstalter_tage(self) -> int:
        return int(self.toleranz)

    def bewerte(self, kennzahlen: Kennzahlen) -> Zielbewertung:
        anzahl = kennzahlen.offene_module
        alter = kennzahlen.aeltestes_modul_tage

        if anzahl > self.hoechstzahl + 1 or alter > self.hoechstalter_tage:
            ampel = Ampel.ROT
        elif anzahl > self.hoechstzahl:
            ampel = Ampel.GELB
        else:
            ampel = Ampel.GRUEN

        if anzahl == 0:
            hinweis = "Zurzeit ist kein Modul in Bearbeitung."
        elif kennzahlen.aeltestes_modul_kuerzel is None:
            hinweis = f"{anzahl} Module in Bearbeitung, ohne hinterlegtes Startdatum."
        elif alter > self.hoechstalter_tage:
            hinweis = (
                f"Ältestes offen seit {alter} Tagen ({kennzahlen.aeltestes_modul_kuerzel}), "
                f"Grenze sind {self.hoechstalter_tage} Tage."
            )
        elif anzahl > self.hoechstzahl:
            hinweis = f"Limit von {self.hoechstzahl} überschritten, ältestes seit {alter} Tagen."
        else:
            hinweis = f"Im Limit, ältestes offen seit {alter} Tagen."

        return Zielbewertung(
            titel=self.titel,
            kennwert=str(anzahl),
            zusatz="Module in Bearbeitung",
            hinweis=hinweis,
            ampel=ampel,
        )
