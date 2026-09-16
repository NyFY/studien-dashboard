"""Ausgabe des Dashboards auf der Kommandozeile.

Die Ausgabe verwendet ausser den deutschen Umlauten keine Sonderzeichen.
Umlaute kennt jede westliche Windows-Codepage, Zeichen wie der Gedankenstrich
dagegen nicht. Damit laeuft die Konsolenfassung auch dann, wenn die Ausgabe
in eine Datei umgeleitet wird.
"""

from __future__ import annotations

from ..dto import DashboardDaten
from .dashboard_view import DashboardView

BREITE = 96


class KonsolenView(DashboardView):
    """Textfassung des Dashboards.

    Sie ist die Rueckfallebene, falls auf einem Rechner keine grafische
    Oberflaeche zur Verfuegung steht, und dient zugleich als Beleg dafuer,
    dass die Anzeige austauschbar ist.
    """

    def zeige(self, daten: DashboardDaten) -> None:
        self._kopf(daten)
        self._ziele(daten)
        self._verlauf(daten)
        self._notenverteilung(daten)
        self._module(daten)
        print("=" * BREITE)

    # -- Bausteine --------------------------------------------------------

    def _kopf(self, daten: DashboardDaten) -> None:
        print("=" * BREITE)
        print(f"STUDIEN-DASHBOARD   {daten.studiengang_titel}")
        print(
            f"Studienbeginn {daten.studienbeginn:%d.%m.%Y}   "
            f"Zielabschluss {daten.zieldatum:%d.%m.%Y}   "
            f"Stichtag {daten.stichtag:%d.%m.%Y}   "
            f"Tag {daten.tag_im_studium} von "
            f"{(daten.zieldatum - daten.studienbeginn).days}"
        )
        print("=" * BREITE)

    def _ziele(self, daten: DashboardDaten) -> None:
        for nummer, bewertung in enumerate(daten.bewertungen, start=1):
            print(f"\nZIEL {nummer}  {bewertung.ampel.zeichen}  {bewertung.titel}")
            print(f"         {bewertung.kennwert}  {bewertung.zusatz}")
            print(f"         {bewertung.hinweis}")

    def _verlauf(self, daten: DashboardDaten) -> None:
        kennzahlen = daten.kennzahlen
        anteil = kennzahlen.ects_ist / kennzahlen.ects_gesamt
        soll_anteil = kennzahlen.ects_soll / kennzahlen.ects_gesamt
        laenge = 60
        gefuellt = min(round(laenge * anteil), laenge)
        marke = round(laenge * soll_anteil)

        balken = ["-"] * laenge
        for stelle in range(gefuellt):
            balken[stelle] = "#"
        if 0 <= marke < laenge:
            balken[marke] = "|"

        print("\nECTS-FORTSCHRITT")
        print("  [" + "".join(balken) + "]")
        soll = f"{kennzahlen.ects_soll:.1f}".replace(".", ",")
        print(
            f"  {kennzahlen.ects_ist} von {kennzahlen.ects_gesamt} ECTS, "
            f"Sollstand heute {soll} (Marke |)"
        )

    def _notenverteilung(self, daten: DashboardDaten) -> None:
        if not daten.notenverteilung:
            return
        print(f"\nNOTENVERTEILUNG  ({daten.anzahl_bewertet} bewertete Module)")
        hoechster = max(anzahl for _, anzahl in daten.notenverteilung) or 1
        for etikett, anzahl in daten.notenverteilung:
            balken = "#" * round(30 * anzahl / hoechster)
            print(f"  {etikett:<9} {balken:<30} {anzahl}")

    def _module(self, daten: DashboardDaten) -> None:
        print("\nOFFENE MODULE UND NÄCHSTE FRISTEN")
        if not daten.offene_module:
            print("  Zurzeit ist kein Modul in Bearbeitung.")
            return
        kopf = f"  {'':<5}{'KÜRZEL':<16}{'MODUL':<44}{'ECTS':>5}  {'NÄCHSTE FRIST':<34}{'OFFEN':>8}"
        print(kopf)
        print("  " + "-" * (len(kopf) - 2))
        zeichen = {"gruen": "[ok]", "gelb": "[!]", "rot": "[X]"}
        for zeile in daten.offene_module:
            bezeichnung = (
                zeile.bezeichnung if len(zeile.bezeichnung) <= 43
                else zeile.bezeichnung[:40] + "..."
            )
            print(
                f"  {zeichen[zeile.ampel]:<5}{zeile.kuerzel:<16}{bezeichnung:<44}"
                f"{zeile.ects:>5}  {zeile.naechste_frist:<34}"
                f"{(str(zeile.offen_seit_tage) + ' Tage') if zeile.offen_seit_tage is not None else '-':>8}"
            )
