# Systemtest MCP-Layer – alle Server in `opencode.json`

> **Datum:** 2026-10-01 · **Methode:** live `initialize` + `tools/list` + `tools/call` pro Server · **Fundort:** `~/.config/opencode/opencode.json`

Regel aus `AGENTS.md` §11: MCP-Server sind **optional**, die Pflicht-Basis ist die lokale Memory (`data/memory/`). Dieser Test prüft, welche Server real antworten.

## Methode

| Schritt | Umsetzung |
|---|---|
| Serverliste | `json.load(opencode.json)["mcp"]` – alles, was dort steht |
| Client | Python-SDK `mcp` aus `/home/opc/mcp-servers/hela-mem-mcp/.venv` |
| Existenz | erstes Wort des `command` gegen `which`/`os.path.exists` geprüft |
| Handshake | `initialize()` (Server-Name/Version) |
| Tools | `tools/list` (volle Namen protokolliert) |
| Tool-Call | min. 1 `tools/call`: read-only Tool bevorzugt, Argumente aus `inputSchema`; bei Fehler nächster Kandidat (max. 4 Tools × 2 Argument-Varianten) |
| Timeout | 40 s (venv) / 60 s (npx/uvx) / 75 s (remote) pro Server |
| Artefakt | `/tmp/opencode/mcp_harness.py` → `/tmp/opencode/systemtest-mcp.json` (Repo bleibt unverändert) |

## Übersicht

Einträge in `opencode.json`: **18** – davon **1** deaktiviert, **17** aktiv. Ergebnis: **15/17** laufen mit Handshake **und** erfolgreichem Tool-Call, **2** nicht. Tools gesamt: **122**.

| Server | Status | Handshake | Tools | gerufen | Ergebnis | s |
|---|---|---|---:|---|---|---:|
| `context7` | disabled (in opencode.json `enabled: false`) | – | – | – | – | – |
| `n8n-mcp` | ok | OK | 28 | `search_nodes` | OK | 2.2 |
| `obsidian` | ok | OK | 18 | `search_notes` | OK | 1.3 |
| `kubernetes` | ok | OK | 23 | `explain_resource` | OK | 2.3 |
| `sqlalchemy-mcp` | binary_fehlt | – | – | – | – (kein Start möglich) | 0.0 |
| `visuals-mcp` | binary_fehlt | – | – | – | – (kein Start möglich) | 0.0 |
| `cognee` | ok | OK | 5 | `recall` | OK | 9.2 |
| `livekit-docs` | ok | OK | 9 | `get_docs_overview` | OK | 0.9 |
| `graphiti` | ok | OK | 13 | `search_nodes` | OK | 3.2 |
| `hela-mem` | ok | OK | 6 | `retrieve` | OK | 11.0 |
| `reflexion` | ok | OK | 1 | `reflect` | OK | 3.2 |
| `react` | ok | OK | 1 | `react_step` | OK | 5.8 |
| `mars` | ok | OK | 3 | `mars_list_strategies` | OK | 1.0 |
| `trace` | ok | OK | 6 | `metric_recall_at_k` | OK | 2.4 |
| `godel-agent` | ok | OK | 2 | `read_logic` | OK | 1.1 |
| `agent-dice` | ok | OK | 1 | `geometric_consensus_fuse` | OK | 2.6 |
| `adas` | ok | OK | 3 | `adas_init_archive` | OK | 1.0 |
| `governance-mcp` | ok | OK | 3 | `resolve_entities` | OK | 22.3 |

## Detail pro Server (echte Ausgabe)

### `context7`

- in `opencode.json` auf `enabled: false` gesetzt – **nicht gestartet** (bewusst deaktiviert, daher auch nicht getestet).

### `n8n-mcp`

