"""Studienziel 3: Begrenzung gleichzeitig offener Module."""

from __future__ import annotations

from ..dto import Kennzahlen
from ..ergebnis import Ampel, Zielbewertung
from .studienziel import Studienziel


class WipZiel(Studienziel):
    """Uebertraegt das Work-in-Progress-Limit aus Kanban auf das Studium.

    Bewertet werden zwei Groessen: die Anzahl gleichzeitig begonnener Module
    und das Alter des aeltesten davon. Ein einzelnes lange liegen gebliebenes
    Modul ist das eigentliche Warnsignal.
    """

    bedeutung = ("hoechstens gleichzeitig offene Module", "hoechstes Alter in Tagen")

    def __init__(self, hoechstzahl: int = 3, hoechstalter_tage: int = 90) -> None:
        super().__init__(hoechstzahl, hoechstalter_tage)

    @classmethod
    def aus_werten(cls, zielwert: float, toleranz: float) -> "WipZiel":
        return cls(hoechstzahl=int(zielwert), hoechstalter_tage=int(toleranz))

    @property
    def titel(self) -> str:
        wort = "Modul" if self.hoechstzahl == 1 else "Module"
        return f"Höchstens {self.hoechstzahl} {wort} gleichzeitig"

    @property
    def hoechstzahl(self) -> int:
        return int(self.zielwert)

    @property
    def hoechstalter_tage(self) -> int:
        return int(self.toleranz)

    def bewerte(self, kennzahlen: Kennzahlen) -> Zielbewertung:
        anzahl = kennzahlen.offene_module
        alter = self.alter_aeltestes_modul(kennzahlen)

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

    # -- Fachliche Ausgabe des Ziels --------------------------------------

    def alter_aeltestes_modul(self, kennzahlen: Kennzahlen) -> int:
        """Alter des am laengsten begonnenen Moduls in Tagen.

        Die Anzahl offener Module allein unterschaetzt das Risiko: Drei seit
        einer Woche begonnene Module sind etwas anderes als drei seit einem
        halben Jahr liegen gebliebene. Deshalb gehoert diese Zahl zum Ziel.
        """
        return kennzahlen.aeltestes_modul_tage
