"""Fachliche Berechnungen, die mehrere Domaenenobjekte betreffen."""

from .fortschritts_service import FortschrittsService
from .noten_service import NOTENBAENDER, NotenService

__all__ = ["NOTENBAENDER", "FortschrittsService", "NotenService"]
