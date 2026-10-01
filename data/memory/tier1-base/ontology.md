# Tier 1 – Base Knowledge: Ontologie

> Schicht: Tier 1 (Base Knowledge) der 3-Schicht-Gedächtnis-Pipeline.
> Quelle (semantische Hierarchie): SHIMI (arXiv:2504.06135).
> Quelle (Ontologie + bi-temporal): ARIADNE Tier 2 (arXiv:2105.09864), Graphiti (arXiv:2501.13956).
> Lab-Prinzip: keine Erfindungen – nur Auftrag + Quellen.

## A. Die 8 Stufen (semantische Knoten)

| # | Stufe | Schreib-/Leserichtung |
|---|---|---|
| 1 | Erfahrung | schreibt in Working Memory |
| 2 | Wissen | liest aus Working Memory |
| 3 | Gedächtnis | schreibt in Ontologie |
| 4 | Kognition | liest Ontologie, schreibt M |
| 5 | Denken | schreibt Self-Feedback |
| 6 | Nicht-Kognition | schreibt in Working Memory |
| 7 | Handeln | schreibt Aktion in Working Memory |
| 8 | Wissen+ | schreibt revidiertes Modell zurück |

Quelle: `knowledge/lifecycle/rekursion/wissenszyklus-8-stufen.md`.

## B. Die 5 Phasen (rekursive Kanten)

| Phase | Funktion |
|---|---|
| Konstrukt | baut Modell π aus Ziel g |
| Akt | führt π aus |
| Observe | sammelt Zustand s + Feedback r |
| Compare | vergleicht r mit externem Signal |
| Revise | schreibt (π, I) zurück |

Quelle: `knowledge/lifecycle/rekursion/index.md`.

## C. Ontologie-Grounding (Auftrag + Quelle)

Jeder Knoten trägt (nach ARIADNE Tier 2 / Graphiti):
- **Ontologie-Bezug** (Konzept/URI),
- **Gültigkeitsfenster** (`gueltig_von` / `gueltig_bis`) – bi-temporal,
- **Provenienz** (Episode + Quelle).

Quellen:
- ARIADNE 3-Tier (Tier 2 Semantic, bi-temporale Felder): https://arxiv.org/abs/2105.09864
- Graphiti (Fakten mit Validitätsfenstern): https://arxiv.org/abs/2501.13956
- SHIMI (semantische Hierarchie): https://arxiv.org/abs/2504.06135
