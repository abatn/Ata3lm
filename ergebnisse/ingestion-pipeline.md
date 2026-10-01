# Ingestion-Pipeline – ergebnisse/rekursion/ → knowledge/structured/

> Datum: 2026-10-01
> Zweck: Ingestion-Pipeline nach dem Neo4j Meta-Knowledge-Graph (MKG).
> Lab-Prinzip: Keine Erfindungen – jeder Schritt mit Quellen-Link.
> Geltung: `AGENTS.md` §6 (keine Erfindungen), §10 (Fast Write Routing).

---

## 1. PostToolUse-Hook (Quelle: Neo4j MKG)

**Quelle:** https://github.com/neo4j-labs/meta-knowledge-graph

**Wörtlich (MKG):** „The `PostToolUse` hook also turns out to be a general way to
materialise structured tool output into the graph … unwraps that JSON and merges it
straight into the domain graph … each keyed on its real … id so the same entity seen
twice lands on one node rather than a duplicate … **The API call becomes the exception
rather than the habit**."

**Anwendung (Auftrag):** Strukturierte Tool-/Rekursions-Ergebnisse werden als
**typisierte Knoten** in `knowledge/structured/` geschrieben.

---

## 2. Pipeline-Schritte (Quelle: Neo4j GraphRAG)

**Quelle:** https://neo4j.com/docs/neo4j-graphrag-python/current/user_guide_kg_builder.html

| Schritt | Aktion | Quelle |
|---|---|---|
| 1. **Extraktion** | Entitäten aus `ergebnisse/rekursion/` extrahieren | Neo4j GraphRAG (Entity/Relation Extractor) |
| 2. **Auflösung** | Entitäten zu bestehenden Knoten auflösen (Deduplizierung) | Neo4j Resolver (`SinglePropertyExactMatchResolver`, `FuzzyMatchResolver`) |
| 3. **Schreiben** | Kanten mit Gültigkeitszeiträumen schreiben | Graphiti bi-temporal (arXiv:2501.13956) |

**Wörtlich (Neo4j Resolver):** „The Entity Resolver … merg[es] entity nodes that
represent the same real-world object."
**Wörtlich (Graphiti):** „Facts have validity windows … old facts are invalidated — not deleted."

---

## 3. Test: 3 Rekursions-Dateien verarbeitet (t=4, t=5, t=6)

| Datei | Extrahiert (Entität) | Aufgelöst | Geschrieben |
|---|---|---|---|
| `011-t4-rekursion.md` | Solver `berechne_durchschnitt` | neu (kein Duplikat) | `entity-solver-berechne-durchschnitt.md` |
| `012-t5-rekursion.md` | Solver `finde_minimum` | neu | `entity-solver-finde-minimum.md` |
| `013-t6-rekursion.md` | Solver `berechne_median` | neu | `entity-solver-berechne-median.md` |

### Kanten (mit Gültigkeit)
| Subjekt --Relation--> Objekt | Gültigkeit |
|---|---|
| t=4 --produces--> berechne_durchschnitt | von 2026-09-30, offen |
| t=5 --produces--> finde_minimum | von 2026-09-30, offen |
| t=6 --produces--> berechne_median | von 2026-10-01, offen |
| berechne_median --supersedes--> berechne_durchschnitt | von 2026-10-01 |

Datei: `knowledge/structured/relations-rekursion-solver.md`.

### Ablauf
```text
ergebnisse/rekursion/011..013
   │ [1] Extraktion (Entitäten)
   ▼
   │ [2] Auflösung (zu bestehenden Knoten; kein Duplikat)
   ▼
   │ [3] Schreiben (Kanten + Gültigkeitszeiträume)
   ▼
knowledge/structured/  (neue Entitäten + Relationen)
```

---

## 4. Ergebnis: neue Einträge in knowledge/structured/

**Vorher:** 2 Einträge (`entity-fast-write-routing.md`, `relation-agent-uses-fwr.md`).
**Nachher:** 6 Einträge (+ README):
- `entity-solver-berechne-durchschnitt.md` (t=4)
- `entity-solver-finde-minimum.md` (t=5)
- `entity-solver-berechne-median.md` (t=6)
- `relations-rekursion-solver.md` (Kanten mit Gültigkeit)

---

## 5. Quellen (verifiziert)

| Quelle | HTTP | Link |
|---|---|---|
| Neo4j MKG (PostToolUse-Hook) | 200 | https://github.com/neo4j-labs/meta-knowledge-graph |
| Neo4j GraphRAG Pipeline | 200 | https://neo4j.com/docs/neo4j-graphrag-python/current/user_guide_kg_builder.html |
| Graphiti (bi-temporal) | 200 | https://arxiv.org/abs/2501.13956 |
| Fast Write Routing | 200 | https://arxiv.org/abs/2608.22215 |

> MKG-Blog (Medium): HTTP 403 (Bot-Schutz) – Inhalt über das Repo verifiziert.

---

## 6. Status

| Punkt | Status |
|---|---|
| PostToolUse-Hook | ✅ dokumentiert (MKG) |
| Pipeline (Extract→Resolve→Write) | ✅ dokumentiert (Neo4j GraphRAG) |
| 3 Dateien verarbeitet (t=4/5/6) | ✅ |
| Neue Einträge in knowledge/structured/ | ✅ 4 neu (3 Entitäten + 1 Relation) |

**Ehrlich:** Hook-Konzept + Pipeline stammen aus Neo4j MKG/GraphRAG; die
Gültigkeitszeiträume aus Graphiti (bi-temporal). Die konkreten Entitäten wurden
aus den tatsächlichen Rekursions-Dateien extrahiert (keine Erfindung).
