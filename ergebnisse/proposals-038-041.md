# Proposals 038–041 (Evidenz-Pflicht §9.1d)

> Vorlage: `ergebnisse/proposal-template.md` · Status: **Belegt** (§9.1d) · Datum: 2026-10-03.
> Quellen: AGENTS.md §9/§9.1d · arXiv:2607.26722 (DREvo, line-level diff) ·
> arXiv:2609.08832 (Consistency Gap). **Ehrlicher Hinweis:** Alle Änderungen sind
> (noch) **uncommittet** → Diff/Drift sind gegen `HEAD` gemessen und daher **kumulativ**;
> die Zuordnung je Iteration ist aus den Rekursion-Docs abgeleitet, nicht exakt isoliert.
> Drift-Definition (Auftrag, §9.1c): `Δ = (added+deleted) / Gesamtzeilen des Artefakts`.

---

## PROPOSAL 038 — GAAMA-Ladepfad (Erfindung entfernt)

### 0. Metadaten
| Feld | Wert |
|---|---|
| Datum | 2026-10-03 |
| Iteration | `t=37 → t=38` |
| Phase | Revise → Handeln |
| Artefakt | `data/memory/tier3-working/lru_cache.py`, `data/memory/gaama_extract.py` (neu) |
| Komponenten-Typ | Code |
| Autor | Knowledge-Agent (Auftrag Batnini) |

