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
            return SimpleNamespace(
                choices=[
                    SimpleNamespace(
                        message=SimpleNamespace(
                            **(
                                {"content": content}
                                if reasoning is None
                                else {"content": content, "reasoning_content": reasoning}
                            )
                        )
                    )
                ]
            )

    class Client:
        def __init__(self, *a, **kw):
            self.chat = SimpleNamespace(completions=Completions())

    return SimpleNamespace(OpenAI=Client)


@pytest.fixture
def no_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)


# --------------------------------------------------------------- HMM-Trägheit
def test_row_normalize_und_noop_ohne_llm(no_key):
    """Heuristik entfernt (Rekursion 032/NOOP): ohne LLM-Key -> None, kein Default."""
    import numpy as np

    P = ra._row_normalize(np.array([[1.0, 3.0], [2.0, 2.0]]))
    assert np.allclose(P.sum(axis=1), 1.0)
    assert ra.parse_transition_delta("the action was wrong and failed", 4) is None
    assert ra.parse_transition_delta("everything matched my inertia", 4) is None


def test_parse_transition_delta_mit_llm(monkeypatch):
    payload = json.dumps([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]])
    monkeypatch.setitem(sys.modules, "openai", _fake_openai(content=payload))
    delta = ra.parse_transition_delta("text", 4)
    assert delta[0][0] == 1 and delta[3][3] == 1


def test_parse_transition_delta_noop_bei_kein_json_und_fehler(monkeypatch):
    """NOOP: kein JSON bzw. LLM-Fehler -> None (keine Faustregel, kein Crash)."""
    monkeypatch.setitem(sys.modules, "openai", _fake_openai(content="kein json"))
    assert ra.parse_transition_delta("wrong", 4) is None
    monkeypatch.setitem(sys.modules, "openai", _fake_openai(raises=True))
    assert ra.parse_transition_delta("wrong", 4) is None


def test_parse_transition_delta_falsche_form_ist_noop(monkeypatch):
    """2×2 statt 4×4 -> NOOP: None (verworfen), keine Ersatz-Matrix, kein Crash."""
    monkeypatch.setitem(sys.modules, "openai", _fake_openai(content="[[1,2],[3,4]]"))
    assert ra.parse_transition_delta("wrong", 4) is None


def test_parse_transition_delta_4x4_wird_uebernommen(monkeypatch):
    """Strenge Form-Prüfung: korrekte K×K-Matrix kommt unverändert durch."""
    monkeypatch.setitem(sys.modules, "openai", _fake_openai(content=json.dumps([[3, 0, 0, 0]] * 4)))
    delta = ra.parse_transition_delta("beliebig", 4)
    assert delta.shape == (4, 4) and delta[0][0] == 3 and delta[1][1] == 0


def test_parse_transition_delta_reasoning_fallback(monkeypatch):
    payload = json.dumps([[2, 0, 0, 0]] * 4)
    monkeypatch.setitem(sys.modules, "openai", _fake_openai(content=None, reasoning=payload))
    assert ra.parse_transition_delta("text", 4)[0][0] == 2


def test_hmm_update_noop_ohne_matrix(no_key):
    """NOOP: ohne gültige LLM-Matrix bleibt P_t unverändert (Mem0 NONE)."""
    hmm = ra.HMMInertia()
    before = [row[:] for row in hmm.P.tolist()]
    ch = hmm.update_from_reflection("the action was wrong")
    assert ch["skipped"] is True and ch["delta"] is None
    assert ch["note"] == ra.HMM_NOOP_NOTE
    assert hmm.P.tolist() == before  # kein Update, kein Crash
    assert len(ch["after"]) == 4 and ch["lr"] == hmm.lr


def test_hmm_update_mit_llm_matrix(monkeypatch):
    import numpy as np

    monkeypatch.setitem(sys.modules, "openai", _fake_openai(content=json.dumps([[1, 0, 0, 0]] * 4)))
    hmm = ra.HMMInertia()
    ch = hmm.update_from_reflection("reflection")
    assert ch["skipped"] is False and ch["delta"][0][0] == 1
    assert np.allclose(np.array(ch["after"]).sum(axis=1), 1.0)
    assert ch["after"] != ch["before"]  # P_t wurde geändert


def test_step_free_prototype(no_key):
    import numpy as np

    hmm = ra.HMMInertia()
    assert hmm.K == 4 and hmm.z == 0
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
    assert out["forgetting"]["forgotten"] == ["isolated_n5"]  # 3 Bedingungen erfüllt
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
    assert "Hub hub_x" in text and "Hub hub_y" in text  # idempotent, beide Zeilen


