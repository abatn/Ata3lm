"""Offline-Unit-Tests für ``scripts/live_run.py`` (Guardrail 7: kein Netz, keine Fakes).

Getestet werden die **testbaren Helfer** (`_summarize_cycle`, `_summarize_recursion`,
`_load_tasks`, `_resolve_endpoint`, `_record_to_task`) auf Stub-Daten bzw. mit
injiziertem Loader. Der **echte** Lauf (ZsRE + NVIDIA-Endpoint) wird separat vom
Auftraggeber gestartet; fehlt der Key, bricht das Skript mit klarem Fehler ab.
"""

import importlib.util
from pathlib import Path

import pytest

_SPEC = importlib.util.spec_from_file_location(
    "live_run",
    Path(__file__).resolve().parents[1] / "scripts" / "live_run.py",
)
live_run = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(live_run)


# --------------------------------------------------------------- _summarize_cycle
def test_summarize_cycle_stub_felder():
    out = {
        "stages": ["Erfahrung", "Wissen", "Gedächtnis", "Wissen+"],
        "results": {
            "Gedächtnis": {"stage": "Gedächtnis", "ok": True, "action": "write-new", "steps": [["fwr", "write-new"]]},
            "Wissen+": {"stage": "Wissen+", "DI": 0.0, "gate": "allow", "revised": True},
        },
    }
    summary = live_run._summarize_cycle(out)
    assert summary["stages"] == ["Erfahrung", "Wissen", "Gedächtnis", "Wissen+"]
    assert summary["ok"] is True
    assert summary["action"] == "write-new"
    assert summary["gate"] == "allow"
    assert summary["revised"] is True
    assert summary["DI"] == 0.0
    assert summary["results"] is out["results"]


def test_summarize_cycle_fehlende_felder_robust():
    summary = live_run._summarize_cycle({})
    assert summary["stages"] == []
    assert summary["ok"] is None
    assert summary["gate"] is None
    assert summary["results"] == {}


# ----------------------------------------------------------- _summarize_recursion
def test_summarize_recursion_stub_felder():
    out = {
        "phases": ["Konstrukt", "Akt", "Observe", "Compare", "Revise"],
        "results": {
            "Akt": {"phase": "Akt", "ok": True, "action": "non-write", "gate": "allow"},
            "Compare": {"phase": "Compare", "observed": True, "score": 1.0, "gate": "allow"},
            "Revise": {"phase": "Revise", "skipped": False, "lr": 0.05},
        },
    }
    summary = live_run._summarize_recursion(out)
    assert summary["phases"] == ["Konstrukt", "Akt", "Observe", "Compare", "Revise"]
    assert summary["ok"] is True
    assert summary["action"] == "non-write"
    assert summary["gate"] == "allow"
    assert summary["observed"] is True
    assert summary["score"] == 1.0
    assert summary["compare_gate"] == "allow"
    assert summary["revised"] is True
    assert summary["results"] is out["results"]


def test_summarize_recursion_skipped_und_leer():
    out = {"phases": ["Akt", "Compare"], "results": {"Akt": {"ok": False}, "Compare": {"observed": False}}}
    summary = live_run._summarize_recursion(out)
    assert summary["ok"] is False
    assert summary["observed"] is False
    assert summary["revised"] is None  # keine Revise-Phase -> keine Aussage
    assert live_run._summarize_recursion({})["phases"] == []


# ---------------------------------------------------------------- _record_to_task
def test_record_to_task_gueltig_und_ungueltig():
    assert live_run._record_to_task(
        {"messages": [{"role": "user", "content": " Q "}, {"role": "assistant", "content": " A "}]}
    ) == {"question": "Q", "fact": "A", "correct": "A"}
    assert live_run._record_to_task({"messages": [{"content": "Q"}, {"content": " "}]}) is None  # leere Antwort
    assert live_run._record_to_task({"messages": [{"content": "Q"}]}) is None  # zu wenige Nachrichten
    assert live_run._record_to_task({"kein": "record"}) is None
    assert live_run._record_to_task(None) is None


