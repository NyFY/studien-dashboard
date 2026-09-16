"""Abstrakte Oberklasse aller Ansichten."""

from __future__ import annotations

from abc import ABC, abstractmethod

from ..dto import DashboardDaten


class DashboardView(ABC):
    """Vertrag fuer jede Darstellung des Dashboards.

    Weil die Ansicht nur diese eine Methode anbietet, laesst sich die
    Fensterfassung gegen die Konsolenfassung tauschen, ohne dass Controller
    oder Fachlogik davon etwas merken.
    """

    @abstractmethod
    def zeige(self, daten: DashboardDaten) -> None:
        """Stellt den uebergebenen Datensatz dar."""
