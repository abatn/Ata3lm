"""Reflective Agent (data/memory/reflective_agent.py) – HMM · Hub/Forgetting · Retrieval.

Echte Verifikation (Guardrail 7): LLM-Schritte laufen gegen das **echte** Endpoint
(`_live.call`); Fehlerpfade über ein **echtes** unerreichbares Endpoint
(`OPENAI_BASE_URL=http://127.0.0.1:9`). Parsing ist als reine Funktion (`_matrix_from_raw`,
`_summary_from_raw`) mit echten Strings getestet – kein Fake-LLM.
"""

import json

import numpy as np
import pytest
import reflective_agent as ra
from _live import call

BAD = "http://127.0.0.1:9"


@pytest.fixture
def no_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)


# --------------------------------------------------------------- HMM-Trägheit
def test_row_normalize_und_noop_ohne_llm(no_key):
    """Heuristik entfernt (Rekursion 032/NOOP): ohne LLM-Key -> None, kein Default."""
    P = ra._row_normalize(np.array([[1.0, 3.0], [2.0, 2.0]]))
    assert np.allclose(P.sum(axis=1), 1.0)
    assert ra.parse_transition_delta("the action was wrong and failed", 4) is None
    assert ra.parse_transition_delta("everything matched my inertia", 4) is None


def test_parse_transition_delta_mit_llm_real():
    """Echtes LLM (Guardrail 7): liefert gültige K×K-Matrix (echte Wiederholung bis Erfolg)."""
    out = None
    for _ in range(8):
        out = call(ra.parse_transition_delta, "The action matched my usual inertia; slight bias to caution.", 4)
        if out is not None:
            break
    assert out is not None and out.shape == (4, 4)


def test_matrix_from_raw_noop_und_form():
    """Reine Parsing-Funktion mit echten Strings (kein Fake-LLM)."""
    assert ra._matrix_from_raw("kein json hier", 4) is None
    assert ra._matrix_from_raw("[[1,2],[3,4]]", 4) is None  # 2×2 statt 4×4
    d = ra._matrix_from_raw(json.dumps([[3, 0, 0, 0]] * 4), 4)
    assert d.shape == (4, 4) and d[0][0] == 3 and d[1][1] == 0


def test_parse_transition_delta_fehler_real(monkeypatch):
    """Echtes unerreichbares Endpoint -> NOOP (None), kein Crash."""
    monkeypatch.setenv("OPENAI_BASE_URL", BAD)
    assert ra.parse_transition_delta("wrong", 4) is None


def test_hmm_update_noop_ohne_matrix(no_key):
    """NOOP: ohne gültige LLM-Matrix bleibt P_t unverändert (Mem0 NONE)."""
    hmm = ra.HMMInertia()
    before = [row[:] for row in hmm.P.tolist()]
    ch = hmm.update_from_reflection("the action was wrong")
    assert ch["skipped"] is True and ch["delta"] is None
    assert ch["note"] == ra.HMM_NOOP_NOTE
    assert hmm.P.tolist() == before
    assert len(ch["after"]) == 4 and ch["lr"] == hmm.lr


def test_hmm_update_mit_delta_real():
    """Eq. 2 mit echter numerischer Δ-Matrix (kein LLM): P_t wird geändert."""
    hmm = ra.HMMInertia()
    before = hmm.P.copy()
    ch = hmm.update_from_reflection("beliebig", delta=np.array([[1.0, 0, 0, 0]] * 4))
    assert ch["skipped"] is False and ch["delta"][0][0] == 1
    assert np.allclose(np.array(ch["after"]).sum(axis=1), 1.0)
    assert not np.allclose(hmm.P, before)


def test_step_free_prototype(no_key):
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
    assert out["forgetting"]["forgotten"] == ["isolated_n5"]
    assert out["conflict"]["conflict"] is True


# ------------------------------------------------------- Destillation / Dateien
def test_distill_ohne_llm(no_key):
    g = _graph()
    entry = ra.distill(g, "hub")
    assert entry["neighbors"] == ["n0", "n1"]
    assert entry["summary"] == "Hub"
    assert entry["hub_score"] == 1.8


def test_summary_from_raw():
    assert ra._summary_from_raw(" Synthese ", "c") == "Synthese"
    assert ra._summary_from_raw("", "c").startswith("(LLM leer)")


def test_distill_mit_llm_real():
    """Echtes LLM; bei transientem Endpoint-Fehler erneut (real, kein Fake)."""
    g = _graph()
    out = call(ra.distill, g, "hub")
    for _ in range(6):
        if not out["summary"].startswith("(LLM nicht verfügbar"):
            break
        out = call(ra.distill, g, "hub")
    assert isinstance(out["summary"], str) and out["summary"]
    assert not out["summary"].startswith("(LLM nicht verfügbar")


