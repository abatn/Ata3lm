# MCP-Kontext-Steuerung (TTC · Lazy-Gating · Top-5/Stufe)

> Datum: 2026-10-03 · Status: **Belegt** (Quellen) + **Auftrag** (Top-5/Stufe).
> Lab-Prinzip §6: keine Erfindung. Guardrail 7: echte Aktivierung/Messung.
> **Alle Zahlen sind real gemessen** an den aktivierten Projekt-MCP-Servern.

## 1. Quellen (verifiziert)

| Quelle | Kern | Link |
|---|---|---|
| **TTC Spec v1.0** | kompakter Katalog (`WHEN/ERR/TAGS`), 66,6 % über 10 verbose Tools | https://doi.org/10.5281/zenodo.19869008 |
| **Tool Attention** | Dynamic Tool Gating + Lazy Schema Loading (−95 %) | https://arxiv.org/abs/2604.21816 |
| **Strayspark** | Token-Budget bindet vor Tool-Anzahl (22 Tools = 9.456 Token; char/4) | https://www.strayspark.studio/blog/how-many-tools-should-mcp-server-expose-token-budget |
| **RAG-MCP / vixra** | Selection Collapse (~13,62 %); 150k+ Token | arXiv:2505.10570 / ai.vixra.org |

## 2. Ist-Stand (real aktiviert, `scripts/mcp_probe.py`)

**12 Projekt-MCPs** gestartet + `tools/list` (MCP-SDK, echt) → **49 Tools** (nicht 122):

| Server | Tools | | Server | Tools |
|---|---|---|---|---|
| graphiti | 13 | | mars | 3 |
| hela-mem | 6 | | adas | 3 |
| trace | 6 | | governance-mcp | 3 |
| memory | 5 | | godel-agent | 2 |
| cognee | 5 | | reflexion / react / agent-dice | 1 |

**Nicht Projekt** (nicht aktiviert): context7, sqlalchemy-mcp, visuals-mcp (aus) · n8n-mcp, obsidian, kubernetes, livekit-docs.

## 3. Umsetzung (`data/memory/mcp_catalog.py`)

| Funktion | Zweck | Quelle |
|---|---|---|
| `mcp_schema_to_ttc(tool)` | MCP-JSON-Schema → **TTC-Block** (`PURPOSE/IN/OUT/ERR/WHEN/TAGS`) | TTC Spec v1.0 |
| `build_catalog` / `measure` | TTC-Katalog + Token vor/nach (char/4) | TTC / Strayspark |
| `iso_score` / `lazy_gate` | Intent-Overlap + **nur Top-k** laden | Tool Attention |
| `top_k_per_stage` | **Top-5 je Stufe** (8×5=40) | Auftrag |

## 4. Token-Messung (real, 49 Tools)

```text
TTC-Kompression:        8.857 → 8.770 Token  (−1,0 %)
Top-5-Gating (1 Stufe): 8.857 →   638 Token  (−92,8 %)
```
- **Ehrlich:** TTC bringt hier nur **1,0 %** — unsere MCP-Schemas sind bereits knapp
  (Paper: 66,6 % bei **verbosen** JSON-Schemas; TTC-`WHEN` dupliziert sonst `PURPOSE`).
- **Der große Hebel ist Lazy-Gating:** pro Stufe nur **5** statt **49** Tools → **−92,8 %**
  (deckt sich mit Tool Attention −95 % / Strayspark Front-Door).

## 5. Test

`tests/test_mcp_catalog.py` (7): TTC-Konverter, Token-Reduktion, `iso_score`, `lazy_gate`,
`top_k_per_stage`, echte 5 Tools. `mcp_catalog.py` **100 % Coverage**.

## 6. Gate (§9)

- Interface-Änderung (neues Modul/Skript) → **approved** (Batnini, „go").
- **Guardrail 3:** Provenienz `ergebnisse/rekursion/044-mcp-aktivierung.md`.
- **§9.1b:** `AGENTS.md` unverändert → kein Snapshot.
- **§11:** MCPs optional über lokaler Memory (Pflicht-Basis); Ausfall → lokaler Fallback.
- **Guardrail 7:** echte Aktivierung + `tools/list`, keine Simulation.

## 7. Ehrliche Grenzen
- **49 Tools** real (nicht 122; die 122 umfassten auch Nicht-Projekt-Server).
- TTC-Reduktion schema-abhängig (hier 1,0 %).
- `top_k_per_stage` = **Auftrag** (Stufen→Query-Mapping), kein Paper-Claim.
- ISO = Bag-of-Words-Proxy (Paper nutzt Sentence-Embeddings).
