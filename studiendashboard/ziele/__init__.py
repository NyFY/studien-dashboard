"""Studienziele und ihre Bewertung.

Die Ergebnisklassen ``Ampel`` und ``Zielbewertung`` liegen im Paket ``dto``,
weil auch die Ansichten sie brauchen. Sie werden hier zur Bequemlichkeit
weitergereicht.
"""

from ..dto import Ampel, Zielbewertung
from .notenziel import Notenziel
from .studienziel import Studienziel
from .wipziel import WipZiel
from .zeitziel import Zeitziel
from .zielfabrik import BEDEUTUNG, erzeuge_ziel, standardziele

__all__ = [
    "BEDEUTUNG", "Ampel", "Notenziel", "Studienziel", "WipZiel", "Zeitziel",
    "Zielbewertung", "erzeuge_ziel", "standardziele",
]
