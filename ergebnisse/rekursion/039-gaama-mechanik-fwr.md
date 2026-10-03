# Rekursion 039: GAAMA-Paper-Mechanik (d=2, Hub-Dampening) + §10.1-FWR

> Datum: 2026-10-03 · Tiefe: `t=38 → t=39` · Phase: **Revise → Handeln**
> Freigabe: `approved: Batnini, 2026-10-03` („ja … nach AGENTS.md und ganz wichtig die Dokumentation").
> Ziel `g`: fehlende GAAMA-Mechanik (Expansion d=2, Hub-Dampening) + §10.1-FWR-Routing.

## 1. Quellen

- GAAMA arXiv:2603.27910 §3.4 (d=2, α=0.6, additive Bewertung) + Repo
  `services/ltm_retriever.py`, `services/pagerank.py` (`hub_dampening_threshold=50`,
  `degree_correction`).
- AGENTS.md §10.1 (Router beim Eintreffen eines Facts), §9 (Gate), §9.1d (Evidenz).

## 2. Änderung (Diff)

| Datei | Änderung |
|---|---|
| `data/memory/tier3-working/lru_cache.py` | `_bidirectional`, `expand_subgraph` (d=2), Hub-Dampening (`GAAMA_HUB_THRESHOLD=50`) + `degree_correction`; `hybrid_scores` nutzt beides |
| `data/memory/gaama_extract.py` | `route_extracted_facts(facts, classify_fn)` — **§10.1**: jeder Fact zuerst durch den FWR (injizierbar) |
| `tests/test_tier2_tier3.py` | +5 Tests (Hub-Dampening, degree_correction, expand_subgraph, bidirectional) |
| `tests/test_gaama_extract.py` | +2 Tests (§10.1-Routing) |
| `ergebnisse/tier2-tier3.md`, `ergebnisse/gaama-schema.md`, `connectors/gaama.md`, `tests/README.md` | nachgezogen |

## 3. Compare-Beleg (extern)

```text
make test -> 260 passed · Coverage 100,00 % (Line+Branch) · ruff clean
```

**Score** = 260/260 = **100 %**. **Drift:** additiv (neue Helfer + Tests); kein
Datenformat-Bruch → unter Drift-Bound (10 %).

## 4. Ehrlicher Befund

Das uniforme **Hub-Dampening** (GAAMA `edges_from_core_edges`) skaliert alle
Ausgangsgewichte eines Knotens gleich → kürzt sich unter der Per-Source-Normalisierung
weg. Wirksam ist GAAMAs **`degree_correction`** (Endscore ÷ `log(1+degree)`) — beide
wörtlich implementiert, der Effekt ehrlich dokumentiert.

## 5. Gate (§9)

- Interface-Erweiterung (neue Funktionen/Parameter) → Freigabe erteilt.
- §9.1d: Diff/Score/Drift in `ergebnisse/proposals-038-041.md` (Proposal 039). §9.1b: `AGENTS.md` unverändert → kein Snapshot.
- §10.1 jetzt verdrahtet (`route_extracted_facts`); persistentes Schreiben bleibt getrennt
  (§9.2c-Trust dort).

## 6. Nächstes Self-Feedback (t+1)

- Live-Lauf mit echtem LLM-Extraktor (externes Compare-Signal §6) — optional.
- §9.2c write-path validation an die persistente Write-Kette anbinden.
