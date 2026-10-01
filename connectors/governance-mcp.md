# Connector: Governance-MCP

> Lab-Prinzip: MD-first. Mechanismen aus den Quellen, Übertragungen als
> `[Mapping/Auftrag]` markiert. Keine weiteren Quellen behauptet.

## 1. Identität **[Auftrag]**

Exponiert die drei Governance-Primitive des Knowledge-Agenten als lokalen
MCP-Server (stdio, FastMCP):

| Tool | Zweck | Gate-Wirkung |
|---|---|---|
| `drift_index` | JSD-basierter Drift-Index + Capped Simplex | `DI > τ` → `ask` |
| `lyapunov_check` | `E[ΔV] ≤ 0` (Lyapunov-bounded damping) | Verletzung → `ask` |
| `resolve_entities` | Entity-Resolution: GLiNER, sonst Regeln | keins (Fail-Soft) |

Server: `/home/opc/mcp-servers/governance-mcp/server.py`
Registriert in: `~/.config/opencode/opencode.json` → `mcp."governance-mcp"`

## 2. Mechanismen aus den Quellen

### 2.1 Drift-Index (C1) **[Belegt]**

Quelle: WhyLab / Causal Audit Framework, https://github.com/neogenesislab/WhyLab-NeurIPS2026
(HTTP 200, 2026-10-01). JSD-Variante: https://arxiv.org/abs/2601.04170 (HTTP 200).

`DI = JSD(current ‖ reference)`; Signalgewichte aus Entropie-Bedarf, projiziert
auf das **capped simplex** `Σw = 1, 0 ≤ wᵢ ≤ w_max` mit `w_max = 0.6`
**[Auftrag]**. Schwellenwert `τ` **[Auftrag]**.

### 2.2 Lyapunov-bounded damping (C3) **[Belegt]**

Quelle: WhyLab C3, https://github.com/neogenesislab/WhyLab-NeurIPS2026 (HTTP 200).

Energie-Sequenz `V`; stabil, wenn `E[ΔV] = mean(V[t+1] − V[t]) ≤ 0`.
Übertragung: Verletzung → `gate="ask"` **[Auftrag]** (AGENTS.md §9).

### 2.3 Entity-Resolution **[Belegt]**

Quellen: GraphRAG-SDK, https://github.com/FalkorDB/GraphRAG-SDK (HTTP 200);
GLiNER-Relex, https://arxiv.org/abs/2605.10108 (HTTP 200);
Modell `urchade/gliner_multi-v2.1`, https://huggingface.co/urchade/gliner_multi-v2.1 (HTTP 200).

GLiNER-Prinzip (lokal, deterministisch, keine API-Calls); regelbasierter
Fallback als Auftrag, solange `gliner` nicht importierbar ist.
Schwellwert `0.4`, kalibriert (siehe `ergebnisse/mcp-check-gliner.md`) **[Auftrag]**.

## 3. Integration in den Knowledge-Agenten

- **Stufe 1 Erfahrung:** `resolve_entities` klassifiziert Eingaben (Phase/Stage/
  Concept/Solver) vor dem Store.
- **Stufe 3 Gedächtnis:** `drift_index` überwacht die Signalverteilung gegen die
  Baseline; über τ → Human-Gate.
- **Stufe 5 Denken / Stufe 7 Handeln:** `lyapunov_check` prüft, ob die
  Energie des Systems fällt; sonst kein automatisches Weiterschreiben.
- **Dual-Layer (§11):** der MCP ist **Zugang**, nicht Speicher — dieselbe Logik
  liegt lokal in `data/memory/{ingestion_hook,bias_monitor,reflective_agent}.py`
  und bleibt damit ohne Netz erreichbar.

## 4. Nachweise

- Abdeckungsprüfung (kein bestehender MCP deckt die Punkte ab):
  `ergebnisse/mcp-check-gliner.md`, `ergebnisse/mcp-check-drift.md`,
  `ergebnisse/mcp-check-lyapunov.md`
- Server-Bau, Registrierung, Tool-Rohausgaben: `ergebnisse/mcp-neu.md`
- Iteration: `ergebnisse/rekursion/030-governance-mcp.md`
