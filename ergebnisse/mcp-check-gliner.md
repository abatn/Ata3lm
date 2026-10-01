# MCP-Check Auftrag 1: GLiNER — Abdeckung + Entscheidung

> Datum: 2026-10-01 · Auftrag 1 von 3 · Phase: Observe → Compare
> Lab-Prinzip §6: nur gemessene Werte, Rohausgaben aus den Läufen.
> Alle Quellen vor Verwendung auf HTTP 200 geprüft (Methode aus
> `ergebnisse/test-quellen.md`).

## 1. Prüfung: Deckt einer der 16 MCP-Server GLiNER ab?

**Quelle der Prüfung:** `ergebnisse/mcp-16-test.md` (Handshake + vollständige
Tool-Listen aller 16 Server, Stand 2026-09-30) + direkter Code-Durchgriff auf
`/home/opc/mcp-servers/*-mcp/server.py`.

```bash
grep -in "drift\|lyapunov\|gliner\|ner\b\|entity" ergebnisse/mcp-16-test.md
# -> 1 Treffer, und der ist graphitis "delete_entity_edge" (Knoten- Löschen, kein NER)
```

| Server | Tools (Anzahl) | GLiNER/NER? |
|---|---|---|
| graphiti | 13 | nein (`delete_entity_edge` = KG-Löschung) |
| cognee | 11 | nein |
| hela-mem | 6 | nein |
| mars | 3 | nein |
| trace | 6 | nein |
| adas | 3 | nein |
| godel-agent | 2 | nein |
| reflexion / react / agent-dice | 1 / 1 / 1 | nein |
| kubernetes, n8n, obsidian, livekit-docs, sqlalchemy, visuals | (Umgebung) | nein |

**Ergebnis: KEIN MCP deckt GLiNER ab. → Option a/b greift.**

## 2. Entscheidung: a) echtes GLiNER installieren (Human-Gate: approved)

Menschliche Freigabe 2026-10-01: **Option a** (statt b: Regeln nur als Auftrag).

### 2.1 Installation (real, lokal, keine API-Calls)

| Schritt | Ergebnis |
|---|---|
| Ziel-venv | `/home/opc/mcp-servers/hela-mem-mcp/.venv` (Python 3.12.13) — dieselbe, die `governance-mcp` nutzt |
| Warum nicht System-Python | `gliner 0.2.29` verlangt `requires_python >=3.10`; System-`python3` = 3.9.25 |
| Paket | `gliner==0.2.29` + `sentencepiece` mit `--no-deps` (bewusst) |
| `--no-deps`-Grund | gliner pinnt `transformers<5.17.0`; die venv hat **5.18.0**. Ein normales Install hätte transformers **downgegraded** und die fremde venv beschädigt. |
| Nachinstalliert | `protobuf` (ohne: SentencePiece-Extractor scheitert), `tiktoken` (Fallback der fehlschlägt) |
| Modell | `urchade/gliner_multi-v2.1` (HuggingFace, 5 Dateien, HTTP 200) |
| Kontrolle | `transformers` **bleibt 5.18.0** (vorher = nachher) |

```bash
uv pip install --python /home/opc/mcp-servers/hela-mem-mcp/.venv/bin/python \
     --no-deps gliner==0.2.29 sentencepiece
uv pip install --python /home/opc/mcp-servers/hela-mem-mcp/.venv/bin/python \
     protobuf tiktoken
```

### 2.2 Kalibrierung des Schwellenwerts (§9.1c: Schwellen kalibrieren, nicht setzen)

Gemessen an den beiden realen Testsätzen des Projekts:

| threshold | Satz 1 (Enrichment-Text) | Satz 2 (Demo-Text) |
|---|---|---|
| 0.5 (bisher im Code, **unbelegt**) | **`[]`** (Score 0.4775 → verworfen) | `Fast Write Routing` (0.5537) |
| **0.4 (neuer Default)** | `Fast Write Routing` (0.4775) | `Fast Write Routing` (0.5537), `Konstrukt` (0.4347) |
| 0.3 | `Fast Write Routing` | + `Der Knowledge-Agent` (0.3161, **falsch** als `Solver`) |

