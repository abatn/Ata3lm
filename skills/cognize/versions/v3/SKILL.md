---
name: cognize
description: "Kognition (Stufe 4 des 8-Stufen-Zyklus): Ontologie lesen, Kandidaten-Verknüpfungen vorschlagen (LLM proposed), vorgeschaltete Inferenz-Schicht (SHACL-SPARQL-Regeln) materialisiert implizite Triples, dann symbolische Validierung (SHACL Core + SHACL-SPARQL) gegen die Ontologie (Symbolic validates), und nur bei PASS nach Working Memory schreiben (Commit). Nutze diesen Skill, wenn aus gespeichertem Wissen neue Verknüpfungen abgeleitet werden sollen – ohne Erfindungen, jede Inferenz mit Prämissen-Beleg und Quellen-Link."
---

# Skill: cognize

> Lab-Prinzip, MD-first. Auftrags-Begriffe sind als solche markiert
> (Auftrag, keine Quellen-Behauptung).
> Projekt-Doku: `knowledge/lifecycle/kognition.md`.
> Connector: `connectors/cognee-validation.md`.
> Inferenz-Ablage: `knowledge/cognition/`.
> **Fester Loop: LLM → Symbolic → Commit** (neuro-symbolisch, siehe unten).

## Zweck

Wissen verstehen, verknüpfen, Schlussfolgerungen ziehen: Der Skill liest
die Ontologie, erzeugt Kandidaten-Verknüpfungen (LLM), materialisiert **vor**
der Validierung die impliziten Konsequenzen (Inferenz-Schicht), validiert
symbolisch und übernimmt nur bei **PASS** die belegten Verknüpfungen
(Self-Feedback (Auftrag) für Stufe 5).

## Wann anwenden

- Wenn neue Kanten/Relationen aus bestehendem Wissen abgeleitet werden sollen.
- Wenn implizite Konsequenzen (Inferenz) vor der Validierung materialisiert
  werden müssen.
- Wenn ein LLM-Vorschlag symbolisch geprüft und nur bei **PASS** übernommen
  werden soll (neuro-symbolischer Loop).
- Wenn Kandidaten-Verknüpfungen gegen Ontologie-Constraints geprüft werden müssen.
- NICHT anwenden ohne lesbare Ontologie und ohne dokumentierte Quellen.

## Fester Loop: LLM → Symbolic → Commit (neuro-symbolisch)

> Quelle: **AWS Semantic Layer** — „neurosymbolic approach combines deterministic
> symbolic reasoning with probabilistic LLM capabilities" (Accuracy/Consistency/
> Explainability; SHACL-Validatoren; „validate actions"; auditable reasoning chains).
> + **Swansea (Robaldo & Batsakis)** — erst Inferenz (SHACL-SPARQL), dann Validierung.

Der Loop ist **fest** und wird nicht übersprungen:

```text
        ┌──────────────────────────────────────────────┐
        ▼                                              │
1. LLM proposed        Kandidaten generieren            │
   (Entitäten, Relationen, Kanten)                     │
        │                                              │
        ▼                                              │
2. Symbolic validates  (a) Inferenz-Schicht            │
   SHACL-SPARQL CONSTRUCT, Fixpunkt                    │
                       (b) SHACL Core + SHACL-SPARQL   │
        │                                              │
   ┌────┴─────┐                                        │
   │ PASS?    │── nein (FAIL) ──► zurück an 1 (LLM) ───┘
   └────┬─────┘   (Fehlergrund mitgeben; KEIN Commit)
        │ ja
        ▼
3. Commit              validierte + belegte Verknüpfung
   nach Working Memory (Auftrag); sonst rejected
```

- **FAIL → zurück an LLM:** der Loop terminiert nicht bei Fehler, sondern
  gibt den Validierungsgrund an Schritt 1 zurück (Re-Proposal). Kein Commit.
- **Commit nur bei PASS:** ohne symbolisches PASS keine Übernahme (Guardrail).

## Ablauf

1. **Ontologie lesen**
   - Begriffe, Relationen, Constraints aus `knowledge/` laden.
   - Geltende Schwellen laden (u. a. Fuzzy-Matching cutoff 0.80 –
     Vorgabe (Auftrag), keine Quellen-Behauptung; konfigurierbar).

2. **Kandidaten-Verknüpfungen vorschlagen (LLM proposed)**
   - LLM generiert Kandidaten (Entitäten, Relationen, Kanten) aus dem
     gespeicherten Wissen.
   - Entity-Matching nur oberhalb der konfigurierbaren Schwelle
     (Vorgabe (Auftrag): 0.80); Treffer darunter werden verworfen oder als
     `rejected` dokumentiert.

