# Gesamtprüfung MCP – End-to-End-Test

> Datum: 2026-09-30
> Umfang: Alle 16 aktiven MCP-Server + Tool-Test + E2E-Rekursion t=6
> Lab-Prinzip: Keine Erfindungen – nur tatsächliche Ausgaben.

---

## Aufgabe 1 + 2: Server- & Tool-Test

### Alle 16 Server

| # | Server | Typ | Handshake | Tools | Tool-Call |
|---|---|---|---|---|---|
| 1 | graphiti | local | ✅ | 13 | ✅ `add_memory` |
| 2 | cognee | local | ✅ | 11 | ⚠️ Timeout |
| 3 | hela-mem | local | ✅ | 6 | ✅ `store_episodic` |
| 4 | reflexion | local | ✅ | 1 | ✅ `reflect` |
| 5 | react | local | ✅ | 1 | ✅ `react_step` |
| 6 | mars | local | ✅ | 3 | ✅ `mars_run_strategy` |
| 7 | trace | local | ✅ | 6 | ✅ `metric_recall_at_k` |
| 8 | godel-agent | local | ✅ | 2 | ✅ `run_code` |
| 9 | agent-dice | local | ✅ | 1 | ✅ `geometric_consensus_fuse` |
| 10 | adas | local | ✅ | 3 | ✅ `adas_init_archive` |
| 11 | kubernetes | local | ✅ | 23 | (nicht getestet) |
| 12 | n8n-mcp | local | ✅ | viele | (nicht getestet) |
| 13 | obsidian | local | ✅ | viele | (nicht getestet) |
| 14 | livekit-docs | remote | ✅ | (remote) | (nicht getestet) |
| 15 | sqlalchemy-mcp | local | ❌ | — | — |
| 16 | visuals-mcp | local | ❌ | — | — |

**14/16 antworten. 2 fehlgeschlagen.**

### Fehlgeschlagene Server
| Server | Fehler |
|---|---|
| sqlalchemy-mcp | `[Errno 2] No such file or directory: 'sqlalchemy-mcp-server'` |
| visuals-mcp | `[Errno 2] No such file or directory: 'visuals-mcp'` |

> Beide sind **Umgebungs-Server** (nicht Projekt) mit fehlenden Binaries.

---

## Aufgabe 3: E2E-Rekursion t=6

**Aufgabe:** `berechne_median` (neuer Solver v6).

| Schritt | Ergebnis |
|---|---|
| Observe | π₀ = `liste[len(liste)//2]` (Bug) |
| Compare | **2/4** (Python-Interpreter) |
| Revise | MARS-Reflexion: „erst sortieren, dann Median" |
| Konstrukt | `solver_v6_improved.py` |
| Akt | **4/4** (Python-Interpreter) |

**Genutzte MCPs:**
| MCP | Tool | Reale Ausgabe |
|---|---|---|
| HeLa-Mem | `store_episodic` | `{"stored": true, "node_id": "2"}` ✅ |
| MARS | `mars_analyze_failure` | „sortiere zuerst…" ✅ |
| Graphiti | `add_memory` | `Episode 't6-rekursion' queued` ✅ |
| Cognee | `remember` | ⚠️ Timeout (>280s) |

Dokument: `ergebnisse/rekursion/013-t6-rekursion.md`

---

## Aufgabe 4: Gesamturteil

### Sind alle 16 MCPs funktionsfähig?

## ⚠️ NEIN – 14/16 funktionsfähig

| Kategorie | Anzahl |
|---|---|
| Funktionsfähig (Handshake OK) | **14** |
| Fehlgeschlagen (Binary fehlt) | **2** (sqlalchemy-mcp, visuals-mcp) |
| Projekt-MCPs funktionsfähig | **10/10** ✅ |
| Tool-Calls erfolgreich | **9/10** (cognee Timeout) |

### Offene Punkte

| # | Punkt | Kategorie | Schwere |
|---|---|---|---|
| 1 | sqlalchemy-mcp: Binary fehlt | Umgebungs-Server | 🟠 Mittel |
| 2 | visuals-mcp: Binary fehlt | Umgebungs-Server | 🟠 Mittel |
| 3 | cognee `remember` zu langsam (>280s) | Projekt-Server | 🟡 Niedrig |
| 4 | Rekursion t=6 = `pending` | Freigabe | 🟡 Niedrig |
| 5 | kubernetes/n8n/obsidian/livekit Tool-Calls nicht getestet | Test-Umfang | 🟡 Niedrig |

### Was funktioniert ✅
- ✅ **Alle 10 Projekt-MCP-Server** antworten (Handshake + Tools)
- ✅ 9/10 Projekt-Tool-Calls erfolgreich
- ✅ E2E-Rekursion t=6: π₀=2/4 → π₁=4/4 (mit HeLa-Mem, MARS, Graphiti)
- ✅ Graphiti + FalkorDB (temporaler Graph) funktioniert
- ✅ 14/16 Server insgesamt erreichbar

### Was nicht funktioniert ❌
- ❌ `sqlalchemy-mcp` (Binary `sqlalchemy-mcp-server` fehlt)
- ❌ `visuals-mcp` (Binary `visuals-mcp` fehlt)
- ⚠️ `cognee` `remember` (zu langsam, Timeout)

---

## Ausgabe-Dateien
| Datei | Inhalt |
|---|---|
| `ergebnisse/mcp-16-test.md` | Server + Tool-Test |
| `ergebnisse/rekursion/013-t6-rekursion.md` | E2E-Rekursion t=6 |
| `ergebnisse/gesamtpruefung-mcp.md` | dieses Urteil |

---

**Endgültiges Urteil:** **14/16 MCP-Server funktionsfähig.** Die **10 Projekt-MCP-Server
sind alle funktionsfähig** (Handshake + Tools; 9/10 Tool-Calls erfolgreich). Die 2
fehlgeschlagenen Server (`sqlalchemy-mcp`, `visuals-mcp`) sind **Umgebungs-Server**
mit fehlenden Binaries – **nicht Teil des Projekts**. Alle Zahlen sind ehrlich
dokumentiert (Lab-Prinzip §6).
