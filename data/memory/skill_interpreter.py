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

import bias_monitor
import evaluator_version
import fast_write_router
import gate_labels
import ingestion_hook
import jsonschema
import mandate
import pipeline
import procedural_memory
import reflective_agent
import shared_memory
import trace_audit
import trust
import write_gateway


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
    process_m = re.search(r"^process:\s*(.+)$", fm, re.M)
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
        "process": process_m.group(1).strip() if process_m else None,
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


def _mandate_write_denied(ctx: dict) -> str | None:
    """R02 §9: Das Kontext-Mandat muss `write:memory` erlauben – sonst fail-closed.

    Das Skill-Mandat wird hier **wirksam** (zuvor ignorierte der Executor es und
    der MCP-Write nutzte ein Default-Schreibmandat). Ohne Mandat oder bei einem
    Read-only-Mandat (`read:memory`) erfolgt KEIN Write.
    """
    m = ctx.get("mandate_obj")
    if m is None:
        return "kein Mandat im Kontext → fail-closed (§9)"
    dec = mandate.assess(m, action="write:memory", resource="data/memory", amount=0.0, now=float(ctx.get("now", 0.0)))
    if not gate_labels.is_allow(dec["gate"]):
        return f"Mandat verweigert Write ({dec['gate']}): {dec['reason']} (§9)"
    return None


def _fallback_domain_violation(ctx: dict, key: str, trust_color: str) -> str | None:
    """K7/B3 §9.2c/§9.3: fail-closed im Fallback.

    Ein *fachliches* `rejected` (blue-geschützt, unbekannter Trust) darf auch im
    lokalen Fallback nicht geschrieben werden. Bei fehlenden Trust-Metadaten wird
    eine **existierende** Zieldatei abgelehnt (nie fail-open).
    """
    target = Path(ctx["tier3_dir"]) / key
    try:
        import mcp_memory_server as mcp_server

        db_path = mcp_server._trust_db_path()
        db = mcp_server._load_trust_db(db_path) if db_path is not None else None
    except ImportError:  # SDK/Modul nicht verfügbar → keine Metadaten
        db = None
    if db is None:
        return "Trust-Metadaten nicht verfügbar – fail-closed (§9.2c/§9.3)" if target.exists() else None
    current = db.get(f"tier3/{key}")  # R11/R13/R14: Scope-qualifizierter Trust-Schlüssel
    if current == "blue" and trust_color == "green":
        return "green darf bestätigtes blue nicht überschreiben (§9.2c/§10.7)"
    if target.exists() and current is None:
        return "existierende Zieldatei + unbekannter Trust – fail-closed (§9.2c/§9.3)"
    return None


def _local_fallback(ctx: dict, key: str, content: str, trust_color: str, reason: str) -> dict:
    """§11-Fallback bei echtem MCP-Ausfall – mit denselben Schutzregeln (§9.2a/§9.2c).

    N5: `red` wird nicht persistiert, der Key darf nicht aus `tier3` entkommen,
    PII wird VOR dem Store entfernt; geschrieben wird nur innerhalb `tier3_dir`.
    K7/B3: blue-geschützte/ungültige Trust-Kombinationen werden fail-closed abgelehnt.
    """
    if trust_color == "red":
        return {
            "ok": False,
            "status": "rejected",
            "via": "local-fallback",
            "reason": "Tri-Color Red: Verstoß – nicht gespeichert",
        }
    denied = _mandate_write_denied(ctx)  # R02 §9: Read-only-Mandat blockiert den Write
    if denied is not None:
        return {"ok": False, "status": "rejected", "via": "local-fallback", "reason": denied[:80]}
    if trust_color not in ("blue", "green", "red"):
        return {"ok": False, "via": "local-fallback", "reason": f"ungültige Trust-Farbe {trust_color!r}"}
    if not key or ".." in key or key.startswith("/") or "/" in key or "\\" in key:
        return {"ok": False, "via": "local-fallback", "reason": f"ungültiger key: {key!r}"}
    violation = _fallback_domain_violation(ctx, key, trust_color)
    if violation is not None:
        return {"ok": False, "status": "rejected", "via": "local-fallback", "reason": violation}
    # K2: EIN Schreibpfad – die Mutation läuft durch das Write-Gateway (inkl. PII + Provenienz).
    target = Path(ctx["tier3_dir"]) / key
    res = write_gateway.store_file(
        target=target,
        content=content,
        now=float(ctx.get("now", 0.0)),
        activity="skill-memory-write",
        agent="skill-interpreter",
        origin="user",
        verified=True,
    )
    return {
        "ok": res["ok"],
        "via": "local-fallback",
        "reason": (res.get("reason") or reason)[:80],
        "written": (res.get("written") or [None])[0],
        "trust": trust_color,
    }


