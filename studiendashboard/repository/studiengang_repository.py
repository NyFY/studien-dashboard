"""Abstrakte Schnittstelle fuer die Speicherung."""

from __future__ import annotations

from abc import ABC, abstractmethod

from ..domain import Studiengang
from ..ziele import Studienziel


class StudiengangRepository(ABC):
    """Legt fest, was ein Repository koennen muss, nicht wie es speichert.

    Der Controller haengt ausschliesslich von dieser Klasse ab und nicht von
    einer konkreten Speicherloesung. Genau das ist das Dependency-Inversion-
    Prinzip: Die Fachlogik gibt die Schnittstelle vor, die Technik erfuellt sie.
    """

    @abstractmethod
    def lade(self) -> Studiengang:
        """Liefert den gespeicherten Studiengang mit allen Semestern und Modulen."""

    @abstractmethod
    def speichere(self, studiengang: Studiengang) -> None:
        """Schreibt den uebergebenen Studiengang vollstaendig zurueck."""

    @abstractmethod
    def lade_ziele(self) -> list[Studienziel]:
        """Liefert die gespeicherten Studienziele."""

    @abstractmethod
    def speichere_ziele(self, ziele: list[Studienziel]) -> None:
        """Schreibt die uebergebenen Studienziele zurueck."""

    @abstractmethod
    def ist_leer(self) -> bool:
        """True, wenn noch keine Daten vorhanden sind."""
