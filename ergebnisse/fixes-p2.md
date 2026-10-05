# Korrekturen P2 (F3 · S2 · S3)

> Datum: 2026-10-05 · Status: **Auftrag** (Fixes) + **Belegt** (Regeln). Freigabe: `approved` (Batnini).
> Guardrail 7: echte Repro-Tests, 100 % Coverage. **Nur P2** (P3 offen). Kein Commit ohne Erlaubnis (Guardrail 6).

## 1. Umgesetzte Befunde

| ID | Befund | Fix | Regel | Datei |
|---|---|---|---|---|
| **F3** | Runner speicherte bei Mandats-`deny` weiter (raw+action, `revised=True`) | Stage 1 PII-minimieren; Stage 7 (`Handeln`) **übersprungen** wenn `Gedächtnis.ok` false; `Wissen+.revised = ok` | §9.1/§9.2a | `lifecycle_runner.py` |
| **S2** | Update überschrieb die Datei; erfundener `"alt"`-Vorgänger; keine echte Historisierung | Bestehenden **Structured-Stand archivieren** (`<key>.superseded-<ts>.md`), dann schreiben (invalidieren, nicht löschen) | §10.7 | `pipeline.py` |
| **S3** | Drift-Gate lief **nach** dem Write; konstante Verteilung | Drift-Gate **vor** dem Write; echte Verteilung `{cls: 1.0}`; bei `ask` **kein Write** | §9.1c | `pipeline.py` |

## 2. Diff (Kern)

- **F3** `lifecycle_runner.py`:
  - `_stage_erfahrung`: `wm.store(key, trust.PIIFilter().minimize(fact))`.
  - `_stage_handeln`: `if not ged["ok"]: return {..., "skipped": True}` (kein Action-Write).
  - `_stage_wissen_plus`: `revised = bool(ged["ok"])`.
- **S2** `pipeline.py` (write-update): vor dem Schreiben wird der bestehende `structured/<key>.md`
  nach `<key>.superseded-<int(now)>.md` archiviert; `superseded = {key, old_found, archived}`.
- **S3** `pipeline.py`: Drift-Gate (Schritt 5) **vor** Write (Schritt 6); `drift.observe({cls: 1.0})`;
  bei `gate=="ask"` → `{"ok": False, "gate": "ask", ...}` ohne Write.

## 3. Tests (echt, Guardrail 7)

- `tests/test_lifecycle_runner.py`: `test_denied_lifecycle_stoppt_writes` (F3).
- `tests/test_pipeline.py`: `test_write_update_archiviert_alten_stand` (S2, neu);
  `test_write_update_supersediert_bitemporal` (S2, an neuen Vertrag angepasst);
  `test_drift_gate_ok_bei_stabilität` (S3, Baseline = gemessene Verteilung).
- **Volle Suite: 333 passed · 100 % (2680/634).**

## 4. Gate (§9)

- Verhaltensänderungen (Runner-Gate, Update-Historisierung, Drift-Reihenfolge) → **approved** (Batnini).
- Guardrail 3: Provenienz `ergebnisse/rekursion/059-fixes-p2.md`. §9.1b: `AGENTS.md` unverändert.
- Guardrail 6: **kein Commit** ohne Erlaubnis.
- **Ehrliche Grenzen:** S2 archiviert den **Structured**-Stand; §10.7 nennt `tier1-base` — der
  tier1-Supersede läuft weiterhin über `fast_write_router.apply_write_action` (FWR-Direktpfad).
  Drift-Verteilung `{cls: 1.0}` ist die Verteilung **eines** Laufs (mehrstufige Verteilung = offen).
  **Offen (P3):** F4 (bi-temporal `as_of`), F5 (Transport-≠Fach-`ok`), A9 (lazy Client).
