# Rekursion 033: Robuster strukturierter Grader (JSON-Quote)

> Datum: 2026-10-02 · Tiefe: `t=32 → t=33` · Phase: **Observe → Compare → Revise**
> Freigabe: `approved: Batnini, 2026-10-02` (Auftrag „nach AGENTS.md … setze ein").
> Ziel `g`: die κ-Messung aus §10.9 war **fallback-dominiert** (70/90 kein JSON)
> → Grader zuverlässiger machen, damit κ überhaupt interpretierbar wird.

## 1. `(π, I, M)`-Diff

| | vorher | nachher |
|---|---|---|
| π | `make_llm_class_grader` = 1 Call, `json_object`, `_extract_json` | **json-repair + Retry(max_attempts) + Mehrheit(votes) + optional `json_schema`** |
| I | ein ungültiges JSON ⇒ sofort Fallback „Incorrect" | Reparatur/Retry zuerst; Fallback erst nach Erschöpfung |
| M | JSON-Quote n=90: **20/90** valide | Schema-Modus: 2/5 valide (statt 0/5), Retry senkt Fallbacks |

**Drift:** 84 eingefügt / 19 entfernt = **103 von 1041 Zeilen = 9,89 %** < 10 % (§9.1c) ✓

## 2. Umsetzung (Quellen HTTP 200, geprüft 2026-10-02)

| Baustein | Quelle |
|---|---|
| `_repair_json` (json-repair) | https://github.com/mangiucugna/json_repair (PyPI `json-repair`) |
| `json_schema` strict (`_class_schema`) | https://platform.openai.com/docs/guides/structured-outputs |
| Server-Structured-Generation | https://docs.nvidia.com/nim/large-language-models/latest/structured-generation.html |
| Retry/Validierung (instructor-Muster) | https://github.com/jxnl/instructor |
| Constrained Decoding (Ausblick) | https://github.com/vllm-project/vllm · https://github.com/mlc-ai/xgrammar |

- `make_llm_class_grader(..., max_attempts=3, votes=1, use_schema=False)`:
  Retry mit strengerem Prompt ab Versuch 2, `json-repair` vor Pydantic,
  Mehrheitsentscheid über `votes` Samples (Gleichstand → Fallback), fail-soft.
- ENV: `RQGM_GRADER_MAX_ATTEMPTS`, `RQGM_GRADER_VOTES`.
- Dependency: `json-repair==0.44.1` (Python-3.9-kompatibel; 0.63.5 braucht >3.9).

## 3. Compare-Beleg (externe Signale)

```text
make test  → 189 passed · 1649/1649 Statements · 360/360 Branches = 100,00 %

Schema-Test (5 Items, max_attempts=1):
  use_schema=False: Fallbacks=5/5  Klassen=['Incorrect'×5]
  use_schema=True : Fallbacks=3/5  Klassen=['Incorrect','Incorrect','Incorrect','Almost','Correct']
  → JSON-Schema (server-erzwungen) verbessert die Quote messbar (0/5 → 2/5 valide)

Robuster n=90-Lauf (json-repair + 3 Retries): 75/90 erreicht, 50 Fallbacks
  → Lauf lief in die Zeitgrenze (3000 s), KEIN finales κ (ehrlich: unvollständig).
```

**Ehrlich:** Der robuste Grader **hilft** (Fallback-Rate 78 % → ~67 % bei 75/90;
Schema 0/5 → 2/5 valide), aber der NVIDIA-Endpoint bleibt mit dem Reasoning-Modell
unzuverlässig. Der **vollständige** Fix ist **server-seitige constrained decoding**
(vLLM/XGrammar/NIM `guided_json`) oder ein **Instruct-/JSON-Modell** – beides ist
nicht Teil dieses Repos. Die **+9 % des Papers** bleiben NICHT reproduziert.

## 4. Gate / Freigabe (§9)

- **Neue Quelle** (json-repair, OpenAI Structured Outputs, NVIDIA NIM): §9 verlangt
  Human-Gate — durch den Auftrag erteilt.
- **Interface-Erweiterung** (`max_attempts`/`votes`/`use_schema`): additiv,
  Defaults unverändert → durch Auftrag freigegeben.
- Drift 9,89 % < 10 % · keine AGENTS.md-Änderung · §9.3-Freigabe 2026-10-02.

## 5. Nächstes Self-Feedback (t+1)

- n=90-Lauf mit `use_schema=True` + `max_attempts=3` erneut (Zeitbudget größer).
- Optional Modellwechsel (`RQGM_GRADER_MODEL` auf ein Instruct-Modell).
- Constrained Decoding nur, wenn ein Endpoint mit `guided_json` verfügbar ist.
