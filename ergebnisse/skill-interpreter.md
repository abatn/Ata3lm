# Skill-Interpreter (`data/memory/skill_interpreter.py`)

> Datum: 2026-10-04 · Status: **Belegt** (Standard) + **Auftrag** (Verdrahtung).
> Guardrail 7: echte LLM-/Tool-Ausführung. Ziel `g`: Schicht-6-Lücke schließen —
> `## Ablauf`-Schritte **LLM-ausgeführt** (nicht NL-parser) + MCP-Tools **mit Executor**.

## 1. Quellen (verifiziert, §6)

| Quelle | Kern | Link |
|---|---|---|
| **Agent Skills** (Anthropic / agentskills.io) | SKILL.md = LLM-Instruktion (progressive disclosure); Ausführung via Tools | docs.anthropic.com/…/agent-skills/overview · agentskills.io |
| **ReAct** (Yao et al. 2023) | Thought → Action → Observation | arXiv:2210.03629 |
| **MCP-Spec + Python-SDK** | Client ruft `tools/call` (stdio/in-process) | modelcontextprotocol.io/specification · py.sdk.modelcontextprotocol.io |
| **LLMCompiler** (Kim et al., ICML 2024) | Planner → Executor | arXiv:2312.04511 |

**Befund:** Das `SKILL.md`-Format **ist** der Agent-Skills-Standard → die `## Ablauf`-Schritte
werden **vom LLM** über Tool-Calling ausgeführt (kein Eigen-Parser). MCP-Tools laufen über
den offiziellen MCP-Pfad.

## 2. Zwei Modi

| Modus | Was | Quelle |
|---|---|---|
| `run_skill` | führt die in `## Prozesse (Aufrufe)` **deklarierten** Prozesse aus | Auftrag |
| `run_skill_agent` | **ReAct-Loop**: LLM liest `## Ablauf` und ruft registrierte Tools auf | Agent Skills + ReAct |

- **Tool-Schemas:** Function-Calling (OpenAI-Format); Namen werden MCP/LLM-konform
  saniert (`pipeline.py` → `pipeline_py`, da `.` ungültig ist).
- **Executoren:** `pipeline.py` → `pipeline.route_and_store`; `memory.write` →
  **FastMCP in-process** (`mcp_memory_server.build_server().call_tool(...)`, offizieller MCP-Pfad).
- **§11-Fallback:** MCP-Fehler → **lokale Memory** (kein Datenverlust).
- **Guardrail 7:** ohne Key/Endpoint → **NOOP** (kein Fake).

## 3. Echte Ausgabe (CLI, echtes LLM mit Function-Calling, 2026-10-04)

```text
skill: act · steps: 6 · stopped: true
step 1  action=tool   tool=pipeline.py  -> ok=true action=write-new
        mandate=ALLOW · fwr=write-new · trust=PII entfernt · write=write-new
step 2  action=final  "Die Element-Pipeline (Stufe 7) wurde erfolgreich ausgeführt …"
```

- Das **LLM** hat den Skill gelesen und **selbst** das Tool `pipeline.py` aufgerufen (ReAct).
- `memory.write` läuft in-process über **FastMCP** (getestet, schreibt real).

## 4. Test (echt, Guardrail 7)

`tests/test_skill_interpreter.py` (14 Tests): deklarativer Runner (5) + ReAct-Loop (9):
`test_agent_tool_und_final`, `test_agent_noop_ohne_llm`, `test_agent_unbekanntes_tool`,
`test_agent_max_steps`, `test_agent_memory_write_in_process_mcp` (echter FastMCP-Call),
`test_memory_write_fallback` (§11), `test_agent_sanitized_tool_name`, `_parse_mcp`-Zweige.
`skill_interpreter.py`: **100 %** Line+Branch.

## 5. Gate (§9)

- Interface-Änderung (ReAct-Loop + MCP-Executor) → **approved** (Batnini, „setze das ein").
- Guardrail 3: Provenienz `ergebnisse/rekursion/050-skill-interpreter-agent.md`.
- Guardrail 6: kein Commit ohne Erlaubnis. §9.1b: `AGENTS.md` unverändert.
- **Ehrliche Grenzen:** Der Loop ist ein **einzelner** Tool-Call pro Schritt (nicht parallel
  wie LLMCompiler); MCP wird **in-process** (FastMCP) aufgerufen, nicht über stdio/HTTP.
