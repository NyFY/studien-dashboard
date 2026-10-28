"""Tests der Abhaengigkeitsrichtung zwischen den Paketen.

Im Reflexionsdokument steht die Regel, dass die Abhaengigkeiten nur in eine
Richtung zeigen duerfen. Ein UML-Diagramm kann das nicht erzwingen und ein
Kommentar im Quelltext auch nicht. Diese Tests lesen deshalb die Importe
aller Module mit ``ast`` ein und pruefen die Regel am Code selbst. Faellt
spaeter ein Import in die falsche Richtung, schlaegt der Test fehl und nicht
erst die Wartung in einem halben Jahr.

Erfasst werden alle Schreibweisen, mit denen sich eine Paketgrenze
ueberschreiten laesst: ``from ..paket import X``, ``from .. import paket``,
``from studiendashboard.paket import X`` und ``import studiendashboard.paket``.
"""

from __future__ import annotations

import ast
import unittest
from pathlib import Path

WURZEL = "studiendashboard"
PAKET = Path(__file__).resolve().parent.parent / WURZEL

#: Welches Paket welche anderen Pakete kennen darf. Alles, was hier nicht
#: steht, ist ein Verstoss gegen die Schichtung.
ERLAUBT: dict[str, set[str]] = {
    "domain": set(),
    "ergebnis": set(),
    "dto": {"ergebnis"},
    "ziele": {"dto", "ergebnis"},
    "service": {"domain", "dto"},
    "repository": {"domain", "ziele"},
    "controller": {"domain", "dto", "ergebnis", "repository", "service", "ziele"},
    "view": {"dto", "ergebnis"},
}

#: Die Dateien unmittelbar in ``studiendashboard`` sind der Composition Root.
#: ``app.py`` erzeugt und verdrahtet alle Objekte und darf deshalb als
#: einzige Stelle jedes Paket kennen.
WURZELDATEIEN = {"app.py", "__init__.py", "__main__.py"}


def importierte_pakete(datei: Path) -> set[str]:
    """Liefert die Pakete von ``studiendashboard``, die diese Datei importiert.

    Relative Importe werden zum vollen Modulnamen aufgeloest, damit auch
    ``from .. import view`` erkannt wird: Dort steht das Paket im Namen des
    importierten Objekts und nicht im Modul des Importbefehls. Das eigene
    Paket zaehlt nicht mit, denn es ueberschreitet keine Grenze.
    """
    teile = datei.relative_to(PAKET).parts
    eigenes = teile[0] if len(teile) > 1 else None
    paketpfad = [WURZEL, *teile[:-1]]

    gefunden: set[str] = set()
    for knoten in ast.walk(ast.parse(datei.read_text(encoding="utf-8"))):
        if isinstance(knoten, ast.Import):
            ziele = [alias.name for alias in knoten.names]
        elif isinstance(knoten, ast.ImportFrom) and knoten.level == 0:
            ziele = [knoten.module or ""]
        elif isinstance(knoten, ast.ImportFrom):
            basis = paketpfad[: len(paketpfad) - knoten.level + 1]
            if knoten.module:
                ziele = [".".join([*basis, knoten.module])]
            else:
                ziele = [".".join([*basis, alias.name]) for alias in knoten.names]
        else:
            continue

        for ziel in ziele:
            stuecke = ziel.split(".")
            # Nur Unterpakete zaehlen; ``from .app import ...`` trifft ein
            # Modul der Wurzel und ueberschreitet keine Paketgrenze.
            if stuecke[0] == WURZEL and len(stuecke) > 1:
                if (PAKET / stuecke[1]).is_dir():
                    gefunden.add(stuecke[1])

    return gefunden - {eigenes} if eigenes else gefunden


def module_von(paket: str) -> list[Path]:
    """Alle Python-Dateien eines Pakets, auch in Unterordnern."""
    return sorted(
        datei
        for datei in (PAKET / paket).rglob("*.py")
        if "__pycache__" not in datei.parts
    )


class TestAbhaengigkeitsrichtung(unittest.TestCase):
    """Jedes Paket kennt nur die Pakete, die unter ihm liegen."""

    def test_jedes_paket_haelt_sich_an_die_erlaubten_importe(self) -> None:
        for name, erlaubt in ERLAUBT.items():
            for datei in module_von(name):
                with self.subTest(modul=str(datei.relative_to(PAKET))):
                    self.assertLessEqual(importierte_pakete(datei), erlaubt)

    def test_ergebnis_haengt_an_keinem_anderen_paket(self) -> None:
        """Die Ergebnistypen sind die Wurzel und duerfen nichts kennen.

        Genau deshalb haben sie ein eigenes Paket: Lagen sie bei den Zielen,
        muessten sich ``dto`` und ``ziele`` gegenseitig importieren.
        """
        for datei in module_von("ergebnis"):
            self.assertEqual(importierte_pakete(datei), set(), datei.name)

    def test_nur_der_composition_root_kennt_alle_pakete(self) -> None:
        """Ausser ``app.py`` darf keine Datei quer durch alle Schichten greifen."""
        wurzeldateien = {
            datei.name for datei in PAKET.glob("*.py")
        }
        self.assertEqual(wurzeldateien, WURZELDATEIEN)
        for datei in PAKET.glob("*.py"):
            self.assertLessEqual(importierte_pakete(datei), set(ERLAUBT), datei.name)

    def test_die_pakete_bilden_keinen_ringschluss(self) -> None:
        """Keine Kette tatsaechlicher Importe fuehrt zu ihrem Paket zurueck.

        Ausgewertet wird der Code, nicht die Tabelle ``ERLAUBT``: Nur so kann
        der Test an einer spaeteren Codeaenderung ueberhaupt fehlschlagen.
        """
        graph = {
            paket: set().union(*(importierte_pakete(d) for d in module_von(paket)))
            for paket in ERLAUBT
        }
        besucht: set[str] = set()

        def pruefe(paket: str, pfad: tuple[str, ...]) -> None:
            self.assertNotIn(paket, pfad, f"Ringschluss: {' -> '.join(pfad + (paket,))}")
            if paket in besucht:
                return
            besucht.add(paket)
            for naechstes in sorted(graph[paket]):
                pruefe(naechstes, pfad + (paket,))

        for start in sorted(graph):
            pruefe(start, ())


class TestVollstaendigkeit(unittest.TestCase):
    """Die Regeln muessen alle Pakete erfassen, sonst pruefen sie zu wenig."""

    def test_alle_pakete_sind_in_den_regeln_erfasst(self) -> None:
        vorhanden = {
            ordner.name
            for ordner in PAKET.iterdir()
            if ordner.is_dir() and (ordner / "__init__.py").exists()
        }
        self.assertEqual(vorhanden, set(ERLAUBT))

    def test_keine_erlaubnis_steht_ungenutzt_in_der_tabelle(self) -> None:
        """Was erlaubt ist, soll auch gebraucht werden.

        Sonst waechst die Tabelle mit Rechten, die niemand mehr einloest, und
        der Test wird mit der Zeit schwaecher statt schaerfer.
        """
        for paket, erlaubt in ERLAUBT.items():
            genutzt = set().union(*(importierte_pakete(d) for d in module_von(paket)))
            self.assertEqual(erlaubt, genutzt, paket)


if __name__ == "__main__":
    unittest.main(verbosity=2)
