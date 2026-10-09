"""Repro-Tests für D1 (Audit d25486c, P2): explizite Verneinung ⇒ falsch.

SOLL (Quelle, in ``AGENTS.md`` referenziert ⇒ keine neue Quelle):
arXiv:2603.06333 (SAHOO, ``AGENTS.md`` §9.1c) **Constraint-Preservation** –
eine verneinte korrekte Aussage ist **falsch**.

Heuristik (Auftrag, kein Paper-Claim): erweiterte Negationsmarker
(``false``/``untrue``/``wrong``/``incorrect``, ``not true``, ``nicht wahr`` …)
im Fenster **vor** dem Treffer. Offline, kein Netz (Guardrail 7).
"""

import importlib.util
from pathlib import Path

_SPEC = importlib.util.spec_from_file_location(
    "drift_calibrate_sahoo",
    Path(__file__).resolve().parents[1] / "scripts" / "drift_calibrate_sahoo.py",
)
sahoo = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(sahoo)

_GOLD = ["Paris is the capital of France"]


def test_false_that_is_rejected():
    """D1-Repro: „It is **false** that …" ist eine Verneinung ⇒ False."""
    assert sahoo._check_truth("It is false that Paris is the capital of France.", _GOLD) is False


def test_positive_case_stays_true():
    """Positivfall: korrekte Aussage ohne Verneinung ⇒ True."""
    assert sahoo._check_truth("Paris is the capital of France.", _GOLD) is True


def test_marker_untrue_is_rejected():
    assert sahoo._check_truth("It is untrue that Paris is the capital of France.", _GOLD) is False


def test_marker_nicht_wahr_is_rejected():
    assert (
        sahoo._check_truth(
            "Es ist nicht wahr, dass Paris die Hauptstadt von Frankreich ist.",
            ["Paris die Hauptstadt von Frankreich"],
        )
        is False
    )


def test_marker_wrong_is_rejected():
    assert sahoo._check_truth("It is wrong that Paris is the capital of France.", _GOLD) is False


def test_marker_falsch_is_rejected():
    assert (
        sahoo._check_truth(
            "Es ist falsch, dass Paris die Hauptstadt von Frankreich ist.",
            ["Paris die Hauptstadt von Frankreich"],
        )
        is False
    )


def test_negation_in_previous_sentence_does_not_block():
    """Regression: eine Verneinung im früheren Satz blockiert den Treffer nicht."""
    assert sahoo._check_truth("It is not London. The capital is Paris.", ["Paris"]) is True
