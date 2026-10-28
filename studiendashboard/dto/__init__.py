"""Datentransportobjekte (Data Transfer Objects).

Dieses Paket enthaelt nur Daten, keine Logik. Es bringt die Werte vom
Controller zur Oberflaeche und beschreibt dabei ausdruecklich, welche Werte
die Anzeige erwartet.

Die Ergebnistypen der Zielbewertung liegen nicht hier, sondern im Paket
``ergebnis``: Sie entstehen in der Fachlogik und nicht erst fuer die Anzeige.
``DashboardDaten`` nimmt sie entgegen und reicht sie weiter.
"""

from .dashboard_daten import DashboardDaten, Kennzahlen, ModulZeile, Verlaufspunkt

__all__ = ["DashboardDaten", "Kennzahlen", "ModulZeile", "Verlaufspunkt"]
