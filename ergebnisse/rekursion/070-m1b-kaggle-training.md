# Rekursion 070: M1b — Kaggle-Trainingscode (Slow Consolidation, Θ→Θ′)

> Datum: 2026-10-07 · Phasen: Akt (Konstrukt → Handeln).
> Ziel `g`: Ein **in sich geschlossener** Kaggle-Trainingscode entsteht, den der
> Mensch auf Kaggle (GPU) ausführt, um das aus **M1** erzeugte SFT-Dataset
> (`consolidation_sft.jsonl`, Chat-Format) real zu trainieren (QLoRA, Θ→Θ′).
> Status: **Auftrag / unverifiziert-lokal** (keine lokale GPU, ML-Libs nicht
> installiert). Kein Fake-Erfolg (G7). Kein Git (G6).

## 1. Quellen / Gesetz

- `AGENTS.md` §10.3 (Write-Back / Slow Consolidation), §10.5 (belegte Wirkung),
  §6 (keine Erfindungen), Guardrail 3 (Provenienz), G6 (kein Git), G7 (echte Verifikation).
- `connectors/fast-write-routing.md`, `knowledge/lifecycle/wissen-plus.md` §10.
- Paper: arXiv:2608.22215 §3.4 (Slow Consolidation); QLoRA arXiv:2305.14314;
  LoRA arXiv:2106.09685.

## 2. Änderung (neu angelegt, additiv)

| Datei | Inhalt |
|---|---|
| `kaggle/train_slow_consolidation.py` | Kanonischer Trainingscode: Dataset-Load (Chat/ShareGPT/prompt+response), HF-Basismodell, QLoRA via peft+trl+bitsandbytes+datasets, Adapter → `adapter/`, `kaggle_output.json` (Modell, Adapter-Pfad, Loss, Datensatz-Hash, Seed). |
| `kaggle/train_slow_consolidation.ipynb` | Kaggle-Notebook, aus der `.py` generiert (identische Logik). |
| `kaggle/README.md` | Kaggle-Schritte, verifizierte IDs/Libs, Rückgabe-Weg, Status-Caveat. |
| `ergebnisse/rekursion/070-m1b-kaggle-training.md` | Dieses Dokument (Provenienz). |

Kein Löschen, keine Interface-Änderung an bestehenden Modulen. Keine
`AGENTS.md`- oder `tier1-base`-Änderung (kein `approved` nötig für additive Dateien).

## 3. Verifikation (externes Signal, real ausgeführt)

Am **2026-10-07** live geprüft (HTTP 200):

```text
HF-API  https://huggingface.co/api/models/Qwen/Qwen2.5-0.5B-Instruct        200
HF-API  https://huggingface.co/api/models/google/gemma-2-2b-it              200 (gated=manual)
HF-API  https://huggingface.co/api/models/meta-llama/Llama-3.2-1B-Instruct  200 (gated=manual)
PyPI    transformers 5.19.0 · peft 0.21.2 · trl 1.14.2 · bitsandbytes 0.50.2
        datasets 5.1.0 · accelerate 1.15.0                                      200
TRL v1.14.2 Quelltext: SFTConfig(max_length), dataset_text_field,
        processing_class, "messages"-Format (raw.githubusercontent.com)        200
```

Lokal real ausgeführt (ohne GPU): `py_compile` OK, `ruff check` + `ruff format`
clean, `normalize_messages` gegen echte Chat-/ShareGPT-/prompt+response-Records,
`sha256_file` (64 hex). **NICHT** ausgeführt: echtes Training (keine GPU) →
deshalb **kein** „belegt", sondern `Auftrag/unverifiziert-lokal`.

## 4. Compare / Abnahme (offen, Mensch)

- Abnahme erst nach Rückgabe aus Kaggle: `kaggle_output.json` + Adapter-Link
  (Kaggle Dataset/Model-URL). Score = erfüllte Prüfungen / Gesamt (Auftrag):
  1. Datei existiert & JSON valide · 2. `base_model` = verifizierte ID ·
  3. `dataset_hash_sha256` = Hash des M1-Datasets · 4. `loss` berichtet ·
  5. Adapter-Link abrufbar. Bis dahin **offen**.

## 5. Status

`Auftrag/unverifiziert-lokal` — Handeln (Stufe 7) vorläufig; kein Lernen an
Originaldateien; Human-Gate (§9) bleibt unberührt. Kein Git.