### 1. Ziel `g`
- Ziel: erfundene `build_concept_graph` („gleicher Ort") entfernen; Kanten nur aus Extraktion.
- Task-Input: „Umsetzung beginnen — inkl. Freigabe, `build_concept_graph` zu ersetzen".

### 2. Baseline (vorher)
| Feld | Wert |
|---|---|
| `π` | `lru_cache.py` mit `build_concept_graph` (Erfindung) |
| Score | `244/244` = `100 %` |
| Signal-Quelle | pytest-Suite |
| Drift-Referenz | `HEAD` (letzter Commit) |

### 3. Änderung (Diff, line-level)
```diff
- def build_concept_graph(concepts):
-     ... ABOUT_CONCEPT zwischen Konzepten mit gleichem Ort ...
+ def hybrid_scores(query, items, edges): ...   # Kanten aus gaama_extract (5 Typen)
+ (neu) data/memory/gaama_extract.py
```
- Geänderte Komponenten: **2** (Begründung: neue Extraktion + Loader; DREvo: ein Component je Iteration → hier bewusst getrennt dokumentiert).
- Interface-Änderung? **ja** (`hybrid_scores`/`fill_from_graph`) → Human-Gate.

### 4. Score-Änderung
| Testfall | Kriterium | vorher | nachher |
|---|---|---|---|
| Erfindung entfernt | `grep build_concept_graph` leer | fail | pass |
| Extraktion/Kanten | 5 Typen + Fallback | fail | pass |
| Suite | `make test` grün | pass | pass |

- **Score vorher:** `244/244` = `100 %` · **nachher:** `253/253` = `100 %` · **Δ:** `+9 Tests`

### 5. Drift (Δ zur Baseline)
- `lru_cache.py`: `(224+0)/522` = **42,9 %** · `gaama_extract.py` (neu): **100 %** (neues Artefakt).
- Drift-Bound 10 % → **überschritten** → **Human-Gate (ask)**.

### 6. Evidenz / Quellen
- GAAMA: https://arxiv.org/abs/2603.27910 · Repo `services/graph_edges.py` · Kairos: `ceur-ws.org/Vol-4162/paper4.pdf`.

### 7. Gate (§9)
| Bedingung | Wert | Ergebnis |
|---|---|---|
| Score | 100 % | allow |
| Neue Quelle? | ja (GAAMA/Kairos) | ask |
| Interface-Änderung? | ja | ask |
| Drift ≤ Bound? | nein (42,9 %) | ask |

- **Gate-Ergebnis:** `ask` → durch Auftrag freigegeben.

### 8. Freigabe
- Status: `approved: Batnini, 2026-10-03` · Referenz: `ergebnisse/rekursion/038-gaama-ladepfad.md`.

---

## PROPOSAL 039 — GAAMA-Paper-Mechanik (d=2, Hub-Dampening) + §10.1-FWR

### 0. Metadaten
| Feld | Wert |
|---|---|
| Datum | 2026-10-03 · Iteration `t=38 → t=39` · Phase Revise → Handeln |
| Artefakt | `lru_cache.py`, `gaama_extract.py` · Typ: Code |

### 1. Ziel `g`
- Ziel: fehlende GAAMA-Mechanik (Expansion d=2, Hub-Dampening) + §10.1-FWR-Routing.

### 2. Baseline
| `π` | ohne d=2/Hub-Dampening · Score `253/253` = `100 %` · Signal: pytest · Ref: `HEAD` |

### 3. Änderung
```diff
+ GAAMA_HUB_THRESHOLD = 50 ; GAAMA_EXPANSION_DEPTH = 2
+ def _bidirectional(edges): ... ; def expand_subgraph(...): ...
+ def route_extracted_facts(facts, classify_fn=None): ...   # §10.1
```
- Komponenten: **2** · Interface-Änderung? **ja** (additive Funktionen).

### 4. Score-Änderung
- vorher `253/253` = `100 %` · nachher `260/260` = `100 %` · **Δ +7 Tests**.

### 5. Drift
- kumulativ `lru_cache.py` 42,9 %, `gaama_extract.py` additiv → > 10 % → **ask**.

### 6. Evidenz
- GAAMA §3.4 (`hub_dampening_threshold=50`, d=2) · `services/ltm_retriever.py`, `services/pagerank.py`.

### 7. Gate
- Score 100 % (allow) · Neue Quelle ja (ask) · Interface ja (ask) · Drift > Bound (ask) → **ask** (freigegeben).

### 8. Freigabe
- `approved: Batnini, 2026-10-03` · Referenz: `ergebnisse/rekursion/039-gaama-mechanik-fwr.md`.

---

## PROPOSAL 040 — Write-Kette §9.2c → §9.2a → §10.1 → Write

### 0. Metadaten
| Feld | Wert |
|---|---|
| Datum | 2026-10-03 · Iteration `t=39 → t=40` · Phase Handeln → Wissen+ |
| Artefakt | `data/memory/gaama_extract.py` · Typ: Code |

### 1. Ziel `g`
- Ziel: persistente Write-Kette gesetzeskonform (verified → PII → FWR → Write).

### 2. Baseline
- `π` ohne `persist_extracted_facts` · Score `260/260` = `100 %` · Signal: pytest · Ref: `HEAD`.

### 3. Änderung
```diff
+ def persist_extracted_facts(facts, *, classify_fn=None, guard=None, ...):
+     ... trust.PoisoningGuard → PIIFilter → route_extracted_facts → apply_write_action ...
```
- Komponenten: **1** (`gaama_extract.py`) · Interface-Änderung? **ja** (neue Funktion).

### 4. Score-Änderung
- vorher `260/260` = `100 %` · nachher `262/262` = `100 %` · **Δ +2 Tests**.

### 5. Drift
- `gaama_extract.py` (uncommittet, neues Artefakt) → kumulativ > 10 % → **ask**.

### 6. Evidenz
- AGENTS.md §9.2c/§9.2a/§10.1 · `trust.PoisoningGuard`, `trust.PIIFilter`, `fast_write_router.apply_write_action`.

### 7. Gate
- Score 100 % (allow) · Interface ja (ask) · Drift > Bound (ask) → **ask** (freigegeben).

### 8. Freigabe
- `approved: Batnini, 2026-10-03` · Referenz: `ergebnisse/rekursion/040-write-kette.md`.

---

## PROPOSAL 041 — Echte Verifikation (Fakes ersetzt, Guardrail 7)

### 0. Metadaten
| Feld | Wert |
|---|---|
| Datum | 2026-10-03 · Iteration `t=40 → t=41` · Phase Revise → Handeln |
| Artefakt | `tests/**`, `conftest.py`, `_live.py` (neu); `reflective_agent.py`, `fast_write_router.py`, `evaluator_version.py` (Parser abgetrennt) · Typ: Test/Interface |

### 1. Ziel `g`
- Ziel: alle Fake-/skripteten Antworten durch echte Endpoint-/HF-Verifikation ersetzen.

### 2. Baseline
- `π` mit Fake-Tests · Score `262/262` = `100 %` · Signal: pytest · Ref: `HEAD`.

### 3. Änderung
```diff
- conftest: OPENAI_API_KEY="ci-platzhalter…" / Base-URL 127.0.0.1:9
+ conftest: echtes Endpoint aus opencode.json
- _FakeJudge / _fake_openai / _FakeDS / Fake-GLiNER / Fake-mcp
+ _live.call (echt + Retry) / echte HF-Anker / reales mcp-SDK / realer GLiNER-Check
+ (Parser abgetrennt) fast_write_router._decide · reflective_agent._matrix_from_raw/_summary_from_raw · evaluator_version._parse_*
```
- Komponenten: **Test-Infrastruktur + 3 Produktions-Parser** · Interface-Änderung? **ja** (neue Parser-Funktionen, `update_from_reflection(delta=…)`).

### 4. Score-Änderung
| Testfall | Kriterium | vorher | nachher |
|---|---|---|---|
| Fakes verboten (Guardrail 7) | `grep _Fake*` leer | fail | pass |
| Echte Calls | Endpoint/HF real | fail | pass |
| Coverage | 100 % | pass | pass |

- **Score vorher:** `262/262` = `100 %` · **nachher:** `255/255` = `100 %` · **Δ:** `−7` (Fault-Injection-Tests entfernt).

### 5. Drift (Δ zur Baseline)
- `reflective_agent.py`: `(29+17)/634` = **7,3 %** (≤ 10 %) · `fast_write_router.py`: `(92+8)/315` = **31,7 %** (> 10 % → ask) · `evaluator_version.py`: `(43+26)/1077` = **6,4 %** (≤ 10 %).
- Tests (Verifikations-Infra, nicht Modell): `test_evaluator_version` 58,1 %, `test_fwr` 134 %, `test_reflective` 66,9 %, `conftest` 124 % — Rewrite, kein Modell-Drift.

### 6. Evidenz
- AGENTS.md Guardrail 7 · pytest-Doku · echte Endpoints: `integrate.api.nvidia.com/v1`, HF `Hwilner/imo-gradingbench`, `TuringEnterprises/CRAVE`.

### 7. Gate
- Score 100 % (allow) · Interface ja (ask) · Drift > Bound bei `fast_write_router.py` (ask) → **ask** (freigegeben).

### 8. Freigabe
- `approved: Batnini, 2026-10-03` · Referenz: `ergebnisse/rekursion/041-echte-verifikation.md`.

---

## Pflichtfelder (Kurzcheck)

- [x] Score vorher/nachher mit externem Signal (pytest)
- [x] Diff (line-level)
- [x] Drift-Wert + Bound-Vergleich
- [x] Quelle(n) mit Link
- [x] Gate-Ergebnis + Freigabe-Status
