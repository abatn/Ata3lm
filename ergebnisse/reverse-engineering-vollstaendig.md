# Reverse Engineering (vollständig, alle 8 Schichten)

> Datum: 2026-10-04 · Methode: `ast`/`grep`/`ls` über den **echten** Code
> (`data/memory/**`, `skills/**`, `connectors/**`, `opencode.json`, `AGENTS.md`, `ergebnisse/rekursion/**`).
> **Keine Erfindungen** — nur was tatsächlich im Code/Doku steht. Lücken werden klar benannt.
> **Korrektur der Auftrags-Zahlen (ehrlich):** „13 Module" → real **20**; „42 Rekursionen" → real
> **56** (000–055); „17 Connectoren" ✓; „19 MCP" ✓; „14 Skills" ✓.
> **Selbst-Korrektur:** Ein früherer Analyse-Lauf zählte **19** Module (Glob übersah Unterordner);
> real sind es **20** (18 top-level + `shared/` + `tier3-working/`).

## 0. Übersicht (Schicht · Status · Beweis · Lücke)

| # | Schicht | Status | Beweis (Code/Doku) | Lücke |
|---|---|---|---|---|
| 0 | **Gesetz** (AGENTS.md §1–§11) | **teilweise** | §9 `pipeline.route_and_store:59`; §9.3 `approval.approve:45`/`finalize:76`; §9.1c `bias_monitor.observe:111`; §9.2a `trust.minimize:49`; §10 `fast_write_router.classify:223`/`apply_write_action:153`; §11 `mcp_memory_server.build_server:161`; §6 `shacl_inferenz.pipeline:56`; Test `tests/test_agents_law.py` | §1–§8 sind **Doku/Auftrag**, nicht als Code erzwungen |
| 1 | **Lifecycle — 8 Stufen** | **teilweise (Runner)** | `lifecycle_runner.run_cycle:153` ruft je Stufe eine echte Funktion: `_stage_erfahrung:77` … `_stage_wissen_plus:135` | Stufenfolge = **Auftrag**; Stufe 5 = echte LLM-Reflexion, offline NOOP |
| 2 | **Rekursion — 5 Phasen** | **teilweise** | `reflective_agent`: `parse_transition_delta:67`, `detect_hubs:224`, `detect_forgetting:229`, `resolve_conflict:247`, `run_once:380`; `evaluator_version.RedQueenLoop:411` | **kein Runner** Konstrukt→Akt→Observe→Compare→Revise; Phasen = `.md`-Skills |
| 3 | **Gedächtnis — 20 Module** | **verdrahtet** | Import-Graph unten; 20 Module, 294 defs gesamt | Einstiegspunkte ohne Importer (CLI/Tests) |
| 4 | **Connectoren — 17** | **Doku + Binding** | `connectors/*.md` (17, je `## Prozess`); `connector_binding.bind:...` (SHACL + Prozess-Aufruf) | Zuordnung = Auftrag; SHACL prüft nur `minCount 1` |
| 5 | **MCP-Server — 19 (16 aktiv)** | **extern/optional + Live-Binding** | `opencode.json` (19/16); `mcp_memory_server` (5 Tools); `mcp_live_binding.call_tool_live` (stdio `tools/call`) | Live braucht Deps/Keys (§11 optional) |
| 6 | **Skills — 14 aktiv** | **verwaltet + ausgeführt** | `skills/procedural_memory.py` (Versionierung); `skill_interpreter.run_skill`/`run_skill_agent` (ReAct) | NL-`## Ablauf` nur via LLM-Tool-Calling, nicht garantiert |
| 7 | **Ergebnisse — 56 Rekursionen (000–055)** | **konsistent** | 56 nummerierte Dateien == Index; `tests/test_agents_law.py::test_provenienz_jeder_rekursion` | — |

## 1. Details je Schicht

### Schicht 0 — Gesetz (AGENTS.md §1–§11)
- **Daten-Analyse:** `AGENTS.md` = **411 Zeilen**; `data/memory/mandate.md` = **58 Zeilen**.
- **Im Code umgesetzt (def + Zeile):** §9 `pipeline.route_and_store:59` (+ `drift_gate:44`),
  §9.1b Versionierung (`tier1-base/versions/vN/`), §9.1c `bias_monitor.observe:111`,
  §9.2a `trust.minimize:49`, §9.3 `approval.approve:45`/`finalize:76`, §10
  `fast_write_router.classify:223`/`apply_write_action:153`, §11 `mcp_memory_server.build_server:161`,
  §6 `shacl_inferenz.pipeline:56`/`validate:48`.
- **Nicht als Code erzwungen:** §1–§8 (Prinzipien) — Doku/Auftrag.
- **Widerspruch (Doku↔Code):** `ergebnisse/connector-prozess.md` behauptet „Ein SHACL-MCP-Server
  (pyshacl) ist **nicht** implementiert" — real nutzen `shacl_inferenz.py:48` und
  `connector_binding.validate_connector` **pyshacl** (Doku veraltet).

