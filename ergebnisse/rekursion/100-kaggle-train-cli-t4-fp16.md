# Rekursion 100: Kaggle-SFT-Skript – echte CLI + T4-gerechtes dtype

> Datum: 2026-10-09 · Phasen: Konstrukt → Akt → Observe → Compare (echtes externes
> Signal: Kaggle-Lauf-Log).
> Ziel `g` (§2): das Kaggle-Trainingsskript (Slow Consolidation, §10.3) so
> korrigieren, dass es auf der **T4** läuft und die CLI-Fehler aus dem echten
> Kaggle-Lauf behoben sind.
> Quellen (belegt): PyTorch-Doku `torch.cuda.is_bf16_supported`
> (<https://docs.pytorch.org/docs/stable/generated/torch.cuda.is_bf16_supported.html>),
> PyTorch-Issue #118122 (sm_75 als bf16-kompatibel gemeldet,
> <https://github.com/pytorch/pytorch/issues/118122>), sglang-PR #34681
> („CUDA: BF16 additionally requires compute capability 8.0+ … FP16 has no such
> restriction", <https://github.com/sgl-project/sglang/pull/34681>).
> Status: **approved** (Auftrag Batnini, 2026-10-09; §9 Interface-Änderung
> additiv → Human-Gate `ask`).

## 1. Anlass (echter Kaggle-Lauf)

Drei Fehler traten real auf:

1. **`--dataset`/`--out` wirkungslos.** Das Skript hatte **kein `argparse`** →
   Argumente wurden ignoriert; `find_dataset()` nahm die montierte
   `consolidation_sft.jsonl` (**4,2 M** Zeilen statt der erwarteten 50 k).
2. **`RuntimeError` im Backward:** `gemm input type at::BFloat16 and output type
   float is only supported for CUDA devices with compute capability 8.0 or higher`
   (`trl/kernels/chunked_logprob.py`).
3. **`SFTTrainer does not support nn.DataParallel`** — Kaggle T4 **×2** sichtbar.

## 2. Ursache (belegt)

- Zeile 315 (alt): `compute_dtype = torch.bfloat16 if torch.cuda.is_bf16_supported()
  else torch.float16`. `is_bf16_supported()` hat Default **`including_emulation=True`**
  → meldet auf **T4 (sm_75, Turing)** `True` (nur emuliert). **bf16-*Mathe*** (GEMM)
  braucht aber **CC ≥ 8.0** → TRL-Fused-Kernel (`addmm` bf16→fp32) bricht ab.
  (Quellen siehe Kopf; fp16 hat hier keine Beschränkung.)
- Ursache (1) + (3): kein `argparse`; zwei GPUs → `DataParallel`.

## 3. Fix (Diff, `kaggle/train_slow_consolidation.py`)

```diff
+import argparse
...
+def parse_args(argv=None):
+    """CLI (optional) – ueberschreibt die ENV-Werte."""
+    ap = argparse.ArgumentParser(...)
+    ap.add_argument("--source", choices=["zsre","local","capybara"], default=None)
+    ap.add_argument("--dataset", default=None)
+    ap.add_argument("--out", default=None)
+    ap.add_argument("--epochs", type=float, default=None)
+    ap.add_argument("--gpu", default=None)
+    return ap.parse_args(argv)
...
-def main():
+def main(argv=None):
+    global SFT_SOURCE, NUM_EPOCHS, OUTPUT_DIR, ADAPTER_DIR, OUTPUT_JSON
+    args = parse_args(argv)  # --gpu vor set_seed (Cuda-Kontext)
...
-    compute_dtype = torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16
+    cc_major, cc_minor = torch.cuda.get_device_capability(0)
+    compute_dtype = torch.bfloat16 if cc_major >= 8 else torch.float16
...
         "compute_dtype": ..., "compute_capability": f"sm_{cc_major}{cc_minor}",
```

- CLI ist **additiv**: ENV bleibt funktionsfähig, CLI überschreibt ENV.
- `kaggle/train_slow_consolidation.ipynb` wurde **synchron** nachgezogen
  (identische Logik, 18 Zellen; `import argparse`, `parse_args`, neues `main`,
  kein `is_bf16_supported()` mehr).
- `kaggle/README.md` dokumentiert CLI + sm_80/T4-Hinweis + „zwei GPUs ⇒ `--gpu 0`".

## 4. Verifikation (echt, Guardrail 7)

- `ruff check` + `ruff format --check`: grün (2 Dateien).
- `tests/test_kaggle_train_cli.py` (neu, offline, kein torch): **3 passed**
  (`--dataset/--out/--source/--gpu/--epochs` gemappt; Defaults `None`; ungültige
  `--source` → `SystemExit`).
- Voller pytest-Lauf **lokal**: **781 passed**, 1 Fail =
  `tests/test_reflective.py::test_distill_mit_llm_real` (externer, flakiger
  LLM-Endpoint – **nicht** durch diese Änderung). `data/memory/zsre_corpus.py`
  bleibt **100 %** (im Offline-Filter fällt es, weil der `live`-Test entfällt).
- Kaggle-Lauf (menschlich): nach dem Fix mussten 50 000 Zeilen korrekt tokenisiert
  werden → bestätigt (ENV-Aufruf + F6-Dataset wirken).

## 5. §9-Gate

- **Interface-Änderung additiv** (neue CLI-Optionen, keine Signatur-Brüche der
  Kerne) ⇒ Human-Gate `ask` → **Freigabe erteilt** (Auftrag Batnini, 2026-10-09).
- Keine neue Quelle (PyTorch/TRL bereits im Projekt); keine `self_update`-Änderung
  an Gesetz-/Memory-Dateien.
- Guardrail 6 (Git-Sperre) beachtet: **kein Commit ohne Erlaubnis**.

## 6. Ehrlicher Caveat

- Das Skript bleibt `unverifiziert-lokal`; die **Korrektheit des gelaufenen
  Trainings** (Loss/Adapter) bestätigt erst der Kaggle-Lauf + Rückfluss (M1).
- Der T4-Fix erzwingt **fp16**; das kann numerisch minimal von bf16 abweichen
  (dokumentiert, kein Paper-Claim).