def _run_memory_write(ctx: dict, scope: str = "tier3", key: str = "", content: str = "", trust: str = "green") -> dict:
    """Echter Executor für das MCP-Tool `memory.write` (in-process via FastMCP, §11).

    Offizieller MCP-Pfad: `FastMCP.call_tool` (in-process, kein Subprozess).
    **§11-Fallback N5:** NUR bei echtem Ausfall (SDK/Transport). Validierungs- und
    Scope-Fehler (`ValueError` aus `_path`/`_scope_dir`) werden als Fehler gemeldet –
    KEIN Fallback. Der Fallback validiert Pfad, filtert PII und lehnt `red` ab.
    """
    key = key or (re.sub(r"[^a-z0-9]+", "-", (ctx["question"] or "").lower()).strip("-")[:60] + ".md")
    content = content or ctx["fact"]
    denied = _mandate_write_denied(ctx)  # R02 §9: Kontext-Mandat VOR dem echten MCP-Aufruf
    if denied is not None:
        return {"ok": False, "via": "mandate", "status": "rejected", "reason": denied[:80]}
    try:
        import mcp_memory_server
    except ImportError as exc:  # echter Ausfall: SDK nicht verfügbar -> §11-Fallback
        return _local_fallback(ctx, key, content, trust, f"MCP-SDK fehlt: {exc}")
    try:
        server = mcp_memory_server.build_server()
        result = asyncio.run(
            server.call_tool("memory.write", {"scope": scope, "key": key, "content": content, "trust": trust})
        )
    except Exception as exc:  # noqa: BLE001 - echte Ausführung
        # FastMCP verpackt Funktionsfehler in `ToolError` mit `from <fehler>`; der
        # ursprüngliche Fehler bleibt als `__cause__` erhalten.
        # K7/B3: eine fachliche Ablehnung (`DomainRejection`) ist KEIN Transportausfall
        # und darf NIE in den lokalen Fallback; Validierungs-/Scope-Fehler ebenso.
        if isinstance(exc, write_gateway.DomainRejection) or isinstance(exc.__cause__, write_gateway.DomainRejection):
            return {"ok": False, "via": "mcp", "status": "rejected", "reason": str(exc)[:80]}
        if isinstance(exc.__cause__, ValueError):
            return {"ok": False, "via": "mcp", "reason": str(exc.__cause__)[:80]}
        return _local_fallback(ctx, key, content, trust, str(exc))
    parsed = _parse_mcp(result)
    if write_gateway.is_domain_rejection(parsed):  # fachliches `rejected` → NIE Fallback
        return {
            "ok": False,
            "via": "mcp",
            "status": "rejected",
            "reason": parsed.get("reason", ""),
            "result": parsed,
        }
    return {"via": "mcp", "result": parsed}


def _run_ingestion_hook(ctx: dict, **_ignored) -> dict:
    """Stufe 1: Encoding-Gate (Berechtigung) + Entity-Resolution (Ergebnis)."""
    decision = ingestion_hook.EncodingGate().check(ctx["fact"], "prompt", 1.0)
    return {
        "accepted": decision.accepted,
        "reason": decision.reason,
        "entities": ingestion_hook.resolve_entities(ctx["fact"], backend="rules"),
    }


