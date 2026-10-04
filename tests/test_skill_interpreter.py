"""Skill-Interpreter (data/memory/skill_interpreter.py) — ReAct-Loop + MCP (Guardrail 7)."""

from pathlib import Path

import mandate
import mcp_memory_server
import skill_interpreter as si

ROOT = Path("/home/opc/knowledge-agent")


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
    monkeypatch.setattr(mcp_memory_server, "SCOPES", {"tier3": tmp_path / "mcp"})
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
