"""Datentransportobjekte (Data Transfer Objects).

Dieses Paket enthaelt nur Daten, keine Logik. Alle darueber liegenden
Schichten duerfen es benutzen, es selbst benutzt keine andere Schicht ausser
den Fachklassen.
"""

from .dashboard_daten import DashboardDaten, Kennzahlen, ModulZeile, Verlaufspunkt
from .ergebnis import Ampel, Zielbewertung

__all__ = [
    "Ampel", "DashboardDaten", "Kennzahlen", "ModulZeile",
    "Verlaufspunkt", "Zielbewertung",
]
