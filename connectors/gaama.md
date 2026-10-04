# GAAMA – Connector (Graph-Augmented Associative Memory)

## Titel
GAAMA: Graph Augmented Associative Memory for Agents (+ Validation-Gated Hebbian Learning)

## Quellen
- **GAAMA:** arXiv:2603.27910 – https://arxiv.org/abs/2603.27910 (Code: https://github.com/swarna-kpaul/gaama)
- **Kairos** (Validation-Gated Hebbian Learning for Adaptive Agent Memory): NeurIPS 2025 –
  https://nips.cc/virtual/2025/129852 · OpenReview https://openreview.net/forum?id=EN9VRTnZbK ·
  CEUR-WS https://ceur-ws.org/Vol-4162/paper4.pdf

## Kernfunktion
GAAMA baut einen konzept-vermittelten Wissensgraphen (**4 Knotentypen**: episode, fact,
reflection, concept) mit **5 strukturellen Kantentypen** (NEXT, DERIVED_FROM,
DERIVED_FROM_FACT, HAS_CONCEPT, ABOUT_CONCEPT). Retrieval kombiniert **Cosine-KNN** mit
**edge-type-aware Personalized PageRank** additiv:

```text
score(n) = w_sim · sim(n, q) + w_ppr · ppr(n)      (Paper-Defaults: w_sim=1.0, w_ppr=0.1, α=0.6)
Kantengewichte (Table 2): NEXT 0.8 · DERIVED_FROM 0.8 · DERIVED_FROM_FACT 0.5 · HAS_CONCEPT 0.8 · ABOUT_CONCEPT 0.8
```

**Kairos** ergänzt: **Validation-Gated Learning** – Graph-Konsolidierung (Hebbian-LTP:
edge strengthening, temporal decay, emergent connections) nur, wenn die
Multi-Dimension-Qualitätsprüfung (**logical, grounding, novelty, alignment**) besteht.
Befund: **novelty ist orthogonal** zu Korrektheit (nicht mit Qualität mitteln).

## Integration in den Knowledge-Agenten

| Stufe | Anwendung | Code |
|---|---|---|
| Gedächtnis (3) | Ladepfad tier2 → tier3: Extraktion → Graph → Hybrid-Retrieval | `gaama_extract.py` + `lru_cache.fill_from_graph` |
| Gedächtnis (3) | Validation-Gated Konsolidierung (LTP) | `lru_cache.consolidate_edges` |
| Kognition (4) | Nachbar-Boost über typisierte Kanten (PPR) | `lru_cache.edge_type_aware_ppr` |

**Kanten nur aus Extraktion (keine Erfindung):** `gaama_extract.build_graph` erzeugt die
5 Kantentypen aus den Extraktions-Ergebnissen (EdgeSpecs) — **nicht** aus Datei-Orten.
Die frühere „gleicher Ort"-Regel (`build_concept_graph`) wurde 2026-10-03 entfernt (§6).

**Paper-Mechanik:** beidseitige Kanten + **Subgraph-Expansion d=2** + **Hub-Dampening 50**
(`degree_correction`) + additive Bewertung. **§10.1:** `route_extracted_facts` schickt
extrahierte Facts zuerst durch den Fast Write Router. **Write-Kette:**
`persist_extracted_facts` = §9.2c (verified) → §9.2a (PII) → §10.1 (FWR) → Write.

## Dokumentation + Test
- Doku: `ergebnisse/tier2-tier3.md`, Beleg: `ergebnisse/gaama-schema.md`
- Test: `tests/test_gaama_extract.py` (Extraktion/Kanten) + `tests/test_tier2_tier3.py`
  (Hybrid, PPR, `fill_from_graph`, Validation-Gate)


## Prozess (Aufruf) [Auftrag]

Dieser Connector bedient: `lru_cache.py` — Ladepfad tier2→tier3 (Hybrid-Retrieval).

MCP-Interface / Ontologie-Validierung (SHACL, W3C): https://www.w3.org/TR/shacl/ · `ergebnisse/connector-prozess.md`.
