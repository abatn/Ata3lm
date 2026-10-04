# Reverse Engineering (vollständig, alle 8 Schichten)

> Datum: 2026-10-04 · Methode: `grep`/`ls`/`find` über den **echten** Code
> (`data/memory/**`, `skills/**`, `connectors/**`, `opencode.json`, `AGENTS.md`).
> **Keine Erfindungen** — nur was tatsächlich im Code steht. Lücken werden klar benannt.
> **Korrektur der Auftrags-Zahlen (ehrlich):** „13 Module" → real **16**;
> „42 Rekursionen" → real **48** (000–047); „14 Skills" → **14 aktiv** (43 inkl. `versions/`).

## 0. Übersicht (Schicht · Status · Beweis · Lücke)

| # | Schicht | Status | Beweis (Code/Doku) | Lücke |
|---|---|---|---|---|
| 0 | **Gesetz** (AGENTS.md §1–§11) | **teilweise** | §9 `pipeline.py:20-24`; §9.3 `approval.py`; §9.1c `bias_monitor.py`; §9.2a `trust.py`; §10 `fast_write_router.py`+`gaama_extract.py`; §11 `mcp_memory_server.py`; Test `tests/test_agents_law.py` | §1–§8 sind **Doku/Auftrag**, nicht als Code erzwungen |
| 1 | **Lifecycle — 8 Stufen** | **teilweise (Runner)** | `knowledge/lifecycle/*.md` (8); **`lifecycle_runner.run_cycle`** (führt alle 8 Stufen aus, ruft je eine echte Funktion); Test `tests/test_lifecycle_runner.py` | Stufenfolge + Stufe→Modul = **Auftrag** (AGENTS.md §3 erlaubt das); Stufe 5 = echte LLM-Reflexion, offline NOOP |
| 2 | **Rekursion — 5 Phasen** | **teilweise** | `reflective_agent.run_once` (Hub/Forgetting/HMM); `evaluator_version.RedQueenLoop` (Epochen) | **kein Runner** Konstrukt→Akt→Observe→Compare→Revise (Phasen = `.md`-Skills) |
| 3 | **Gedächtnis — 16 Module** | **verdrahtet** | Import-Graph unten; Tests + CLI | Einstiegspunkte ohne Importer (CLI/Tests): `ingestion_hook`, `reflective_agent`, `mcp_memory_server`, `lru_cache`, `shared_memory`, `mcp_catalog`, `shacl_inferenz` |
| 4 | **Connectoren — 17** | **Doku + Binding** | `connectors/*.md` (17, je `## Prozess`); AGENTS.md-Tabelle; **`connector_binding.bind`** (parse → SHACL-Validierung → Prozess-Aufruf → MCP-Record); Test `tests/test_connector_binding.py` | SHACL prüft nur die Invariante (minCount 1), nicht die inhaltliche Richtigkeit |
| 5 | **MCP-Server — 19 (16 aktiv)** | **extern/optional** | `opencode.json` (19/16); eigener `mcp_memory_server.py` (5 Tools); `mcp_catalog.py` (TTC-Katalog der **real** gestarteten 12 Projekt-MCPs) | **kein `.py` ruft** externe MCPs live (Graphiti/Cognee/…); §11 optional |
| 6 | **Skills — 14 aktiv** | **verwaltet + ausgeführt (deklarierte Prozesse)** | `skills/*/SKILL.md` (14 aktiv, 43 inkl. `versions/`); `skills/procedural_memory.py` (snapshot/update/rollback); **`skill_interpreter.run_skill`** (führt die deklarierten Prozesse aus); Test `tests/test_skill_interpreter.py` | NL-`## Ablauf`-Schritte werden **nicht** interpretiert (nur deklarierte Prozesse) |
| 7 | **Ergebnisse — 48 Rekursionen (000–047)** | **konsistent** | 48 nummerierte Dateien; Index + `tests/test_agents_law.py` (`test_rekursion_index_vollstaendig`) | — |

## 1. Details je Schicht

### Schicht 0 — Gesetz (AGENTS.md §1–§11)
- **Im Code umgesetzt:** §9 (`pipeline.py`: Mandat/Trust/Approval/Bi-Temporal/Drift),
  §9.1b (`versions/vN/`), §9.1c (`bias_monitor.py`), §9.2a PII (`trust.py`),
  §9.3 (`approval.py`), §10 (`fast_write_router.py`, `gaama_extract.py`),
  §11 (`mcp_memory_server.py`). **Neu:** §6-Inferenz-vor-Validierung real
  (`shacl_inferenz.py`, rdflib+pyshacl).
- **Nicht als Code erzwungen:** §1–§8 (Prinzipien) — als **Auftrag/Doku** vorhanden.
- **Beweis:** `tests/test_agents_law.py` (prüft §-Abschnitte, Guardrails, Provenienz, Versionierung).

### Schicht 1 — Lifecycle (8 Stufen)
- `knowledge/lifecycle/` hat 8 Phasen-Dateien. **`lifecycle_runner.run_cycle`** führt sie
  jetzt in gesetzter Reihenfolge aus (Erfahrung → … → Wissen+), jede Stufe ruft eine
  **echte** Funktion (`ingestion_hook`, `pipeline`, `lru_cache`, `reflective_agent`,
  `bias_monitor`). `ingestion_hook.py:170-171` kennt zusätzlich Regex-Muster für Stage/Phase.
