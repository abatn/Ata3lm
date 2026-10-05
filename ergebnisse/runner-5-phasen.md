# 5-Phasen-Runner (`data/memory/recursion_runner.py`)

> Datum: 2026-10-04 · Status: **Belegt** (SEAA) + **Auftrag** (Phasenfolge).
> Guardrail 7: echter Zyklus. Ziel `g`: Konstrukt → Akt → Observe → Compare → Revise ausführen.

## 1. Quellen (verifiziert, §6)

- **SEAA** (arXiv:2609.17331, „Self-Emergence Agent Architecture"): „a **Hidden Markov Model
  (HMM)** that encodes long-term behavioral and cognitive inertia as an **editable
  state-transition matrix**"; die Reflexion „updates the **HMM parameters themselves**".
  → `reflective_agent.HMMInertia` (Repo).
- **AGENTS.md §2** (5 Phasen: Konstrukt, Akt, Observe, Compare, Revise) — Auftrag.

## 2. Phase → echtes Modul (Auftrag)

| # | Phase | echte Funktion |
|---|---|---|
| 1 | Konstrukt (π0) | `reflective_agent.HMMInertia()` (SEAA-π0, K=4) |
| 2 | Akt | `pipeline.route_and_store` (Mandat→FWR→Trust→Write) |
| 3 | Observe | `ingestion_hook.resolve_entities` (Traces/States, keine Wertung) |
| 4 | Compare | `evaluator_version.best_belief` (externes Signal) |
| 5 | Revise | `reflective_agent.HMMInertia.update_from_reflection` (SEAA Eq. 2: Δ aktualisiert P) |

- **Phasenfolge = Auftrag** (gesetzte Ordnung, kein Paper-Claim).
- **SEAA-Kern:** die Reflexion (Phase 5) aktualisiert die **HMM-Übergangsmatrix** selbst —
  nicht nur Text. Ohne gültige Δ-Matrix → **NOOP** (P bleibt).

## 3. Echte Ausgabe (CLI, 2026-10-04)

```text
Konstrukt  K=4 · pi0=uniform (SEAA Listing 1)
Akt        ok=true action=write-new
Observe    entities=[]
Compare    belief=0.3426 (externes Ground-Truth-Signal)
Revise     skipped=false · lr=0.05   (echte Δ-Matrix -> HMM aktualisiert)
```

## 4. Test (echt, Guardrail 7)

`tests/test_recursion_runner.py` (3 Tests): voller Zyklus (Δ-Matrix → HMM-Update), NOOP
(ohne LLM/Δ), Akt-Deny (Mandat-Gate). `recursion_runner.py`: **100 %** Line+Branch.

## 5. Gate (§9)

- Interface-Änderung (neues Modul) → **approved** (Batnini, Auftrag).
- Guardrail 3: Provenienz `ergebnisse/rekursion/057-recursion-runner.md`.
- Guardrail 6: kein Commit ohne Erlaubnis. §9.1b: `AGENTS.md` unverändert.
- **Ehrliche Grenzen:** Phasenfolge + Phase→Modul = **Auftrag**; „Compare" nutzt
  `best_belief` (Beta-Belief) als externes Signal, nicht den vollen Grader-Loop.
