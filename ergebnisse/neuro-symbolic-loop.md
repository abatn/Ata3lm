# LLM → Symbolic → Commit als fester Loop (neuro-symbolisch)

> Datum: 2026-10-01
> Status: **Belegt** (neuro-symbolisches Prinzip, Inferenz-vor-Validierung) + **Auftrag** (Loop-Fixierung, FAIL→LLM)
> Prinzip: Keine Erfindungen (§6).
> Doku: `skills/cognize/SKILL.md` (via L4-Mechanik, Version v2)

## 1. Quellen (verifiziert, HTTP 200)

| Quelle | Kernaussage (wörtlich/nah) | Link |
|---|---|---|
| **AWS Semantic Layer** | „The **neurosymbolic approach** combines deterministic symbolic reasoning with probabilistic LLM capabilities to deliver Accuracy, Consistency, and Explainability (ACE)"; Agents brauchen „structured, verifiable knowledge to make decisions, **validate actions**, and provide **auditable reasoning chains**"; „SHACL validators for constraint enforcement", ELK/HermiT für OWL | https://docs.aws.amazon.com/prescriptive-guidance/latest/semantic-layer-agentic-ai-ontology-reasoning-virtual-knowledge-graph/semantic-layer-agentic-ai-ontology-reasoning-virtual-knowledge-graph.html |
| **Swansea (Robaldo & Batsakis)** | erst **Inferenz** (SHACL-SPARQL-Regeln, Fixpunkt), dann **Validierung** (SHACL-Shapes); „SHACL shapes alone are insufficient" | https://www.semantic-web-journal.net/system/files/swj3959.pdf |
| W3C SHACL-AF | SPARQL-Rules (`CONSTRUCT-WHERE`) | https://www.w3.org/TR/shacl-af/#SPARQLRule |

## 2. Der feste Loop

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

## 3. Was ist belegt, was ist Auftrag?

| Aussage | Status |
|---|---|
| Neuro-symbolisch: deterministisches Symbolic + probabilistisches LLM | **Belegt** (AWS) |
| Symbolic **validiert** LLM-Aktionen; auditable reasoning chains | **Belegt** (AWS) |
| Inferenz **vor** Validierung (SHACL-SPARQL → SHACL) | **Belegt** (Swansea) |
| Commit nur bei PASS | **Belegt** (Prinzip: „validate actions" vor Ausführung) |
| **FAIL → zurück an LLM** (Re-Proposal-Schleife) | **Auftrag** (Loop-Fixierung; AWS nennt „human-in-the-loop" und Validierung, nicht explizit die Re-Proposal-Kante) |
| Konkrete Ablage/Provenienz | **Auftrag** |

> **Ehrlich:** AWS belegt die neuro-symbolische Kombination und das Validieren
> von Aktionen; die **explizite Rückkante FAIL→LLM** ist eine Projekt-Entscheidung
> (Auftrag), die das belegte „validate before commit" zu einem festen Loop macht.

## 4. Umsetzung

- `skills/cognize/SKILL.md`: neuer Abschnitt **„Fester Loop: LLM → Symbolic → Commit"**;
  Guardrail 8 (kein Commit ohne PASS; FAIL → LLM).
- Angewandt über die **L4-Mechanik** (`skills/procedural_memory.py`):
  `cognize` → `versions/v2/`, Audit-Eintrag in `skills/AUDIT.md`.

## 5. Selbsttest / Beleg der Anwendung

```text
propose_update: {'applied': True, 'status': 'approved', 'version': 'v2'}
skills/cognize/versions/: v1  v2
AUDIT: | ... | skills/cognize/SKILL.md | update applied (v2) | Fester LLM→Symbolic→Commit-Loop dokumentiert (AWS Semantic Layer + Swansea) |
YAML cognize: OK
```

## 6. Bezug zu bestehenden Artefakten

- Inferenz-vor-Validierung: `ergebnisse/inferenz-shacl.md` + `ergebnisse/inferenz-shacl-test.md`.
- Inferenz-Ablage: `knowledge/cognition/inference-001..003.md`.
- L4-Versionierung/Audit: `skills/README.md`, `ergebnisse/procedural-memory.md`.

## 7. Quellen (HTTP 200, 2026-10-01)

- AWS Semantic Layer (Prescriptive Guidance)
- https://www.semantic-web-journal.net/system/files/swj3959.pdf (Swansea)
- https://www.w3.org/TR/shacl-af/#SPARQLRule