- **Typ:** `local` · **Command/URL:** `['npx', 'n8n-mcp']`
- **Binary:** OK: /home/opc/.npm-global/bin/npx
- **Handshake:** OK (Version `2.91.0`) · **28 Tools:** `tools_documentation`, `search_nodes`, `get_node`, `validate_node`, `get_template`, `search_templates`, `validate_workflow`, `n8n_create_workflow`, `n8n_get_workflow`, `n8n_update_full_workflow`, `n8n_update_partial_workflow`, `n8n_delete_workflow`, `n8n_list_workflows`, `n8n_validate_workflow`, `n8n_autofix_workflow`, `n8n_test_workflow`, `n8n_executions`, `n8n_evaluations`, `n8n_health_check`, `n8n_workflow_versions`, `n8n_deploy_template`, `n8n_manage_datatable`, `n8n_manage_folders`, `n8n_manage_credentials`, `n8n_audit_instance`, `n8n_manage_agents`, `n8n_explore_node_resources`, `n8n_list_catalog`
- **`tools/call`:** `search_nodes` mit `{"query": "test"}` → **OK**
  ```
  {   "query": "test",   "results": [     {       "nodeType": "@testdino/n8n-nodes-testdino.testDino",       "workflowNodeType": "@testdino/n8n-nodes-testdino.testDino",       "displayName": "TestDino",       "description": "Query TestDino test runs, test cases, specs, analytics, and reports",       "category": "Community",       "package": "@testdino/n8n-nodes-testdino",       "isCommunity": true,       "isVerified": true,       "authorName": "testdino.npm",       "npmDownloads": 208     },     {
  ```
- Versuche: 1 (geprüfte Tools: `search_nodes`)
- Dauer: 2.2 s

### `obsidian`

- **Typ:** `local` · **Command/URL:** `['npx', '-y', '@bitbonsai/mcpvault@latest', '/home/batnini/obsidian-vault/']`
- **Binary:** OK: /home/opc/.npm-global/bin/npx
- **Handshake:** OK (Version `0.16.0`) · **18 Tools:** `read_note`, `write_note`, `patch_note`, `list_directory`, `delete_note`, `search_notes`, `move_note`, `move_file`, `read_multiple_notes`, `update_frontmatter`, `get_notes_info`, `get_frontmatter`, `manage_tags`, `get_vault_stats`, `list_all_tags`, `wiki_link`, `get_note_outline`, `read_note_lines`
- **`tools/call`:** `search_notes` mit `{"query": "test"}` → **OK**
  ```
  []
  ```
- Versuche: 3 (geprüfte Tools: `list_directory`, `read_note`, `search_notes`)
- Dauer: 1.3 s

### `kubernetes`

- **Typ:** `local` · **Command/URL:** `['npx', 'mcp-server-kubernetes']`
- **Binary:** OK: /home/opc/.npm-global/bin/npx
- **Handshake:** OK (Version `4.1.8`) · **23 Tools:** `cleanup`, `kubectl_get`, `kubectl_describe`, `kubectl_apply`, `kubectl_delete`, `kubectl_create`, `kubectl_logs`, `kubectl_scale`, `kubectl_patch`, `kubectl_rollout`, `kubectl_context`, `kubectl_reconnect`, `explain_resource`, `install_helm_chart`, `upgrade_helm_chart`, `uninstall_helm_chart`, `node_management`, `port_forward`, `stop_port_forward`, `exec_in_pod`, `list_api_resources`, `kubectl_generic`, `ping`
- **`tools/call`:** `explain_resource` mit `{"resource": "pods"}` → **OK**
  ```
  KIND:       Pod VERSION:    v1  DESCRIPTION:     Pod is a collection of containers that can run on a host. This resource is     created by clients and scheduled onto hosts.      FIELDS:   apiVersion	<string>     APIVersion defines the versioned schema of this representation of an object.     Servers should convert recognized schemas to the latest internal value, and     may reject unrecognized values. More info:     https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions
  ```
- Versuche: 1 (geprüfte Tools: `explain_resource`)
- Dauer: 2.3 s

### `sqlalchemy-mcp`

- **Typ:** `local` · **Command/URL:** `['sqlalchemy-mcp-server', '--db-url', 'postgresql://meeting_user:meeting_password@localhost:5432/meeting_db', '--mode', 'readonly']`
- **Binary:** FEHLT: sqlalchemy-mcp-server
- **Status: binary_fehlt**

### `visuals-mcp`

- **Typ:** `local` · **Command/URL:** `['visuals-mcp']`
- **Binary:** FEHLT: visuals-mcp
- **Status: binary_fehlt**

### `cognee`

- **Typ:** `local` · **Command/URL:** `['uvx', '--python', '3.12', '--from', 'cognee-mcp', 'cognee-mcp', '--transport', 'stdio']`
- **Binary:** OK: /home/opc/.local/bin/uvx
- **Handshake:** OK (Version `0.5.6`) · **5 Tools:** `remember`, `recall`, `forget`, `search_tools`, `call_tool`
- **`tools/call`:** `recall` mit `{"query": "test"}` → **OK**
  ```
  no matching memories [system] Memory is still warming up: no knowledge graph data exists yet for the requested datasets.
  ```
