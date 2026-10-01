# inference-001 — bi-temporale Invalidierung (Graphiti-Supersede)

```text
Regel-ID:     R1
Regel:        Supersede-Regel (Graphiti, bi-temporale Kanten):
              Wenn  X --supersedes--> Y  und  X.gueltig_von = d,
              dann  Y --invalid_at--> d.
Input-Triples:
  - Solver berechne_median --supersedes--> Solver berechne_durchschnitt
    (Quelle: knowledge/structured/relations-rekursion-solver.md;
     https://arxiv.org/abs/2501.13956)
  - Solver berechne_median . gueltig_von = 2026-10-01
    (Quelle: knowledge/structured/entity-solver-berechne-median.md)
Output-Triples:
  - Solver berechne_durchschnitt --invalid_at--> 2026-10-01   (neu materialisiert)
Quelle:       https://arxiv.org/abs/2501.13956 (Graphiti, bi-temporale Kanten)
Status:       belegt
```

## Prämissen → Konklusion

Prämissen:
- P1: `Solver berechne_median --supersedes--> Solver berechne_durchschnitt`
  (Quelle: `knowledge/structured/relations-rekursion-solver.md`, t=6-Ablösung;
  https://arxiv.org/abs/2501.13956)
- P2: `Solver berechne_median` `gueltig_von: 2026-10-01`
  (Quelle: `knowledge/structured/entity-solver-berechne-median.md`)

Konklusion:
- K: `Solver berechne_durchschnitt --invalid_at--> 2026-10-01`
  (via: Supersede-Regel R1 / Graphiti)

Status: **belegt** (beide Prämissen mit Quellen-Link; Regel aus Graphiti).

## Inferenz-Schicht-Bezug

- Inferenz (Regel R1) materialisiert ein **neues Triple** (`invalid_at`), das im
  expliziten Graph nicht steht. Erst danach ist es für SHACL prüfbar.
- Vgl. `ergebnisse/inferenz-shacl.md` (Inferenz vor Validierung).
