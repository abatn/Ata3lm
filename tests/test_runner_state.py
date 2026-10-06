"""K1: Geteilter persistenter Runner-Zustand – Snapshot/Reconstruct/Restart (Auftrag K1).

Abnahme (Bericht §4, Prio 1): 2. Prozess liest State; WM/Graph/HMM/Drift fortgesetzt
(Restart-Test, echter Subprozess). K1-STOPP: Snapshot NIE nur Schlüssel ohne
Inhalte/Metadaten (`validate`).
"""

import json
import os
import subprocess
import sys
from pathlib import Path

import ingestion_hook
import lru_cache
import numpy as np
import pytest
import reflective_agent
import runner_state as rs

ROOT = Path(__file__).resolve().parents[1]


def _wm_graph_hmm():
    wm = lru_cache.WorkingMemory(capacity=15)
    wm.store("raw:q", "Inhalt A", importance=0.7)
    graph = ingestion_hook.MemoryGraph()
    graph.add_node("n1", last_access=5.0, recent_access=2)
    graph.edges[("n1", "related", "n2")] = 0.5
    graph.add_node("n2")
    hmm = reflective_agent.HMMInertia(states=4, lr=0.05, beta=4.0)
    hmm.P = np.full((4, 4), 0.25)
    return wm, graph, hmm


# --------------------------------------------------------------- Snapshot/Validate
def test_snapshot_enthalt_inhalte_metadaten_und_freigaben():
    wm, graph, hmm = _wm_graph_hmm()
    st = rs.snapshot(
        wm=wm,
        graph=graph,
        hmm=hmm,
        drift_reference={"write": 1.0},
        schema={"structured": 3},
        open_approvals=[{"subject": "Gesetz X", "state": "first_approved"}],
        runner="lifecycle-runner",
        now=100.0,
    )
    assert st["wm"]["items"]["raw:q"]["value"] == "Inhalt A"  # Inhalt, NIE nur Schlüssel
    assert st["wm"]["items"]["raw:q"]["importance"] == 0.7  # Metadaten
    assert st["graph"]["edges"] == [["n1", "related", "n2", 0.5]]
    assert len(st["hmm"]["P"]) == 4 and st["hmm"]["lr"] == 0.05
    assert st["drift"]["reference"] == {"write": 1.0}
    assert st["schema"] == {"structured": 3}  # Schema-/Revisionsstand
    assert st["open_approvals"][0]["state"] == "first_approved"  # offene Freigaben
    assert st["schema_version"] == rs.SCHEMA_VERSION


def test_validate_stoppt_nur_schluessel_ohne_inhalt():
    with pytest.raises(rs.StateError, match="schema_version"):
        rs.validate({"wm": None, "schema": {}, "open_approvals": []})
    with pytest.raises(rs.StateError, match="Schema-/Revisionsstand"):
        rs.validate({"schema_version": 1, "schema": "x", "open_approvals": []})
    with pytest.raises(rs.StateError, match="offene Freigaben"):
        rs.validate({"schema_version": 1, "schema": {}, "open_approvals": "x"})
    with pytest.raises(rs.StateError, match="nur Schlüssel"):
        rs.validate({"schema_version": 1, "schema": {}, "open_approvals": [], "wm": {"items": ["a", "b"]}})
    with pytest.raises(rs.StateError, match="ohne Inhalt/Metadaten"):
        rs.validate({"schema_version": 1, "schema": {}, "open_approvals": [], "wm": {"items": {"k": "roh"}}})
    with pytest.raises(rs.StateError, match="ohne Inhalt/Metadaten"):
        rs.validate({"schema_version": 1, "schema": {}, "open_approvals": [], "wm": {"items": {"k": {"last_used": 1}}}})
    with pytest.raises(rs.StateError, match="ohne Inhalt/Metadaten"):
        rs.validate({"schema_version": 1, "schema": {}, "open_approvals": [], "wm": {"items": {"k": {"value": "v"}}}})
    with pytest.raises(rs.StateError, match="Knoten"):
        rs.validate({"schema_version": 1, "schema": {}, "open_approvals": [], "graph": {"edges": []}})
    with pytest.raises(rs.StateError, match="Übergangsmatrix"):
        rs.validate({"schema_version": 1, "schema": {}, "open_approvals": [], "hmm": {"states": 4}})


