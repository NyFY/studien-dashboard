"""Aufzaehlung Ampel."""

from __future__ import annotations

from enum import Enum


class Ampel(Enum):
    """Einordnung eines Studienziels in drei Stufen.

    Die Aufzaehlung traegt die Darstellung gleich mit: Jede Stufe weiss,
    welche Farbe und welches Zeichen zu ihr gehoeren. Die Ansichten muessen
    deshalb nicht selbst entscheiden, wie Gruen aussieht, und zwei Ansichten
    koennen nicht auseinanderlaufen.
    """

    GRUEN = "gruen"
    GELB = "gelb"
    ROT = "rot"

    @property
    def farbe(self) -> str:
        """Farbwert fuer Flaechen und Balken."""
        return {"gruen": "#2E7D32", "gelb": "#D89400", "rot": "#C62828"}[self.value]

    @property
    def schriftfarbe(self) -> str:
        """Farbwert fuer Text auf weissem Grund.

        Das Gelb der Flaechen ist als Schrift zu hell. Die dunklere Variante
        gehoert aus demselben Grund an die Aufzaehlung wie die helle: Sonst
        legt sie jede Ansicht fuer sich fest, und zwei Ansichten laufen
        auseinander.
        """
        return {"gruen": "#2E7D32", "gelb": "#8A6100", "rot": "#C62828"}[self.value]

    @property
    def zeichen(self) -> str:
        """Zeichen fuer die Ausgabe auf der Kommandozeile."""
        return {"gruen": "[ok]", "gelb": "[!]", "rot": "[X]"}[self.value]
