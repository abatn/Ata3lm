# MCP-Ziel-Plan – Umsetzung nach offiziellen MCP-Vorlagen

> Datum: 2026-09-30
> Status: **UMGESETZT** – P1–P4 fertig (16 MCP-Server aktiv), P5 dokumentiert (Info).
> Geltung: unterliegt `AGENTS.md` (8 Prinzipien + §9 Gate + §10 Fast Write Routing)
> Lab-Prinzip §6: Keine Erfindungen – nur verifizierte Quellen (offizielle Docs/Code).

---

## 1. Ziel

Alle Projekt-Connectoren als ausführbare MCP-Server bereitstellen, **ohne eigene
Erfindungen**: Wir kopieren das **offizielle MCP-Muster** und wickeln unsere
Logik (HeLa-Mem, MARS, Gödel Agent, …) als MCP-Tools ein.

Zwei Wege:
- **A) Integrieren** – wo bereits ein MCP-Server existiert (Graphiti, Cognee).
- **B) Selbst bauen** – wo Code existiert, aber kein MCP (7 Systeme).

Nicht baubar: Paper-Systeme (kein Code) → nur Info-Referenz.

---

## 2. Quellen (verifiziert, offiziell)

| # | Quelle | Was | Link |
|---|---|---|---|
| Q1 | MCP Python SDK (offiziell) | `FastMCP`, Server in 15 Zeilen | https://github.com/modelcontextprotocol/python-sdk |
| Q2 | MCP-Spezifikation (offiziell) | Protokoll-Standard | https://modelcontextprotocol.io/ |
| Q3 | MCP-Registry (offiziell) | Alle veröffentlichten Server | https://registry.modelcontextprotocol.io/ |
| Q4 | MCP Reference Servers (offiziell) | Memory, Sequential Thinking, Everything, … | https://github.com/modelcontextprotocol/servers |
| Q5 | MCP Example Remote Server (offiziell) | Voll-Beispiel + OAuth | https://github.com/modelcontextprotocol/example-remote-server |
| Q6 | Graphiti MCP (offiziell) | fertiger Server | https://github.com/getzep/graphiti/blob/main/mcp_server/README.md |
| Q7 | Cognee MCP (offiziell) | fertiger Server | https://docs.cognee.ai/cognee-mcp/mcp-overview |
| Q8 | Python SDK Docs | „Building Servers" | https://py.sdk.modelcontextprotocol.io/v1/server/ |

> Alle Links HTTP-verifiziert (siehe `ergebnisse/quellen-test.md`-Methode).

---

## 3. Baukasten (offiziell)

### 3.1 SDK-Befehle
```bash
uv add "mcp[cli]"          # SDK + CLI installieren
mcp dev server.py          # lokaler Test (MCP Inspector)
mcp run server.py --transport streamable-http
```

### 3.2 Bau-Muster (offiziell, FastMCP)
```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("hela-mem")          # Name = Connector/System

@mcp.tool()
def store_episodic(text: str) -> str:
    """Store an episodic memory."""   # Docstring → Tool-Beschreibung
    return ...                        # unsere System-Logik

if __name__ == "__main__":
    mcp.run(transport="stdio")        # stdio (lokal) oder streamable-http
```

### 3.3 Offizielle Referenz-Server (als Vorlage)
| Referenz | Zweck | Als Vorlage für |
|---|---|---|
| **Memory** | Knowledge-Graph-Memory | HeLa-Mem |
| **Sequential Thinking** | reflektierendes Denken | MARS, Reflexion, ReAct |
| **Everything** | Test aller Features | Gödel Agent |
| **Fetch / Filesystem / Git / Time** | einfache Muster | Basis-Beispiele |

---

## 4. Best-Match: System → Vorlage

