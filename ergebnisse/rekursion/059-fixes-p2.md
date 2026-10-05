# Rekursion 059: Korrekturen P2 (F3 · S2 · S3)

> Datum: 2026-10-05 · Tiefe: `t=58 → t=59` · Phase: **Revise**
> Freigabe: `approved` (Batnini). Interface-/Verhaltensänderung → §9 approved.
> Ziel `g`: E2E-Befunde F3 (deny speichert), S2 (keine Historisierung), S3 (Drift nach Write) beheben.

## 1. Quellen (verifiziert, §6)

- AGENTS.md §9.1 (Gate/deny), §9.2a (PII), §10.7 (Supersede), §9.1c (Drift).

## 2. Änderung (Diff)

| Datei | Änderung |
|---|---|
| `data/memory/lifecycle_runner.py` | PII-Filter (Stage 1); `Handeln` skip bei nicht-ok; `revised = ok` |
| `data/memory/pipeline.py` | Update archiviert alten Stand; Drift-Gate vor Write + echte Verteilung |
| `tests/test_lifecycle_runner.py` | +`test_denied_lifecycle_stoppt_writes` |
| `tests/test_pipeline.py` | +`test_write_update_archiviert_alten_stand`; 2 Tests angepasst |
| `ergebnisse/fixes-p2.md` | **neu** |

## 3. Compare-Beleg (extern, echt)

```text
F3: deny-Mandat -> Gedächtnis.ok=false, Handeln.skipped=true, Wissen+.revised=false, raw ohne E-Mail
S2: bestehender structured/…md -> archiviert (…superseded-5.md == "ALT"), neu geschrieben ("NEU")
S3: drift baseline {"a":1.0} -> gate=ask, KEIN Write; stabil -> gate=ok, Write
Volle Suite: 333 passed · 100 % (2680/634)
```

**Score** = 333/333 Tests = 100 %. **Drift:** additiv (2 Module + 3 Tests + 1 Doku).

## 4. Gate (§9)

- Verhaltensänderungen → **approved** (Batnini). §9.1b: `AGENTS.md` unverändert.
- Ehrliche Grenzen: S2 archiviert Structured-Stand (tier1-Supersede bleibt FWR-Pfad);
  Drift-Verteilung = ein Lauf. P3 (F4/F5/A9) offen.