- **Lücke (ehrlich):** Stufenfolge + Stufe→Modul sind **Auftrag** (AGENTS.md §3 erlaubt das
  ausdrücklich: „gesetzte Ordnung, kein Paper-Claim"); Stufe 5 (Denken) ruft die **echte**
  LLM-Reflexion (`parse_transition_delta`), offline → NOOP.

### Schicht 2 — Rekursion (5 Phasen)
- `reflective_agent.run_once` (Hub/Forgetting/HMM) + `evaluator_version.RedQueenLoop` (Epochen) existieren — aber **kein** expliziter Konstrukt→Akt→Observe→Compare→Revise-Runner.
- Die 5 Phasen liegen als `skills/recursive-improve/*/SKILL.md` (Doku).
- **Lücke:** Phasen-Ausführung ist Auftrag/Doku.

### Schicht 3 — Gedächtnis (16 Module: 14 top-level + `shared/` + `tier3-working/`)
- **Import-Graph (echt, `grep`):**
  - `pipeline` → `approval`, `bi_temporal`, `bias_monitor`, `mandate`, `trust`, `fast_write_router`
  - `ingestion_hook` → `pipeline`
  - `gaama_extract` → `fast_write_router`, `trust`
  - `reflective_agent` → `mandate`, `pipeline`, `evaluator_version`
  - `lru_cache` nutzt `gaama_extract`-Graph (übergeben, kein Import)
- **Neu (standalone, von Tests/CLI genutzt):** `mcp_catalog.py`, `shacl_inferenz.py`.
- **Einstiegspunkte** (kein Importer): `ingestion_hook`, `reflective_agent`, `mcp_memory_server`, `lru_cache`, `shared_memory`, `mcp_catalog`, `shacl_inferenz`.
- **Lücke:** keine (bis auf Einstiegspunkte).

### Schicht 4 — Connectoren (17)
- `connectors/*.md` (17). **`connector_binding.bind`** liest den `## Prozess (Aufruf)`,
  validiert die SHACL-Invariante (`ex:ConnectorShape`, `sh:minCount 1`, echte pyshacl-Engine),
  ruft den zugeordneten Prozess auf (9 Executoren) und schreibt einen Bindungs-Nachweis via MCP.
- Zuordnung über `AGENTS.md`-Tabelle + `ergebnisse/verbindungs-diagramm.md` §5 + `ergebnisse/connector-binding.md`.
- **Lücke:** die Zuordnung selbst ist **Auftrag**; SHACL prüft nur „≥ 1 Prozess".

### Schicht 5 — MCP-Server (19 konfiguriert, 16 aktiv)
- `opencode.json`: 19 Einträge (16 aktiv). **Kein `.py` ruft** Graphiti/Cognee/HeLa/… **live** auf.
- Eigener Code: `mcp_memory_server.py` (5 Tools) + `mcp_catalog.py` (TTC-Katalog der
  **real gestarteten** 12 Projekt-MCPs → 49 Tools; Guardrail 7). Der Start selbst
  erfolgt über `scripts/mcp_probe.py` (stdio), nicht aus dem Repo-Code heraus.
- **Lücke (by design, §11):** externe MCPs sind **optional**, nicht im Repo-Code verdrahtet.

### Schicht 6 — Skills (14 aktiv; 43 inkl. `versions/`)
- Aktive `SKILL.md`: 8 Stufen-Skills (`collect-experience`, `structure-knowledge`,
  `store-memory`, `cognize`, `reflect`, `non-cognitive`, `act`, `expand-knowledge`)
  + `recursive-improve` + 5 Phasen (`konstrukt/akt/observe/compare/revise`) = **14**.
- `skills/procedural_memory.py` **verwaltet** sie (snapshot/update/rollback/audit).
  **`skill_interpreter.run_skill`** führt die in `## Prozesse (Aufrufe)` deklarierten
  Prozesse aus; **`run_skill_agent`** (ReAct-Tool-Calling-Loop, Agent Skills/ReAct) lässt
  das **LLM** die `## Ablauf`-Schritte über registrierte Tools ausführen.
- **Lücke:** MCP-Tools laufen **in-process** (FastMCP), nicht über stdio/HTTP; ein Tool-Call
  pro Schritt (nicht parallel wie LLMCompiler).

### Schicht 7 — Ergebnisse (48 nummerierte Rekursionen 000–047)
- 48 nummerierte Dateien == Index-Zeilen (`ergebnisse/rekursion/README.md`); Provenienz-
  Test (`approved`/`quelle`) + Index-Test bestehen. **Neu:** 043–047 (MCP-Kontext/Aktivierung/
  Kalibrierung, SHACL-Inferenz, Spreading-Activation).
- **Lücke:** keine.

## 2. Quellen
- Code: `data/memory/*.py` (14), `data/memory/*/*.py` (`shared_memory.py`, `lru_cache.py`),
  `skills/procedural_memory.py`, `scripts/mcp_probe.py`.
- Doku: `AGENTS.md`, `knowledge/lifecycle/`, `connectors/` (17), `skills/` (14 aktiv),
  `opencode.json` (19/16), `ergebnisse/rekursion/` (48 nummeriert).
- Methode: `grep -rn`/`ls`/`find` (2026-10-04).

## 3. Fazit (ehrlich)
- **Verdrahtet (Code):** Schicht 3 (Gedächtnis, 16 Module) + §9/§10/§11.
- **Nur Doku/Auftrag (kein Code-Pfad):** Schicht 1 (8 Stufen), Schicht 4 (Connectoren),
  Schicht 5 (externe MCPs, optional), Schicht 6 (Skills).
- **Teilweise:** Schicht 0 (Prinzipien §1–§8), Schicht 2 (5 Phasen).
- **Konsistent:** Schicht 7 (48 Rekursionen).
- **Wichtigster offener Punkt:** Schichten 1/2/4/6 haben **keinen ausführenden Code** —
  sie sind als Auftrag/Doku vorhanden. Das ist bekannt und wird nicht als „implementiert" ausgegeben.