- Versuche: 1 (geprüfte Tools: `recall`)
- Dauer: 9.2 s

### `livekit-docs`

- **Typ:** `remote` · **Command/URL:** `https://docs.livekit.io/mcp/`
- **Handshake:** OK (Version `1.5.0`) · **9 Tools:** `get_docs_overview`, `get_sdks`, `get_pages`, `docs_search`, `get_changelog`, `get_python_agent_example`, `get_pricing_info`, `submit_docs_feedback`, `code_search`
- **`tools/call`:** `get_docs_overview` mit `{"context": "test"}` → **OK**
  ```
  # LiveKit docs  > LiveKit is an open-source platform for building voice, video, and physical AI agents. It includes the Agents framework for Python and Node.js, realtime WebRTC infrastructure with SDKs for every platform, telephony, and LiveKit Cloud, the hosted commercial offering.  ## Instructions for AI agents  - Append `.md` to any page URL for clean Markdown, or send an `Accept: text/markdown` header. - Append `/llms.txt` to any of the section URLs listed below for the full page index of th
  ```
- Versuche: 1 (geprüfte Tools: `get_docs_overview`)
- Dauer: 0.9 s

### `graphiti`

- **Typ:** `local` · **Command/URL:** `['uv', 'run', '--directory', '/home/opc/mcp-servers/graphiti/mcp_server', 'main.py', '--config', 'config/config-nvidia.yaml', '--transport', 'stdio']`
- **Binary:** OK: /home/opc/.local/bin/uv
- **Handshake:** OK (Version ``) · **13 Tools:** `add_memory`, `search_nodes`, `search_memory_facts`, `delete_entity_edge`, `delete_episode`, `get_entity_edge`, `get_episodes`, `summarize_saga`, `build_communities`, `add_triplet`, `get_episode_entities`, `clear_graph`, `get_status`
- **`tools/call`:** `search_nodes` mit `{"query": "test"}` → **OK**
  ```
  {   "message": "No relevant nodes found",   "nodes": [] }
  ```
- Versuche: 1 (geprüfte Tools: `search_nodes`)
- Dauer: 3.2 s

### `hela-mem`

- **Typ:** `local` · **Command/URL:** `['/home/opc/mcp-servers/hela-mem-mcp/.venv/bin/python', '/home/opc/mcp-servers/hela-mem-mcp/server.py']`
- **Binary:** OK: /home/opc/mcp-servers/hela-mem-mcp/.venv/bin/python
- **Handshake:** OK (Version `1.30.0`) · **6 Tools:** `store_episodic`, `retrieve`, `add_semantic`, `search_semantic`, `process_turn`, `save_state`
- **`tools/call`:** `retrieve` mit `{"query": "test"}` → **OK**
  ```
  [{"node": {"id": "3", "content": "t=6 Rekursion: berechne_median, pi0=2/4.", "role": "user", "embedding": [-0.0017267765942960978, 0.05200114846229553, -0.02133060246706009, -0.026854388415813446, -0.07699651271104813, 0.013759749941527843, -0.05497901514172554, 0.17461474239826202, -0.014663757756352425, 0.004716099705547094, 0.08688896149396896, -0.05484137311577797, 0.026504362002015114, -0.056057270616292953, -0.12993955612182617, -0.06324318796396255, -0.023218972608447075, -0.0420246571302
  ```
- Versuche: 1 (geprüfte Tools: `retrieve`)
- Dauer: 11.0 s

### `reflexion`

- **Typ:** `local` · **Command/URL:** `['/home/opc/mcp-servers/reflexion-mcp/.venv/bin/python', '/home/opc/mcp-servers/reflexion-mcp/server.py']`
- **Binary:** OK: /home/opc/mcp-servers/reflexion-mcp/.venv/bin/python
- **Handshake:** OK (Version `1.30.0`) · **1 Tools:** `reflect`
- **`tools/call`:** `reflect` mit `{"context": "test", "question": "Was ist 2+2? Antworte in einem Satz."}` → **OK**
  ```
  The previous attempt likely failed because I either answered in English, used more than one sentence, or omitted the required German wording such as “ist” or a period, causing a phrasing mismatch with the expected answer. To avoid this, I will now first confirm the language of the question, compute the result silently
  ```
- Versuche: 1 (geprüfte Tools: `reflect`)
- Dauer: 3.2 s

### `react`

