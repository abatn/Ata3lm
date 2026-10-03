# MCP-Memory-Server – 5 Kern-Tools + Tri-Color Trust (schließt die 6 MCP-LÜCKEN)

> Datum: 2026-10-03 · Auftrag: „Schließe die 6 MCP-Lücken … nach Atomic Notes
> (MCP-Interface) und ATHENA (Tri-Color Trust)." · Lab-Prinzip §6 · Human-Gate §9.

## 1. Quellen (HTTP 200, geprüft 2026-10-03)

| Quelle | Wörtlicher Beleg | Link |
|---|---|---|
| **Atomic** (MCP-Interface) | „Atomic exposes five MCP tools"; „**Search** Atomic **before** answering"; „Store durable preferences … **Update stale atoms instead of creating duplicates**" | https://atomicapp.ai/guides/mcp-server/ · https://github.com/kenforthewin/atomic |
| **ATHENA / Tri-Color Trust Model** (Leu, 2026) | **Blue** = explicit, user-authored · **Green** = neural, AI-suggested (pending validation) · **Red** = supervised, flagged by formal constraint validation (violation); „**AI can only propose; it cannot auto-commit** to curated knowledge" | https://exa.ai/library/publication/ydhtt93r884 |

## 2. Die 5 Kern-Tools

| Tool | was | Tri-Color-Bezug |
|---|---|---|
| `memory.read` | Ressource aus einem Scope lesen | – |
| `memory.write` | schreiben mit Trust-Gate | **blue→confirmed · green→proposed · red→rejected** |
| `memory.search` | Volltextsuche (Such-vor-Schreiben) | Atomic: „search before answering" |
| `memory.consolidate` | Bestand je Scope zählen + Index schreiben | – |
| `memory.link` | typisierte Kante anlegen | Tri-Color je Kante |

## 3. Exponierte Scopes (MCP über lokaler Memory, §11)

`tier1` (tier1-base) · `tier2` (tier2-index) · `tier3` (tier3-working) ·
`structured` (knowledge/structured) · `connectors` · `skills`

Damit sind **alle 6 MCP-LÜCKEN** aus `ergebnisse/verbindungen-diagramm.md` §2.1
geschlossen: MCP → tier1/2/3, → structured, → connectors, → skills (je 1 Tool-Pfad).

## 4. Registrierung (`/home/opc/.config/opencode/opencode.json`)

```json
"memory": {
  "type": "local",
  "command": ["/home/opc/mcp-servers/hela-mem-mcp/.venv/bin/python",
              "/home/opc/knowledge-agent/data/memory/mcp_memory_server.py"],
  "env": { "MCP_MEMORY_ROOT": "/home/opc/knowledge-agent" },
  "enabled": true
}
```

MCP-Einträge danach: **19** (vorher 18).

## 5. Echter Tool-Test (MCP-Client → Server, isoliertes Root)

```text
TOOLS: ['memory.read', 'memory.write', 'memory.search', 'memory.consolidate', 'memory.link']
memory.read {"scope":"tier1","key":"identity.md"} -> {"ok":true,"content":"Agent-Identitaet: knowledge-agent\n"}
memory.write {"scope":"structured","key":"note.md","content":"KI-Vorschlag","trust":"green"} -> {"ok":true,"status":"proposed","trust":"green","bytes":12}
memory.write {"scope":"structured","key":"bad.md","content":"x","trust":"red"} -> {"ok":false,"status":"rejected","reason":"Tri-Color Red: Constraint-Verstoß – nicht gespeichert"}
memory.search {"query":"cognee"} -> {"ok":true,"n_hits":3,"hits":[{"scope":"connectors","file":"cognee-memory.md","line":1,"text":"Cognee = Graph+Vektor Memory"},…]}
memory.link {"a":"tier1:identity","b":"connectors:cognee","trust":"blue"} -> {"ok":true,"edge":{"from":"tier1:identity","to":"connectors:cognee","trust":"blue","status":"confirmed"}}
memory.consolidate {} -> {"ok":true,"scopes":{"tier1":{"files":1},…}}
```

Beleg: `/tmp/opencode/mcp-memory.out` (Rohtext). Der `red`-Write wurde **nicht**
gespeichert (Tri-Color-Gate).

## 6. Tests

```text
make test → 209 passed · 1838/1838 Statements · 426/426 Branches = 100,00 %
tests/test_mcp_memory.py: read/write/search/link/consolidate, Scope-/Key-Validierung,
  Tri-Color (blue/green/red/ungültig), Nicht-UTF8-Skip, build_server (5 Tools, Fake-SDK)
```

## 7. Gate / Freigabe (§9)

- **Neue Quelle** (Atomic, Tri-Color Trust): §9 → Human-Gate; durch den Auftrag erteilt.
- **Interface-Erweiterung** (neuer MCP-Server + opencode.json-Eintrag): additiv.
- **Tri-Color-Gate** erzwingt: KI schreibt nur `green` (**proposed**); `blue`
  (confirmed) ist menschlich; `red` wird **abgelehnt** — Quelle: „AI can only propose".
- Ehrliche Grenze: `mcp`-SDK ist im System-Python nicht installiert → Modul importiert
  es **lazy**; Tests decken `build_server()` mit Fake-SDK, der echte Lauf nutzt das Venv.
