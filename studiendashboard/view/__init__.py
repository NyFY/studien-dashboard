"""Darstellung des Dashboards.

Das Paket enthaelt zwei austauschbare Ansichten. Die Fensterfassung wird erst
beim Zugriff geladen, damit das Programm auch auf Systemen ohne tkinter
lauffaehig bleibt.
"""

from .dashboard_view import DashboardView
from .konsolen_view import KonsolenView

__all__ = ["DashboardView", "KonsolenView", "TkDashboardView"]


def __getattr__(name: str):
    """Laedt die tkinter-Ansicht verzoegert (PEP 562)."""
    if name == "TkDashboardView":
        from .tk_dashboard_view import TkDashboardView

        return TkDashboardView
    raise AttributeError(f"{__name__} kennt kein Attribut {name!r}")
