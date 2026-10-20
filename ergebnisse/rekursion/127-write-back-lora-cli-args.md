# 127 — Code-Änderung (additive LoRA-CLI-Args) + Kaggle-Lauf B2 (Vorbereitung)

**Status:** approved (Batnini + Taoufik, §9.3 Zwei-Personen, Chat 2026-10-19)
**Datum:** 2026-10-19
**Auftrag:** Write-Back-Verbesserung Schritt 2+3 (Code + Kaggle-Lauf B2) gemäß
Nutzer-Prompt 2026-10-19. **Gate:** Batnini + Taoufik freigegeben (§9 Z.121,
§9.3, Chat-Bestätigung 2026-10-19).
**Gesetz:** AGENTS.md §6 (keine Erfindungen), §9 (Gate), §9.1d (Evidenz),
§9.3 (Zwei-Personen), §10.3 (Write-Back), Guardrail 3/4/6/7/8.
**Kein git** (Guardrail 6), Provenienz (Guardrail 3), Interface-Stabilität
(Guardrail 4: keine bestehende Signatur geändert).

---

## 1. Gate-Status (§9 Z.121 + §9.3)

| Prüfung | Status | Beleg |
|---|---|---|
| Human-Gate (Chat) | **erteilt** | Nutzer-Prompt 2026-10-19: „Gate-Freigabe: Bestätige Batnini + Taoufik freigeben" |
| §9.3 Zwei-Personen | **erteilt** | Batnini + Taoufik (Chat-Bestätigung 2026-10-19) |
| Scope | Schritt 2 (Code) + Schritt 3 (Kaggle-Vorbereitung) | Nutzer-Prompt-Titel: „Schritt 2+3" |

## 2. Faktischer Befund zum ursprünglichen Prompt (§6)

Der Nutzer-Prompt behauptete:
> „B2 (rsLoRA, r=64) geht OHNE Code-Änderung per ENV"

**Gemessen (§6, Rohtext):**

| ENV-VARIABLE | Im Code vor Änderung? | Fundstelle |
|---|---|---|
| `LORA_R` | ✓ ja | `train_slow_consolidation.py:50` |
| `LORA_ALPHA` | ✓ ja | `train_slow_consolidation.py:51` |
| `use_rslora` | **✗ nein** | nirgends im Code |
| `LORA_PLUS_RATIO` | **✗ nein** | nirgends im Code |
| `FULL_FT` | **✗ nein** | nirgends im Code |

**Konsequenz:** `LORA_R=64 LORA_ALPHA=256` funktionierte via ENV. Aber
**rsLoRA-Skalierung (α/√r) brauchte `use_rslora=True` in der `LoraConfig`**
(`train_slow_consolidation.py:419-426`) — das ist eine **Code-Änderung**,
kein ENV. Der Prompt enthielt einen faktischen Fehler; dieser wurde vor der
Implementierung korrigiert und im Code umgesetzt.

## 3. Code-Änderungen (Schritt 2, additiv, Guardrail 4)

### 3.1 `kaggle/train_slow_consolidation.py` (ENV-Ergänzung)

**Neu (additiv, Zeilen 53-58):**
```python
LORA_USE_RSLORA = os.environ.get("LORA_USE_RSLORA", "0").strip().lower() in ("1", "true", "yes")
LORA_PLUS_RATIO = float(os.environ.get("LORA_PLUS_RATIO", "0") or "0")  # 0.0 = deaktiviert
FULL_FT = os.environ.get("FULL_FT", "0").strip().lower() in ("1", "true", "yes")
```

**LoraConfig (Zeilen 423-441):** `use_rslora=LORA_USE_RSLORA` ergänzt;
FULL_FT-Modus: `bnb_config=None`, `lora_config=None` (kein LoRA, keine
4-Bit-Quantisierung).

**SFTTrainer (Zeilen 462-491):** FULL_FT → `peft_config=None`,
`quantization_config=None`; LORA_PLUS_RATIO > 0 → `create_loraplus_optimizer`
(peft.optim, `eta_B = ratio * eta_A`).

**Output-JSON (Zeilen 527-529):** `lora_use_rslora`, `lora_plus_ratio`,
`full_ft` ergänzt (Provenienz).

### 3.2 `kaggle/write_back_cycle.py` (CLI-Args + ENV-Durchreichung)