def test_snapshot_stoppt_ohne_inhalt(tmp_path):
    bad = {"schema_version": 1, "schema": {}, "open_approvals": [], "wm": {"items": {"k": ["nur", "keys"]}}}
    with pytest.raises(rs.StateError):
        rs.save(bad, tmp_path / "state.json")  # STOPP vor jedem Schreiben
    assert not (tmp_path / "state.json").exists()


# -------------------------------------------------------- Persistenz (atomar+Lock)
def test_save_load_roundtrip(tmp_path):
    wm, graph, hmm = _wm_graph_hmm()
    st = rs.snapshot(wm=wm, graph=graph, hmm=hmm, now=1.0)
    res = rs.save(st, tmp_path / "state.json")
    assert res["ok"] is True and res["bytes"] > 0
    loaded = rs.load(tmp_path / "state.json")
    assert loaded["wm"]["items"]["raw:q"]["value"] == "Inhalt A"
    assert rs.load(tmp_path / "fehlt.json") is None  # Cold-Start


def test_save_lock_bei_nebenlaeufigkeit(tmp_path):
    wm, graph, hmm = _wm_graph_hmm()
    st = rs.snapshot(wm=wm, graph=graph, hmm=hmm, now=1.0)
    p = tmp_path / "state.json"
    rs.save(st, p)
    lock = tmp_path / "state.json.lock"
    lock.write_text("pid-anders", encoding="utf-8")  # paralleler Schreiber hält den Lock
    res = rs.save(st, p)
    assert res["ok"] is False and "Nebenläufigkeit" in res["reason"]


def test_save_stale_lock_wird_ersetzt(tmp_path):
    wm, graph, hmm = _wm_graph_hmm()
    st = rs.snapshot(wm=wm, graph=graph, hmm=hmm, now=1.0)
    p = tmp_path / "state.json"
    lock = tmp_path / "state.json.lock"
    lock.write_text("abgebrochen", encoding="utf-8")
    os.utime(lock, (1.0, 1.0))  # alter Lock: Schreiber abgebrochen
    res = rs.save(st, p)
    assert res["ok"] is True and not lock.exists()


def test_load_recovery_nach_schreibabbruch(tmp_path):
    wm, graph, hmm = _wm_graph_hmm()
    st = rs.snapshot(wm=wm, graph=graph, hmm=hmm, now=1.0)
    payload = json.dumps(st)
    p = tmp_path / "state.json"
    # (a) Abbruch VOR os.replace: nur tmp vorhanden -> Wiederherstellung
    (tmp_path / "state.json.tmp").write_text(payload, encoding="utf-8")
    loaded = rs.load(p)
    assert loaded["wm"]["items"]["raw:q"]["value"] == "Inhalt A"
    assert p.exists()  # wiederhergestellter Zustand festgehalten
    # (b) korrupte Hauptdatei + heile tmp -> tmp gewinnt
    p.write_text("{kaputt", encoding="utf-8")
    (tmp_path / "state.json.tmp").write_text(payload, encoding="utf-8")
    assert rs.load(p)["wm"]["items"]["raw:q"]["value"] == "Inhalt A"
    # (c) korrupt ohne Recovery -> StateError
    p.write_text("{kaputt", encoding="utf-8")
    (tmp_path / "state.json.tmp").unlink(missing_ok=True)
    with pytest.raises(rs.StateError, match="korrupt"):
        rs.load(p)


