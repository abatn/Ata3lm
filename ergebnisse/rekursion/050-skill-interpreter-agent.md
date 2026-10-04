# Rekursion 050: Skill-Interpreter — ReAct-Tool-Calling-Loop + MCP-Executor

> Datum: 2026-10-04 · Tiefe: `t=49 → t=50` · Phase: **Konstrukt → Akt**
> Freigabe: Batnini („setze das ein"). Interface-Änderung → §9 approved.
> Ziel `g`: `## Ablauf` LLM-ausführen (Agent Skills/ReAct) + MCP-Tools mit Executor (§11).

## 1. Quellen (verifiziert, §6)

- Agent Skills (Anthropic/agentskills.io): SKILL.md = LLM-Instruktion, Ausführung via Tools.
- ReAct (arXiv:2210.03629): Thought→Action→Observation.
- MCP-Spec + Python-SDK: `tools/call` (in-process via FastMCP).
- LLMCompiler (arXiv:2312.04511, ICML 2024): Planner→Executor.

## 2. Änderung (Diff)

| Datei | Änderung |
|---|---|
| `data/memory/skill_interpreter.py` | **+** `run_skill_agent` (ReAct-Loop), `_default_llm` (Function-Calling), `_run_memory_write` (MCP in-process + §11-Fallback), `_fn_name`, `_tool_specs` |
| `tests/test_skill_interpreter.py` | **14 Tests** (Loop-Zweige, MCP-Call, Fallback) |
| `ergebnisse/skill-interpreter.md` | aktualisiert (2 Modi + echte Ausgabe) |

## 3. Compare-Beleg (extern, echt)

```text
Echtes LLM (Function-Calling): step1 tool=pipeline.py -> write-new; step2 final
FastMCP in-process memory.write: ok=true (Datei real geschrieben)
pytest test_skill_interpreter.py: 14 passed · skill_interpreter.py 100 % Line+Branch
```

**Score** = 14/14 Tests = 100 %. **Drift:** additiv (Modul-Funktionen + Tests + Doku).

## 4. Gate (§9)

- Interface-Änderung → **approved** (Batnini). §9.1b: `AGENTS.md` unverändert.
- Ehrliche Grenzen: ein Tool-Call pro Schritt (nicht parallel); MCP in-process (nicht stdio).
