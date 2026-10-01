# Neuer MCP-Server: `governance-mcp`

> Datum: 2026-10-01 · Auftrag „MCP-Strategie" · Phase: Handeln
> Lab-Prinzip §6: Quellen verifiziert, keine Erfindungen. Fail-soft: jedes Tool
> fängt Ausnahmen ab (`except Exception → {"error": ...}` bzw. Fallback-Regeln).

## 1. Warum ein neuer Server

Die drei Auftrags-Punkte waren von **keinem** der 16 MCP-Server abgedeckt
(Nachweis je Punkt: `ergebnisse/mcp-check-gliner.md`,
`ergebnisse/mcp-check-drift.md`, `ergebnisse/mcp-check-lyapunov.md`;
Grundlage `ergebnisse/mcp-16-test.md` mit allen Tool-Listen).
Gemäß Auftrag: „Wenn KEIN MCP den Punkt abdeckt: Baue einen neuen MCP-Server
nach Standard (stdio oder HTTP)."

## 2. Standard & Quellen (HTTP 200 geprüft 2026-10-01)

| Element | Wahl | Quelle | Status |
|---|---|---|---|
| Protokoll | **stdio** (wie alle lokalen Server im Projekt) | https://modelcontextprotocol.io/ | 200 |
| SDK | `mcp.server.fastmcp.FastMCP` | https://py.sdk.modelcontextprotocol.io/v1/server/ | 200 |
| Registry-Konvention | `mcp dev` / `mcp run` | https://registry.modelcontextprotocol.io/ | 200 |
| Drift C1 + Lyapunov C3 | WhyLab Causal Audit Framework | https://github.com/neogenesislab/WhyLab-NeurIPS2026 | 200 |
| JSD-Drift | Agent Drift | https://arxiv.org/abs/2601.04170 | 200 |
| Entity-Extraction | GraphRAG-SDK Step 1 | https://github.com/FalkorDB/GraphRAG-SDK | 200 |
| GLiNER | GLiNER-Relex | https://arxiv.org/abs/2605.10108 | 200 |

(Identisches Bau-Muster wie in `ergebnisse/mcp-ziel-plan.md` §3.1 dokumentiert.)

## 3. Datei & Registrierung

| Feld | Wert |
|---|---|
| Server | `/home/opc/mcp-servers/governance-mcp/server.py` |
| Python | `/home/opc/mcp-servers/hela-mem-mcp/.venv/bin/python` (3.12.13, enthält `mcp` **und** `gliner`) |
| Registrierung | `~/.config/opencode/opencode.json` → `mcp."governance-mcp"` |
| Eintrag | `type: local`, `command: [venv-python, server.py]`, `env: {GLINER_MODEL, GLINER_THRESHOLD: "0.4"}`, `enabled: true` |
| Server-Anzahl | 16 → **17** aktive Server (18 Einträge, `context7` bleibt deaktiviert) |

> `opencode.json` liegt **außerhalb** des Repos (persönliche OpenCode-Konfig)
> und ist daher nicht Teil des Git-Commits — Änderung hier dokumentiert statt
> versioniert.

### Human-Gate (§9 / §9.3)

Neuer MCP = Interface-Änderung → **immer menschliches Gate**.
Freigabe: Mensch, 2026-10-01 („Registrieren, hela-mem-venv nutzen").
Zwei-Personen-Fluss (`pending → first_approved → …`) greift hier nicht, weil es
sich nicht um einen `self_update`-Vorgang an einer Originaldatei handelt; der
Freigabe-Vermerk steht in `ergebnisse/rekursion/030-governance-mcp.md`.

## 4. Tools (3) — tatsächliche Ausgaben nach `initialize` + `tools/list` + `call_tool`

```text
server: governance-mcp
tools: ['drift_index', 'lyapunov_check', 'resolve_entities']
```

| Tool | Signatur | Rohausgabe (echter Lauf) |
|---|---|---|
| `drift_index` | `(current, reference, tau=0.02, w_max=0.6)` | `{"DI": 0.0685, "weighted_shift": 0.2, "weights": {"approve": 0.3317, "reject": 0.3317, "revise": 0.3366}, "flagged": true, "gate": "ask", "tau": 0.02}` |
| `lyapunov_check` | `(energies, tau=0.0)` | stabil: `{"E_dV": -0.16, ..., "stable": true, "gate": "ok"}` · instabil: `{"E_dV": 0.3, ..., "stable": false, "gate": "ask"}` |
| `resolve_entities` | `(text, backend="auto")` | `auto` → `{"entity_type": "Concept", "span": "Fast Write Routing", "confidence": 0.4775, "backend": "gliner"}` · `rules` → 3 Treffer mit `backend: "rules"`, `confidence: 1.0` |

Testskript: `/tmp/opencode/mcp_governance_test.py` (stdio-Handshake über den
MCP-Client des hela-mem-venv).

## 5. Beziehung zur lokalen Code-Basis (Dual-Layer, §11)

`governance-mcp` **dupliziert nicht**, sondern **exponiert** dieselbe Logik,
die auch lokal in `data/memory/` liegt:

| MCP-Tool | lokale Implementierung | Layer-Regel (§11.3) |
|---|---|---|
| `drift_index` | `data/memory/bias_monitor.py` | lokale Memory bleibt Pflicht-Basis |
| `lyapunov_check` | `data/memory/reflective_agent.py` | lokaler Pfad führt weiter, MCP ist Zugang |
| `resolve_entities` | `data/memory/ingestion_hook.py` | Fallback `rules`, wenn `gliner` fehlt |

MCP-Ausfall → lokaler Aufruf, kein Datenverlust (§11.2).

## 6. Guardrails

- **Fail-soft:** alle drei Tools in `try/except`; `resolve_entities` fällt ohne
  GLiNER auf `backend=rules` zurück, bei `backend="gliner"` ohne Modell → `[]`.
- **Gate-Anbindung:** `drift_index` → `flagged ⇒ gate="ask"`;
  `lyapunov_check` → `E[ΔV] > τ ⇒ gate="ask"`.
- **§6 keine Erfindungen:** jede Zeile der Server-Kommentare referenziert eine
  oben auf HTTP 200 geprüfte Quelle.
- **§11:** kein Schreibvorgang ausschließlich in den MCP; die Fakten liegen in
  `knowledge/structured/` bzw. `data/memory/`.

## 7. Reproduzierbarer Test

```bash
# 1) MCP-Handshake + 3 Tool-Calls
/home/opc/mcp-servers/hela-mem-mcp/.venv/bin/python /tmp/opencode/mcp_governance_test.py

# 2) Lokaler (MCP-freier) Selbsttest derselben Logik
LYAPUNOV_SIM=1 python3 data/memory/reflective_agent.py
python3 data/memory/bias_monitor.py
/home/opc/mcp-servers/hela-mem-mcp/.venv/bin/python -W ignore data/memory/ingestion_hook.py
```
