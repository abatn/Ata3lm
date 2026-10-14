"""P-A (Rek. 115): Probe- und Flush-Pfad nutzen denselben Grader.

Quelle: AGENTS.md §6/§10.3; data/memory/acceptance_gate.py (grade, base_rate_guard).
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "data" / "memory"))

import acceptance_gate  # noqa: E402


def _load(name: str, rel: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


CASES = [
    ("Paris", "Paris", True),
    ("paris.", "Paris", True),
    ("Paris, the capital of France", "Paris", False),  # Gelaber: strict = False
    ("", "Paris", False),
    ("Berlin", "", False),  # leeres Gold ⇒ kein Treffer
    ("Pariser Platz", "Paris", False),  # Teilstring allein reicht nicht
    ("Paris\nLondon", "Paris", True),  # erste Zeile zählt
    ("\n\n  Paris", "Paris", True),  # führende Leerzeilen werden übersprungen
]


def test_grade_strict_decisions():
    for answer, gold, expected in CASES:
        assert acceptance_gate.grade(answer, gold) is expected, (answer, gold)


def test_probe_and_flush_use_same_grader():
    probe_mod = _load("e2e_theta_probe", "kaggle/e2e_theta_probe.py")
    assert probe_mod.grade is acceptance_gate.grade
    # write_back_cycle importiert ebenfalls den Gate-Grader (Flush-Probe-Pfad)
    wbc = _load("write_back_cycle", "kaggle/write_back_cycle.py")
    assert wbc._grade is acceptance_gate.grade
    for answer, gold, expected in CASES:
        assert probe_mod.grade(answer, gold) == wbc._grade(answer, gold) == expected


def test_base_rate_guard_flags_zero_base():
    assert acceptance_gate.base_rate_guard(0, 10) is not None
    assert acceptance_gate.base_rate_guard(3, 10) is None
    assert acceptance_gate.base_rate_guard(0, 0) == "keine Items"


def test_run_guard_base_rate_flags_zero_base_hits():
    """T1: Run-Level-Guard (Flush) nutzt denselben Grader wie Probe; 0 Basistreffer ⇒ Einwand."""
    wbc = _load("write_back_cycle_guard", "kaggle/write_back_cycle.py")
    zero = [{"gold": "Paris", "base_answer": "Berlin"}, {"gold": "Rom", "base_answer": "Wien"}]
    hit = zero + [{"gold": "Paris", "base_answer": "Paris."}]
    assert wbc._run_guard(zero) is not None  # base_hits == 0 ⇒ abstain-Grund
    assert wbc._run_guard(hit) is None  # ein Basistreffer ⇒ kein Einwand
    assert wbc._run_guard([]) is not None  # keine Items ⇒ Einwand
