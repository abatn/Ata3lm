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

## Echte Ausführung mit Engine (2026-10-04, Guardrail 7)

> Engine: `rdflib 7.6.0` (SPARQL-CONSTRUCT) + `pyshacl 0.40.1` (SHACL-Shapes), im venv installiert.
> Code: `data/memory/shacl_inferenz.py` · Test: `tests/test_shacl_inferenz.py` (3 Tests, echt).

**Zitat verifiziert** (swj3959, S. 5, wörtlich):
> „Similar to standard OWL reasoners such as HermiT, which repeatedly apply OWL
> axioms until no further triples can be inferred, our approach also **iteratively
> applies SHACL-SPARQL rules until the inferred graph reaches closure, prior to
> validation.**"

**Korrektur (ehrlich, §6):** Die Angabe „max 10 Runden, wie SHACL-AF §8.3" ist
**nicht belegt**. SHACL-AF §8.3 ist das *sh:Rules Entailment Regime*; §8.4 sagt
ausdrücklich: „only covers a single 'iteration' over all rules … The latter is
left to future work." Die **offiziellen** Rundengrenzen kommen aus den **Engines**:

| Quelle | Wert | Beleg |
|---|---|---|
| **pyshacl 0.40.1** (unsere Engine) | **100** | `RULES_ITERATE_LIMIT = 100` — `pyshacl/rules/__init__.py:89` |
| TopBraid SHACL (`shaclinfer`) | Default **1** | README: `-maxiterations 1` |
| Triply SHACL Rules | Default **0** | Doku: `maxIterations` (0 = keine Iteration) |
| W3C SHACL 1.2 Rules | impl.-abhängig | „pre-configured maximum iteration count" |
| HuggingFace | — | kein SHACL-Iterationswert gefunden |

Der Cap wird daher **aus der Engine importiert** (`DEFAULT_MAX_ROUNDS = RULES_ITERATE_LIMIT`
= **100**), kein Paper-Claim.

### Ablauf (real)

```text
1) Inferenz:  SPARQL-CONSTRUCT-Regeln iterativ bis Fixpunkt (Cap = pyshacl 100)
2) Validierung: pyshacl prüft den materialisierten Graphen
```

### Lauf-Ausgabe (echt)

```text
SHACL allein (explizit): conforms = True      # i2 (Ende<Beginn) NICHT erkannt
Nach Inferenz:           conforms = False     # i2 erkannt
  Runde 1: 1 neues Triple -> ex:hasNegativeDuration
  Runde 2: 0 neue Triples  -> Fixpunkt erreicht
Report: "More than 0 values on ex:i2->ex:hasNegativeDuration"
```

### Materialisierte Inferenzen / geprüfte Constraints

| Regel | CONSTRUCT (Kurz) | materialisiert (real) |
|---|---|---|
| R1 | `?i hasNegativeDuration true` WHERE `?te < ?tb` | `ex:i2 hasNegativeDuration true` |

| Shape | Constraint | Ergebnis |
|---|---|---|
| `ex:NoNegativeDurationShape` | `sh:path ex:hasNegativeDuration ; sh:maxCount 0` | **verletzt** (`ex:i2`) |

Ergebnis: Dasselbe Muster wie im Paper — die verletzende Information steht **nicht**
im expliziten Graphen; erst die Fixpunkt-Inferenz macht sie für SHACL sichtbar.

## Quellen (alle HTTP 200, 2026-10-01; swj3959 erneut 2026-10-04)

- https://www.semantic-web-journal.net/system/files/swj3959.pdf (Swansea, SHACL-Inferenz/Validierung)
- https://semantic-web-journal.net/content/interplay-between-validation-and-inference-shacl-investigation-time-ontology-0
- https://github.com/liviorobaldo/TimeOntologyInSHACL (Referenz-Implementierung)
- https://www.w3.org/TR/shacl-af/#SPARQLRule (SHACL Advanced Features, SPARQL-Rules)
- https://docs.aws.amazon.com/prescriptive-guidance/latest/semantic-layer-agentic-ai-ontology-reasoning-virtual-knowledge-graph/semantic-layer-agentic-ai-ontology-reasoning-virtual-knowledge-graph.html (AWS Semantic Layer, symbolische Validierung)