# ---------------------------------------------------------------- Rekonstruktion
def test_reconstruct_setzt_wm_graph_hmm_drift_fort():
    wm, graph, hmm = _wm_graph_hmm()
    st = rs.snapshot(wm=wm, graph=graph, hmm=hmm, drift_reference={"non-write": 1.0}, now=1.0)
    rec = rs.reconstruct(st)
    assert rec["wm"].items["raw:q"]["value"] == "Inhalt A"
    assert {"hits", "pinned", "importance"} <= set(rec["wm"].items["raw:q"])  # Metadaten erhalten
    assert rec["graph"].edges[("n1", "related", "n2")] == 0.5 and set(rec["graph"].nodes) == {"n1", "n2"}
    assert np.allclose(rec["hmm"].P, 0.25) and rec["hmm"].K == 4
    assert rec["drift_reference"] == {"non-write": 1.0}


def test_reconstruct_ohne_teile():
    rec = rs.reconstruct(rs.snapshot(now=1.0))
    assert rec == {"wm": None, "graph": None, "hmm": None, "drift_reference": None}


# ------------------------------------------------------------- Restart (2. Prozess)
def test_restart_zweiter_prozess_liest_state(tmp_path):
    """K1-Abnahme: ein echter 2. Prozess setzt WM/Graph/HMM/Drift fort (Restart-Test)."""
    wm, graph, hmm = _wm_graph_hmm()
    st = rs.snapshot(wm=wm, graph=graph, hmm=hmm, drift_reference={"write": 1.0}, now=1.0)
    p = tmp_path / "state.json"
    rs.save(st, p)
    code = (
        "import json, sys\n"
        "import runner_state\n"
        "rec = runner_state.reconstruct(runner_state.load(sys.argv[1]))\n"
        "print(json.dumps({"
        "'wm': rec['wm'].items['raw:q']['value'], "
        "'edge': rec['graph'].edges[('n1', 'related', 'n2')], "
        "'hmm_P': round(float(rec['hmm'].P[0][0]), 4), "
        "'drift': rec['drift_reference']}))\n"
    )
    env = dict(os.environ)
    env["PYTHONPATH"] = os.pathsep.join(
        [
            str(ROOT / "data/memory"),
            str(ROOT / "data/memory/shared"),
            str(ROOT / "data/memory/tier3-working"),
            str(ROOT / "skills"),
        ]
    )
    out = subprocess.run([sys.executable, "-c", code, str(p)], capture_output=True, text=True, check=True, env=env)
    data = json.loads(out.stdout.strip().splitlines()[-1].replace("'", '"'))
    assert data["wm"] == "Inhalt A"  # WM-Inhalt fortgesetzt
    assert data["edge"] == 0.5  # Graph fortgesetzt
    assert data["hmm_P"] == 0.25  # HMM fortgesetzt
    assert data["drift"] == {"write": 1.0}  # Drift-Checkpoint fortgesetzt


# ------------------------------------------------------- Integration in beide Runner
def test_runner_teilen_state_ueber_beide_laeufe(tmp_path, monkeypatch):
    """K1: 8-Stufen- und 5-Phasen-Runner nutzen denselben persistierten Zustand."""
    import lifecycle_runner as lr
    import recursion_runner as rr

    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setenv("LIFECYCLE_DRIFT_REFERENCE", str(tmp_path / "drift.json"))
    p = tmp_path / "state.json"
    out = lr.run_cycle(
        "Wo?",
        "Fakt",
        "Fakt",
        classify_fn=lambda q, f, c: {"class": "write-new"},
        structured_dir=tmp_path / "s",
        tier3_dir=tmp_path / "t",
        state_path=p,
    )
    assert out["results"]["Wissen"]["added_edges"] == 0  # kein explizites relations-Argument
    assert p.exists() and "raw:wo" in rs.load(p)["wm"]["items"]  # WM-Inhalt persistiert
    out2 = rr.run_recursion(
        "Wo?",
        "Fakt",
        "Fakt",
        classify_fn=lambda q, f, c: {"class": "write-new"},
        mandate_obj=lr._default_mandate(),
        structured_dir=tmp_path / "s2",
        tier3_dir=tmp_path / "t2",
        delta=np.full((4, 4), 0.05),
        successes=1,
        state_path=p,
    )
    assert out2["results"]["Konstrukt"]["pi0"] == "uniform (SEAA Listing 1)"  # erster HMM-Lauf
    out3 = rr.run_recursion(
        "Wo?",
        "Fakt",
        "Fakt",
        classify_fn=lambda q, f, c: {"class": "write-new"},
        mandate_obj=lr._default_mandate(),
        structured_dir=tmp_path / "s3",
        tier3_dir=tmp_path / "t3",
        delta=np.full((4, 4), 0.05),
        successes=1,
        state_path=p,
    )
    assert out3["results"]["Konstrukt"]["pi0"] == "fortgesetzt (K1 Runner-State)"  # Restart
    st = rs.load(p)
    assert st["runner"] == "recursion-runner"
    assert st["hmm"] is not None  # HMM im gemeinsamen State
    assert "raw:wo" in st["wm"]["items"]  # WM-Inhalt aus dem 1. Lauf erhalten