### Schicht 1 — Lifecycle (8 Stufen)
- **Daten-Analyse (`knowledge/lifecycle/`):** experience 104 · wissen 87 · gedaechtnis 151 ·
  kognition 118 · denken 165 · nicht-kognition 125 · handeln 112 · wissen-plus 117 Zeilen (8 Dateien).
- **Stufen-Funktionen (`lifecycle_runner.py`):** `_stage_erfahrung:77`, `_stage_wissen:85`,
  `_stage_gedaechtnis:90`, `_stage_kognition:105`, `_stage_denken:110`, `_stage_nicht_kognition:117`,
  `_stage_handeln:123`, `_stage_wissen_plus:135`, Orchestrator `run_cycle:153`.
- **Tote Stufen:** **keine** — jede `_stage_*` wird von `run_cycle` aufgerufen.
- **Lücke:** Stufenfolge + Stufe→Modul = **Auftrag** (AGENTS.md §3 erlaubt das).

### Schicht 2 — Rekursion (5 Phasen)
- **Daten-Analyse (`knowledge/lifecycle/rekursion/`):** index 229 · konstrukt 149 · akt 112 ·
  observe 110 · compare 99 · revise 115 · wissenszyklus-8-stufen 172 Zeilen (7 Dateien).
- **Phasen-Funktionen:** Konstrukt→`reflective_agent.run_once:380`; Akt→`lifecycle_runner`/`pipeline`;
  Observe→`ingestion_hook`; Compare→`evaluator_version.RedQueenLoop:411`; Revise→
  `reflective_agent.parse_transition_delta:67`/`detect_hubs:224`.
- **Tote Phasen:** **keine** — die Phasen sind `.md`-Skills; **kein expliziter Phasen-Runner**
  (Lücke, Auftrag/Doku).

### Schicht 3 — Gedächtnis (20 Module)
- **Daten-Analyse (`data/memory/`):** 20 Module (18 top-level + `shared/` + `tier3-working/`),
  **294 defs** gesamt. Größte:
  `evaluator_version.py` 1077 Z., 64 defs · `reflective_agent.py` 634 Z., 28 defs ·
  `ingestion_hook.py` 555 Z., 27 defs.
- **Import-Graph (echt):**
  - `pipeline` → approval, bi_temporal, bias_monitor, fast_write_router, mandate, trust
  - `connector_binding` → bias_monitor, evaluator_version, fast_write_router, ingestion_hook, mandate, mcp_memory_server, pipeline, reflective_agent, shacl_inferenz, trust
  - `lifecycle_runner` → bias_monitor, ingestion_hook, mandate, pipeline, reflective_agent
  - `skill_interpreter` → mandate, mcp_memory_server, pipeline
  - `reflective_agent` → evaluator_version, mandate, pipeline
  - `gaama_extract` → fast_write_router, trust · `ingestion_hook` → pipeline · `mcp_live_binding` → mcp_catalog
- **Tote Funktionen:** **keine** (Heuristik: jede def hat ≥1 Aufruf). Interne Helfer ohne
  **externen** Aufrufer (kein toter Code, nur nicht von außen genutzt): `_stage_*` (lifecycle_runner),
  `_p_*` (connector_binding), `_default_classify` (pipeline), `_frontmatter`/`_run_pipeline`/`_task_prompt`
  (skill_interpreter), `_server_params`/`_call` (mcp_live_binding), `validate_write` (shared_memory).
- **Einstiegspunkte ohne Importer (CLI/Tests):** `ingestion_hook`, `reflective_agent`,
  `mcp_memory_server`, `lru_cache`, `shared_memory`, `mcp_catalog`, `shacl_inferenz`,
  `mcp_live_binding`, `lifecycle_runner`, `skill_interpreter`, `connector_binding`.

### Schicht 4 — Connectoren (17)
- **Daten-Analyse (`connectors/`, 17 Dateien):** Zeilen + Refs — affective-signals 80 · agento-ariadne 86 ·
  cca-framework 127 · cognee-memory 75 · cognee-validation 64 · consistency-gap 55 · fast-write-routing 81 ·
  gaama 55 · goedel-agent 100 · governance-mcp 73 · hela-evolution 59 · hela-semantic 82 ·
  htac-agentdice 73 · mars-seaa 81 · observer-agent 62 · react 66 · reflexion-trace 80.
- **AGENTS.md-Referenzen:** die AGENTS.md-Tabelle nennt 12 (u. a. `agento-ariadne:395-396`,
  `hela-semantic:397-398`, `cognee-memory:399-400`, `mars-seaa:401-402`, `htac-agentdice:403-404`,
  `hela-evolution:405`, `affective-signals:407`, `fast-write-routing:408`, `gaama:409-410`,
  `governance-mcp:411`). **0 AGENTS.md-Refs:** cca-framework, consistency-gap, observer-agent, reflexion-trace
  (nur im Code/Binding bzw. Connector-Tabelle §5).
