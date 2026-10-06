# Rekursion 067: K4 — Skills maschinell an Executoren binden

> Datum: 2026-10-06 · Tiefe: `t=66 → t=67` · Phasen: Observe → Compare → Revise.
> Freigabe: **`approved`** (Batnini, 2026-10-06) — das `process:`-Frontmatter-Feld ist ein
> **neues Interface** (§9/Guardrail 4); Freigabe erteilt.
> Ziel `g`: 14/14 Skills lauffähig ODER ehrlich `doc-only` (nachgewiesen).

## 1. Quellen (verifiziert, §6)

- Voyager (arXiv:2305.16291) — „ever-growing skill library of **executable code**":
  <https://arxiv.org/abs/2305.16291> (HTTP 200, 2026-10-06).
- JSON-Schema-Spec (Draft 2020-12): <https://json-schema.org/specification>
  (HTTP 200, 2026-10-06) — **Struktur**validierung.
- Vorlage: `ergebnisse/kopplung-komponenten-bericht.md` §K4; `skills/README.md` (L4).

## 2. Observe (`self_inspect` + `interact`)

- `skill_interpreter.DEFAULT_REGISTRY` = nur `{pipeline.py, memory.write}` (2 Executoren).
- 14 aktive `SKILL.md` deklarieren Prozesse nur in Prosa; kein maschinenlesbares
  Skill→Executor-Feld.

## 3. Compare (externes Signal, Pflicht)

- Referenz: `tests/test_skill_binding.py` (14/14 parametrisiert) + `pytest` real.
- Score vorher / nachher: 2/14 bindbar → **14/14 lauffähig**.
- Beleg (echter Test-Output):
  ```text
  tests/test_skill_binding.py + test_skill_interpreter.py + test_skills.py
  -> 46 passed
  Coverage data/memory/skill_interpreter.py -> 100 % (182 stmts · 40 branches)
  ```

## 4. Revise (Diff von `(π, I)`)

| Datei | Änderung |
|---|---|
| `data/memory/skill_interpreter.py` | `process`-Parsing; 7 reale Executoren; `DEFAULT_REGISTRY` 2→9; `PROCESS_SCHEMA` + `validate_process` + `bind_skill` + `bind_all_skills` |
| `skills/*/SKILL.md` (14) | Frontmatter `process:` |
| `tests/test_skill_binding.py` | neu (23 Tests) |
| `skills/README.md`, `skills/AUDIT.md` | Doku + Audit (§9-Hinweis) |
| `ergebnisse/k4-skill-binding.md` | Bericht |

## 5. Gate (§9) + Provenienz

- **Interface-Änderung** (Skill-Manifest-Schema) ⇒ **Human-Gate** — dokumentiert, nicht
  heimlich. Status: **`approved`** (Batnini, 2026-10-06).
- Guardrail 6 (kein Git) eingehalten; Guardrail 7 (echte Tests, kein Fake) eingehalten.
- §9.1b: `AGENTS.md`/`tier1-base` unverändert ⇒ kein `versions/vN`.

## 6. Self-Feedback für `t+1`

- `process:`-Werte sind als JSON-Schema-Enum an `DEFAULT_REGISTRY` gekoppelt;
  neue Executoren erweitern Registry **und** Schema in einem Schritt.
- Nicht-integrierbare Skills künftig explizit `process: doc-only` (Pfad getestet).