def test_run_once(tmp_path, monkeypatch):
    graph = _graph()
    monkeypatch.setattr(ra, "GRAPH_FILE", tmp_path / "g.json")
    (tmp_path / "g.json").write_text(json.dumps(graph), encoding="utf-8")
    monkeypatch.setattr(ra, "STRUCTURED", tmp_path / "structured")
    monkeypatch.setattr(ra, "INDEX_DIR", tmp_path / "tier2")
    monkeypatch.setitem(sys.modules, "openai", _fake_openai(raises=True))
    monkeypatch.setenv("RQGM_LOOP", "0")  # explizit aus (Debug)
    out = ra.run_once()
    assert out["hubs"] == ["hub"] and out["hmm_states"] == 4
    assert out["distilled"][0]["hmm_skipped"] is True  # NOOP (LLM nicht erreichbar)
    assert out["rqgm"] is None  # RQGM_LOOP=0 -> aus
    assert (tmp_path / "structured" / "distilled-hub-hub.md").exists()


def test_run_once_rqgm_default_an(tmp_path, monkeypatch):
    graph = _graph()
    monkeypatch.setattr(ra, "GRAPH_FILE", tmp_path / "g.json")
    (tmp_path / "g.json").write_text(json.dumps(graph), encoding="utf-8")
    monkeypatch.setattr(ra, "STRUCTURED", tmp_path / "structured")
    monkeypatch.setattr(ra, "INDEX_DIR", tmp_path / "tier2")
    monkeypatch.setitem(sys.modules, "openai", _fake_openai(raises=True))
    monkeypatch.delenv("RQGM_LOOP", raising=False)  # Default = an
    out = ra.run_once()
    assert out["rqgm"] is not None
    assert out["rqgm"]["report"]["current"] == "evaluator_v3"


def test_run_once_mit_rqgm_loop(tmp_path, monkeypatch):
    graph = _graph()
    monkeypatch.setattr(ra, "GRAPH_FILE", tmp_path / "g.json")
    (tmp_path / "g.json").write_text(json.dumps(graph), encoding="utf-8")
    monkeypatch.setattr(ra, "STRUCTURED", tmp_path / "structured")
    monkeypatch.setattr(ra, "INDEX_DIR", tmp_path / "tier2")
    monkeypatch.setitem(sys.modules, "openai", _fake_openai(raises=True))
    monkeypatch.setenv("RQGM_LOOP", "1")  # §9.3 freigegeben
    out = ra.run_once()
    assert out["rqgm"] is not None
    assert len(out["rqgm"]["trajectory"]) == 8
    assert out["rqgm"]["report"]["current"] == "evaluator_v3"


# ------------------------------------------------------------- Dual-Path-Retrieval
def test_embed_cos_und_retrieval(tmp_path, monkeypatch):
    import numpy as np

    assert float(np.linalg.norm(ra._embed("a b a"))) == pytest.approx(1.0)
    assert float(np.linalg.norm(ra._embed(""))) == 0.0
    assert ra._cos(ra._embed(""), ra._embed("x")) == 0.0
    assert ra._cos(ra._embed("a"), ra._embed("a")) == pytest.approx(1.0)

    graph = {
        "nodes": {
            "n1": {"content": "HMM Traegheit Revise", "timestamp_days": 0.0},
            "n2": {"content": "voellig anderes Thema", "timestamp_days": 30.0},
            "n3": {"content": "Solver Bug Integer-Division", "timestamp_days": 0.0},
        },
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


def test_simulate_3_reflections_noop_ohne_llm(no_key):
    out = ra.simulate_3_reflections()
    assert len(out) == 3 and out[0]["lr"] == ra.HMMInertia().lr
    assert all(r["skipped"] is True and r["delta_row0"] is None for r in out)
    assert all(r["note"] == ra.HMM_NOOP_NOTE for r in out)


def test_simulate_3_reflections_mit_llm(monkeypatch):
    monkeypatch.setitem(sys.modules, "openai", _fake_openai(content=json.dumps([[1, 0, 0, 0]] * 4)))
    out = ra.simulate_3_reflections()
    assert len(out) == 3 and all(r["skipped"] is False for r in out)
    assert out[0]["delta_row0"][0] == 1


def test_lyapunov_check_und_simulate(no_key):
    assert ra.lyapunov_check([1.0]) == {"E_dV": 0.0, "stable": True, "gate": "ok", "note": "zu wenig Daten"}
    ly = ra.simulate_lyapunov()
    assert ly["stable"]["stable"] is True and ly["stable"]["gate"] == "ok"
    assert ly["unstable"]["stable"] is False and ly["unstable"]["gate"] == "ask"
