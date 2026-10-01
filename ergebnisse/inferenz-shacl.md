# Inferenz-Schicht vor SHACL-Validierung (cognize-Skill)

> Datum: 2026-10-01
> Status: **Belegt** (Mechanik) + **Auftrag** (Umsetzung im Skill)
> Prinzip: Keine Erfindungen (§6). Quelle unten wörtlich belegt.

## Quelle (verifiziert, HTTP 200)

Robaldo, L. & Batsakis, S. — **HRC School of Law, Swansea University** (Wales, UK)
— „On the interplay between validation and inference in SHACL – an investigation
on the Time Ontology", *Semantic Web Journal*.

> „To detect the identified invalid knowledge graphs, it is necessary to infer
> specific additional triples from the explicitly asserted ones. These triples
> cannot be derived internally by SHACL shapes. **Once the inferred triples are
> available, SHACL shapes can then be used to identify invalid patterns within
> the inferred knowledge graph.** In this sense, the inferred triples serve as
> 'intermediate results' required for the final validation, which cannot be
> accomplished by SHACL shapes in a single step."

Weitere belegte Punkte aus derselben Quelle:
- „SHACL shapes alone are insufficient to validate even relatively simple
  knowledge graphs" (Beispiel: Zeitintervalle, die vor ihrem Start enden).
- Vorgehen: **erst Inferenz** (SHACL-SPARQL-Regeln, `CONSTRUCT-WHERE`),
  **dann Validierung** (SHACL-Shapes, `SELECT-WHERE`).
- Regeln werden **iterativ bis zum Fixpunkt** angewendet (analog OWL-Reasoner
  wie HermiT), nicht nur einmal.
- SHACL Core = einfache Constraints (Kardinalität, Wertebereich, Datentyp);
  SHACL-SPARQL = komplexe Regeln (Zeitintervall-Logik, transitive Beziehungen).
- Das Paper wählt SHACL-SPARQL (nicht OWL/SWRL); OWL wird als mögliche, aber
  laut Autoren weniger geeignete Alternative diskutiert.

Zweite Swansea-2024-Arbeit (Kontext): Anim, Robaldo, Wyner — „A SHACL-Based
Approach for Enhancing Automated Compliance Checking with RDF Data"
(*Information* 15(12):759, 2024) — SHACL-SPARQL-Regeln (`sh:order`) für
temporale/aggregierte Compliance.

## Aufgabe 1 — Inferenz vor Validierung

- **Vor SHACL:** SHACL-SPARQL-Regeln (`CONSTRUCT-WHERE`) laufen bis zum Fixpunkt
  und materialisieren implizite Konsequenzen (alternativ SPARQL-CONSTRUCT oder
  OWL-Reasoner).
- **Danach:** SHACL-Validierung (Core + SHACL-SPARQL) **auf dem materialisierten
  Graphen**.
- **Grund:** SHACL prüft nur explizite Triples; bestimmte Invaliditäten
  (z. B. Zeitintervall endet vor Start) werden erst durch Inferenz sichtbar.
- **Umsetzung:** `skills/cognize/SKILL.md` (Ablauf Schritt 3 vor Schritt 4).

## Aufgabe 2 — Inferenz-Kette dokumentieren

- Pro Inferenz: welche **Regel** (Regel-ID) hat welche **neuen Triples** erzeugt?
- Ablage: `knowledge/cognition/inference-<id>.md` (Provenienz als
  First-Class State).
- Format: **Input-Triples, Regel, Output-Triples** (+ Quelle, Status).
- **Umsetzung:** `knowledge/cognition/README.md` (Abschnitt „Inferenz-Kette").

## Aufgabe 3 — SHACL Core vs. SHACL-SPARQL

| Zweck | Sprachmittel |
|---|---|
| Einfache Constraints (Kardinalität, Datentyp, Wertebereich) | **SHACL Core** |
| Komplexe Regeln (Zeitintervall-Logik, transitive Beziehungen) | **SHACL-SPARQL** |

- Quelle (wörtlich): „Once the inferred triples are available, SHACL shapes can
  then be used to identify invalid patterns."

## Aufgabe 4 — Test

- Simulation: Fall, den SHACL allein **nicht** erkennt; mit Inferenz-Schicht
  wird die Invalidität **sichtbar**.
- Datei: `ergebnisse/inferenz-shacl-test.md` (mit Lauf-Ausgabe).

## Ausgabe

| Artefakt | Art |
|---|---|
| `skills/cognize/SKILL.md` | erweitert (Inferenz-Schritt 3, Guardrail 7, Quelle) |
| `knowledge/cognition/README.md` | erweitert (Inferenz-Ketten-Format) |
| `ergebnisse/inferenz-shacl.md` | neu (dieses Dokument) |
| `ergebnisse/inferenz-shacl-test.md` | neu (Test/Simulation) |

## Status-Trennung

| Aussage | Status |
|---|---|
| SHACL allein reicht für bestimmte Invaliditäten nicht (Inferenz nötig) | **Belegt** (Swansea) |
| Iterative Inferenz bis Fixpunkt, dann Validierung | **Belegt** (Swansea) |
| SHACL Core einfach / SHACL-SPARQL komplex | **Belegt** (Swansea) |
| Umsetzung im cognize-Skill + Ablageformat | **Auftrag** (Projekt) |

## Quellen (alle HTTP 200, 2026-10-01)

- https://www.semantic-web-journal.net/system/files/swj3959.pdf (Swansea, SHACL-Inferenz/Validierung)
- https://semantic-web-journal.net/content/interplay-between-validation-and-inference-shacl-investigation-time-ontology-0
- https://github.com/liviorobaldo/TimeOntologyInSHACL (Referenz-Implementierung)
- https://www.w3.org/TR/shacl-af/#SPARQLRule (SHACL Advanced Features, SPARQL-Rules)
- https://docs.aws.amazon.com/prescriptive-guidance/latest/semantic-layer-agentic-ai-ontology-reasoning-virtual-knowledge-graph/semantic-layer-agentic-ai-ontology-reasoning-virtual-knowledge-graph.html (AWS Semantic Layer, symbolische Validierung)
