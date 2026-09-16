"""Entity-Klasse Versuch."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from .note import Note


@dataclass(frozen=True, slots=True)
class Versuch:
    """Ein einzelner Pruefungsversuch.

    Ein abgelegter Versuch ist ein historischer Sachverhalt und wird deshalb
    unveraenderlich gehalten. Die Note ist ein abgeleitetes Attribut, im
    Klassendiagramm mit ``/note`` gekennzeichnet: Gespeichert werden die
    Punkte, die Note ergibt sich daraus.
    """

    nummer: int
    datum: date
    erreichte_punkte: int

    def __post_init__(self) -> None:
        if self.nummer not in (1, 2, 3):
            raise ValueError("An der IU sind hoechstens drei Versuche moeglich")
        if not 0 <= self.erreichte_punkte <= 100:
            raise ValueError(
                f"Punktzahl {self.erreichte_punkte} liegt ausserhalb von 0 bis 100"
            )

    @property
    def note(self) -> Note:
        """Abgeleitete Note aus der Punktzahl."""
        return Note.aus_punkten(self.erreichte_punkte)

    @property
    def ist_bestanden(self) -> bool:
        """True, wenn der Versuch mit 4,0 oder besser abgeschlossen wurde."""
        return self.note.ist_bestanden

    def __str__(self) -> str:
        return f"Versuch {self.nummer} vom {self.datum:%d.%m.%Y}: {self.note}"