- **Typ:** `local` · **Command/URL:** `['/home/opc/mcp-servers/react-mcp/.venv/bin/python', '/home/opc/mcp-servers/react-mcp/server.py']`
- **Binary:** OK: /home/opc/mcp-servers/react-mcp/.venv/bin/python
- **Handshake:** OK (Version `1.30.0`) · **1 Tools:** `react_step`
- **`tools/call`:** `react_step` mit `{"question": "Was ist 2+2? Antworte in einem Satz."}` → **OK**
  ```
  Thought: The question asks for the result of 2+2 in German, requiring a single sentence answer. Finish[2+2 ergibt 4.]
  ```
- Versuche: 1 (geprüfte Tools: `react_step`)
- Dauer: 5.8 s

### `mars`

- **Typ:** `local` · **Command/URL:** `['/home/opc/mcp-servers/mars-mcp/.venv/bin/python', '/home/opc/mcp-servers/mars-mcp/server.py']`
- **Binary:** OK: /home/opc/mcp-servers/mars-mcp/.venv/bin/python
- **Handshake:** OK (Version `1.30.0`) · **3 Tools:** `mars_list_strategies`, `mars_run_strategy`, `mars_analyze_failure`
- **`tools/call`:** `mars_list_strategies` mit `{}` → **OK**
  ```
  {"zero_shot_cot": "Zero-shot chain-of-thought with XML output format", "zero_shot": "Zero-shot direct answer with XML output format", "zero_shot_self_consistency": "Self-consistency with 5 samples and XML output format", "zero_shot_self_consistency_10": "Self-consistency with 10 samples and XML output format", "self_refine": "Self-refine with XML output format", "few_shot_cot": "Few-shot chain-of-thought with XML output format", "concise_enhanced": "Concise prompting with XML output format", "sp
  ```
- Versuche: 1 (geprüfte Tools: `mars_list_strategies`)
- Dauer: 1.0 s

### `trace`

- **Typ:** `local` · **Command/URL:** `['/home/opc/mcp-servers/TRACE/.venv/bin/python', '/home/opc/mcp-servers/trace-mcp/server.py']`
- **Binary:** OK: /home/opc/mcp-servers/TRACE/.venv/bin/python
- **Handshake:** OK (Version `1.30.0`) · **6 Tools:** `metric_recall_at_k`, `metric_gold_rank`, `metric_precision_in_accepted`, `metric_recall_in_accepted`, `metric_compute`, `parse_json`
- **`tools/call`:** `metric_recall_at_k` mit `{"gold_ids": ["test"], "candidate_ids": ["test"], "k": 1}` → **OK**
  ```
  1.0
  ```
- Versuche: 1 (geprüfte Tools: `metric_recall_at_k`)
- Dauer: 2.4 s

### `godel-agent`

- **Typ:** `local` · **Command/URL:** `['/home/opc/mcp-servers/godel-mcp/.venv/bin/python', '/home/opc/mcp-servers/godel-mcp/server.py']`
- **Binary:** OK: /home/opc/mcp-servers/godel-mcp/.venv/bin/python
- **Handshake:** OK (Version `1.30.0`) · **2 Tools:** `run_code`, `read_logic`
- **`tools/call`:** `read_logic` mit `{"module_name": "logic", "target_name": "get_source_code"}` → **OK**
  ```
  def get_source_code(obj, obj_name):     if hasattr(obj, '__source__'):         if inspect.isclass(obj):             return f'class {obj_name}:\n' + "\n\n".join(f"{code}" for code in obj.__source__.values())         return obj.__source__     else:         return inspect.getsource(obj) 
  ```
- Versuche: 1 (geprüfte Tools: `read_logic`)
- Dauer: 1.1 s

### `agent-dice`

- **Typ:** `local` · **Command/URL:** `['/home/opc/mcp-servers/agent-dice-mcp/.venv/bin/python', '/home/opc/mcp-servers/agent-dice-mcp/server.py']`
- **Binary:** OK: /home/opc/mcp-servers/agent-dice-mcp/.venv/bin/python
- **Handshake:** OK (Version `1.30.0`) · **1 Tools:** `geometric_consensus_fuse`
- **`tools/call`:** `geometric_consensus_fuse` mit `{"base": [1.0, 1.0], "b1": [1.0, 1.0], "b2": [1.0, 1.0], "b3": [1.0, 1.0]}` → **OK**
  ```
  [1.0, 1.0]
  ```
- Versuche: 2 (geprüfte Tools: `geometric_consensus_fuse`)
- Dauer: 2.6 s

### `adas`