- **Tote Connectoren:** **keine** — jeder der 17 wird von `connector_binding.bind` gebunden
  (parse `## Prozess` → Prozess-Aufruf). `py-Refs=0` heißt nur „kein direkter Modulname im Code"
  (Connectoren sind `.md`); das Binding ist der Code-Pfad.

### Schicht 5 — MCP-Server (19, 16 aktiv)
- **Daten-Analyse (`opencode.json`):** **19 Einträge, 16 aktiv**. Deaktiviert (3): `context7`,
  `sqlalchemy-mcp`, `visuals-mcp`.
- **command-Aufrufe (Auszug):** `cognee` → `uvx`; `graphiti` → `uv`; `hela-mem`/`reflexion`/`react`/
  `mars`/`trace`/`godel-agent`/`agent-dice`/`adas`/`governance-mcp`/`memory` →
  `/home/opc/mcp-servers/<name>/.venv/bin/python …`; `n8n-mcp`/`obsidian`/`kubernetes` → `npx`;
  `livekit-docs` → URL (remote).
- **Tote MCPs:** die 3 **deaktivierten** (context7, sqlalchemy-mcp, visuals-mcp). Absolute
  Server-Binaries vorhanden (binary_ok). `memory` zeigt auf `hela-mem-mcp`-Venv (nicht auf den
  eigenen `mcp_memory_server.py`) — ehrliche Beobachtung.
- **Live-Aufruf:** `mcp_live_binding.call_tool_live` (stdio `tools/call`), Test `tests/test_mcp_live_binding.py`.

### Schicht 6 — Skills (14 aktiv)
- **Daten-Analyse (`skills/`):** 14 aktive `SKILL.md` — act 62 · cognize 162 · collect-experience 65 ·
  expand-knowledge 79 · non-cognitive 88 · recursive-improve 162 · akt 83 · compare 77 · konstrukt 108 ·
  observe 78 · revise 111 · reflect 103 · store-memory 88 · structure-knowledge 76 Zeilen.
- **Referenzen:** `skills/README.md` listet die 3 Regeln + Struktur; jeder Skill nennt seinen Prozess
  (`## Prozesse`); Test `tests/test_skills.py`.
- **Tote Skills:** **keine** — alle 14 sind gelistet; `skill_interpreter.run_skill`/`run_skill_agent`
  führen die deklarierten Prozesse aus.

### Schicht 7 — Ergebnisse (56 Rekursionen 000–055)
- **Daten-Analyse:** **56 nummerierte** Dateien (000–055) == Index-Zeilen; Status: 56× „approved"
  (Header), 6× „rejected" (als Begriff), 11× „pending" (als Begriff) — mehrere Wörter pro Datei möglich.
- **Konsistenz:** `tests/test_agents_law.py::test_provenienz_jeder_rekursion` (Freigabe + Quelle je Datei)
  + Index-Vollständigkeit bestehen.
- **Widerspruch (Doku↔Code):** Auftrag nennt „42 Rekursionen (000–042)" — real **56** (000–055).
  Die bekannte Hub-Abweichung (`reflective_agent` fixe Klasse `write-new`) ist in
  `ergebnisse/verbindungen-diagramm.md` §6 dokumentiert (kein stiller Widerspruch).

## 2. Fazit (ehrlich)

- **Verdrahtet (Code):** Schicht 3 (20 Module) + §9/§10/§11 + §6 (SHACL).
- **Nur Doku/Auftrag:** Schicht 1 (Stufenfolge), Schicht 4 (Zuordnung), Schicht 5 (externe MCPs),
  Schicht 6 (NL-`## Ablauf`).
- **Teilweise:** Schicht 0 (Prinzipien §1–§8), Schicht 2 (kein Phasen-Runner).
- **Konsistent:** Schicht 7 (56 Rekursionen).
- **Korrekturen:** 20 Module (nicht 13), 56 Rekursionen (nicht 42); `connector-prozess.md`-Aussage
  „kein SHACL-Server" ist überholt (pyshacl aktiv).

## 3. Quellen
- Code: `data/memory/*.py` (18) + `data/memory/{shared,tier3-working}/*.py` (2) = **20**;
  `skills/procedural_memory.py`, `scripts/mcp_probe.py`.
- Doku: `AGENTS.md` (411 Z.), `knowledge/lifecycle/` (8), `knowledge/lifecycle/rekursion/` (7),
  `connectors/` (17), `skills/` (14 aktiv), `opencode.json` (19/16), `ergebnisse/rekursion/` (56).
- Methode: `ast`/`grep -rn`/`ls` (2026-10-04).
