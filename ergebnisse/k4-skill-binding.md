# K4 — Skills maschinell an Executoren binden

> Datum: 2026-10-06 · Bezug: `AGENTS.md` §3, `skills/README.md` (L4),
> `ergebnisse/kopplung-komponenten-bericht.md` §K4.
> Test-Lauf (Auftrag): `.venv/bin/python -m pytest tests/test_skill_binding.py tests/test_skill_interpreter.py tests/test_skills.py -q --no-cov`.

## 1. Ziel + Quellen (verifiziert, §6)

Ziel: **14/14 Skills** an einen **echten Executor** gebunden oder ehrlich
`doc-only` (nachgewiesen, nicht behauptet).

| Quelle | Link | HTTP | Rolle |
|---|---|---|---|
| Voyager | <https://arxiv.org/abs/2305.16291> | 200 | Skill-Bibliothek = „executable code" |
| JSON-Schema-Spec | <https://json-schema.org/specification> | 200 | Struktur-Validierung (`process:`) |

**Caveat (Review, §6):** JSON Schema prüft **nur die Struktur**. Die echte
Ausführung (Eingabe→Berechtigung→Ergebnis) ist separat getestet
(`tests/test_skill_binding.py`). `doc-only` = ehrliche Kennzeichnung, keine Fake-Fähigkeit.

## 2. Änderungen (Dateien)

| Datei | Änderung |
|---|---|
| `data/memory/skill_interpreter.py` | `parse_skill` liefert `process`; real Executoren `_run_ingestion_hook`, `_run_fast_write_router`, `_run_trust`, `_run_bias_monitor`, `_run_shared_memory`, `_run_reflective_agent`, `_run_evaluator`; `DEFAULT_REGISTRY` 2→9 Keys; `PROCESS_SCHEMA` (JSON Schema Draft 2020-12); `validate_process`, `bind_skill`, `bind_all_skills` |
| `skills/<14>/SKILL.md` | Frontmatter `process: <executor>` (`doc-only` möglich) |
| `tests/test_skill_binding.py` | **neu**: 23 Tests (14/14 parametrisiert + Schema/Guards/doc-only/unbound) |
| `skills/README.md` | Abschnitt „Maschinenlesbares `process:`-Feld (K4)" + §9-Interface-Hinweis |
| `skills/AUDIT.md` | Audit-Zeile (proposal; §9 `approved` erforderlich) |

## 3. 14/14-Matrix (lauffähig, Test)

| # | Skill | `process:` | Status | Test |
|---|---|---|---|---|
| 1 | collect-experience | `ingestion_hook.py` | lauffähig | `test_skill_lauffaehig[collect-experience]` |
| 2 | structure-knowledge | `fast_write_router.py` | lauffähig | `test_skill_lauffaehig[structure-knowledge]` |
| 3 | store-memory | `pipeline.py` | lauffähig | `test_skill_lauffaehig[store-memory]` |
| 4 | cognize | `reflective_agent.py` | lauffähig | `test_skill_lauffaehig[cognize]` |
| 5 | reflect | `bias_monitor.py` | lauffähig | `test_skill_lauffaehig[reflect]` |
| 6 | non-cognitive | `trust.py` | lauffähig | `test_skill_lauffaehig[non-cognitive]` |
| 7 | act | `pipeline.py` | lauffähig | `test_skill_lauffaehig[act]` |
| 8 | expand-knowledge | `shared_memory.py` | lauffähig | `test_skill_lauffaehig[expand-knowledge]` |
| 9 | recursive-improve | `pipeline.py` | lauffähig | `test_skill_lauffaehig[recursive-improve]` |
| 10 | recursive-improve/observe | `ingestion_hook.py` | lauffähig | `test_skill_lauffaehig[observe]` |
| 11 | recursive-improve/compare | `evaluator_version.py` | lauffähig | `test_skill_lauffaehig[compare]` |
| 12 | recursive-improve/revise | `reflective_agent.py` | lauffähig | `test_skill_lauffaehig[revise]` |
| 13 | recursive-improve/konstrukt | `reflective_agent.py` | lauffähig | `test_skill_lauffaehig[konstrukt]` |
| 14 | recursive-improve/akt | `pipeline.py` | lauffähig | `test_skill_lauffaehig[akt]` |

**Ergebnis: 14/14 lauffähig, 0 `doc-only`.** Der `doc-only`-Pfad ist dennoch
implementiert und getestet (`test_bind_doc_only`), ebenso `unbound`
(`test_bind_unbound_ohne_registry`) und fehlendes Feld (`test_bind_ohne_process_feld`).

## 4. Compare-Beleg (echte Zahlen)

```text
tests/test_skill_binding.py                                    23 passed
tests/test_skill_binding.py + test_skill_interpreter.py +
  test_skills.py                                              46 passed
Coverage (nur skill_interpreter.py, line+branch):
  data/memory/skill_interpreter.py  182 stmts  0 miss  40 branch  0 partial  100%
```

Berechtigung/Wirkung belegt (`test_executor_berechtigung_wirkt`):
`trust` → `verified=False` ⇒ `admission.admitted is False` (§9.2c);
`ingestion_hook` → Fakt zu kurz ⇒ `accepted is False` (Encoding-Gate);
`fast_write_router` → `refusal=True` ⇒ Klasse `write-new` (§10.7).

## 5. §9 / Guardrails

- **Guardrail 4 / §9:** `process:` ist ein **neues Interface** (Skill-Manifest-Schema).
  Einführung + Erweiterung der erlaubten Werte ⇒ **Human-Gate (`approved`) nötig** —
  dokumentiert in `skills/README.md` + `skills/AUDIT.md` (nicht heimlich).
- **Guardrail 6 (Git):** kein `git add/commit/push`.
- **Guardrail 7 / §6:** Alle Executoren laufen real (kein Fake); Quellen HTTP 200 geprüft.
- **§9.1b:** `AGENTS.md`/`tier1-base` unverändert ⇒ kein `versions/vN`.

## 6. Offene Punkte

- Voller Repo-Lauf (`make test`, 100 % über alle Module) wurde gemäß Auftrag
  **nicht** ausgeführt (Netz/Endpoint, ~15 min); gezielter Lauf + Modul-Coverage 100 %.
- Änderungen an den 14 `SKILL.md` sind auditiert; §9-`approved` erteilt
  (Batnini, 2026-10-06).
