# Korrekturen P3 (F4 · F5 · A9)

> Datum: 2026-10-05 · Status: **Auftrag** (Fixes) + **Belegt** (Regeln). Freigabe: `approved` (Batnini).
> Guardrail 7: echte Tests, 100 % Coverage. Kein Commit ohne Erlaubnis (Guardrail 6).

## 1. Umgesetzte Befunde

| ID | Befund | Fix | Regel | Datei |
|---|---|---|---|---|
| **F4** | `as_of` vor Bekanntwerden der Korrektur lieferte `[]` (mutiertes `valid_to` ohne Transaktionsbezug) | neues Feld `valid_to_known_at`; `as_of` zählt `valid_to` nur, wenn es zum `knowledge_time` **bekannt** war | §10.7 (Engram: „keep the history") | `bi_temporal.py` |
| **F5** | `call_tool_live.ok` = nur Transport (`not isError`); fachliches `ok=false` wurde als Erfolg gemeldet | `ok = transport_ok AND inner_ok` (inneres JSON `ok`); neues Feld `transport_ok` | §6 (eindeutiger Vertrag) | `mcp_live_binding.py` |
| **A9** | globaler `OpenAI(...)` beim Import → Crash/Collection-Fehler ohne Key | **lazy** Client (`_get_client()`), kein Netz-/Key-Zugriff beim Import | Guardrail 7 / Robustheit | `fast_write_router.py` |

## 2. Diff (Kern)

- **F4** `bi_temporal.py`: `Fact.valid_to_known_at`; in `assert_fact` beim Supersede `f.valid_to_known_at = recorded_at`;
  `as_of`: `if knowledge_time >= (valid_to_known_at or recorded_at) and valid_time >= valid_to: skip`.
- **F5** `mcp_live_binding.py`: `_inner_ok(content)` (JSON `ok`); `call_tool_live` → `ok = transport_ok and inner_ok` + `transport_ok`.
- **A9** `fast_write_router.py`: `_client=None` + `_get_client()` (lazy); `_ask` nutzt `_get_client()`.

## 3. Tests (echt, Guardrail 7)

- `tests/test_bi_temporal.py`: +`test_as_of_vor_bekanntwerden_der_korrektur` (F4); **eine Erwartung korrigiert**
  (`as_of("2024-02-01","2024-04-01")` `[]` → `["Globex"]` — die alte Zeile kodierte den Fehler).
- `tests/test_mcp_live_binding.py`: +`test_call_tool_live_rejected_write` (F5), +`test_inner_ok_zweige`.
- `tests/test_fwr.py`: +`test_import_ohne_key_kein_crash` (A9).
- **Volle Suite: 337 passed · 100 % (2707/648).**

## 4. Gate (§9)

- Verhaltens-/Interface-Änderungen (Fact-Feld, Rückgabe-Vertrag, lazy Client) → **approved** (Batnini).
- Guardrail 3: Provenienz `ergebnisse/rekursion/060-fixes-p3.md`. §9.1b: `AGENTS.md` unverändert.
- Guardrail 6: **kein Commit** ohne Erlaubnis.
- **Ehrliche Grenzen:** F4-`as_of` ist die korrigierte Semantik (nur eine Test-Erwartung angepasst, begründet);
  `data/memory/tier1-base/ontology.md` beschreibt das neue Feld `valid_to_known_at` **nicht** (nicht geändert → kein §9.1b-Snapshot).
