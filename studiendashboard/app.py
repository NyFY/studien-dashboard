"""Startpunkt und Verdrahtung der Schichten (Composition Root)."""

from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

from .controller import DashboardController
from .repository import (
    SQLiteStudiengangRepository, SpeicherStudiengangRepository,
    StudiengangRepository, erzeuge_beispielstudiengang,
)
from .service import FortschrittsService, NotenService
from .view import DashboardView, KonsolenView
from .ziele import Studienziel, standardziele

STANDARD_DATENBANK = Path("daten") / "studium.db"


class DashboardApp:
    """Erzeugt alle Objekte, verbindet sie und startet die Anzeige.

    Nur an dieser Stelle wird entschieden, welche Speicherung und welche
    Ansicht zum Einsatz kommen. Alle anderen Klassen kennen ausschliesslich
    die abstrakten Oberklassen.
    """

    def __init__(
        self,
        datenbankpfad: Path | str = STANDARD_DATENBANK,
        im_speicher: bool = False,
        zielnote: float | None = None,
        wip_grenze: int | None = None,
    ) -> None:
        self.datenbankpfad = Path(datenbankpfad)
        self.im_speicher = im_speicher
        # None bedeutet: den gespeicherten Wert verwenden.
        self.zielnote = zielnote
        self.wip_grenze = wip_grenze

    # -- Verdrahtung ------------------------------------------------------

    def erzeuge_repository(self, zuruecksetzen: bool = False) -> StudiengangRepository:
        """Waehlt die Speicherung und legt beim ersten Start Beispieldaten an."""
        if self.im_speicher:
            return SpeicherStudiengangRepository(erzeuge_beispielstudiengang())

        if zuruecksetzen and self.datenbankpfad.exists():
            self.datenbankpfad.unlink()

        repository = SQLiteStudiengangRepository(self.datenbankpfad)
        if repository.ist_leer():
            studiengang = erzeuge_beispielstudiengang()
            repository.speichere(studiengang)
            repository.speichere_ziele(standardziele(studiengang.geplante_dauer_monate))
        return repository

    def erzeuge_ziele(
        self, repository: StudiengangRepository, geplante_dauer_monate: int
    ) -> list[Studienziel]:
        """Laedt die gespeicherten Studienziele.

        Sind noch keine hinterlegt, werden die drei Ziele aus der
        Konzeptionsphase angelegt. Aufrufparameter auf der Kommandozeile
        ueberschreiben den gespeicherten Wert fuer diesen einen Programmlauf.
        """
        ziele = repository.lade_ziele()
        if not ziele:
            ziele = standardziele(geplante_dauer_monate)
            repository.speichere_ziele(ziele)

        for ziel in ziele:
            if self.zielnote is not None and ziel.art == "notenziel":
                ziel.zielwert = self.zielnote
            if self.wip_grenze is not None and ziel.art == "wipziel":
                ziel.zielwert = self.wip_grenze
        return ziele

    def erzeuge_ansicht(self, oberflaeche: str, schliesse_nach_ms: int | None = None) -> DashboardView:
        """Liefert die gewuenschte Ansicht, mit Rueckfall auf die Konsole.

        Geprueft wird nicht nur, ob tkinter installiert ist, sondern auch, ob
        sich tatsaechlich ein Fenster oeffnen laesst. Auf einem Rechner ohne
        Bildschirm, etwa ueber eine SSH-Sitzung, ist tkinter vorhanden, aber
        nicht benutzbar.
        """
        if oberflaeche == "konsole":
            return KonsolenView()
        try:
            import tkinter

            pruefung = tkinter.Tk()
            pruefung.destroy()
        except ImportError:
            print("Hinweis: tkinter ist nicht verfügbar, es wird die Konsole verwendet.\n")
            return KonsolenView()
        except tkinter.TclError as fehler:
            print(f"Hinweis: Es lässt sich kein Fenster öffnen ({fehler}).")
            print("Es wird die Konsole verwendet.\n")
            return KonsolenView()

        from .view import TkDashboardView

        return TkDashboardView(schliesse_nach_ms=schliesse_nach_ms)

    # -- Ablauf -----------------------------------------------------------

    def start(
        self,
        stichtag: date | None = None,
        oberflaeche: str = "fenster",
        zuruecksetzen: bool = False,
        schliesse_nach_ms: int | None = None,
    ) -> None:
        """Startet das Dashboard."""
        repository = self.erzeuge_repository(zuruecksetzen)
        studiengang = repository.lade()
        ziele = self.erzeuge_ziele(repository, studiengang.geplante_dauer_monate)
        notenziel = next((z for z in ziele if z.art == "notenziel"), None)
        controller = DashboardController(
            repository=repository,
            fortschritts_service=FortschrittsService(),
            noten_service=NotenService(),
            ziele=ziele,
            zielnote=notenziel.zielwert if notenziel else 2.0,
        )
        daten = controller.lade_dashboard_daten(stichtag or date.today())
        self.erzeuge_ansicht(oberflaeche, schliesse_nach_ms).zeige(daten)


