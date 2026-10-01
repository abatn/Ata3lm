# Connector: HeLa-Semantic (für Lifecycle-Phase WISSEN, Stufe 2)

> Lab-Prinzip MD-first. Kennzeichnung: **[Auftrag]** = Auftragsvorgabe,
> **[Quelle]** = aus den unten genannten Quellen abgeschrieben/übernommen.
> Keine weiteren Quellen, keine erfundenen Zahlen/Details.

## 1. Identität

**[Auftrag]** Dieser Connector bindet die HeLa-Semantik an die
WISSEN-Phase: Er liefert die Vorlage dafür, wie Rohdaten aus dem
Working Memory in strukturiertes, wiederverwendbares semantisches
Wissen überführt werden.

## 2. Mechanismen (aus Quellen abgeschrieben)

**[Quelle: HeLa-Mem Paper — https://aclanthology.org/2026.acl-long.625/]**

- Duale Organisation: episodischer Memory-Graph via Ko-Aktivierung +
  semantischer Store via Hebbian Distillation durch Reflective Agent.
- Dual-Path Retrieval via Spreading Activation.

**[Quelle: HeLa-Mem Code — https://github.com/ReinerBRO/HeLa-Mem]**

- Code für LongMemEval/LoCoMo.
- Module: `hebbian_memory` / `hebbian_knowledge_memory` / `hebbian_retriever`.

**[Quelle: AWS Semantic Layer — https://docs.aws.amazon.com/prescriptive-guidance/latest/semantic-layer-agentic-ai-ontology-reasoning-virtual-knowledge-graph/semantic-layer-agentic-ai-ontology-reasoning-virtual-knowledge-graph.html]**

- Neurosymbolische KI: LLM-Anreicherung + symbolische Validierung.
- Standards: OWL/RDF/SPARQL/SHACL/R2RML/SWRL.
- Werkzeuge: Ontop, ELK/HermiT.
- ACE-Prinzipien: Accuracy/Consistency/Explainability.
- Schnittstellen: MCP/A2A.

## 3. Mapping auf WISSEN

**[Auftrag; Mapping, kein wörtliches Quellen-Zitat]**

- Hebbian Distillation als Vorlage für Stufe 2: Reflective Agent
  identifiziert dicht verbundene Memory-Hubs und destilliert sie in
  strukturiertes, wiederverwendbares semantisches Wissen mit Evidence-Links.
- Neurosymbolische Arbeitsteilung als Vorlage: LLM für semantische
  Anreicherung/Extraktion, symbolisches Reasoning (OWL/SPARQL/SHACL/SWRL)
  für Validierung/Konsistenz/Erklärbarkeit nach ACE.
- Die Auftrags-Formulierung „LLM extrahiert Entitäten, symbolischer
  Reasoner validiert" ist ein **Mapping auf die obigen Quellen, kein
  wörtliches Zitat** aus Paper oder AWS-Guidance.

## 4. Grenzen (aus Quellen übernommen)

**[Quelle]** Es werden nur die oben unter Abschnitt 2 genannten
Mechanismen beansprucht. Insbesondere werden behauptet:

- nur die duale Organisation (Ko-Aktivierung + Hebbian Distillation
  durch Reflective Agent) und Dual-Path Retrieval via Spreading
  Activation aus dem HeLa-Paper;
- nur die genannten Code-Module und Benchmark-Namen aus dem HeLa-Repo;
- nur die genannten Standards, Werkzeuge, ACE-Prinzipien und
  Schnittstellen aus der AWS-Guidance.

**[Auftrag]** Alles darüber hinaus (z. B. konkrete Schwellenwerte,
Algorithmen-Details, Performance-Zahlen) wird nicht behauptet und gilt
als Erfindung → `rejected`.

## 5. Quellen

- HeLa-Mem Paper (ACL 2026): https://aclanthology.org/2026.acl-long.625/
- HeLa-Mem Code: https://github.com/ReinerBRO/HeLa-Mem
- AWS Semantic Layer (Prescriptive Guidance): https://docs.aws.amazon.com/prescriptive-guidance/latest/semantic-layer-agentic-ai-ontology-reasoning-virtual-knowledge-graph/semantic-layer-agentic-ai-ontology-reasoning-virtual-knowledge-graph.html