Schlussfolgerung: 0.5 machte die Enrichment-Stufe faktisch wirkungslos (0 Treffer),
0.3 zieht Fehl-Rauschen mit falschem Label ein. **Default = 0.4**, per
`GLINER_THRESHOLD` überschreibbar. Kein Signatur-/Interface-Wechsel
(Parameter ändert sich nicht, nur der Default).

### 2.3 Selbsttest (real, Rohausgabe)

```bash
V=/home/opc/mcp-servers/hela-mem-mcp/.venv
$V/bin/python -W ignore data/memory/ingestion_hook.py
```

```
=== [2] Entity-Resolution (deterministisch, GLiNER-Prinzip) ===
  Entitäten: [('Concept', 'Fast Write Routing', 0.5537), ('Concept', 'Konstrukt', 0.4347)]
  Reproduzierbar (2. Lauf identisch): True
...
=== Enrichment (async) verarbeitet: 1 Item(s) ===
  steps: ['entity-resolution', 'graph-update', 'consolidation'] | entities: ['Fast Write Routing']
```

**Fail-Soft-Nachweis** (System-Python 3.9, `gliner` nicht importierbar):

```bash
python3 data/memory/ingestion_hook.py
```

```
=== [2] Entity-Resolution (deterministisch, GLiNER-Prinzip) ===
  Entitäten: [('Concept', 'Knowledge-Agent', 1.0), ('Concept', 'Fast Write Routing', 1.0),
              ('Phase', 'Konstrukt', 1.0), ('Stage', 'Handeln', 1.0)]
...
  entities: ['Knowledge-Agent', 'Fast Write Routing', 'Konstrukt']
```

### 2.4 Ehrlicher Vergleich der beiden Backends

| | `backend=rules` | `backend=gliner` (0.4) |
|---|---|---|
| Treffer Satz 1 | 3 (Knowledge-Agent, Fast Write Routing, Konstrukt) | 1 (Fast Write Routing) |
| Treffer Satz 2 | 4 (inkl. `Handeln`) | 2 |
| confidence | **1.0 bei jedem Treffer** (Wörterbuch, kein Modell) | 0.43–0.55 (modelliert) |
| unbekannter Term | nie gefunden | möglich (generalisiert) |
| Cost/Abhängigkeit | keine | torch + Modell (~30 s Kaltstart) |

Regeln haben auf dem geschlossenen Wörterbuch mehr Recall, sind aber
**über-sicher** (confidence=1.0 ist gesetzt, nicht gemessen) und können keine
unbekannten Terme finden. Beide Pfade bleiben erhalten: `auto → gliner falls
vorhanden, sonst rules`.

## 3. Quellen (HTTP 200 geprüft 2026-10-01)

| Quelle | Link | Status |
|---|---|---|
| GLiNER-Relex | https://arxiv.org/abs/2605.10108 | 200 |
| GraphRAG-SDK (Entity-Extraction Step 1) | https://github.com/FalkorDB/GraphRAG-SDK | 200 |
| Modell | https://huggingface.co/urchade/gliner_multi-v2.1 | 200 |
| GLiNER PyPI (`0.2.29`, `requires_python>=3.10`) | https://pypi.org/pypi/gliner/json | 200 |

## 4. Gate (§9)

| Bedingung | Wert | Ergebnis |
|---|---|---|
| Score (8 Tests, §`030`) | 8/8 = 100 % | allow |
| Neue Quelle? | nein — GLiNER-Relex/GraphRAG-SDK standen schon in `AGENTS.md`-Connector-Tabelle | — |
| Interface-Änderung? | nein (Default-Wert, keine Signatur) | — |
| Drift ≤ 10 %? | `ingestion_hook.py` 5/475 = **1,05 %** | ≤ Bound |

**Gate-Ergebnis: allow.** Menschliche Freigabe für die Installation lag
vorausgehend vor (Option a, 2026-10-01).