def lies_argumente(argumente: list[str] | None = None) -> argparse.Namespace:
    """Liest die Aufrufparameter von der Kommandozeile."""
    parser = argparse.ArgumentParser(
        prog="studiendashboard",
        description="Dashboard für den eigenen Studienfortschritt.",
    )
    parser.add_argument("--konsole", action="store_true",
                        help="Ausgabe auf der Kommandozeile statt im Fenster")
    parser.add_argument("--stichtag", metavar="JJJJ-MM-TT",
                        help="Bewertungsstichtag, Vorgabe ist heute")
    parser.add_argument("--datenbank", default=str(STANDARD_DATENBANK), metavar="PFAD",
                        help=f"Pfad zur Datenbankdatei, Vorgabe {STANDARD_DATENBANK}")
    parser.add_argument("--im-speicher", action="store_true",
                        help="ohne Datenbankdatei arbeiten, nichts wird gespeichert")
    parser.add_argument("--zuruecksetzen", action="store_true",
                        help="Datenbank löschen und mit Beispieldaten neu anlegen")
    parser.add_argument("--zielnote", type=float,
                        help="überschreibt die gespeicherte Zielnote für diesen Lauf")
    parser.add_argument("--wip-grenze", type=int,
                        help="überschreibt die gespeicherte Modulgrenze für diesen Lauf")
    parser.add_argument("--schliesse-nach", type=int, metavar="MS",
                        help="Fenster nach dieser Zeit automatisch schließen (für Tests)")
    return parser.parse_args(argumente)


def main(argumente: list[str] | None = None) -> int:
    """Einstiegspunkt des Programms."""
    # Sicherheitsnetz: Steht die Windows-Konsole auf einer Codepage, die ein
    # Zeichen nicht kennt, wird es ersetzt statt das Programm abzubrechen.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")

    gewaehlt = lies_argumente(argumente)
    try:
        stichtag = date.fromisoformat(gewaehlt.stichtag) if gewaehlt.stichtag else date.today()
    except ValueError:
        print(f"'{gewaehlt.stichtag}' ist kein gültiges Datum. Erwartet wird JJJJ-MM-TT.")
        return 2

    anwendung = DashboardApp(
        datenbankpfad=gewaehlt.datenbank,
        im_speicher=gewaehlt.im_speicher,
        zielnote=gewaehlt.zielnote,
        wip_grenze=gewaehlt.wip_grenze,
    )
    anwendung.start(
        stichtag=stichtag,
        oberflaeche="konsole" if gewaehlt.konsole else "fenster",
        zuruecksetzen=gewaehlt.zuruecksetzen,
        schliesse_nach_ms=gewaehlt.schliesse_nach,
    )
    return 0
