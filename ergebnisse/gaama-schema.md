# GAAMA-Schema (Beleg) – Knoten, Kanten, PPR, Extraktion

> Datum: 2026-10-03 · Phase: **Observe/Belegen** (§1, §6) · **Kein Code geändert.**
> Zweck: Das GAAMA-Schema **wörtlich** aus Paper **und** Code dokumentieren, damit die
> Korrektur des Ladepfads (tier2 → tier3) **nicht** auf Erfindungen beruht.
> Methode: Repo-Dateien direkt gelesen (rohe URLs), Stand Commit
> `2d992f7f7b97c802bfe4c799878a5477cac1b6ff`.

## 0. Quellen (verifiziert)

| Quelle | Link |
|---|---|
| Paper | https://arxiv.org/abs/2603.27910 · HTML https://arxiv.org/html/2603.27910v2 |
| Repo | https://github.com/swarna-kpaul/gaama |
| `core/types.py` | https://raw.githubusercontent.com/swarna-kpaul/gaama/main/core/types.py |
| `services/pagerank.py` | https://raw.githubusercontent.com/swarna-kpaul/gaama/main/services/pagerank.py |
| `services/graph_edges.py` | https://raw.githubusercontent.com/swarna-kpaul/gaama/main/services/graph_edges.py |
| `services/interfaces.py` | https://raw.githubusercontent.com/swarna-kpaul/gaama/main/services/interfaces.py |
| `services/llm_extractors.py` | https://raw.githubusercontent.com/swarna-kpaul/gaama/main/services/llm_extractors.py |
| `services/ltm_retriever.py` | https://raw.githubusercontent.com/swarna-kpaul/gaama/main/services/ltm_retriever.py |
| `services/defaults.py` | https://raw.githubusercontent.com/swarna-kpaul/gaama/main/services/defaults.py |
| `prompts/fact_generation.md` | https://raw.githubusercontent.com/swarna-kpaul/gaama/main/prompts/fact_generation.md |
| `prompts/reflection_generation.md` | https://raw.githubusercontent.com/swarna-kpaul/gaama/main/prompts/reflection_generation.md |

## 1. Knoten- und Kantentypen (wörtlich, `core/types.py`)

```python
ALLOWED_NODE_KINDS = frozenset({"entity", "fact", "episode", "reflection", "skill", "concept"})
ALLOWED_EDGE_TYPES = frozenset({
    "NEXT", "DERIVED_FROM", "DERIVED_FROM_FACT",
    "HAS_CONCEPT", "ABOUT_CONCEPT",
})
```

- **5 Kantentypen** — exakt wie im Paper (Table 1).
- **Knoten:** Paper nennt **4** (episode, fact, reflection, concept); der Code listet
  **6** (`entity`, `skill` zusätzlich). → **Ehrliche Abweichung** Paper↔Code.
- Kantenrichtung (Paper Table 1): `NEXT` Episode→Episode · `DERIVED_FROM` Fact→Episode ·
  `DERIVED_FROM_FACT` Reflection→Fact · `HAS_CONCEPT` Episode→Concept ·
  `ABOUT_CONCEPT` Fact→Concept. **Es gibt keinen Concept→Concept-Typ.**

## 2. PPR (wörtlich, `services/pagerank.py`)

```python
DEFAULT_EDGE_TYPE_WEIGHTS = {
    "HAS_CONCEPT": 0.8, "ABOUT_CONCEPT": 0.8, "NEXT": 0.8,
    "DERIVED_FROM": 0.8, "DERIVED_FROM_FACT": 0.5,
}
_DEFAULT_EDGE_TYPE_FALLBACK = 0.5

def personalized_pagerank(seed_weights, edges, *, alpha=0.85, max_iterations=200,
                          tolerance=1e-6, degree_correction=False):
```

