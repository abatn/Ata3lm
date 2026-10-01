# Connector: Consistency Gap (ReAct auf AppWorld)

> Lab-Prinzip, MD-first. Alle Zahlen nur zitiert, nicht selbst gemessen.

## Identität

- Paper: Duesterwald, Elder, Ngweta, Ubaru, Zimon (2026): Closing the
  Consistency Gap – https://arxiv.org/abs/2609.08832 (8. Sep 2026)
- Praxis: IBM Research / Hugging Face, ALTK-Evolve Consistency –
  https://huggingface.co/blog/ibm-research/altk-evolve-consistency
- Benchmark: AppWorld `test_normal`, 168 Tasks (via Paper referenziert:
  Trivedi et al. 2024 – keine Eigenbehauptung zu Benchmark-Details)
- Agent: ReAct (Yao et al. 2023, https://arxiv.org/abs/2210.03629) + GPT-4.1

## Mechanismus (aus Quellen abgeschrieben)

- Metriken: Mean@k (Mittel), Pass@k (≥1 von k, optimistisch),
  Pass^k (alle k, pessimistisch); Pass^k ≤ Mean@k ≤ Pass@k;
  Gap = Mean@k − Pass^k; normalized Consistency@k = Pass^k/Mean@k.
- Befund: Mean@5 77.4 %, Pass^5 53.0 % → Gap 24.4 pp (Hard bis ~30 pp).
- Consistency Analyzer: 1 Trace, kein Ground Truth, kein Replay –
  pro Entscheidungsschritt 1 Zusatz-Call mit k Completions (Default 5),
  Black-Box, Scorecard flip-anfälliger Schritte → Guideline-Generator →
  episodisches Memory.
- Wirkung (zitiert): Pass^5 53.0 % → 69.0 % (+16.0 pp same-task,
  +13.0 pp similar-task), Mean@5 77.4 % → 81.0 %, Gap → 12.0 pp.
- Lehre: Konsistenz ⊥ Capability; Pass^k neben Mean@k berichten.

## Mapping auf Compare

| Compare | Beleg |
|---|---|
| Ähnlichkeit/Konsistenz | Pass@k vs. Pass^k + Gap-Tabelle |
| Externes Signal | AppWorld-Grader (belegt); Code-Run/DB als geforderte Signaltypen (Auftrag + Eltern-Guardrail, keine Paper-Behauptung) |
| Flip-Diagnose | Consistency Analyzer (Resampling-Logik) |

## Grenzen (aus Quellen übernommen)

- Alle Zahlen: 1 Benchmark-Slice (test_normal), 1–2 Modelle – keine
  Produktions- oder Fremd-Benchmark-Behauptung.
- Analyzer-Kosten: 1 Extra-Call pro Entscheidungsschritt (Gesamtkosten je
  nach Schrittlänge – im Blog nicht beziffert, hier nicht erfunden).

## Quellen

- https://arxiv.org/abs/2609.08832
- https://huggingface.co/blog/ibm-research/altk-evolve-consistency
- https://arxiv.org/abs/2210.03629
