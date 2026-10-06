"""Skill-Interpreter (data/memory/skill_interpreter.py) — ReAct-Loop + MCP (Guardrail 7)."""

import json
from pathlib import Path

import mandate
import mcp_memory_server
import skill_interpreter as si
import trace_audit
import write_gateway

ROOT = Path(__file__).resolve().parents[1]


def _mandate():
    return mandate.Mandate(
        mandate_id="test",
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


def _ctx(tmp_path):
    return {
        "question": "Wo?",
        "fact": "Kontakt: max@example.com, Version 2.",
        "correct": "Version 2.",
        "classify_fn": lambda q, f, c: {"class": "write-new"},
        "mandate_obj": _mandate(),
        "now": 100.0,
        "structured_dir": tmp_path / "structured",
        "tier3_dir": tmp_path / "tier3",
    }


def _llm(calls):
    it = iter(calls)
    return lambda messages, tools: next(it)


# --- deklarativer Runner (bestehend) ---


def test_parse_skill_act():
    spec = si.parse_skill(ROOT / "skills/act/SKILL.md")
    assert spec["name"] == "act"
    assert len(spec["steps"]) >= 6
    assert "pipeline.py" in spec["processes"]
    assert "memory.write" in spec["mcp_tools"]
    assert any("icml.cc" in s for s in spec["sources"])


def test_parse_skill_minimal(tmp_path):
    p = tmp_path / "minimal" / "SKILL.md"
    p.parent.mkdir(parents=True)
    p.write_text("# Nur Titel\n", encoding="utf-8")
    spec = si.parse_skill(p)
    assert spec["name"] == "minimal" and spec["steps"] == [] and spec["processes"] == []


def test_run_skill_pipeline_executed(tmp_path):
    out = si.run_skill(ROOT / "skills/act/SKILL.md", _ctx(tmp_path))
    assert [t for t in out["trace"] if t["process"] == "pipeline.py"][0]["executed"] is True


def test_run_skill_ohne_executor(tmp_path):
    out = si.run_skill(ROOT / "skills/act/SKILL.md", _ctx(tmp_path), registry={})
    assert all(t["executed"] is False for t in out["trace"])


def test_list_skills():
    assert len(si.list_skills()) >= 14


# --- ReAct-Tool-Calling-Loop ---


def test_agent_tool_und_final(tmp_path):
    ctx = _ctx(tmp_path)
    llm = _llm([{"tool": "pipeline.py", "args": {}, "id": "c1"}, {"final": "fertig"}])
    out = si.run_skill_agent(ROOT / "skills/act/SKILL.md", ctx, llm_fn=llm)
    assert out["stopped"] is True and out["final"] == "fertig"
    tool_steps = [t for t in out["trace"] if t["action"] == "tool"]
    assert tool_steps[0]["tool"] == "pipeline.py" and tool_steps[0]["result"]["ok"] is True


def test_agent_noop_ohne_llm(tmp_path):
    out = si.run_skill_agent(ROOT / "skills/act/SKILL.md", _ctx(tmp_path), llm_fn=_llm([None]))
    assert out["trace"][0]["action"] == "noop" and out["final"] is None


def test_agent_unbekanntes_tool(tmp_path):
    llm = _llm([{"tool": "gibt-es-nicht", "args": {}}])
    out = si.run_skill_agent(ROOT / "skills/act/SKILL.md", _ctx(tmp_path), llm_fn=llm)
    assert out["trace"][0]["action"] == "error"


def test_agent_max_steps(tmp_path):
    def _llm_immer_tool(messages, tools):
        return {"tool": "pipeline.py", "args": {}}

    out = si.run_skill_agent(ROOT / "skills/act/SKILL.md", _ctx(tmp_path), llm_fn=_llm_immer_tool, max_steps=2)
    assert len(out["trace"]) == 2 and out["stopped"] is False


def test_agent_memory_write_in_process_mcp(tmp_path, monkeypatch):
    monkeypatch.setattr(mcp_memory_server, "SCOPES", {"tier2": tmp_path / "mcp-t2", "tier3": tmp_path / "mcp"})
    llm = _llm(
        [
            {"tool": "memory.write", "args": {"scope": "tier3", "key": "k.md", "content": "hi", "trust": "green"}},
            {"final": "ok"},
        ]
    )
    out = si.run_skill_agent(ROOT / "skills/act/SKILL.md", _ctx(tmp_path), llm_fn=llm)
    step = [t for t in out["trace"] if t["action"] == "tool"][0]
    assert step["result"]["via"] == "mcp" and step["result"]["result"]["ok"] is True
    assert (tmp_path / "mcp" / "k.md").exists()


def test_memory_write_fallback(tmp_path, monkeypatch):
    def _boom():
        raise RuntimeError("MCP down")

    monkeypatch.setattr(mcp_memory_server, "build_server", _boom)
    out = si._run_memory_write(_ctx(tmp_path), scope="tier3", key="f.md", content="x")
    assert out["via"] == "local-fallback" and (tmp_path / "tier3" / "f.md").exists()


def test_n5_echter_ausfall_fallback_schreibt_pii_frei(tmp_path, monkeypatch):
    """N5 §9.2a/§11: echter Transport-Ausfall -> Fallback, aber PII wird entfernt."""
    monkeypatch.setattr(mcp_memory_server, "build_server", lambda: (_ for _ in ()).throw(RuntimeError("down")))
    r = si._run_memory_write(_ctx(tmp_path), scope="tier3", key="pii.md", content="Mail max@example.com", trust="green")
    assert r["ok"] is True and r["via"] == "local-fallback"
    text = (tmp_path / "tier3" / "pii.md").read_text(encoding="utf-8")
    assert "max@example.com" not in text  # §9.2a PII-Filter auch im Fallback


def test_n5_fallback_rejectet_red(tmp_path, monkeypatch):
    """N5 §9.2c: Fallback persistiert KEIN trust=red."""
    monkeypatch.setattr(mcp_memory_server, "build_server", lambda: (_ for _ in ()).throw(RuntimeError("down")))
    r = si._run_memory_write(_ctx(tmp_path), scope="tier3", key="red.md", content="RED", trust="red")
    assert r["ok"] is False and r.get("status") == "rejected"
    assert not (tmp_path / "tier3" / "red.md").exists()


def test_n5_fallback_blockiert_path_traversal(tmp_path, monkeypatch):
    """N5 §11: Fallback darf nicht aus tier3 heraus schreiben (`../`)."""
    monkeypatch.setattr(mcp_memory_server, "build_server", lambda: (_ for _ in ()).throw(RuntimeError("down")))
    r = si._run_memory_write(_ctx(tmp_path), scope="tier3", key="../ESCAPED.md", content="x")
    assert r["ok"] is False
    assert not (tmp_path / "ESCAPED.md").exists()
    assert not (tmp_path / "tier3" / "ESCAPED.md").exists()


def test_n5_fallback_ungueltige_trust_farbe(tmp_path, monkeypatch):
    """N5: unbekannte Trust-Farbe -> Fallback rejected."""
    monkeypatch.setattr(mcp_memory_server, "build_server", lambda: (_ for _ in ()).throw(RuntimeError("down")))
    r = si._run_memory_write(_ctx(tmp_path), scope="tier3", key="x.md", content="x", trust="gelb")
    assert r["ok"] is False and "ungültige Trust-Farbe" in r["reason"]
    assert not (tmp_path / "tier3" / "x.md").exists()


def test_n5_validierungsfehler_kein_fallback(tmp_path):
    """N5: Validierungs-/Scope-Fehler (ValueError aus _path) -> Fehler, KEIN Fallback."""
    r = si._run_memory_write(_ctx(tmp_path), scope="bogus-scope", key="x.md", content="x", trust="green")
    assert r["ok"] is False and r.get("via") != "local-fallback"
    assert not (tmp_path / "tier3" / "x.md").exists()


def test_n5_mcp_sdk_fehlt_fallback(tmp_path, monkeypatch):
    """N5 §11: echter Ausfall (SDK nicht importierbar) -> Fallback."""
    import sys

    monkeypatch.setitem(sys.modules, "mcp_memory_server", None)  # `import ...` -> ImportError
    r = si._run_memory_write(_ctx(tmp_path), scope="tier3", key="sdk.md", content="x", trust="green")
    assert r["ok"] is True and r["via"] == "local-fallback"
    assert (tmp_path / "tier3" / "sdk.md").exists()


def test_parse_mcp_zweige():
    class _B:
        text = "kein json"

    class _N:
        text = None

    assert si._parse_mcp([_B()]) == {"text": "kein json"}
    assert si._parse_mcp([_N()]) == {"ok": False, "reason": "leeres MCP-Ergebnis"}
    assert si._parse_mcp([]) == {"ok": False, "reason": "leeres MCP-Ergebnis"}


def test_tool_specs_default_zweig():
    specs = si._tool_specs({"unbekannt.py": lambda *a, **k: None})
    assert specs[0]["function"]["name"] == "unbekannt_py"  # Punkt -> _ (Function-Calling)


def test_agent_sanitized_tool_name(tmp_path):
    llm = _llm([{"tool": "pipeline_py", "args": {}, "id": "c1"}, {"final": "ok"}])
    out = si.run_skill_agent(ROOT / "skills/act/SKILL.md", _ctx(tmp_path), llm_fn=llm)
    assert [t for t in out["trace"] if t["action"] == "tool"][0]["tool"] == "pipeline.py"


# --- K7/B3: fachliches reject NIE über den lokalen Fallback ---


def _boom_servers(**msg):
    def _raise():
        raise msg["exc"]

    return _raise


def test_k7_domain_reject_kein_fallback(tmp_path, monkeypatch):
    """K7/B3: MCP-`rejected` (red) → via=mcp, KEIN Fallback-Write."""
    monkeypatch.setattr(mcp_memory_server, "SCOPES", {"tier2": tmp_path / "t2", "tier3": tmp_path / "t3"})
    r = si._run_memory_write(_ctx(tmp_path), scope="tier3", key="red.md", content="x", trust="red")
    assert r["ok"] is False and r["via"] == "mcp" and r["status"] == "rejected"
    assert not (tmp_path / "tier3" / "red.md").exists()


def test_k7_domain_rejection_exception_kein_fallback(tmp_path, monkeypatch):
    """K7/B3: fachliche Ablehnung als DomainRejection → via=mcp, KEIN Fallback."""
    monkeypatch.setattr(
        mcp_memory_server, "build_server", _boom_servers(exc=write_gateway.DomainRejection("fachlich abgelehnt"))
    )
    r = si._run_memory_write(_ctx(tmp_path), scope="tier3", key="d.md", content="x", trust="green")
    assert r["ok"] is False and r["via"] == "mcp" and r["status"] == "rejected"
    assert not (tmp_path / "tier3" / "d.md").exists()


def test_k7_domain_rejection_cause_kein_fallback(tmp_path, monkeypatch):
    """K7/B3: DomainRejection als __cause__ (FastMCP-Wrapping) → KEIN Fallback."""

    def _raise():
        raise RuntimeError("wrapped") from write_gateway.DomainRejection("fachlich abgelehnt")

    monkeypatch.setattr(mcp_memory_server, "build_server", _raise)
    r = si._run_memory_write(_ctx(tmp_path), scope="tier3", key="d2.md", content="x", trust="green")
    assert r["ok"] is False and r["via"] == "mcp" and r["status"] == "rejected"
    assert not (tmp_path / "tier3" / "d2.md").exists()


def test_k7_fallback_blue_geschuetzt(tmp_path, monkeypatch):
    """K7/B3 §9.2c: Fallback darf bestätigtes `blue` nicht durch `green` überschreiben."""
    tier3 = tmp_path / "tier3"
    tier3.mkdir()
    (tier3 / "b.md").write_text("ALT-BLUE", encoding="utf-8")
    db = tmp_path / "mcp-trust.json"
    db.write_text(json.dumps({"b.md": "blue"}), encoding="utf-8")
    monkeypatch.setattr(mcp_memory_server, "_trust_db_path", lambda: db)
    monkeypatch.setattr(mcp_memory_server, "build_server", _boom_servers(exc=RuntimeError("MCP down")))
    r = si._run_memory_write(_ctx(tmp_path), scope="tier3", key="b.md", content="NEU-GREEN", trust="green")
    assert r["ok"] is False and r.get("status") == "rejected"
    assert (tier3 / "b.md").read_text(encoding="utf-8") == "ALT-BLUE"


def test_k7_fallback_existing_unknown_trust_fail_closed(tmp_path, monkeypatch):
    """K7/B3 §9.2c: existierende Datei + unbekannter Trust → fail-closed (kein Write)."""
    tier3 = tmp_path / "tier3"
    tier3.mkdir()
    (tier3 / "u.md").write_text("ALT", encoding="utf-8")
    monkeypatch.setattr(mcp_memory_server, "_trust_db_path", lambda: tmp_path / "leer.json")
    monkeypatch.setattr(mcp_memory_server, "build_server", _boom_servers(exc=RuntimeError("MCP down")))
    r = si._run_memory_write(_ctx(tmp_path), scope="tier3", key="u.md", content="NEU", trust="green")
    assert r["ok"] is False and r.get("status") == "rejected"
    assert (tier3 / "u.md").read_text(encoding="utf-8") == "ALT"


def test_k7_fallback_ohne_trust_db_existing_fail_closed(tmp_path, monkeypatch):
    """K7/B3 §9.2c: keine Trust-Metadaten (tier2 fehlt) + existierende Datei → fail-closed."""
    tier3 = tmp_path / "tier3"
    tier3.mkdir()
    (tier3 / "n.md").write_text("ALT", encoding="utf-8")
    monkeypatch.setattr(mcp_memory_server, "_trust_db_path", lambda: None)
    monkeypatch.setattr(mcp_memory_server, "build_server", _boom_servers(exc=RuntimeError("MCP down")))
    r = si._run_memory_write(_ctx(tmp_path), scope="tier3", key="n.md", content="NEU", trust="green")
    assert r["ok"] is False and r.get("status") == "rejected"
    assert (tier3 / "n.md").read_text(encoding="utf-8") == "ALT"


# --- K7: Trace + Audit (Spans ≠ Audit) ---


def test_result_field_zweige():
    assert si._result_field({"ok": True}, "ok") is True
    assert si._result_field("kein-dict", "ok") is None


def test_run_skill_agent_mit_recorder(tmp_path):
    """K7: Execution-Graph-Spans + dauerhaftes Auditprotokoll entstehen real."""
    rec = trace_audit.Recorder(spans_path=tmp_path / "spans.jsonl", audit_path=tmp_path / "audit.jsonl")
    llm = _llm([{"tool": "pipeline.py", "args": {}, "id": "c1"}, {"final": "ok"}])
    si.run_skill_agent(ROOT / "skills/act/SKILL.md", _ctx(tmp_path), llm_fn=llm, recorder=rec)
    rec.flush()

    events = [json.loads(line)["event"] for line in (tmp_path / "audit.jsonl").read_text(encoding="utf-8").splitlines()]
    assert "skill.tool" in events and "skill.finish" in events  # (c) Audit-Eintrag
    names = [json.loads(line)["name"] for line in (tmp_path / "spans.jsonl").read_text(encoding="utf-8").splitlines()]
    assert {"skill.run", "skill.tool"} <= set(names)  # Execution-Graph
    rec.shutdown()
