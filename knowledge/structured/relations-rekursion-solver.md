# Relationen: Rekursion → Solver (mit Gültigkeit)

- Ontologie-Bezug: Kernbeziehungen; siehe `data/memory/tier1-base/core-relations.md`
- Quelle: `ergebnisse/rekursion/011..013-*.md`
- Evidence: Rekursions-Historie t=4, t=5, t=6
- Status: validiert

| Subjekt --Relation--> Objekt | Gültigkeit | Quelle |
|---|---|---|
| t=4 --produces--> Solver berechne_durchschnitt | gueltig_von: 2026-09-30, bis: offen | `011-t4-rekursion.md` |
| t=5 --produces--> Solver finde_minimum | gueltig_von: 2026-09-30, bis: offen | `012-t5-rekursion.md` |
| t=6 --produces--> Solver berechne_median | gueltig_von: 2026-10-01, bis: offen | `013-t6-rekursion.md` |
| Solver berechne_median --supersedes--> Solver berechne_durchschnitt | gueltig_von: 2026-10-01 | t=6 (Ablösung) |

**Supersede-Regel (Quelle: Graphiti, arXiv:2501.13956):** alte Fakten werden
**invalidiert, nicht gelöscht** (`valid_at`/`invalid_at`).

## Quellen
- Graphiti (bi-temporale Kanten): https://arxiv.org/abs/2501.13956
- Neo4j Meta-Knowledge-Graph (Knoten-Keying): https://github.com/neo4j-labs/meta-knowledge-graph
