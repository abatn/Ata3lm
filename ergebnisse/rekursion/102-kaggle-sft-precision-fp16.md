# Rekursion 102: Kaggle-SFT – offizielles QLoRA-Muster (Präzision/dtype)

> Datum: 2026-10-10 · Phasen: Konstrukt → Akt → Observe → Compare (echtes Signal:
> Kaggle-Lauf-Traceback).
> Ziel `g` (§2): das Kaggle-SFT-Skript so definieren, dass es auf der **T4**
> durchläuft — nach dem **offiziellen** TRL/PEFT-Muster.
> Quellen (belegt):
> - TRL `SFTTrainer`: <https://huggingface.co/docs/trl/main/en/sft_trainer>
>   („pass the kwargs of `from_pretrained()` to `SFTConfig` via `model_init_kwargs`";
>   „If `dtype` is not specified … it defaults to `float32`"; `quantization_config`
>   „Ignored if the model is already instantiated").
> - PEFT `Quantization`: <https://huggingface.co/docs/peft/main/en/developer_guides/quantization>
>   (QLoRA = `BitsAndBytesConfig(load_in_4bit, nf4, …)` + PEFT-Adapter).
> - HF-PR #39782 („Use `dtype` instead of `torch_dtype`"), vLLM-Issue #54187
>   (`torch_dtype` deprecated seit transformers 4.56).
> Status: **approved** (Auftrag Batnini, 2026-10-10).

## 1. Anlass (echter Lauf)

`trainer.train()` brach im ersten Schritt ab:
```
NotImplementedError: "_amp_foreach_non_finite_check_and_unscale_cuda"
not implemented for 'BFloat16'
  ... torch/amp/grad_scaler.py unscale_ ...
```
(Log-Warnung: `` `torch_dtype` is deprecated! Use `dtype` instead! ``)

## 2. Ursache (belegt)

- **transformers v5** (Notebook-Pin `==5.19.0`): Default-`dtype` = `auto` ⇒ das Modell
  erbt den **Config-dtype = bf16** (`Qwen2.5` `config.json` `torch_dtype=bfloat16`).
- Das Skript **lud das Modell selbst** ⇒ TRL ignoriert `model_init_kwargs`
  (`quantization_config`/`model_init_kwargs` gelten nur, wenn TRL lädt).
- Mein voriger Versuch mit `torch_dtype=` ist seit 4.56 **deprecated** und bewirkt in v5
  **nicht** die Umstellung ⇒ LoRA/Grads bleiben **bf16**, aber `SFTConfig(fp16=True)`
  erzeugt einen **fp16-GradScaler** ⇒ `unscale_` auf bf16 → Crash.
- **AGENTS.md-Verstoß (ehrlich):** ich änderte **ohne** die Ziel-Umgebung vorher zu
  beobachten ⇒ **Prinzip 1** + **Guardrail 5** (kein Handeln ohne Beobachten),
  **§6/Guardrail 2** (kein Compare ohne externes Signal), **§9.1d** (Evidenz).

## 3. Fix = offizielles TRL/PEFT-Muster (`kaggle/train_slow_consolidation.py`)

```diff
-    from peft import LoraConfig, prepare_model_for_kbit_training
-    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
+    from peft import LoraConfig
+    from transformers import AutoTokenizer, BitsAndBytesConfig
...
-    model = AutoModelForCausalLM.from_pretrained(BASE_MODEL, ..., torch_dtype/dtype=...)
-    model = prepare_model_for_kbit_training(model, ...)
-    lora_config = LoraConfig(..., target_modules=pick_target_modules(model))
+    bnb_config = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4",
+                                    bnb_4bit_use_double_quant=True,
+                                    bnb_4bit_compute_dtype=compute_dtype)
+    model_init_kwargs = {"dtype": compute_dtype}          # v5: dtype (T4 => fp16)
+    lora_config = LoraConfig(..., target_modules="all-linear")  # QLoRA-Stil
...
     trainer = SFTTrainer(
-        model=model,
+        model=BASE_MODEL,                # String -> TRL lädt mit model_init_kwargs
         args=sft_args,                   # SFTConfig(..., model_init_kwargs=model_init_kwargs)
         train_dataset=dataset,
         peft_config=lora_config,
+        quantization_config=bnb_config,
         processing_class=tokenizer,
     )
```

- Damit lädt **TRL** das Modell in **fp16** (T4) → Grads fp16 → GradScaler passt.
- `pick_target_modules` entfällt (String-Modell); QLoRA nutzt `"all-linear"`.
- Evidenz: `model_init_dtype` statt `model_dtype_key`.

## 4. Verifikation

- `python -c ast.parse(...)`: Syntax ok.
- `ruff check .` + `ruff format --check .`: **grün** (116 Dateien).
- `tests/test_kaggle_train_cli.py`: **3 passed**.
- **Ehrlich:** GPU-Beweis nur auf Kaggle (lokal keine GPU) — als Hypothese
  gekennzeichnet; bei erneutem Fehler: **Stopp + Rollback**.

## 5. §9-Gate

- Keine neue Quelle (TRL/PEFT already Projekt), kein `self_update`, Interface stabil.
- Guardrail 6 (Git): Commit/Push nur nach Erlaubnis.

## 6. Ehrlicher Caveat

- `all-linear` bindet mehr Layer als zuvor (Qwen: q/k/v/o/gate/up/down) — gewollt
  (QLoRA-Stil), kann minimal mehr Speicher brauchen.
- Ob das Training konvergiert, bestätigt erst der Kaggle-Lauf + Rückfluss (M1).
