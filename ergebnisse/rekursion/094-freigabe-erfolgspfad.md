# Rekursion 094: Freigabe-Erfolgspfad im Live-Driver (Zwei-Personen-Freigabe §9.3)

> Datum: 2026-10-09 · Phasen: Konstrukt → Akt → Observe → Compare → Revise.
> Ziel `g` (§2/§9): `write-new`/`write-update` im Live-Driver sollen **mit**
> Zwei-Personen-Freigabe tatsächlich schreiben können – bisher blieb der Akt-Write
> auf `ask`. Quellen (**Belegt**, bereits im Gesetz referenziert ⇒ **keine neue
> Quelle**): `AGENTS.md` §9/§9.3 · `data/memory/approval.py` (EU-KI-VO
> VO (EU) 2024/1689 Art. 14(5), zwei distinkte natürliche Personen);
> `data/memory/write_gateway.py`/`pipeline.py` (Gate-Kette `allow|ask|deny`).
> Status: **`approved`** (§9-Freigabe Batnini + Taoufik, 2026-10-08) –
> **Interface-Änderung**, kenntlich gemacht. Kein `self_update` an
> `AGENTS.md`/`tier1-base`.

## 1. Soll (Belegt + Auftrag)

- **Belegt (§9.3 / approval.py):** `approved` nur bei **≥ 2 distinkten**
  natürlichen Personen; `Flow: pending → first_approved → second_approved →
  approved`. Doppelte Namen zählen nicht.
- **Auftrag (§9):** `write-new`/`write-update` tragen im FWR das Gate `ask`
  (`fast_write_router._decide`). Ein Write ist nur mit menschlicher Freigabe
  zulässig; `deny` wird nie umgangen.
- **Auftrag (R094):** `recursion_runner.run_recursion` muss – wie bereits
  `lifecycle_runner.run_cycle` – `self_update`/`approvers` annehmen und in der
  Akt-Phase an `pipeline.route_and_store` durchreichen. Der Live-Driver erhält
  eine CLI `--approver` (mehrfach); **≥ 2 distinkte** Namen aktivieren
  `self_update` an **beiden** Runnern. **Default unverändert** (kein Write ohne
  Freigabe).

## 2. Ist (vorher → nachher)

| Ort | Vorher | Nachher |
|---|---|---|
| `recursion_runner.run_recursion` | kein `self_update`/`approvers`; `_phase_akt` rief `route_and_store(...)` ohne Freigabe ⇒ Akt blieb `ask` | + optionale Parameter `self_update=False`, `approvers=None`; `_phase_akt` reicht sie an `route_and_store` |
| `scripts/live_run.py` | kein Freigabe-Schalter; beide Runner ohne Freigabe | + CLI `--approver NAME` (`action="append"`); `_resolve_approvers` ⇒ bei ≥ 2 distinkten Namen `self_update=True` + `approvers` an **beide** Runner |

## 3. Umsetzung (Interface-Änderung §9 approved)

- `data/memory/recursion_runner.py`:
  - Signatur `run_recursion(..., self_update: bool = False, approvers=None, ...)`
    (keyword-only).
  - `ctx["self_update"]`/`ctx["approvers"]` gesetzt; `_phase_akt` ruft
    `pipeline.route_and_store(..., self_update=ctx["self_update"], approvers=ctx["approvers"])`.
  - Default `False`/`None` ⇒ **exakt altes Verhalten** (Gate bleibt `ask`,
    kein Write ohne Freigabe).
- `scripts/live_run.py`:
  - `_resolve_approvers(approvers)` → `(self_update, distinkte Namen)`; dedupliziert,
    trimmt, Schwelle **≥ 2** (§9.3).
  - CLI `--approver` (`action="append"`, Default `None`).
  - `_run_task(..., self_update=False, approvers=None)` reicht an **beide** Runner
    (`run_cycle` **und** `run_recursion`) durch; `main` setzt die Werte aus
    `_resolve_approvers` und protokolliert sie im Payload (`self_update`/`approvers`).
  - Ohne `--approver` (bzw. < 2 distinkten) ⇒ Default-Pfad, Gate `ask`.

## 4. Diff (erwartet; `git status --short`/`--stat` siehe unten)

```
 data/memory/recursion_runner.py        | +~22/-1  (Parameter + Akt-Durchreichung)
 scripts/live_run.py                    | +~50/-4  (_resolve_approvers, CLI, _run_task, Payload)
 tests/test_freigabe_pfad.py            | neu      (8 Tests)
 ergebnisse/rekursion/094-freigabe-*.md | neu      (diese Datei)
 ergebnisse/rekursion/README.md         | +1       (Index-Zeile 094)
```

- `AGENTS.md` und `data/memory/tier1-base/` **nicht** geändert (Guardrail 6,
  §9.1b). `tests/test_recursion_runner.py` unverändert. Keine neue Quelle.

## 5. Compare / Tests (offline, echtes Test-Signal)

Neues Repro (`tests/test_freigabe_pfad.py`, offline; Guardrail 7 – **kein**
Netz/Endpoint; Router-Stub `{"class":"write-new","gate":"ask"}`):

| Test | Aussage |
|---|---|
| `test_zwei_personen_freigabe_erlaubt_write` | `self_update=True` + 2 distinkte Personen ⇒ Akt `gate=allow`/`ok=True`, `structured/wo.md` real geschrieben |
| `test_ohne_freigabe_kein_write_ask` | Default ⇒ Akt `ask`, **kein** Write |
| `test_ein_approver_keine_freigabe` | 1 Person ⇒ §9.3 nicht erfüllt ⇒ `ask`, kein Write |
| `test_zwei_gleiche_namen_keine_freigabe` | derselbe Name zweimal zählt nicht (distinkt) ⇒ `ask` |
| `test_resolve_approvers_distinkt_und_schwelle` | Dedup + Schwelle ≥ 2 |
| `test_cli_zwei_approver_aktiviert_self_update` | CLI: 2× `--approver` ⇒ `self_update=True` an `_run_task` |
| `test_cli_ohne_approver_bleibt_ask` | CLI ohne `--approver` ⇒ `self_update=False` |
| `test_cli_ein_approver_bleibt_ask` | CLI mit 1 `--approver` ⇒ `self_update=False` |

**Akzeptanz (ausgeführt):**

- `.venv/bin/python -m pytest tests/test_freigabe_pfad.py -q --no-cov` → **8 passed**.
- `.venv/bin/python -m pytest -m "not network and not live" -q --no-cov -p no:cacheprovider`
  → **729 passed, 27 deselected**.
- Coverage `data/memory/recursion_runner.py` → **100 %** (99 Statements, 0 missed;
  32 Branches, 0 partial).
- `ruff check` + `ruff format --check` (geänderte/neue Dateien) → sauber.

## 6. §9-Gate

**`approved`** – §9-Freigabe Batnini + Taoufik, 2026-10-08. Die Änderung ist
eine **Interface-Änderung** (`run_recursion`-Parameter; neue CLI-Option
`--approver`) – kenntlich gemacht. Alle neuen Parameter haben
**rückwärtskompatible Defaults** (`False`/`None`) ⇒ Default-Verhalten
unverändert (kein Write ohne Freigabe, Gate bleibt `ask`). Keine neue Quelle
(§9.3/`approval.py` bereits im Gesetz), kein `self_update` an Originaldateien.
Änderungen an `data/memory/` nur in `recursion_runner.py`/`scripts/live_run.py`
⇒ **kein** `versions/vN`, `tier1-base` unberührt. **Kein** `git add/commit/push`
(Guardrail 6); `git status --short`/`diff --stat` siehe unten.
