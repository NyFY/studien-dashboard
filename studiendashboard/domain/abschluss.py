"""Aufzaehlung Abschluss.

Der angestrebte Abschluss hat nur wenige fachlich sinnvolle Werte. Als
freier Text waeren "B.Sc.", "Bachelor of Science" und "bachelor"
nebeneinander moeglich, ohne dass das Programm den Unterschied bemerkt.
Die Aufzaehlung begrenzt den Wertebereich schon beim Erzeugen, genau wie
``Modulstatus`` und ``Ampel``.
"""

from __future__ import annotations

from enum import Enum


class Abschluss(Enum):
    """Akademischer Grad, auf den der Studiengang hinauslaeuft."""

    BACHELOR_OF_SCIENCE = "B.Sc."
    BACHELOR_OF_ARTS = "B.A."
    MASTER_OF_SCIENCE = "M.Sc."
    MASTER_OF_ARTS = "M.A."

    @property
    def ist_bachelor(self) -> bool:
        """True fuer die beiden Bachelorgrade.

        Die Aufzaehlung traegt damit die eine Regel, die am Grad haengt, an
        genau einer Stelle statt verteilt in Abfragen.
        """
        return self in (Abschluss.BACHELOR_OF_SCIENCE, Abschluss.BACHELOR_OF_ARTS)

    def __str__(self) -> str:
        return self.value
