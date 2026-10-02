# Rekursion 034: Externer Grader-Test (GPU-Endpoint) – JSON gelöst, Genauigkeit modelllimitiert

> Datum: 2026-10-02 · Tiefe: `t=33 → t=34` · Phase: **Observe → Compare**
> Freigabe: `approved: Batnini, 2026-10-02` (Auftrag „test und führe dein Plan").
> Ziel `g`: κ belastbar machen – zuerst das **JSON-Problem** (Rekursion 033) lösen,
> dann die **Grader-Genauigkeit** messen.

## 1. Aufbau (externe Endpoints, vom Auftraggeber bereitgestellt)

| Endpoint (Ollama, OpenAI-kompatibel) | Modell | Erreichbar |
|---|---|---|
| `https://a221-34-134-79-67.ngrok-free.app/v1` | `qwen3:14b` | `/v1/models` → 200 |
| `https://d07b-34-134-17-240.ngrok-free.app/v1` | `qwen2.5:14b` | `/v1/models` → 200 |

Unser Code lief unverändert dagegen: `OPENAI_BASE_URL=<endpoint>/v1`,
`OPENAI_API_KEY=dummy`, `RQGM_GRADER_MODEL=<id>`, `use_schema=True`.

## 2. Compare-Beleg (5 IMO-Grading-Items, Human: Incorrect/Partial/Partial/Almost/Almost)

```text
qwen3:14b   use_schema=False: Fallbacks 1/5   Klassen [Correct,Correct,Incorrect,Correct,Correct]
qwen3:14b   use_schema=True : Fallbacks 0/5   Klassen [Correct,Correct,Correct,Correct,Correct]
qwen2.5:14b use_schema=False: Fallbacks 0/5   Klassen [Correct,Correct,Correct,Correct,Correct]  (27 s)
qwen2.5:14b use_schema=True : Fallbacks 0/5   Klassen [Correct,Correct,Correct,Correct,Correct]  (7 s)
```

**JSON-Problem GELÖST:** `json_schema`/guided decoding am Endpoint → **0/5 Fallbacks**
(vorher 5/5 am NVIDIA-Endpoint). Das war der Zweck von Rekursion 033.

**Genauigkeit NICHT gelöst:** Übereinstimmung **0/5** – beide 14B-Modelle vergeben
fast immer „Correct". Diagnose an Item 1 (Human: **Incorrect**): die Kandidaten-Antwort
behauptet wörtlich *„I have successfully proven the statement"* und ist ein langer,
selbstsicherer (aber fehlerhafter) Beweis; der 14B-Grader **prüft die Mathematik nicht**
und akzeptiert die Behauptung. Ein geschärfter Prompt (Punkteskala 0–7, „nicht
automatisch korrekt", Rubric explizit) änderte das **nicht** (weiter 5× „Correct").

## 3. Schlussfolgerung (ehrlich, §6)

- **JSON**: gelöst (Endpoint + `json_schema`, 0 Fallbacks). Kein weiterer Code nötig.
- **Genauigkeit**: **modelllimitiert**. Für 4-Klassen-IMO-Bewertung braucht es ein
  stärkeres Modell, das Beweise tatsächlich verifiziert (nicht nur Selbstaussagen glaubt):
  **Qwen3-30B-A3B-Instruct** (MoE, 4-bit, 2×T4) oder **gpt-oss-20b** (Structured Outputs).
- **κ bleibt daher NICHT belastbar** – jetzt nicht wegen Fallbacks, sondern wegen
  Grader-Qualität. Die **+9 % des Papers** bleiben NICHT reproduziert.

## 4. Änderungen in diesem Schritt

| Datei | Änderung |
|---|---|
| `data/memory/evaluator_version.py` | Anker speichert `problem`/`response` getrennt; `_class_prompt` mit Punkteskala + Strenge-Hinweis (15+/4−) |
| `tests/test_evaluator_version.py` | unverändert grün (189 Tests) |

**Drift:** 15 eingefügt / 4 entfernt = **19 von 1052 Zeilen = 1,81 %** < 10 % (§9.1c) ✓

## 5. Gate / Freigabe (§9)

- Keine neue Quelle (die Endpoints sind Auftrags-Infrastruktur; json-repair/Structured
  Outputs bereits in 033 belegt). Kein Interface-Bruch (Prompt-Text + additive Felder).
- Tests: **189 passed · 1651/1651 Statements · 360/360 Branches = 100,00 %**.
- §9.3-Freigabe 2026-10-02.

## 6. Nächstes Self-Feedback (t+1)

- Stärkeres Modell laden: **Qwen3-30B-A3B-Instruct (AWQ, 2×T4)** oder **gpt-oss-20b**,
  via vLLM mit `--guided-decoding-backend xgrammar`.
- Dann 5-Item-Smoke (Genauigkeit!) → bei ≥ ~0.5 Übereinstimmung n=90 → κ + BCa-KI.
