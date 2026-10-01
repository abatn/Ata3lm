# Entität: Solver berechne_durchschnitt

- Ontologie-Bezug: Handeln (7); siehe `data/memory/tier1-base/ontology.md`
- Quelle: `ergebnisse/rekursion/011-t4-rekursion.md`
- Evidence: t=4-Rekursion (π₀=2/4 → π₁=4/4)
- Status: validiert
- Gültigkeit: `gueltig_von: 2026-09-30`, `gueltig_bis: offen`
- Beschreibung: Solver für den Durchschnitt. Bug: Integer-Division `//`.
  Fix: echte Division `/`. Score π₁ = 4/4 (Python-verifiziert).

## Quellen
- https://docs.python.org/3/library/functions.html
