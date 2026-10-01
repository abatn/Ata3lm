"""Reflective Agent (data/memory/reflective_agent.py) – HMM · Hub/Forgetting · Retrieval.

Kein Netz: die optionalen LLM-Schritte werden mit einem Fake-`openai`-Modul
geprüft; Graph-, Structured- und Index-Pfade zeigen auf `tmp_path`.
"""
import json
import sys
from types import SimpleNamespace

import pytest

import reflective_agent as ra


# ------------------------------------------------------------------ Fake-OpenAI
def _fake_openai(content=None, reasoning=None, raises=False):
    class Completions:
        def create(self, **kw):
            if raises:
                raise RuntimeError("endpoint nicht erreichbar")
            return SimpleNamespace(choices=[SimpleNamespace(
                message=SimpleNamespace(**({"content": content} if reasoning is None
                                           else {"content": content, "reasoning_content": reasoning})))])

    class Client:
        def __init__(self, *a, **kw):
            self.chat = SimpleNamespace(completions=Completions())

    return SimpleNamespace(OpenAI=Client)


@pytest.fixture
def no_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)


# --------------------------------------------------------------- HMM-Trägheit
def test_row_normalize_und_parse_heuristik(no_key):
    import numpy as np
    P = ra._row_normalize(np.array([[1.0, 3.0], [2.0, 2.0]]))
    assert np.allclose(P.sum(axis=1), 1.0)
    neg = ra.parse_transition_delta("the action was wrong and failed", 4)
    assert neg[0][0] == -0.4 and neg[0][1] == pytest.approx(0.4 / 3)
    pos = ra.parse_transition_delta("everything matched my inertia", 4)
    assert pos[0][0] == 0.4 and pos[0][1] == pytest.approx(-0.4 / 3)


def test_parse_transition_delta_mit_llm(monkeypatch):
    payload = json.dumps([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]])
    monkeypatch.setitem(sys.modules, "openai", _fake_openai(content=payload))
    delta = ra.parse_transition_delta("text", 4)
    assert delta[0][0] == 1 and delta[3][3] == 1


def test_parse_transition_delta_faellt_zurueck(monkeypatch):
    # (a) kein JSON im Text, (c) LLM wirft -> deterministische Heuristik
    monkeypatch.setitem(sys.modules, "openai", _fake_openai(content="kein json"))
    assert ra.parse_transition_delta("wrong", 4)[0][0] == -0.4
    monkeypatch.setitem(sys.modules, "openai", _fake_openai(raises=True))
    assert ra.parse_transition_delta("wrong", 4)[0][0] == -0.4


def test_parse_transition_delta_falsche_form_crasht(monkeypatch):
    """BEFUND (nicht behoben, Verhaltensänderung → Gate nötig):

    Liefert das LLM eine Matrix falscher Form (hier 2×2 bei k=4), greift der
    Form-Check `delta.shape == (k, k)` und die Heuristik läuft auf dem 2×2-Array
    weiter → `IndexError` (reflective_agent.py:99). Der Test dokumentiert das
    Ist-Verhalten; ein Fix wäre eine Verhaltensänderung (§9).
    """
    monkeypatch.setitem(sys.modules, "openai", _fake_openai(content="[[1,2],[3,4]]"))
    with pytest.raises(IndexError):
        ra.parse_transition_delta("wrong", 4)


def test_parse_transition_delta_reasoning_fallback(monkeypatch):
    payload = json.dumps([[2, 0, 0, 0]] * 4)
    monkeypatch.setitem(sys.modules, "openai", _fake_openai(content=None, reasoning=payload))
    assert ra.parse_transition_delta("text", 4)[0][0] == 2


def test_hmm_update_und_step_free(no_key):
    hmm = ra.HMMInertia()
    assert hmm.K == 4 and hmm.z == 0
    ch = hmm.update_from_reflection("the action was wrong")
    assert ch["lr"] == hmm.lr and len(ch["after"]) == 4
    import numpy as np
    assert np.allclose(np.array(ch["after"]).sum(axis=1), 1.0)
    out = hmm.step_free_prototype()
    assert out["state"] in ra.STATE_NAMES and out["next_state"] in ra.STATE_NAMES
    assert len(out["P_row0"]) == 4
    out2 = hmm.step_free_prototype(n_t=np.array([0.9, 0.05, 0.05]))
    assert "r" in out2


# --------------------------------------------------- Graph · Hubs · Forgetting
def _graph():
    return {
        "nodes": {
            "hub": {"content": "Hub", "last_access_days": 100.0, "recent_access": 3},
            "alt": {"content": "isoliert", "last_access_days": 0.0, "recent_access": 0},
            "ohne_metadaten": {"content": "x"},
        },
        "edges": {"hub": {"n0": 0.9, "n1": 0.9}, "alt": {"n9": 0.01}},
    }


def test_graph_hubs_forgetting_und_neighbors(tmp_path):
    g = _graph()
    p = tmp_path / "graph.json"
    p.write_text(json.dumps(g), encoding="utf-8")
    assert ra.load_graph(p) == g
    assert ra.hub_score(g, "hub") == 1.8
    assert ra.neighbors(g, "hub") == ["n0", "n1"]
    assert ra.detect_hubs(g) == ["hub"]
    assert ra.detect_forgetting(g, now_days=100.0) == ["alt"]
    # fehlende Metadaten zählen konservativ als „aktiv" (access=1)
    assert "ohne_metadaten" not in ra.detect_forgetting(g, now_days=100.0)


