# Rekursion 089: Fail-closed Konsolidierung (F1/F2/F3, Audit 75095d5)

> Datum: 2026-10-08 · Phasen: Konstrukt → Akt → Observe → Compare → Revise.
> Ziel `g` (§9.1c): `flush`/`mark_consolidated`/`_is_consolidated` **fail-closed** an
> Inhalt (`fact_sha256`) **und** positiven Probe binden (F1/F2/F3).
> Quellen (in `AGENTS.md` referenziert ⇒ **keine neue Quelle**):
> **arXiv:2608.22215 §3.4** (AGENTS.md §10.3: Flush nur nach Erfolg, sonst bleibt
> der Fakt) und **`connectors/gaama.md`** (Kairos/Validation-Gated: nur ein
> **positiver** Probe erlaubt Konsolidierung).
> Status: **`approved`** (Batnini + Taoufik, 2026-10-08; §9 Interface-Änderung).

## 1. Soll (Belegt + Auftrag)

- **F1** `flush(...)`: Löschen **nur** bei
  `entries[key].fact_sha256 == content_hash(aktueller Datei-Inhalt)` **und**
  `probe_passed=True`. Mismatch (Fakt geändert), unbekannter Hash, fehlender
  Eintrag oder negativer Probe ⇒ **blocked**, kein Löschen (§10.3 „sonst bleibt").
- **F2** `mark_consolidated(..., probe_passed=False)`: Key **nicht** als
  konsolidiert verbuchen; eine frühere Konsolidierung wird **herabgestuft**.
  `flush`/`discard_if_consolidated` respektieren nur `probe_passed=True`
  (Kairos/Validation-Gated).
- **F3** `_is_consolidated(entry, current_sha)`: **unbekannter Hash ⇒ False**
  (fail-closed, vorher `True`). ⟹ `collect_pending` blendet einen geänderten/
  unbelegten Fakt nicht mehr aus; Discard nur bei Hash-Gleichheit **und** positivem
  Probe.

**Auftrag (Projekt):** die 3-Klassen-Aktionen und Key-Zuordnung sind an §10.7
gebunden; die Formeln/Forderungen stammen aus den o. g. Quellen (Belegt).

## 2. Ist (vorher → nachher)

**Vorher (75095d5, fail-open):**
`_is_consolidated` lieferte bei unbekanntem Hash `True` (Legacy-Key-Match);
`mark_consolidated` ignorierte `probe_passed` beim Verbuchen; `flush` prüfte nur
den Key (`k in consolidated`) und löschte **ohne** Inhalt-Gleichheit. Ein nach dem
Erfolg geänderter Fakt bzw. ein Legacy-State ohne Hash konnte so gelöscht/versteckt
werden.

**Nachher:**

| Ort | Änderung |
|---|---|
| `slow_consolidation._is_consolidated` | fail-closed: kein Eintrag / Probe≠True / Hash leer ⇒ `False`; sonst nur `stored == current_sha` |
| `slow_consolidation.mark_consolidated` | `probe_passed=False` ⇒ kein Eintrag in `consolidated` + Herabstufung (`known.remove`) |
| `slow_consolidation.flush` | liest `entries`; Existenz ⇒ `missing`; sonst `_is_consolidated(entry, content_hash(Datei))` ⇒ nur bei True löschen, sonst `blocked` |
| `fast_write_router.discard_if_consolidated` | erbt fail-closed über `_is_consolidated` (Hash **und** Probe) – Code unverändert, nur Delegation/Doc |
| `fast_write_router._get_client` | keine Semantikänderung; Offline-Coverage-Test ergänzt |

**Wichtiger Effekt (bewusst, fail-closed):** **Legacy-States ohne Hash**
(`{"consolidated":[keys]}`, `fact_sha256=None`) sind ab jetzt **inert** – sie
verhindern weder Sammeln noch erneutes Schreiben und werden **nicht** gelöscht.
Es wurde **kein** Migrations-/Rückfall-Mechanismus erfunden (`AGENTS.md` §6).

## 3. Diff

```
 data/memory/fast_write_router.py  | 11 +++--
 data/memory/slow_consolidation.py | 99 ++++++++++++++++++++++++++++-----------
 tests/test_lifecycle_discard.py   | 48 +++++++++++++++----
 tests/test_network_boundaries.py  | 13 ++++-
 tests/test_slow_consolidation.py  | 10 +++-
 5 files changed, 138 insertions(+), 43 deletions(-)
 tests/test_f1f2f3_consolidation_binding.py | neu, 161 Zeilen (untracked)
```

- `slow_consolidation.py`: `_is_consolidated` (fail-closed), `mark_consolidated`
  (Probe-Herabstufung), `flush` (Hash+Probe-Bindung), Docstrings/§9-Kennzeichnung.
- `fast_write_router.py`: Docstring F2/F3 + Kommentar; keine Logikänderung.
- Tests: zwei Hash-bindungslose Erwartungen angepasst (`test_slow_consolidation`,
  `test_network_boundaries`), Legacy-Discard-Test auf F3 umgestellt
  (`test_lifecycle_discard`), neue Repros `test_f1f2f3_consolidation_binding.py`.
- `AGENTS.md` und `data/memory/tier1-base/` **nicht** geändert.

## 4. Compare / Tests (echtes externes Signal)

Neue Repros (`tests/test_f1f2f3_consolidation_binding.py`, echte tmp-Dateien + echte
PROV-O-Records):

| Test | Aussage |
|---|---|
| `test_flush_preserves_fact_updated_after_success` | F1: nach Erfolg geänderter Fakt bleibt (`blocked`); nach erneutem Hash-Beleg löschbar |
| `test_flush_legacy_state_without_hash_is_blocked` | F1/F3: Legacy-State ⇒ inert, kein Löschen, kein Discard |
| `test_failed_probe_cannot_enable_discard_or_flush` | F2: negativer Probe ⇒ kein Verbuchen/Discard/Flush |
| `test_probe_regression_demotes_prior_consolidation` | F2: späterer negativer Probe stuft frühere Konsolidierung herab |
| `test_consolidated_old_key_does_not_hide_updated_fact` | F3: geänderter Fakt wird wieder `pending` |
| `test_router_does_not_discard_changed_answer_for_old_key` | F3: Router verwirft nur die inhaltsgleiche Antwort |
| `test_is_consolidated_unknown_hash_is_fail_closed` | F3 (Einheit): unbekannter Hash/Negativ-Probe ⇒ `False` |

Angepasst (kodierten das alte fail-open Verhalten):
`tests/test_network_boundaries.py::test_flush_requires_success_evidence`
Fall 4 (Hash gebunden) + neuer Fall 5 (Hash fehlt ⇒ `blocked`, kein Löschen);
`tests/test_slow_consolidation.py` (`test_collect_state_filtert_konsolidiertes`,
`test_flush_entfernt_nur_konsolidierte` binden jetzt den Hash);
`tests/test_lifecycle_discard.py::test_echter_konsolidierungs_state` (F3: realer
Legacy-State ⇒ inert ⇒ `None`; **kein** Schreiben in die reale Datei).

**Akzeptanz (ausgeführt):**

- `.venv/bin/python -m pytest -m "not network and not live" -q --no-cov -p no:cacheprovider`
  → **693 passed, 27 deselected**.
- `ruff check` + `ruff format --check` (geänderte/neue Dateien) → sauber.
- Coverage (voller Offline-Lauf, `--cov-branch`) → `slow_consolidation.py`
  **100 %** (173 Stmts / 68 Branches, 0 Miss) und `fast_write_router.py`
  **100 %** (188 Stmts / 50 Branches, 0 Miss). Hinweis: der Offline-Test
  `test_get_client_lazy_offline` schließt die sonst nur netz-erreichte Lücke in
  `_get_client` (A9, nur Client-Bau, kein Request).

## 5. §9-Gate

**`approved`** (Batnini + Taoufik, 2026-10-08). Keine neue Quelle
(arXiv:2608.22215 / `connectors/gaama.md` in `AGENTS.md` referenziert).
Interface-Änderung (fail-closed Semantik von `flush`/`mark_consolidated`/
`_is_consolidated`) ist freigegeben und im Docstring kenntlich gemacht.
`data/memory/`-Skript/Test ⇒ **kein** `versions/vN`.
**Kein** `git add/commit/push` (§G6); `git status --short`/`diff --stat` siehe §3.
