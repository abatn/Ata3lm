# Rekursion 118 — Write-Back: Base-Rate-Guard aus dem Flush entfernt

## Befund

Der Run-Level-Guard `base_rate_guard` (`min_base_hits=1`) war über `guard_fn=_run_guard`
an den Write-Back-Flush gekoppelt (`kaggle/write_back_cycle.py`, Aufruf von
`slow_consolidation.write_back`). Folge: Fakten, die das Basismodell nicht kennt
(Base-Treffer = 0), konnten **nie** geflusht werden, auch wenn die Θ′-Probe sie korrekt
beantwortet. Das widerspricht dem Paper.

## Quellen

- **Paper arXiv:2608.22215 §3.4 (Flush), Gl. 8 und Text:**
  „A fact is removed from external memory only if consolidation is validated, i.e., the
  updated model answers its probes correctly without retrieval:
  1/m_i · Σ_j EM(Ans_Θ′(q_ij), a_ij) ≥ τ_flush. Otherwise, it remains in external memory."
  → Die Entscheidung ist **pro Fakt** über die mittlere Probe-EM mit Schwelle τ_flush.
  Eine Base-Rate-Bedingung oder einen Run-Level-Guard nennt §3.4 nicht.
- **Rekursion 115** (`ergebnisse/rekursion/115-grader.md`): Die Aussage „Guard nicht
  verdrahtet" in der Index-Notiz (`README.md:142`) war falsch. Die Rek.-115-Datei selbst
  verweist auf die Verdrahtung bei Z. 639.
- **SAGE-Docstring** (`data/memory/acceptance_gate.py:134–136`): Der Guard stammt aus
  SAGE arXiv:2609.36043 (abstain bei Denominator-0-Risiko). Er ist eine Paarvergleichs-
  Regel für das Acceptance-Gate, keine Write-Back-Regel aus 2608.22215.

## Änderung (Diff-Skizze)

```diff
 def _run_guard(probe_results: list):
     """...
     Ohne Ergebnisse ⇒ Einwand ("keine Items").
+
+    NICHT am Write-Back verdrahtet (Rek. 118): ...
     """
 ...
         state_path=state_path,
-        guard_fn=_run_guard,
     )
```

- `_run_guard` und `base_rate_guard` bleiben erhalten (Code-Stabilität).
- `acceptance_gate.evaluate` und das SAGE-Paargate sind unverändert.
- `slow_consolidation.write_back` unverändert: `guard_fn` bleibt als optionaler Parameter.

## Score / Drift

Keine Modellparameter- oder Prompt-Änderung → Score und Drift: **n/a**.

## Verifikation

Siehe `119-write-back-guard-fix-test.md`.

## Freigabe (§9.3)

| Approver | Status | Datum |
|---|---|---|
| Batnini | `first_approved` | 2026-10-16 |
| Taoufik | `second_approved` → `approved` | 2026-10-16 |

Flow: `pending → first_approved (Batnini) → second_approved (Taoufik) → approved`.
Gemäß AGENTS.md §9.3 (Z. 225-232): ≥2 distinkte natürliche Personen.
