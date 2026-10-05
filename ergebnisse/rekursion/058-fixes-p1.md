# Rekursion 058: Korrekturen P1 (F2 · F1 · S1)

> Datum: 2026-10-05 · Tiefe: `t=57 → t=58` · Phase: **Revise**
> Freigabe: `approved` (Batnini). Interface-/Verhaltensänderung → §9 approved.
> Ziel `g`: E2E-Befunde F2 (PII), F1 (green≠blue), S1 (Router-Gate) beheben.

## 1. Quellen (verifiziert, §6)

- AGENTS.md §9.2a (Privacy/PII), §9.2c (verified-only), §9.3 (Zwei-Personen), §10.4 (Gate), §10.7 (Supersede).
- E2E-Audit + Verifikation (9/9 bestätigt).

## 2. Änderung (Diff)

| Datei | Änderung |
|---|---|
| `data/memory/mcp_memory_server.py` | PII-Minimierung vor Store; Trust-DB (`_load_trust_db`/`_save_trust_db`); `green`≠`blue`; `tier1` nur `blue` |
| `data/memory/pipeline.py` | Router-`gate`/`uncertain` beachtet → kein Write vor Freigabe |
| `tests/test_mcp_memory.py` | +4 Tests (F2/F1) |
| `tests/test_pipeline.py` | +2 Tests (S1) |
| `ergebnisse/fixes-p1.md` | **neu** (Doku) |

## 3. Compare-Beleg (extern, echt)

```text
F2: memory.write(..., "…audit-person@example.test…") -> Datei ohne E-Mail (minimize)
F1: blue "Bestätigt" -> green "Vorschlag" = rejected; Datei bleibt "Bestätigt"; tier1 green = rejected
S1: router gate=ask / uncertain -> ok=false gate=ask, kein Write (structured_dir fehlt)
Volle Suite: 330 passed · 100 % (2672/628)
```

**Score** = 330/330 Tests = 100 %. **Drift:** additiv (2 Module + 6 Tests + 1 Doku).

## 4. Gate (§9)

- Verhaltensänderungen → **approved** (Batnini). §9.1b: `AGENTS.md` unverändert.
- Ehrliche Grenzen: `tier1`-nur-`blue` = Auftrags-Umsetzung §9.2c; **fail-closed** ohne
  Trust-Metadaten (nie fail-open). P2/P3 (F3/S2/S3/F4/F5/A9) offen.
