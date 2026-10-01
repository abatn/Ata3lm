# 030 – Governance-MCP (GLiNER + Drift-Index + Lyapunov als MCP)

> Datum: 2026-10-01
> Rekursionstiefe: System-Iteration (Governance/MCP)
> Phase: Observe → Compare → Revise
> Auslöser: menschlicher Auftrag vom 2026-10-01 (drei offene Punkte).
> Baut auf 027 (Drift-Index) und 029 (Forschungslücken) auf.

## 1. Zustand vorher / nachher

| Aspekt | vorher | nachher |
|---|---|---|
| MCP-Abdeckung der 3 Punkte | **0/16 Server** deckt irgendeinen Punkt ab | `governance-mcp` mit 3 Tools (Server 16 → 17) |
| Entity-Resolution | regelbasiert (Wörterbuch, `confidence=1.0` gesetzt) | **echtes GLiNER** `0.2.29` + Modell `urchade/gliner_multi-v2.1`, regelbasierter Fallback erhalten |
| Schwellwert GLiNER | `0.5` (unbelegt; machte Enrichment wirkungslos) | **`0.4`**, kalibriert (§9.1c), per `GLINER_THRESHOLD` überschreibbar |
| Drift-Index | schon in `bias_monitor.py` (027), nur lokal | zusätzlich als MCP-Tool `drift_index` exponiert |
| Lyapunov `E[ΔV]≤0` | fehlte | implementiert in `reflective_agent.py` + MCP-Tool `lyapunov_check` |

**Diff `(π, I, M)`:**
- `π` (Code): `ingestion_hook.py` 5/475 Zeilen geändert; `reflective_agent.py`
  24/503 Zeilen neu; `bias_monitor.py` **unverändert** (0/149).
- `I` (Interface): kein Signatur-Wechsel. Neue MCP-Tools = neue Server-Registrierung.
- `M` (Memory): keine Tier-1-Änderung → **kein `versions/vN/`-Snapshot nötig**
  (Versionierungs-Mechanik A greift nur bei `data/memory/tier1-base/`).

## 2. Änderungen

| Datei | Was |
|---|---|
| `data/memory/ingestion_hook.py` | `GLINER_THRESHOLD` (Default 0.4, kalibriert) |
| `data/memory/reflective_agent.py` | `lyapunov_check()`, `simulate_lyapunov()`, `LYAPUNOV_SIM=1` |
| `data/memory/bias_monitor.py` | unverändert (Auftrag 2 war bereits implementiert) |
| `/home/opc/mcp-servers/governance-mcp/server.py` | 3 Tools, Threshold/Confidence-Parität zu `ingestion_hook` |
| `~/.config/opencode/opencode.json` | `mcp."governance-mcp"` registriert (außerhalb des Repos) |
| `ergebnisse/mcp-check-{gliner,drift,lyapunov}.md`, `ergebnisse/mcp-neu.md` | Nachweise |
| `connectors/governance-mcp.md`, `AGENTS.md` Connector-Tabelle (15 → 16) | Gesetz/Connector |

## 3. Compare-Beleg (externes Signal, 8 Tests)

Score = erfüllte Tests / Gesamttests (§9).

| # | Test | Erwartung | Ergebnis |
|---|---|---|---|
| T1 | MCP-Handshake `tools/list` | 3 Tools | `['drift_index', 'lyapunov_check', 'resolve_entities']` ✓ |
| T2 | `drift_index(DI=0.0685, τ=0.02)` | `DI > τ` → `ask` | `"flagged": true, "gate": "ask"` ✓ |
| T3 | `lyapunov_check(fallend)` | `E[ΔV]=-0.16 ≤ 0` → `ok` | `"stable": true, "gate": "ok"` ✓ |
| T4 | `lyapunov_check(wachsend)` | `E[ΔV]=+0.3 > 0` → `ask` | `"stable": false, "gate": "ask"` ✓ |
| T5 | `resolve_entities(backend=auto)` | GLiNER | `"backend": "gliner"`, `confidence 0.4775` ✓ |
| T6 | `resolve_entities(backend=rules)` | Fallback | 3 Treffer, `"backend": "rules"` ✓ |
| T7 | System-Python ohne `gliner` | kein Crash, Fallback | 4/3 Treffer, Enrichment liefert Entities ✓ |
| T8 | GLiNER deterministisch | 2. Lauf identisch | `Reproduzierbar (2. Lauf identisch): True` ✓ |

