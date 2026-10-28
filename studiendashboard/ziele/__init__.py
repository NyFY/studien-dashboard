"""Studienziele und ihre Bewertung.

Jedes Ziel bekommt die Kennzahlen aus dem Paket ``dto`` und liefert eine
``Zielbewertung`` aus dem Paket ``ergebnis``. Weitergereicht wird hier
nichts: Wer das Ergebnis braucht, holt es dort, wo es definiert ist.
"""

from .notenziel import Notenziel
from .studienziel import Studienziel
from .wipziel import WipZiel
from .zeitziel import Zeitziel
from .zielfabrik import bedeutungen, erzeuge_ziel, standardziele

__all__ = [
    "Notenziel", "Studienziel", "WipZiel", "Zeitziel",
    "bedeutungen", "erzeuge_ziel", "standardziele",
]
