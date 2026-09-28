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

    Eine Punktzahl allein ist fachlich nicht auswertbar. Der Versuch fuehrt
    deshalb die beiden Bezugsgroessen mit, auf die sie sich bezieht: die
    erreichbare Hoechstpunktzahl und die Bestehensgrenze. Beide stehen am
    Versuch und nicht an der Pruefungsleistung, damit ein einmal abgelegter
    Versuch fuer sich allein auswertbar bleibt.
    """

    nummer: int
    datum: date
    erreichte_punkte: int
    max_punkte: int = 100
    bestehensgrenze: int = 50

    def __post_init__(self) -> None:
        if self.nummer not in (1, 2, 3):
            raise ValueError("An der IU sind hoechstens drei Versuche moeglich")
        if self.max_punkte <= 0:
            raise ValueError("Die erreichbare Hoechstpunktzahl muss groesser als null sein")
        if not 0 < self.bestehensgrenze <= self.max_punkte:
            raise ValueError(
                "Die Bestehensgrenze muss zwischen einem Punkt und der "
                f"Hoechstpunktzahl {self.max_punkte} liegen"
            )
        if not 0 <= self.erreichte_punkte <= self.max_punkte:
            raise ValueError(
                f"Punktzahl {self.erreichte_punkte} liegt ausserhalb von 0 "
                f"bis {self.max_punkte}"
            )

    @property
    def erfuellungsgrad(self) -> int:
        """Erreichte Punkte in Prozent der Hoechstpunktzahl, kaufmaennisch gerundet."""
        return round(self.erreichte_punkte * 100 / self.max_punkte)

    @property
    def note(self) -> Note:
        """Abgeleitete Note aus dem Erfuellungsgrad."""
        return Note.aus_punkten(self.erfuellungsgrad)

    @property
    def ist_bestanden(self) -> bool:
        """True, wenn die Bestehensgrenze erreicht wurde."""
        return self.erreichte_punkte >= self.bestehensgrenze

    def __str__(self) -> str:
        return f"Versuch {self.nummer} vom {self.datum:%d.%m.%Y}: {self.note}"
