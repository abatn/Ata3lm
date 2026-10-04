# Verifikations-Verifikation (Zwei-Personen-Gate · Guardrail 7 · Out-of-Band)

> Datum: 2026-10-04 · Status: **Belegt** (Quelle) + **Auftrag** (Repo-Zuordnung).
> Ziel `g`: prüfen, ob die **externe Verifikation** im Repo real existiert — mit `Datei:Zeile`.
> Lab-Prinzip §6: keine Erfindung; fehlende Begriffe werden **klar** benannt.

## 1. Quelle (verifiziert)

- **When Do Agent Loops Mistake Stagnation for Progress? Self-Evaluation Bias and Externally
  Grounded Verification in Long-Running Autonomous LLM Agent Loops** — Park & Choi (2026),
  arXiv:2607.25152; **Zenodo concept DOI 10.5281/zenodo.21594735** („Progress Mirage").
  Wörtlich: „Across 54 cycles a frontier agent claimed improvement every time, yet **56 percent
  had a measured delta of zero or below**"; „the self-verdict gate … degenerated into accept-all";
  „**out-of-band evaluation with real-world access is a structural requirement**".

## 2. Verifikations-Tabelle (`Datei:Zeile`)

| Komponente | Status | Beleg |
|---|---|---|
| **Zwei-Personen-Gate** | **vorhanden** | `data/memory/approval.py:36` (`class TwoPersonApproval`), `:17` (Flow), `:45` (`approve`), `:55` (distinkt-Prüfung), `:72` (`first_approved`/`second_approved`), `:76-77` (`finalize`, `< 2`), `:83` (`approved`); Gesetz `AGENTS.md:229,231` |
| **Guardrail 7** | **vorhanden** | `AGENTS.md:105-106` („Tests/Compare nur mit echten Quellen/LLM/Endpoint; Fake verboten"); echte Ausführung `tests/_live.py:3,26,31` (`call` → echte Funktion); reale Calls `tests/test_reflective.py:141`, `tests/test_evaluator_version.py:371`, `tests/test_fwr.py:17`, `tests/test_gaama_extract.py:75` |
| **Out-of-Band Evaluation** | **vorhanden** (als Held-out-Anchor) | `data/memory/evaluator_version.py:167` (`class GroundTruthAnchor`), `:168` („Held-out Ground-Truth-Checkpoints"), `:205` (`anchor_successes`), `:411` (`class RedQueenLoop`); Gesetz `AGENTS.md:65` („Compare nur mit externem Signal") |

## 3. Details

- **Zwei-Personen-Gate:** `pending → first_approved → second_approved → approved`; `finalize`
  verlangt **≥ 2 distinkte** Personen (`approval.py:77`); dieselbe Person zählt nicht doppelt
  (`:55`). Gesetz: AGENTS.md §9.3.
- **Guardrail 7:** Kein Fake — `tests/_live.py::call` ruft die **echte** Funktion (LLM/Endpoint)
  mit Retry nur für transiente Fehler; Compare nur mit echtem Signal.
- **Out-of-Band / Held-out:** `GroundTruthAnchor` = **held-out Ground-Truth-Checkpoints** (externes
  Signal) treibt `RedQueenLoop`. Das entspricht dem Paper-Kern: Bewertung muss **außerhalb** des
  Transkripts (real-world) verankert sein.

## 4. Fazit (ehrlich)

- **Zwei-Personen-Gate, Guardrail 7, externes Signal (Held-out-Anchor)** sind **real implementiert**
  und **verdrahtet**.
- **Ehrliche Lücke:** Der Begriff **„Out-of-Band"** steht **nicht** im Repo; belegt ist
  **„Held-out Ground-Truth-Checkpoints"** (`evaluator_version.py:168`). Die Gleichsetzung ist
  **Auftrag/Mapping**, kein wörtliches Zitat. Das Paper stützt Guardrail 7: Selbstbewertung ist
  unzuverlässig (56 % delta ≤ 0) → externe Verifikation ist strukturell nötig.

## 5. Gate (§9)

- Reine **Verifikation + Doku** (keine Code-/Interface-Änderung) → kein Human-Gate nötig.
- Guardrail 3: Provenienz `ergebnisse/rekursion/055-verifikation-verifikation.md`.
- Guardrail 6: kein Commit ohne Erlaubnis. §9.1b: `AGENTS.md` unverändert.
