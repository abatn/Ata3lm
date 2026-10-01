# Ingestion-Hook – asynchron, deterministisch, gedächtniszentriert

> Datum: 2026-10-01 (v2: 4 Forschungslücken geschlossen)
> Status: **Belegt** (Mechanik) + **Auftrag** (Schwellen/Implementierung)
> Prinzip: Keine Erfindungen (§6). Jede Aussage mit Quelle oder als Auftrag markiert.
> Code: `data/memory/ingestion_hook.py`

## 1. Quellen (verifiziert, HTTP 200)

| Quelle | Kernaussage (wörtlich/nah) | Link |
|---|---|---|
| **Trellis** (ADR + Design) | „**LLM never in the write path**"; deterministische Klassifikatoren inline; Background-Worker; **fail-soft / never-raise** | https://github.com/ronsse/trellis-ai |
| **GraphRAG-SDK** (FalkorDB) | **Two-Step Extraction**: Step 1 `GLiNERExtractor` (lokal, keine API-Calls), Step 2 LLM; **Entity-Resolution** | https://github.com/FalkorDB/GraphRAG-SDK |
| **GLiNER-Relex** | deterministische, lokale NER+RE („same text always produces the same graph") | https://arxiv.org/abs/2605.10108 |
| **TrueMemory** | **SessionStart / UserPromptSubmit / SessionEnd**; „runs the **encoding gate on each fact**" | https://github.com/buildingjoshbetter/TrueMemory |
| **agentmemory** | Lifecycle-Hooks; **SHA-256-Dedup (5-min)**; „**Privacy first — API keys, secrets, `<private>` tags stripped before storage**"; Security-Advisory nennt Muster (Bearer, `sk-proj-`, `gh[pus]_`, PEM, DB-URLs) | https://github.com/rohitg00/agentmemory |
| **Neo4j MKG** | `PostToolUse`-Hook schreibt **typisierte Knoten** in den Graph | https://github.com/neo4j-labs/meta-knowledge-graph |
| **HeLa-Mem** (ACL 2026) | **Adaptive Forgetting** = 3 Bedingungen gleichzeitig: (1) edge weight < **δ_prune**, (2) inactive > **δ_age**, (3) **zero recent access**; **Hub Detection** = edge weight > **δ_hub**; τ=60, η=0.02, λ=0.995 | https://arxiv.org/abs/2604.16839 |
| **Memory Survey** (arXiv:2603.07670) | Konsolidierung (Episoden → Semantik), **Kontradiktions-Erkennung**, „learned forgetting", periodische Konsolidierung | https://arxiv.org/abs/2603.07670 |

> **Korrektur ggü. Auftragstext:** Der Auftrag nannte für Adaptive Forgetting
> „edge_weight < **δ_hub**". Die Quelle sagt **δ_prune** (Bedingung 1); δ_hub ist
> die *Hub-Detection*-Schwelle. Implementiert ist **δ_prune** (quellenkonform).

## 2. Architektur (Write-Path vs. Enrichment-Path)

```text
Lifecycle-Event (SessionStart | UserPromptSubmit | SessionEnd)
   │  WRITE-PATH: synchron, deterministisch, KEIN LLM
   ▼
[1] Dedup (SHA-256, 5-min) ─────────────► Treffer → rejected
   ▼
[2] Encoding-Gate (Länge, Typ, Quellvertrauen, PRIVACY) ─► Fail → rejected + Grund
   ▼
[3] Deterministische Tags (session_id, timestamp, source_type) → JSONL-Log
   │
   └─► ENRICHMENT-PATH: asynchron (off the write path)
        [4] Entity-Resolution → [5] Graph-Update (Konsistenz) → [6] Konsolidierung
```

## 3. Lifecycle-Events

| Event | Aktion |
|---|---|
| `SessionStart` | Session registrieren (deterministischer Tag) |
| `UserPromptSubmit` | Dedup → Gate → Tag; bei „accept" Enrichment **async** |
| `SessionEnd` | Session-Abschluss-Tag |

## 4. Encoding-Gate (deterministisch)

| Regel | Wert | Status |
|---|---|---|
| Mindestlänge | 12 | Auftrag |
| Maximallänge | 8000 | Auftrag |
| Erlaubte Typen | prompt, tool_result, transcript, note | Auftrag |
| Quellvertrauen | ≥ 0.5 | Auftrag |
| **Privacy (4. Prüfung)** | Secret-/private-Muster | **Belegt** (agentmemory) |

## 5. Erweiterungen (die 4 Forschungslücken)

### 5.1 Privacy-Filter VOR dem Store — **Belegt** (agentmemory)
- **Mechanik (belegt):** „API keys, secrets, `<private>` tags stripped before
  storage"; Security-Advisory listet Muster (Bearer, `sk-proj-*`, `gh[pus]_*`,
  PEM, DB-URLs). Deterministisch, **kein LLM**.