def test_recursion_state_coldstart_ohne_state_file(tmp_path, monkeypatch):
    """K1: `run_recursion` mit state_path, aber ohne vorhandenen State (Cold-Start-Zweig)."""
    import lifecycle_runner as lr
    import recursion_runner as rr

    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    p = tmp_path / "neu.json"  # existiert NICHT -> resumed is None
    out = rr.run_recursion(
        "Q",
        "F",
        "C",
        classify_fn=lambda q, f, c: {"class": "non-write"},
        mandate_obj=lr._default_mandate(),
        structured_dir=tmp_path / "s",
        tier3_dir=tmp_path / "t",
        state_path=p,
    )
    assert out["results"]["Konstrukt"]["pi0"] == "uniform (SEAA Listing 1)"
    assert p.exists()  # State wird nach dem Lauf gespeichert


# ------------------------------------------------------- R06: echtes CAS (rev)
def test_cas_verhindert_lost_update(tmp_path):
    """R06: zwei Leser ab rev 0 → der zweite Schreiber verliert nicht still (kein Overwrite)."""
    wm, graph, hmm = _wm_graph_hmm()
    p = tmp_path / "state.json"
    assert rs.save(rs.snapshot(wm=wm, graph=graph, hmm=hmm, now=1.0), p, expected_rev=0)["ok"] is True
    assert rs.load(p)["rev"] == 1
    # Leser B hat noch rev 0 im Kopf, A hat inzwischen rev 1 geschrieben
    res = rs.save(rs.snapshot(now=2.0), p, expected_rev=0)
    assert res["ok"] is False and "CAS" in res["reason"] and res["rev"] == 1
    assert rs.load(p)["rev"] == 1  # A's Stand bleibt erhalten
    # Leser B liest frisch (rev 1) → Schreiben gelingt, rev wird monoton fortgesetzt
    fresh = rs.load(p)
    assert rs.save(rs.snapshot(now=3.0), p, expected_rev=fresh["rev"])["ok"] is True
    assert rs.load(p)["rev"] == 2


def test_cas_ohne_expected_rev_ist_rueckwaertskompatibel(tmp_path):
    """R06: ohne `expected_rev` bleibt der alte Vertrag; `rev` wird trotzdem fortgeschrieben."""
    st = rs.snapshot(now=1.0)
    p = tmp_path / "state.json"
    assert rs.save(st, p)["ok"] is True and rs.load(p)["rev"] == 1
    assert rs.save(st, p)["ok"] is True and rs.load(p)["rev"] == 2


def test_current_rev_fehlt_korrupt_und_gueltig(tmp_path):
    """R06: `_current_rev` fällt bei fehlender/korrupter/nicht-int Revision auf 0 zurück."""
    p = tmp_path / "state.json"
    assert rs._current_rev(p) == 0  # fehlt
    p.write_text("{kaputt", encoding="utf-8")
    assert rs._current_rev(p) == 0  # korruptes JSON
    p.write_text("[1, 2]", encoding="utf-8")
    assert rs._current_rev(p) == 0  # kein Dict
    p.write_text('{"rev": "x"}', encoding="utf-8")
    assert rs._current_rev(p) == 0  # nicht int-bar
    p.write_text('{"rev": 5}', encoding="utf-8")
    assert rs._current_rev(p) == 5


