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
    # A4/§9: Score 3/4 = 0.75 liegt im ask-Band (70–94 %) -> Revision nur mit Freigabe.
    out = _run(tmp_path, delta=np.full((4, 4), 0.05), successes=3, failures=1, revise_approved=True)
    assert out["phases"] == list(rr.PHASES)
    assert len(out["trace"]) == 5
    assert out["results"]["Konstrukt"]["K"] == 4
    assert out["results"]["Akt"]["action"] == "write-new"
    assert out["results"]["Compare"]["belief"] > 0
    assert out["results"]["Compare"]["gate"] == "ask"  # 0.75 im ask-Band
    assert out["results"]["Revise"]["skipped"] is False  # Freigabe + echte Δ-Matrix -> HMM aktualisiert


def test_noop_ohne_llm(tmp_path, monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    out = _run(tmp_path, reflection_text="keine matrix", successes=1)  # delta=None + kein Key -> NOOP
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


def test_b6_rein_negative_evidenz_keine_revision(tmp_path):
    """B6 (K6): Compare.observed=True genügt NICHT – negative Beobachtungen sind kein Revisionsbeleg."""
    out = _run(tmp_path, delta=np.full((4, 4), 0.05), successes=0, failures=3)
    assert out["results"]["Compare"]["observed"] is True  # Signal liegt vor ...
    r = out["results"]["Revise"]
    assert r["skipped"] is True and "Evidenz" in r["reason"]  # ... ist aber negativ/unzureichend


def test_b6_gate_ask_keine_revision():
    """B6 (K6): ohne ausdrücklich zulässige Entscheidung (gate=ask) keine Revision."""

    class _HMM:
        def update_from_reflection(self, text, delta=None):  # pragma: no cover - darf nie laufen
            raise AssertionError("Revision ohne zulässige Entscheidung")

    ctx = {
        "results": {"Akt": {"ok": True, "gate": "ask"}, "Compare": {"observed": True}},
        "successes": 5,
        "failures": 0,
        "hmm": _HMM(),
        "reflection_text": "",
        "delta": None,
    }
    r = rr._phase_revise(ctx)
    assert r["skipped"] is True and "ausdrücklich zulässig" in r["reason"]


def test_r10_niedriger_score_keine_revision():
    """R10/§9: 1 Erfolg / 99 Fehler (Score 0.01 < 0.70) → keine Revision."""

    class _HMM:
        def update_from_reflection(self, text, delta=None):  # pragma: no cover - darf nie laufen
            raise AssertionError("Revision trotz Score < 70 %")

    ctx = {
        "results": {"Akt": {"ok": True, "gate": "allow"}, "Compare": {"observed": True}},
        "successes": 1,
        "failures": 99,
        "hmm": _HMM(),
        "reflection_text": "",
        "delta": None,
    }
    r = rr._phase_revise(ctx)
    assert r["skipped"] is True and "Score" in r["reason"]


def test_r10_schwelle_70_prozent_ask_gated(tmp_path):
    """A4/§9: Score == 0.70 (7/10) liegt im ask-Band (70–94 %) → ohne Freigabe keine Revision."""
    out = _run(tmp_path, delta=np.full((4, 4), 0.05), successes=7, failures=3)
    assert out["results"]["Compare"]["gate"] == "ask"
    r = out["results"]["Revise"]
    assert r["skipped"] is True and "ask" in r["reason"]
    # Mit menschlicher Freigabe ist die Revision im ask-Band erlaubt.
    out2 = _run(tmp_path, delta=np.full((4, 4), 0.05), successes=7, failures=3, revise_approved=True)
    assert out2["results"]["Revise"]["skipped"] is False


def test_a4_compare_allow_automatisch(tmp_path):
    """A4/§9: Score ≥ 95 % ⇒ allow → automatische Revision ohne Freigabe."""
    out = _run(tmp_path, delta=np.full((4, 4), 0.05), successes=19, failures=1)
    assert out["results"]["Compare"]["gate"] == "allow"
    assert out["results"]["Revise"]["skipped"] is False


def test_a4_compare_deny(tmp_path):
    """A4/§9: Score < 70 % ⇒ Compare-Gate deny → keine Revision."""
    out = _run(tmp_path, delta=np.full((4, 4), 0.05), successes=1, failures=3, revise_approved=True)
    assert out["results"]["Compare"]["gate"] == "deny"
    r = out["results"]["Revise"]
    assert r["skipped"] is True and "Score" in r["reason"]


def test_a4_compare_deny_branch_direkt():
    """A4/§9: ein explizites Compare-Gate `deny` blockiert die Revision auch bei hohem Score."""

    class _HMM:
        def update_from_reflection(self, text, delta=None):  # pragma: no cover - darf nie laufen
            raise AssertionError("Revision trotz deny")

    ctx = {
        "results": {"Akt": {"ok": True, "gate": "allow"}, "Compare": {"observed": True, "gate": "deny"}},
        "successes": 9,
        "failures": 1,
        "hmm": _HMM(),
        "reflection_text": "",
        "delta": None,
        "revise_approved": True,
    }
    r = rr._phase_revise(ctx)
    assert r["skipped"] is True and "deny" in r["reason"]


def test_r07_r18_recursion_state_save(tmp_path):
    """R07/R18: `save`-Rückgabe sichtbar; deny persistiert keinen State; rev wächst."""
    p = tmp_path / "state.json"
    out = _run(tmp_path, delta=np.full((4, 4), 0.05), successes=3, failures=1, state_path=p)
    assert out["state_save"]["ok"] is True and out["state_save"]["rev"] == 1
    out2 = _run(tmp_path, delta=np.full((4, 4), 0.05), successes=3, failures=1, state_path=p)
    assert out2["state_save"]["rev"] == 2
    p2 = tmp_path / "deny.json"
    out3 = _run(
        tmp_path,
        mandate_obj=_mandate(actions=frozenset()),
        delta=np.full((4, 4), 0.05),
        state_path=p2,
    )
    assert out3["results"]["Akt"]["ok"] is False
    assert out3["state_save"]["ok"] is False and not p2.exists()


def test_b6_ok_ohne_evidenz_skipped_reason():
    """B6 (K6): ok + gate allow, aber kein externes Signal ⇒ keine Revision."""

    class _HMM:
        def update_from_reflection(self, text, delta=None):  # pragma: no cover - darf nie laufen
            raise AssertionError("Revision ohne Evidenz")

    ctx = {
        "results": {"Akt": {"ok": True, "gate": "allow"}, "Compare": {"observed": False}},
        "successes": 0,
        "failures": 0,
        "hmm": _HMM(),
        "reflection_text": "",
        "delta": None,
    }
    r = rr._phase_revise(ctx)
    assert r["skipped"] is True and "Evidenz" in r["reason"]