- **Implementierung:** `PrivacyFilter.scan()/redact()`, als **4. Prüfung** im
  `EncodingGate` (vor dem Log-Write).
- **Test:** `sk-proj-…`, `password=…`, `ghp_…`, `<private>…</private>` → **rejected**.

### 5.2 Entity-Resolution als echte Stufe — **Belegt** (GraphRAG-SDK/GLiNER)
- **Mechanik (belegt):** Step 1 GLiNER lokal, keine API-Calls, deterministisch
  („same text always produces the same graph").
- **Implementierung:** `resolve_entities(text)` → Liste
  `{entity_type, span, start, end, confidence}`.
- **Ehrlich:** Regeln/Wörterbuch (kein GLiNER-Modell installiert) — setzt das
  GLiNER-**Prinzip** um (lokal, deterministisch, reproduzierbar), ist aber
  **nicht** GLiNER selbst.
- **Test:** gleicher Satz → gleiche Entitäten (2. Lauf identisch = `True`).

### 5.3 Graph-Update mit Konsistenzprüfung — **Belegt** (GraphRAG / Neo4j MKG)
- **Mechanik (belegt):** Graph-Write typisierter Knoten; Entity-Resolution;
  Kontradiktions-Erkennung (Memory Survey: „contradiction detection").
- **Implementierung:** `update_graph(graph, entities, relations)` → Graph-Delta
  (`added_nodes`, `added_edges`, `deduped`, `rejected`). Konflikte:
  (a) funktionale Relation mit zweitem Objekt, (b) asymmetrische Relation in
  Gegenrichtung.
- **Test:** `(a supersedes b)` + `(b supersedes a)` → **rejected**;
  `(i1 hasEnd 05-01)` + `(i1 hasEnd 06-01)` → **rejected**.

### 5.4 Konsolidierung mit Vergessens-Operator — **Belegt** (HeLa-Mem, Memory Survey)
- **Mechanik (belegt):** Adaptive Forgetting (3 Bedingungen: edge weight <
  **δ_prune**, inactive > **δ_age**, zero recent access); Hub-Detection
  (edge weight > **δ_hub**) → Hebbian Distillation.
- **Implementierung:** `consolidate(graph, now_ts)` → Report
  (`hubs`, `forgotten`, `kept`).
- **Schwellen:** δ_hub=1.5, δ_prune=0.5, δ_age=60 Tage (**Auftrag**);
  τ=60, η=0.02, λ=0.995 (**belegt**, HeLa-Mem).
- **Test:** Hub n2 (weight 1.8) → **hub** (nicht evakuiert); isolierter n5
  (weight 0.1, 100 Tage inaktiv, 0 Zugriffe) → **forgotten**.

## 6. Selbsttest (reale Ausgabe)

```text
=== [0] Lifecycle + Gate + Dedup ===
  OK                -> accepted | enrichment: queued
  zu kurz           -> rejected | zu kurz (4 < 12)
  Dedup             -> rejected | Duplikat (SHA-256, 5-min-Fenster)

=== [1] Privacy-Filter VOR dem Store (agentmemory) ===
  Mein Key: sk-proj-ABCDEFGHIJKLMNOP -> rejected | Privacy: Secret-Muster: sk-proj-[A-Za-z0-9\-_]{20,}
  password=SuperGeheim123            -> rejected | Privacy: Secret-Muster: (?:api[_-]?key|token|secret|password|pas
  Token ghp_ABCDEFGHIJKLMNOPQRSTUVWX -> rejected | Privacy: Secret-Muster: gh[pus]_[A-Za-z0-9]{36,}
  Inhalt <private>geheim</private> h -> rejected | Privacy: private-Tag (<private>...</private>) gefunden

=== [2] Entity-Resolution (deterministisch, GLiNER-Prinzip) ===
  Entitäten: [('Concept', 'Knowledge-Agent', 1.0), ('Concept', 'Fast Write Routing', 1.0), ('Phase', 'Konstrukt', 1.0), ('Stage', 'Handeln', 1.0)]
  Reproduzierbar (2. Lauf identisch): True

=== [3] Graph-Update mit Konsistenzprüfung ===
  add (a supersedes b) -> added: [('solver_a', 'supersedes', 'solver_b')]
  add (b supersedes a) -> rejected: ['Konflikt: Gegenrichtung solver_a supersedes solver_b existiert']
  add (i1 hasEnd 05-01) -> added: [('i1', 'hasEnd', '2024-05-01')]
  add (i1 hasEnd 06-01) -> rejected: ['Konflikt: i1 hasEnd bereits -> 2024-05-01']

=== [4] Konsolidierung mit Vergessens-Operator (HeLa-Mem) ===
  Hubs (δ_hub, distill): [('hub_n2', 1.8)]
  Forgotten (δ_prune/δ_age/0-access): [('isolated_n5', 0.1, 100.0)]
  Kept: []

=== Enrichment (async) verarbeitet: 1 Item(s) ===
  steps: ['entity-resolution', 'graph-update', 'consolidation'] | entities: ['Knowledge-Agent', 'Fast Write Routing', 'Konstrukt']
```

**Ergebnis:** Alle 4 Prüfungen bestehen — Privacy rejectet Secrets/`<private>`;
Entity-Resolution ist reproduzierbar; Graph-Update rejectet beide Konfliktarten;
Konsolidierung behält den Hub und vergisst den isolierten Knoten.

## 7. Status-Trennung

| Aussage | Status |
|---|---|
| LLM nicht im Write-Path; deterministisch zuerst | **Belegt** (Trellis) |
| Lifecycle-Events SessionStart/UserPromptSubmit/SessionEnd | **Belegt** (TrueMemory/agentmemory) |
| Encoding-Gate pro Fakt | **Belegt** (TrueMemory) |
| Privacy-Filter (Secrets/`<private>`) vor dem Store | **Belegt** (agentmemory) |
| Entity-Resolution deterministisch/lokal | **Belegt** (GraphRAG/GLiNER) |
| Graph-Write + Kontradiktions-Erkennung | **Belegt** (GraphRAG/MKG/Memory Survey) |
| Adaptive Forgetting (3 Bedingungen, δ_prune) | **Belegt** (HeLa-Mem) |
| Konkrete Schwellen (12/8000/0.5/5min/1.5/0.5/60) | **Auftrag** |
| Regelbasierte statt GLiNER-Modell-NER | **Auftrag** (Approximation) |
| Implementierung `ingestion_hook.py` | **Auftrag** |

## 8. Dateien

| Artefakt | Art |
|---|---|
| `data/memory/ingestion_hook.py` | erweitert (v2: 4 Erweiterungen) |
| `ergebnisse/ingestion-hook.md` | erweitert (dieses Dokument) |
| `ergebnisse/rekursion/014-*.md` | Provenienz dieser Iteration |

## 9. Quellen (alle HTTP 200, 2026-10-01)

- https://github.com/ronsse/trellis-ai
- https://github.com/FalkorDB/GraphRAG-SDK
- https://arxiv.org/abs/2605.10108 (GLiNER-Relex)
- https://github.com/buildingjoshbetter/TrueMemory
- https://github.com/rohitg00/agentmemory
- https://github.com/neo4j-labs/meta-knowledge-graph
- https://arxiv.org/abs/2604.16839 (HeLa-Mem)
- https://arxiv.org/abs/2603.07670 (Memory Survey)
