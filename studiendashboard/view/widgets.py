"""Wiederverwendbare Bausteine der grafischen Oberflaeche.

Jeder Baustein kuemmert sich um genau eine Darstellung und rechnet nichts.
Alle Werte kommen fertig aus dem Datentransportobjekt.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from ..dto import DashboardDaten, Kennzahlen, Verlaufspunkt, Zielbewertung

DUNKEL = "#082540"
AKZENT = "#4B91B9"
HELL = "#EAF5FA"
GRAU = "#6B7885"
RASTER = "#E4EAEF"
WEISS = "#FFFFFF"


class KennzahlKachel(ttk.Frame):
    """Kachel fuer ein Studienziel mit farbigem Statusbalken."""

    def __init__(self, eltern: tk.Misc, bewertung: Zielbewertung, nummer: int) -> None:
        super().__init__(eltern, style="Kachel.TFrame", padding=0)
        farbe = bewertung.ampel.farbe

        tk.Frame(self, background=farbe, height=6).pack(fill="x")
        #: Innenbereich der Kachel, an den weitere Bausteine gehaengt werden koennen.
        self.innen = ttk.Frame(self, style="Innen.TFrame", padding=(16, 8, 16, 10))
        self.innen.pack(fill="both", expand=True)
        innen = self.innen

        ttk.Label(innen, text=f"ZIEL {nummer}", style="Etikett.TLabel").pack(anchor="w")
        ttk.Label(innen, text=bewertung.titel, style="Kacheltitel.TLabel").pack(
            anchor="w", pady=(1, 6)
        )

        wertzeile = ttk.Frame(innen, style="Innen.TFrame")
        wertzeile.pack(anchor="w", fill="x")
        ttk.Label(wertzeile, text=bewertung.kennwert, style="Grosswert.TLabel").pack(side="left")
        ttk.Label(wertzeile, text="  " + bewertung.zusatz, style="Zusatz.TLabel").pack(
            side="left", anchor="s", pady=(0, 6)
        )

        hinweis = ttk.Label(innen, text=bewertung.hinweis, wraplength=330, justify="left")
        hinweis.configure(foreground=farbe, font=("Helvetica", 9, "bold"))
        hinweis.pack(anchor="w", pady=(6, 0))


class Fortschrittsbalken(tk.Canvas):
    """Waagerechter Balken mit einer Marke fuer den Sollstand."""

    def __init__(self, eltern: tk.Misc, kennzahlen: Kennzahlen, breite: int = 340) -> None:
        super().__init__(eltern, width=breite, height=32, background=WEISS, highlightthickness=0)
        self._kennzahlen = kennzahlen
        self._breite = breite
        self.bind("<Configure>", lambda _ereignis: self._zeichne())
        self._zeichne()

    def _zeichne(self) -> None:
        self.delete("all")
        breite = max(self.winfo_width(), self._breite)
        anteil = self._kennzahlen.ects_ist / self._kennzahlen.ects_gesamt
        soll = self._kennzahlen.ects_soll / self._kennzahlen.ects_gesamt

        self.create_rectangle(0, 14, breite, 30, fill="#EDF1F4", outline="")
        self.create_rectangle(0, 14, breite * anteil, 30, fill=AKZENT, outline="")
        marke = breite * soll
        self.create_line(marke, 8, marke, 34, fill=DUNKEL, width=2)
        self.create_text(
            marke, 4, text=f"Soll {self._kennzahlen.ects_soll:.0f}", anchor="s",
            font=("Helvetica", 8, "bold"), fill=DUNKEL,
        )


class BurnUpDiagramm(tk.Canvas):
    """Verlauf der bestandenen ECTS mit Sollgerade und Prognose."""

    RAND = (58, 22, 96, 34)  # links, oben, rechts, unten

    def __init__(self, eltern: tk.Misc, daten: DashboardDaten) -> None:
        super().__init__(eltern, background=WEISS, highlightthickness=0, height=170)
        self._daten = daten
        self.bind("<Configure>", lambda _ereignis: self._zeichne())

    # -- Umrechnung Datenraum in Bildschirmkoordinaten --------------------

    def _x(self, tag: float) -> float:
        links, _, rechts, _ = self.RAND
        gesamt = (self._daten.zieldatum - self._daten.studienbeginn).days
        nutzbar = max(self.winfo_width() - links - rechts, 10)
        return links + nutzbar * min(tag / gesamt, 1.15)

    def _y(self, ects: float) -> float:
        _, oben, _, unten = self.RAND
        nutzbar = max(self.winfo_height() - oben - unten, 10)
        gesamt = self._daten.kennzahlen.ects_gesamt
        return self.winfo_height() - unten - nutzbar * ects / gesamt

    def _zeichne(self) -> None:
        self.delete("all")
        daten = self._daten
        gesamt_tage = (daten.zieldatum - daten.studienbeginn).days
        gesamt_ects = daten.kennzahlen.ects_gesamt

        for ects in range(0, gesamt_ects + 1, 45):
            y = self._y(ects)
            self.create_line(self.RAND[0], y, self._x(gesamt_tage), y, fill=RASTER)
            self.create_text(self.RAND[0] - 8, y, text=str(ects), anchor="e",
                             font=("Helvetica", 8), fill=GRAU)
        # Die Achse richtet sich nach dem Zeitmodell: 36, 48 oder 72 Monate.
        monate_gesamt = max(daten.geplante_dauer_monate, 1)
        schritt = 6 if monate_gesamt <= 48 else 12
        for monat in range(0, monate_gesamt + 1, schritt):
            tag = round(gesamt_tage * monat / monate_gesamt)
            self.create_text(self._x(tag), self._y(0) + 14, text=f"M{monat}", anchor="n",
                             font=("Helvetica", 8), fill=GRAU)

        self.create_line(self.RAND[0], self._y(gesamt_ects), self.RAND[0], self._y(0), fill="#9AA5B1")
        self.create_line(self.RAND[0], self._y(0), self._x(gesamt_tage), self._y(0), fill="#9AA5B1")
        self.create_text(self.RAND[0] - 8, self._y(gesamt_ects) - 12, text="ECTS", anchor="e",
                         font=("Helvetica", 9, "bold"), fill=DUNKEL)

        # Sollgerade
        self.create_line(self._x(0), self._y(0), self._x(gesamt_tage), self._y(gesamt_ects),
                         fill="#9AA5B1", width=2)
        self.create_text(self._x(gesamt_tage * 0.62) + 4, self._y(gesamt_ects * 0.62) - 10,
                         text="Soll", font=("Helvetica", 9, "bold"), fill=GRAU)

        # Istverlauf
        punkte = self._istpunkte(daten.verlauf)
        if len(punkte) >= 2:
            self.create_line(*punkte, fill=AKZENT, width=3)
        for eintrag in daten.verlauf:
            x, y = self._x(eintrag.tag), self._y(eintrag.ects)
            self.create_oval(x - 3, y - 3, x + 3, y + 3, fill=AKZENT, outline="")

        # Prognose
        if daten.kennzahlen.prognose_datum is not None:
            letzter = daten.verlauf[-1]
            ziel_tag = (daten.kennzahlen.prognose_datum - daten.studienbeginn).days
            farbe = "#C62828" if daten.kennzahlen.tage_verzug > 0 else "#2E7D32"
            self.create_line(self._x(letzter.tag), self._y(letzter.ects),
                             self._x(ziel_tag), self._y(gesamt_ects),
                             fill=farbe, width=2, dash=(6, 4))
            self.create_text(
                self._x(gesamt_tage) + 8, self._y(gesamt_ects) + 16, anchor="nw",
                text=f"Prognose\n{daten.kennzahlen.prognose_datum:%d.%m.%Y}",
                font=("Helvetica", 8, "bold"), fill=farbe,
            )

        # Zielpunkt
        x, y = self._x(gesamt_tage), self._y(gesamt_ects)
        self.create_oval(x - 4, y - 4, x + 4, y + 4, outline=DUNKEL, width=2)
        self.create_text(x + 6, y - 8, text="Ziel", anchor="w",
                         font=("Helvetica", 9, "bold"), fill=DUNKEL)

    def _istpunkte(self, verlauf: tuple[Verlaufspunkt, ...]) -> list[float]:
        return [
            wert
            for eintrag in verlauf
            for wert in (self._x(eintrag.tag), self._y(eintrag.ects))
        ]


class Notenverteilung(tk.Canvas):
    """Saeulendiagramm der bestandenen Module je Notenband."""

    def __init__(self, eltern: tk.Misc, daten: DashboardDaten) -> None:
        super().__init__(eltern, background=WEISS, highlightthickness=0, height=170)
        self._daten = daten
        self.bind("<Configure>", lambda _ereignis: self._zeichne())

    def _zeichne(self) -> None:
        self.delete("all")
        verteilung = self._daten.notenverteilung
        if not verteilung:
            return

        breite, hoehe = self.winfo_width(), self.winfo_height()
        rand_unten, rand_oben = 34, 34
        hoechster = max(anzahl for _, anzahl in verteilung) or 1
        saeulenbreite = max((breite - 60) / len(verteilung) * 0.6, 8)
        abstand = (breite - 60) / len(verteilung)
        grundlinie = hoehe - rand_unten

        for stelle, (etikett, anzahl) in enumerate(verteilung):
            x = 40 + stelle * abstand + (abstand - saeulenbreite) / 2
            saeulenhoehe = (hoehe - rand_unten - rand_oben) * anzahl / hoechster
            self.create_rectangle(
                x, grundlinie - saeulenhoehe, x + saeulenbreite, grundlinie,
                fill=AKZENT if anzahl else "#E4EAEF", outline="",
            )
            self.create_text(x + saeulenbreite / 2, grundlinie - saeulenhoehe - 8,
                             text=str(anzahl), font=("Helvetica", 9, "bold"), fill=DUNKEL)
            self.create_text(x + saeulenbreite / 2, grundlinie + 14, text=etikett,
                             font=("Helvetica", 8), fill=GRAU)

        self.create_line(24, grundlinie, breite - 16, grundlinie, fill="#9AA5B1")

        schnitt = self._daten.kennzahlen.notendurchschnitt
        stelle = self._daten.notenschnitt_band
        if schnitt is not None and stelle >= 0:
            x = 40 + stelle * abstand + (abstand - saeulenbreite) / 2 - 6
            self.create_line(x, rand_oben - 12, x, grundlinie, fill="#2E7D32", width=2, dash=(4, 3))
            self.create_text(breite - 16, 12, anchor="e",
                             text=f"Ø {schnitt:.2f}".replace(".", ","),
                             font=("Helvetica", 9, "bold"), fill="#2E7D32")


class Modultabelle(ttk.Frame):
    """Tabelle der offenen Module mit Frist, Alter und Ampel."""

    SPALTEN = (
        ("kuerzel", "Kürzel", 148, "w"),
        ("modul", "Modul", 400, "w"),
        ("ects", "ECTS", 52, "center"),
        ("status", "Status", 126, "w"),
        ("note", "Note", 52, "center"),
        ("frist", "Nächste Frist", 216, "w"),
        ("alter", "Offen seit", 82, "center"),
    )

    def __init__(self, eltern: tk.Misc, daten: DashboardDaten) -> None:
        super().__init__(eltern)
        self.tabelle = ttk.Treeview(
            self, columns=[s[0] for s in self.SPALTEN], show="headings",
            height=max(len(daten.offene_module), 3),
        )
        for name, ueberschrift, breite, ausrichtung in self.SPALTEN:
            self.tabelle.heading(name, text=ueberschrift)
            self.tabelle.column(name, width=breite, anchor=ausrichtung, stretch=(name == "modul"))

        for farbe in ("gruen", "gelb", "rot"):
            self.tabelle.tag_configure(farbe, foreground={"gruen": "#2E7D32",
                                                          "gelb": "#8A6100",
                                                          "rot": "#C62828"}[farbe])

        for zeile in daten.offene_module:
            self.tabelle.insert(
                "", "end", tags=(zeile.ampel,),
                values=(
                    zeile.kuerzel, zeile.bezeichnung, zeile.ects, zeile.status, zeile.note,
                    zeile.naechste_frist,
                    f"{zeile.offen_seit_tage} Tage" if zeile.offen_seit_tage is not None else "–",
                ),
            )
        self.tabelle.pack(fill="both", expand=True)
