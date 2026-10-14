# Rekursion 116: P-C Kaskade Variante A (getrennte FWR-Modelle)

- **Datum:** 2026-10-14 · **Phase:** Konstrukt/Akt-Folgewirkung · kein Compare-Lauf.
- **Freigabe:** Batnini + Taoufik (Auftrag 2026-10-14, §9/§9.3). **Kein Diff-SHA gebunden** (§9.1d-Lücke, siehe T3).
- **Trennung:** P-A (Grader) ist in **Rek. 115** dokumentiert.

## 1. Ziel g

Die Kaskade aus §10.2 (Stufe 1 klein, Stufe 2 groß) wird real getrennt; Laufzeitwerte werden protokolliert. Alternative Variante B (§10.2 streichen) ist nicht gewählt.

## 2. Baseline

`_configure_llm_env` setzte `FWR_SMALL_MODEL` = `FWR_LARGE_MODEL` = `--llm-model` (`kaggle/write_back_cycle.py`). Die Kaskade wirkte also nicht.

## 3. Diff (line-level, §3)

- `_configure_llm_env(base_url, model, *, small_model=None, large_model=None)`: Default = gemeinsames Modell (rückwärtskompatibel); gibt `applied` zurück.
- CLI `--fwr-small-model` / `--fwr-large-model` (Default `None` = `--llm-model`).
- `main()` schreibt das Laufzeit-Protokoll `LLM-ENV (Laufzeit-Protokoll, P-C): {...}` auf stdout.
- **Interface:** neue optionale keyword-only Parameter (additiv).

## 4. Test / Prüfung

- `py_compile` OK; `--help` zeigt beide Flags (siehe Verifikationslauf in Abschlussbericht).
- Kein eigener Unit-Test für die Env-Zuweisung in dieser Iteration (offen).

## 5. Score-Änderung / Drift

- **Score:** nicht gemessen.
- **Drift:** nicht gemessen (kein Wert erfunden).

## 6. Caveat (ehrlich)

- Kein Lauf mit zwei verschiedenen Modellen. Verfügbarkeit der Größen (Paper 1.7B/8B, arXiv:2608.22215 §3.3) ist offen. Das Laufzeit-Protokoll macht die tatsächlichen Werte sichtbar.

## 7. Nicht behauptet (§7)

- Keine Wirkungsaussage zu Θ′.
