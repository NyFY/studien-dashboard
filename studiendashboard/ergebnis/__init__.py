"""Ergebnistypen der Zielbewertung.

Das Bewerten eines Studienziels liefert nicht Daten fuer die Anzeige,
sondern ein fachliches Ergebnis: eine Einordnung samt Begruendung. Deshalb
hat es ein eigenes Paket und liegt nicht bei den Datentransportobjekten im
Paket ``dto``. Die trennen sich in ihrem Zweck: Ein Ergebnis entsteht in der
Fachlogik, ein Transportobjekt entsteht erst fuer die Oberflaeche.

Das eigene Paket haelt ausserdem die Abhaengigkeiten gerichtet. Laegen die
beiden Typen bei den Zielen, entstuende ein Ringschluss zwischen ``dto`` und
``ziele``: ``DashboardDaten`` fuehrt die Zielbewertungen mit und muesste
``ziele`` importieren, waehrend jedes Ziel die ``Kennzahlen`` aus ``dto``
braucht. So haengen ``ziele``, ``dto``, ``controller`` und ``view``
gleichermassen von ``ergebnis`` ab, und ``ergebnis`` haengt an keinem Paket.

``tests/test_architektur.py`` liest die Importe aller Module ein und laesst
diese Richtung nicht mehr kaputtgehen.
"""

from .ampel import Ampel
from .zielbewertung import Zielbewertung

__all__ = ["Ampel", "Zielbewertung"]
