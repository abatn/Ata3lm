# Rekursion 051: Connector-Binding (SHACL/W3C)

> Datum: 2026-10-04 · Tiefe: `t=50 → t=51` · Phase: **Konstrukt → Akt**
> Freigabe: Batnini (Auftrag). Interface-Änderung → §9 approved.
> Ziel `g`: Schicht-4-Lücke schließen — 17 Connectoren an den **Code** binden.

## 1. Quellen (verifiziert, §6)

- W3C SHACL (Rec. 2017): https://www.w3.org/TR/shacl/
- AGENTS.md §5; Zuordnung: `ergebnisse/connector-prozess.md`.

## 2. Änderung (Diff)

| Datei | Änderung |
|---|---|
| `data/memory/connector_binding.py` | **neu**: `parse_connector`, `validate_connector` (pyshacl), `bind`, `bind_all`, 9 Prozess-Executoren |
| `tests/test_connector_binding.py` | **neu**: 7 Tests (inkl. `bind_all` = 17 Connectoren) |
| `ergebnisse/connector-binding.md` | **neu** (Doku + echte Ausgabe) |
| `ergebnisse/reverse-engineering-vollstaendig.md` | Schicht 4 „nur Doku" → „+ Binding" |

## 3. Compare-Beleg (extern, echt)

```text
bind(htac-agentdice): process=pipeline.py, shacl conforms=true,
  executed=true (write-new: mandate=ALLOW · trust=PII entfernt), recorded via MCP
pytest test_connector_binding.py: 7 passed · connector_binding.py 100 % Line+Branch
```

**Score** = 7/7 Tests = 100 %. **Drift:** additiv (1 Modul, 1 Test, 2 Docs).

## 4. Gate (§9)

- Interface-Änderung → **approved** (Batnini). §9.1b: `AGENTS.md` unverändert.
- Ehrliche Grenzen: Zuordnung = Auftrag; SHACL prüft nur die Invariante (minCount 1).
