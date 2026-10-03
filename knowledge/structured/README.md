# knowledge/structured/ — Ablage für strukturiertes Wissen (Stufe 2: WISSEN)

> Lab-Prinzip MD-first. Kennzeichnung: **[Auftrag]** = Auftragsvorgabe,
> **[Quelle]** = quellenbelegt (siehe Quellen unten).
> Status dieser Ablage: **[Auftrag]** angelegt, wartet auf t=1
> (noch keine Wissenseinheiten enthalten).

## Konvention: Entitäts-Format

**[Auftrag]** Jede Entitäts-Datei in `knowledge/structured/` folgt diesem Format:

```markdown
# Entität: <Name>

- Ontologie-Bezug: <Konzept/URI> (Pflicht)
- Quelle: <Herkunft, z. B. Working-Memory-Trace> (Pflicht)
- Evidence: <Evidence-Link auf Working Memory> (Pflicht)
- Status: <z. B. vorgeschlagen / validiert / rejected>
- Beschreibung: <kurz, nur Auftrags- oder quellenbelegt>
```

## Konvention: Relations-Format

**[Auftrag]** Jede Relation wird als typisierte Kante zwischen zwei
Entitäten dokumentiert:

```markdown
# Relation: <Subjekt> --<Relationstyp>--> <Objekt>

- Ontologie-Bezug: <Relations-Konzept> (Pflicht)
- Quelle: <Herkunft> (Pflicht)
- Evidence: <Evidence-Link auf Working Memory> (Pflicht)
- Status: <z. B. vorgeschlagen / validiert / rejected>
```

## Pflichtfelder

**[Auftrag]** Ohne diese drei Felder keine Ablage:

1. **Ontologie-Bezug** — Verknüpfung mit Ontologie-Konzept.
2. **Quelle** — Herkunft der Extraktion.
3. **Evidence** — Evidence-Link auf das Working Memory.

Guardrail **[Auftrag]**: keine unbelegten Entitäten; Extraktion ohne
Quelle + Evidence-Link → `rejected`.

Quellenbezug **[Quelle: HeLa-Mem Paper]**: Evidence-Links entsprechen der
Hebbian-Distillation-Vorlage (semantischer Store via Reflective Agent).
**[Quelle: AWS Semantic Layer]**: Validierung nach ACE
(Accuracy/Consistency/Explainability) mit OWL/SPARQL/SHACL/SWRL.

## Status

**[Auftrag]** Angelegt, wartet auf t=1. Verzeichnis existiert, enthält
aktuell nur diese README. Erste Befüllung erfolgt im ersten
WISSEN-Durchlauf gemäß `knowledge/lifecycle/wissen.md` und
`skills/structure-knowledge/SKILL.md`.

## Ingestion-Pipeline (Auftrag + Quellen)

Die Befüllung von `knowledge/structured/` läuft über eine **Ingestion-Pipeline**
mit drei Schritten (quellenbelegt):

| Schritt | Aktion | Quelle |
|---|---|---|
| 1. **Extract** | Entitäten aus Rohdaten extrahieren | Graphiti (arXiv:2501.13956), Cognee (github.com/topoteretes/cognee) |
| 2. **Resolve** | Entitäten zu bestehenden Knoten auflösen (Deduplizierung) | Graphiti (arXiv:2501.13956) |
| 3. **Write Edges** | Kanten mit Gültigkeitszeiträumen schreiben (bi-temporal) | Graphiti (arXiv:2501.13956) |

**Dual-Write-Routing** (Quelle: Fast Write Routing, arXiv:2608.22215):
Jede Erfahrung durchläuft zuerst einen **billigen Klassifikator**:

| Kategorie | Aktion |
|---|---|
| **write-new** | `knowledge/structured/` **+** `data/memory/tier3-working/` |
| **write-update** | `knowledge/structured/` aktualisieren + alten `tier1-base/`-Eintrag **supersedieren** (invalidieren, nicht löschen) |
| **no-write** (non-write) | nur in Rekursions-Historie (`ergebnisse/rekursion/`) behalten |

Implementierung: `fast_write_router.apply_write_action` (AGENTS.md §10.7). Details: `ergebnisse/fwr-write.md`.

Details: `ergebnisse/ingestion-pipeline.md`.

### Quellen

- Graphiti (Graph-Ingestion, bi-temporale Kanten): https://arxiv.org/abs/2501.13956
- Fast Write Routing (Dual-Write-Routing): https://arxiv.org/abs/2608.22215
- Cognee (Extract→Cognify→Load): https://github.com/topoteretes/cognee

## PostToolUse-Hook + MKG-Pipeline (Quelle: Neo4j Meta-Knowledge-Graph)

**Quelle:** Neo4j Meta-Knowledge-Graph (MKG), https://github.com/neo4j-labs/meta-knowledge-graph;
Neo4j GraphRAG Pipeline: https://neo4j.com/docs/neo4j-graphrag-python/current/user_guide_kg_builder.html.

**PostToolUse-Hook (wörtlich, MKG):** „The `PostToolUse` hook also turns out to be a
general way to materialise structured tool output into the graph … unwraps that JSON
and merges it straight into the domain graph … each keyed on its real … id so the same
entity seen twice lands on one node rather than a duplicate … **The API call becomes
the exception rather than the habit**."

### Pipeline-Schritte (Neo4j GraphRAG)

| Schritt | Aktion | Quelle |
|---|---|---|
| 1. **Extraktion** | Entitäten aus `ergebnisse/rekursion/` extrahieren | Neo4j GraphRAG (Entity/Relation Extractor) |
| 2. **Auflösung** | Entitäten zu bestehenden Knoten auflösen (Deduplizierung) | Neo4j Resolver (`SinglePropertyExactMatchResolver`, `FuzzyMatchResolver`) |
| 3. **Schreiben** | Kanten mit Gültigkeitszeiträumen schreiben | Graphiti bi-temporal (arXiv:2501.13956) |

**Wörtlich (MKG):** „each keyed on its real … id so the same entity seen twice lands
on one node rather than a duplicate."

**Eingabe:** `ergebnisse/rekursion/` (Rekursions-Historie) → **Ausgabe:** typisierte
Knoten + Kanten in `knowledge/structured/`.

Details + Test (t=4, t=5, t=6): `ergebnisse/ingestion-pipeline.md`.

## Quellen

- HeLa-Mem Paper (ACL 2026): https://aclanthology.org/2026.acl-long.625/
- HeLa-Mem Code: https://github.com/ReinerBRO/HeLa-Mem
- AWS Semantic Layer (Prescriptive Guidance): https://docs.aws.amazon.com/prescriptive-guidance/latest/semantic-layer-agentic-ai-ontology-reasoning-virtual-knowledge-graph/semantic-layer-agentic-ai-ontology-reasoning-virtual-knowledge-graph.html
