# Entität: Solver berechne_median

- Ontologie-Bezug: Handeln (7); siehe `data/memory/tier1-base/ontology.md`
- Quelle: `ergebnisse/rekursion/013-t6-rekursion.md`
- Evidence: t=6-Rekursion (π₀=2/4 → π₁=4/4), MCPs: HeLa-Mem, MARS, Graphiti
- Status: validiert
- Gültigkeit: `gueltig_von: 2026-10-01`, `gueltig_bis: offen`
- Beschreibung: Solver für den Median. Bug: mittleres Element der unsortierten Liste.
  Fix: erst `sorted()`, dann Median (Mittelwert bei gerader Länge). Score π₁ = 4/4.

## Quellen
- https://docs.python.org/3/library/functions.html#sorted
