"""Repository auf Basis einer SQLite-Datenbankdatei."""

from __future__ import annotations

import sqlite3
from datetime import date
from pathlib import Path

from ..domain import (
    Abschluss, Fallstudie, Klausur, Modul, Modulstatus, Portfolio,
    Pruefungsleistung, Studiengang, Versuch,
)
from ..ziele import Studienziel, erzeuge_ziel
from .studiengang_repository import StudiengangRepository

SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS studiengang (
    id                      INTEGER PRIMARY KEY CHECK (id = 1),
    bezeichnung             TEXT    NOT NULL,
    abschluss               TEXT    NOT NULL,
    gesamt_ects             INTEGER NOT NULL,
    geplante_dauer_monate INTEGER NOT NULL,
    studienbeginn           TEXT    NOT NULL,
    anzahl_semester         INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS modul (
    kuerzel         TEXT    PRIMARY KEY,
    bezeichnung     TEXT    NOT NULL,
    ects            INTEGER NOT NULL,
    status          TEXT    NOT NULL,
    begonnen_am     TEXT,
    -- Multiplizitaet 0..1 aus dem Klassendiagramm: Ein Modul aus dem
    -- Modulhandbuch darf noch keinem Semester zugeordnet sein.
    semester_nummer INTEGER
);

-- ON DELETE CASCADE bildet die Komposition aus dem Klassendiagramm ab:
-- Mit dem Modul verschwinden auch seine Pruefungsleistungen und Versuche.
CREATE TABLE IF NOT EXISTS pruefungsleistung (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    modul_kuerzel     TEXT    NOT NULL REFERENCES modul (kuerzel) ON DELETE CASCADE,
    art               TEXT    NOT NULL,
    gewichtung        REAL    NOT NULL DEFAULT 1.0,
    termin            TEXT,
    dauer_minuten     INTEGER,
    ist_onlineklausur INTEGER,
    thema             TEXT
);

CREATE TABLE IF NOT EXISTS phasenfrist (
    id                   INTEGER PRIMARY KEY AUTOINCREMENT,
    pruefungsleistung_id INTEGER NOT NULL REFERENCES pruefungsleistung (id) ON DELETE CASCADE,
    frist                TEXT    NOT NULL
);

CREATE TABLE IF NOT EXISTS versuch (
    id                   INTEGER PRIMARY KEY AUTOINCREMENT,
    pruefungsleistung_id INTEGER NOT NULL REFERENCES pruefungsleistung (id) ON DELETE CASCADE,
    nummer               INTEGER NOT NULL,
    datum                TEXT    NOT NULL,
    erreichte_punkte     INTEGER NOT NULL,
    max_punkte           INTEGER NOT NULL DEFAULT 100,
    bestehensgrenze      INTEGER NOT NULL DEFAULT 50,
    UNIQUE (pruefungsleistung_id, nummer)
);

-- Die Studienziele werden mitgespeichert. Zielwert und Toleranz haben je
-- Zielart eine eigene Bedeutung; die Zuordnung steht in ziele/zielfabrik.py.
CREATE TABLE IF NOT EXISTS studienziel (
    art       TEXT    PRIMARY KEY,
    zielwert  REAL    NOT NULL,
    toleranz  REAL    NOT NULL,
    ist_aktiv INTEGER NOT NULL DEFAULT 1
);

CREATE INDEX IF NOT EXISTS idx_modul_semester ON modul (semester_nummer);
"""


class SQLiteStudiengangRepository(StudiengangRepository):
    """Speichert den gesamten Studiengang in einer einzigen Datenbankdatei.

    Die Datenbank kommt vollstaendig aus der Standardbibliothek. Es ist kein
    Server noetig, die Datei laesst sich kopieren und mitnehmen.
    """

    def __init__(self, dateipfad: str | Path) -> None:
        self.dateipfad = Path(dateipfad)
        self.dateipfad.parent.mkdir(parents=True, exist_ok=True)
        self._erstelle_tabellen()

    # -- Verbindung -------------------------------------------------------

    def _verbindung(self) -> sqlite3.Connection:
        verbindung = sqlite3.connect(self.dateipfad)
        verbindung.row_factory = sqlite3.Row
        verbindung.execute("PRAGMA foreign_keys = ON")
        return verbindung

    def _erstelle_tabellen(self) -> None:
        with self._verbindung() as verbindung:
            verbindung.executescript(SCHEMA)

    def ist_leer(self) -> bool:
        with self._verbindung() as verbindung:
            (anzahl,) = verbindung.execute("SELECT COUNT(*) FROM studiengang").fetchone()
        return anzahl == 0

    # -- Lesen ------------------------------------------------------------

    def lade(self) -> Studiengang:
        """Baut das gesamte Objektgeflecht aus der Datenbank auf."""
        with self._verbindung() as verbindung:
            kopf = verbindung.execute("SELECT * FROM studiengang WHERE id = 1").fetchone()
            if kopf is None:
                raise LookupError(f"In {self.dateipfad.name} ist kein Studiengang gespeichert")

            studiengang = Studiengang(
                bezeichnung=kopf["bezeichnung"],
                abschluss=Abschluss[kopf["abschluss"]],
                gesamt_ects=kopf["gesamt_ects"],
                geplante_dauer_monate=kopf["geplante_dauer_monate"],
                studienbeginn=date.fromisoformat(kopf["studienbeginn"]),
                anzahl_semester=kopf["anzahl_semester"],
            )

            for zeile in verbindung.execute(
                "SELECT * FROM modul ORDER BY semester_nummer, kuerzel"
            ):
                modul = Modul(
                    kuerzel=zeile["kuerzel"],
                    bezeichnung=zeile["bezeichnung"],
                    ects=zeile["ects"],
                    status=Modulstatus(zeile["status"]),
                    begonnen_am=(
                        date.fromisoformat(zeile["begonnen_am"]) if zeile["begonnen_am"] else None
                    ),
                )
                for leistung in self._lade_leistungen(verbindung, modul.kuerzel):
                    modul.verlange(leistung)
                studiengang.semester_mit_nummer(zeile["semester_nummer"]).belege(modul)

        return studiengang

    def _lade_leistungen(
        self, verbindung: sqlite3.Connection, modul_kuerzel: str
    ) -> list[Pruefungsleistung]:
        """Erzeugt die passenden Unterklassen aus der Spalte ``art``.

        Dies ist die einzige Stelle im Programm, an der noch nach der
        Pruefungsart unterschieden wird. Ueberall sonst genuegt die
        abstrakte Oberklasse.
        """
        leistungen: list[Pruefungsleistung] = []
        for zeile in verbindung.execute(
            "SELECT * FROM pruefungsleistung WHERE modul_kuerzel = ? ORDER BY id",
            (modul_kuerzel,),
        ).fetchall():
            art = zeile["art"]
            if art == "klausur":
                leistung: Pruefungsleistung = Klausur(
                    pruefungstermin=date.fromisoformat(zeile["termin"]),
                    dauer_minuten=(
                        zeile["dauer_minuten"] if zeile["dauer_minuten"] is not None else 90
                    ),
                    ist_onlineklausur=bool(zeile["ist_onlineklausur"]),
                    gewichtung=zeile["gewichtung"],
                )
            elif art == "fallstudie":
                leistung = Fallstudie(
                    abgabefrist=date.fromisoformat(zeile["termin"]),
                    thema=zeile["thema"] or "",
                    gewichtung=zeile["gewichtung"],
                )
            elif art == "portfolio":
                fristen = [
                    date.fromisoformat(f["frist"])
                    for f in verbindung.execute(
                        "SELECT frist FROM phasenfrist WHERE pruefungsleistung_id = ? ORDER BY frist",
                        (zeile["id"],),
                    )
                ]
                leistung = Portfolio(
                    phasenfristen=fristen,
                    gewichtung=zeile["gewichtung"],
                )
            else:
                raise ValueError(f"Unbekannte Pruefungsart in der Datenbank: {art}")

            for v in verbindung.execute(
                "SELECT nummer, datum, erreichte_punkte, max_punkte, bestehensgrenze "
                "FROM versuch "
                "WHERE pruefungsleistung_id = ? ORDER BY nummer",
                (zeile["id"],),
            ):
                leistung.trage_versuch_ein(
                    Versuch(
                        nummer=v["nummer"],
                        datum=date.fromisoformat(v["datum"]),
                        erreichte_punkte=v["erreichte_punkte"],
                        max_punkte=v["max_punkte"],
                        bestehensgrenze=v["bestehensgrenze"],
                    )
                )
            leistungen.append(leistung)
        return leistungen

    # -- Studienziele -----------------------------------------------------

    def lade_ziele(self) -> list[Studienziel]:
        """Liest die gespeicherten Ziele und erzeugt die passenden Unterklassen."""
        with self._verbindung() as verbindung:
            zeilen = verbindung.execute(
                "SELECT art, zielwert, toleranz, ist_aktiv FROM studienziel ORDER BY rowid"
            ).fetchall()
        return [
            erzeuge_ziel(
                art=zeile["art"],
                zielwert=zeile["zielwert"],
                toleranz=zeile["toleranz"],
                ist_aktiv=bool(zeile["ist_aktiv"]),
            )
            for zeile in zeilen
        ]

    def speichere_ziele(self, ziele: list[Studienziel]) -> None:
        """Schreibt die Ziele vollstaendig neu."""
        with self._verbindung() as verbindung:
            verbindung.execute("DELETE FROM studienziel")
            verbindung.executemany(
                "INSERT INTO studienziel (art, zielwert, toleranz, ist_aktiv) "
                "VALUES (?, ?, ?, ?)",
                [(z.art, z.zielwert, z.toleranz, int(z.ist_aktiv)) for z in ziele],
            )

    # -- Schreiben --------------------------------------------------------

    def speichere(self, studiengang: Studiengang) -> None:
        """Schreibt den Studiengang vollstaendig neu.

        Fuer einen Datenbestand dieser Groesse ist das einfacher und sicherer
        als ein Abgleich einzelner Zeilen.
        """
        try:
            self._schreibe(studiengang)
        except sqlite3.IntegrityError as fehler:
            raise ValueError(
                "Der Studiengang liess sich nicht speichern. Vermutlich ist "
                "dasselbe Modulkuerzel in zwei Semestern belegt."
            ) from fehler

    def _schreibe(self, studiengang: Studiengang) -> None:
        with self._verbindung() as verbindung:
            verbindung.execute("DELETE FROM modul")       # raeumt per CASCADE mit auf
            verbindung.execute("DELETE FROM studiengang")
            verbindung.execute(
                "INSERT INTO studiengang VALUES (1, ?, ?, ?, ?, ?, ?)",
                (
                    studiengang.bezeichnung,
                    studiengang.abschluss.name,
                    studiengang.gesamt_ects,
                    studiengang.geplante_dauer_monate,
                    studiengang.studienbeginn.isoformat(),
                    len(studiengang.semester),
                ),
            )

            for semester in studiengang.semester:
                for modul in semester.module:
                    verbindung.execute(
                        "INSERT INTO modul VALUES (?, ?, ?, ?, ?, ?)",
                        (
                            modul.kuerzel, modul.bezeichnung, modul.ects,
                            modul.status.value,
                            modul.begonnen_am.isoformat() if modul.begonnen_am else None,
                            semester.nummer,
                        ),
                    )
                    for leistung in modul.pruefungsleistungen:
                        self._speichere_leistung(verbindung, modul.kuerzel, leistung)

    def _speichere_leistung(
        self, verbindung: sqlite3.Connection, modul_kuerzel: str, leistung: Pruefungsleistung
    ) -> None:
        art = {"Klausur": "klausur", "Portfolio": "portfolio", "Fallstudie": "fallstudie"}[
            leistung.art()
        ]
        termin = None
        dauer = None
        online = None
        thema = None
        if isinstance(leistung, Klausur):
            termin = leistung.pruefungstermin.isoformat()
            dauer = leistung.dauer_minuten
            online = int(leistung.ist_onlineklausur)
        elif isinstance(leistung, Fallstudie):
            termin = leistung.abgabefrist.isoformat()
            thema = leistung.thema

        zeiger = verbindung.execute(
            "INSERT INTO pruefungsleistung "
            "(modul_kuerzel, art, gewichtung, termin, dauer_minuten, "
            " ist_onlineklausur, thema) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (modul_kuerzel, art, leistung.gewichtung,
             termin, dauer, online, thema),
        )
        leistung_id = zeiger.lastrowid

        if isinstance(leistung, Portfolio):
            verbindung.executemany(
                "INSERT INTO phasenfrist (pruefungsleistung_id, frist) VALUES (?, ?)",
                [(leistung_id, frist.isoformat()) for frist in leistung.phasenfristen],
            )

        verbindung.executemany(
            "INSERT INTO versuch (pruefungsleistung_id, nummer, datum, erreichte_punkte, "
            "max_punkte, bestehensgrenze) VALUES (?, ?, ?, ?, ?, ?)",
            [
                (leistung_id, v.nummer, v.datum.isoformat(), v.erreichte_punkte,
                 v.max_punkte, v.bestehensgrenze)
                for v in leistung.versuche
            ],
        )
