# Ingestion-Hook – asynchron, deterministisch, gedächtniszentriert

> Datum: 2026-10-01
> Status: **Belegt** (Mechanik) + **Auftrag** (Schwellen/Implementierung)
> Prinzip: Keine Erfindungen (§6). Jede Aussage mit Quelle oder als Auftrag markiert.
> Code: `data/memory/ingestion_hook.py`

## 1. Quellen (verifiziert, HTTP 200)

| Quelle | Kernaussage (wörtlich/nah) | Link |
|---|---|---|
| **Trellis** (ADR + Design) | „**LLM never in the write path**"; deterministische Klassifikatoren inline, LLM opt-in (`allow_llm_fallback=False`); Background-**Worker** für Enrichment/Kuration; **fail-soft / never-raise** Hooks | https://github.com/ronsse/trellis-ai |
| **GraphRAG-SDK** (FalkorDB) | **Two-Step Extraction**: Step 1 `GLiNERExtractor` (lokal, **keine API-Calls**), Step 2 LLM (verify + relations); **Entity-Resolution** | https://github.com/FalkorDB/GraphRAG-SDK |
| **GLiNER-Relex** | deterministische, lokale NER+RE („same text always produces the same graph") | https://arxiv.org/abs/2605.10108 |
| **TrueMemory** | Memory-Lifecycle: **SessionStart / UserPromptSubmit / SessionEnd**; „runs the **encoding gate on each fact**" | https://github.com/buildingjoshbetter/TrueMemory |
| **agentmemory** | Lifecycle-Hooks; deterministische **SHA-256-Dedup (5-min)** + Privacy-Filter **vor** dem Store | https://github.com/rohitg00/agentmemory |

## 2. Architektur (Write-Path vs. Enrichment-Path)

```text
Lifecycle-Event (SessionStart | UserPromptSubmit | SessionEnd)
   │  WRITE-PATH: synchron, deterministisch, KEIN LLM
   ▼
[1] Dedup (SHA-256, 5-min) ──► Treffer → rejected
   ▼
[2] Encoding-Gate (Länge, Typ, Quellvertrauen) ──► Fail → rejected + Grund
   ▼
[3] Deterministische Tags (session_id, timestamp, source_type) → JSONL-Log
   │
   └─► ENRICHMENT-PATH: asynchron (off the write path)
        [4] Enrichment-Queue → Entity-Resolution → Graph-Update → Konsolidierung
```

- **Kein Write-Path-Block:** Der Hook schreibt nur deterministische Tags; die
  teure Arbeit (Enrichment) läuft **asynchron** danach.
- **Kein LLM im kritischen Pfad:** Quelle Trellis („LLM never in the write path").

## 3. Lifecycle-Events

| Event | Aktion |
|---|---|
| `SessionStart` | Session registrieren (deterministischer Tag) |
| `UserPromptSubmit` | Dedup → Encoding-Gate → Tag schreiben; bei „accept" Enrichment **async** einreihen |
| `SessionEnd` | Session-Abschluss-Tag |

Quelle: TrueMemory (Lifecycle) + agentmemory (Hook-Set).

## 4. Encoding-Gate (deterministisch)

| Regel | Wert | Status |
|---|---|---|
| Mindestlänge | 12 Zeichen | **Auftrag** |
| Maximallänge | 8000 Zeichen | **Auftrag** |
| Erlaubte Typen | `prompt`, `tool_result`, `transcript`, `note` | **Auftrag** |
| Quellvertrauen | ≥ 0.5 | **Auftrag** |

Quelle (Mechanik): TrueMemory „encoding gate"; agentmemory „deterministische
Filterung vor dem Store". Die konkreten Schwellen sind Projekt-Vorgabe.

## 5. Enrichment-Queue (asynchron)

- Stufen: **Entity-Resolution → Graph-Update → Konsolidierung**.
- Quelle: Trellis Background-Worker (enrichment/curation) + GraphRAG Entity-Resolution.
- Läuft nach dem Store, damit der Write-Path nicht blockiert.

## 6. Selbsttest (reale Ausgabe)

```text
=== Ingestion-Hook Demo (deterministisch, kein LLM) ===
SessionStart        -> session_start
UserPromptSubmit OK -> accepted | ok | enrichment: queued
Gate: zu kurz      -> rejected | zu kurz (4 < 12)
Gate: falscher Typ -> rejected | Typ 'unknown' nicht erlaubt
Dedup              -> rejected | Duplikat (SHA-256, 5-min-Fenster)
Gate: Quellvertr.  -> rejected | Quellvertrauen 0.2 < 0.5
SessionEnd          -> session_end
Enrichment (async) verarbeitet: 1 Item(s)
```

**Ergebnis:** Write-Path deterministisch + ohne LLM; Gate filtert (Länge, Typ,
Quellvertrauen); Dedup greift; Enrichment läuft asynchron (1 akzeptiertes Item).

## 7. Status-Trennung

| Aussage | Status |
|---|---|
| LLM nicht im Write-Path; deterministisch zuerst | **Belegt** (Trellis) |
| Lifecycle-Events SessionStart/UserPromptSubmit/SessionEnd | **Belegt** (TrueMemory/agentmemory) |
| Encoding-Gate pro Fakt | **Belegt** (TrueMemory) |
| Asynchrone Enrichment-Worker (Resolution/Graph/Konsolidierung) | **Belegt** (Trellis/GraphRAG) |
| Konkrete Schwellen (12/8000/0.5/5-min) | **Auftrag** (Projekt-Vorgabe) |
| Implementierung `ingestion_hook.py` | **Auftrag** (Projekt) |

## 8. Dateien

| Artefakt | Art |
|---|---|
| `data/memory/ingestion_hook.py` | neu (Implementierung) |
| `ergebnisse/ingestion-hook.md` | neu (dieses Dokument) |
| `.gitignore` | Runtime-Log ausgenommen |

## 9. Quellen (alle HTTP 200, 2026-10-01)

- https://github.com/ronsse/trellis-ai
- https://github.com/FalkorDB/GraphRAG-SDK
- https://arxiv.org/abs/2605.10108 (GLiNER-Relex)
- https://github.com/buildingjoshbetter/TrueMemory
- https://github.com/rohitg00/agentmemory
