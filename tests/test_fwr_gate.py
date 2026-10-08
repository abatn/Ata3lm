"""Eskalationsgate `g*` (arXiv:2608.22215 §3.3.1/§3.3.2) – offline, deterministisch.

Reine Formeln + `classify(reward_gate=True)` mit injizierten LLM-Antworten
(`_ask`-Stub): kein Netz, keine skriptete „Verifikation" realer Modellgüte —
nur die Papier-Logik (Belegt) und die Verhaltens-Approximation (Auftrag) werden
unit-getestet.
"""

import fast_write_router as fwr
import pytest

SMALL = fwr.SMALL_MODEL
LARGE = fwr.LARGE_MODEL


# --------------------------------------------------------------- reward (§3.3.1)
def test_reward_write_gewinnt():
    assert fwr.reward(True, False, 0.08) == {"rW": pytest.approx(0.92), "rD": 0.0}


def test_reward_gleichstand_ist_negativ():
    r = fwr.reward(True, True, 0.08)
    assert r["rW"] == pytest.approx(-0.08) and r["rD"] == 0.0


def test_reward_kein_schreiben_und_kein_korrekt():
    r = fwr.reward(False, False, 0.08)
    assert r["rW"] == pytest.approx(-0.08) and r["rD"] == 0.0
    # discard korrekt, write falsch -> r(W) = 0 - 1 - λ_s
    assert fwr.reward(False, True, 0.08)["rW"] == pytest.approx(-1.08)


# ------------------------------------------------------- escalation_gain (§3.3.2)
def test_escalation_gain_gross_besser_eskaliert():
    g = fwr.escalation_gain(small_w=False, small_d=True, large_w=True, large_d=False, lambda_s=0.08, lambda_e=0.005)
    assert g["escalate"] is True and g["g"] == pytest.approx(0.915)
    assert g["a_small"] == "D" and g["a_large"] == "W"
    assert g["V_small"] == pytest.approx(0.0) and g["V_large"] == pytest.approx(0.915)


def test_escalation_gain_klein_genuegt_nicht_eskalieren():
    g = fwr.escalation_gain(small_w=True, small_d=False, large_w=True, large_d=False, lambda_s=0.08, lambda_e=0.005)
    assert g["escalate"] is False and g["g"] == pytest.approx(-0.005)
    assert g["a_small"] == "W" and g["a_large"] == "W"


def test_escalation_gain_gross_verwirft():
    # beide Router: discard gewinnt (write korrekt UND discard korrekt) -> a="D"
    g = fwr.escalation_gain(small_w=True, small_d=False, large_w=True, large_d=True, lambda_s=0.08, lambda_e=0.005)
    assert g["a_small"] == "W" and g["a_large"] == "D"
    assert g["V_large"] == pytest.approx(-0.005) and g["escalate"] is False


def test_escalation_gain_lambda_e_kippt_vorzeichen():
    kwargs = dict(small_w=False, small_d=True, large_w=True, large_d=False, lambda_s=0.08)
    low = fwr.escalation_gain(**kwargs, lambda_e=0.005)
    high = fwr.escalation_gain(**kwargs, lambda_e=1.0)
    assert low["g"] > 0 and low["escalate"] is True
    assert high["g"] < 0 and high["escalate"] is False


def test_escalation_gain_grenzfall_g_null_kein_eskalieren():
    g = fwr.escalation_gain(small_w=True, small_d=False, large_w=True, large_d=False, lambda_s=0.08, lambda_e=0.0)
    assert g["g"] == pytest.approx(0.0) and g["escalate"] is False


def test_argmax_gleichstand_waehlt_discard():
    assert fwr._argmax_reward({"rW": 0.0, "rD": 0.0}) == "D"
    assert fwr._argmax_reward({"rW": 0.001, "rD": 0.0}) == "W"


# --------------------------------------------------------------------- _env_float
def test_env_float_default_env_und_ungueltig(monkeypatch):
    monkeypatch.delenv("FWR_LAMBDA_S", raising=False)
    assert fwr._env_float("FWR_LAMBDA_S", 0.08) == 0.08
    monkeypatch.setenv("FWR_LAMBDA_S", "0.2")
    assert fwr._env_float("FWR_LAMBDA_S", 0.08) == 0.2
    monkeypatch.setenv("FWR_LAMBDA_S", "kaputt")
    assert fwr._env_float("FWR_LAMBDA_S", 0.08) == 0.08


# ----------------------------------------------- classify(reward_gate=True) offline
def _fake_ask(answers):
    """Stub: `_ask`-Antwort je Router (zero-shot vs. mit Memory)."""

    def fake(model, question, memory=None, max_tokens=2000):
        return answers["mem" if memory else "zero"][model]

    return fake


