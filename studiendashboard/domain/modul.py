"""Entity-Klasse Modul."""

from __future__ import annotations

from datetime import date

from .modulstatus import Modulstatus
from .note import Note
from .pruefungsleistung import Pruefungsleistung


class Modul:
    """Ein Modul des Studiengangs.

    Das Modul besitzt seine Pruefungsleistungen (Komposition). Damit diese
    Beziehung im Code sichtbar bleibt und nicht wie eine Aggregation aussieht,
    wird die interne Liste nur als Tupel herausgegeben. Wer eine
    Pruefungsleistung hinzufuegen will, muss den dafuer vorgesehenen Weg gehen.
    """

    def __init__(
        self,
        kuerzel: str,
        bezeichnung: str,
        ects: int,
        status: Modulstatus = Modulstatus.OFFEN,
        begonnen_am: date | None = None,
    ) -> None:
        if ects <= 0:
            raise ValueError("Ein Modul muss mindestens einen ECTS-Punkt haben")
        self.kuerzel = kuerzel
        self.bezeichnung = bezeichnung
        self.ects = ects
        self.status = status
        self.begonnen_am = begonnen_am
        self._pruefungsleistungen: list[Pruefungsleistung] = []

    # -- Komposition ------------------------------------------------------

    def verlange(self, leistung: Pruefungsleistung) -> None:
        """Haengt eine Pruefungsleistung an dieses Modul."""
        self._pruefungsleistungen.append(leistung)

    @property
    def pruefungsleistungen(self) -> tuple[Pruefungsleistung, ...]:
        """Unveraenderliche Sicht auf die Pruefungsleistungen des Moduls."""
        return tuple(self._pruefungsleistungen)

    # -- Abgeleitete Attribute -------------------------------------------

    @property
    def note(self) -> Note | None:
        """Modulnote als gewichtetes Mittel der besten Versuche.

        Liefert None, solange nicht jede Pruefungsleistung des Moduls
        bestanden ist. Ein Modul mit einer nicht bestandenen Teilleistung hat
        damit keine Note, statt eine rechnerisch gemittelte auszuweisen.
        Das Ergebnis wird auf die naechstgelegene gueltige Notenstufe gerundet.
        """
        if not self.ist_bestanden:
            return None
        beste = [leistung.bester_versuch for leistung in self._pruefungsleistungen]

        summe = sum(
            versuch.note.wert * leistung.gewichtung          # type: ignore[union-attr]
            for leistung, versuch in zip(self._pruefungsleistungen, beste)
        )
        gewicht = sum(leistung.gewichtung for leistung in self._pruefungsleistungen)
        return _naechste_notenstufe(summe / gewicht)

    @property
    def ist_bestanden(self) -> bool:
        """True, wenn alle Pruefungsleistungen des Moduls bestanden sind."""
        return bool(self._pruefungsleistungen) and all(
            leistung.ist_bestanden for leistung in self._pruefungsleistungen
        )

    def naechste_frist(self, stichtag: date) -> date | None:
        """Frueheste offene Frist ueber alle Pruefungsleistungen hinweg."""
        fristen = [
            frist
            for leistung in self._pruefungsleistungen
            if (frist := leistung.naechste_frist(stichtag)) is not None
        ]
        return min(fristen) if fristen else None

    def offen_seit_tagen(self, stichtag: date) -> int | None:
        """Anzahl Tage seit Beginn der Bearbeitung.

        Liefert None, wenn kein Startdatum hinterlegt ist, das Modul nicht
        mehr offen ist oder der Stichtag noch vor dem Beginn liegt.
        """
        if self.begonnen_am is None or not self.status.zaehlt_als_offen:
            return None
        tage = (stichtag - self.begonnen_am).days
        return tage if tage >= 0 else None

    @property
    def bestanden_am(self) -> date | None:
        """Datum, an dem das Modul vollstaendig bestanden war.

        Das ist der spaeteste Zeitpunkt, zu dem eine seiner Pruefungs-
        leistungen bestanden wurde. Ohne vollstaendiges Bestehen None.
        """
        if not self.ist_bestanden:
            return None
        zeitpunkte = [
            leistung.bestanden_am
            for leistung in self._pruefungsleistungen
            if leistung.bestanden_am is not None
        ]
        return max(zeitpunkte) if zeitpunkte else None

    def war_bestanden_am(self, stichtag: date) -> bool:
        """True, wenn das Modul zum Stichtag bereits bestanden war."""
        zeitpunkt = self.bestanden_am
        return zeitpunkt is not None and zeitpunkt <= stichtag

    def __repr__(self) -> str:
        return f"Modul({self.kuerzel!r}, {self.ects} ECTS, {self.status.value})"


def _naechste_notenstufe(wert: float) -> Note:
    """Rundet einen berechneten Mittelwert auf die naechste gueltige Notenstufe."""
    from .note import NOTENSTUFEN

    passende = min(NOTENSTUFEN, key=lambda stufe: abs(stufe - wert))
    return Note(passende)
