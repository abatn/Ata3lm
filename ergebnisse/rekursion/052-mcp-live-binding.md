# Rekursion 052: MCP-Live-Binding (Governance: Tool-Path Fingerprinting)

> Datum: 2026-10-04 · Tiefe: `t=51 → t=52` · Phase: **Konstrukt → Akt**
> Freigabe: Batnini (Auftrag). Interface-Änderung → §9 approved.
> Ziel `g`: externe MCPs **live** aufrufen (stdio) + Governance (Fingerprinting/Correlation).

## 1. Quellen (verifiziert, §6)

- Intent Leakage by Design (Chang 2026): Tool-Path Fingerprinting + Cross-Endpoint Correlation.
- MCP-Spec (stdio transport): `tools/call`.
- Integration: `mcp_catalog` (TTC), `scripts/mcp_probe.py` (stdio).

**Korrektur:** Auftrag nennt „Zenodo 2026"; verifizierte Quelle = Chang-2026-Arbeit.

## 2. Änderung (Diff)

| Datei | Änderung |
|---|---|
| `data/memory/mcp_live_binding.py` | **neu**: `call_tool_live`, `tool_path_fingerprint`, `cross_endpoint_correlation`, `catalog_server`, `load_servers` |
| `tests/test_mcp_live_binding.py` | **neu**: 9 Tests (inkl. Live-stdio-Aufruf) |
| `ergebnisse/mcp-live.md` | **neu** (Doku + echte Ausgabe) |
| `ergebnisse/reverse-engineering-vollstaendig.md` | Schicht 5 „extern/optional" → „+ Live-Binding" |

## 3. Compare-Beleg (extern, echt)

```text
call_tool_live("memory","memory.search",{"query":"SHACL"}) -> ok=true
  content: {"ok":true,"query":"SHACL","n_hits":0,"hits":[]}
  fingerprint: 56aaf9fa34f9b391
pytest test_mcp_live_binding.py: 9 passed · mcp_live_binding.py 100 % Line+Branch
```

**Score** = 9/9 Tests = 100 %. **Drift:** additiv (1 Modul, 1 Test, 2 Docs).

## 4. Gate (§9)

- Interface-Änderung → **approved** (Batnini). §9.1b: `AGENTS.md` unverändert.
- Ehrliche Grenzen: Test nutzt den eigenen Server (offline, reliabel); externe Server optional (§11).
