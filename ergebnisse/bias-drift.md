# Bias-Drift-Monitor (Feedback-Schleifen-Kontrolle)

> Datum: 2026-10-01
> Status: **Belegt** (Feedback-Loop-Risiko + Monitoring-Pflicht) + **Auftrag** (Mechanik/τ)
> Prinzip: Keine Erfindungen (§6).
> Code: `data/memory/bias_monitor.py`

## 1. Quellen (verifiziert, HTTP 200)

| Quelle | Kernaussage (wörtlich) | Link |
|---|---|---|
| **EU-KI-VO Art. 15(4)** | „High-risk AI systems that continue to learn … shall be developed in such a way as to eliminate or reduce as far as possible the risk of possibly **biased outputs influencing input for future operations (‘feedback loops’)** … with appropriate mitigation measures." | https://ai-act-service-desk.ec.europa.eu/en/ai-act/article-15 · https://eur-lex.europa.eu/eli/reg/2024/1689/oj |
| **EC-Implementation-Guidance (2026)** | Dokumentation soll „performance and **fairness metrics that will be monitored**, the **thresholds beyond which the system will be halted or rolled back**, and the **human oversight** measures" beschreiben | https://futurium.ec.europa.eu/system/files/2026-07/Implementation-Guidance-EU-AI-Act_1.pdf |

→ Belegt: (a) Feedback-Loops können Bias verstärken → mitigieren; (b) Monitoring
von Fairness-Metriken mit **Schwellen** + Human-Oversight. Die konkrete
Drift-Metrik/τ ist **Auftrag**.

## 2. Ziel & Mechanik

- **Ziel:** Überwachen, wie wiederholte `self_update`-Aufrufe die **Verteilung
  der Entscheidungen** verändern.
- **Drift-Maß:** **Total-Variation-Distanz** (0..1) zwischen Entscheidungs-
  verteilungen (baseline vs. aktuell; zusätzlich Schritt-zu-Schritt).
- **Trigger:** `drift > τ` → **Flag + Human-Gate** (`ask`).
- **τ = 0.10** (Auftrag, konsistent mit AGENTS.md §9.1 Drift-Bound).

## 3. Ablauf

```text
baseline-Verteilung ──┐
                      ▼
self_update #1 ─► observe(dist) ─► drift = TV(dist, baseline)
self_update #2 ─► observe(dist) ─► drift > τ ? ─► ja: FLAG + Human-Gate (ask)
…                                                  nein: ok
```

## 4. Selbsttest (reale Ausgabe) — 10 self_updates

```text
=== Bias-Drift-Monitor: 10 self_update-Aufrufe ===
  Baseline: {'approve': 0.5, 'revise': 0.3, 'reject': 0.2} | tau=0.1
  self_update  1: drift=0.0300 -> ok
  self_update  2: drift=0.0600 -> ok
  self_update  3: drift=0.0900 -> ok
  self_update  4: drift=0.1200 -> ask     ← τ überschritten
  self_update  5: drift=0.1500 -> ask
  ...
  self_update 10: drift=0.3000 -> ask
  Report: {'steps': 10, 'tau': 0.1, 'flagged_steps': [4,5,6,7,8,9,10], 'max_drift': 0.3}
```

**Ergebnis:** Die kumulative Verschiebung durch wiederholte `self_update`s wird
sichtbar; ab **Schritt 4** (drift 0.12 > τ 0.10) greift **Flag + Human-Gate**.

## 5. Status-Trennung

| Aussage | Status |
|---|---|
| Feedback-Loops können Bias verstärken (zu mitigieren) | **Belegt** (Art. 15(4)) |
| Fairness-Metriken + Schwellen + Human-Oversight überwachen | **Belegt** (EC-Guidance) |
| TV-Distanz als Drift-Maß | **Auftrag** |
| τ = 0.10 | **Auftrag** (§9.1) |

## 6. Dateien

| Artefakt | Art |
|---|---|
| `data/memory/bias_monitor.py` | neu (`BiasDriftMonitor`) |
| `ergebnisse/bias-drift.md` | neu (dieses Dokument) |
| `ergebnisse/rekursion/024-*.md` | Provenienz |

## 7. Quellen (HTTP 200, 2026-10-01)

- https://ai-act-service-desk.ec.europa.eu/en/ai-act/article-15 (Art. 15(4))
- https://eur-lex.europa.eu/eli/reg/2024/1689/oj (VO (EU) 2024/1689)
- https://futurium.ec.europa.eu/system/files/2026-07/Implementation-Guidance-EU-AI-Act_1.pdf
