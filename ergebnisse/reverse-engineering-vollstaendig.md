# Reverse Engineering (vollständig, alle 8 Schichten)

> Datum: 2026-10-03 · Methode: `grep`/`ls` über den **echten** Code (`data/memory/**`,
> `skills/**`, `connectors/**`, `opencode.json`, `AGENTS.md`). **Keine Erfindungen** —
> nur was tatsächlich im Code steht. Lücken werden klar benannt.
> Ehrlicher Hinweis: Der Auftrag nennt „13 Module"; real sind es **14** (`data/memory/*.py`).

## 0. Übersicht (Schicht · Status · Beweis · Lücke)

| # | Schicht | Status | Beweis (Code/Doku) | Lücke |
|---|---|---|---|---|
| 0 | **Gesetz** (AGENTS.md §1–§11) | **teilweise** | §9: `pipeline.py:20-24`; §10: `fast_write_router.py`; §11: `mcp_memory_server.py`; Konformitäts-Test `tests/test_agents_law.py` | Prinzipien §1–§8 sind **Doku/Auftrag**, nicht als Code erzwungen |
| 1 | **Lifecycle — 8 Stufen** | **nur Doku** | `knowledge/lifecycle/*.md` (8 Dateien) | **kein Code durchläuft** Erfahrung→…→Wissen+; nur Regex-Muster `ingestion_hook.py:170-171` |
| 2 | **Rekursion — 5 Phasen** | **teilweise** | `reflective_agent.run_once` (Hub/Forgetting/HMM); `evaluator_version.RedQueenLoop` (Epochen) | **kein Runner** Konstrukt→Akt→Observe→Compare→Revise; Phasen sind `.md`-Skills |
| 3 | **Gedächtnis — 14 Module** | **verdrahtet** | Import-Graph: `pipeline.py` → `approval/bi_temporal/bias_monitor/mandate/trust`; `reflective_agent`→`evaluator_version`; `ingestion_hook`/`reflective_agent`→`pipeline`; `gaama_extract`→`fast_write_router`/`trust` | Einstiegspunkte ohne Importer: `ingestion_hook`, `reflective_agent`, `mcp_memory_server`, `lru_cache`, `shared_memory` (CLI/Tests) |
| 4 | **Connectoren — 17** | **nur Doku** | `connectors/*.md`; AGENTS.md-Tabelle | **kein `.py` referenziert `connectors/`** (nur `mcp_memory_server.py` hat Scope „connectors") |
| 5 | **MCP-Server — 19** | **extern/nur Doku** | `opencode.json` (19 Einträge); eigener `mcp_memory_server.py` | **kein `.py` ruft** die externen MCPs (Graphiti/Cognee/…); §11 optional |
| 6 | **Skills — 14** | **verwaltet, nicht ausgeführt** | `skills/*/SKILL.md` (14); `skills/procedural_memory.py` (snapshot/update/rollback) | **kein `.py` führt Skills aus** (nur Versionierung) |
| 7 | **Ergebnisse — 43 Rekursionen (000–042)** | **konsistent** | 43 Dateien == 43 Index-Zeilen (`ergebnisse/rekursion/README.md`); `tests/test_agents_law.py:46` + `test_rekursion_index_vollstaendig` | — |

## 1. Details je Schicht

### Schicht 0 — Gesetz (AGENTS.md §1–§11)
- **Umgesetzt:** §9 (`pipeline.py`: Mandat/Trust/Approval/Bi-Temporal/Drift), §9.3 (`approval.py`), §9.1c (`bias_monitor.py`), §9.1b (`versions/vN/`), §10 (`fast_write_router.py`, `gaama_extract.py`), §11 (`mcp_memory_server.py`).
- **Nicht als Code erzwungen:** §1 Beobachte-ohne-Deuten, §2 Ziel `g`, §3 8-Stufen, §4 Brich-die-Muster, §5 Wolke, §6 Keine-Erfindungen (Verfahren), §7 Kognition, §8 Nicht-Kognition — als **Auftrag/Doku** vorhanden.
- **Beweis:** `tests/test_agents_law.py` (prüft §-Abschnitte, Guardrails, Provenienz, Versionierung).

### Schicht 1 — Lifecycle (8 Stufen)
- `knowledge/lifecycle/` hat 8 Phasen-Dateien. **Kein Code-Funktion** durchläuft sie als Zyklus.
- `ingestion_hook.py:170-171` kennt nur Regex-Muster für Stage/Phase (Entity-Resolution).
- **Lücke:** 8-Stufen-Durchlauf ist Auftrag/Doku, nicht implementiert.

### Schicht 2 — Rekursion (5 Phasen)
- `reflective_agent.run_once` (Hub/Forgetting/HMM) und `evaluator_version.RedQueenLoop` (Epochen) existieren — aber **kein** expliziter Konstrukt→Akt→Observe→Compare→Revise-Runner.
- Die 5 Phasen liegen als `skills/recursive-improve/*/SKILL.md` (Doku).
- **Lücke:** Phasen-Ausführung ist Auftrag/Doku.

### Schicht 3 — Gedächtnis (14 Module)
- Import-Graph (echte Kanten): `pipeline` → `approval`, `bi_temporal`, `bias_monitor`, `mandate`, `trust`; `reflective_agent` → `evaluator_version`; `ingestion_hook` → `pipeline`; `reflective_agent` → `pipeline`; `gaama_extract` → `fast_write_router`, `trust`; `lru_cache` nutzt `gaama_extract`-Graph (übergeben).
- **Einstiegspunkte** (kein Importer, per CLI/Test): `ingestion_hook`, `reflective_agent`, `mcp_memory_server`, `lru_cache`, `shared_memory`.
- **Lücke:** keine (bis auf Einstiegspunkte).

### Schicht 4 — Connectoren (17)
- `connectors/*.md` (17). **Kein `.py` importiert/referenziert sie** (Grep `connector` in `*.py` → nur `mcp_memory_server.py` Scope).
- Sie werden über `AGENTS.md`-Tabelle + `ergebnisse/verbindungen-diagramm.md` §5 zugeordnet.
- **Lücke:** Connectoren sind **reine Doku**, kein Code-Pfad.

### Schicht 5 — MCP-Server (19)
- `opencode.json`: 19 Einträge (16 aktiv). **Kein `.py` ruft** Graphiti/Cognee/HeLa/Reflexion/… auf.
- Nur der eigene `mcp_memory_server.py` ist Code (5 Tools).
- **Lücke (by design, §11):** externe MCPs sind **optional**, nicht im Repo-Code verdrahtet.

### Schicht 6 — Skills (14)
- `skills/*/SKILL.md` (14 aktiv). `skills/procedural_memory.py` **verwaltet** sie (snapshot/update/rollback/audit), **führt sie aber nicht aus**.
- **Lücke:** Skill-Ausführung ist Auftrag/Doku (kein Interpreter im Code).

### Schicht 7 — Ergebnisse (43 Rekursionen 000–042)
- 43 Dateien == 43 Index-Zeilen; Provenienz-Test (`approved`/`quelle`) + Index-Test bestehen.
- **Lücke:** keine.

## 2. Quellen
- Code: `data/memory/*.py`, `data/memory/*/*.py`, `skills/procedural_memory.py`.
- Doku: `AGENTS.md`, `knowledge/lifecycle/`, `connectors/`, `opencode.json`, `ergebnisse/rekursion/`.
- Methode: `grep -rn`/`ls` (2026-10-03).

## 3. Fazit (ehrlich)
- **Verdrahtet (Code):** Schicht 3 (Gedächtnis) + §9/§10/§11.
- **Nur Doku/Auftrag (kein Code-Pfad):** Schicht 1 (8 Stufen), Schicht 4 (Connectoren), Schicht 5 (externe MCPs), Schicht 6 (Skills).
- **Teilweise:** Schicht 0 (Prinzipien §1–§8), Schicht 2 (5 Phasen).
- **Konsistent:** Schicht 7 (Ergebnisse).
