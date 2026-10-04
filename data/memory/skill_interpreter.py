#!/usr/bin/env python3
"""Skill-Interpreter: (a) deklarativer Prozess-Runner, (b) LLM-Tool-Calling-Loop (ReAct).

Quellen (verifiziert):
  - **Agent Skills** (Anthropic/agentskills.io): SKILL.md = LLM-Instruktion
    (progressive disclosure); Ausführung via Tools, nicht via Eigen-Parser.
    https://docs.anthropic.com/en/docs/agents-and-tools/agent-skills/overview
  - **ReAct** (Yao et al. 2023): Thought → Action → Observation. https://arxiv.org/abs/2210.03629
  - **MCP-Spec + Python-SDK**: Client ruft `tools/call`; stdio/in-process.
    https://modelcontextprotocol.io/specification · https://py.sdk.modelcontextprotocol.io/
  - **LLMCompiler** (Kim et al., ICML 2024): Planner→Executor. https://arxiv.org/abs/2312.04511

Lab-Prinzip §6: keine Erfindung — jede Lösung = verifizierte Spec. **§11:** MCP ist optional
über der lokalen Memory (Fallback bei Ausfall). **Guardrail 7:** echte LLM-/Tool-Ausführung;
ohne Key/Endpoint → **NOOP** (kein Fake).

`run_skill`       — führt die in `## Prozesse (Aufrufe)` deklarierten Prozesse aus (deterministisch).
`run_skill_agent` — ReAct-Loop: das LLM liest die `## Ablauf`-Schritte und ruft die Tools auf.
"""

from __future__ import annotations

import asyncio
import json
import os
import re
from pathlib import Path

import pipeline
import procedural_memory


def _section(text: str, keyword: str) -> str:
    """Zeilen unter einer `## <keyword>`-Überschrift (bis zur nächsten `## `)."""
    out, on = [], False
    for line in text.splitlines():
        if line.startswith("## "):
            on = keyword.lower() in line.lower()
            continue
        if on:
            out.append(line)
    return "\n".join(out)


def _frontmatter(text: str) -> str:
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    return m.group(1) if m else ""


def parse_skill(path: Path) -> dict:
    """SKILL.md → {name, description, steps, processes, mcp_tools, guardrails, sources}."""
    path = Path(path)
    text = path.read_text(encoding="utf-8")
    fm = _frontmatter(text)
    name_m = re.search(r"^name:\s*(.+)$", fm, re.M)
    desc_m = re.search(r"^description:\s*(.+)$", fm, re.M)
    steps = [
        re.sub(r"\*\*", "", m.group(1)).strip()
        for m in re.finditer(r"^\s*\d+\.\s+(.*)$", _section(text, "ablauf"), re.M)
    ]
    proc_section = _section(text, "prozesse")
    processes = [m.group(1) for m in re.finditer(r"^-\s+`([^`]+)`", proc_section, re.M)]
    mcp_tools = []
    for line in proc_section.splitlines():
        if "MCP-Tools" in line:
            mcp_tools += re.findall(r"`([^`]+)`", line)
    guardrails = [
        re.sub(r"\*\*", "", m.group(1)).strip()
        for m in re.finditer(r"^\s*\d+\.\s+(.*)$", _section(text, "guardrails"), re.M)
    ]
    sources = re.findall(r"https?://\S+", _section(text, "quellen"))
    return {
        "name": name_m.group(1).strip() if name_m else path.parent.name,
        "description": desc_m.group(1).strip() if desc_m else "",
        "steps": steps,
        "processes": processes,
        "mcp_tools": mcp_tools,
        "guardrails": guardrails,
        "sources": sources,
    }


def list_skills() -> list[Path]:
    """Aktive Skills (über `procedural_memory.active_skills`, Versionen ausgeschlossen)."""
    return procedural_memory.active_skills()


def _run_pipeline(ctx: dict, **_ignored) -> dict:
    """Echter Executor für den deklarierten Prozess `pipeline.py` (Stufe 7)."""
    return pipeline.route_and_store(
        question=ctx["question"],
        fact=ctx["fact"],
        correct=ctx["correct"],
        classify_fn=ctx["classify_fn"],
        mandate_obj=ctx["mandate_obj"],
        now=ctx["now"],
        structured_dir=ctx["structured_dir"],
        tier3_dir=ctx["tier3_dir"],
    )


