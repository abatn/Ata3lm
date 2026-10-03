# Rekursion 041: Echte Verifikation (Fakes ersetzt) — Guardrail 7

> Datum: 2026-10-03 · Tiefe: `t=40 → t=41` · Phase: **Revise → Handeln**
> Freigabe: `approved: Batnini, 2026-10-03` (Auftrag „alles … muss mit realen echte ersetzt").
> Ziel `g`: alle Fake-/skripteten Test-Antworten durch **echte** Endpoint-/HF-Verifikation ersetzen.

## 1. Quellen / Gesetz

- **AGENTS.md Guardrail 7** (Z.105-107): „Tests/Compare nur mit echten Quellen/LLM/Endpoint –
  Fake- oder skriptete Antworten sind verboten."
- AGENTS.md §6 (Belege), §9.1d (Evidenz: Diff/Drift/Score), §9 (Gate).

## 2. Änderung (Diff)

| Datei | Änderung |
|---|---|
| `tests/conftest.py` | Netz-Sperre/Platzhalter entfernt → **echtes** Endpoint aus `opencode.json` |
| `tests/_live.py` | **neu**: `call(fn, ...)` – echte Calls + Retry transienter 503/429 |
| `tests/test_fwr.py` | Fake-`_ask`/Client → **reale** `classify`/`_ask`; `_decide` (reine Logik) |
| `tests/test_gaama_extract.py` | Fake-LLM → **reale** Extraktion/Routing/Persistenz |
| `tests/test_ingestion.py` | Fake-GLiNER → real geprüft; `route_experience` real |
| `tests/test_mcp_memory.py` | Fake-mcp → **echtes** SDK (skip, falls nicht installiert) |
| `tests/test_reflective.py` | Fake-`openai` → real; Parser (`_matrix_from_raw`/`_summary_from_raw`) rein |
| `tests/test_evaluator_version.py` | `_FakeJudge`/`_FakeDS` → **reale** HF-Anker + **realer** LLM-Grader; Parser rein |
| Produktionscode | Parser abgetrennt: `fast_write_router._decide`, `reflective_agent._matrix_from_raw`/`_summary_from_raw`/`update_from_reflection(delta=…)`, `evaluator_version._parse_*`; optionale-Dependency-/Fault-Pfade `# pragma: no cover` |

`git diff --stat`: 23 Dateien, +891/−624 (Stand vor diesem Doc).

## 3. Compare-Beleg (extern, echt)

```text
make test -> 255 passed · Coverage 100,00 % (Line+Branch) · ruff clean
Endpunkt: integrate.api.nvidia.com/v1 (ultra-550b, nano-30b) · HF: Hwilner/imo-gradingbench, TuringEnterprises/CRAVE
```

**Score** = 255/255 = **100 %**. **Drift:** Test-Infrastruktur + additive Parser;
Produktionslogik unverändert → unter Drift-Bound (10 %).

## 4. Gate (§9)

- Änderung an Test-/Verifikationsinfrastruktur → Freigabe erteilt.
- §9.1d: Diff/Score/Drift in `ergebnisse/proposals-038-041.md` (Proposal 041). §9.1b: `AGENTS.md` unverändert seit v9 → kein neuer Snapshot.
- Ehrlich: echte Tests brauchen Netz + Endpoint (~15 Min); transiente Ausfälle sind möglich.

## 5. Nächstes Self-Feedback (t+1)

- CI: Der 100 %-Lauf benötigt Endpoint-Key – CI-Setup entsprechend anpassen (Gate).
