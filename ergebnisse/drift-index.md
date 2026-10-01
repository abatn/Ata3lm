# JSD-basierter Drift-Index (DI)

> Datum: 2026-10-01
> Status: **Belegt** (JSD-Drift + Lyapunov-Damping) + **Auftrag** (Gewichtung/τ/w_max)
> Prinzip: Keine Erfindungen (§6).
> Code: `data/memory/bias_monitor.py`

## 1. Quellen (verifiziert, HTTP 200)

| Quelle | Kernaussage | Link |
|---|---|---|
| **WhyLab – A Causal Audit Framework for Stable Agent Self-Improvement** (2026) | drei Verteidigungen: **C1 information-theoretic drift detection (Drift Index)**, C2 E-value × Sensitivitätsfilter, **C3 Lyapunov-bounded adaptive damping** | https://github.com/neogenesislab/WhyLab-NeurIPS2026 |
| **Agent Drift** (arXiv:2601.04170) | **Jensen-Shannon-Divergenz** zur Drift-Messung (Agent Stability Index) | https://arxiv.org/abs/2601.04170 |
| **EU-KI-VO Art. 15(4)** | biased outputs → Feedback-Loops → mitigieren; EC-Guidance: fairness metrics + thresholds + human oversight | https://ai-act-service-desk.ec.europa.eu/en/ai-act/article-15 |

## 2. Was ersetzt wurde

| vorher | nachher |
|---|---|
| `total_variation` (TV) | **`jsd()` – Jensen-Shannon-Divergenz** (Basis 2, [0,1]) |
| einfache Summe | **entropie-gewichtete Signal-Aggregation** + **Capped Simplex** |

## 3. Mechanik

- **DI = JSD(current, reference)** — informationstheoretischer Drift-Index (ersetzt TV).
- **Entropie-gewichtete Signale:** pro Kategorie `|Δp_k|`; Gewicht `w_k ∝` Entropie-Beitrag
  `-p_ref(k)·log2 p_ref(k)` (Kategorien mit höherer Referenz-Entropie wiegen mehr).
- **Capped Simplex:** `w_max = 0.6` — kein Einzelsignal > 0.6 (Projektion auf
  `{Σw=1, 0≤w_i≤0.6}`).
- **Lyapunov-bounded adaptive damping:** `damping = max(0, 1 − 10·DI)` (WhyLab C3).
- **Trigger:** `DI > τ` → Flag + Human-Gate (τ = 0.02, Auftrag für den JSD-Bereich).

## 4. Selbsttest (reale Ausgabe) — 10 self_updates

```text
=== JSD-basierter Drift-Index: 10 self_update-Aufrufe ===
  Baseline: {'approve':0.5,'revise':0.3,'reject':0.2} | tau=0.02 | w_max=0.6
  self_update  1: DI(JSD)=0.0006 weighted=0.0202 damping=0.994 -> ok
  self_update  2: DI(JSD)=0.0026 weighted=0.0403 damping=0.974 -> ok
  self_update  3: DI(JSD)=0.0059 weighted=0.0605 damping=0.941 -> ok
  self_update  4: DI(JSD)=0.0106 weighted=0.0807 damping=0.894 -> ok
  self_update  5: DI(JSD)=0.0167 weighted=0.1008 damping=0.833 -> ok
  self_update  6: DI(JSD)=0.0243 weighted=0.1210 damping=0.757 -> ask   ← τ überschritten
  ...
  self_update 10: DI(JSD)=0.0731 weighted=0.2016 damping=0.269 -> ask
  Report: {'flagged_steps':[6,7,8,9,10], 'max_DI':0.0731}
  Gewichte (capped simplex): {'approve':0.337,'revise':0.351,'reject':0.313}  (alle ≤ 0.6)
```

**Ergebnis:** Der JSD-DI steigt mit der kumulativen Verschiebung; ab **Schritt 6**
(DI 0.024 > τ 0.02) greift **Flag + Human-Gate**; Entropie-Gewichte bleiben im
Capped Simplex (≤ 0.6); Damping fällt monoton (Lyapunov-bounded).

## 5. Status-Trennung

| Aussage | Status |
|---|---|
| Information-theoretischer Drift-Index (C1) | **Belegt** (WhyLab) |
| Lyapunov-bounded adaptive damping (C3) | **Belegt** (WhyLab) |
| JSD zur Drift-Messung | **Belegt** (Agent Drift) |
| Entropie-Gewichtung, `w_max=0.6`, τ=0.02 | **Auftrag** |

## 6. Dateien

| Artefakt | Art |
|---|---|
| `data/memory/bias_monitor.py` | erweitert (JSD, Entropie-Gewichte, Capped Simplex) |
| `ergebnisse/drift-index.md` | neu (dieses Dokument) |
| `ergebnisse/rekursion/027-*.md` | Provenienz |

## 7. Quellen (HTTP 200, 2026-10-01)

- https://github.com/neogenesislab/WhyLab-NeurIPS2026 (Causal Audit Framework)
- https://arxiv.org/abs/2601.04170 (Agent Drift)
- https://ai-act-service-desk.ec.europa.eu/en/ai-act/article-15 (EU-KI-VO Art. 15(4))