# ----------------------------------------------- R19: Policy + LRU-Reihenfolge
def test_snapshot_policy_und_reihenfolge_bleiben(tmp_path):
    """R19: Restart darf Policy + Eintragsreihenfolge (z→a) nicht verändern."""
    wm = lru_cache.WorkingMemory(capacity=15, policy="lru")
    for key in ("z", "a", "m"):
        wm.store(key, key.upper())
    st = rs.snapshot(wm=wm, now=1.0)
    assert st["wm"]["policy"] == "lru"
    assert list(st["wm"]["items"].keys()) == ["z", "a", "m"]
    rec = rs.reconstruct(st)
    assert rec["wm"].policy == "lru"
    assert list(rec["wm"].items.keys()) == ["z", "a", "m"]  # nicht alphabetisch sortiert
    p = tmp_path / "state.json"
    rs.save(st, p)
    assert list(rs.load(p)["wm"]["items"].keys()) == ["z", "a", "m"]  # kein sort_keys


# ------------------------------- R05: Richtungswechsel 5-Phasen -> 8-Stufen
def test_richtungswechsel_5zu8_legt_keine_none_defaults(tmp_path, monkeypatch):
    """R05: 5-Phasen-Cold-Start (wm/graph=None) → 8-Stufen-Resume darf Defaults nicht überschreiben."""
    import lifecycle_runner as lr
    import recursion_runner as rr

    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setenv("LIFECYCLE_DRIFT_REFERENCE", str(tmp_path / "drift.json"))
    p = tmp_path / "state.json"
    rr.run_recursion(
        "Q",
        "F",
        "C",
        classify_fn=lambda q, f, c: {"class": "non-write"},
        mandate_obj=lr._default_mandate(),
        structured_dir=tmp_path / "s",
        tier3_dir=tmp_path / "t",
        state_path=p,
    )
    st = rs.load(p)
    assert st["wm"] is None and st["graph"] is None  # Cold-Start-Zustand (R05-Auslöser)
    out = lr.run_cycle(  # 8-Stufen-Resume: früher AttributeError (NoneType.store)
        "Wo?",
        "Fakt",
        "Fakt",
        classify_fn=lambda q, f, c: {"class": "write-new"},
        structured_dir=tmp_path / "s2",
        tier3_dir=tmp_path / "t2",
        state_path=p,
    )
    assert out["results"]["Erfahrung"]["stored"].startswith("raw:")
    assert rs.load(p)["wm"] is not None  # Defaults fortan persistiert


def test_lifecycle_state_resume_zweiter_lauf(tmp_path, monkeypatch):
    """K1: der 8-Stufen-Runner setzt beim 2. Lauf den gespeicherten State fort (359-361)."""
    import lifecycle_runner as lr

    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setenv("LIFECYCLE_DRIFT_REFERENCE", str(tmp_path / "drift.json"))
    p = tmp_path / "state.json"
    lr.run_cycle(
        "Wo?",
        "Fakt A",
        "Fakt A",
        classify_fn=lambda q, f, c: {"class": "write-new"},
        structured_dir=tmp_path / "s1",
        tier3_dir=tmp_path / "t1",
        state_path=p,
    )
    out2 = lr.run_cycle(  # 2. Lauf -> `resumed is not None` (Resume-Zweig)
        "Wo?",
        "Fakt B",
        "Fakt B",
        classify_fn=lambda q, f, c: {"class": "write-new"},
        structured_dir=tmp_path / "s2",
        tier3_dir=tmp_path / "t2",
        state_path=p,
    )
    assert out2["results"]["Erfahrung"]["stored"].startswith("raw:")
    assert "raw:wo" in rs.load(p)["wm"]["items"]  # WM-Inhalt über den Restart erhalten
