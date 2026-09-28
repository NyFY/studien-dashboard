"""Koordination zwischen Speicherung, Fachlogik und Anzeige."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import date

from ..domain import Modul
from ..dto import DashboardDaten, Kennzahlen, ModulZeile
from ..repository import StudiengangRepository
from ..service import FortschrittsService, NotenService
from ..ziele import Studienziel

#: Ab wie vielen Tagen ein offenes Modul in der Tabelle gelb bzw. rot wird.
_GELB_AB_TAGEN = 30
_ROT_AB_TAGEN = 90


class DashboardController:
    """Stellt aus allen Bausteinen den Datensatz fuer die Anzeige zusammen.

    Der Controller rechnet selbst nichts. Er holt den Studiengang beim
    Repository, laesst die Services rechnen, gibt die Kennzahlen an die
    Studienziele und packt das Ergebnis in ein Datentransportobjekt. Er kennt
    nur die abstrakte Repository-Klasse, nicht die konkrete Speicherung.
    """

    def __init__(
        self,
        repository: StudiengangRepository,
        fortschritts_service: FortschrittsService,
        noten_service: NotenService,
        ziele: Sequence[Studienziel],
        zielnote: float = 2.0,
    ) -> None:
        self.repository = repository
        self.fortschritts_service = fortschritts_service
        self.noten_service = noten_service
        self.ziele = tuple(ziele)
        self.zielnote = zielnote

    # -- oeffentliche Schnittstelle ---------------------------------------

    def lade_dashboard_daten(self, stichtag: date) -> DashboardDaten:
        """Liefert alles, was eine Ansicht zum Anzeigen braucht."""
        studiengang = self.repository.lade()
        kennzahlen = self._berechne_kennzahlen(studiengang, stichtag)

        bewertungen = tuple(
            ziel.bewerte(kennzahlen) for ziel in self.ziele if ziel.ist_aktiv
        )

        return DashboardDaten(
            studiengang_titel=studiengang.bezeichnung,
            abschluss=str(studiengang.abschluss),
            studienbeginn=studiengang.studienbeginn,
            zieldatum=studiengang.zieldatum,
            geplante_dauer_monate=studiengang.geplante_dauer_monate,
            stichtag=stichtag,
            kennzahlen=kennzahlen,
            bewertungen=bewertungen,
            offene_module=self._baue_modulzeilen(
                studiengang.offene_module_am(stichtag), stichtag
            ),
            verlauf=self.fortschritts_service.verlauf(studiengang, stichtag),
            notenverteilung=self.noten_service.verteilung(studiengang, stichtag),
            anzahl_bewertet=self.noten_service.anzahl_bewertet(studiengang, stichtag),
            notenschnitt_band=self.noten_service.band_index(kennzahlen.notendurchschnitt),
        )

    # -- interne Bausteine ------------------------------------------------

    def _berechne_kennzahlen(self, studiengang, stichtag: date) -> Kennzahlen:
        offene = studiengang.offene_module_am(stichtag)
        # Nur Module mit bekanntem Startdatum koennen ein Alter haben.
        mit_alter = [
            (modul, tage)
            for modul in offene
            if (tage := modul.offen_seit_tagen(stichtag)) is not None
        ]
        aeltestes, aeltestes_tage = max(
            mit_alter, key=lambda eintrag: eintrag[1], default=(None, 0)
        )

        return Kennzahlen(
            ects_ist=self.fortschritts_service.ist_ects(studiengang, stichtag),
            ects_soll=self.fortschritts_service.soll_ects(studiengang, stichtag),
            ects_gesamt=studiengang.gesamt_ects,
            notendurchschnitt=self.noten_service.durchschnitt(studiengang, stichtag),
            benoetigter_restschnitt=self.noten_service.benoetigter_restschnitt(
                studiengang, self.zielnote, stichtag
            ),
            offene_module=len(offene),
            aeltestes_modul_tage=aeltestes_tage,
            aeltestes_modul_kuerzel=aeltestes.kuerzel if aeltestes else None,
            prognose_datum=self.fortschritts_service.prognose(studiengang, stichtag),
            zieldatum=studiengang.zieldatum,
            tage_verzug=self.fortschritts_service.tage_verzug(studiengang, stichtag),
        )

    def _baue_modulzeilen(
        self, module: Sequence[Modul], stichtag: date
    ) -> tuple[ModulZeile, ...]:
        """Baut die Tabellenzeilen, aelteste offene Module zuerst."""
        sortiert = sorted(module, key=lambda m: m.offen_seit_tagen(stichtag) or 0, reverse=True)
        return tuple(self._baue_modulzeile(modul, stichtag) for modul in sortiert)

    def _baue_modulzeile(self, modul: Modul, stichtag: date) -> ModulZeile:
        tage = modul.offen_seit_tagen(stichtag)
        return ModulZeile(
            kuerzel=modul.kuerzel,
            bezeichnung=modul.bezeichnung,
            ects=modul.ects,
            status=str(modul.status),
            note=str(modul.note) if modul.note else "-",
            naechste_frist=self._fristtext(modul, stichtag),
            offen_seit_tage=tage,
            ampel=self._ampel_fuer_alter(tage),
        )

    @staticmethod
    def _fristtext(modul: Modul, stichtag: date) -> str:
        """Beschreibt die naechste Frist samt der zugehoerigen Pruefungsart.

        Es reicht nicht, das Datum und die Art getrennt zu ermitteln: Bei
        mehreren Pruefungsleistungen wuerden sonst die Art der einen und das
        Datum der anderen angezeigt.
        """
        if not modul.pruefungsleistungen:
            return "kein Termin hinterlegt"

        offene = [
            (leistung, frist)
            for leistung in modul.pruefungsleistungen
            if (frist := leistung.naechste_frist(stichtag)) is not None
        ]
        if offene:
            leistung, frist = min(offene, key=lambda eintrag: eintrag[1])
            return f"{leistung.art()} {frist:%d.%m.%Y}"

        # Alle Termine liegen in der Vergangenheit.
        letzte = max(modul.pruefungsleistungen, key=lambda leistung: leistung.endfrist)
        return f"{letzte.art()} {letzte.endfrist:%d.%m.%Y} verstrichen"

    @staticmethod
    def _ampel_fuer_alter(tage: int | None) -> str:
        if tage is None:
            return "gruen"
        if tage > _ROT_AB_TAGEN:
            return "rot"
        return "gelb" if tage > _GELB_AB_TAGEN else "gruen"
