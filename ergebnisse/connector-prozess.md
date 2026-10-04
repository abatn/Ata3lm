# Connector-Prozess-Lücken (SHACL/W3C)

> Datum: 2026-10-03 · Status: **Auftrag** (Zuordnung) + **Belegt** (W3C SHACL).
> Ziel: jeder Connector nennt den Prozess, den er bedient (validierbare Schnittstelle).

## 1. Quelle (verifiziert)

- **W3C SHACL (Shapes Constraint Language):** W3C Recommendation 20 July 2017 —
  https://www.w3.org/TR/shacl/ (Abstract: „a language for validating RDF graphs
  against a set of conditions … provided as shapes").
- Zuordnung (Auftrag): `ergebnisse/verbindungen-diagramm.md` §5, `AGENTS.md` Connector-Tabelle.

**Ehrlicher Hinweis:** Der Auftrag nennt „16 Connectoren"; real sind es **17**
(`ls connectors/*.md`). Ein **SHACL-MCP-Server** (pyshacl) ist **nicht** implementiert —
die Relation wird als **SHACL-Shape + Test** erzwungen (siehe §3).

## 2. Connector → Prozess (Auftrag)

| Connector | Prozess (`data/memory/`) |
|---|---|
| affective-signals | `trust.py` |
| agento-ariadne | `shared_memory.py` |
| cca-framework | `reflective_agent.py` |
| cognee-memory | `reflective_agent.py` |
| cognee-validation | `reflective_agent.py` |
| consistency-gap | `evaluator_version.py` |
| fast-write-routing | `fast_write_router.py` |
| gaama | `lru_cache.py` |
| goedel-agent | `reflective_agent.py` |
| governance-mcp | `bias_monitor.py` |
| hela-evolution | `reflective_agent.py` |
| hela-semantic | `reflective_agent.py` |
| htac-agentdice | `pipeline.py` |
| mars-seaa | `bias_monitor.py` |
| observer-agent | `ingestion_hook.py` |
| react | `pipeline.py` |
| reflexion-trace | `reflective_agent.py` |

In jede `connectors/*.md` wurde ein Abschnitt `## Prozess (Aufruf) [Auftrag]` eingefügt.

## 3. SHACL-Shape (Validierungsidee, W3C)

Die Invariante „jeder Connector hat ≥ 1 Prozess" als SHACL-Shape (minCount 1):

```turtle
@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix ex: <http://example.org/connector#> .

ex:ConnectorShape a sh:NodeShape ;
  sh:targetClass ex:Connector ;
  sh:property [
    sh:path ex:process ;
    sh:minCount 1 ;
    sh:nodeKind sh:IRI ;
  ] .
```

## 4. Test

`tests/test_connector_prozess.py` (offline): genau **17** Connectoren; jeder enthält
`## Prozess` + ein `*.py`; jedes genannte Modul existiert in `data/memory/`.

## 5. Gate (§9)

- Connector-/Interface-Änderung → **approved** (Batnini, 2026-10-03).
- Ehrlich: Die Prozess-Zuordnung ist **Auftrag**, kein Paper-Claim; SHACL dient als
  Validierungs-**Rahmen** (Shape), nicht als laufender MCP-Server.
