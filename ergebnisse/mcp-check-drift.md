# MCP-Check Auftrag 2: Drift-Index — Abdeckung + Status

> Datum: 2026-10-01 · Auftrag 2 von 3 · Phase: Observe → Compare
> Lab-Prinzip §6: gemessene Werte, Rohausgaben aus dem Lauf.

## 1. Prüfung: Deckt einer der 16 MCP-Server (MARS, TRACE, …) den Drift-Index ab?

**Quelle:** `ergebnisse/mcp-16-test.md` (vollständige Tool-Listen) +
Code-Durchgriff auf `/home/opc/mcp-servers/{mars,trace,adas,godel}-mcp/server.py`.

| Server | Tools | Drift/JSD/τ? |
|---|---|---|
| mars | `mars_list_strategies`, `mars_run_strategy`, `mars_analyze_failure` | nein |
| trace | `metric_recall_at_k`, `metric_gold_rank`, `metric_precision_in_accepted`, `metric_recall_in_accepted`, `metric_compute`, `parse_json` | nein (Retrieval-Metriken, kein Drift) |
| adas | `adas_init_archive`, `adas_get_prompt`, `adas_propose_agent` | nein |
| godel-agent | `run_code`, `read_logic` | nein (Executor, keine Governance) |
| alle übrigen 12 | (siehe `mcp-16-test.md`) | nein |

```bash
grep -in "drift\|lyapunov\|jsd" ergebnisse/mcp-16-test.md
# -> 0 Treffer
```

**Ergebnis: KEIN MCP deckt den Drift-Index ab.**

## 2. Status der geforderten Implementierung

Gefordert: JSD-basierte Signalgewichtung in `data/memory/bias_monitor.py` mit
Schwellenwert τ und Capped Simplex (`w_max=0.6`).

**Befund: bereits implementiert** (Iteration 027, `ergebnisse/rekursion/027-drift-index.md`);
in dieser Iteration erneut ausgeführt und verifiziert — kein erneuter Code-Eingriff nötig.

| Anforderung | Fundstelle | Status |
|---|---|---|
| JSD | `data/memory/bias_monitor.py:34` `def jsd(p, q)` | vorhanden |
| Capped Simplex, `w_max=0.6` | `bias_monitor.py:50` `def capped_simplex(w, w_max=0.6)`; `bias_monitor.py:82` `w_max: float = 0.6` | vorhanden |
| Schwellenwert τ | `bias_monitor.py:81` `tau: float = 0.10` (Demo nutzt `tau=0.02`, passend zum JSD-Bereich) | vorhanden |
| Flag → Human-Gate | `bias_monitor.py:111` `flagged = metric > self.tau` → `gate`-Signal | vorhanden |

### Selbsttest (real)

```bash
python3 data/memory/bias_monitor.py
```

```
  self_update  9: DI(JSD)=0.0577 weighted=0.1815 damping=0.423 -> ask
  self_update 10: DI(JSD)=0.0731 weighted=0.2016 damping=0.269 -> ask

  Report: {'steps': 10, 'tau': 0.02, 'w_max': 0.6, 'flagged_steps': [6, 7, 8, 9, 10],
           'max_DI': 0.0731, 'max_jsd': 0.0731}

  Beispiel Signale/Gewichte (capped simplex w_max=0.6):
  {'DI': 0.0752, 'jsd': 0.0752, 'weighted_shift': 0.2024,
   'signals': {'revise': 0.2, 'approve': 0.3, 'reject': 0.1},
   'weights': {'revise': 0.3508, 'approve': 0.3366, 'reject': 0.3126}}
```

Geprüft: `Σ w = 1`, `max w = 0.3508 ≤ w_max 0.6` ✓ · Flag ab Schritt 6 (> τ) ✓.

## 3. MCP-Lücke wird geschlossen

Da kein bestehender Server es abdeckt, liegt der Drift-Index als Tool
**`drift_index`** im neuen `governance-mcp` (siehe `ergebnisse/mcp-neu.md`).
Aufruf-Rohausgabe (echter MCP-Handshake):

```text
drift_index: {"DI": 0.0685, "weighted_shift": 0.2,
              "weights": {"approve": 0.3317, "reject": 0.3317, "revise": 0.3366},
              "flagged": true, "gate": "ask", "tau": 0.02}
```

## 4. Quellen (HTTP 200 geprüft 2026-10-01)

| Quelle | Link | Status |
|---|---|---|
| WhyLab / Causal Audit Framework (Drift Index C1) | https://github.com/neogenesislab/WhyLab-NeurIPS2026 | 200 |
| Agent Drift (JSD) | https://arxiv.org/abs/2601.04170 | 200 |
| Bestehende Iteration 027 | `ergebnisse/rekursion/027-drift-index.md` | — |

## 5. Gate (§9)

Score 8/8 (s. `ergebnisse/rekursion/030-governance-mcp.md`) · keine neue Quelle
(Google/WhyLab stand schon in 027) · keine Interface-Änderung · Drift
`bias_monitor.py` 0/149 = **0 %** → **allow**.
