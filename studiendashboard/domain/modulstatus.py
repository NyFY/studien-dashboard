"""Aufzaehlung Modulstatus."""

from __future__ import annotations

from enum import Enum


class Modulstatus(Enum):
    """Bearbeitungsstand eines Moduls.

    Die Aufzaehlung traegt bewusst etwas fachliche Logik. Beide Regeln, die
    am Status haengen, stehen damit an genau einer Stelle: ob ein Modul noch
    offen ist und ob es Aufmerksamkeit bindet.
    """

    OFFEN = "offen"
    IN_BEARBEITUNG = "in Bearbeitung"
    BESTANDEN = "bestanden"
    NICHT_BESTANDEN = "nicht bestanden"

    @property
    def zaehlt_als_offen(self) -> bool:
        """True, wenn das Modul begonnen oder geplant, aber nicht abgeschlossen ist."""
        return self in (Modulstatus.OFFEN, Modulstatus.IN_BEARBEITUNG)

    @property
    def bindet_aufmerksamkeit(self) -> bool:
        """True nur fuer bereits begonnene Module.

        Nur diese zaehlen gegen das Work-in-Progress-Limit. Ein Modul, das
        noch gar nicht angefangen wurde, kostet keine Aufmerksamkeit.
        """
        return self is Modulstatus.IN_BEARBEITUNG

    def __str__(self) -> str:
        return self.value
