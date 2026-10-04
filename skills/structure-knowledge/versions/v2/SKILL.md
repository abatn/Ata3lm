---
name: structure-knowledge
description: Rohdaten aus Working Memory in strukturiertes Wissen mit Ontologie-Bezug überführen und in knowledge/structured/ ablegen.
---

# Structure-Knowledge (Skill zur Lifecycle-Phase WISSEN, Stufe 2)

> Lab-Prinzip MD-first. Kennzeichnung: **[Auftrag]** = Auftragsvorgabe,
> **[Quelle]** = aus den Quellen im Abschnitt „Quellen" belegt.
> Keine weiteren Quellen, keine erfundenen Zahlen/Details.

## Ablauf

**[Auftrag; Mapping-Formulierung, kein wörtliches Quellen-Zitat]**

1. **Rohdaten aus Working Memory lesen.**
   Nur lesen, nichts deuten (Beobachten vor Handeln).
2. **Entitäten/Relationen extrahieren (LLM).**
   **[Auftrag: Mapping auf AWS „LLM-Anreicherung/Extraktion", kein wörtliches Zitat.]**
3. **Gegen Ontologie validieren (symbolisch).**
   **[Auftrag: Mapping auf AWS „symbolische Validierung (OWL/SPARQL/SHACL/SWRL)" und HeLa „semantischer Store via Hebbian Distillation", kein wörtliches Zitat.]**
   Konsistenz- und Formatprüfung; bei Verstoß: ablehnen (`rejected`), nicht raten.
4. **Mit Quellen- + Evidence-Links in `knowledge/structured/` schreiben.**
   Jede Einheit mit Ontologie-Bezug, Quelle und Evidence-Link auf das Working Memory.
5. **Ontologie-Eintrag anlegen.**
   Verknüpfung von Entität/Relation mit Ontologie-Konzept dokumentieren.

## HeLa-Bezug

**[Quelle: HeLa-Mem Paper]** Semantischer Store via Hebbian Distillation
durch Reflective Agent; episodischer Memory-Graph via Ko-Aktivierung;
Dual-Path Retrieval via Spreading Activation.

**[Quelle: HeLa-Mem Code]** Module `hebbian_memory` /
`hebbian_knowledge_memory` / `hebbian_retriever`; Code für LongMemEval/LoCoMo.

Skill-Mapping **[Auftrag]**: dicht verbundene Memory-Hubs identifizieren
und in wiederverwendbares semantisches Wissen mit Evidence-Links destillieren.

## AWS-Bezug

**[Quelle: AWS Semantic Layer]** Neurosymbolisch: LLM-Anreicherung +
symbolische Validierung; OWL/RDF/SPARQL/SHACL/R2RML/SWRL; Ontop, ELK/HermiT;
ACE (Accuracy/Consistency/Explainability); MCP/A2A-Schnittstellen.

Skill-Mapping **[Auftrag, kein wörtliches Zitat]**: LLM für semantische
Anreicherung/Extraktion, symbolisches Reasoning für
Validierung/Konsistenz/Erklärbarkeit nach ACE; die Formulierung
„LLM extrahiert Entitäten, symbolischer Reasoner validiert" ist ein
Mapping, kein Quellen-Zitat.

## Guardrails

**[Auftrag]**

- Jede Extraktion mit Quelle + Evidence-Link; sonst keine Ablage.
- Keine unbelegten Entitäten.
- Kein Handeln ohne vorheriges Lesen des Working Memory.
- Keine Schnittstellenänderung ohne Freigabe (Human-Gate).
- Nur Auftrags- oder quellenbelegte Aussagen; Erfundenes → `rejected`.

## Quellen

- HeLa-Mem Paper (ACL 2026): https://aclanthology.org/2026.acl-long.625/
- HeLa-Mem Code: https://github.com/ReinerBRO/HeLa-Mem
- AWS Semantic Layer (Prescriptive Guidance): https://docs.aws.amazon.com/prescriptive-guidance/latest/semantic-layer-agentic-ai-ontology-reasoning-virtual-knowledge-graph/semantic-layer-agentic-ai-ontology-reasoning-virtual-knowledge-graph.html


## Prozesse (Aufrufe) [Auftrag]

Dieser Skill ruft folgende Prozesse in `data/memory/` auf (MCP-Interface nach Atomic: https://atomicapp.ai/guides/mcp-server/):

- `fast_write_router.py` — 3-Klassen + `apply_write_action` (Stufe 2)
- **MCP-Tools:** `memory.write`

Quelle (Auftrag): `skills/README.md` (Skill→Prozess), `ergebnisse/mcp-memory.md` (Atomic).
