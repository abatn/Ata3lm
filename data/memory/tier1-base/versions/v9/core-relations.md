# Tier 1 – Base Knowledge: Kernbeziehungen

> Schicht: Tier 1 (Base Knowledge) der 3-Schicht-Gedächtnis-Pipeline.
> Quelle (Kanten/Beziehungen): Graphiti (arXiv:2501.13956) – "entities + relationships (edges)".
> Quelle (semantische Baum-Kanten): SHIMI (arXiv:2504.06135) – "each directed edge encodes a parent-child relationship".
> Lab-Prinzip: keine Erfindungen – nur Auftrag + Quellen.

## Kernbeziehungen (typisierte Kanten)

| Subjekt --Relation--> Objekt | Beleg |
|---|---|
| Erfahrung --schreibt--> Working Memory | wissenszyklus-8-stufen.md |
| Working Memory --liest--> Wissen | wissenszyklus-8-stufen.md |
| Wissen --schreibt--> Gedächtnis | wissenszyklus-8-stufen.md |
| Gedächtnis --schreibt--> Ontologie | gedaechtnis.md |
| Ontologie --liest--> Kognition | wissenszyklus-8-stufen.md |
| Kognition --schreibt--> M (Working Memory) | wissenszyklus-8-stufen.md |
| Denken --schreibt--> Self-Feedback (sr) | index.md |
| Handeln --schreibt--> Working Memory | wissenszyklus-8-stufen.md |
| Wissen+ --schreibt--> revidiertes Modell | wissenszyklus-8-stufen.md |

## Konzept-Hierarchie (Tier-1-zu-Tier-2-Kanten)

- `Konzept --parent--> Unterkonzept` (semantische Baumkante)
  → Quelle: SHIMI (arXiv:2504.06135), "parent-child relationship".
- `Fakt --valid_at/invalid_at--> Zeitfenster` (bi-temporale Kante)
  → Quelle: Graphiti (arXiv:2501.13956).

## Quellen

- Graphiti (temporaler Graph, Kanten + Validitätsfenster): https://arxiv.org/abs/2501.13956
- SHIMI (semantische Hierarchie, parent-child): https://arxiv.org/abs/2504.06135
- `knowledge/lifecycle/rekursion/wissenszyklus-8-stufen.md`, `index.md`
