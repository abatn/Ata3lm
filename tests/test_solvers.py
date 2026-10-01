"""Historische Solver-Snapshots (ergebnisse/rekursion/solver/*.py).

Die Dateien sind Rekursions-Artefakte (v1..v6, je mit „improved"-Variante).
Getestet wird das jeweilige Ist-Verhalten – inklusive der dokumentierten
Schwächen der Originale (π₀..π₆) und der Korrektur der „improved"-Varianten.
"""
import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SOLVER_DIR = ROOT / "ergebnisse" / "rekursion" / "solver"


def _load(name):
    spec = importlib.util.spec_from_file_location(f"solver_mod_{name}",
                                                  SOLVER_DIR / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.mark.parametrize("name,func,arg,expected", [
    ("solver", "sortiere_zahlen", [3, 1, 2, 1, 3], [1, 1, 2, 3, 3]),   # Schwäche: Duplikate
    ("solver_improved", "sortiere_zahlen", [3, 1, 2, 1, 3], [1, 2, 3]),
    ("solver_v3", "finde_maximum", [3, 1, 4, 1, 5], 3),               # Schwäche: erstes Element
    ("solver_v3_improved", "finde_maximum", [3, 1, 4, 1, 5], 5),
    ("solver_v4", "berechne_durchschnitt", [1, 2], 1),                # Schwäche: Integer-Division
    ("solver_v4_improved", "berechne_durchschnitt", [1, 2], 1.5),
    ("solver_v5", "finde_minimum", [3, 1, 4, 1, 5], 3),               # Schwäche: erstes Element
    ("solver_v5_improved", "finde_minimum", [3, 1, 4, 1, 5], 1),
    ("solver_v6", "berechne_median", [3, 1, 4, 1, 5], 4),             # Schwäche: unsortiert
    ("solver_v6_improved", "berechne_median", [3, 1, 4, 1, 5], 3),
    ("solver_v6_improved", "berechne_median", [1, 2, 3, 4], 2.5),
])
def test_solver_funktion(name, func, arg, expected):
    assert getattr(_load(name), func)(arg) == expected


@pytest.mark.parametrize("name,func", [
    ("solver_v3", "finde_maximum"),
    ("solver_v3_improved", "finde_maximum"),
    ("solver_v4", "berechne_durchschnitt"),
    ("solver_v4_improved", "berechne_durchschnitt"),
    ("solver_v5", "finde_minimum"),
    ("solver_v5_improved", "finde_minimum"),
    ("solver_v6", "berechne_median"),
    ("solver_v6_improved", "berechne_median"),
])
def test_leere_liste_gibt_none(name, func):
    assert getattr(_load(name), func)([]) is None


def test_v1_verbesserung_entfernt_duplikate():
    alt = _load("solver").sortiere_zahlen([3, 1, 2, 1, 3])
    neu = _load("solver_improved").sortiere_zahlen([3, 1, 2, 1, 3])
    assert alt == [1, 1, 2, 3, 3]      # bekannte Schwäche von v1
    assert neu == [1, 2, 3]            # verbesserte Variante
