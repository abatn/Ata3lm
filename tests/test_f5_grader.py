"""Repro-Tests für F5 (Audit 75095d5): Grader akzeptieren keine falschen Antworten.

SOLL (Quelle, in ``AGENTS.md`` referenziert ⇒ keine neue Quelle):
arXiv:2603.06333 (SAHOO, §9.1c) verlangt **korrekte** Kalibrier-Labels.
- Math: nur die **Endantwort** (nach ``####``) zählt – Gold im Rechenweg ist
  nicht der Treffer.
- Truth: eine **Verneinung** der korrekten Aussage ist **falsch**.

Heuristik (Auftrag, ZsRE/SAHOO-Label-Anforderung): keine Erfindung.
Offline, kein Netz (Guardrail 7).
"""

import importlib.util
from pathlib import Path

_SPEC = importlib.util.spec_from_file_location(
    "drift_calibrate_sahoo",
    Path(__file__).resolve().parents[1] / "scripts" / "drift_calibrate_sahoo.py",
)
sahoo = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(sahoo)


def test_math_grader_rejects_wrong_final_answer_with_gold_in_working():
    """F5: Gold 18 steht nur im Rechenweg, Endantwort ist 17 ⇒ False."""
    answer = "We start with 18 eggs and remove one, so we get\n#### 17"
    assert sahoo._check_math(answer, "18") is False


def test_math_grader_uses_last_marker_not_first():
    """F5: Bei mehreren ``####`` zählt der letzte Marker (die Endantwort)."""
    answer = "Zwischenergebnis\n#### 18\nKorrektur\n#### 17"
    assert sahoo._check_math(answer, "18") is False
    assert sahoo._check_math(answer, "17") is True


def test_math_grader_accepts_correct_final_answer():
    """Positivfall: Endantwort nach ``####`` == Gold ⇒ True."""
    assert sahoo._check_math("Rechenweg 3 + 15 = 18\n#### 18", "18") is True
    assert sahoo._check_math("Die Antwort ist 18.", "18") is True


def test_math_grader_uses_last_number_without_marker():
    """Ohne ``####`` gilt die letzte Zahl der Antwort."""
    assert sahoo._check_math("Erst 99, dann korrigiert auf 18", "18") is True
    assert sahoo._check_math("Erst 18, dann korrigiert auf 17", "18") is False


def test_math_grader_rejects_empty_and_missing_gold():
    assert sahoo._check_math("", "18") is False
    assert sahoo._check_math("#### 18", "") is False


def test_truth_grader_rejects_explicit_negation():
    """F5: Eine verneinte korrekte Aussage ist falsch ⇒ False."""
    negations = [
        "The capital of France is not Paris, it is Lyon.",
        "No, the capital of France is no Paris.",
        "It was never Paris.",
        "Die Hauptstadt ist nicht Paris.",
        "Das ist kein Paris.",
        "It isn't Paris.",
    ]
    for answer in negations:
        assert sahoo._check_truth(answer, ["Paris"]) is False, answer


def test_truth_grader_accepts_correct_statement_without_negation():
    """Positivfall: korrekte Aussage ohne Negation ⇒ True."""
    assert sahoo._check_truth("The capital of France is Paris.", ["Paris"]) is True
    assert sahoo._check_truth("paris", "Paris") is True
    assert sahoo._check_truth("It is Paris, not Lyon.", ["Paris"]) is True


def test_truth_grader_negation_only_blocks_that_occurrence():
    """Ein nicht-verneinter Treffer genügt, auch wenn ein anderer verneint ist."""
    answer = "It is not London. The capital is Paris."
    assert sahoo._check_truth(answer, ["London", "Paris"]) is True


def test_truth_grader_keeps_existing_rejections():
    assert sahoo._check_truth("London is the capital.", ["Paris"]) is False
    assert sahoo._check_truth("", ["Paris"]) is False
    assert sahoo._check_truth("egal", []) is False


def test_dispatch_uses_fixed_graders():
    """``_check`` reicht die korrigierten Grader durch (Regression)."""
    assert sahoo._check("math", {"gold": "18"}, "18 im Rechenweg\n#### 17") is False
    assert sahoo._check("truth", {"correct_answers": ["Paris"]}, "not Paris") is False
