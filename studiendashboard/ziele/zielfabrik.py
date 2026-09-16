"""Erzeugt Studienziele aus gespeicherten Werten.

Diese Zuordnung ist die einzige Stelle, an der aus der gespeicherten Zielart
wieder die passende Unterklasse wird. Sie entspricht dem Vorgehen im
Repository, das aus der Spalte ``art`` die richtige Pruefungsform erzeugt.
"""

from __future__ import annotations

from .notenziel import Notenziel
from .studienziel import Studienziel
from .wipziel import WipZiel
from .zeitziel import Zeitziel

#: Bedeutung von zielwert und toleranz je Zielart.
BEDEUTUNG: dict[str, tuple[str, str]] = {
    "zeitziel": ("angestrebte Studiendauer in Monaten", "erlaubter Rueckstand in ECTS"),
    "notenziel": ("angestrebte Abschlussnote", "erlaubte Ueberschreitung"),
    "wipziel": ("hoechstens gleichzeitig offene Module", "hoechstes Alter in Tagen"),
}


def erzeuge_ziel(art: str, zielwert: float, toleranz: float, ist_aktiv: bool) -> Studienziel:
    """Baut das zur Art passende Studienziel.

    Raises:
        ValueError: Wenn die Zielart unbekannt ist.
    """
    if art == "zeitziel":
        ziel: Studienziel = Zeitziel(zielmonate=int(zielwert), toleranz_ects=toleranz)
    elif art == "notenziel":
        ziel = Notenziel(zielnote=zielwert, toleranz=toleranz)
    elif art == "wipziel":
        ziel = WipZiel(hoechstzahl=int(zielwert), hoechstalter_tage=int(toleranz))
    else:
        raise ValueError(f"Unbekannte Zielart: {art}")
    ziel.ist_aktiv = ist_aktiv
    return ziel


def standardziele(geplante_dauer_monate: int = 48) -> list[Studienziel]:
    """Die drei Ziele aus der Konzeptionsphase mit ihren Ausgangswerten."""
    return [
        Zeitziel(zielmonate=geplante_dauer_monate),
        Notenziel(zielnote=2.0),
        WipZiel(hoechstzahl=3),
    ]