| Unser System | Aktion | Beste Vorlage |
|---|---|---|
| **Graphiti** | integrieren | Q6 (fertig) |
| **Cognee** | integrieren | Q7 (fertig) |
| **HeLa-Mem** | bauen | Memory-Server (Q4) |
| **Reflexion** | prüfen→bauen | `reflexion-kit` (Community) + Sequential Thinking (Q4) |
| **Gödel Agent** | bauen | Everything-Server (Q4) |
| **MARS** | bauen | Sequential Thinking (Q4) |
| **TRACE** | bauen | `arunshar/trace` / `trace-mcp` (Community) |
| **ReAct** | bauen | Sequential Thinking (Q4) |
| **Agent-Dice** | bauen | custom (keine Vorlage) |
| **ADAS** | bauen | custom (keine Vorlage) |

> **Namensgleichheiten-Warnung:** „MARS", „ADAS", „TRACE", „HeLa" existieren
> mehrfach als fremde Projekte → nur das **exakte Repo** aus dem Connector matchen.

---

## 5. Vorgehen (6 Schritte pro System)

1. **Holen** – SDK + passenden Referenz-Server klonen
   (`git clone` von Q1/Q4).
2. **Studieren** – Muster ablesen (Tool-Deklaration, Transport, Config).
3. **Übertragen** – System-Funktionen als `@mcp.tool()` einwickeln
   (nur verifizierte Module, z.B. `hela_mem/hebbian_memory.py`).
4. **Testen** – `mcp dev server.py` (MCP Inspector, offiziell).
5. **Eintragen** – in `/home/opc/.config/opencode/opencode.json` → `mcp`-Block
   (`local` mit `command` / `remote` mit `url`).
6. **Freigabe** – **Human-Gate (§9)** vor Aktivierung.

---

## 6. AGENTS.md-Konformität

| Prinzip/Guardrail | Anwendung auf MCP-Plan |
|---|---|
| §1 Beobachte ohne zu deuten | erst prüfen (existiert MCP?), nicht deuten |
| §3 8-Stufen-Zyklus | Bau durchläuft Erfahrung→…→Wissen+ |
| §4 Brich die Muster (mit Quellen) | neuer Server nur mit Beleg-Trace + Link + Freigabe |
| §5 Wie eine Wolke | Policies revidierbar (Config, nicht fest verdrahtet) |
| **§6 Keine Erfindungen** | nur offizielle Muster (Q1–Q8) kopieren, keine erfundenen Tools |
| §9 Automatisches Gate | neue Quelle → **ask**; Interface-Änderung → **ask** |
| §10 Fast Write Routing | Router unterhalb des Gates; speichert in Cognee/Graphiti |

### Guardrails (verbindlich)
- Jede MCP-Verbindung = **neue Quelle** → **Human-Gate (ask)** (§9).
- Neue Tools/Signaturen = **Interface-Änderung** → **Human-Gate (ask)** (§9).
- Provenienz: jede Verbindung in `ergebnisse/` mit Quelle.
- Fremd-Code vor Integration prüfen (Lizenz, Aktivität, Sicherheit).

---

## 7. Offene Entscheidungen (an den Menschen)

| # | Frage | Optionen |
|---|---|---|
| 1 | Start-Scope | nur P1 (Graphiti+Cognee) / auch P2 |
| 2 | Hosting | lokal (stdio/Docker) / remote (HTTP) |
| 3 | LLM-Provider | vorhandene NVIDIA-Keys / Ollama lokal |
| 4 | Fremd-Code | akzeptieren / nur offizielle Vorlagen |
| 5 | Tier-3 (Paper) | Info belassen / Doku-Tool bauen |
| 6 | Freigabe §9 | erforderlich vor Aktivierung |

---

## 8. Roadmap

| Phase | Inhalt | Systeme | Aufwand | Status |
|---|---|---|---|---|
| **P1** | integrieren (fertig) | Graphiti, Cognee | niedrig | ✅ fertig |
| **P2** | bauen (Vorlage Memory/Sequential Thinking) | HeLa-Mem, Reflexion, ReAct | mittel | ✅ fertig |
| **P3** | bauen | MARS, TRACE | mittel–hoch | ✅ fertig |
| **P4** | bauen (custom) | Gödel Agent, Agent-Dice, ADAS | hoch | ✅ fertig |
| **P5** | Info belassen | 9 Paper-Systeme | niedrig | ✅ dokumentiert |

