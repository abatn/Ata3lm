# Rekursion 102: Kaggle-SFT – Präzisions-Mismatch (bf16-Config vs. fp16-Scaler)

> Datum: 2026-10-10 · Phasen: Konstrukt → Akt → Observe → Compare (echtes Signal:
> Kaggle-Lauf-Traceback).
> Ziel `g` (§2): das Kaggle-SFT-Skript so korrigieren, dass das Training auf der
> **T4** durchläuft (nach dem dtype-Fix aus Rek. 100).
> Quelle (belegt): `Qwen/Qwen2.5-0.5B-Instruct` `config.json` → `torch_dtype=bfloat16`
> (HF, HTTP 200); PyTorch/`torch.amp.GradScaler` (`unscale_`) + `SFTConfig(fp16=…)`.
> Status: **approved** (Auftrag Batnini, 2026-10-10; keine Interface-Änderung).

## 1. Anlass (echter Lauf)

Nach Rek. 100 lief das Training an, brach aber im ersten Optimizer-Schritt ab:

```
NotImplementedError: "_amp_foreach_non_finite_check_and_unscale_cuda"
not implemented for 'BFloat16'
  ... torch/amp/grad_scaler.py:358 unscale_ ...
```

## 2. Ursache (belegt)

- Rek. 100 wählt auf der T4 `compute_dtype = fp16` (CC 7.5 < 8.0) ⇒ `SFTConfig(fp16=True)`
  ⇒ **fp16-`GradScaler`**.
- Das Skript lud das Modell **ohne** `dtype`. `Qwen/Qwen2.5-0.5B-Instruct` hat aber
  `torch_dtype=bfloat16` (verifiziert in `config.json`) → die nicht-quantisierten Teile
  **und die LoRA-Adapter** wurden **bf16**.
- Folge: **bf16-Grads** treffen auf den **fp16-Scaler** (`unscale_`) → der obige Fehler.
  (Kein Netz-/Fake-Problem — reine Präzisions-Inkonsistenz.)

## 3. Fix (`kaggle/train_slow_consolidation.py`)

```diff
-    model = AutoModelForCausalLM.from_pretrained(
-        BASE_MODEL, quantization_config=bnb_config, device_map="auto", token=hf_token)
+    # Einzel-Praezision erzwingen (belegt: Basis-Config ist bf16 -> sonst bf16-Grads
+    # gegen fp16-Scaler). Version-sicher: v5 `dtype`, aeltere `torch_dtype`.
+    import inspect
+    _load_kwargs = {"quantization_config": bnb_config, "device_map": "auto", "token": hf_token}
+    _dtype_key = "dtype" if "dtype" in inspect.signature(
+        AutoModelForCausalLM.from_pretrained).parameters else "torch_dtype"
+    _load_kwargs[_dtype_key] = compute_dtype
+    model = AutoModelForCausalLM.from_pretrained(BASE_MODEL, **_load_kwargs)
```

- Alles einheitlich **fp16** auf der T4 (Modell + LoRA + bnb-Compute + Scaler).
- `model_dtype_key` wird als Evidenz ins `kaggle_output.json` geschrieben (§9.1d).
- `train_slow_consolidation.ipynb` synchron nachgezogen (ruff-formatiert).

## 4. Verifikation (echt)

- `python -c ast.parse(...)`: Syntax ok.
- `ruff check .` + `ruff format --check .`: **grün** (116 Dateien).
- `tests/test_kaggle_train_cli.py`: **3 passed** (CLI unverändert).
- (Der Trainingslauf selbst wird auf Kaggle vom Menschen ausgeführt — Status
  bleibt `Auftrag/unverifiziert-lokal`.)

## 5. §9-Gate

- Keine neue Quelle, kein `self_update`, Interface stabil ⇒ kein Human-Gate nötig
  (Freigabe dennoch dokumentiert). Guardrail 6: Commit/Push nach Erlaubnis.

## 6. Ehrlicher Caveat

- Der Fix **erzwingt** fp16 statt bf16; auf Ampere+ (CC ≥ 8.0) bleibt bf16 aktiv
  (dort ist der Mismatch nicht zu erwarten, da kein fp16-Scaler).
- Ob der Trainingslauf konvergiert, bestätigt erst der Kaggle-Lauf + Rückfluss (M1).
