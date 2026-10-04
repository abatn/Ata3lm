# Rekursion 043: MCP-Kontext-Steuerung (TTC · Lazy-Gating · Top-5/Stufe)

> Datum: 2026-10-03 · Tiefe: `t=42 → t=43` · Phase: **Revise → Handeln**
> Freigabe: `approved: Batnini, 2026-10-03` (Auftrag „setze das plan nach der AGENTS.md").
> Ziel `g`: MCP-Kontext reduzieren nach Forschungsstandard (TTC, Tool Attention, Strayspark).

## 1. Quellen (verifiziert)

- TTC Spec v1.0 — Zenodo `10.5281/zenodo.19869008` (66,6 %, `WHEN/ERR/TAGS`).
- Tool Attention — arXiv:2604.21816 (Dynamic Gating + Lazy Schema Loading).
- Strayspark — Token-Budget (22 Tools = 9.456 Token; char/4).
- RAG-MCP / vixra — Selection Collapse (~13,62 %).

## 2. Änderung (Diff)

| Datei | Änderung |
|---|---|
| `data/memory/mcp_catalog.py` | **neu**: `mcp_schema_to_ttc`, `build_catalog`, `measure`, `iso_score`, `lazy_gate`, `top_k_per_stage` |
| `tests/test_mcp_catalog.py` | **neu**: 7 Tests (TTC, Token-Reduktion, Gating) |
| `ergebnisse/mcp-kontext.md` | **neu**: Quellen, Messung, Test |

## 3. Compare-Beleg (extern/echt)

```text
5 echte MCP-Tools: Token vor 371 -> nach 244 (Reduktion 34,2 %)
test_mcp_catalog.py: 7 passed; mcp_catalog.py 100 % Coverage
```

**Score** = 7/7 = 100 %. **Drift:** additiv (neues Modul + Test); kein Interface-Bruch.

## 4. Gate (§9)

- Interface-Änderung → **approved** (Batnini). §9.1b: `AGENTS.md` unverändert → kein Snapshot.
- Ehrliche Grenzen: 122 externe Tools nicht offline messbar; `top_k_per_stage` = Auftrag;
  ISO = Bag-of-Words-Proxy.
