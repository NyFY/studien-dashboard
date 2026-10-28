"""Abstrakte Oberklasse aller Studienziele."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import ClassVar

from ..dto import Kennzahlen
from ..ergebnis import Zielbewertung


class Studienziel(ABC):
    """Ein ueberwachtes Ziel des Studiums.

    Alle Ziele liefern dasselbe Ergebnis, naemlich eine Zielbewertung,
    rechnen dafuer aber unterschiedlich. Ein viertes Ziel ist deshalb eine
    neue Unterklasse (Open-Closed-Prinzip). Damit das wirklich gilt, traegt
    sich jede Unterklasse beim Erben selbst in ein Verzeichnis ein. Weder der
    Controller noch das Repository noch die Zielfabrik muessen dafuer
    angefasst werden; eine if-Kette ueber die Zielarten gibt es nicht.

    Bewertet werden bewusst nur die Kennzahlen und nicht der gesamte
    Studiengang. Das Ziel braucht das Objektgeflecht nicht zu kennen, und die
    Bewertung laesst sich damit ohne Datenbank testen.
    """

    #: Was zielwert und toleranz bei dieser Zielart bedeuten.
    bedeutung: ClassVar[tuple[str, str]] = ("Zielwert", "Toleranz")

    #: Alle Unterklassen, nach ihrer Kennung. Wird beim Erben gefuellt.
    _arten: ClassVar[dict[str, type["Studienziel"]]] = {}

    def __init_subclass__(cls, **kwargs: object) -> None:
        super().__init_subclass__(**kwargs)
        Studienziel._arten[cls.kennung()] = cls

    @classmethod
    def kennung(cls) -> str:
        """Kurzname, unter dem die Datenbank diese Zielart speichert."""
        return cls.__name__.lower()

    @classmethod
    def mit_kennung(cls, kennung: str) -> type["Studienziel"]:
        """Die Unterklasse zu einer gespeicherten Kennung.

        Raises:
            ValueError: Wenn keine Unterklasse diese Kennung traegt.
        """
        try:
            return cls._arten[kennung]
        except KeyError:
            bekannt = ", ".join(sorted(cls._arten))
            raise ValueError(
                f"Unbekannte Zielart: {kennung}. Bekannt sind: {bekannt}"
            ) from None

    @classmethod
    def aus_werten(cls, zielwert: float, toleranz: float) -> "Studienziel":
        """Baut das Ziel aus den gespeicherten Zahlen.

        Unterklassen, deren Werte ganzzahlig sind, ueberschreiben das.
        """
        return cls(zielwert, toleranz)

    def __init__(self, zielwert: float, toleranz: float, ist_aktiv: bool = True) -> None:
        self.zielwert = zielwert
        self.toleranz = toleranz
        self.ist_aktiv = ist_aktiv

    @property
    @abstractmethod
    def titel(self) -> str:
        """Ueberschrift der Kachel.

        Bewusst berechnet und nicht gespeichert: Wird der Zielwert geaendert,
        aendert sich die Ueberschrift mit, statt einen alten Wert zu nennen.
        """

    @abstractmethod
    def bewerte(self, kennzahlen: Kennzahlen) -> Zielbewertung:
        """Bewertet die Kennzahlen und liefert eine Ampel mit Begruendung."""

    @property
    def art(self) -> str:
        """Kurzname der Zielart, unter dem das Ziel gespeichert wird."""
        return type(self).kennung()

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.zielwert}, {self.toleranz})"