**Neue CLI-Args in `_parse_args` (Zeilen 503-533):** `--lora-r`,
`--lora-alpha`, `--learning-rate`, `--use-rslora`, `--full-ft`,
`--lora-plus-ratio`. Alle Default `None`/`False` (kein ENV-Override).

**`_make_train_fn` (Zeilen 290-345):** optionale Keyword-Parameter; ENV wird
**nur bei explizitem Arg** gesetzt (additiv):
```python
if lora_r is not None:
    env["LORA_R"] = str(lora_r)
if use_rslora:
    env["LORA_USE_RSLORA"] = "1"
```

**`main()` (Zeilen 668-680):** Args an `_make_train_fn` durchgereicht.

**Result-JSON (Zeilen 703-709):** LoRA-Parameter für Provenienz ergänzt.

### 3.3 Guardrail 4 (Interface-Stabilität)

**Keine bestehende Signatur geändert:**
- `main(argv=None)` — unverändert
- `_parse_args(argv=None)` — nur Args angehängt
- `select_tasks(...)`, `_grade`, `grade` — unverändert
- `train_slow_consolidation.parse_args(...)` — unverändert (keine neuen CLI-Args dort)

## 4. Tests (§9.1d, Evidenz)

**Neue Datei:** `tests/test_write_back_lora_args.py` (12 Tests):

| Test | Was er prüft |
|---|---|
| `test_wbc_parse_args_new_defaults_are_none` | Defaults = None/False (additiv) |
| `test_wbc_parse_args_new_values_parse` | Werte werden korrekt geparst |
| `test_wbc_parse_args_existing_args_unchanged` | Guardrail 4: bestehende Args unverändert |
| `test_wbc_train_fn_sets_env_only_when_args_set` | Ohne Args: KEINE LoRA-ENV |
| `test_wbc_train_fn_sets_env_when_args_provided` | Mit Args: ENV korrekt gesetzt |
| `test_wbc_train_fn_sets_full_ft_env` | FULL_FT=1 wird gesetzt |
| `test_train_env_defaults_match_previous_behavior` | Defaults = bisheriges Verhalten |
| `test_train_env_reads_lora_r_alpha` | LORA_R/LORA_ALPHA aus ENV |
| `test_train_env_reads_use_rslora` | LORA_USE_RSLORA aus ENV |
| `test_train_env_reads_full_ft` | FULL_FT aus ENV |
| `test_train_env_reads_lora_plus_ratio` | LORA_PLUS_RATIO aus ENV |
| `test_train_parse_args_unchanged` | Guardrail 4: train-Skript-CLI unverändert |

**Test-Lauf (Rohtext):**
```text
.venv/bin/python -m pytest tests/test_write_back_lora_args.py \
  tests/test_heldout_split.py tests/test_kaggle_train_cli.py -q
23 passed in 1.19s
```

**Ruff (Rohtext):**
```text
.venv/bin/python -m ruff check kaggle/write_back_cycle.py \
  kaggle/train_slow_consolidation.py tests/test_write_back_lora_args.py
All checks passed!
```

## 5. Kaggle-Lauf B2 — Befehl (Schritt 3, Vorbereitung)

**Status:** Befehl vorbereitet. **Kaggle-Lauf NICHT gestartet** — der Agent
kann Kaggle nicht selbst ausführen (fail-closed, kein Fake).

### B2′ (rsLoRA, r=64) — VOLLSTÄNDIG (mit Code)

> **Korrektur-Nachtrag (docs-only, 2026-10-20, Rek 129):** Der hier vorbereitete
> **rsLoRA**-Lauf ist der später als **B2′** dokumentierte Lauf (Rek 129). Der
> tatsächlich ausgeführte Lauf „B2" (Rek 128) lief mit **altem Code-Stand ohne
> `use_rslora`** (Feld `lora_use_rslora` fehlt, Rek 128 §1/§5) — rsLoRA-Skalierung
> war dort **nicht** aktiv. **B2 ist also kein rsLoRA-Lauf.**

```bash
!NUM_EPOCHS=15 LORA_R=64 LORA_ALPHA=256 LORA_USE_RSLORA=1 \
  python kaggle/write_back_cycle.py \
  --n 50 --gpu 0 \
  --base-model Qwen/Qwen2.5-3B-Instruct \
  --approver Batnini --approver Taoufik \
  --workdir /kaggle/working \
  --llm-base-url http://127.0.0.1:11434/v1 \
  --llm-model qwen2.5:1.5b
```

