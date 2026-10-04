# MCP-Kalibrierung (Ist vs. veröffentlichte Zahlen)

> Datum: 2026-10-03 · Status: **Belegt** (Quellen) + **Auftrag** (k=5).
> Guardrail 7: alle Ist-Werte real gemessen (`ergebnisse/mcp-probe.json`, 49 Tools).
> Ehrlichkeit: Abweichungen werden benannt, nicht geglättet.

## 1. Ist vs. Paper

| Metrik | Veröffentlicht | Unser Ist (real) | Abweichung | Grund |
|---|---|---|---|---|
| **TTC-Kompression** | 66,6 % (Zenodo 19869008) | **1,0 %** (8.857→8.770) | −65,6 pp | unsere MCP-Schemas sind bereits knapp; TTC-`WHEN` dupliziert `PURPOSE` |
| **Top-k-Gating** | −95 % (Tool Attention, arXiv:2604.21816) | **−95,8 %** (k=5) | **+0,8 pp** | deckt sich |
| **Token/Tool** | 429,8 (Strayspark, 22 Tools=9.456) | **180,8** (49 Tools=8.857) | **2,4× schlanker** | knappe Schemas |
| **Selection Collapse** | 13,62 % (RAG-MCP) | Top-5 mildert | — | Gating statt Voll-Liste |

## 2. Kalibrierung (echte Messung)

```text
Token/Tool:        180,8
Budget -> Tools:   5.000→27 · 3.000→16 · 2.000→11 · 1.000→5
k  Token  Reduktion
 1     67   99,2 %
 3    250   97,2 %
 5    371   95,8 %   <- Tool-Attention-Ziel (-95 %) erreicht
 8  1.843   79,2 %
20  5.699   35,7 %
49  8.857    0,0 %
```

**Ergebnis (Auftrag):** **k=5 je Stufe** trifft das veröffentlichte Ziel (−95 %)
und liegt unter 1.000 Token. `lazy_gate`-Schwelle bleibt default; Budget-Anker = 1.000 Token.

## 3. Quellen

- TTC Spec v1.0 — https://doi.org/10.5281/zenodo.19869008
- Tool Attention — https://arxiv.org/abs/2604.21816
- Strayspark (Token-Budget) — https://www.strayspark.studio/blog/how-many-tools-should-mcp-server-expose-token-budget
- RAG-MCP — arXiv:2505.10570

## 4. Gate (§9)

- Additiv (nur Doku + Rekursion) → **approved** (Batnini, „continue").
- **§9.1b:** `AGENTS.md` unverändert → kein Snapshot. **Guardrail 7:** echte Messung.
- Ehrliche Grenze: TTC-**Paper**-Wert nicht reproduziert (Schemas zu knapp) → als Abweichung geführt.
