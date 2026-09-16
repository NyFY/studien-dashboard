"""Abstrakte Oberklasse aller Studienziele."""

from __future__ import annotations

from abc import ABC, abstractmethod

from ..dto import Kennzahlen, Zielbewertung


class Studienziel(ABC):
    """Ein ueberwachtes Ziel des Studiums.

    Alle Ziele liefern dasselbe Ergebnis, naemlich eine Zielbewertung,
    rechnen dafuer aber unterschiedlich. Ein viertes Ziel ist deshalb eine
    neue Unterklasse und kein Eingriff in den Controller (Open-Closed-Prinzip).

    Bewertet werden bewusst nur die Kennzahlen und nicht der gesamte
    Studiengang. Das Ziel braucht das Objektgeflecht nicht zu kennen, und die
    Bewertung laesst sich damit ohne Datenbank testen.
    """

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
        return type(self).__name__.lower()

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.zielwert}, {self.toleranz})"
