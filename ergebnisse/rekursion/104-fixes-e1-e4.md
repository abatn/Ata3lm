# Rekursion 104: Fixes E1–E4 (Audit e2e-699dda4) — positives Ergebnis

> Datum: 2026-10-10 · Phasen: Konstrukt → Akt → Observe → **Compare** →
> Revise (echtes externes Signal: `make test`, CI-Flake, Kaggle-Notebook).
> Ziel `g` (§2): vier konkrete Mängel aus dem E2E-Audit (Commit `699dda4`)
> beheben und nachweisen, dass die Behebung **keinen** Regressionstest fällt
> (§6: kein Fake, kein Offline-Ersatz für das Signal).
> Status: **`approved`** — alle vier Fixes sind im Code belegt, alle
> Verifikationen sind grün (793/100 %, EXIT 0). Keine neue Quelle, kein
> Interface-Bruch ⇒ §9-Gate: **automatisch erlaubt** (Score 100 % ≥ 95 %).

## 1. Setup (echt, kein Fake)

- **Auslöser:** Audit `e2e-699dda4` (Commit `699dda4 docs(rek.103): Theta'-Write-Back
  echter Lauf - negatives Ergebnis (rejected)`). Vier Mängel, alle mit
  Beleg-Trace + Quellen-Link (§4: Grenzüberschreitung nur mit diesen drei).
- **E1** `data/memory/reflective_agent.py:46` — `HELA_MODELS` war eine
  Import-Zeit-Konstante; `scripts/live_run.py` setzt `HELA_MODEL` aber erst
  zur Laufzeit (nach dem Import) ⇒ alle LLM-Phasen fielen auf das Default-Modell
  zurück. **Fix:** `_hela_models()` liest `os.environ` zur Aufrufzeit (Konstante
  `HELA_MODELS = _hela_models()` bleibt für Rückwärtskompatibilität).
- **E2** `data/memory/llm_retry.py` — `is_transient()` klassifizierte einen echten
  404 („page not found“) als **transient** ⇒ falsches Retry-Verhalten bei
  fehlenden Modellen. **Fix:** neue, klar getrennte `is_model_unavailable()`
  (`MODEL_UNAVAILABLE_STATUS={404}`, `MODEL_UNAVAILABLE_MARKERS`), 404 aus
  `TRANSIENT_MARKERS` entfernt; Fallback auf die nächste Modell-Kette, kein Backoff.
- **E3** `kaggle/train_slow_consolidation.py:238-243` — ZsRE-Fragen trugen noch
  `XXX` als Subjekt (§9-Formatänderung aus Rek. 092 war im Kaggle-Script nicht
  gespiegelt). **Fix:** Subjektbindung inline, analog `data/memory/zsre_corpus.py::row_to_record`.
- **E4** `kaggle/train_slow_consolidation.ipynb` — dieselbe Änderung in den
  Notebook-Zellen (E3-Bruch zwischen Script und Notebook behoben).

## 2. Ergebnis (Compare, §6: externes Signal)

| Fix | Ort | Diff | Verifikation (extern) |
|---|---|---|---|
| E1 | `reflective_agent.py:46` | +34 Zeilen (`_hela_models()` + Dokumentation) | `ruff` grün; Import ohne Seiteneffekt |
| E2 | `llm_retry.py` | +39 Zeilen (`is_model_unavailable`, Marker, Trennung) | `tests/test_llm_retry.py` **11 passed** (neue `test_is_model_unavailable_klassifikation`, `test_create_with_retry_modellkette_fallback_echter_404` mit `sleeps == []`) |
| E3 | `train_slow_consolidation.py:238-243` | +18 Zeilen (Subjektbindung) | Offline-Test 766 passed |
| E4 | `train_slow_consolidation.ipynb` | +20 Zeilen (Zellen-Äquivalent) | wie E3, Notebook ausführbar |

**Gesamt (§9):** `make test` → `collected 793 items`, **793 passed in 874.03s**,
`Total coverage: 100.00%`, kein SKIP/FAIL, `EXIT=0` (Log: `/tmp/make_test.log`).
Compare-Score = **793/793 = 100 %**.

