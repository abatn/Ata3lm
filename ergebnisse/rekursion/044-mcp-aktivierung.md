# Rekursion 044: MCP-Aktivierung + Messung (12 Projekt-Server)

> Datum: 2026-10-03 · Tiefe: `t=43 → t=44` · Phase: **Observe → Compare**
> Freigabe: `approved: Batnini, 2026-10-03` (Auftrag „ok go").
> Ziel `g`: die 12 Projekt-MCPs **echt aktivieren**, Tools messen (statt nur 5).

## 1. Quellen

- MCP Python SDK (stdio_client) — echte Aktivierung.
- TTC Spec v1.0 (Zenodo 19869008) · Tool Attention (arXiv:2604.21816) · Strayspark · RAG-MCP.

## 2. Änderung (Diff)

| Datei | Änderung |
|---|---|
| `scripts/mcp_probe.py` | **neu**: startet Projekt-MCPs, `tools/list`, schreibt `ergebnisse/mcp-probe.json` |
| `ergebnisse/mcp-probe.json` | **neu**: reale Tool-Schemas (12 Server) |
| `ergebnisse/mcp-kontext.md` | aktualisiert (echte Zahlen) |
| `tests/test_mcp_catalog.py`, `data/memory/mcp_catalog.py` | aus Rekursion 043 |

## 3. Compare-Beleg (extern, echt)

```text
scripts/mcp_probe.py: 12/12 Server ok · 49 Tools real
TTC:        8.857 -> 8.770 Token (-1,0 %)
Top-5:      8.857 ->   638 Token (-92,8 %)
```

**Score** = 12/12 Server = 100 %. **Drift:** additiv (Skript + Doku).

## 4. Gate (§9)

- Interface-Änderung (Skript) → **approved** (Batnini). §9.1b: `AGENTS.md` unverändert.
- Ehrliche Grenzen: 49 Tools (nicht 122); TTC 1,0 % (Schemas knapp); ISO = Bag-of-Words.
