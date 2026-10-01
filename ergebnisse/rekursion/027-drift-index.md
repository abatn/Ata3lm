# 027 – JSD-basierter Drift-Index (ersetzt TV)

> Datum: 2026-10-01
> Rekursionstiefe: System-Iteration (Governance/Monitoring), nicht Solver-t
> Phase: Revise (bias_monitor.py: TV → JSD)
> Auslöser: menschlicher Auftrag vom 2026-10-01. Baut auf 024 auf.

## 1. Zustand vorher / nachher

| Aspekt | vorher (024) | nachher (027) |
|---|---|---|
| Metrik | `total_variation` | **JSD** (Jensen-Shannon) |
| Aggregation | einfache Summe | **entropie-gewichtet + Capped Simplex (w_max=0.6)** |
| Damping | – | **Lyapunov-bounded** |

## 2. Änderungen

- `data/memory/bias_monitor.py`: `jsd()`, `entropy()`, `capped_simplex()`; DI = JSD;
  entropie-gewichtete Kategorie-Signale; Damping.
- `ergebnisse/drift-index.md`.

## 3. Compare-Beleg (externes Signal)

`python3 data/memory/bias_monitor.py` (reale Ausgabe): 10 self_updates;
DI(JSD) 0.0006 → 0.0731; ab Schritt 6 (> τ=0.02) Flag + Human-Gate;
Gewichte im Capped Simplex (≤ 0.6); Damping monoton fallend.

## 4. Quellen (belegt, HTTP 200)

- WhyLab – Causal Audit Framework (2026): C1 Drift Index, C3 Lyapunov-bounded damping:
  https://github.com/neogenesislab/WhyLab-NeurIPS2026
- Agent Drift (arXiv:2601.04170): JSD zur Drift-Messung.
- EU-KI-VO Art. 15(4): Feedback-Loops: https://ai-act-service-desk.ec.europa.eu/en/ai-act/article-15

## 5. Abgrenzung (Auftrag)

Entropie-Gewichtung, `w_max=0.6`, τ=0.02 = **Auftrag**; JSD-Drift + Lyapunov-Damping
= **Belegt** (WhyLab/Agent Drift).

## 6. Guardrails

- `AGENTS.md` unverändert; Flag löst Human-Gate aus (kein Auto-Update).

## 7. Freigabe

**Freigabe-Status für π₁:** `approved: Batnini, 2026-10-01`.
