"""Berechnungen rund um die Noten."""

from __future__ import annotations

from datetime import date

from ..domain import NOTENSTUFEN, Studiengang

#: Bandbreiten fuer die Notenverteilung im Dashboard.
NOTENBAENDER: tuple[tuple[str, float, float], ...] = (
    ("1,0-1,3", 1.0, 1.3),
    ("1,4-1,7", 1.4, 1.7),
    ("1,8-2,0", 1.8, 2.0),
    ("2,1-2,3", 2.1, 2.3),
    ("2,4-2,7", 2.4, 2.7),
    ("ab 2,8", 2.8, 5.0),
)


class NotenService:
    """Rechnet Durchschnitt, benoetigten Restschnitt und Verteilung."""

    def durchschnitt(self, studiengang: Studiengang, stichtag: date | None = None) -> float | None:
        """Ungerundeter, ECTS-gewichteter Notendurchschnitt zum Stichtag."""
        return studiengang.notendurchschnitt_bis(stichtag or date.max)

    def benoetigter_restschnitt(
        self, studiengang: Studiengang, zielnote: float, stichtag: date | None = None
    ) -> float | None:
        """Welchen Schnitt die verbleibenden ECTS hoechstens haben duerfen.

        Loest die Gleichung
        ``(bisherige_ects * schnitt + rest_ects * x) / gesamt_ects = zielnote``
        nach ``x`` auf.

        Returns:
            Den erlaubten Schnitt, oder None wenn keine ECTS mehr offen sind
            oder noch keine Note vorliegt.
        """
        stichtag = stichtag or date.max
        schnitt = self.durchschnitt(studiengang, stichtag)
        if schnitt is None:
            return None
        erreicht = studiengang.erreichte_ects_bis(stichtag)
        rest_ects = studiengang.gesamt_ects - erreicht
        if rest_ects <= 0:
            return None
        return (zielnote * studiengang.gesamt_ects - erreicht * schnitt) / rest_ects

    def verteilung(
        self, studiengang: Studiengang, stichtag: date | None = None
    ) -> tuple[tuple[str, int], ...]:
        """Anzahl bestandener Module je Notenband."""
        noten = [
            modul.note.wert
            for modul in studiengang.bestandene_module_bis(stichtag or date.max)
            if modul.note is not None
        ]
        return tuple(
            (etikett, sum(1 for wert in noten if untere <= wert <= obere))
            for etikett, untere, obere in NOTENBAENDER
        )

    def anzahl_bewertet(self, studiengang: Studiengang, stichtag: date | None = None) -> int:
        """Anzahl der Module mit einer Note."""
        return sum(
            1
            for modul in studiengang.bestandene_module_bis(stichtag or date.max)
            if modul.note is not None
        )

    @staticmethod
    def band_index(schnitt: float | None) -> int:
        """Stelle des Notenbands, in das ein Durchschnitt faellt.

        Der Wert wandert als Zahl in das Datentransportobjekt, damit die
        Anzeige die Notenbaender nicht selbst kennen muss.
        """
        if schnitt is None:
            return -1
        for stelle, (_, untere, obere) in enumerate(NOTENBAENDER):
            if untere - 0.05 <= schnitt <= obere + 0.05:
                return stelle
        return len(NOTENBAENDER) - 1

    @staticmethod
    def ist_gueltige_note(wert: float) -> bool:
        """Prueft, ob ein Wert eine zulaessige Notenstufe ist."""
        return wert in NOTENSTUFEN