3. **Inferenz-Schicht (vorgeschaltet, VOR SHACL)**
   - Zuerst die impliziten Konsequenzen materialisieren: SHACL-SPARQL-Regeln
     (`CONSTRUCT-WHERE`) iterativ bis zum Fixpunkt anwenden (wie OWL-Reasoner,
     z. B. HermiT); alternativ SPARQL-CONSTRUCT oder OWL-Reasoner.
   - Grund: SHACL prüft nur explizite Triples; bestimmte Invaliditäten
     (z. B. Zeitintervall endet vor Start) werden erst durch Inferenz sichtbar.
   - Quelle: Robaldo & Batsakis (Swansea University), Semantic Web Journal.

4. **Symbolisch validieren (Symbolic validates) — auf dem materialisierten Graph**
   - SHACL Core für einfache Constraints (Kardinalität, Datentyp, Wertebereich).
   - SHACL-SPARQL für komplexe Regeln (Zeitintervall-Logik, transitive
     Beziehungen).
   - Deterministisch, reproduzierbar, mit Provenienz; vorgeschriebene vs.
     gelernte Struktur beachten (Pydantic-Ontologie vs. gelernte Struktur;
     Hybrid-Retrieval als Abrufweg).
   - **FAIL → zurück an Schritt 2** (Re-Proposal), kein Commit.

5. **Commit (nur bei PASS)**
   - Nur validierte Verknüpfungen mit Prämissen-Beleg + Quellen-Link nach
     Working Memory (Auftrag) schreiben.
   - Unvalidierte oder unbelegte Kandidaten → `rejected` mit Grund.

6. **Inferenz-Kette + Schlussfolgerung in `knowledge/cognition/` dokumentieren**
   - Pro Inferenz eine Datei `inference-<id>.md`: Input-Triples, Regel
     (Regel-ID), Output-Triples, Quelle (Provenienz als First-Class State).
   - Zusätzlich Prämissen → Konklusion (Pflichtfelder laut
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
7. Inferenz VOR Validierung: erst materialisieren (SHACL-SPARQL), dann prüfen.
   Keine Validierung nur auf dem expliziten Graph – das verpasst Invaliditäten.
8. **Loop fest:** kein Commit ohne symbolisches PASS; bei FAIL zurück an den
   LLM (Re-Proposal) mit Fehlergrund.

## Input / Output

Input: Ontologie (Begriffe, Relationen, Constraints), Working-Memory-Stand,
Kontext aus Stufe 1–3.

Output: validierte Verknüpfungen in Working Memory +
`knowledge/cognition/`-Files (Prämissen, Konklusion, Quelle, Status) +
`rejected`-Liste mit Grund.

## Quellen (ausschließlich diese, keine weiteren behauptet)

- Cognee (Ontologie-Grounding, Graph-Reasoning):
  https://github.com/topoteretes/cognee
- AWS Semantic Layer (neurosymbolisch: „combines deterministic symbolic
  reasoning with probabilistic LLM capabilities"; SHACL-Validatoren; OWL/SWRL;
  deterministische reproduzierbare Inferenz mit Provenienz vs. probabilistische
  LLM-Outputs; auditable reasoning chains):
  https://docs.aws.amazon.com/prescriptive-guidance/latest/semantic-layer-agentic-ai-ontology-reasoning-virtual-knowledge-graph/semantic-layer-agentic-ai-ontology-reasoning-virtual-knowledge-graph.html
- Graphiti (vorgeschriebene Pydantic-Ontologie vs. gelernte Struktur;
  Hybrid-Retrieval):
  https://github.com/getzep/graphiti
- Robaldo & Batsakis, Swansea University (HRC School of Law) — „On the
  interplay between validation and inference in SHACL – an investigation on
  the Time Ontology", Semantic Web Journal: erst Inferenz (SHACL-SPARQL),
  dann Validierung; SHACL allein unzureichend für zeitliche Invaliditäten:
  https://www.semantic-web-journal.net/system/files/swj3959.pdf
- W3C SHACL Advanced Features (SPARQL-Rules, CONSTRUCT-WHERE):
  https://www.w3.org/TR/shacl-af/#SPARQLRule


## Prozesse (Aufrufe) [Auftrag]

Dieser Skill ruft folgende Prozesse in `data/memory/` auf (MCP-Interface nach Atomic: https://atomicapp.ai/guides/mcp-server/):

- `reflective_agent.py` — Konsolidierung (Stufe 4)
- **MCP-Tools:** `memory.read`, `memory.search`

Quelle (Auftrag): `skills/README.md` (Skill→Prozess), `ergebnisse/mcp-memory.md` (Atomic).