- **α-Diskrepanz (ehrlich):** **Paper §3.4: α = 0.6**; **Code-Default: α = 0.85.**
- Max-Normalisierung auf `[0,1]`; `degree_correction=False` (optional `r/log(1+deg)`).
- `edges_from_core_edges(..., hub_dampening_threshold=50)`:
  - effektives Gewicht `w = base_w · (stored_w ** 2)` (Stored-Gewicht **quadriert**),
  - **jede Kante wird in BEIDE Richtungen** eingefügt (`(src,tgt)` und `(tgt,src)`),
  - **Hub-Dampening:** Grad > 50 → ausgehende Gewichte × `50/deg`,
  - danach Per-Source-Normalisierung (row-stochastic).

## 3. Extraktion (wörtlich, Prompts + `llm_extractors.py`)

**Facts+Concepts** (`fact_generation.md`), Ausgabe JSON:
- Facts: `fact_text` (required), `belief` (0–1), `source_episode_ids` (required), `concepts` (required).
- Concepts: `concept_label` (2–5 Wörter, snake_case), `episode_ids` (required).
- Regeln (wörtlich): atomare Claims; keine Duplikate; relative Daten absolut auflösen;
  1–3 Concepts pro Episode; keine Personennamen/generische Wörter/Adjektive/Daten;
  bestehende Concepts wiederverwenden.

**Reflections** (`reflection_generation.md`), Ausgabe JSON:
- `reflection_text` (required), `belief` (0–1), `source_fact_ids` (required);
  synthetisiert aus **mehreren** Facts; darf leer sein.

**Extraktor** (`LLMFactExtractor` / `LLMReflectionExtractor`):
- Kontext-Budget 2000 Wörter (Facts: 35 % neue Episoden / 25 % verwandte / 25 % Facts / 15 % Concepts;
  Reflections: 40/30/30), JSON-Retry (2×), Markdown-Fences werden entfernt.

**Kantenbau** (`graph_edges.py`): `build_edges_from_nodes(nodes, edge_specs)` aus
`EdgeSpec(source_index, target_index, edge_type, label)` (`services/interfaces.py`);
`_normalize_edge_type` → Großbuchstaben, **unbekannt ⇒ `DERIVED_FROM`**.

## 4. Retrieval-Implementierung (wörtlich, `services/ltm_retriever.py`)

```python
NODE_KNN_K = 40;  LAMBDA = 0.01;  GEL_BELIEF = 1.0
NodeKNNPageRankRetrievalEngine(..., node_knn_k=40, ppr_alpha=0.6,
                               ppr_max_iterations=100, expansion_depth=1)
```

Ablauf (`retrieve`):
1. KNN über `2 × budget` (mind. `2 × 40`) Nodes.
2. Seeds = Top-`40` nach Similarity; `seeds` normalisiert.
3. Graph-Expansion ab Seeds (`expansion_depth=1`).
4. Fehlende Graph-Knoten nachladen; Similarity für graph-entdeckte Knoten nachrechnen.
5. `edges_from_core_edges(...)` → `personalized_pagerank(seeds, edges, alpha=0.6, max_iterations=100, ...)`.
6. **Additive Bewertung:** PPR und Sim je max-normalisiert, dann
   `score = ppr_score_weight·ppr + sim_score_weight·sim`, danach `× _belief_weight`
   (GEL-Knoten `GEL_BELIEF=1.0`, sonst `1.0`).
7. Budget je Kind (`max_facts/reflections/skills/episodes`), Episoden chronologisch.

**Default-Gewichte (Code):** wenn Optionen fehlen → **`ppr_score_weight = 1.0`,
`sim_score_weight = 1.0`** (gleichgewichtet). Paper §3.4 nennt `w_ppr=0.1`, `w_sim=1.0`.
**Semantic-only:** `score = sim · belief` (kein PPR/Graph). **Hybrid:** semantische Basis +
selektive PPR-Same-Type-Upgrades (`hybrid_fusion` `rrf`|`max_score`).

`services/defaults.py` (wörtlich): nur `DefaultTraceNormalizer` (Identität) und
`SimpleEvaluator` (**Stub**, leeres `EvalReport`) — **enthält keine Scoring-Gewichte.**

## 5. Kanonische Paper-Werte (wir folgen dem Paper)

