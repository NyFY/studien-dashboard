"""Entity-Klasse Semester."""

from __future__ import annotations

from datetime import date

from .modul import Modul


class Semester:
    """Ein Studienhalbjahr.

    Die Beziehung zu den Modulen ist eine Aggregation: Ein Modul stammt aus
    dem Modulhandbuch und existiert unabhaengig von der Zuordnung zu einem
    Semester. Deshalb werden hier fertige Module uebergeben, und beim
    Entfernen bleibt das Modul erhalten.
    """

    def __init__(self, nummer: int, beginn: date, ende: date) -> None:
        if nummer < 1:
            raise ValueError("Die Semesternummer beginnt bei 1")
        self.nummer = nummer
        self.beginn = beginn
        self.ende = ende
        self._module: list[Modul] = []

    # -- Aggregation ------------------------------------------------------

    def belege(self, modul: Modul) -> None:
        """Ordnet ein bereits bestehendes Modul diesem Semester zu."""
        if any(vorhanden.kuerzel == modul.kuerzel for vorhanden in self._module):
            raise ValueError(f"{modul.kuerzel} ist in Semester {self.nummer} bereits belegt")
        self._module.append(modul)

    def gib_frei(self, kuerzel: str) -> Modul:
        """Loest die Zuordnung und gibt das Modul zurueck.

        Das Modul lebt danach weiter und kann einem anderen Semester
        zugeordnet werden. Genau das unterscheidet die Aggregation von der
        Komposition.
        """
        for stelle, modul in enumerate(self._module):
            if modul.kuerzel == kuerzel:
                return self._module.pop(stelle)
        raise KeyError(f"{kuerzel} ist in Semester {self.nummer} nicht belegt")

    @property
    def module(self) -> tuple[Modul, ...]:
        """Unveraenderliche Sicht auf die belegten Module."""
        return tuple(self._module)

    # -- Abgeleitete Attribute -------------------------------------------

    @property
    def ects_bestanden(self) -> int:
        """Summe der ECTS aller bestandenen Module dieses Semesters."""
        return sum(modul.ects for modul in self._module if modul.ist_bestanden)

    @property
    def ects_gesamt(self) -> int:
        """Summe der ECTS aller belegten Module."""
        return sum(modul.ects for modul in self._module)

    def __repr__(self) -> str:
        return f"Semester({self.nummer}, {len(self._module)} Module)"
