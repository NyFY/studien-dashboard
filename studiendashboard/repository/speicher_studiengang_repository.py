"""Repository, das die Daten nur im Arbeitsspeicher haelt."""

from __future__ import annotations

from ..domain import Studiengang
from ..ziele import Studienziel, standardziele
from .studiengang_repository import StudiengangRepository


class SpeicherStudiengangRepository(StudiengangRepository):
    """Haelt den Studiengang im Arbeitsspeicher.

    Diese Fassung existiert nicht aus Bequemlichkeit, sondern weil sie die
    Repository-Abstraktion begruendet: Die automatisierten Tests laufen damit
    ohne Datenbankdatei, und beim Ausprobieren bleibt nichts auf der Platte
    zurueck. Der Controller merkt den Unterschied nicht.
    """

    def __init__(
        self,
        studiengang: Studiengang | None = None,
        ziele: list[Studienziel] | None = None,
    ) -> None:
        self._studiengang = studiengang
        self._ziele = ziele

    def lade(self) -> Studiengang:
        if self._studiengang is None:
            raise LookupError("Es wurde noch kein Studiengang hinterlegt")
        return self._studiengang

    def speichere(self, studiengang: Studiengang) -> None:
        self._studiengang = studiengang

    def lade_ziele(self) -> list[Studienziel]:
        if self._ziele is None:
            monate = self._studiengang.geplante_dauer_monate if self._studiengang else 48
            self._ziele = standardziele(monate)
        return self._ziele

    def speichere_ziele(self, ziele: list[Studienziel]) -> None:
        self._ziele = list(ziele)

    def ist_leer(self) -> bool:
        return self._studiengang is None