def _parse_mcp(result) -> dict:
    """FastMCP-`call_tool`-Ergebnis (Content-Blöcke) → Dict."""
    for block in result or []:
        text = getattr(block, "text", None)
        if text:
            try:
                return json.loads(text)
            except json.JSONDecodeError:
                return {"text": text}
    return {"ok": False, "reason": "leeres MCP-Ergebnis"}


def _run_memory_write(ctx: dict, scope: str = "tier3", key: str = "", content: str = "", trust: str = "green") -> dict:
    """Echter Executor für das MCP-Tool `memory.write` (in-process via FastMCP, §11).

    Offizieller MCP-Pfad: `FastMCP.call_tool` (in-process, kein Subprozess).
    **§11-Fallback:** schlägt MCP fehl → lokale Memory (kein Datenverlust).
    """
    key = key or (re.sub(r"[^a-z0-9]+", "-", (ctx["question"] or "").lower()).strip("-")[:60] + ".md")
    content = content or ctx["fact"]
    try:
        import mcp_memory_server

        server = mcp_memory_server.build_server()
        result = asyncio.run(
            server.call_tool("memory.write", {"scope": scope, "key": key, "content": content, "trust": trust})
        )
        return {"via": "mcp", "result": _parse_mcp(result)}
    except Exception as exc:  # noqa: BLE001 - §11-Fallback
        fallback_dir = Path(ctx["tier3_dir"])
        fallback_dir.mkdir(parents=True, exist_ok=True)
        (fallback_dir / key).write_text(content, encoding="utf-8")
        return {"via": "local-fallback", "reason": str(exc)[:80], "written": str(fallback_dir / key)}


# Registrierte Executoren (Tool-/Prozessname -> echte Funktion).
DEFAULT_REGISTRY = {"pipeline.py": _run_pipeline, "memory.write": _run_memory_write}

# Tool-Beschreibungen (Auftrag) für das Function-Calling-Schema.
TOOL_SPECS = {
    "pipeline.py": {
        "description": "Führt die Element-Pipeline aus (Mandat→FWR→Trust→Write, Stufe 7).",
        "parameters": {"type": "object", "properties": {}, "required": []},
    },
    "memory.write": {
        "description": "Schreibt einen Fakt in einen Memory-Scope (Tri-Color-Trust).",
        "parameters": {
            "type": "object",
            "properties": {
                "scope": {"type": "string"},
                "key": {"type": "string"},
                "content": {"type": "string"},
                "trust": {"type": "string"},
            },
            "required": ["scope", "key", "content"],
        },
    },
}


def _fn_name(key: str) -> str:
    """Function-Calling-Name (nur a-z A-Z 0-9 _ - erlaubt; `pipeline.py` -> `pipeline_py`)."""
    return re.sub(r"[^A-Za-z0-9_-]", "_", key)


def _tool_specs(registry: dict) -> list:
    out = []
    for name in registry:
        spec = TOOL_SPECS.get(
            name, {"description": f"Prozess {name}", "parameters": {"type": "object", "properties": {}}}
        )
        out.append({"type": "function", "function": {"name": _fn_name(name), **spec}})
    return out


def run_skill(skill_path: Path, ctx: dict, registry: dict | None = None) -> dict:
    """Führt die im Skill deklarierten Prozesse aus (nur mit registriertem Executor)."""
    spec = parse_skill(skill_path)
    reg = DEFAULT_REGISTRY if registry is None else registry
    trace = []
    for proc in spec["processes"]:
        fn = reg.get(proc)
        if fn is None:
            trace.append({"process": proc, "executed": False, "reason": "kein Executor (Doku)"})
        else:
            trace.append({"process": proc, "executed": True, "result": fn(ctx)})
    return {"skill": spec["name"], "steps": spec["steps"], "processes": spec["processes"], "trace": trace}


def _task_prompt(spec: dict) -> str:
    steps = "\n".join(f"{i}. {s}" for i, s in enumerate(spec["steps"], 1))
    return f"Skill: {spec['name']} — {spec['description']}\n\nAblauf:\n{steps}\n\nFühre die passenden Tools aus."