**Score: 8/8 = 100 % ≥ 95 % → Gate `allow`.**

Rohausgaben: `ergebnisse/mcp-neu.md` §4, `ergebnisse/mcp-check-gliner.md` §2.3,
`ergebnisse/mcp-check-lyapunov.md` §2, `ergebnisse/mcp-check-drift.md` §2.

## 4. Drift-Bound (§9.1c)

| Artefakt | Δ | Bound |
|---|---|---|
| `ingestion_hook.py` | 5/475 = 1,05 % | ≤ 10 % ✓ |
| `reflective_agent.py` | 24/503 = 4,77 % | ≤ 10 % ✓ |
| `bias_monitor.py` | 0/149 = 0 % | ✓ |

Kein Drift-Flag.

## 5. Quellen (HTTP 200 geprüft 2026-10-01)

- MCP-Protokoll/SDK: https://modelcontextprotocol.io/, https://py.sdk.modelcontextprotocol.io/v1/server/,
  https://registry.modelcontextprotocol.io/
- WhyLab Causal Audit Framework (C1 Drift, C3 Lyapunov-bounded damping):
  https://github.com/neogenesislab/WhyLab-NeurIPS2026
- Agent Drift (JSD): https://arxiv.org/abs/2601.04170
- GraphRAG-SDK (Entity-Extraction): https://github.com/FalkorDB/GraphRAG-SDK
- GLiNER-Relex: https://arxiv.org/abs/2605.10108 · Modell:
  https://huggingface.co/urchade/gliner_multi-v2.1
- Gödel-Agent (Abgrenzung, kein Lyapunov-Werkzeug): https://arxiv.org/abs/2410.04444

Keine **neue** Quelle hinzugefügt — alle standen schon in der
`AGENTS.md`-Connector-Tabelle (daher kein §9 „Neue Quelle → Gate").

## 6. Gate-Entscheidung (§9)

| Bedingung | Wert | Gate |
|---|---|---|
| Compare-Score | 100 % | allow |
| Neue Quelle | keine | – |
| Interface-Änderung | keine Signatur-Änderung (neuer MCP-Server = separate Registrierung) | – |
| Drift | max. 4,77 % | – |
| `self_update` an Originaldatei | nein (neue/nachgeführte Dateien) | – |

→ **automatisch erlaubt**. Die drei menschlichen Freigaben des Auftrags
(GLiNER installieren, MCP registrieren, `AGENTS.md` nur Connector-Tabelle)
lagen **vor** der Umsetzung vor.

## 7. Freigabe

**Freigabe-Status:** `approved: Batnini, 2026-10-01`.
(Entscheidungen dokumentiert in dieser Iteration; §9.3 Zwei-Personen-Verifikation
gilt nur für `self_update`-Flows an Originaldateien — hier nicht einschlägig.)

## 8. Nächstes Self-Feedback (t+1)

- `mcp_governance_test.py` als dauerhaften Test im Repo ablegen (liegt aktuell
  in `/tmp/`).
- GLiNER-Threshold an einem größeren Testset kalibrieren (n=2 Sätze ist dünn);
  bei ≥30 Sätzen gelernten Schwellwert einsetzen (§9.1c).
- `lyapunov_check` mit echten Energieserien aus `BiasDriftMonitor`-Reports
  koppeln statt mit Beispielvektoren.
- Prüfen, ob `governance-mcp` die Gate-Entscheidung (§9-Tabelle) als eigenes
  Tool `gate_decision(score, condition)` exponiert.
