# MCP-Live-Binding (`data/memory/mcp_live_binding.py`)

> Datum: 2026-10-04 · Status: **Belegt** (Quelle + MCP-Spec) + **Auftrag** (Verdrahtung).
> Guardrail 7: **echter** Live-Aufruf. Ziel `g`: externe MCPs **live** an den Code binden.

## 1. Quellen (verifiziert, §6)

- **Intent Leakage by Design: Governance Gaps in MCP, Tool Use, and A2A** (Yuchia Chang, 2026)
  nennt wörtlich **Tool-Path Fingerprinting** („the sequence and combination of tool
  invocations leaks strategic intent") und **Cross-Endpoint Correlation** („behavioral
  patterns across independent MCP servers can be linked to reconstruct holistic user profiles").
  → **Korrektur:** Der Auftrag nennt „Zenodo, 2026"; die verifizierte Primärquelle ist die
  **Chang-2026-Arbeit** (die beiden Gap-Namen stimmen wörtlich).
- **MCP-Spec** (stdio transport): Client ruft `tools/call` über stdin/stdout.
  https://modelcontextprotocol.io/specification
- **Integration:** `mcp_catalog.py` (TTC-Katalog) + `scripts/mcp_probe.py` (load_servers/probe).

## 2. Funktionen

| Funktion | Was | Quelle |
|---|---|---|
| `call_tool_live(server, tool, args)` | **echter** `tools/call` über stdio | MCP-Spec |
| `tool_path_fingerprint([(server, tool)])` | stabile ID der Aufruf-Sequenz (sha256) | Chang 2026 |
| `cross_endpoint_correlation(records)` | gleiche Tool-Pfade über Server gruppieren | Chang 2026 |
| `catalog_server(server)` | live `tools/list` → **TTC-Katalog** (`mcp_catalog`) | TTC + mcp_probe |
| `load_servers()` | aktive lokale MCPs aus `opencode.json` (leer, wenn fehlt) | mcp_probe |

- **§11:** MCP ist optional; fehlt ein Server/Endpoint → `ok:false` mit Grund (kein Fake).
- **Generic:** Graphiti/Cognee/HeLa-Mem werden über denselben Pfad aufgerufen (Server aus
  `opencode.json`); eigene Abhängigkeiten/Keys bleiben Voraussetzung.

## 3. Echte Ausgabe (CLI, Live-`tools/call` über stdio, 2026-10-04)

```text
call_tool_live("memory", "memory.search", {"query": "SHACL"})
{
  "server": "memory", "tool": "memory.search", "ok": true,
  "content": ["{\n  \"ok\": true,\n  \"query\": \"SHACL\",\n  \"n_hits\": 0,\n  \"hits\": []\n}"],
  "fingerprint": "56aaf9fa34f9b391"
}
```

- Echter MCP-Handshake (`initialize`) + `tools/call` über **stdio** (Server als Subprozess).
- **Tool-Path Fingerprinting** liefert die stabile ID `56aaf9fa34f9b391`.

## 4. Test (echt, Guardrail 7)

`tests/test_mcp_live_binding.py` (9 Tests): Fingerprint (deterministisch), Cross-Endpoint-
Correlation, **Live-Aufruf des eigenen MCP-Servers** (`memory.search` über stdio),
unbekannter Server, Fehler-Server, `catalog_server` (live `tools/list` + TTC), Config-Fehlen.
`mcp_live_binding.py`: **100 %** Line+Branch.

## 5. Gate (§9)

- Interface-Änderung (neues Modul) → **approved** (Batnini, Auftrag).
- Guardrail 3: Provenienz `ergebnisse/rekursion/052-mcp-live-binding.md`.
- Guardrail 6: kein Commit ohne Erlaubnis. §9.1b: `AGENTS.md` unverändert.
- **Ehrliche Grenzen:** Der Test nutzt den **eigenen** MCP-Server (reliabel, offline);
  Graphiti/Cognee/HeLa brauchen ihre eigenen Deps/Keys (§11 optional). Der Governance-Teil
  ist **Fingerprinting/Correlation** (Chang 2026), kein laufender Multi-Tenant-Registry.
