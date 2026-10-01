# WISSEN — Stufe 2 des 8-Stufen-Zyklus

> Lab-Prinzip MD-first. Status-Kennzeichnung in diesem Dokument:
> **[Auftrag]** = gesetzte Betriebsregel aus dem Implementierungsauftrag,
> kein Quellen-Claim. **[Quelle]** = aus einer der unten genannten Quellen belegt.
> Keine weiteren Quellen behauptet, keine Zahlen/Details erfunden.

## 1. Definition

**[Auftrag]** WISSEN (Stufe 2) liest Rohdaten aus dem Working Memory,
wandelt sie in strukturiertes Wissen um und legt sie mit Ontologie-Bezug
in `knowledge/structured/` ab.

Das heißt im Einzelnen **[Auftrag]**:

- **Lesen:** Input sind Rohdaten/Traces aus dem Working Memory (Stufe 1-nah).
- **Umwandeln:** Rohdaten werden in Entitäten und Relationen mit definiertem Format überführt.
- **Ablegen:** Ablage erfolgt ausschließlich in `knowledge/structured/` und nur mit Ontologie-Bezug.

## 2. HeLa-Mapping

**[Quelle: HeLa-Mem Paper]** Duale Organisation: episodischer Memory-Graph
via Ko-Aktivierung + semantischer Store via Hebbian Distillation durch
einen Reflective Agent; Dual-Path Retrieval via Spreading Activation.

**[Quelle: HeLa-Mem Code]** Code für LongMemEval/LoCoMo; Module
`hebbian_memory` / `hebbian_knowledge_memory` / `hebbian_retriever`.

Mapping auf Stufe 2 **[Auftrag, kein wörtliches Quellen-Zitat]**:

- Hebbian Distillation als Vorlage: der Reflective Agent identifiziert
  dicht verbundene Memory-Hubs und destilliert sie in strukturiertes,
  wiederverwendbares semantisches Wissen mit Evidence-Links.
- Die Evidence-Links entsprechen der Forderung, jede Wissenseinheit auf
  ihre Herkunft im Working Memory zurückzuführen.

## 3. AWS-Mapping

**[Quelle: AWS Semantic Layer]** Neurosymbolische KI: LLM-Anreicherung +
symbolische Validierung; Standards OWL/RDF/SPARQL/SHACL/R2RML/SWRL;
Werkzeuge Ontop, ELK/HermiT; ACE-Prinzipien
(Accuracy/Consistency/Explainability); Schnittstellen MCP/A2A.

Mapping auf Stufe 2 **[Auftrag, kein wörtliches Quellen-Zitat]**:

- Neurosymbolisch: LLM für semantische Anreicherung/Extraktion,
  symbolisches Reasoning (OWL/SPARQL/SHACL/SWRL) für
  Validierung/Konsistenz/Erklärbarkeit.
- ACE-Prinzipien als Richtmaß: Accuracy, Consistency, Explainability.
- Auftrags-Formulierung „LLM extrahiert Entitäten, symbolischer Reasoner
  validiert" ist **[Auftrag: Mapping auf die obigen Quellen, kein
  wörtliches Zitat aus den Quellen]**.

## 4. Rekursionsschnittstelle

**[Auftrag]**

- **Liest:** Working Memory (Rohdaten/Traces der Stufe 1).
- **Schreibt:** Ontologie / `knowledge/structured/` (strukturierte Einheiten
  mit Ontologie-Bezug).
- Keine andere Schreibstelle in dieser Stufe.

## 5. Input / Output

| Feld | Beschreibung | Status |
|------|--------------|--------|
| Input | Rohdaten aus Working Memory | **[Auftrag]** |
| Verarbeitung | Entitäten/Relationen extrahieren (LLM), gegen Ontologie validieren (symbolisch) | **[Auftrag: Mapping, kein wörtliches Zitat]** |
| Output | Strukturierte Einheiten in `knowledge/structured/` mit Ontologie-Bezug + Quelle + Evidence-Link; Ontologie-Eintrag | **[Auftrag]** |

## 6. Guardrails

**[Auftrag]**

1. Jede Extraktion mit Quelle + Evidence-Link. Ohne beides keine Ablage.
2. Keine unbelegten Entitäten: keine Entität/Relation ohne Herkunftsnachweis.
3. Keine Format-/Schnittstellenänderung ohne Freigabe (Human-Gate).
4. Keine Stufe überspringen: kein Schreiben ohne vorheriges Lesen des Working Memory.
5. Keine Erfindungen: nur Auftrags-Begriffe oder quellenbelegte Aussagen; alles andere → `rejected`.

## 7. Quellen

NUR diese Quellen (keine weiteren behauptet):

- HeLa-Mem Paper (ACL 2026): https://aclanthology.org/2026.acl-long.625/ — duale Organisation: episodischer Memory-Graph via Ko-Aktivierung + semantischer Store via Hebbian Distillation durch Reflective Agent; Dual-Path Retrieval via Spreading Activation.
- HeLa-Mem Code: https://github.com/ReinerBRO/HeLa-Mem — Code für LongMemEval/LoCoMo, Module `hebbian_memory` / `hebbian_knowledge_memory` / `hebbian_retriever`.
- AWS Semantic Layer (Prescriptive Guidance): https://docs.aws.amazon.com/prescriptive-guidance/latest/semantic-layer-agentic-ai-ontology-reasoning-virtual-knowledge-graph/semantic-layer-agentic-ai-ontology-reasoning-virtual-knowledge-graph.html — Neurosymbolische KI: LLM-Anreicherung + symbolische Validierung; OWL/RDF/SPARQL/SHACL/R2RML/SWRL; Ontop, ELK/HermiT; ACE: Accuracy/Consistency/Explainability; MCP/A2A-Schnittstellen.
