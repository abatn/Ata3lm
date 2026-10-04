# Rekursion 049: Skill-Interpreter (Procedural Memory First-Class)

> Datum: 2026-10-04 · Tiefe: `t=48 → t=49` · Phase: **Konstrukt → Akt**
> Freigabe: Batnini (Auftrag). Interface-Änderung → §9 approved.
> Ziel `g`: Schicht-6-Lücke („Skills verwaltet, nicht ausgeführt") mit echtem Interpreter schließen.

## 1. Quellen (verifiziert, §6)

- Memory Survey (arXiv:2603.07670): „memory as a first-class system component"; „temporal versioning".
- Mem^p (arXiv:2508.06433, ACL 2026 Findings): lifelong procedural memory; Build/Retrieval/Update; deprecate.
- AFTER (arXiv:2606.23127): Skill-Files als „first-class artifact".

**Korrektur:** „Procedural Memory First-Class" ← Mem^p (+ Memory Survey); nicht allein die Memory Survey.

## 2. Änderung (Diff)

| Datei | Änderung |
|---|---|
| `data/memory/skill_interpreter.py` | **neu**: `parse_skill`, `run_skill`, `list_skills`, `DEFAULT_REGISTRY` |
| `tests/test_skill_interpreter.py` | **neu**: 5 Tests (echter Skill-Lauf) |
| `ergebnisse/skill-interpreter.md` | **neu** (Doku + echte Ausgabe) |
| `ergebnisse/reverse-engineering-vollstaendig.md` | Schicht 6 „verwaltet" → „+ Interpreter" |

## 3. Compare-Beleg (extern, echt)

```text
run_skill(skills/act/SKILL.md): skill=act, steps=6
pipeline.py executed=true -> ok=true action=write-new
  mandate=ALLOW · fwr=write-new · trust=PII entfernt · write=write-new
pytest test_skill_interpreter.py: 5 passed · skill_interpreter.py 100 % Line+Branch
```

**Score** = 5/5 Tests = 100 %. **Drift:** additiv (1 Modul, 1 Test, 2 Docs).

## 4. Gate (§9)

- Interface-Änderung → **approved** (Batnini). §9.1b: `AGENTS.md` unverändert.
- Ehrliche Grenzen: Skills = Doku; Interpreter führt nur **deklarierte Prozesse** aus
  (keine NL-Interpretation der `## Ablauf`-Schritte); MCP-Tools lokal ohne Executor (§11).
