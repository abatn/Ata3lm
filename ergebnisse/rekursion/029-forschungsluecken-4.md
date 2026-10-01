# 029 – Vier Forschungslücken konsolidiert (L4 · Shared · Drift · GLiNER)

> Datum: 2026-10-01
> Rekursionstiefe: System-Iteration (Konsolidierung), nicht Solver-t
> Phase: Revise (GLiNER-Backend ehrlich; 1–3 nachgewiesen)
> Auslöser: menschlicher Auftrag vom 2026-10-01.

## 1. Zustand vorher / nachher

| # | vorher | nachher |
|---|---|---|
| 1 L4 | implementiert (015/020/025) | nachgewiesen (Test) |
| 2 Shared | implementiert (018/021/026) | nachgewiesen (Test) |
| 3 Drift | implementiert (027) | nachgewiesen (Test) |
| 4 GLiNER | regelbasiert | **pluggable Backend** (`auto`/`gliner`/`rules`); Regeln = Auftrag |

## 2. Änderungen

- `data/memory/ingestion_hook.py`: `gliner_available()`, `_get_gliner()`,
  `resolve_entities(..., backend=)` — echtes GLiNER falls installiert, sonst Regeln (Auftrag).
- `ergebnisse/forschungsluecken-4.md` (konsolidierte Doku).

## 3. Compare-Beleg (externes Signal)

- L4: `propose_update` pending ohne `approved`; mit → v9; Rollback → v1 (gesichert v10).
- Shared: v1 `superseded_by v2`; v3 `superseded_by v2` (kein Löschen).
- Drift: DI(JSD) 0.0006 → 0.0243; ab Schritt 6 (>τ) Flag.
- GLiNER: `gliner_available=False` → backend=`rules`; `backend="gliner"` → `[]`.

## 4. Quellen (belegt, HTTP 200)

- Memory Survey 2603.07670 · TEA 2506.12508 · Mem^p 2508.06433 (L4)
- LatticeMind 2608.08236 · Governed Collaborative Memory 2605.04264 (Shared)
- WhyLab Causal Audit Framework (github.com/neogenesislab/WhyLab-NeurIPS2026) · Agent Drift 2601.04170 (Drift)
- GraphRAG-SDK (github.com/FalkorDB/GraphRAG-SDK) · GLiNER-Relex 2605.10108 (GLiNER)

## 5. Guardrails

- `AGENTS.md` unverändert (in diesem Schritt); fail-soft (resolve_entities fällt auf Regeln zurück);
  Provenienz: `ergebnisse/forschungsluecken-4.md`.

## 6. Freigabe

**Freigabe-Status für π₁:** `pending` (menschliche Freigabe ausstehend).