_SYSTEM = "Du bist ein Tool-Calling-Agent. Lies den Skill und rufe die passenden Tools auf. Antworte am Ende final."


def _default_llm(messages: list, tools: list):  # pragma: no cover - Netzbetrieb (Guardrail 7)
    """Echtes LLM mit Function-Calling; ohne Key/Endpoint → None (NOOP, kein Fake)."""
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        return None
    from openai import OpenAI

    client = OpenAI(api_key=key, base_url=os.environ.get("OPENAI_BASE_URL"))
    resp = client.chat.completions.create(
        model=os.environ.get("HELA_MODEL", "nvidia/nemotron-3-ultra-550b-a55b"),
        messages=messages,
        tools=tools,
        tool_choice="auto",
        temperature=0.0,
    )
    msg = resp.choices[0].message
    if msg.tool_calls:
        tc = msg.tool_calls[0]
        try:
            args = json.loads(tc.function.arguments or "{}")
        except json.JSONDecodeError:
            args = {}
        return {"tool": tc.function.name, "args": args, "id": tc.id}
    return {"final": msg.content or ""}


def run_skill_agent(
    skill_path: Path, ctx: dict, *, llm_fn=None, registry: dict | None = None, max_steps: int = 8
) -> dict:
    """ReAct-Loop (Agent Skills/ReAct): LLM liest `## Ablauf` und ruft registrierte Tools auf."""
    spec = parse_skill(skill_path)
    reg = DEFAULT_REGISTRY if registry is None else registry
    llm = llm_fn if llm_fn is not None else _default_llm
    messages = [{"role": "system", "content": _SYSTEM}, {"role": "user", "content": _task_prompt(spec)}]
    tools = _tool_specs(reg)
    name_map = {_fn_name(k): k for k in reg}
    trace, final, stopped = [], None, False
    for step in range(1, max_steps + 1):
        call = llm(messages, tools)
        if call is None:
            trace.append({"step": step, "action": "noop", "reason": "kein LLM/Endpoint"})
            stopped = True
            break
        if "final" in call:
            final = call["final"]
            trace.append({"step": step, "action": "final", "content": final})
            stopped = True
            break
        name, args = call.get("tool"), call.get("args") or {}
        name = name_map.get(name, name)
        fn = reg.get(name)
        if fn is None:
            trace.append({"step": step, "action": "error", "tool": name, "reason": "unbekanntes Tool"})
            stopped = True
            break
        result = fn(ctx, **args)
        trace.append({"step": step, "action": "tool", "tool": name, "result": result})
        call_id = call.get("id") or f"call-{step}"
        messages.append(
            {
                "role": "assistant",
                "content": None,
                "tool_calls": [
                    {"id": call_id, "type": "function", "function": {"name": name, "arguments": json.dumps(args)}}
                ],
            }
        )
        messages.append({"role": "tool", "tool_call_id": call_id, "content": json.dumps(result, ensure_ascii=False)})
    return {"skill": spec["name"], "steps": spec["steps"], "trace": trace, "final": final, "stopped": stopped}


if __name__ == "__main__":  # pragma: no cover - CLI
    import json as _json

    import mandate

    ctx = {
        "question": "Beispiel?",
        "fact": "Kontakt: max@example.com, Version 2.",
        "correct": "Version 2.",
        "classify_fn": lambda q, f, c: {"class": "write-new"},
        "mandate_obj": mandate.Mandate(
            mandate_id="skill-interpreter",
            principal="Batnini",
            agent="knowledge-agent",
            actions=frozenset({"write:memory"}),
            resources=frozenset({"data/memory"}),
            amount_limit=1.0,
            max_uses=10_000,
            valid_from=0.0,
            valid_until=1e12,
            approval_threshold=0.5,
        ),
        "now": 100.0,
        "structured_dir": "/tmp/skill-interpreter/structured",
        "tier3_dir": "/tmp/skill-interpreter/tier3",
    }
    out = run_skill_agent(Path("skills/act/SKILL.md"), ctx)
    print(
        _json.dumps(
            {"skill": out["skill"], "steps": len(out["steps"]), "stopped": out["stopped"], "trace": out["trace"]},
            ensure_ascii=False,
            indent=2,
        )
    )