def test_resolve_conflict_supersede():
    facts = [{"s": "solver", "p": "v", "o": "a", "status": "valid"}]
    d = ra.resolve_conflict(facts, "solver", "v", "b", "2026-10-01")
    assert d["conflict"] is True and facts[0]["status"] == "superseded"
    assert d["added"]["o"] == "b" and len(facts) == 2
    facts2 = [{"s": "solver", "p": "v", "o": "a", "status": "superseded"}]
    assert ra.resolve_conflict(facts2, "solver", "v", "c", "2026-10-02")["conflict"] is False


def test_simulate_lifecycle():
    out = ra.simulate_lifecycle()
    assert out["consolidation"]["hubs"] == ["hub_n2"]
    assert out["forgetting"]["forgotten"] == ["isolated_n5"]   # 3 Bedingungen erfüllt
    assert out["conflict"]["conflict"] is True


# ------------------------------------------------------- Destillation / Dateien
def test_distill_ohne_llm(no_key):
    g = _graph()
    entry = ra.distill(g, "hub")
    assert entry["neighbors"] == ["n0", "n1"]
    # n0/n1 sind keine Knoten im Graph -> nur der Hub-Content kommt in den Cluster
    assert entry["summary"] == "Hub"
    assert entry["hub_score"] == 1.8


def test_distill_mit_llm_und_fehlern(monkeypatch):
    g = _graph()
    monkeypatch.setitem(sys.modules, "openai", _fake_openai(content=" Synthese "))
    assert ra.distill(g, "hub")["summary"] == "Synthese"
    monkeypatch.setitem(sys.modules, "openai", _fake_openai(content=""))
    assert ra.distill(g, "hub")["summary"].startswith("(LLM leer)")
    monkeypatch.setitem(sys.modules, "openai", _fake_openai(raises=True))
    assert ra.distill(g, "hub")["summary"].startswith("(LLM nicht verfügbar")


def test_write_semantic_und_update_index(tmp_path, monkeypatch):
    monkeypatch.setattr(ra, "STRUCTURED", tmp_path / "structured")
    monkeypatch.setattr(ra, "INDEX_DIR", tmp_path / "tier2")
    entry = {"hub": "hub_x", "neighbors": ["a", "b"], "summary": "Inhalt", "hub_score": 1.8}
    sem = ra.write_semantic(entry)
    assert sem.name == "distilled-hub-hub_x.md" and "Inhalt" in sem.read_text(encoding="utf-8")
    idx = ra.update_index(entry)
    ra.update_index({"hub": "hub_y", "neighbors": [], "summary": "s", "hub_score": 2.0})
    text = idx.read_text(encoding="utf-8")
    assert "Hub hub_x" in text and "Hub hub_y" in text      # idempotent, beide Zeilen


def test_run_once(tmp_path, monkeypatch):
    graph = _graph()
    monkeypatch.setattr(ra, "GRAPH_FILE", tmp_path / "g.json")
    (tmp_path / "g.json").write_text(json.dumps(graph), encoding="utf-8")
    monkeypatch.setattr(ra, "STRUCTURED", tmp_path / "structured")
    monkeypatch.setattr(ra, "INDEX_DIR", tmp_path / "tier2")
    monkeypatch.setitem(sys.modules, "openai", _fake_openai(raises=True))
    out = ra.run_once()
    assert out["hubs"] == ["hub"] and out["hmm_states"] == 4
    assert (tmp_path / "structured" / "distilled-hub-hub.md").exists()


# ------------------------------------------------------------- Dual-Path-Retrieval
def test_embed_cos_und_retrieval(tmp_path, monkeypatch):
    import numpy as np
    assert float(np.linalg.norm(ra._embed("a b a"))) == pytest.approx(1.0)
    assert float(np.linalg.norm(ra._embed(""))) == 0.0
    assert ra._cos(ra._embed(""), ra._embed("x")) == 0.0
    assert ra._cos(ra._embed("a"), ra._embed("a")) == pytest.approx(1.0)

    graph = {
        "nodes": {"n1": {"content": "HMM Traegheit Revise", "timestamp_days": 0.0},
                  "n2": {"content": "voellig anderes Thema", "timestamp_days": 30.0},
                  "n3": {"content": "Solver Bug Integer-Division", "timestamp_days": 0.0}},
        "edges": {"n1": {"n2": 0.9}, "n3": {"n1": 0.5}},
    }
    dr = ra.DualPathRetrieval()
    r = dr.retrieve(graph, "HMM Traegheit Revise", now_days=1.0, top_k=2)
    assert r["top_k"][0] == "n1" and len(r["top_k"]) == 2
    assert set(r["base"]) == {"n1", "n2", "n3"} and r["spread"]["n2"] > r["base"]["n2"]
    assert all(v >= dr.theta for v in r["activated"].values())

    monkeypatch.setattr(ra, "GRAPH_FILE", tmp_path / "g.json")
    (tmp_path / "g.json").write_text(json.dumps(graph), encoding="utf-8")
    assert len(ra.simulate_5_multihop()) == 5
    assert len(ra.simulate_5_multihop(graph)) == 5


def test_simulate_3_reflections_und_lyapunov(no_key):
    out = ra.simulate_3_reflections()
    assert len(out) == 3 and out[0]["lr"] == ra.HMMInertia().lr
    assert ra.lyapunov_check([1.0]) == {"E_dV": 0.0, "stable": True,
                                        "gate": "ok", "note": "zu wenig Daten"}
    ly = ra.simulate_lyapunov()
    assert ly["stable"]["stable"] is True and ly["stable"]["gate"] == "ok"
    assert ly["unstable"]["stable"] is False and ly["unstable"]["gate"] == "ask"