- **Typ:** `local` · **Command/URL:** `['/home/opc/mcp-servers/adas-mcp/.venv/bin/python', '/home/opc/mcp-servers/adas-mcp/server.py']`
- **Binary:** OK: /home/opc/mcp-servers/adas-mcp/.venv/bin/python
- **Handshake:** OK (Version `1.30.0`) · **3 Tools:** `adas_init_archive`, `adas_get_prompt`, `adas_propose_agent`
- **`tools/call`:** `adas_init_archive` mit `{}` → **OK**
  ```
  [{"thought": "Directly formatting the output can be challenging. A good practice is to allow the LLM to write the transformation code and then evaluate it to generate the output. This ensures that the output is derived from executable code, improving reliability.", "name": "Chain-of-Thought", "code": "def forward(self, taskInfo):\n    # Instruction for the Chain-of-Thought (CoT) approach with code generation\n    cot_instruction = \"Please think step by step and then solve the task by writing th
  ```
- Versuche: 1 (geprüfte Tools: `adas_init_archive`)
- Dauer: 1.0 s

### `governance-mcp`

- **Typ:** `local` · **Command/URL:** `['/home/opc/mcp-servers/hela-mem-mcp/.venv/bin/python', '/home/opc/mcp-servers/governance-mcp/server.py']`
- **Binary:** OK: /home/opc/mcp-servers/hela-mem-mcp/.venv/bin/python
- **Handshake:** OK (Version `1.30.0`) · **3 Tools:** `drift_index`, `lyapunov_check`, `resolve_entities`
- **`tools/call`:** `resolve_entities` mit `{"text": "The meeting is about the knowledge agent and drift monitoring."}` → **OK**
  ```
  {   "entity_type": "Concept",   "span": "knowledge agent",   "start": 25,   "end": 40,   "confidence": 0.5939,   "backend": "gliner" } \| {   "entity_type": "Concept",   "span": "drift monitoring",   "start": 45,   "end": 61,   "confidence": 0.746,   "backend": "gliner" }
  ```
- Versuche: 1 (geprüfte Tools: `resolve_entities`)
- Dauer: 22.3 s

## Nicht lauffähig / nicht getestet

| Server | Grund |
|---|---|
| `sqlalchemy-mcp` | FEHLT: sqlalchemy-mcp-server |
| `visuals-mcp` | FEHLT: visuals-mcp |
| `context7` | in `opencode.json` `enabled: false` |

**Ehrliche Befunde:**

- `sqlalchemy-mcp` und `visuals-mcp` sind in `opencode.json` eingetragen, aber die Binaries `sqlalchemy-mcp-server` und `visuals-mcp` existieren nicht im PATH – die Einträge sind damit **toter Config-Platzhalter** (Handshake unmöglich).
- `context7` ist absichtlich deaktiviert.
- Aufgerufen wurden bewusst lesende Tools: `search_nodes` (n8n, graphiti), `search_notes` (obsidian), `explain_resource` (kubernetes), `recall` (cognee), `get_docs_overview` (livekit-docs), `retrieve` (hela-mem), `read_logic` (godel-agent), `resolve_entities` (governance-mcp) u. a. Schreibende Tools (`delete_*`, `add_memory`, `forget`, `write_note`, `n8n_create_workflow`) wurden **nicht** aufgerufen.
- Nur **2 Server** brauchten mehr als einen Versuch, Details in den Versuchslisten oben:
  - `obsidian`: `read_note` `{"path": "/"}` → *File not found*, `list_directory` ohne Pfad → *Directory not found*, dann `search_notes` `{"query": "test"}` → **HTTP-Call OK, Ergebnis `[]` (kein Treffer für "test" – leeres Resultat, kein Beweis für Inhalte)**.
  - `agent-dice`: Variante 1 (String-Arrays) → *too many dimensions 'str'*, Variante 2 (Float-Arrays) → `[1.0, 1.0]`.
- Alle anderen Server liefen beim ersten Tool-Call durch.

## Quellen (HTTP-Status am 2026-10-01 geprüft)

- Serverliste: `~/.config/opencode/opencode.json` (lokale Datei)
- MCP-Spezifikation: https://modelcontextprotocol.io/docs/2026-07-28/getting-started/intro — **HTTP 200** (mit Redirect)
- `livekit-docs` (remote): `https://docs.livekit.io/mcp/` antwortet auf `initialize` (GET = 405, MCP-POST-Handshake = OK)
- Fallback-Regel: `AGENTS.md` §11.2

