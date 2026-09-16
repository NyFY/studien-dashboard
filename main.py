"""Startskript des Studien-Dashboards.

Aufruf:
    python main.py                      Fenster mit dem heutigen Stichtag
    python main.py --konsole            Ausgabe auf der Kommandozeile
    python main.py --stichtag 2026-08-18
    python main.py --zuruecksetzen      Beispieldaten neu anlegen
    python main.py -h                   zeigt alle Schalter
"""

from __future__ import annotations

import sys

from studiendashboard.app import main

if __name__ == "__main__":
    sys.exit(main())
