# Test: Alle 16 MCP-Server

> Datum: 2026-09-30
> Zweck: Prüfung aller 16 aktiven MCP-Server aus `opencode.json` (Existenz, Handshake, Tools, Tool-Call)
> Methode: MCP-Handshake (`initialize` + `tools/list`) + echte Tool-Calls, Roh-Ausgabe
> Lab-Prinzip: Keine Erfindungen – nur tatsächliche Ausgaben.

---

## Aufgabe 1 + 2: Server-Test & Tool-Test

| # | Server | Typ | Existenz | Handshake | Tools | Tool-Call |
|---|---|---|---|---|---|---|
| 1 | **graphiti** | local | ✅ | ✅ „Graphiti Agent Memory" | **13** | ✅ `add_memory` |
| 2 | **cognee** | local | ✅ | ✅ „Cognee" v1.30 | **11** | ⚠️ `remember` Timeout (280s) |
| 3 | **hela-mem** | local | ✅ | ✅ „hela-mem" | **6** | ✅ `store_episodic` |
| 4 | **reflexion** | local | ✅ | ✅ „reflexion" | **1** | ✅ `reflect` |
| 5 | **react** | local | ✅ | ✅ „react" | **1** | ✅ `react_step` |
| 6 | **mars** | local | ✅ | ✅ „mars" | **3** | ✅ `mars_run_strategy` |
| 7 | **trace** | local | ✅ | ✅ „trace" | **6** | ✅ `metric_recall_at_k` |
| 8 | **godel-agent** | local | ✅ | ✅ „godel-agent" | **2** | ✅ `run_code` |
| 9 | **agent-dice** | local | ✅ | ✅ „agent-dice" | **1** | ✅ `geometric_consensus_fuse` |
| 10 | **adas** | local | ✅ | ✅ „adas" | **3** | ✅ `adas_init_archive` |
| 11 | **kubernetes** | local | ✅ | ✅ „kubernetes" | viele (23) | (nicht getestet) |
| 12 | **n8n-mcp** | local | ✅ | ✅ „n8n-documentation-mcp" | viele | (nicht getestet) |
| 13 | **obsidian** | local | ✅ | ✅ „mcpvault" | viele | (nicht getestet) |
| 14 | **livekit-docs** | remote | ✅ | ✅ „livekit-docs" v1.5.0 | (remote) | (nicht getestet) |
| 15 | **sqlalchemy-mcp** | local | ❌ | ❌ | — | — |
| 16 | **visuals-mcp** | local | ❌ | ❌ | — | — |

**Ergebnis: 14/16 antworten. 2 fehlgeschlagen.**

---

## Tool-Listen (verifiziert)

- **graphiti (13):** `add_memory, search_nodes, search_memory_facts, delete_entity_edge, delete_episode, get_entity_edge, get_episodes, summarize_saga, build_communities, add_triplet, get_episode_entities, clear_graph, get_status`
- **cognee (11):** `remember, recall, forget, visualize_graph_ui, upload_file_ui, open_cognee_workspace, cognify_file, list_datasets_json, list_dataset_data_json, get_client_info_json, create_dataset_json`
- **hela-mem (6):** `store_episodic, retrieve, add_semantic, search_semantic, process_turn, save_state`
- **mars (3):** `mars_list_strategies, mars_run_strategy, mars_analyze_failure`
- **trace (6):** `metric_recall_at_k, metric_gold_rank, metric_precision_in_accepted, metric_recall_in_accepted, metric_compute, parse_json`
- **adas (3):** `adas_init_archive, adas_get_prompt, adas_propose_agent`
- **godel-agent (2):** `run_code, read_logic`
- **reflexion (1):** `reflect`
- **react (1):** `react_step`
- **agent-dice (1):** `geometric_consensus_fuse`

---

## Tatsächliche Tool-Ausgaben (Roh)

| Server | Tool | Input | Ausgabe (real) |
|---|---|---|---|
| hela-mem | `store_episodic` | `{"content":"Alice works at Acme Corp in Berlin.","role":"user"}` | `{"stored": true, "node_id": "0"}` |
| reflexion | `reflect` | `{question:"Capital of France?", scratchpad:"...Lyon"}` | „The previous answer was incorrect because I relied on an unverified memory…" |
| react | `react_step` | `{question:"Capital of France?", context:"...Paris"}` | `Thought: …the answer is Paris.\nFinish[Paris]` |
| mars | `mars_run_strategy` | `{strategy:"zero_shot", question:"What is 2+2?"}` | `4` |
| trace | `metric_recall_at_k` | `{gold_ids:["a","b"],candidate_ids:["b","c","a"],k:2}` | `0.5` |
| godel-agent | `run_code` | `{code_type:"python",code:"print(sum(range(10)))"}` | `Execution Summary (Python):\nOutput:\n45` |
| agent-dice | `geometric_consensus_fuse` | `{base:[0,0,0],b1:[1,2,3],b2:[1,2,3],b3:[-1,-2,-3]}` | `[1.0, 2.0, 3.0]` |
| adas | `adas_init_archive` | `{}` | 5 Agenten (COT_code, Reflexion, …) |
| graphiti | `add_memory` | `{name:"test",episode_body:"Alice works at Acme Corp in Berlin."}` | `{"message":"Episode 'test' queued for processing in group 'main'"}` |
| cognee | `remember` | `{data:"...",dataset_name:"test"}` | ⚠️ **kein Ergebnis** (Timeout 280s – Verarbeitung zu langsam) |

---

## Fehlgeschlagene Server (mit Fehlermeldung)

| Server | Fehler |
|---|---|
| **sqlalchemy-mcp** | `[Errno 2] No such file or directory: 'sqlalchemy-mcp-server'` |
| **visuals-mcp** | `[Errno 2] No such file or directory: 'visuals-mcp'` |

> Beide: die konfigurierten Binaries existieren nicht im PATH. **Umgebungs-Server, nicht Projekt.**

---

## Zusammenfassung

| Kategorie | Anzahl |
|---|---|
| Getestet (Handshake OK) | **14** |
| Tool-Calls erfolgreich | **9** (von 10 Projekt-Servern) |
| Tool-Call Timeout | 1 (cognee `remember`) |
| Fehlgeschlagen (Binary fehlt) | **2** (sqlalchemy-mcp, visuals-mcp) |

**Fazit:** 14/16 Server antworten. Die **10 Projekt-MCP-Server** antworten alle
(Handshake OK); 9/10 Tool-Calls erfolgreich, cognees `remember` ist zu langsam.
2 Umgebungs-Server (sqlalchemy-mcp, visuals-mcp) haben fehlende Binaries.
