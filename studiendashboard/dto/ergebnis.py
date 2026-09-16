"""Ergebnisobjekte der Zielbewertung.

Sie liegen im Paket ``dto``, weil sowohl die Studienziele als auch die
Ansichten sie brauchen. Damit zeigen alle Abhaengigkeiten in eine Richtung:
``ziele`` und ``view`` haengen von ``dto`` ab, nie umgekehrt.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Ampel(Enum):
    """Bewertungsergebnis eines Studienziels."""

    GRUEN = "gruen"
    GELB = "gelb"
    ROT = "rot"

    @property
    def farbe(self) -> str:
        """Farbwert fuer die grafische Oberflaeche."""
        return {"gruen": "#2E7D32", "gelb": "#D89400", "rot": "#C62828"}[self.value]

    @property
    def zeichen(self) -> str:
        """Zeichen fuer die Ausgabe auf der Kommandozeile."""
        return {"gruen": "[ok]", "gelb": "[!]", "rot": "[X]"}[self.value]


@dataclass(frozen=True, slots=True)
class Zielbewertung:
    """Ergebnis der Bewertung eines Studienziels.

    Die Ampel allein reicht der Oberflaeche nicht. Sie braucht zusaetzlich
    den Kennwert und einen kurzen Satz, der die Konsequenz benennt. Diese
    Klasse ist in Phase 2 aus genau diesem Grund hinzugekommen.
    """

    titel: str
    kennwert: str
    zusatz: str
    hinweis: str
    ampel: Ampel
