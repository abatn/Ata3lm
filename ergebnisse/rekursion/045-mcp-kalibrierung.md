# Rekursion 045: MCP-Kalibrierung (Ist vs. Paper)

> Datum: 2026-10-03 · Tiefe: `t=44 → t=45` · Phase: **Compare → Revise**
> Freigabe: `approved: Batnini, 2026-10-03` (Auftrag „continue").
> Ziel `g`: Ist-Werte gegen veröffentlichte Zahlen kalibrieren (keine Erfindung).

## 1. Quellen

- TTC Spec v1.0 (Zenodo 19869008) · Tool Attention (arXiv:2604.21816) ·
  Strayspark · RAG-MCP (arXiv:2505.10570).

## 2. Änderung (Diff)

| Datei | Änderung |
|---|---|
| `ergebnisse/mcp-kalibrierung.md` | **neu**: Ist-vs-Paper-Tabelle + k-Kalibrierung |

Kein Code geändert (nur Doku).

## 3. Compare-Beleg (extern, echt)

```text
TTC:    Paper 66,6 %  vs  Ist  1,0 %   (-65,6 pp, Schemas knapp)
Top-k:  Paper -95 %   vs  Ist -95,8 % (+0,8 pp)  -> k=5
Token/Tool: 429,8 (Strayspark) vs 180,8 (Ist, 2,4x schlanker)
k=5: 371 Token (95,8 %) unter 1.000-Token-Budget
```

**Score** = 4/4 Metriken verglichen (3 gedeckt, 1 Abweichung benannt) = 100 %.
**Drift:** additiv (1 Doku).

## 4. Gate (§9)

- Additiv → **approved** (Batnini). §9.1b: `AGENTS.md` unverändert.
- Ehrliche Grenze: TTC-Paper-Wert **nicht** reproduziert → als Abweichung dokumentiert.
