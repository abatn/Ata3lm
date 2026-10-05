"""5-Phasen-Runner (data/memory/recursion_runner.py) — echter Zyklus (Guardrail 7)."""

from pathlib import Path

import mandate
import numpy as np
import recursion_runner as rr

ROOT = Path(__file__).resolve().parents[1]


def _mandate(actions=frozenset({"write:memory"})):
    return mandate.Mandate(
        mandate_id="t",
        principal="Batnini",
        agent="knowledge-agent",
        actions=actions,
        resources=frozenset({"data/memory"}),
        amount_limit=1.0,
        max_uses=100,
        valid_from=0.0,
        valid_until=1e12,
        approval_threshold=0.5,
    )


def _run(tmp_path, **kw):
    return rr.run_recursion(
        "Wo?",
        "Kontakt: max@example.com, Version 2.",
        "Version 2.",
        classify_fn=lambda q, f, c: {"class": "write-new"},
        mandate_obj=kw.pop("mandate_obj", _mandate()),
        structured_dir=tmp_path / "structured",
        tier3_dir=tmp_path / "tier3",
        **kw,
    )


def test_vollstaendiger_zyklus(tmp_path):
    out = _run(tmp_path, delta=np.full((4, 4), 0.05), successes=3, failures=1)
    assert out["phases"] == list(rr.PHASES)
    assert len(out["trace"]) == 5
    assert out["results"]["Konstrukt"]["K"] == 4
    assert out["results"]["Akt"]["action"] == "write-new"
    assert out["results"]["Compare"]["belief"] > 0
    assert out["results"]["Revise"]["skipped"] is False  # echte Δ-Matrix -> HMM aktualisiert


def test_noop_ohne_llm(tmp_path, monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    out = _run(tmp_path, reflection_text="keine matrix")  # delta=None + kein Key -> NOOP
    assert out["results"]["Revise"]["skipped"] is True


def test_akt_gate_deny(tmp_path):
    out = _run(tmp_path, mandate_obj=_mandate(actions=frozenset()), delta=np.full((4, 4), 0.05))
    assert out["results"]["Akt"]["ok"] is False and out["results"]["Akt"]["action"] == "deny"


def test_deny_keine_revision(tmp_path):
    """S1a/§9: abgelehnte Akt-Aktion -> keine Revision."""
    out = _run(tmp_path, mandate_obj=_mandate(actions=frozenset()), delta=np.full((4, 4), 0.05))
    assert out["results"]["Akt"]["ok"] is False
    assert out["results"]["Revise"]["skipped"] is True


def test_compare_ohne_beobachtung_kein_ground_truth(tmp_path):
    """S1b/§1/§6: ohne externe Beobachtung kein Ground-Truth-Label."""
    out = _run(tmp_path, delta=np.full((4, 4), 0.05))  # 0/0 Beobachtungen
    assert out["results"]["Compare"]["observed"] is False
    assert "kein externes Signal" in out["results"]["Compare"]["signal"]
