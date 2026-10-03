# Rekursion 038: GAAMA-Ladepfad korrigiert (Erfindung entfernt)

> Datum: 2026-10-03 · Tiefe: `t=37 → t=38` · Phase: **Revise → Handeln**
> Freigabe: `approved: Batnini, 2026-10-03` („Umsetzung beginnen — inkl. Freigabe, die
> erfundene `build_concept_graph` zu ersetzen").
> Ziel `g`: Ladepfad tier2→tier3 **paper-konform** machen; erfundene Kanten entfernen.

## 1. Quellen

- GAAMA arXiv:2603.27910 (Table 1/2, §3.1–3.4) + Repo `swarna-kpaul/gaama`
  (`graph_edges.py`, `llm_extractors.py`, `prompts/*`, `pagerank.py`, `ltm_retriever.py`).
- Kairos „Validation-Gated Hebbian Learning" (NeurIPS 2025, `ceur-ws.org/Vol-4162/paper4.pdf`).
- Beleg-Doku: `ergebnisse/gaama-schema.md`.

## 2. Änderung (Diff)

| Datei | Änderung |
|---|---|
| `data/memory/gaama_extract.py` | **neu**: Extraktion (Facts/Concepts/Reflections) + Kantenbau (5 Typen), LLM injizierbar |
| `data/memory/tier3-working/lru_cache.py` | **`build_concept_graph` (Erfindung) entfernt**; `hybrid_scores(query, items, edges)`; `fill_from_graph`; PPR überspringt unbekannte Endpunkte |
| `tests/test_gaama_extract.py` | **neu**: 8 Tests (Schema, Kanten, Fallback, Graph) |
| `tests/test_tier2_tier3.py` | angepasst auf erfindungsfreies API (10 Tests) |
| `ergebnisse/tier2-tier3.md`, `connectors/gaama.md`, `data/memory/README.md`, `tests/README.md`, `ergebnisse/verbindungen-diagramm.md` | nachgezogen |

`git diff --stat`: 16 Dateien, +448/−25 (Stand vor diesem Doc).

## 3. Compare-Beleg (extern)

```text
make test -> 253 passed · Coverage 100,00 % (Line+Branch) · ruff clean
```

**Score** = 253/253 erfüllte Tests = **100 %** → §9 „Automatisch (allow)" für Tests;
**aber** Interface-Änderung + Ersetzen → **Human-Gate** (erteilt).

**Drift:** additiv + Ersetzen einer 15-Zeilen-Funktion; kein Datenformat-Bruch →
unter Drift-Bound (10 %), dokumentiert. Offener Punkt: Extraktions-Writes → §10.1 FWR.

## 4. Gate (§9)

- Ersetzen `build_concept_graph` → **approved** (Batnini).
- §9.1d: Diff/Drift/Score in `ergebnisse/proposals-038-041.md` (Proposal 038). §9.1b: `AGENTS.md` **unverändert** → kein neuer Snapshot.
- §6: Kanten nur aus Extraktion (EdgeSpecs), keine Erfindung.

## 5. Nächstes Self-Feedback (t+1)

- §10.1-Verdrahtung: extrahierte Facts vor persistentem Write durch den **Fast Write Router**.
- Optional: Live-Lauf mit echtem LLM-Extraktor (externes Compare-Signal §6).