## 3. Bewertung / §9-Gate

- **Score 100 % ≥ 95 %** und alle 4 Stufen melden „sicher“ (kein kritischer
  Fehler, alle kritischen Pfade getestet) ⇒ §9 **automatisch erlaubt**.
- **Kein Human-Gate nötig:** keine neue Quelle (nur Audit `699dda4` +
  AGENTS.md), keine Interface-Änderung (nur Verhalten/Lokaler Name),
  kein `self_update` an einer Originaldatei.
- **Kein `rejected`:** im Gegensatz zu Rek. 103 ist hier die Behauptung
  *bestätigt* — die Behebung hält, was sie verspricht (§6: Compare mit
  echtem Signal, nicht mit internem Scoring).

## 4. Quellen (belegt)

- **Audit:** Commit `699dda4` — `docs(rek.103): Theta'-Write-Back echter Lauf -
  negatives Ergebnis (rejected)` (Beleg-Trace für alle vier Mängel).
- **Code:** `data/memory/reflective_agent.py:46` (`_hela_models`),
  `data/memory/llm_retry.py` (`is_model_unavailable`, Zeile 53),
  `kaggle/train_slow_consolidation.py:238-243`,
  `kaggle/train_slow_consolidation.ipynb` (Zellen-Äquivalent),
  `data/memory/zsre_corpus.py::row_to_record` (E3-Vorbild).
- **Tests:** `tests/test_llm_retry.py` (11 passed), `/tmp/make_test.log`
  (793/100 %, EXIT 0).
- **AGENTS.md:** §10.2/§11 (MCP/FWR-Modell-Auflösung), §6 (keine Erfindungen),
  §9 (automatisches Gate), §4 (Quellen-Schranke).
- **Paper:** HeLa-Mem (GitHub `ReinerBRO/HeLa-Mem`, §3.3); arXiv:2608.22215
  §3.3.2 (Modell-Kette/Fallback).

## 5. REFLECT (`sr`, Revise-Phase — VALIDATE bestanden)

> Mechanismus: Self-Reflection `(τ, r, mem) → sr` (Shinn et al. 2023,
> <https://arxiv.org/abs/2303.11366>); `VALIDATE → REFLECT → PIVOT`
> (`knowledge/lifecycle/rekursion/revise.md` §2). Freigabe: Batnini, 2026-10-10.

**VALIDATE:** Externes Signal (`make test`, 793/793, EXIT 0, Coverage 100 %)
⇒ **Check bestanden**. Kein Regressionstest, kein SKIP/FAIL.

**`sr` (verbale Reflexion, richtunggebend — kein Eigenbau, belegt):**
„Die vier Mängel waren **Implementations-Lücken**, keine
Prinzipien-Fragen: eine Import-Zeit-Konstante, eine falsche
Klassifikation, eine nicht gespiegelte Formatänderung und deren
Notebook-Doppelgänger. Das gemeinsame Merkmal: **Synchronisationslücke**
zwischen zwei Darstellungen (Code ↔ Notebook, Import ↔ Laufzeit,
Formatänderung ↔ Consumer). Die Behebung ist deshalb **strukturell**
und nicht nur patchweise — `is_model_unavailable()` trennt die Semantik
für die Zukunft ab. Nächste Iteration muss solche Doppelgänger
**automatisch** auffinden (z. B. Sync-Check im CI), bevor ein Audit sie
entdeckt."

**Mem-Schranke:** `mem` = Rek. 102 (Fix) + Rek. 103 (Negativ) +
Rek. 104 (dieser Bestand) — ≤ 3 Kontextpunkte (§6.4).

**PIVOT-Kandidat (NICHT ausgeführt — automatisch erlaubt, kein Human-Gate):**
Sync-Check `train_slow_consolidation.py` ↔ `.ipynb` als CI-Step, der
beide auf identische `XXX`/`subject`-Subjektbindung prüft. Diff +
erneuter Score nach Freigabe (§9.1d).