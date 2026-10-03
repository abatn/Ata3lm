# Ladepfad tier2 → tier3 (GAAMA + Validation-Gated Hebbian Learning)

> Datum: 2026-10-03 · Lab-Prinzip §6 (keine Erfindungen) · Human-Gate §9.
> Code: `data/memory/gaama_extract.py` (Extraktion) +
> `data/memory/tier3-working/lru_cache.py` (`hybrid_scores`, `fill_from_graph`,
> `edge_type_aware_ppr`, `validation_gate`, `consolidate_edges`).

## 0. Korrektur der Erfindung (2026-10-03)

Die frühere Funktion `build_concept_graph` erzeugte **Concept↔Concept**-Kanten vom Typ
`ABOUT_CONCEPT` aus „gleichem Ort" — das ist **nicht** GAAMA (`ABOUT_CONCEPT` = Fact→Concept)
und war eine **Erfindung** (§6). Sie ist **entfernt**. Kanten entstehen jetzt
**ausschließlich** aus der Extraktion (`gaama_extract.build_graph`, EdgeSpecs).

## 1. Quellen (verifiziert, siehe `ergebnisse/gaama-schema.md`)

- **GAAMA** arXiv:2603.27910 — 4 Knoten-/5 Kantentypen (Table 1), Gewichte (Table 2),
  Hybrid-Retrieval (Cosine-KNN + edge-type-aware PPR, α=0.6, w_sim=1.0/w_ppr=0.1).
- **Kairos** „Validation-Gated Hebbian Learning for Adaptive Agent Memory"
  (NeurIPS 2025, `ceur-ws.org/Vol-4162/paper4.pdf`, Singh & Yu) — 4 Qualitätsdimensionen
  (logical, grounding, novelty, alignment); novelty **orthogonal** (nicht gemittelt).

## 2. Ladepfad (Code, paper-konform)

```text
episodic_graph.json (Episoden, verbatim)
   └─ gaama_extract.load_episodes()
   └─ gaama_extract.extract_facts_concepts(episodes, llm_fn)   # Step 2 (LLM, injizierbar)
   └─ gaama_extract.extract_reflections(facts, llm_fn)         # Step 3 (LLM)
   └─ gaama_extract.build_graph(...)  -> nodes + edges (NEXT/DERIVED_FROM/HAS_CONCEPT/
                                        ABOUT_CONCEPT/DERIVED_FROM_FACT)  # KEINE Erfindung
   └─ lru_cache.hybrid_scores(query, items, edges)   # Seeds → beidseitig → d=2 → PPR
   └─ WorkingMemory.fill_from_graph(...)  -> Tier 3 (search-before-store)
   └─ gaama_extract.route_extracted_facts(facts)      # §10.1: Fast Write Router zuerst
```

`hybrid_scores` folgt GAAMA §3.4: Seeds = Top-Cosine → **beidseitige** Kanten
(`_bidirectional`) → **Subgraph-Expansion d=2** (`expand_subgraph`) → `edge_type_aware_ppr`
(α=0.6, ≤200 Iter., Table-2-Gewichte, **Hub-Dampening threshold 50**, optional
`degree_correction`) → additiv `w_sim·cos + w_ppr·ppr`. Kanten mit unbekannten
Endpunkten werden übersprungen.

**Hinweis (ehrlich):** Das uniforme Hub-Dampening skaliert alle Ausgangsgewichte eines
Knotens gleich und kürzt sich unter der Per-Source-Normalisierung weg; wirksam ist
GAAMAs `degree_correction` (Endscore ÷ `log(1+degree)`).

## 3. Validation-Gated Consolidation (Kairos)

`validation_gate(dims)` konsolidiert nur, wenn **logical, grounding, alignment ≥ τ** (0.6);
**novelty** getrennt (orthogonal, blockiert nicht). `consolidate_edges()` stärkt bei
bestandener Prüfung `edge_weight` (Hebbian-LTP).

## 4. Test (offline, kein Netz)

`tests/test_gaama_extract.py` (8) + `tests/test_tier2_tier3.py` (10):
- Extraktion mit **Fake-LLM**; Kantenbau (5 Typen, Fallback `DERIVED_FROM`, self-loop/Index verworfen);
- Hybrid-Scores + PPR-Propagation; `fill_from_graph` (5 Knoten → Tier3);
- Validation-Gate (novelty orthogonal); keine Concept↔Concept-Kante.

## 5. Suite-Beleg

```text
make test -> 260 passed · Coverage 100,00 % (Line+Branch) · ruff clean
```

## 6. Write-Kette §9.2c → §9.2a → §10.1 → Write

`gaama_extract.persist_extracted_facts(facts, ...)` ist die **persistente** Kette:
1. **§9.2c** `trust.PoisoningGuard.admit` — nur **trusted origin UND verified** (sonst `rejected`).
2. **§9.2a** `trust.PIIFilter.minimize` — PII entfernen.
3. **§10.1** `route_extracted_facts` — Fast Write Router (erste Instanz).
4. **Write** `fast_write_router.apply_write_action` (injizierbar via `write_fn`).

`classify_fn`/`guard`/`write_fn` sind injizierbar (offline testbar). Der Ladepfad
(Tier2→Tier3, Cache) bleibt davon getrennt.

## 7. Human-Gate §9

- Ersetzen der erfundenen `build_concept_graph` → **approved** (Batnini, 2026-10-03).
- Interface-Änderung (`hybrid_scores`/`fill_from_graph`) → Freigabe erteilt.
- Provenienz: `ergebnisse/rekursion/038-gaama-ladepfad.md`.