| Parameter | Paper-Wert | Quelle |
|---|---|---|
| PPR-Damping `α` | **0.6** | GAAMA §3.4 (Gl. 4) |
| Score-Gewichte | **`w_ppr = 0.1`, `w_sim = 1.0`** | GAAMA §3.4 (Gl. 5) |
| Kantengewichte | NEXT 0.8 · DERIVED_FROM 0.8 · DERIVED_FROM_FACT 0.5 · HAS_CONCEPT 0.8 · ABOUT_CONCEPT 0.8 | GAAMA Table 2 |
| Expansion-Tiefe | **d = 2** | GAAMA §3.4 (Step 2) |
| PPR-Iterationen | bis **200** (Toleranz 1e-6) | GAAMA §3.4 |
| Knoten / Kanten | 4 Knoten (episode, fact, reflection, concept) / 5 Kanten | GAAMA Table 1 |

**Unser Stand (`lru_cache.py`):** `GAAMA_ALPHA=0.6` ✓ · `GAAMA_W_SIM=1.0` ✓ ·
`GAAMA_W_PPR=0.1` ✓ · `GAAMA_EDGE_WEIGHTS` = Table 2 ✓ · `edge_type_aware_ppr(iters=200)` ✓.
→ Die Werte sind bereits **paper-konform**; die Expansion-Tiefe **d=2** ist noch nicht
implementiert (unsere Graph-Kanten stammen aus dem Index, nicht aus Expansion).

## 6. Status / Grenzen (ehrlich)

- **Belegt:** 5 Kantentypen, Kantengewichte, Extraktions-Schema (Facts/Concepts/Reflections),
  PPR-Mechanik (α, Iterationen, beidseitige Kanten, Gewicht², Hub-Dampening 50),
  Retrieval-Pipeline + additive Bewertung (`ltm_retriever.py`).
- **Paper ↔ GAAMA-Code (Abweichungen nur im GAAMA-Repo, nicht bei uns):**
  1. Knoten: Paper **4** vs. Repo-Code **6** (`entity`, `skill` zusätzlich).
  2. α: Paper **0.6**; `pagerank.py`-Funktionsdefault **0.85**, aber `ltm_retriever.py`
     übergibt **0.6** → effektiv Paper-Wert.
  3. Gewichte: Paper `0.1 / 1.0`; Repo-Code-Default **1.0 / 1.0**.
  4. Expansion-Tiefe: Paper **2**; Engine-Default **1**.
  5. PPR-Iterationen: Paper **200**; Engine **100**.
- **Kairos-PDF verifiziert:** Titel „Validation-Gated Hebbian Learning for Adaptive Agent
  Memory", Pragya Singh & Stanley Yu (UPenn), `ceur-ws.org/Vol-4162/paper4.pdf` (S. 1) —
  4 Dimensionen (logical, grounding, novelty, alignment) wörtlich bestätigt.
- **Kein Produktionscode geändert.** Nächster Schritt (nach Freigabe): Korrektur des
  Ladepfads gemäß Schema (§10.1 FWR, §9 Gate, §9.1c/d Drift/Proposal), Werte = Paper.

## 7. Umsetzung (2026-10-03, `approved` Batnini)

- **Erfindung entfernt:** `build_concept_graph` („gleicher Ort") gelöscht.
- **Neu:** `data/memory/gaama_extract.py` (Facts/Concepts/Reflections + 5 Kantentypen,
  LLM injizierbar) und `lru_cache.fill_from_graph` (Hybrid: Cosine + PPR, Paper-Werte).
- **Paper-Mechanik ergänzt:** beidseitige Kanten (`_bidirectional`), **Subgraph-Expansion
  d=2** (`expand_subgraph`), **Hub-Dampening 50** + `degree_correction` (GAAMA-wörtlich).
- **§10.1:** `gaama_extract.route_extracted_facts` schickt extrahierte Facts zuerst durch
  den Fast Write Router (injizierbar).
- **§9.2c/a + §10.1 (Write-Kette):** `gaama_extract.persist_extracted_facts`
  (PoisoningGuard → PII → FWR → Write).
- Provenienz: `ergebnisse/rekursion/038-gaama-ladepfad.md`, `039-…`, `040-…`; Test: 262 passed, 100 %.