# ------------------------------------------------------------------- _load_tasks
def _records():
    return [
        {"messages": [{"role": "user", "content": "Q1"}, {"role": "assistant", "content": "A1"}]},
        {"messages": [{"role": "user", "content": "Q2"}, {"role": "assistant", "content": "A2"}]},
        {"messages": [{"role": "user", "content": "Q3"}, {"role": "assistant", "content": ""}]},  # leer -> skip
        {"kein": "record"},
        {"messages": [{"role": "user", "content": "Q4"}, {"role": "assistant", "content": "A4"}]},
    ]


def test_load_tasks_mit_injiziertem_loader():
    tasks = live_run._load_tasks(10, loader=lambda n: _records())
    assert tasks == [
        {"question": "Q1", "fact": "A1", "correct": "A1"},
        {"question": "Q2", "fact": "A2", "correct": "A2"},
        {"question": "Q4", "fact": "A4", "correct": "A4"},
    ]


def test_load_tasks_cap_und_seed_deterministisch():
    assert len(live_run._load_tasks(2, loader=lambda n: _records())) == 2
    a = live_run._load_tasks(3, seed=42, loader=lambda n: _records())
    b = live_run._load_tasks(3, seed=42, loader=lambda n: _records())
    assert a == b
    assert all(t["question"] in {"Q1", "Q2", "Q4"} for t in a)


# --------------------------------------------------------------- _resolve_endpoint
def test_resolve_endpoint_aus_env(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "k")
    monkeypatch.setenv("OPENAI_BASE_URL", "http://x")
    assert live_run._resolve_endpoint(config_path=Path("/gibt-es-nicht.json")) == {
        "api_key": "k",
        "base_url": "http://x",
    }


def test_resolve_endpoint_fehlender_key_klarer_fehler(tmp_path, monkeypatch):
    """Guardrail 7: ohne Key klarer Abbruch – ohne Netz, ohne Fake."""
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_BASE_URL", raising=False)
    with pytest.raises(RuntimeError, match="OPENAI_API_KEY"):
        live_run._resolve_endpoint(config_path=tmp_path / "fehlt.json")


# --------------------------------------------------- _run_task (Verdrahtung, offline)
def test_run_task_verdrahtung_offline(tmp_path, monkeypatch):
    """Beide Runner real verdrahtet, LLM-Stufen offline gestubbt (kein Netz, kein Fake-Lauf)."""
    import fast_write_router
    import lifecycle_runner
    import recursion_runner
    import reflective_agent

    monkeypatch.setattr(fast_write_router, "classify", lambda q, f, c: {"class": "non-write"})
    monkeypatch.setattr(reflective_agent, "parse_transition_delta", lambda text, k: None)  # NOOP
    monkeypatch.setattr(
        live_run,
        "_make_probe",
        lambda task: lambda: {"ok": True, "successes": 1, "failures": 0, "evidence": {"stub": True}},
    )
    monkeypatch.setenv("LIFECYCLE_DRIFT_REFERENCE", str(tmp_path / "drift.json"))

    task = {"question": "Hauptstadt?", "fact": "Zentaria", "correct": "Zentaria"}
    result = live_run._run_task(task, tmp_path / "t0", now=1.0)

    assert result["question"] == "Hauptstadt?"
    assert result["cycle"]["stages"] == list(lifecycle_runner.STAGES)
    assert result["cycle"]["ok"] is True
    assert result["cycle"]["action"] == "none"  # pipeline: non-write -> "none"
    assert result["recursion"]["phases"] == list(recursion_runner.PHASES)
    assert result["recursion"]["ok"] is True
    assert result["recursion"]["observed"] is True  # externes Probe-Signal
    assert result["recursion"]["revised"] is False  # NOOP-Matrix -> keine HMM-Revision


def test_endpoint_from_config_liest_provider(tmp_path):
    cfg = tmp_path / "opencode.json"
    cfg.write_text(
        '{"provider": {"nvidia-llama-nemotron": {"options": {"apiKey": "abc", "baseURL": "http://y"}}}}',
        encoding="utf-8",
    )
    assert live_run._endpoint_from_config(cfg) == {"api_key": "abc", "base_url": "http://y"}
    bad = tmp_path / "kaputt.json"
    bad.write_text("{kaputt", encoding="utf-8")
    assert live_run._endpoint_from_config(bad) == {}