def _run_fast_write_router(ctx: dict, **_ignored) -> dict:
    """Stufe 2: 3-Klassen-Entscheidung §10.7 (Eingabe = Zero-Shot-Checks)."""
    cls, gate = fast_write_router._decide(
        bool(ctx.get("refusal", False)),
        bool(ctx.get("large_correct", True)),
        bool(ctx.get("memory_correct", True)),
    )
    return {"class": cls, "gate": gate}


def _run_trust(ctx: dict, **_ignored) -> dict:
    """Stufe 6: Privacy (PII löschen) + Poisoning-Guard + Bias-Check (§9.2)."""
    admission = trust.PoisoningGuard().admit(
        {"source": ctx.get("origin", "user"), "verified": bool(ctx.get("verified", True))}
    )
    bias = trust.BiasCheck(checkpoint=float(ctx.get("checkpoint", 0.0)), tau=float(ctx.get("tau", 0.10))).check(
        float(ctx.get("bias_current", 0.0))
    )
    return {"minimized": trust.PIIFilter().minimize(ctx["fact"]), "admission": admission, "bias": bias}


def _run_bias_monitor(ctx: dict, **_ignored) -> dict:
    """Stufe 5: Drift-Index (§9.1c) aus Baseline vs. aktueller Verteilung."""
    monitor = bias_monitor.BiasDriftMonitor(baseline=ctx["baseline"], tau=float(ctx.get("tau", 0.10)))
    return monitor.observe(ctx["distribution"], step=ctx.get("step", 1))


def _run_shared_memory(ctx: dict, **_ignored) -> dict:
    """Stufe 8: Shared-Tier-Write mit ACL-Berechtigung + Konfliktauflösung."""
    agent = ctx.get("agent", "agent")
    tier = shared_memory.SharedTier(
        acl={agent: {"read": {"*"}, "write": {"*"}}},
        trust={agent: float(ctx.get("trust", 0.5))},
    )
    write = tier.write(agent, ctx.get("key", "skill"), ctx.get("value", ctx["fact"]))
    return {"write": write, "sync": tier.sync()}


def _run_reflective_agent(ctx: dict, **_ignored) -> dict:
    """Stufe 4/5: HMM-Trägheits-Update aus Reflexions-Matrix (SEAA Eq. 2)."""
    update = reflective_agent.HMMInertia().update_from_reflection(
        ctx.get("reflection", ""), delta=ctx["reflection_delta"]
    )
    return {"skipped": update["skipped"], "after": update["after"]}


def _run_evaluator(ctx: dict, **_ignored) -> dict:
    """Compare: ε-Best-Belief + Cohen's κ auf externen Rater-Listen (Red-Queen)."""
    return {
        "best_belief": evaluator_version.best_belief(int(ctx.get("successes", 3)), int(ctx.get("failures", 1))),
        "kappa": evaluator_version.cohens_kappa(ctx["rater_a"], ctx["rater_b"]),
    }


# Registrierte Executoren (Tool-/Prozessname -> echte Funktion).
DEFAULT_REGISTRY = {
    "pipeline.py": _run_pipeline,
    "memory.write": _run_memory_write,
    "ingestion_hook.py": _run_ingestion_hook,
    "fast_write_router.py": _run_fast_write_router,
    "trust.py": _run_trust,
    "bias_monitor.py": _run_bias_monitor,
    "shared_memory.py": _run_shared_memory,
    "reflective_agent.py": _run_reflective_agent,
    "evaluator_version.py": _run_evaluator,
}

# K4: maschinenlesbares Frontmatter-Feld `process:` (JSON Schema Draft 2020-12).
# Quelle (Belegt): JSON-Schema-Spec https://json-schema.org/specification.
# Hinweis (§6): JSON Schema prüft nur die STRUKTUR – die echte Ausführung
# belegt `bind_skill` (Eingabe→Berechtigung→Ergebnis).
PROCESS_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "SKILL.md frontmatter `process:` (K4)",
    "type": "object",
    "properties": {
        "process": {"type": "string", "enum": sorted([*DEFAULT_REGISTRY, "doc-only"])},
    },
    "required": ["process"],
    "additionalProperties": False,
}


