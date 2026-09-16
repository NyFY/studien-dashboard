"""Datentransportobjekte zwischen Controller und Oberflaeche.

Der Controller koennte seine Ergebnisse auch als Woerterbuch liefern. Dann
waere aber nirgends festgehalten, welche Schluessel es gibt und welchen Typ
sie haben. Die folgenden Klassen beschreiben die Schnittstelle ausdruecklich.
Sie enthalten keine Fachlogik.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

from .ergebnis import Zielbewertung


@dataclass(frozen=True, slots=True)
class Kennzahlen:
    """Alle Zahlen, die die Studienziele zur Bewertung brauchen."""

    ects_ist: int
    ects_soll: float
    ects_gesamt: int
    notendurchschnitt: float | None
    benoetigter_restschnitt: float | None
    offene_module: int
    aeltestes_modul_tage: int
    aeltestes_modul_kuerzel: str | None
    prognose_datum: date | None
    zieldatum: date
    tage_verzug: int

    @property
    def ects_abweichung(self) -> float:
        """Vorsprung oder Rueckstand gegenueber dem Sollstand."""
        return self.ects_ist - self.ects_soll


@dataclass(frozen=True, slots=True)
class ModulZeile:
    """Eine Zeile der Modultabelle."""

    kuerzel: str
    bezeichnung: str
    ects: int
    status: str
    note: str
    naechste_frist: str
    offen_seit_tage: int | None
    ampel: str


@dataclass(frozen=True, slots=True)
class Verlaufspunkt:
    """Ein Punkt des ECTS-Verlaufs."""

    tag: int
    datum: date
    ects: int


@dataclass(frozen=True, slots=True)
class DashboardDaten:
    """Vollstaendiger Datensatz fuer eine Ansicht.

    Die Ansicht rechnet nichts mehr. Alles, was sie anzeigt, steht hier.
    """

    studiengang_titel: str
    abschluss: str
    studienbeginn: date
    zieldatum: date
    geplante_dauer_monate: int
    stichtag: date
    kennzahlen: Kennzahlen
    bewertungen: tuple[Zielbewertung, ...]
    offene_module: tuple[ModulZeile, ...]
    verlauf: tuple[Verlaufspunkt, ...]
    notenverteilung: tuple[tuple[str, int], ...] = field(default_factory=tuple)
    anzahl_bewertet: int = 0
    notenschnitt_band: int = -1     # Index in notenverteilung, -1 wenn ohne Note

    @property
    def tag_im_studium(self) -> int:
        return (self.stichtag - self.studienbeginn).days
