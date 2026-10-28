"""Erzeugt Studienziele aus gespeicherten Werten.

Die Zuordnung von Kennung zu Unterklasse steht nicht hier, sondern im
Verzeichnis der Oberklasse ``Studienziel``, in das sich jede Unterklasse beim
Erben selbst eintraegt. Diese Datei dispatcht nur noch darueber. Ein viertes
Studienziel ist damit wirklich eine neue Unterklasse und sonst nichts: Es gibt
keine Stelle mehr, die alle Zielarten aufzaehlt und mitwachsen muesste.
"""

from __future__ import annotations

from .notenziel import Notenziel
from .studienziel import Studienziel
from .wipziel import WipZiel
from .zeitziel import Zeitziel


def erzeuge_ziel(art: str, zielwert: float, toleranz: float, ist_aktiv: bool) -> Studienziel:
    """Baut das zur Kennung passende Studienziel.

    Raises:
        ValueError: Wenn keine Unterklasse diese Kennung traegt.
    """
    ziel = Studienziel.mit_kennung(art).aus_werten(zielwert, toleranz)
    ziel.ist_aktiv = ist_aktiv
    return ziel


def bedeutungen() -> dict[str, tuple[str, str]]:
    """Was zielwert und toleranz je Zielart bedeuten.

    Wird aus dem Verzeichnis gelesen und waechst deshalb mit einer neuen
    Unterklasse mit, ohne dass hier etwas nachgetragen wird.
    """
    return {
        kennung: klasse.bedeutung
        for kennung, klasse in sorted(Studienziel._arten.items())
    }


def standardziele(geplante_dauer_monate: int = 48) -> list[Studienziel]:
    """Die drei Ziele aus der Konzeptionsphase mit ihren Ausgangswerten.

    Nur die Erstbefuellung einer leeren Datenbank. Danach stehen die Ziele in
    der Tabelle ``studienziel`` und werden von dort gelesen.
    """
    return [
        Zeitziel(zielmonate=geplante_dauer_monate),
        Notenziel(zielnote=2.0),
        WipZiel(hoechstzahl=3),
    ]
