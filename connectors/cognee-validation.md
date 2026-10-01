# Connector: Cognee-Validierung (Ontologie-Grounding + symbolische Prüfung)

> Lab-Prinzip, MD-first. „Cognee-Validierung", „Kognition",
> „Self-Feedback" und „Working Memory" sind Auftrags-Vokabular für die
> unten beschriebenen Mechanismen (Mapping, keine Quellen-Behauptung).

## Identität

- Cognee (Ontologie-Grounding, Graph-Reasoning):
  https://github.com/topoteretes/cognee
- AWS Semantic Layer (symbolische Validierung: OWL/SHACL/SWRL,
  deterministische reproduzierbare Inferenz mit Provenienz vs.
  probabilistische LLM-Outputs):
  https://docs.aws.amazon.com/prescriptive-guidance/latest/semantic-layer-agentic-ai-ontology-reasoning-virtual-knowledge-graph/semantic-layer-agentic-ai-ontology-reasoning-virtual-knowledge-graph.html
- Graphiti (vorgeschriebene Pydantic-Ontologie vs. gelernte Struktur;
  Hybrid-Retrieval):
  https://github.com/getzep/graphiti

## Mechanismen (aus Quellen abgeschrieben, keine Details erfunden)

- **Cognee:** Ontologie-Grounding und Graph-Reasoning – Wissen wird an
  einer Ontologie geerdet und als Graph verknüpft und geschlossen.
- **AWS Semantic Layer:** symbolische Validierung mit OWL/SHACL/SWRL;
  deterministische, reproduzierbare Inferenz mit Provenienz – gegenübergestellt
  zu probabilistischen LLM-Outputs, die allein keine Garantie für Konsistenz
  geben.
- **Graphiti:** vorgeschriebene Pydantic-Ontologie vs. gelernte Struktur;
  Hybrid-Retrieval als Abrufweg (symbolisch + vektoriell kombiniert).

## Mapping auf Kognition

| Kognition | Beleg |
|---|---|
| Ontologie lesen | Cognee: Ontologie-Grounding; Graphiti: vorgeschriebene Pydantic-Ontologie |
| Kandidaten-Verknüpfungen vorschlagen | Probabilistische LLM-Outputs (AWS-Gegenüberstellung) |
| Symbolisch validieren (Konsistenz/Constraints via OWL/SHACL) | AWS Semantic Layer: OWL/SHACL/SWRL, deterministische reproduzierbare Inferenz mit Provenienz |
| Belegte Verknüpfungen schreiben (Self-Feedback (Auftrag)) | Cognee: Graph-Reasoning; Übernahme nur mit Prämissen-Beleg + Quellen-Link |
| Abruf gelernt + vorgeschrieben | Graphiti: gelernte Struktur vs. Pydantic-Ontologie; Hybrid-Retrieval |

## Grenzen (nur aus Auftrag und Quellen-Umfang, nichts erfunden)

- Keine Zahlen, Schwellen oder Interna aus den Quellen behauptet – die
  Quellen werden hier nur im oben genannten Umfang referenziert.
- **Fuzzy-Matching cutoff 0.80:** Vorgabe (Auftrag),
  keine Quellen-Behauptung. Konfigurierbare Schwelle für Entity-Matching;
  kein Cognee-Fakt, kein allgemeines Gesetz. Änderung nur mit
  menschlicher Freigabe und Dokumentation.
- Jede Inferenz braucht Prämissen-Beleg + Quellen-Link, sonst `rejected`
  (Schlussfolgerungs-Regel aus `knowledge/lifecycle/kognition.md`).
- Keine beleglosen Ontologie-Änderungen (Provenienz + Human-Gate,
  vgl. `AGENTS.md` Prinzip 5 und 6).

## Quellen (ausschließlich diese, keine weiteren behauptet)

- https://github.com/topoteretes/cognee
- https://docs.aws.amazon.com/prescriptive-guidance/latest/semantic-layer-agentic-ai-ontology-reasoning-virtual-knowledge-graph/semantic-layer-agentic-ai-ontology-reasoning-virtual-knowledge-graph.html
- https://github.com/getzep/graphiti
