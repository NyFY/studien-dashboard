"""Wertobjekt Note.

In der Konzeptionsphase war die Note noch eine einfache Dezimalzahl. Die
Untersuchung in Phase 2 hat gezeigt, dass damit auch Werte wie 1,5 moeglich
waeren, die es als Notenstufe nicht gibt. Die Note ist deshalb ein eigenes,
unveraenderliches Wertobjekt mit Pruefung beim Erzeugen.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import total_ordering

#: Alle an der IU vergebenen Notenstufen.
NOTENSTUFEN: tuple[float, ...] = (
    1.0, 1.3, 1.7, 2.0, 2.3, 2.7, 3.0, 3.3, 3.7, 4.0, 5.0,
)

#: Untergrenze der Punktzahl je Notenstufe (100-Punkte-Schema der IU).
_PUNKTEGRENZEN: tuple[tuple[int, float], ...] = (
    (95, 1.0), (90, 1.3), (85, 1.7), (80, 2.0), (75, 2.3),
    (70, 2.7), (65, 3.0), (60, 3.3), (55, 3.7), (50, 4.0),
)


@total_ordering
@dataclass(frozen=True, slots=True)
class Note:
    """Eine Pruefungsnote zwischen 1,0 und 5,0.

    Das Objekt ist unveraenderlich (``frozen=True``). Eine einmal
    eingetragene Note laesst sich dadurch nicht versehentlich ueberschreiben.
    """

    wert: float

    def __post_init__(self) -> None:
        if self.wert not in NOTENSTUFEN:
            raise ValueError(
                f"{self.wert} ist keine gueltige Notenstufe. "
                f"Erlaubt sind: {', '.join(str(n) for n in NOTENSTUFEN)}"
            )

    @classmethod
    def aus_punkten(cls, punkte: int) -> "Note":
        """Rechnet eine Punktzahl von 0 bis 100 in eine Notenstufe um.

        Args:
            punkte: Erreichte Punkte der Pruefungsleistung.

        Returns:
            Die zugehoerige Note. Unter 50 Punkten ist das die 5,0.
        """
        if not 0 <= punkte <= 100:
            raise ValueError(f"Punktzahl {punkte} liegt ausserhalb von 0 bis 100")
        for grenze, wert in _PUNKTEGRENZEN:
            if punkte >= grenze:
                return cls(wert)
        return cls(5.0)

    @property
    def ist_bestanden(self) -> bool:
        """True, wenn die Note 4,0 oder besser ist."""
        return self.wert <= 4.0

    def __str__(self) -> str:
        """Deutsche Schreibweise mit Komma, zum Beispiel ``1,7``."""
        return f"{self.wert:.1f}".replace(".", ",")

    def __lt__(self, andere: object) -> bool:
        """Kleinere Zahl bedeutet bessere Note."""
        if not isinstance(andere, Note):
            return NotImplemented
        return self.wert < andere.wert
