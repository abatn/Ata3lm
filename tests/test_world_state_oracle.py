"""World-State-Oracle: Out-of-Band-Evaluation mit echtem externen Signal (§6).

Quelle: arXiv:2607.25152 (+ Zenodo 10.5281/zenodo.21594735), per curl HTTP 200
verifiziert (2026-10-07). Guardrail 7: die Probes unten sind **echte** Checks
(Datei lesen, Code ausführen, Wert vergleichen) – keine skriptete Antwort.
"""

from pathlib import Path

import mandate
import numpy as np
import recursion_runner as rr
import world_state_oracle as wso

ROOT = Path(__file__).resolve().parents[1]


# ---------------------------------------------------------------------------
# 1. world_state_oracle.evaluate (echtes Probe-Callable)
# ---------------------------------------------------------------------------
def test_probe_ok_liefert_externes_signal(tmp_path):
    f = tmp_path / "state.txt"
    f.write_text("42", encoding="utf-8")
    res = wso.evaluate("Datei enthält 42", lambda: f.read_text(encoding="utf-8") == "42")
    assert res["ok"] is True
    assert res["signal"] == wso.Signal
    assert res["reason"] is None
    assert res["successes"] == 1 and res["failures"] == 0


def test_probe_false_kein_signal():
    res = wso.evaluate("Code ergibt 5", lambda: 2 + 2 == 5)
    assert res["ok"] is False
    assert res["signal"] == wso.NO_SIGNAL


def test_probe_raise_kein_signal():
    def probe():
        raise RuntimeError("DB nicht erreichbar")

    res = wso.evaluate("DB-Wert", probe)
    assert res["ok"] is False
    assert res["signal"] == wso.NO_SIGNAL
    assert "Probe-Fehler" in res["reason"]


def test_probe_none_kein_signal():
    res = wso.evaluate("Behauptung", None)
    assert res["ok"] is False
    assert res["signal"] == wso.NO_SIGNAL
    assert "kein echtes Probe-Callable" in res["reason"]
    assert res["evidence"] is None


def test_probe_nicht_callable_kein_signal():
    res = wso.evaluate("Behauptung", 42)
    assert res["ok"] is False and res["signal"] == wso.NO_SIGNAL


def test_probe_dict_ok_default_zaehler():
    res = wso.evaluate("Check", lambda: {"ok": True, "evidence": {"file": "state.txt"}})
    assert res["ok"] is True
    assert res["successes"] == 1 and res["failures"] == 0
    assert res["evidence"] == {"file": "state.txt"}


def test_probe_dict_not_ok_explizite_zaehler():
    res = wso.evaluate(
        "Check",
        lambda: {"ok": False, "successes": 2, "failures": 5, "evidence": {"x": 1}},
    )
    assert res["ok"] is False
    assert res["successes"] == 2 and res["failures"] == 5
    assert res["evidence"] == {"x": 1}


def test_probe_dict_ohne_ok_key_truthy():
    res = wso.evaluate("Check", lambda: {"result": 7})
    assert res["ok"] is True  # nicht-leeres Dict ist truthy
    assert res["evidence"] == {"result": {"result": 7}}


def test_probe_falsy_non_dict():
    res = wso.evaluate("Check", lambda: 0)
    assert res["ok"] is False and res["successes"] == 0 and res["failures"] == 1


def test_probe_truthy_non_dict():
    res = wso.evaluate("Check", lambda: "ok")
    assert res["ok"] is True and res["successes"] == 1 and res["failures"] == 0


# ---------------------------------------------------------------------------
# 2. Compare koppelt den Oracle (Selbstreport allein genügt nicht, §6)
# ---------------------------------------------------------------------------
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


def test_compare_oracle_false_overrides_hoher_selbstreport(tmp_path):
    """Selbstreport 99/0 darf ohne externes Signal KEIN observed=True erzeugen."""
    out = _run(
        tmp_path,
        delta=np.full((4, 4), 0.05),
        successes=99,
        failures=0,
        world_state_probe=lambda: False,
    )
    c = out["results"]["Compare"]
    assert c["observed"] is False
    assert c["gate"] == "ask"
    assert "kein externes Signal" in c["signal"]
    assert c["self_report"]["successes"] == 99  # nur Annotation, kein Signal


def test_compare_oracle_ok_allow(tmp_path):
    out = _run(
        tmp_path,
        delta=np.full((4, 4), 0.05),
        world_state_probe=lambda: {"ok": True, "successes": 19, "failures": 1},
    )
    c = out["results"]["Compare"]
    assert c["observed"] is True
    assert c["score"] == 0.95 and c["gate"] == "allow"
    assert c["oracle"]["ok"] is True
    assert c["oracle"]["claim"] == "Kontakt: max@example.com, Version 2."


def test_compare_oracle_ok_ohne_zaehler_score_eins(tmp_path):
    out = _run(
        tmp_path,
        delta=np.full((4, 4), 0.05),
        world_state_probe=lambda: {"ok": True, "successes": 0, "failures": 0},
    )
    c = out["results"]["Compare"]
    assert c["observed"] is True and c["score"] == 1.0 and c["gate"] == "allow"


def test_compare_oracle_eigene_claim(tmp_path):
    out = _run(
        tmp_path,
        delta=np.full((4, 4), 0.05),
        world_state_probe=lambda: True,
        world_state_claim="",
    )
    # leerer Claim ist falsy -> Fallback auf `fact`
    assert out["results"]["Compare"]["oracle"]["claim"] == "Kontakt: max@example.com, Version 2."
    out2 = _run(
        tmp_path,
        delta=np.full((4, 4), 0.05),
        world_state_probe=lambda: True,
        world_state_claim="Version 2.",
    )
    assert out2["results"]["Compare"]["oracle"]["claim"] == "Version 2."


def test_compare_ohne_probe_legacy_pfad(tmp_path):
    """Ohne Probe bleibt der bisherige Pfad (Rückwärtskompatibilität)."""
    out = _run(tmp_path, delta=np.full((4, 4), 0.05), successes=3, failures=1)
    c = out["results"]["Compare"]
    assert c["observed"] is True and "oracle" not in c