def test_distill_fehler_real(monkeypatch):
    monkeypatch.setenv("OPENAI_BASE_URL", BAD)
    assert ra.distill(_graph(), "hub")["summary"].startswith("(LLM nicht verfügbar")


def test_write_semantic_und_update_index(tmp_path, monkeypatch):
    monkeypatch.setattr(ra, "STRUCTURED", tmp_path / "structured")
    monkeypatch.setattr(ra, "INDEX_DIR", tmp_path / "tier2")
    entry = {"hub": "hub_x", "neighbors": ["a", "b"], "summary": "Inhalt", "hub_score": 1.8}
    sem = ra.write_semantic(entry)
    assert sem.name == "distilled-hub-hub_x.md" and "Inhalt" in sem.read_text(encoding="utf-8")
    idx = ra.update_index(entry)
    ra.update_index({"hub": "hub_y", "neighbors": [], "summary": "s", "hub_score": 2.0})
    text = idx.read_text(encoding="utf-8")
    assert "Hub hub_x" in text and "Hub hub_y" in text


def _run_once_env(tmp_path, monkeypatch):
    graph = _graph()
    monkeypatch.setattr(ra, "GRAPH_FILE", tmp_path / "g.json")
    (tmp_path / "g.json").write_text(json.dumps(graph), encoding="utf-8")
    monkeypatch.setattr(ra, "STRUCTURED", tmp_path / "structured")
    monkeypatch.setattr(ra, "INDEX_DIR", tmp_path / "tier2")
    monkeypatch.setenv("OPENAI_BASE_URL", BAD)  # echtes, unerreichbares Endpoint


def test_run_once(tmp_path, monkeypatch):
    _run_once_env(tmp_path, monkeypatch)
    monkeypatch.setenv("RQGM_LOOP", "0")
    out = ra.run_once()
    assert out["hubs"] == ["hub"] and out["hmm_states"] == 4
    assert out["distilled"][0]["hmm_skipped"] is True
    assert out["rqgm"] is None
    assert (tmp_path / "structured" / "distilled-hub-hub.md").exists()


def test_run_once_rqgm_default_an(tmp_path, monkeypatch):
    _run_once_env(tmp_path, monkeypatch)
    monkeypatch.delenv("RQGM_LOOP", raising=False)
    out = ra.run_once()
    assert out["rqgm"] is not None
    assert out["rqgm"]["report"]["current"] == "evaluator_v3"


def test_run_once_mit_rqgm_loop(tmp_path, monkeypatch):
    _run_once_env(tmp_path, monkeypatch)
    monkeypatch.setenv("RQGM_LOOP", "1")
    out = ra.run_once()
    assert out["rqgm"] is not None
    assert len(out["rqgm"]["trajectory"]) == 8
    assert out["rqgm"]["report"]["current"] == "evaluator_v3"


# ------------------------------------------------------------- Dual-Path-Retrieval
def test_embed_cos_und_retrieval(tmp_path, monkeypatch):
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


def test_simulate_3_reflections_real():
    """Echtes LLM: 3 Reflexionen, je ein Ergebnis (skipped je nach Modell)."""
    out = call(ra.simulate_3_reflections)
    assert len(out) == 3 and all("skipped" in r for r in out)


def test_lyapunov_check_und_simulate(no_key):
    assert ra.lyapunov_check([1.0]) == {"E_dV": 0.0, "stable": True, "gate": "ok", "note": "zu wenig Daten"}
    ly = ra.simulate_lyapunov()
    assert ly["stable"]["stable"] is True and ly["stable"]["gate"] == "ok"
    assert ly["unstable"]["stable"] is False and ly["unstable"]["gate"] == "ask"


def test_run_once_mit_pipeline_route(tmp_path, monkeypatch):
    """A) pipeline hat einen Aufrufer (opt-in PIPELINE_ROUTE=1)."""
    _run_once_env(tmp_path, monkeypatch)
    monkeypatch.setattr(ra, "ROOT", tmp_path)
    monkeypatch.setattr(ra, "HMMInertia", lambda: _NullHMM())
    monkeypatch.setenv("RQGM_LOOP", "0")
    monkeypatch.setenv("PIPELINE_ROUTE", "1")
    out = ra.run_once()
    assert out["pipeline"] and out["pipeline"][0]["action"] == "write-new"
    assert (tmp_path / "data/memory/tier3-working").exists()


class _NullHMM:
    K = 4
    lr = 0.05

    def update_from_reflection(self, text, delta=None):
        return {"before": [], "after": [], "delta": None, "skipped": True, "note": "test"}


def test_matrix_from_raw_ungueltiges_json():
    """Ungültiges JSON mit Klammern -> except-Zweig -> None (reine Funktion)."""
    assert ra._matrix_from_raw("[1,2,]", 4) is None
