# 014 – Ingestion-Hook v2: 4 Forschungslücken geschlossen

> Datum: 2026-10-01
> Rekursionstiefe: System-Iteration (Memory-Pipeline), nicht Solver-t
> Phase: Revise (Hook erweitert)
> Zweck: `data/memory/ingestion_hook.py` auf Forschungsniveau bringen.
> Auslöser: menschlicher Auftrag vom 2026-10-01.

## 1. Zustand vorher / nachher

| | vorher (v1) | nachher (v2) |
|---|---|---|
| Write-Path | Dedup + EncodingGate (Länge/Typ/Vertrauen) | + **Privacy-Filter** (4. Prüfung) |
| Enrichment-Stufen | String-Platzhalter | **resolve_entities** (deterministisch), **update_graph** (Konsistenz), **consolidate** (Forgetting) |

## 2. Änderungen (Diff, kompakt)

- `+ PrivacyFilter` (agentmemory): erkennt Secrets (`sk-proj-`, `password=`,
  `ghp_`, Bearer, PEM, DB-URLs) + `<private>`-Tags → **rejected**.
- `+ resolve_entities(text)` (GraphRAG/GLiNER-Prinzip): deterministische,
  lokale, reproduzierbare Entity-Liste.
- `+ MemoryGraph` / `update_graph(...)` (GraphRAG/Neo4j MKG/Memory Survey):
  Dedup + **Konflikt-Erkennung** (funktional / asymmetrisch) → Graph-Delta.
- `+ consolidate(graph, now)` (HeLa-Mem): **Adaptive Forgetting**
  (3 Bedingungen, δ_prune) + **Hub-Detection** (δ_hub) → Report.
- `EnrichmentQueue.worker` führt jetzt die echten Stufen aus.

## 3. Compare-Beleg (externes Signal)

Selbsttest: `python3 data/memory/ingestion_hook.py` — **reale** Ausgabe
(siehe `ergebnisse/ingestion-hook.md` §6). Ergebnis:

| Prüfung | Ergebnis |
|---|---|
| Privacy (`sk-proj-`, `password=`, `ghp_`, `<private>`) | ✅ rejected |
| Entity-Resolution reproduzierbar (2. Lauf) | ✅ identisch |
| Graph-Update: 2 widersprüchliche Kanten | ✅ rejected + Grund |
| Konsolidierung: Hub behalten / isolierter Knoten vergessen | ✅ |

## 4. Quellen (belegt, HTTP 200)

- https://github.com/rohitg00/agentmemory (Privacy-Filter)
- https://github.com/FalkorDB/GraphRAG-SDK + https://arxiv.org/abs/2605.10108 (Entity-Resolution/GLiNER)
- https://github.com/neo4j-labs/meta-knowledge-graph (Graph-Write)
- https://arxiv.org/abs/2604.16839 (HeLa-Mem, Adaptive Forgetting)
- https://arxiv.org/abs/2603.07670 (Memory Survey, Konsolidierung/Kontradiktion)
- https://github.com/ronsse/trellis-ai (LLM never in write path)

## 5. Schwellen (Auftrag, nicht forschungsbelegt)

δ_hub=1.5, δ_prune=0.5, δ_age=60 Tage, min_len=12, max_len=8000,
min_trust=0.5, Dedup-Fenster=300 s. (τ=60, η=0.02, λ=0.995 = **belegt** aus HeLa-Mem.)

## 6. Guardrails

- Kein `self_update` an Originaldateien ausser `data/memory/ingestion_hook.py`
  (Auftrag). **`AGENTS.md` unverändert.**
- Fail-soft: Hook wirft nie in den Agent-Flow (try/except).

## 7. Freigabe

**Freigabe-Status für π₁:** `approved: Batnini, 2026-10-01`
(Auslöser: menschlicher Auftrag vom 2026-10-01; freigegeben).
