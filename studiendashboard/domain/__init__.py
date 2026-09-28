"""Fachklassen des Studien-Dashboards.

Dieses Paket enthaelt ausschliesslich die Entity-Klassen aus der
Konzeptionsphase. Es kennt weder Datenbank noch Oberflaeche.
"""

from .abschluss import Abschluss
from .modul import Modul
from .modulstatus import Modulstatus
from .note import NOTENSTUFEN, Note
from .pruefungsleistung import Fallstudie, Klausur, Portfolio, Pruefungsleistung
from .semester import Semester
from .studiengang import Studiengang, addiere_monate
from .versuch import Versuch

__all__ = [
    "NOTENSTUFEN", "Abschluss", "Fallstudie", "Klausur", "Modul", "Modulstatus", "Note",
    "Portfolio", "Pruefungsleistung", "Semester", "Studiengang", "Versuch",
    "addiere_monate",
]
