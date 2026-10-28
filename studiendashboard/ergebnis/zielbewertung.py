"""Ergebnis der Bewertung eines Studienziels."""

from __future__ import annotations

from dataclasses import dataclass

from .ampel import Ampel


@dataclass(frozen=True, slots=True)
class Zielbewertung:
    """Was beim Bewerten eines Studienziels herauskommt.

    Die Ampel allein reicht nicht. Eine rote Ampel ohne Zahl und ohne Satz
    dazu sagt mir nicht, was ich tun soll. Diese Klasse ist in Phase 2 aus
    genau diesem Grund hinzugekommen und haelt beides beieinander.

    Sie ist unveraenderlich, weil eine Bewertung die Lage zu einem Stichtag
    beschreibt. Wer sie aendern will, bewertet neu.
    """

    titel: str
    kennwert: str
    zusatz: str
    hinweis: str
    ampel: Ampel
