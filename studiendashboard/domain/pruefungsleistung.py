"""Abstrakte Entity-Klasse Pruefungsleistung und ihre Auspraegungen.

Die drei Pruefungsformen unterscheiden sich nicht nur im Namen, sondern
darin, wie sich die naechste Frist ergibt. Genau deshalb ist hier eine
Vererbungshierarchie modelliert und kein Aufzaehlungsattribut.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date

from .versuch import Versuch


class Pruefungsleistung(ABC):
    """Oberklasse aller Pruefungsformen eines Moduls.

    Die Versuche gehoeren ausschliesslich zu dieser Pruefungsleistung
    (Komposition). Nach aussen werden sie deshalb nur als unveraenderliches
    Tupel herausgegeben.
    """

    def __init__(self, gewichtung: float = 1.0) -> None:
        if not 0 < gewichtung <= 1.0:
            raise ValueError("Die Gewichtung muss groesser als 0 und hoechstens 1 sein")
        self.gewichtung = gewichtung
        self._versuche: list[Versuch] = []

    # -- Komposition ------------------------------------------------------

    def trage_versuch_ein(self, versuch: Versuch) -> None:
        """Nimmt einen Versuch auf.

        Raises:
            ValueError: Wenn die Versuchsnummer bereits belegt ist oder mehr
                als drei Versuche eingetragen wuerden.
        """
        if len(self._versuche) >= 3:
            raise ValueError("Es sind hoechstens drei Versuche moeglich")
        if any(v.nummer == versuch.nummer for v in self._versuche):
            raise ValueError(f"Versuch {versuch.nummer} ist bereits eingetragen")
        self._versuche.append(versuch)

    @property
    def versuche(self) -> tuple[Versuch, ...]:
        """Alle Versuche in der Reihenfolge ihrer Nummer."""
        return tuple(sorted(self._versuche, key=lambda v: v.nummer))

    # -- Abgeleitete Attribute -------------------------------------------

    @property
    def bester_versuch(self) -> Versuch | None:
        """Der Versuch mit der besten Note, oder None ohne Versuche."""
        if not self._versuche:
            return None
        return min(self._versuche, key=lambda v: v.note.wert)

    @property
    def bestanden_am(self) -> date | None:
        """Datum des fruehesten bestandenen Versuchs."""
        bestandene = [versuch for versuch in self._versuche if versuch.ist_bestanden]
        return min(versuch.datum for versuch in bestandene) if bestandene else None

    @property
    def ist_bestanden(self) -> bool:
        """True, wenn mindestens ein Versuch bestanden wurde."""
        return any(versuch.ist_bestanden for versuch in self._versuche)

    # -- Abstrakter Vertrag ----------------------------------------------

    @abstractmethod
    def naechste_frist(self, stichtag: date) -> date | None:
        """Liefert die naechste fachlich relevante Frist ab dem Stichtag.

        Jede Pruefungsform beantwortet diese Frage anders. Genau darin liegt
        der Grund fuer die Vererbung.
        """

    @abstractmethod
    def art(self) -> str:
        """Bezeichnung der Pruefungsform fuer die Anzeige."""

    @property
    @abstractmethod
    def endfrist(self) -> date:
        """Letzte Frist dieser Leistung, unabhaengig vom Stichtag.

        Wird gebraucht, um eine verstrichene Frist von einer fehlenden
        Terminangabe unterscheiden zu koennen.
        """

    def __str__(self) -> str:
        """Die Unterklasse benennt die Pruefungsform, ein eigenes
        Bezeichnungsfeld wuerde diese Information nur wiederholen."""
        return f"{self.art()} ({self.endfrist:%d.%m.%Y})"


class Klausur(Pruefungsleistung):
    """Klausur mit einem festen Pruefungstermin."""

    def __init__(
        self,
        pruefungstermin: date,
        dauer_minuten: int = 90,
        ist_onlineklausur: bool = True,
        gewichtung: float = 1.0,
    ) -> None:
        super().__init__(gewichtung)
        self.pruefungstermin = pruefungstermin
        self.dauer_minuten = dauer_minuten
        self.ist_onlineklausur = ist_onlineklausur

    def naechste_frist(self, stichtag: date) -> date | None:
        return self.pruefungstermin if self.pruefungstermin >= stichtag else None

    @property
    def endfrist(self) -> date:
        return self.pruefungstermin

    def art(self) -> str:
        return "Klausur"


class Portfolio(Pruefungsleistung):
    """Portfolio mit mehreren Phasenfristen.

    Die naechste Frist ist die frueheste noch offene Phasenfrist. Damit ist
    diese Klasse das beste Beispiel dafuer, warum ein einzelnes Datumsfeld in
    der Oberklasse nicht gereicht haette.
    """

    def __init__(
        self,
        phasenfristen: list[date],
        gewichtung: float = 1.0,
    ) -> None:
        super().__init__(gewichtung)
        if not phasenfristen:
            raise ValueError("Ein Portfolio braucht mindestens eine Phasenfrist")
        self.phasenfristen = tuple(sorted(phasenfristen))

    @property
    def anzahl_phasen(self) -> int:
        return len(self.phasenfristen)

    def aktuelle_phase(self, stichtag: date) -> int:
        """Nummer der Phase, an der am Stichtag gearbeitet wird."""
        vergangen = sum(1 for frist in self.phasenfristen if frist < stichtag)
        return min(vergangen + 1, self.anzahl_phasen)

    def naechste_frist(self, stichtag: date) -> date | None:
        offene = [frist for frist in self.phasenfristen if frist >= stichtag]
        return offene[0] if offene else None

    @property
    def endfrist(self) -> date:
        return self.phasenfristen[-1]

    def art(self) -> str:
        return "Portfolio"


class Fallstudie(Pruefungsleistung):
    """Schriftliche Ausarbeitung mit einer einzigen Abgabefrist."""

    def __init__(
        self,
        abgabefrist: date,
        thema: str = "",
        gewichtung: float = 1.0,
    ) -> None:
        super().__init__(gewichtung)
        self.abgabefrist = abgabefrist
        self.thema = thema

    def naechste_frist(self, stichtag: date) -> date | None:
        return self.abgabefrist if self.abgabefrist >= stichtag else None

    @property
    def endfrist(self) -> date:
        return self.abgabefrist

    def art(self) -> str:
        return "Fallstudie"