def validate_process(spec: dict) -> dict:
    """Validiert die Struktur des `process:`-Feldes gegen `PROCESS_SCHEMA`."""
    value = {"process": spec.get("process")}
    errors = sorted(jsonschema.Draft202012Validator(PROCESS_SCHEMA).iter_errors(value), key=lambda e: list(e.path))
    return {"valid": not errors, "errors": [e.message for e in errors]}


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


def bind_skill(skill_path: Path, ctx: dict, registry: dict | None = None) -> dict:
    """Bindet EINEN Skill an seinen Executor (K4): parse → Schema prüfen → ausführen.

    `process: doc-only` wird ehrlich als solches gemeldet (kein Executor, keine
    Ausführung). Ein Wert ohne registrierten Executor → `unbound` (kein Fake).
    """
    spec = parse_skill(skill_path)
    reg = DEFAULT_REGISTRY if registry is None else registry
    validation = validate_process(spec)
    proc = spec.get("process")
    if proc == "doc-only":
        return {
            "skill": spec["name"],
            "process": proc,
            "valid": validation["valid"],
            "status": "doc-only",
            "executed": False,
            "reason": "doc-only: kein Executor (ehrlich gekennzeichnet)",
        }
    fn = reg.get(proc)
    if fn is None:
        return {
            "skill": spec["name"],
            "process": proc,
            "valid": validation["valid"],
            "status": "unbound",
            "executed": False,
            "reason": f"kein Executor für {proc!r}",
        }
    return {
        "skill": spec["name"],
        "process": proc,
        "valid": validation["valid"],
        "status": "lauffähig",
        "executed": True,
        "result": fn(ctx),
    }


def bind_all_skills(ctx: dict, registry: dict | None = None) -> list:
    """Bindet alle aktiven Skills (`procedural_memory.active_skills`, 14)."""
    return [bind_skill(p, ctx, registry=registry) for p in list_skills()]


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


def _result_field(result, name):
    """Feld aus einem Tool-Ergebnis (dict) – sonst None (Audit-robust)."""
    return result.get(name) if isinstance(result, dict) else None


def run_skill_agent(
    skill_path: Path,
    ctx: dict,
    *,
    llm_fn=None,
    registry: dict | None = None,
    max_steps: int = 8,
    recorder=None,
) -> dict:
    """ReAct-Loop (Agent Skills/ReAct): LLM liest `## Ablauf` und ruft registrierte Tools auf.

    K7/B3: optionaler `recorder` (OTel-Spans + Audit, `trace_audit`); ohne Angabe
    wird `KNOWLEDGE_TRACE_DIR` ausgewertet (ungesetzt → NOOP, kein Write).
    """
    spec = parse_skill(skill_path)
    reg = DEFAULT_REGISTRY if registry is None else registry
    llm = llm_fn if llm_fn is not None else _default_llm
    rec = recorder if recorder is not None else trace_audit.Recorder.from_env()
    messages = [{"role": "system", "content": _SYSTEM}, {"role": "user", "content": _task_prompt(spec)}]
    tools = _tool_specs(reg)
    name_map = {_fn_name(k): k for k in reg}
    trace, final, stopped = [], None, False
    with rec.span("skill.run", **{"skill.name": spec["name"], "skill.processes": len(spec["processes"])}):
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
            with rec.span("skill.tool", **{"tool": name, "step": step}):
                result = fn(ctx, **args)
                rec.audit(
                    "skill.tool",
                    step=step,
                    tool=name,
                    ok=_result_field(result, "ok"),
                    via=_result_field(result, "via"),
                )
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
            messages.append(
                {"role": "tool", "tool_call_id": call_id, "content": json.dumps(result, ensure_ascii=False)}
            )
        rec.audit("skill.finish", stopped=stopped, steps=len(trace), final=final is not None)
    rec.flush()
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
