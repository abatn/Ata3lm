# 005 – Compare-Unterphase eingebaut (Docs, keine Code-Änderung)

- Datum: 2026-09-30
- Rekursionstiefe: `t=0.C` (Strukturerweiterung, noch kein `self_update`)
- Phasen: Compare (Pass@k vs. Pass^k, Consistency Gap; nur externe Signale)
- Zustand `(π, I, M)`: unverändert; `M` erweitert um
  `knowledge/lifecycle/rekursion/compare.md`,
  `skills/recursive-improve/compare/SKILL.md`,
  `connectors/consistency-gap.md`
- Observe: arXiv-Abstract + HTML-Volltext (Metriken, AppWorld-Zahlen,
  Analyzer) + HF-Blog gelesen.
- Compare: Quellen per HTTP verifiziert (arXiv 2609.08832, HF-Blog 200 OK).
  Alle Zahlen (77.4 % / 53.0 % / 24.4 pp → 12.0 pp) als Zitate
  gekennzeichnet, nicht selbst gemessen. Code-Ausführung/DB als geforderte
  Signaltypen (Auftrag + Guardrail) markiert – Paper-Beleg ist der
  AppWorld-Grader.
- Revise: keine Code-Revision (nur Docs).
- Quelle:
  - https://arxiv.org/abs/2609.08832
  - https://huggingface.co/blog/ibm-research/altk-evolve-consistency
  - https://arxiv.org/abs/2210.03629
- Freigabe: `approved: Batnini, 2026-09-30, Grund: Alle Connectoren sind in den 3 Kern-Dateien integriert; Cross-Referenz-Test bestanden.`
- **Korrigierte Verankerung (keine 1:1):** Aus `wissenszyklus-8-stufen.md:110-119`:
  Stufe 8 Wissen+ = Compare + Revise; Stufe 1 Erfahrung = Observe + Akt-Obs; Stufe 4 Kognition = Observe + Akt-Relate.
- Self-Feedback für `t+1`: erstes echtes Compare (k/n/Grader fixieren)
  erst nach Freigabe + Referenz starten.
