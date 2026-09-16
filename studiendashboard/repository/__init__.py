"""Speicherung des Studiengangs."""

from .demodaten import erzeuge_beispielstudiengang
from .speicher_studiengang_repository import SpeicherStudiengangRepository
from .sqlite_studiengang_repository import SQLiteStudiengangRepository
from .studiengang_repository import StudiengangRepository

__all__ = [
    "SQLiteStudiengangRepository", "SpeicherStudiengangRepository",
    "StudiengangRepository", "erzeuge_beispielstudiengang",
]
