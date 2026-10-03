# Rekursion 037: Ladepfad tier2 → tier3 (GAAMA-Hybrid + Validation-Gate)

> Datum: 2026-10-03 · Tiefe: `t=36 → t=37` · Phase: **Revise → Handeln → Wissen+**
> Freigabe: `approved: Batnini, 2026-10-03` (Auftrag „Schließe den Ladepfad tier2 → tier3 … Human-Gate §9").
> Ziel `g`: Hybrid-Retrieval (Cosine + edge-type-aware PPR) lädt aus `concept-index.md`
> in Tier 3; Graph-Konsolidierung nur validierungs-gated.

## 1. Quellen (verifiziert, HTTP 200)

- **GAAMA** arXiv:2603.27910 — 4 Knoten-/5 Kantentypen (Table 1), Hybrid-Retrieval
  (Cosine-KNN + edge-type-aware PPR, Gl. 4–5), Kantengewichte (Table 2).
- **Kairos** „Validation-Gated Hebbian Learning for Adaptive Agent Memory", NeurIPS 2025
  (`nips.cc/virtual/2025/129852`, OpenReview `EN9VRTnZbK`) — 4 Qualitätsdimensionen
  (logical, grounding, novelty, alignment); novelty orthogonal.

## 2. Änderung (Diff, additiv)

| Datei | Änderung |
|---|---|
| `data/memory/tier3-working/lru_cache.py` | + `parse_concept_index`, `build_concept_graph`, `edge_type_aware_ppr`, `hybrid_scores`, `validation_gate`, `fill_from_tier2`, `consolidate_edges` |
| `tests/test_tier2_tier3.py` | **neu**: 10 Tests (5 Konzepte → Tier3, PPR, Gate) |
| `ergebnisse/tier2-tier3.md` | **neu**: Quellen, Ladepfad, Gate, Simulation |
| `connectors/gaama.md` | **neu**: Connector |
| `data/memory/README.md`, `tests/README.md`, `ergebnisse/verbindungen-diagramm.md` | nachgezogen |
| `AGENTS.md` (Connector-Tabelle) + `versions/v7/` | neue Quelle registriert (§9.1b Snapshot) |

Bestehende Aufrufer unverändert (kein Interface-Bruch).

## 3. Compare-Beleg (extern)

```text
make test -> 244 passed · Coverage 100,00 % (Line+Branch) · ruff clean
Simulation: 10 Konzepte, top-5 geladen in Tier3 (8 Stufen, 5 Phasen, Kernbeziehungen, Lifecycle-Phasen, Identität/Rolle)
```

**Drift:** additiv (neue Funktionen + Doku); ≤ Drift-Bound (10 %).

## 4. Gate (§9)

- Neue Quelle (GAAMA, Kairos) → **approved** (Batnini, 2026-10-03, Auftrag + Quellenprüfung).
- Validation-Gate: Konsolidierung nur bei `logical ∧ grounding ∧ alignment ≥ τ`;
  `novelty` getrennt (orthogonal), blockiert nicht.
- §9.1b: `AGENTS.md` geändert → Snapshot `versions/v7/`.
- §9.3-Zwei-Personen: Record `ergebnisse/fwr-code-korrektur.md` §0 (offen: 2. Person).

## 5. Nächstes Self-Feedback (t+1)

- Optional: `pipeline.load_from_tier2` auf `fill_from_tier2` (Hybrid) umstellen —
  Interface-Änderung → Freigabe nötig.