def test_classify_reward_gate_eskaliert_zu_write_new(monkeypatch):
    stub = {"zero": {SMALL: "I don't know", LARGE: "I don't know"}, "mem": {SMALL: "I don't know", LARGE: "Zentaria"}}
    monkeypatch.setattr(fwr, "_ask", _fake_ask(stub))
    r = fwr.classify("Hauptstadt Xylophonia?", "Xylophonia: Zentaria.", "Zentaria", reward_gate=True)
    assert r["class"] == "write-new" and r["gate"] == "ask"
    assert r["stage"] == 2 and r["escalated"] is True
    assert r["gate_info"]["g"] > 0 and r["gate_info"]["a_large"] == "W"


def test_classify_reward_gate_small_zero_korrekt_non_write(monkeypatch):
    stub = {"zero": {SMALL: "Paris", LARGE: "Paris"}, "mem": {SMALL: "Paris", LARGE: "Paris"}}
    monkeypatch.setattr(fwr, "_ask", _fake_ask(stub))
    r = fwr.classify("Hauptstadt Frankreich?", "Paris.", "Paris", reward_gate=True)
    assert r["class"] == "non-write" and r["gate"] == "allow"
    assert r["stage"] == 1 and r["escalated"] is False


def test_classify_reward_gate_small_memory_entscheidet(monkeypatch):
    stub = {"zero": {SMALL: "I don't know", LARGE: "I don't know"}, "mem": {SMALL: "Zentaria", LARGE: "Zentaria"}}
    monkeypatch.setattr(fwr, "_ask", _fake_ask(stub))
    r = fwr.classify("Hauptstadt Xylophonia?", "Zentaria.", "Zentaria", reward_gate=True)
    assert r["class"] == "write-new" and r["stage"] == 1 and r["escalated"] is False


def test_classify_reward_gate_uncertain_ohne_memory(monkeypatch):
    stub = {
        "zero": {SMALL: "Antarctic Desert", LARGE: "Antarctic Desert"},
        "mem": {SMALL: "Antarctic Desert", LARGE: "Antarctic Desert"},
    }
    monkeypatch.setattr(fwr, "_ask", _fake_ask(stub))
    r = fwr.classify("Größte Wüste?", "Sahara.", "Sahara", reward_gate=True)
    assert r["class"] == "uncertain" and r["gate"] == "ask"
    assert r["stage"] == 1 and r["escalated"] is False


def test_classify_reward_gate_explizite_lambdas(monkeypatch):
    stub = {"zero": {SMALL: "I don't know", LARGE: "I don't know"}, "mem": {SMALL: "I don't know", LARGE: "Zentaria"}}
    monkeypatch.setattr(fwr, "_ask", _fake_ask(stub))
    r = fwr.classify("Q", "F", "Zentaria", reward_gate=True, lambda_s=0.2, lambda_e=0.008)
    assert r["escalated"] is True and r["gate_info"]["g"] == pytest.approx(0.792)


def test_classify_reward_gate_env_ueberschreibt_lambda(monkeypatch):
    monkeypatch.setenv("FWR_LAMBDA_S", "0.2")
    monkeypatch.setenv("FWR_LAMBDA_E", "0.008")
    stub = {"zero": {SMALL: "I don't know", LARGE: "I don't know"}, "mem": {SMALL: "I don't know", LARGE: "Zentaria"}}
    monkeypatch.setattr(fwr, "_ask", _fake_ask(stub))
    r = fwr.classify("Q", "F", "Zentaria", reward_gate=True)
    assert r["gate_info"]["g"] == pytest.approx(0.792)


# ------------------------------------------------- classify (Legacy-Fallback) offline
def test_classify_legacy_small_korrekt_non_write(monkeypatch):
    stub = {"zero": {SMALL: "Paris", LARGE: "Paris"}, "mem": {SMALL: "Paris", LARGE: "Paris"}}
    monkeypatch.setattr(fwr, "_ask", _fake_ask(stub))
    r = fwr.classify("Hauptstadt Frankreich?", "Paris.", "Paris")
    assert r["class"] == "non-write" and r["stage"] == 1 and r["escalated"] is False


def test_classify_legacy_eskaliert_write_new(monkeypatch):
    stub = {"zero": {SMALL: "I don't know", LARGE: "I don't know"}, "mem": {SMALL: "I don't know", LARGE: "Zentaria"}}
    monkeypatch.setattr(fwr, "_ask", _fake_ask(stub))
    r = fwr.classify("Hauptstadt Xylophonia?", "Zentaria.", "Zentaria")
    assert r["class"] == "write-new" and r["stage"] == 2 and r["escalated"] is True
