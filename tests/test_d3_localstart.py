"""D3 (Audit d25486c, P2): lokaler Live-Start nutzt EIN vorhandenes Modell.

Offline (Guardrail 7: **kein** Netz/Endpoint): geprüft werden `_apply_hela_model_default`
und die neue CLI `--require-success` mit gestubbten `_resolve_endpoint`/`_load_tasks`/
`_run_task` (die echten Runner-Aufrufe sind nicht Teil dieses Tests).

Soll:
  1. `HELA_MODEL` wird nur gesetzt, wenn es fehlt (aus `FWR_LARGE_MODEL` →
     `FWR_SMALL_MODEL` → `DEFAULT_MODEL`); ein vorhandener Wert bleibt unverändert.
  2. `--require-success`: ohne erfolgreichen Write **und** ohne positives Oracle ⇒
     Exit 1; mit ≥ 1 Erfolg ⇒ Exit 0; ohne Flag ⇒ Exit 0 (exakt altes Verhalten).
"""

import importlib.util
import os
from pathlib import Path

_SPEC = importlib.util.spec_from_file_location(
    "live_run",
    Path(__file__).resolve().parents[1] / "scripts" / "live_run.py",
)
live_run = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(live_run)


# --------------------------------------------------- HELA_MODEL-Default (D3.1)
def test_hela_default_aus_fwr_large(monkeypatch):
    """Fehlendes `HELA_MODEL` wird aus `FWR_LARGE_MODEL` abgeleitet (lokal)."""
    monkeypatch.delenv("HELA_MODEL", raising=False)
    monkeypatch.setenv("FWR_LARGE_MODEL", "qwen-local")
    monkeypatch.delenv("FWR_SMALL_MODEL", raising=False)
    assert live_run._apply_hela_model_default() == "qwen-local"
    assert os.environ["HELA_MODEL"] == "qwen-local"


def test_hela_default_aus_fwr_small(monkeypatch):
    """Ohne `FWR_LARGE_MODEL` greift `FWR_SMALL_MODEL`."""
    monkeypatch.delenv("HELA_MODEL", raising=False)
    monkeypatch.delenv("FWR_LARGE_MODEL", raising=False)
    monkeypatch.setenv("FWR_SMALL_MODEL", "klein-lokal")
    assert live_run._apply_hela_model_default() == "klein-lokal"


def test_hela_default_fallback_default_model(monkeypatch):
    """Ohne FWR-Modelle fällt `HELA_MODEL` auf `DEFAULT_MODEL` zurück."""
    monkeypatch.delenv("HELA_MODEL", raising=False)
    monkeypatch.delenv("FWR_LARGE_MODEL", raising=False)
    monkeypatch.delenv("FWR_SMALL_MODEL", raising=False)
    assert live_run._apply_hela_model_default() == live_run.DEFAULT_MODEL


def test_hela_vorhandener_wert_bleibt(monkeypatch):
    """Ein bereits gesetztes `HELA_MODEL` wird NICHT überschrieben."""
    monkeypatch.setenv("HELA_MODEL", "bestehend")
    monkeypatch.setenv("FWR_LARGE_MODEL", "qwen-local")
    assert live_run._apply_hela_model_default() == "bestehend"
    assert os.environ["HELA_MODEL"] == "bestehend"


# --------------------------------------------------------- _has_success (D3.2)
def test_has_success_bei_write():
    assert live_run._has_success({"cycle": {"ok": True, "action": "write-update"}}) is True
    assert live_run._has_success({"recursion": {"ok": True, "action": "write-new"}}) is True


def test_has_success_bei_positivem_oracle():
    assert live_run._has_success({"recursion": {"ok": False, "observed": True}}) is True


def test_has_success_ohne_write_und_ohne_oracle():
    run = {"cycle": {"ok": True, "action": "none"}, "recursion": {"ok": False, "observed": False}}
    assert live_run._has_success(run) is False
    assert live_run._has_success({}) is False


# ----------------------------------------------------- CLI --require-success (D3.2)
def _stub_main(monkeypatch, tmp_path, argv, *, run):
    monkeypatch.setattr(live_run, "_resolve_endpoint", lambda: {"api_key": "k", "base_url": "http://x"})
    monkeypatch.setattr(live_run, "_apply_hela_model_default", lambda *a, **k: "qwen-local")
    monkeypatch.setattr(
        live_run,
        "_load_tasks",
        lambda n, seed=None: [{"question": "Q", "fact": "A", "correct": "A"}],
    )
    monkeypatch.setattr(live_run, "_run_task", lambda task, workdir, now, **kw: run)
    return live_run.main([*argv, "--tasks", "1", "--out", str(tmp_path / "out.json")])


def test_require_success_ohne_erfolg_exit1(tmp_path, monkeypatch):
    """Kein Write, kein Oracle ⇒ mit `--require-success` Exit 1 (nicht still 0)."""
    assert _stub_main(monkeypatch, tmp_path, ["--require-success"], run={"question": "Q"}) == 1


def test_require_success_mit_write_exit0(tmp_path, monkeypatch):
    """≥ 1 erfolgreicher Write ⇒ mit `--require-success` Exit 0."""
    run = {"question": "Q", "cycle": {"ok": True, "action": "write-update"}}
    assert _stub_main(monkeypatch, tmp_path, ["--require-success"], run=run) == 0


def test_require_success_mit_positivem_oracle_exit0(tmp_path, monkeypatch):
    """≥ 1 positives Oracle ⇒ mit `--require-success` Exit 0."""
    run = {"question": "Q", "recursion": {"ok": False, "observed": True}}
    assert _stub_main(monkeypatch, tmp_path, ["--require-success"], run=run) == 0


def test_ohne_flag_exit0(tmp_path, monkeypatch):
    """Ohne Flag exakt altes Verhalten: Exit 0 auch ohne Erfolg."""
    assert _stub_main(monkeypatch, tmp_path, [], run={"question": "Q"}) == 0


def test_main_setzt_hela_model(monkeypatch, tmp_path):
    """Die Verdrahtung: `main` setzt den `HELA_MODEL`-Default (echte Funktion)."""
    monkeypatch.delenv("HELA_MODEL", raising=False)
    monkeypatch.setenv("FWR_LARGE_MODEL", "qwen-local")
    monkeypatch.setattr(live_run, "_resolve_endpoint", lambda: {"api_key": "k", "base_url": "http://x"})
    monkeypatch.setattr(
        live_run,
        "_load_tasks",
        lambda n, seed=None: [{"question": "Q", "fact": "A", "correct": "A"}],
    )
    monkeypatch.setattr(live_run, "_run_task", lambda task, workdir, now, **kw: {"recursion": {"observed": True}})
    assert live_run.main(["--tasks", "1", "--out", str(tmp_path / "out.json")]) == 0
    assert os.environ["HELA_MODEL"] == "qwen-local"
