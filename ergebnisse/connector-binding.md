# Connector-Binding (`data/memory/connector_binding.py`)

> Datum: 2026-10-04 · Status: **Belegt** (W3C SHACL) + **Auftrag** (Zuordnung).
> Guardrail 7: echte Ausführung. Ziel `g`: Schicht-4-Lücke schließen — Connectoren an den
> **Code** binden (statt nur Doku).

## 1. Quellen (verifiziert, §6)

- **W3C SHACL** (Shapes Constraint Language, Rec. 2017): https://www.w3.org/TR/shacl/
  („a language for validating RDF graphs against a set of conditions … shapes").
- **AGENTS.md §5** (Wie eine Wolke): Zuordnung als revidierbares Schema.
- **Zuordnung** Connector → Prozess: `ergebnisse/connector-prozess.md` + `## Prozess` in jeder Datei.

## 2. Zuordnung (17 Connectoren → 9 Prozesse, Auftrag)

| Prozess (`data/memory/`) | Connectoren |
|---|---|
| `reflective_agent.py` | cca-framework, cognee-memory, cognee-validation, goedel-agent, hela-evolution, hela-semantic, reflexion-trace |
| `pipeline.py` | htac-agentdice, react |
| `bias_monitor.py` | governance-mcp, mars-seaa |
| `trust.py` | affective-signals |
| `shared_memory.py` | agento-ariadne |
| `evaluator_version.py` | consistency-gap |
| `fast_write_router.py` | fast-write-routing |
| `lru_cache.py` | gaama |
| `ingestion_hook.py` | observer-agent |

## 3. Ablauf

```text
parse_connector(connectors/*.md)  -> {name, process, phase}   (aus `## Prozess (Aufruf)`)
validate_connector(spec)          -> SHACL: ex:ConnectorShape (sh:minCount 1), echte pyshacl-Engine
bind(...)                         -> ruft den Prozess-Executor auf
_record_binding(...)              -> MCP (in-process FastMCP, memory.write), §11-Fallback lokal
```

- **SHACL/W3C:** Die Invariante „jeder Connector hat ≥ 1 Prozess" wird mit **pyshacl**
  geprüft (`sh:minCount 1` auf `ex:process`).
- **Integration `pipeline.py`:** pipeline-gebundene Connectoren (htac-agentdice, react)
  laufen durch `pipeline.route_and_store`.
- **Integration `mcp_memory_server.py`:** jeder Bindungs-Nachweis wird via MCP
  (`memory.write`, in-process FastMCP) geschrieben.

## 4. Echte Ausgabe (CLI, 2026-10-04)

```text
bind(connectors/htac-agentdice.md):
  process = pipeline.py
  shacl   = conforms: true (ex:ConnectorShape, sh:minCount 1)
  executed= true -> ok=true action=write-new
            steps: mandate=ALLOW · fwr=write-new · trust=PII entfernt · write=write-new
  recorded= via=mcp  key=binding-htac-agentdice.md
```

## 5. Test (echt, Guardrail 7)

`tests/test_connector_binding.py` (7 Tests): parse (real/ohne Prozess), SHACL-Validierung
(conforms True/False), `bind` (pipeline + MCP-Record), unbekannter Prozess, **`bind_all`
(17 Connectoren → alle 9 Executoren)**, MCP-Fallback (§11).
`connector_binding.py`: **100 %** Line+Branch.

## 6. Gate (§9)

- Interface-Änderung (neues Modul) → **approved** (Batnini, Auftrag).
- Guardrail 3: Provenienz `ergebnisse/rekursion/051-connector-binding.md`.
- Guardrail 6: kein Commit ohne Erlaubnis. §9.1b: `AGENTS.md` unverändert.
- **Ehrliche Grenzen:** Die Zuordnung ist **Auftrag** (kein Paper-Claim); die SHACL-Prüfung
  validiert die Invariante (`minCount 1`), nicht die inhaltliche Richtigkeit der Zuordnung.
