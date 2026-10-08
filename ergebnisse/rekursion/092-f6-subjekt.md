# Rekursion 092: F6 – ZsRE-Fragen an ihr Subjekt binden (Audit 75095d5)

> Datum: 2026-10-08 · Phasen: Konstrukt → Akt → Observe → Compare → Revise.
> Ziel `g` (§2/§9.1c): ZsRE-Fragen dürfen ihren **Subjektbezug** nicht verlieren.
> `row_to_record` muss den ZsRE-Platzhalter `XXX` durch das `subject` ersetzen,
> damit die Frage subjektgebunden ist – im Paper die (knowledge, query, answer)-
> Triples. Quellen (in `AGENTS.md` referenziert ⇒ **keine neue Quelle**):
> **arXiv:2608.22215 §4.1** („fact corpus from ZsRE … behavioral labeling";
> RQGM-Forderung „subjektgebundene QA-Daten"), Ursprung **Levy, Seo, Choi &
> Zettlemoyer 2017 (CoNLL, `K17-1034`)**. Status: **`approved`** (§9-Freigabe
> Batnini + Taoufik, 2026-10-08) – **Formatänderung** der Records, kenntlich
> gemacht. Kein `self_update` an `AGENTS.md`/`tier1-base`.

## 1. Soll (Belegt + Auftrag)

- **Belegt (arXiv:2608.22215 §4.1):** Der Fakten-Korpus wird aus **ZsRE** gebaut
  und **behavioral** gelabelt; die Frage ist an ihr **Subjekt** gebunden (im
  Paper die `(knowledge, query, answer)`-Triples). Beispiel (frisch aus der
  Quelle): `In one word, how did XXX die?`, `subject=Chen Yi-hsiung`,
  `answers=[suicide]` ⇒ die Frage muss das Subjekt tragen.
- **Belegt (Levy et al. 2017, `K17-1034`):** Ursprung des `XXX`-Platzhalters
  und des `subject`-Feldes in ZsRE.
- **Auftrag (Projekt, F6):** Enthält die `question` `XXX` **und** ist ein
  `subject` vorhanden ⇒ `XXX` durch das Subjekt ersetzen (alle Vorkommen). Das
  Subjekt bleibt als Feld erhalten. **Kein** Erfinden: fehlt das `subject`,
  bleibt die Frage unverändert.
- **Randfälle (Auftrag):** ohne `subject` ⇒ `XXX` bleibt; Frage ohne `XXX` ⇒
  unverändert; mehrfaches `XXX` ⇒ alle Vorkommen ersetzt.

## 2. Ist (vorher → nachher)

**Vorher (Audit 75095d5, Subjekt verworfen):**

```python
question = str(row.get("question") or "").strip()   # "… XXX …"
# subject wird nur als Feld kopiert, die Frage bleibt mit "XXX"
```

⇒ Alle ~200 GPU-Fragen trugen `XXX` statt des Subjekts.

**Nachher:**

| Ort | Änderung |
|---|---|
| `zsre_corpus.row_to_record` | `subject` wird gelesen; `if "XXX" in question and subject:` → `question.replace("XXX", subject)` |
| `subject`-Feld | bleibt erhalten (gestrippt, `or None` bei Fehlen) |
| Modul-Docstring | **Formatänderung (§9 approved)** kenntlich gemacht + Quellen (`K17-1034`, §4.1) |
| `scripts/live_run.py` | **keine Änderung nötig**: `_record_to_task` liest `msgs[0]["content"]` – das ist bereits die **gebundene** Frage; das Subjekt wird nicht erneut verworfen |
| `tests/test_zsre_corpus.py` | `test_row_to_record_mapping` auf gebundene Frage angepasst (kodierte vorher `XXX`) |

## 3. Diff

```
 data/memory/zsre_corpus.py        | (+23/-…) Frage bindet subject (Formatänderung §9)
 tests/test_zsre_corpus.py         | (+4/-…) Mapping-Test auf gebundene Frage
 tests/test_f6_subject.py          | neu, 4 Tests (untracked)
 ergebnisse/rekursion/092-f6-subjekt.md | neu (diese Datei)
 ergebnisse/rekursion/README.md    | +1 Index-Zeile (092)
```

- `AGENTS.md` und `data/memory/tier1-base/` **nicht** geändert (Guardrail 6,
  §9.1b). Keine neue Quelle. `scripts/live_run.py` unverändert (nutzt die
  bereits gebundene Frage).

## 4. Compare / Tests (offline, echtes Test-Signal)

Neues Repro (`tests/test_f6_subject.py`, offline mit Fixture-Dict, Guardrail 7):

| Test | Aussage |
|---|---|
| `test_question_binds_subject` | F6-Kern: `Chen Yi-hsiung` in `messages[0].content`, **kein** `XXX`, `subject`-Feld gesetzt |
| `test_question_without_subject_keeps_placeholder` | ohne `subject` ⇒ `XXX` bleibt (kein Erfinden) |
| `test_question_without_placeholder_unchanged` | Frage ohne `XXX` ⇒ unverändert |
| `test_subject_binding_replaces_all_occurrences` | mehrfaches `XXX` ⇒ alle Vorkommen ersetzt |

Angepasst: `tests/test_zsre_corpus.py::test_row_to_record_mapping` – kodierte
den Roh-Platzhalter (`content == FIXTURE["question"]`), jetzt gebundene Frage.

**Akzeptanz (ausgeführt):**

- `.venv/bin/python -m pytest tests/test_f6_subject.py tests/test_zsre_corpus.py -q --no-cov`
  → **11 passed**.
- Coverage `data/memory/zsre_corpus.py` → **100 %** (56 Statements, 0 missed;
  16 Branches, 0 partial).
- `ruff check` + `ruff format --check` (geänderte/neue Dateien) → sauber.

**Ehrlicher Hinweis (keine Erfindung):** Bereits erzeugte ZsRE-JSONL-Korpora
(z. B. temporäre Lauf-Dateien aus vorherigen Rekursionen) enthalten noch den
`XXX`-Platzhalter; für subjektgebundene Daten muss neu gebaut werden
(`build_zsre_corpus`) – hier nur Code + Tests, kein Netz-/GPU-Lauf
(Guardrail 7). Die Bindung ist rein deterministisch (String-Ersetzung), keine
Heuristik und kein Paper-Claim über Wirkung.

## 5. §9-Gate

**`approved`** – §9-Freigabe Batnini + Taoufik, 2026-10-08. Die Änderung ist
eine **Formatänderung der Records** (Frage trägt das Subjekt), kein
`self_update` an Originaldateien, keine neue Quelle (ZsRE ist bereits über
§10/`connectors/fast-write-routing.md` verankert), keine
Interface-Änderung an Bestandsmodulen (Funktionssignatur `row_to_record(row)`
unverändert). `data/`-Datei/Test ⇒ **kein** `versions/vN`. **Kein**
`git add/commit/push` (Guardrail 6); `git status --short`/`diff --stat` siehe §3.
