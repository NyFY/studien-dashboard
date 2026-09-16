"""Entity-Klasse Studiengang."""

from __future__ import annotations

import calendar
from datetime import date, timedelta

from .modul import Modul
from .note import Note, NOTENSTUFEN
from .semester import Semester


def addiere_monate(ausgangsdatum: date, monate: int) -> date:
    """Addiert Monate auf ein Datum, ohne Fremdbibliothek.

    Faellt der Zieltag im Zielmonat nicht an, wird auf den letzten Tag des
    Monats gekuerzt. Beispiel: Der 31. Maerz plus einen Monat ergibt den
    30. April.
    """
    monat_gesamt = ausgangsdatum.month - 1 + monate
    jahr = ausgangsdatum.year + monat_gesamt // 12
    monat = monat_gesamt % 12 + 1
    tag = min(ausgangsdatum.day, calendar.monthrange(jahr, monat)[1])
    return date(jahr, monat, tag)


class Studiengang:
    """Der belegte Studiengang als Wurzel des Objektgeflechts.

    Die Beziehung zu den Semestern ist eine Komposition. Der Studiengang
    erzeugt seine Semester im Konstruktor selbst und gibt sie nur als
    unveraenderliches Tupel heraus. Von aussen laesst sich damit kein
    Semester einhaengen oder entfernen.
    """

    def __init__(
        self,
        bezeichnung: str,
        abschluss: str,
        gesamt_ects: int,
        geplante_dauer_monate: int,
        studienbeginn: date,
        anzahl_semester: int = 6,
    ) -> None:
        if gesamt_ects <= 0:
            raise ValueError("Ein Studiengang braucht mindestens einen ECTS-Punkt")
        if geplante_dauer_monate <= 0:
            raise ValueError("Die geplante Studiendauer muss groesser als null sein")
        if anzahl_semester <= 0:
            raise ValueError("Ein Studiengang braucht mindestens ein Semester")

        self.bezeichnung = bezeichnung
        self.abschluss = abschluss
        self.gesamt_ects = gesamt_ects
        self.geplante_dauer_monate = geplante_dauer_monate
        self.studienbeginn = studienbeginn

        # Die Semestergrenzen werden gleichmaessig ueber die geplante Dauer
        # verteilt. Bei Teilzeit I dauert ein Semester acht statt sechs Monate,
        # der Lehrplan bleibt derselbe.
        def grenze(nummer: int) -> date:
            monate = round(geplante_dauer_monate * nummer / anzahl_semester)
            return addiere_monate(studienbeginn, monate)

        self._semester: tuple[Semester, ...] = tuple(
            Semester(nummer=nummer, beginn=grenze(nummer - 1), ende=grenze(nummer))
            for nummer in range(1, anzahl_semester + 1)
        )

    # -- Komposition ------------------------------------------------------

    @property
    def semester(self) -> tuple[Semester, ...]:
        """Alle Semester des Studiengangs, nur lesend."""
        return self._semester

    def semester_mit_nummer(self, nummer: int) -> Semester:
        """Liefert das Semester mit der angegebenen Nummer."""
        for semester in self._semester:
            if semester.nummer == nummer:
                return semester
        raise KeyError(f"Semester {nummer} gibt es in diesem Studiengang nicht")

    # -- Zugriff auf die Module ------------------------------------------

    @property
    def module(self) -> tuple[Modul, ...]:
        """Alle Module ueber alle Semester hinweg."""
        return tuple(modul for semester in self._semester for modul in semester.module)

    @property
    def bestandene_module(self) -> tuple[Modul, ...]:
        return tuple(modul for modul in self.module if modul.ist_bestanden)

    def bestandene_module_bis(self, stichtag: date) -> tuple[Modul, ...]:
        """Module, die zum Stichtag bereits bestanden waren.

        Ohne diese Einschraenkung wuerde eine Auswertung mit einem Stichtag in
        der Vergangenheit ECTS mitzaehlen, die damals noch gar nicht erreicht
        waren.
        """
        return tuple(modul for modul in self.module if modul.war_bestanden_am(stichtag))

    @property
    def offene_module(self) -> tuple[Modul, ...]:
        """Module, die begonnen, aber noch nicht abgeschlossen sind."""
        return tuple(modul for modul in self.module if modul.status.bindet_aufmerksamkeit)

    def offene_module_am(self, stichtag: date) -> tuple[Modul, ...]:
        """Module, die am Stichtag bereits begonnen und noch offen waren.

        Ein Modul, dessen Bearbeitung erst nach dem Stichtag begonnen hat,
        band an diesem Tag noch keine Aufmerksamkeit und zaehlt deshalb nicht
        gegen das Work-in-Progress-Limit.
        """
        return tuple(
            modul
            for modul in self.offene_module
            if modul.begonnen_am is None or modul.begonnen_am <= stichtag
        )

    # -- Abgeleitete Attribute -------------------------------------------

    @property
    def erreichte_ects(self) -> int:
        """Summe der ECTS aller bestandenen Module."""
        return sum(modul.ects for modul in self.bestandene_module)

    def erreichte_ects_bis(self, stichtag: date) -> int:
        """Summe der ECTS, die zum Stichtag bereits erreicht waren."""
        return sum(modul.ects for modul in self.bestandene_module_bis(stichtag))

    @property
    def notendurchschnitt(self) -> float | None:
        """ECTS-gewichteter Notendurchschnitt aller bestandenen Module.

        Entspricht dem abgeleiteten Attribut ``/notendurchschnitt`` aus dem
        Klassendiagramm. Der Wert bleibt ungerundet, damit Folgerechnungen
        keinen Rundungsfehler mitschleppen.
        """
        return self.notendurchschnitt_bis(date.max)

    def notendurchschnitt_bis(self, stichtag: date) -> float | None:
        """Notendurchschnitt ueber die zum Stichtag bestandenen Module."""
        bewertet = [
            (modul.ects, modul.note.wert)
            for modul in self.bestandene_module_bis(stichtag)
            if modul.note is not None
        ]
        if not bewertet:
            return None
        gewicht = sum(ects for ects, _ in bewertet)
        return sum(ects * wert for ects, wert in bewertet) / gewicht

    def voraussichtliche_abschlussnote(self) -> Note | None:
        """Der Durchschnitt, gerundet auf die naechste gueltige Notenstufe."""
        schnitt = self.notendurchschnitt
        if schnitt is None:
            return None
        return Note(min(NOTENSTUFEN, key=lambda stufe: abs(stufe - schnitt)))

    @property
    def zieldatum(self) -> date:
        """Letzter Tag der geplanten Studiendauer.

        Die Dauer haengt vom gewaehlten Zeitmodell ab: 36 Monate in Vollzeit,
        48 in Teilzeit I, 72 in Teilzeit II. Bei Studienbeginn am 01.10.2024
        und 48 Monaten ist das der 30.09.2028, also der Tag vor dem
        Monatswechsel.
        """
        return addiere_monate(self.studienbeginn, self.geplante_dauer_monate) - timedelta(days=1)

    @property
    def tage_geplante_dauer(self) -> int:
        """Anzahl Tage zwischen Studienbeginn und Zieldatum."""
        return (self.zieldatum - self.studienbeginn).days

    def __repr__(self) -> str:
        return f"Studiengang({self.bezeichnung!r}, {self.erreichte_ects}/{self.gesamt_ects} ECTS)"
