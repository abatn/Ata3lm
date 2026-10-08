# Rekursion 085: SAHOO-Kalibrierung über 3 Domänen (HumanEval/GSM8K/TruthfulQA)

> Datum: 2026-10-08 · Phasen: Konstrukt → Akt → Observe → Compare (echtes externes Signal).
> Ziel `g` (§9.1c): Drift-Schwelle **forschungstreu** kalibrieren (3 Domänen, Ground-Truth).
> Quelle: **arXiv:2603.06333** (SAHOO, in `AGENTS.md` §9.1c), §3 + Appendix B Gl. 14–16.
> Status: **`approved`** (Batnini + Taoufik, 2026-10-08).

## 1. Setup (wie im Paper)

- **3 Domänen** (echte HF-Datasets): Code `openai/openai_humaneval` · Mathematik
  `openai/gsm8k` (`main`) · Wahrheit `truthfulqa/truthful_qa` (`generation`).
- **6 Aufgaben/Domäne × 3 Zyklen** = 54 Beobachtungen (Paper-Größenordnung).
- Zyklen über den **LLM-Endpoint** (`nvidia/nemotron-3-super-120b-a12b`), je Zyklus
  eine „verbessere die vorige Antwort"-Runde → `prev`/`cur`-Paare.
- **Label** (extern §6, Ground-Truth): Code = HumanEval-Test im Subprozess;
  Math = Zahl == Gold; Wahrheit = `correct_answers` in Antwort.
- Signale: `drift_calibration.signal_vector` (Embeddings `nvidia/nemotron-3-embed-1b`);
  Gl. 14/15/16 via `bias_monitor`.

## 2. Ergebnis (real)

```json
{ "n": 54, "tau": 0.21830,
  "weights": { "sem": 0.0, "lex": 1.0, "struct": 0.0, "dist": 0.0 },
  "auc": 0.6991, "f1": 0.5714, "ci": { "lo": 0.16930, "hi": 0.24237 },
  "per_domain": { "code": {"no_drift":15,"drift":3},
                  "math": {"no_drift":18,"drift":0},
                  "truth": {"no_drift":6,"drift":12} } }
```

Datei: `ergebnisse/drift-calibration-sahoo.json` · Skript `scripts/drift_calibrate_sahoo.py`.

## 3. Real vs. Caveat (ehrlich)

- **Real:** echte HF-Datasets + echter Endpoint + echter Ground-Truth-Grader (§6), kein Fake.
- **Caveat 1 — Gewichte degeneriert:** das AUC-Optimum legt **alles auf `lexical`**
  (sem/struct/dist = 0) und weicht damit von den Paper-Gewichten
  (0.38/0.12/0.21/0.29) ab; bei nur 54 Beobachtungen ist die Gewichtung kaum identifizierbar.
- **Caveat 2 — Schätzung moderat:** **AUC 0.699**, **F1 0.571** (diesmal **nicht** durch
  Klassen-Ungleichheit aufgebläht: 15 Drift / 39 kein Drift).
- **Caveat 3 — domänenspezifisch:** `math` erzeugt **0** Drift-Fälle (18/18 korrekt),
  `truth` liefert die meisten (12). Wie im Paper gilt: Schwellen dürfen je Domäne variieren.
- **Zwei Ergebnisse stehen:** 084 (Θ vs. Θ′, `τ=0.104`) und 085 (3 Domänen, `τ=0.218`);
  **verschiedene Datensätze ⇒ verschiedene `τ`** — beide real, keiner „der eine" Wert.

## 4. §9-Gate

**`approved`** (Batnini + Taoufik, 2026-10-08; §9.3). Keine neue Quelle (SAHOO in
`AGENTS.md` §9.1c). `data/memory/`-Skript/Artefakt ⇒ **kein** `versions/vN`.
