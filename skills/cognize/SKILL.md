---
name: cognize
description: Kognition (Stufe 4 des 8-Stufen-Zyklus): Ontologie lesen, Kandidaten-Verknüpfungen vorschlagen, symbolisch gegen die Ontologie validieren (Konsistenz/Constraints via OWL/SHACL) und nur belegte Verknüpfungen nach Working Memory schreiben. Nutze diesen Skill, wenn aus gespeichertem Wissen neue Verknüpfungen abgeleitet werden sollen – ohne Erfindungen, jede Inferenz mit Prämissen-Beleg und Quellen-Link.
---

# Skill: cognize

> Lab-Prinzip, MD-first. Auftrags-Begriffe sind als solche markiert
> (Auftrag, keine Quellen-Behauptung).
> Projekt-Doku: `knowledge/lifecycle/kognition.md`.
> Connector: `connectors/cognee-validation.md`.
> Inferenz-Ablage: `knowledge/cognition/`.

## Zweck

Wissen verstehen, verknüpfen, Schlussfolgerungen ziehen: Der Skill liest
die Ontologie, erzeugt Kandidaten-Verknüpfungen und übernimmt nur
symbolisch validierte, belegte Verknüpfungen (Self-Feedback (Auftrag) für
Stufe 5).

## Wann anwenden

- Wenn neue Kanten/Relationen aus bestehendem Wissen abgeleitet werden sollen.
- Wenn Kandidaten-Verknüpfungen gegen Ontologie-Constraints geprüft werden müssen.
- NICHT anwenden ohne lesbare Ontologie und ohne dokumentierte Quellen.

## Ablauf

1. **Ontologie lesen**
   - Begriffe, Relationen, Constraints aus `knowledge/` laden.
   - Geltende Schwellen laden (u. a. Fuzzy-Matching cutoff 0.80 –
     Vorgabe (Auftrag), keine Quellen-Behauptung; konfigurierbar).

2. **Kandidaten-Verknüpfungen vorschlagen**
   - LLM generiert Kandidaten (Entitäten, Relationen, Kanten) aus dem
     gespeicherten Wissen.
   - Entity-Matching nur oberhalb der konfigurierbaren Schwelle
     (Vorgabe (Auftrag): 0.80); Treffer darunter werden verworfen oder als
     `rejected` dokumentiert.

3. **Symbolisch validieren (Konsistenz/Constraints)**
   - Jede Kandidaten-Verknüpfung gegen die Ontologie prüfen:
     Konsistenz und Constraints via OWL/SHACL (deterministisch,
     reproduzierbar, mit Provenienz).
   - Vorgeschriebene vs. gelernte Struktur beachten (Pydantic-Ontologie vs.
     gelernte Struktur; Hybrid-Retrieval als Abrufweg).

4. **Belegte Verknüpfungen schreiben**
   - Nur validierte Verknüpfungen mit Prämissen-Beleg + Quellen-Link nach
     Working Memory (Auftrag) schreiben.
   - Unvalidierte oder unbelegte Kandidaten → `rejected` mit Grund.

5. **Jede Schlussfolgerung in `knowledge/cognition/` dokumentieren**
   - Format: Prämissen → Konklusion (Pflichtfelder laut
     `knowledge/cognition/README.md`).
   - Pflicht: Prämissen-Beleg + Quellen-Link pro Inferenz, sonst `rejected`.

## Guardrails (verbindlich, vom Skill erzwungen)

1. Ontologie zuerst lesen; keine erfundenen Begriffe oder Relationen.
2. Jede Kandidaten-Verknüpfung durchläuft die symbolische Validierung
   (Konsistenz/Constraints via OWL/SHACL); ohne Validierung keine Übernahme.
3. Jede Inferenz braucht Prämissen-Beleg + Quellen-Link, sonst `rejected`.
4. Fuzzy-Matching cutoff 0.80 ist eine Vorgabe (Auftrag),
   keine Quellen-Behauptung – konfigurierbare Schwelle, kein Cognee-Fakt;
   Änderung nur mit menschlicher Freigabe.
5. Keine beleglosen Ontologie-Änderungen (Provenienz + Human-Gate).
6. Jede Iteration → Provenienz-File (vgl. `AGENTS.md` Durchsetzung).

## Input / Output

Input: Ontologie (Begriffe, Relationen, Constraints), Working-Memory-Stand,
Kontext aus Stufe 1–3.

Output: validierte Verknüpfungen in Working Memory +
`knowledge/cognition/`-Files (Prämissen, Konklusion, Quelle, Status) +
`rejected`-Liste mit Grund.

## Quellen (ausschließlich diese, keine weiteren behauptet)

- Cognee (Ontologie-Grounding, Graph-Reasoning):
  https://github.com/topoteretes/cognee
- AWS Semantic Layer (symbolische Validierung: OWL/SHACL/SWRL,
  deterministische reproduzierbare Inferenz mit Provenienz vs.
  probabilistische LLM-Outputs):
  https://docs.aws.amazon.com/prescriptive-guidance/latest/semantic-layer-agentic-ai-ontology-reasoning-virtual-knowledge-graph/semantic-layer-agentic-ai-ontology-reasoning-virtual-knowledge-graph.html
- Graphiti (vorgeschriebene Pydantic-Ontologie vs. gelernte Struktur;
  Hybrid-Retrieval):
  https://github.com/getzep/graphiti