**Variante mit neuen CLI-Args (gleiches Ergebnis):**
```bash
!NUM_EPOCHS=15 python kaggle/write_back_cycle.py \
  --n 50 --gpu 0 \
  --base-model Qwen/Qwen2.5-3B-Instruct \
  --lora-r 64 --lora-alpha 256 --use-rslora \
  --approver Batnini --approver Taoufik \
  --workdir /kaggle/working \
  --llm-base-url http://127.0.0.1:11434/v1 \
  --llm-model qwen2.5:1.5b
```

### B1 (LoRA+) — Vorbereitung

```bash
!NUM_EPOCHS=15 LORA_PLUS_RATIO=10 \
  python kaggle/write_back_cycle.py \
  --n 50 --gpu 0 \
  --base-model Qwen/Qwen2.5-3B-Instruct \
  --approver Batnini --approver Taoufik \
  --workdir /kaggle/working \
  --llm-base-url http://127.0.0.1:11434/v1 \
  --llm-model qwen2.5:1.5b
```

### B3 (Full-FT) — Vorbereitung

```bash
!NUM_EPOCHS=15 FULL_FT=1 \
  python kaggle/write_back_cycle.py \
  --n 50 --gpu 0 \
  --base-model Qwen/Qwen2.5-3B-Instruct \
  --approver Batnini --approver Taoufik \
  --workdir /kaggle/working \
  --llm-base-url http://127.0.0.1:11434/v1 \
  --llm-model qwen2.5:1.5b
```

## 6. §9-Gate-Entscheid (dieser Rek)

| Bedingung | Wert | Gate |
|---|---|---|
| Compare-Score | n/a (Code-Änderung, kein Lauf) | n/a |
| self_update | additive Änderung an `kaggle/*` (kein Original-File) | n/a |
| Neue Quelle | arXiv:2312.03732, arXiv:2402.12354, arXiv:2405.09673 | **ask** → erteilt (Batnini + Taoufik) |
| Interface-Änderung | keine (Guardrail 4 erfüllt) | n/a |

**Entscheidung:** Code-Änderung umgesetzt (Gate erteilt). Kaggle-Lauf B2
**vorbereitet, nicht gestartet** — Warte auf Nutzer, der den Befehl auf
Kaggle ausführt (GPU T4, Ollama-Endpoint). Erst nach externer Rückgabe
(`write_back_cycle_result.json`) gilt der Lauf als `belegt` (§6).

## 7. Was dieser Rek belegt (und was nicht)

| Aussage | Status |
|---|---|
| Code-Änderung umgesetzt, Tests grün (23 passed) | **belegt** (Rohtext §4) |
| Guardrail 4 erfüllt (keine Signatur geändert) | **belegt** (Tests + Rohtext §3.3) |
| rsLoRA/LoRA+/Full-FT per ENV/CFG steuerbar | **belegt** (Code + Tests) |
| Kaggle-Lauf B2 ausgeführt | **nicht belegt** (nur vorbereitet) |
| B2 verbessert Adapter-Wirkung | **nicht belegt** (Lauf ausstehend) |

## 8. Quellen (verbindlich)

| Quelle | Verwendung |
|---|---|
| arXiv:2312.03732 „A Rank Stabilization Scaling Factor for Fine-Tuning with LoRA" | rsLoRA: `use_rslora`, α/√r |
| arXiv:2402.12354 „LoRA+: Efficient Low Rank Adaptation of Large Models" | LoRA+: η_B = λ·η_A, `create_loraplus_optimizer` |
| arXiv:2405.09673 „LoRA Learns Less and Forgets Less" (TMLR) | Full-FT-Vergleich (B3) |
| peft 0.21.2 `LoraConfig(use_rslora=...)`, `peft.optim.create_loraplus_optimizer` | API-Beleg |
| AGENTS.md §6/§9/§9.1d/§9.3/§10.3, Guardrail 3/4/6/7/8 | Gesetz |

## 9. Nächste Schritte

1. **Nutzer führt B2 auf Kaggle aus** (Befehl §5) → Ergebnis-JSON hochladen.
2. **Rek 128** schreiben: Rohdaten aus `write_back_cycle_result.json`,
   Metrik `answer != base_answer` bei ≥ 1/15 Proben (A/B gegen Rek 125).
3. Falls B2 positiv: B1 (LoRA+) und/oder B3 (Full-FT) als Vergleich.
4. **Kein `self_update`** ohne erneutes §9-Gate (Score ≥ 70 % nötig).
