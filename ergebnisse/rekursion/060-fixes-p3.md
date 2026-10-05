# Rekursion 060: Korrekturen P3 (F4 · F5 · A9)

> Datum: 2026-10-05 · Tiefe: `t=59 → t=60` · Phase: **Revise**
> Freigabe: `approved` (Batnini). Interface-/Verhaltensänderung → §9 approved.
> Ziel `g`: E2E-Befunde F4 (bi-temporal as_of), F5 (Transport-≠Fach-ok), A9 (lazy Client) beheben.

## 1. Quellen (verifiziert, §6)

- AGENTS.md §10.7 (Bi-Temporal/Engram „keep the history"), §6 (eindeutiger Vertrag), Guardrail 7.

## 2. Änderung (Diff)

| Datei | Änderung |
|---|---|
| `data/memory/bi_temporal.py` | `Fact.valid_to_known_at`; transaktions-bewusstes `as_of` |
| `data/memory/mcp_live_binding.py` | `_inner_ok`; `ok = transport_ok and inner_ok` + `transport_ok` |
| `data/memory/fast_write_router.py` | lazy `_get_client()` statt Import-Client |
| `tests/test_bi_temporal.py` | +F4-Test; 1 Erwartung korrigiert |
| `tests/test_mcp_live_binding.py` | +F5-Test, +`_inner_ok`-Test |
| `tests/test_fwr.py` | +A9-Test |
| `ergebnisse/fixes-p3.md` | **neu** |

## 3. Compare-Beleg (extern, echt)

```text
F4: as_of("2024-03-10","2024-03-10") -> ["Globex"] (vorher []); as_of(2024-02-01, 2024-04-01) -> ["Globex"]
F5: memory.write trust=red -> call_tool_live.ok=false, transport_ok=true
A9: import fast_write_router ohne OPENAI_API_KEY -> kein Crash (mod._client is None)
Volle Suite: 337 passed · 100 % (2707/648)
```

**Score** = 337/337 Tests = 100 %. **Drift:** additiv (3 Module + 4 Tests + 1 Doku).

## 4. Gate (§9)

- Verhaltensänderungen → **approved** (Batnini). §9.1b: `AGENTS.md` unverändert.
- Ehrliche Grenzen: F4-Erwartung korrigiert (alte Zeile kodierte den Fehler); ontology.md nicht aktualisiert.
