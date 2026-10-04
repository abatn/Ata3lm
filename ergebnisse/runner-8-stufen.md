# 8-Stufen-Runner (`data/memory/lifecycle_runner.py`)

> Datum: 2026-10-04 · Status: **Auftrag** (Stufenfolge + Stufe→Modul) · Quellen: AGENTS.md §3 +
> `knowledge/lifecycle/rekursion/wissenszyklus-8-stufen.md`. Guardrail 7: echte Ausführung.
> Ziel `g`: die Schicht-1-Lücke („8 Stufen nur Doku") mit einem **echten** Runner schließen.

## 1. Gesetz + Quelle

- **AGENTS.md §3** (8-Stufen-Zyklus): Erfahrung → Wissen → Gedächtnis → Kognition →
  Denken → Nicht-Kognition → Handeln → Wissen+.
- **`wissenszyklus-8-stufen.md`** (Lese-/Schreib-Semantik + Phasen-Mapping je Stufe).

## 2. Stufe → echtes Modul (Auftrag, aus dem Phasen-Mapping abgeleitet)

| # | Stufe | Phasen-Mapping | **echte** Funktion (kein Fake) |
|---|---|---|---|
| 1 | Erfahrung (schreibt M) | Observe + Akt-Obs | `ingestion_hook.resolve_entities` + `lru_cache.WorkingMemory.store` |
| 2 | Wissen (liest M) | Konstrukt | `ingestion_hook.update_graph` |
| 3 | Gedächtnis (schreibt O) | Konstrukt | **`pipeline.route_and_store`** (Pipeline-Integration) |
| 4 | Kognition (liest O) | Observe + Akt-Relate | `lru_cache.WorkingMemory.consolidate_edges` |
| 5 | Denken (Self-Feedback) | Revise-Reflect | `reflective_agent.parse_transition_delta` (**echte LLM-Reflexion**) |
| 6 | Nicht-Kognition (dämpft) | alle (dämpft) | `reflective_agent.lyapunov_check` (Dämpfung) |
| 7 | Handeln (Aktion → M) | Akt | `lru_cache.WorkingMemory.store` (gedämpfte Aktion) |
| 8 | Wissen+ (Compare/Revise) | Compare + Revise | `bias_monitor.BiasDriftMonitor.observe` (Drift-Gate) |

- **Stufenfolge = Auftrag** (gesetzte Ordnung), **kein Paper-Claim**.
- **Stufe→Modul = Auftrag** (Projekt-Zuordnung), abgeleitet aus dem Phasen-Mapping des Zyklus-Dokuments.
- **Keine Erfindung:** jede Stufe ruft eine **bestehende** Funktion auf.

## 3. Echte Ausgabe (CLI, 2026-10-04)

```text
stages: Erfahrung · Wissen · Gedächtnis · Kognition · Denken · Nicht-Kognition · Handeln · Wissen+
1 Erfahrung      entities=[]           stored=raw:beispiel          (schreibt M)
2 Wissen         added_nodes=[]        added_edges=0                (strukturiert)
3 Gedächtnis     ok=true  action=write-new                           (pipeline)
                 steps: mandate=ALLOW · fwr=write-new · trust=PII entfernt · write=write-new
4 Kognition      consolidated=true     strengthened=[]
5 Denken         self_feedback=0.0     (echte LLM-Reflexion; offline -> NOOP)
6 Nicht-Kognition E_dV=-0.1            damping=1.0  (stabil → keine Dämpfung)
7 Handeln        action=write-new      damped_by=1.0  stored=action:beispiel
8 Wissen+        DI=0.0  gate=ok       revised=true
```

- Stufe 3 ruft **`pipeline.route_and_store`** auf (Mandat → FWR → Trust/PII → Write) — die
  Pipeline-Integration. Stufe 6 dämpft (Lyapunov); Stufe 8 ist das Drift-Gate.

## 4. Test (echt, Guardrail 7)

`tests/test_lifecycle_runner.py` (5 Tests):
- `test_vollstaendiger_durchlauf` — 8 Stufen, echte Spur, M-Writes, Pipeline-Write (Denken offline → NOOP).
- `test_denken_matrix_zweig` — Matrix-Zweig über den **realen** Parser (Test-Seam, echte Eingabe).
- `test_noop_und_instabil` — NOOP (keine Matrix) + instabile Energie → Dämpfung 0.5.
- `test_ueberschreibungen` — Injektion aller Kontexte (Graph/Kanten/dims/Mandat).
- `test_stage_mechanism_vollstaendig` — jede Stufe hat ein echtes Modul.

`lifecycle_runner.py`: **100 %** Line+Branch.

## 5. Gate (§9)

- Interface-Änderung (neues Modul `lifecycle_runner.py`) → **approved** (Batnini, Auftrag).
- Guardrail 3: Provenienz `ergebnisse/rekursion/048-lifecycle-runner.md`.
- Guardrail 6: kein Commit ohne Erlaubnis. §9.1b: `AGENTS.md` unverändert.
- **Ehrliche Grenzen:** Stufenfolge + Stufe→Modul sind **Auftrag** (AGENTS.md §3 erlaubt das
  ausdrücklich: „Stufenfolge selbst ist gesetzte Ordnung, kein Paper-Claim"). **Stufe 5** ruft
  die **echte LLM-Reflexion** (`parse_transition_delta`); offline/ohne Key → **NOOP** (None),
  **keine erfundene Matrix** (Guardrail 7).
