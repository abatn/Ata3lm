"""Freigabe-Erfolgspfad (Rekursion 094): §9.3-Zwei-Personen-Freigabe im Live-Driver.

Offline (Guardrail 7: kein Netz, kein Endpoint): die `run_recursion`-Freigabe wird mit
einem Verhaltens-Stub des Routers geprüft (`write-new` + Gate `ask`); `live_run` mit
gestubbten `_resolve_endpoint`/`_load_tasks`/`_run_task` (die Runner-Aufrufe sind die
echten – nur die LLM-nahen Stufen sind ersetzt).

Soll (§9/§9.3): `write-new`/`write-update` (Router-Gate `ask`) schreiben **nur** mit
`self_update=True` **und** ≥ 2 distinkten Personen; sonst bleibt das Gate `ask`
(kein Write). Default unverändert.
"""

import importlib.util
from pathlib import Path

import mandate
import recursion_runner as rr

_SPEC = importlib.util.spec_from_file_location(
    "live_run",
    Path(__file__).resolve().parents[1] / "scripts" / "live_run.py",
)
live_run = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(live_run)


def _mandate():
    return mandate.Mandate(
        mandate_id="freigabe-test",
        principal="Batnini",
        agent="knowledge-agent",
        actions=frozenset({"write:memory"}),
        resources=frozenset({"data/memory"}),
        amount_limit=1.0,
        max_uses=100,
        valid_from=0.0,
        valid_until=1e12,
        approval_threshold=0.5,
    )


def _run(tmp_path, **kw):
    # Router wie der echte FWR für `write-new`: Klasse + Gate `ask` (§10.4).
    return rr.run_recursion(
        "Wo?",
        "Kontakt: max@example.com, Version 2.",
        "Version 2.",
        classify_fn=lambda q, f, c: {"class": "write-new", "gate": "ask"},
        mandate_obj=_mandate(),
        structured_dir=tmp_path / "structured",
        tier3_dir=tmp_path / "tier3",
        **kw,
    )


# --------------------------------------------------- run_recursion (Akt / §9.3)
def test_zwei_personen_freigabe_erlaubt_write(tmp_path):
    """self_update + 2 distinkte Personen ⇒ Akt gate=allow/ok=True (Write real)."""
    out = _run(tmp_path, self_update=True, approvers=["Batnini", "Taoufik"])
    akt = out["results"]["Akt"]
    assert akt["ok"] is True
    assert akt["gate"] == "allow"
    assert akt["action"] == "write-new"
    assert (tmp_path / "structured" / "wo.md").exists()  # §10.7: structured geschrieben


def test_ohne_freigabe_kein_write_ask(tmp_path):
    """Default (self_update=False, approvers=None) ⇒ Akt ask, kein Write."""
    out = _run(tmp_path)
    akt = out["results"]["Akt"]
    assert akt["ok"] is False
    assert akt["gate"] == "ask"
    assert not (tmp_path / "structured" / "wo.md").exists()


def test_ein_approver_keine_freigabe(tmp_path):
    """self_update, aber nur 1 Person ⇒ §9.3 nicht erfüllt ⇒ ask, kein Write."""
    out = _run(tmp_path, self_update=True, approvers=["Batnini"])
    akt = out["results"]["Akt"]
    assert akt["ok"] is False
    assert akt["gate"] == "ask"
    assert not (tmp_path / "structured" / "wo.md").exists()


def test_zwei_gleiche_namen_keine_freigabe(tmp_path):
    """§9.3: zwei DISTINKTE Personen nötig – derselbe Name zweimal zählt nicht."""
    out = _run(tmp_path, self_update=True, approvers=["Batnini", "Batnini"])
    akt = out["results"]["Akt"]
    assert akt["ok"] is False and akt["gate"] == "ask"
    assert not (tmp_path / "structured" / "wo.md").exists()


# ------------------------------------------------------- live_run (CLI / §9.3)
def test_resolve_approvers_distinkt_und_schwelle():
    assert live_run._resolve_approvers(None) == (False, [])
    assert live_run._resolve_approvers(["Batnini"]) == (False, ["Batnini"])
    assert live_run._resolve_approvers(["Batnini", "Taoufik"]) == (True, ["Batnini", "Taoufik"])
    assert live_run._resolve_approvers(["Batnini", "Batnini"]) == (False, ["Batnini"])
    assert live_run._resolve_approvers([" ", ""]) == (False, [])


def _stub_main(monkeypatch, tmp_path, argv):
    captured = {}
    monkeypatch.setattr(live_run, "_resolve_endpoint", lambda: {"api_key": "k", "base_url": "http://x"})
    monkeypatch.setattr(
        live_run,
        "_load_tasks",
        lambda n, seed=None: [{"question": "Q", "fact": "A", "correct": "A"}],
    )

    def fake_run_task(task, workdir, now, self_update=False, approvers=None):
        captured["self_update"] = self_update
        captured["approvers"] = approvers
        return {"question": task["question"]}

    monkeypatch.setattr(live_run, "_run_task", fake_run_task)
    rc = live_run.main([*argv, "--tasks", "1", "--out", str(tmp_path / "out.json")])
    return rc, captured


def test_cli_zwei_approver_aktiviert_self_update(tmp_path, monkeypatch):
    rc, captured = _stub_main(monkeypatch, tmp_path, ["--approver", "Batnini", "--approver", "Taoufik"])
    assert rc == 0
    assert captured["self_update"] is True
    assert captured["approvers"] == ["Batnini", "Taoufik"]


def test_cli_ohne_approver_bleibt_ask(tmp_path, monkeypatch):
    rc, captured = _stub_main(monkeypatch, tmp_path, [])
    assert rc == 0
    assert captured["self_update"] is False
    assert not captured["approvers"]


def test_cli_ein_approver_bleibt_ask(tmp_path, monkeypatch):
    rc, captured = _stub_main(monkeypatch, tmp_path, ["--approver", "Batnini"])
    assert rc == 0
    assert captured["self_update"] is False
    assert captured["approvers"] == ["Batnini"]
