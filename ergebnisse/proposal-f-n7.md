# PROPOSAL F — N7: Bei `world_state_probe` entscheidet die Oracle-Evidenz (nicht Selbstreport)

> **Phase 0 — NUR Entwurf (Auftrag „Knowledge-Agent härten N1–N8"). NICHT implementieren
> vor §9 `approved` (≥ 2 Personen, §9.3). Befund-Quelle (verbindlich): Audit b09a0a9.**

## 0. Metadaten

| Feld | Wert |
|---|---|
| Datum | 2026-10-08 |
| Iteration | `t → t+1` (geplant, Phase 2) |
| Phase | Konstrukt (Entwurf) |
| Betroffenes Artefakt | `data/memory/recursion_runner.py` |
| Komponenten-Typ | Code |
| Autor | Knowledge-Agent (Auftrag N1–N8) |

### Befund (Soll/Ist, Audit b09a0a9 — verbindlich)

**N7 · P2 · Oracle-Compare vs. Revise verschiedene Evidenz.**
Datei: `recursion_runner.py` ~`:83` (Compare) · ~`:166-169` (Revise).
**Soll:** Bei `world_state_probe` entscheidet die **Oracle-Evidenz**.
**Ist:** `_phase_compare` wertet bei gesetztem `world_state_probe` das Out-of-Band-Ergebnis (`world_state_oracle.evaluate`) aus und meldet `observed`; `_phase_revise` rechnet aber weiter mit dem **Selbstreport** (`score = ctx["successes"] / n`, `evidence_ok` über `ctx["successes"] >= 1`) ⇒ Compare und Revise stützen sich auf **verschiedene** Evidenzquellen; bei `world_state_probe` entscheidet der Selbstreport statt des Oracles (Verstoß gegen §6 „Compare nur mit externem Signal").
Repro (Phase 2): `test_oracle_success_drives_revision_without_self_report`.

## 1. Ziel `g`

- Ziel: Bei gesetztem `world_state_probe` fließt **ausschließlich** die Oracle-Evidenz in die Revisionsentscheidung ein (Selbstreport bleibt Annotation, wie in Compare).
- Task-Input: Repro-Fall aus `tests/test_network_boundaries.py` (Audit b09a0a9).

## 2. Baseline (vorher)

| Feld | Wert |
|---|---|
| `π` (Modell/Policy) | Rev. `b09a0a9`, `recursion_runner.py` |
| Score (externes Signal) | `0/1` = `0 %` — **gemäß Audit-Befund** (Repro-Test entsteht mit Phase 2) |
| Signal-Quelle | 1 benannter Repro-Fall (Audit) |
| Drift-Referenz | Git-Hash `b09a0a9` |

## 3. Änderung (Diff-Skizze, line-level — Richtung, kein Final-Patch)

```diff
 # recursion_runner.py (~:166-169, _phase_revise)
-    n = ctx["successes"] + ctx["failures"]
-    score = (ctx["successes"] / n) if n else 0.0
-    evidence_ok = bool(vergleich.get("observed")) and ctx["successes"] >= 1 and score >= REVISE_MIN_SCORE
+    if ctx.get("world_state_probe"):
+        # N7: bei world_state_probe entscheidet die Oracle-Evidenz (§6) — kein Selbstreport.
+        score = oracle_score(vergleich)          # aus world_state_oracle-Ergebnis
+        evidence_ok = bool(vergleich.get("observed")) and oracle_positive(vergleich) and score >= REVISE_MIN_SCORE
+    else:
+        n = ctx["successes"] + ctx["failures"]
+        score = (ctx["successes"] / n) if n else 0.0
+        evidence_ok = bool(vergleich.get("observed")) and ctx["successes"] >= 1 and score >= REVISE_MIN_SCORE
```

- Geänderte Komponenten: **1**.
- Interface-/Format-Änderung? **ja** — bei `world_state_probe` ändert sich das Format/Verhalten der Revisionsentscheidung (Oracle-Evidenz statt Selbstreport); ctx-Schema unverändert ⇒ §9/Guardrail 4, Human-Gate.

## 4. Score-Änderung

| Testfall | Kriterium | vorher | nachher (Ziel) |
|---|---|---|---|
| `test_oracle_success_drives_revision_without_self_report` | Oracle-Erfolg treibt Revision ohne Selbstreport | fail (Audit-Ist) | pass |

- **Score vorher:** `0/1` = `0 %` (Audit-Befund) · **Score nachher (Ziel):** `1/1` = `100 %`
- **Δ Score (Ziel):** `+100` Prozentpunkte

## 5. Drift (Δ zur Baseline)

- **Definition (Auftrag):** `Δ = geänderte Zeilen / Gesamtzeilen des Artefakts`.
- **Drift-Wert (Schätzung):** ~10/355 ≈ **3 %**.
- **Drift-Bound:** 10 % (Default, §9.1c). **Überschritten?** nein (Schätzung; Messung in Phase 2).

## 6. Evidenz / Quellen

- Quelle 1: AGENTS.md §6 („Compare nur mit externem Signal … sonst konfidente Fehlanpassung") — intern; arXiv:2609.08832 (Consistency Gap) — **bereits im Projekt**.
- Quelle 2: Rekursion 073 (M3: Out-of-Band-Evaluation / World-State-Oracle, `ergebnisse/rekursion/073-out-of-band-eval.md`) — intern.
- Interne Referenz: `data/memory/recursion_runner.py:83-100,150-185` · Audit b09a0a9.

## 7. Gate-Entscheidung (§9)

| Bedingung | Wert | Ergebnis |
|---|---|---|
| Score | `0 % → 100 %` (Ziel) | ask |
| Neue Quelle? | nein | — |
| Interface-/Format-Änderung? | **ja** (Revisionsentscheidung) | **ask** |
| Drift ≤ Bound? | ja (≈ 3 % ≤ 10 %) | — |

- **Gate-Ergebnis:** **`ask`** — Interface-/Format-Änderung (Guardrail 4, `AGENTS.md` §9:120) ⇒ §9 `ask` (≥ 2 Personen, §9.3).

## 8. Freigabe

- Status: `pending`
- Human-Gate-Referenz: Rekursion entsteht mit Phase-2-Umsetzung.
