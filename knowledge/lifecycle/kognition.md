# Kognition – Stufe 4 des 8-Stufen-Zyklus

> Lab-Prinzip: Projekt + Skills + Connectors + Knowledge. MD-first.
> Eltern-Dok: `knowledge/lifecycle/rekursion/wissenszyklus-8-stufen.md` (Stufe 4).
> Kognition liest die Ontologie – das ist der Input für Denken (Stufe 5).
> Auftrags-Begriffe sind als solche markiert (Auftrag, keine Quellen-Behauptung).

## 1. Definition

Kognition bedeutet: Wissen **verstehen**, **verknüpfen** und daraus
**Schlussfolgerungen ziehen**.

- **Lesen:** Kognition liest die Ontologie (Begriffe, Relationen, Constraints).
- **Schreiben:** Kognition schreibt neue Verknüpfungen (Kanten, Inferenzen)
  zurück. Dies ist **Self-Feedback** (Auftrag) im Sinne des 8-Stufen-Zyklus:
  Die Stufe erzeugt das Material, das Denken (Stufe 5) und Handeln (Stufe 7)
  weiterverarbeiten.

„Kognition", „Self-Feedback" und „Working Memory" sind Auftrags-Vokabular
für die hier beschriebenen Mechanismen (Mapping, keine Quellen-Behauptung).

## 2. Verfahren

Zweistufiges Verfahren (Rollen aus Quellen abgeschrieben, Zuordnung als
Auftrag markiert):

1. **LLM schlägt Verknüpfungen vor:** Ein LLM generiert
   Kandidaten-Verknüpfungen (Entitäten, Relationen, Kanten) aus dem
   gespeicherten Wissen. Das entspricht dem probabilistischen,
   generativen Anteil (vgl. AWS Semantic Layer: probabilistische
   LLM-Outputs vs. deterministische Inferenz).
2. **Symbolischer Reasoner validiert gegen die Ontologie:** Jede
   Kandidaten-Verknüpfung wird gegen Ontologie-Regeln geprüft –
   Konsistenz und Constraints via **OWL/SHACL** ( deterministic,
   reproduzierbar, mit Provenienz). Nur validierte Verknüpfungen werden
   übernommen; der Rest wird als `rejected` dokumentiert.

Belegt in:

- Cognee (Ontologie-Grounding, Graph-Reasoning):
  https://github.com/topoteretes/cognee
- AWS Semantic Layer (symbolische Validierung: OWL/SHACL/SWRL,
  deterministische reproduzierbare Inferenz mit Provenienz vs.
  probabilistische LLM-Outputs):
  https://docs.aws.amazon.com/prescriptive-guidance/latest/semantic-layer-agentic-ai-ontology-reasoning-virtual-knowledge-graph/semantic-layer-agentic-ai-ontology-reasoning-virtual-knowledge-graph.html
- Graphiti (vorgeschriebene Pydantic-Ontologie vs. gelernte Struktur;
  Hybrid-Retrieval):
  https://github.com/getzep/graphiti

## 3. Schlussfolgerungs-Regel (verbindlich)

Jede Inferenz braucht einen **Prämissen-Beleg + Quellen-Link**, sonst
Status `rejected`.

- Prämissen: Welche bestehenden Fakten/Kanten die Konklusion tragen.
- Quelle: Link auf die Quelle jedes Prämissen-Fakts (Datei, Commit, URL –
  keine erfundenen Links).
- Ohne beides keine Übernahme nach Working Memory, kein Weiterreichen an
  Stufe 5.

## 4. Rekursionsschnittstelle (lesen → schreiben)

```text
Ontologie ──Kognition──▶ Verknüpfungen nach Working Memory
   │                            │
   │ liest: Begriffe,            ▼
   │ Relationen, Constraints  Denken (Stufe 5) prüft / reflektiert
```

- **Lesen:** Ontologie (Begriffe, Relationen, Constraints aus
  `knowledge/`).
- **Schreiben:** validierte Verknüpfungen nach Working Memory (Auftrag);
  jede Schlussfolgerung zusätzlich dokumentiert in
  `knowledge/cognition/` (Prämissen → Konklusion, Quelle, Status).
- **Weitergabe:** Belegte Verknüpfungen sind der Input für Denken (Stufe 5).

## 5. Input / Output

Input: Ontologie (Begriffe, Relationen, Constraints), Working-Memory-Stand,
Kandidaten-Kontext aus Stufe 1–3.

Output: validierte Verknüpfungen in Working Memory + Files in
`knowledge/cognition/` (Prämissen, Konklusion, Quelle, Status) +
`rejected`-Liste mit Grund.

## 6. Guardrails

1. Kein Handeln ohne Beobachten: Kognition liest zuerst die Ontologie,
   erfindet keine Begriffe.
2. Jede Kandidaten-Verknüpfung durchläuft die symbolische Validierung
   (Konsistenz/Constraints via OWL/SHACL); unvalidierte Vorschläge werden
   nicht übernommen.
3. Jede Inferenz braucht Prämissen-Beleg + Quellen-Link, sonst `rejected`.
4. Schwelle für Entity-Matching: **Fuzzy-Matching cutoff 0.80** –
   **Vorgabe (Auftrag), keine Quellen-Behauptung.** Konfigurierbare
   Schwelle (kein Cognee-Fakt, kein allgemeines Gesetz); Änderungen nur
   mit menschlicher Freigabe und Dokumentation.
5. Keine beleglosen Anpassungen der Ontologie selbst (Flexibilität endet
   an Provenienz + Human-Gate, vgl. `AGENTS.md` Prinzip 5 und 6).
6. Jede Iteration → Provenienz-File (vgl. `AGENTS.md` Durchsetzung).

## 7. Quellen (ausschließlich diese, keine weiteren behauptet)

- Cognee (Ontologie-Grounding, Graph-Reasoning):
  https://github.com/topoteretes/cognee
- AWS Semantic Layer (symbolische Validierung: OWL/SHACL/SWRL,
  deterministische reproduzierbare Inferenz mit Provenienz vs.
  probabilistische LLM-Outputs):
  https://docs.aws.amazon.com/prescriptive-guidance/latest/semantic-layer-agentic-ai-ontology-reasoning-virtual-knowledge-graph/semantic-layer-agentic-ai-ontology-reasoning-virtual-knowledge-graph.html
- Graphiti (vorgeschriebene Pydantic-Ontologie vs. gelernte Struktur;
  Hybrid-Retrieval):
  https://github.com/getzep/graphiti

Referenzen im Repo:

- Skill: `skills/cognize/SKILL.md`
- Connector: `connectors/cognee-validation.md`
- Inferenz-Ablage: `knowledge/cognition/README.md`
