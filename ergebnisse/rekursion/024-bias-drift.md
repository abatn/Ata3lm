# 024 – Bias-Drift-Monitor (Feedback-Schleifen-Kontrolle)

> Datum: 2026-10-01
> Rekursionstiefe: System-Iteration (Governance/Monitoring), nicht Solver-t
> Phase: Konstrukt (neuer Monitor)
> Auslöser: menschlicher Auftrag vom 2026-10-01.

## 1. Zustand vorher / nachher

| | vorher | nachher |
|---|---|---|
| Feedback-Loop-Drift | nicht überwacht | `BiasDriftMonitor` (TV-Distanz, τ) |
| Trigger | – | drift > τ → Flag + Human-Gate |

## 2. Änderungen

- `data/memory/bias_monitor.py` (neu): `BiasDriftMonitor` (total_variation, τ=0.10).
- `ergebnisse/bias-drift.md`.

## 3. Compare-Beleg (externes Signal)

`python3 data/memory/bias_monitor.py` (reale Ausgabe): 10 self_updates;
drift steigt 0.03 → 0.30; ab Schritt 4 (> τ=0.10) **Flag + Human-Gate**;
Report flagged_steps [4..10].

## 4. Quellen (belegt, HTTP 200)

- EU-KI-VO Art. 15(4) (Feedback-Loops, biased outputs → mitigieren):
  https://ai-act-service-desk.ec.europa.eu/en/ai-act/article-15
- VO (EU) 2024/1689: https://eur-lex.europa.eu/eli/reg/2024/1689/oj
- EC-Implementation-Guidance (fairness metrics, thresholds, human oversight):
  https://futurium.ec.europa.eu/system/files/2026-07/Implementation-Guidance-EU-AI-Act_1.pdf

## 5. Abgrenzung (Auftrag)

TV-Distanz als Drift-Maß + τ=0.10 = **Auftrag**; Feedback-Loop-Risiko +
Monitoring-Pflicht = **Belegt**.

## 6. Guardrails

- `AGENTS.md` unverändert; Flag löst Human-Gate aus (kein Auto-Update).

## 7. Freigabe

**Freigabe-Status für π₁:** `pending` (menschliche Freigabe ausstehend).
