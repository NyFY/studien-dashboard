"""Grafische Oberflaeche des Dashboards mit tkinter."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from ..dto import DashboardDaten
from .dashboard_view import DashboardView
from .widgets import (
    DUNKEL, GRAU, HELL, WEISS,
    BurnUpDiagramm, Fortschrittsbalken, KennzahlKachel, Modultabelle, Notenverteilung,
)


class TkDashboardView(DashboardView):
    """Fensterfassung des Dashboards.

    Die Klasse setzt das Fenster aus den Bausteinen im Modul ``widgets``
    zusammen und zeigt ausschliesslich Werte an, die im uebergebenen
    Datentransportobjekt stehen.
    """

    def __init__(self, titel: str = "Studien-Dashboard", schliesse_nach_ms: int | None = None) -> None:
        self.titel = titel
        self.schliesse_nach_ms = schliesse_nach_ms

    def zeige(self, daten: DashboardDaten) -> None:
        wurzel = tk.Tk()
        wurzel.title(self.titel)
        # Das Fenster passt sich an den Bildschirm an, damit es auch auf
        # kleineren Notebooks vollstaendig sichtbar bleibt.
        breite = min(1240, wurzel.winfo_screenwidth() - 60)
        hoehe = min(800, wurzel.winfo_screenheight() - 90)
        wurzel.geometry(f"{breite}x{hoehe}+20+20")
        wurzel.minsize(980, 620)
        wurzel.configure(background=HELL)
        self._setze_stile(wurzel)

        self._kopfzeile(wurzel, daten)
        self._kachelzeile(wurzel, daten)
        self._diagrammzeile(wurzel, daten)
        self._tabellenbereich(wurzel, daten)
        self._fusszeile(wurzel, daten)

        if self.schliesse_nach_ms is not None:
            wurzel.after(self.schliesse_nach_ms, wurzel.destroy)
        wurzel.mainloop()

    # -- Aufbau -----------------------------------------------------------

    @staticmethod
    def _setze_stile(wurzel: tk.Tk) -> None:
        stil = ttk.Style(wurzel)
        try:
            stil.theme_use("clam")
        except tk.TclError:          # falls das Thema auf dem System fehlt
            pass
        stil.configure("TFrame", background=WEISS)
        stil.configure("Kachel.TFrame", background=WEISS, relief="solid", borderwidth=1)
        stil.configure("Innen.TFrame", background=WEISS)
        stil.configure("Flaeche.TFrame", background=HELL)
        stil.configure("TLabel", background=WEISS, foreground=DUNKEL)
        stil.configure("Etikett.TLabel", font=("Helvetica", 8, "bold"), foreground=GRAU)
        stil.configure("Kacheltitel.TLabel", font=("Helvetica", 12, "bold"))
        stil.configure("Grosswert.TLabel", font=("Helvetica", 27, "bold"))
        stil.configure("Zusatz.TLabel", font=("Helvetica", 11), foreground=GRAU)
        stil.configure("Abschnitt.TLabel", font=("Helvetica", 12, "bold"))
        stil.configure("Klein.TLabel", font=("Helvetica", 9), foreground=GRAU)
        stil.configure("Treeview", rowheight=24, fieldbackground=WEISS, background=WEISS)
        stil.configure("Treeview.Heading", font=("Helvetica", 9, "bold"))

    def _kopfzeile(self, wurzel: tk.Tk, daten: DashboardDaten) -> None:
        kopf = tk.Frame(wurzel, background=DUNKEL)
        kopf.pack(fill="x", padx=14, pady=(12, 0))

        links = tk.Frame(kopf, background=DUNKEL)
        links.pack(side="left", padx=18, pady=10, anchor="w")
        tk.Label(links, text="Studien-Dashboard", background=DUNKEL, fg=WEISS,
                 font=("Helvetica", 18, "bold")).pack(anchor="w")
        tk.Label(
            links,
            text=(f"{daten.studiengang_titel}   ·   Studienbeginn "
                  f"{daten.studienbeginn:%d.%m.%Y}   ·   Zielabschluss "
                  f"{daten.zieldatum:%d.%m.%Y}   ·   {daten.kennzahlen.ects_gesamt} ECTS"),
            background=DUNKEL, fg="#9FC3D8", font=("Helvetica", 10),
        ).pack(anchor="w")

        rechts = tk.Frame(kopf, background=DUNKEL)
        rechts.pack(side="right", padx=18, pady=10, anchor="e")
        tk.Label(rechts, text=f"Stichtag {daten.stichtag:%d.%m.%Y}", background=DUNKEL,
                 fg=WEISS, font=("Helvetica", 11, "bold")).pack(anchor="e")
        tk.Label(rechts,
                 text=f"Tag {daten.tag_im_studium} von {(daten.zieldatum - daten.studienbeginn).days}",
                 background=DUNKEL, fg="#9FC3D8", font=("Helvetica", 10)).pack(anchor="e")

    def _kachelzeile(self, wurzel: tk.Tk, daten: DashboardDaten) -> None:
        zeile = tk.Frame(wurzel, background=HELL)
        zeile.pack(fill="x", padx=14, pady=(12, 0))
        for stelle, bewertung in enumerate(daten.bewertungen):
            zeile.columnconfigure(stelle, weight=1, uniform="kachel")
            kachel = KennzahlKachel(zeile, bewertung, stelle + 1)
            kachel.grid(row=0, column=stelle, sticky="nsew",
                        padx=(0 if stelle == 0 else 7, 0 if stelle == len(daten.bewertungen) - 1 else 7))
            if stelle == 0:
                Fortschrittsbalken(kachel.innen, daten.kennzahlen).pack(
                    fill="x", pady=(8, 0)
                )

    def _diagrammzeile(self, wurzel: tk.Tk, daten: DashboardDaten) -> None:
        zeile = tk.Frame(wurzel, background=HELL)
        zeile.pack(fill="both", expand=True, padx=14, pady=(10, 0))
        zeile.columnconfigure(0, weight=3)
        zeile.columnconfigure(1, weight=2)
        zeile.rowconfigure(0, weight=1)

        links = ttk.Frame(zeile, style="Kachel.TFrame", padding=(14, 10))
        links.grid(row=0, column=0, sticky="nsew", padx=(0, 7))
        ttk.Label(links, text="ECTS-Verlauf gegen Studienplan",
                  style="Abschnitt.TLabel").pack(anchor="w")
        ttk.Label(links, text="Ist, Soll und Prognose auf Basis der bisherigen Geschwindigkeit",
                  style="Klein.TLabel").pack(anchor="w", pady=(0, 4))
        BurnUpDiagramm(links, daten).pack(fill="both", expand=True)

        rechts = ttk.Frame(zeile, style="Kachel.TFrame", padding=(14, 10))
        rechts.grid(row=0, column=1, sticky="nsew", padx=(7, 0))
        anzahl = daten.anzahl_bewertet
        ttk.Label(rechts, text="Notenverteilung", style="Abschnitt.TLabel").pack(anchor="w")
        ttk.Label(rechts, text=f"{anzahl} bewertete Module",
                  style="Klein.TLabel").pack(anchor="w", pady=(0, 4))
        Notenverteilung(rechts, daten).pack(fill="both", expand=True)

    def _tabellenbereich(self, wurzel: tk.Tk, daten: DashboardDaten) -> None:
        bereich = ttk.Frame(wurzel, style="Kachel.TFrame", padding=(14, 10))
        bereich.pack(fill="both", expand=True, padx=14, pady=(10, 0))
        ttk.Label(bereich, text="Offene Module und nächste Fristen",
                  style="Abschnitt.TLabel").pack(anchor="w", pady=(0, 6))
        Modultabelle(bereich, daten).pack(fill="both", expand=True)

    def _fusszeile(self, wurzel: tk.Tk, daten: DashboardDaten) -> None:
        fuss = tk.Frame(wurzel, background=HELL)
        fuss.pack(fill="x", padx=14, pady=(8, 8))
        prognose = daten.kennzahlen.prognose_datum
        prognosetext = (
            f"Prognose {prognose:%d.%m.%Y}" if prognose else "Prognose noch nicht möglich"
        )
        tk.Label(
            fuss,
            text=(f"Datenquelle studium.db   ·   Datenstand {daten.stichtag:%d.%m.%Y}"
                  f"   ·   {len(daten.offene_module)} Module in Bearbeitung   ·   {prognosetext}"),
            background=HELL, fg=DUNKEL, font=("Helvetica", 9),
        ).pack(side="left")
        tk.Label(fuss, text="Beenden mit Fenster schließen", background=HELL,
                 fg=GRAU, font=("Helvetica", 9)).pack(side="right")
