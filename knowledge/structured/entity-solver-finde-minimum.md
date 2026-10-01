# Entität: Solver finde_minimum

- Ontologie-Bezug: Handeln (7); siehe `data/memory/tier1-base/ontology.md`
- Quelle: `ergebnisse/rekursion/012-t5-rekursion.md`
- Evidence: t=5-Rekursion (π₀=2/4 → π₁=4/4)
- Status: validiert
- Gültigkeit: `gueltig_von: 2026-09-30`, `gueltig_bis: offen`
- Beschreibung: Solver für das Minimum. Bug: gibt erstes Element zurück.
  Fix: `min(liste)`. Score π₁ = 4/4 (Python-verifiziert).

## Quellen
- https://docs.python.org/3/library/functions.html#min