### P5 – Info-Systeme (kein Code → nicht ausführbar)

| System | Quelle | Warum kein MCP |
|---|---|---|
| AgentO | arXiv:2007.09454 | Ontologie/Paper, kein Server-Code |
| ARIADNE | arXiv:2105.09864 | Spezifikation, kein Code |
| AWS Semantic Layer | AWS Prescriptive Guidance | Doku/Beispiel, kein MCP |
| SEAA | arXiv:2609.17331 | Paper, kein MCP |
| HTAC | ICML 2026 Poster 63033 | Poster, kein Code |
| EvoPathBench | arXiv:2609.24663 | Benchmark-Paper |
| JISEM (Affective) | JISEM 2025 | Journal-Paper |
| CCA | IEEE/HAL | Paper |
| Fast Write Routing | arXiv:2608.22215 | Paper („Code upon acceptance") |

> Diese bleiben **Info-/Quellen-Referenzen** (Lab-konform zitierbar), **nicht** als
> ausführende MCP-Tools. Kein Fake-„Execution"-Server (§6).

### P1–P4 – Ergebnis (16 aktive MCP-Server)

| Server | Typ | Quelle |
|---|---|---|
| graphiti | integriert | getzep/graphiti |
| cognee | integriert | topoteretes/cognee |
| hela-mem | gebaut | ReinerBRO/HeLa-Mem |
| reflexion | gebaut | noahshinn/reflexion |
| react | gebaut | noahshinn/reflexion |
| mars | gebaut | Paparare/MARS |
| trace | gebaut | Kepler1908/TRACE |
| godel-agent | gebaut | Arvid-pku/Godel_Agent |
| agent-dice | gebaut | Wuzheng02/Agent-Dice |
| adas | gebaut | ShengranHu/ADAS |

---

## 9. Ergebnis (umgesetzt)

- **Integriert:** 2 (Graphiti, Cognee).
- **Gebaut nach offizieller Vorlage:** 8 (HeLa-Mem, Reflexion, ReAct, MARS, TRACE,
  Gödel Agent, Agent-Dice, ADAS).
- **Aktiv in `opencode.json`:** **16 MCP-Server** (10 Projekt-Connectoren + 6 bestehende).
- **Info belassen:** 9 Paper-Systeme (nicht ausführbar, nur Quelle).
- **Nichts erfunden:** Offizielles MCP-Muster kopiert; System-Funktionen/Prompts
  wörtlich übernommen. Alle Schritte unter Human-Gate (§9).

### Betrieb
- **opencode neu starten** → lädt die neuen MCP-Server.
- **Graphiti** braucht FalkorDB: `docker start graphiti-falkordb` (Port 6380).
- **LLM-Provider:** NVIDIA-Endpoint (`nemotron-3-super-120b` + `nemotron-3-embed-1b`).

---

## 10. Provenienz (Lab-Prinzip §6)

- Dieses Dokument beruht ausschließlich auf den Quellen Q1–Q8 (Abschnitt 2).
- Keine erfundenen Server, Tools oder Zahlen.
- Jeder gebaute Server nutzt **wörtlich vorhandene** Funktionen/Prompts:
  - HeLa-Mem: `hela_mem/hebbian_*.py`
  - Reflexion/ReAct: `hotpotqa_runs/prompts.py`
  - MARS: `prompts.json`
  - TRACE: `src/metrics.py`, `src/scoring.py`
  - Gödel Agent: `src/agent_module.py`
  - Agent-Dice: `Code/merge_atlas.py`
  - ADAS: `_arc/arc_prompt.py`
- Alle Server in `/home/opc/mcp-servers/` mit eigenem venv.

**Status: P1–P5 abgeschlossen.** Alle ausführbaren Systeme sind als MCP-Server
integriert; die Paper-Systeme bleiben Info-Referenzen.
