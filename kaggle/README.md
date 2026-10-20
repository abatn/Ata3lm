# M1b — Kaggle-Training: Slow Consolidation (Write-Back, Θ → Θ′)

> **Status: `Auftrag / unverifiziert-lokal`.**
> Dieser Code ist **hier NICHT ausführbar** — auf dem Entwicklungsrechner gibt es
> **keine GPU** und die ML-Bibliotheken (`transformers`, `peft`, `trl`,
> `bitsandbytes`) sind lokal **nicht installiert**. Es wird **kein Fake-Erfolg**
> behauptet. Das Training läuft real auf **Kaggle (GPU)** durch den Menschen.
>
> Verfahrens-Quelle: `AGENTS.md` **§10.3** (Write-Back / Slow Consolidation),
> `connectors/fast-write-routing.md`, Paper **arXiv:2608.22215 §3.4**.
> Datenquelle: **M1** liefert `consolidation_sft.jsonl` (Chat-Format).

## Dateien

| Datei | Zweck |
|---|---|
| `train_slow_consolidation.py` | Kanonischer, in sich geschlossener Trainingscode (Single Source of Truth). |
| `train_slow_consolidation.ipynb` | Kaggle-Notebook (aus der `.py` generiert, identische Logik) — empfohlen zum Ausführen. |
| `m1_m2_m3_probe.py` | **Read-only**-Messskript (Diagnose M1/M1b/M1c/M2/M3 + Canary, **kein** Training/Write-Back) — siehe „V2" unten. |
| `m1_m2_m3_preregistration.md` | Prä-registrierte Regeln/Schwellen für den Messlauf (Amendment A1) — vor dem Lauf fixiert. |
| `README.md` | Diese Anleitung. |

Was das Skript tut: lädt ein SFT-Dataset (siehe `SFT_SOURCE`), lädt ein **reales**
kleines Basis-Modell von HuggingFace, trainiert **QLoRA** (4-bit + LoRA) via `peft` +
`trl`, speichert den Adapter nach `adapter/` und schreibt `kaggle_output.json`
(Basis-Modell, Adapter-Pfad, Loss, `sft_source`, Datensatz-Hash `sha256`,
Zeilen-Hash-Aggregat, Seed, Lib-Versionen, GPU).

## Datenquellen (`SFT_SOURCE`, klar gekennzeichnet)

| `SFT_SOURCE` | Bedeutung | Daten | Internet? |
|---|---|---|---|
| `local` (**Default**) | M1-JSONL aus `data/memory/slow_consolidation.py` | `consolidation_sft.jsonl` (Kaggle-Input) | nein |
| `zsre` | **§10.3-Konsolidierungskorpus** (offizieller ZsRE-Benchmark) | HF `community-datasets/qa_zre` (Streaming, `ZSRE_N` Fakten) | **ja** |
| `capybara` | **Demo** — NICHT der §10.3-Korpus | HF `LDJnr/Capybara` (Streaming, `CAPYBARA_N`) | **ja** |

Verifizierte Quellen (real geprüft, **HTTP 200**, 2026-10-07):

| Gegenstand | Referenz | Link |
|---|---|---|
| Paper (Fakten aus ZsRE; write-back = (q,a) + sentence-level SFT) | arXiv:2608.22215v2 §3.4 + A.1 | <https://arxiv.org/html/2608.22215v2> |
| ZsRE-Dataset (8,4 M train; `relation, question, subject, context, answers`) | `community-datasets/qa_zre` | <https://huggingface.co/api/datasets/community-datasets/qa_zre> |
| ZsRE-Ursprung | Levy et al. 2017 (CoNLL) | <https://aclanthology.org/K17-1034/> |
| Demo (`source`, `conversation=[{input,output}]`, 16 006 train) | `LDJnr/Capybara` | <https://huggingface.co/api/datasets/LDJnr/Capybara> |
| Chat-JSONL-Format | TRL dataset formats | <https://huggingface.co/docs/trl/dataset_formats> |

**§9-Status (`zsre`):** `community-datasets/qa_zre` ist eine **neue Quelle** und steht
**nicht** in der Ontologie ⇒ **Human-Gate `ask`** (nicht vorab freigegeben).
Der Generator ist `data/memory/zsre_corpus.py::build_zsre_corpus`; Test:
`tests/test_zsre_corpus.py`. Ehrlich: volle Menge verfügbar, hier gesampeltes `n`.

Umgebungsvariablen: `SFT_SOURCE` (`zsre`/`local`/`capybara`), `ZSRE_N` (10000),
`ZSRE_SPLIT` (train), `ZSRE_DATASET`, `CAPYBARA_N` (10000), `CAPYBARA_SPLIT` (train).

### Erwartetes M1-Format (Chat, `SFT_SOURCE=local`)

`data/memory/slow_consolidation.py::build_sft_dataset` (M1) schreibt je Zeile
(z. B. nach `consolidation_sft.jsonl`):

```json
{"messages": [{"role": "user", "content": "<Frage>"},
              {"role": "assistant", "content": "<Fakt>"}],
 "hash": "<sha256 der kanonischen messages>", "key": "...", "class": "write-new", "sha256": "..."}
```

Das Skript liest `messages` (und ignoriert `hash`/`key`/`class`/`sha256` fürs
Training), aggregiert aber vorhandene `hash`-Werte zu
`dataset_row_hash_aggregate_sha256` — so ist der Adapter an M1s **Inhalt-Hashes**
(§6, `provenance.content_hash`) gebunden. Alternativ akzeptiert der Loader
ShareGPT (`conversations`/`from`+`value`) und `prompt`+`response`.

### Rückfluss in M1 (nach Kaggle)

Nach Rückgabe des Adapters schließt M1 den Kreis: `mark_consolidated(keys,
success=True)` verbucht die konsolidierten Keys, `flush(...)` entfernt die Fakten
aus dem externen Puffer (`tier3`). `success=False` (Training fehlgeschlagen) ⇒ kein
Flush (§10.3). M1s `write_back(...)` bleibt ein ehrlicher Stub
(`NotImplementedError`), weil das Training **hier** (Kaggle) läuft.

## Verifizierte Modell-IDs (HF-API, HTTP 200)

Vor Nutzung geprüft am **2026-10-07** via `https://huggingface.co/api/models/<id>`:

| Modell-ID | HTTP | Gated | Pipeline | Link |
|---|---|---|---|---|
| `Qwen/Qwen2.5-0.5B-Instruct` (**Default**) | 200 | nein | text-generation | <https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct> |
| `google/gemma-2-2b-it` (Alternative) | 200 | **manual** (HF-Login/Token nötig) | text-generation | <https://huggingface.co/google/gemma-2-2b-it> |
| `meta-llama/Llama-3.2-1B-Instruct` (Alternative) | 200 | **manual** | text-generation | <https://huggingface.co/meta-llama/Llama-3.2-1B-Instruct> |

Default-`revision` (sha) von Qwen2.5-0.5B-Instruct: `7ae557604adf67be50417f59c2c2f167def9a775`.
Andere Basis-Modelle per Umgebungsvariable `BASE_MODEL=<id>` wählbar.

## Verifizierte Bibliotheken (PyPI, HTTP 200)

Geprüft am **2026-10-07** via `https://pypi.org/pypi/<name>/json`; im Notebook/Cell 1 gepinnt:

| Bibliothek | Version | Link |
|---|---|---|
| `transformers` | 5.19.0 | <https://pypi.org/project/transformers/> |
| `peft` | 0.21.2 | <https://pypi.org/project/peft/> |
| `trl` | 1.14.2 | <https://pypi.org/project/trl/> |
| `bitsandbytes` | 0.50.2 | <https://pypi.org/project/bitsandbytes/> |
| `datasets` | 5.1.0 | <https://pypi.org/project/datasets/> |
| `accelerate` | 1.15.0 | <https://pypi.org/project/accelerate/> |

Kompatibilität (`trl==1.14.2` verlangt `transformers>=4.56.2`, `datasets>=4.7.0`,
`accelerate>=1.4.0`, `peft>=0.13.0`) und die verwendete TRL-API
(`SFTConfig(max_length=...)`, `dataset_text_field`, `processing_class`, `messages`-Format)
wurden am Tag der Erstellung im TRL-Quelltext `v1.14.2` geprüft.

**Achtung – Laufzeitversionen ≠ Notebook-Pins (Audit e2e-699dda4):** Der
veröffentlichte Kaggle-Lauf (HF `Batnini/knowledge-agent-sft-lora`, `kaggle_output.json`)
wurde mit `!python …train_slow_consolidation.py` **direkt** ausgeführt (nicht über die
Notebook-Zelle 1) und nutzte daher **Kaggle-Default-Versionen**:
`transformers 5.16.1`, `peft 0.20.0`, `trl 1.15.0`, `datasets 4.8.5`,
`accelerate 1.14.0`, `bitsandbytes 0.50.2`. Wer die **Pins** (Tabelle oben)
reproduzieren will, muss über die Notebook-Zelle 1 installieren (oder diese
Versionen vorab setzen). Der Lauf-Erfolg belegt damit **seine** Umgebung, nicht
automatisch einen Notebookstart mit den Pins.

## Kaggle-Schritte (exakt)

1. **Kaggle-Account**: <https://www.kaggle.com> → einloggen (verifizierte Handynummer
   ist für GPU/Internet nötig).
2. **GPU aktivieren**: Notebook öffnen → *Settings → Accelerator* → **GPU T4 x1**
   (oder P100). `bf16`-fähige GPU (L4/A100) ist optional; auf T4/P100 schaltet das
   Skript automatisch auf `fp16`.
3. **Dataset hochladen** (aus M1): `consolidation_sft.jsonl` als Kaggle-Dataset
   hochladen (*Datasets → New Dataset*), z. B. Slug `<dein-name>/consolidation-sft`.
   Das Skript findet die Datei automatisch unter `/kaggle/input/**/consolidation_sft.jsonl`;
   alternativ `SFT_DATASET_PATH` setzen.
4. **Notebook ausführen**: `train_slow_consolidation.ipynb` als Kaggle-Notebook
   anlegen (oder importieren), links unter *Input* das Dataset hinzufügen,
   alle Zellen ausführen. Cell 1 installiert die gepinnten Versionen;
   die letzte Zelle ruft `main()` auf.
   - Für `google/gemma-2-2b-it` oder `meta-llama/*`: *Add-ons → Secrets* →
     Secret `HF_TOKEN` anlegen (HF-Token) **und** „Internet" aktivieren.
5. **Output erzeugen**: Das Skript legt `/kaggle/working/adapter/` (LoRA-Adapter +
   Tokenizer) und `/kaggle/working/kaggle_output.json` an.
6. **Zurückschicken**: Adapter als Kaggle-Dataset oder Kaggle-Model veröffentlichen
   (siehe unten) **und** `kaggle_output.json` übergeben. Kein Git (G6).

Aufruf auf Kaggle (Alternativ zum Notebook) – CLI **oder** ENV:

```bash
# CLI (empfohlen): --dataset/--out/--source/--gpu/--epochs
python train_slow_consolidation.py \
    --dataset /kaggle/working/train_f6.jsonl --out /kaggle/working \
    --source local --gpu 0 --epochs 3

# ENV-Alternative (CLI ueberschreibt ENV)
SFT_SOURCE=local SFT_DATASET_PATH=/kaggle/working/train_f6.jsonl \
  OUTPUT_DIR=/kaggle/working CUDA_VISIBLE_DEVICES=0 \
  python train_slow_consolidation.py
```

Nützliche Umgebungsvariablen: `BASE_MODEL`, `SFT_DATASET_PATH`, `OUTPUT_DIR`,
`NUM_EPOCHS` (Default 3), `MAX_LENGTH` (Default 1024), `PER_DEVICE_BATCH` (4),
`GRAD_ACCUM` (4), `LEARNING_RATE` (2e-4), `LORA_R` (16), `LORA_ALPHA` (32),
`SEED` (42), `HF_TOKEN`.

Hinweis (belegt): `bf16`-Mathematik braucht Compute Capability ≥ 8.0 (Ampere+). Auf
**T4 (sm_75)** wählt das Skript automatisch **fp16**
(`torch.cuda.get_device_capability`), sonst bricht der TRL-Fused-Kernel ab
(„gemm input type at::BFloat16 and output type float … 8.0 or higher").
Zwei sichtbare GPUs ⇒ `--gpu 0` (bzw. `CUDA_VISIBLE_DEVICES=0`), sonst `SFTTrainer`
+ `DataParallel` = Fehler.

## Was der Mensch zurückschickt

Eines der beiden (bevorzugt beides):

1. **Adapter-Link**: Kaggle-Dataset- oder Kaggle-Model-URL, die `adapter/`
   (`adapter_config.json`, `adapter_model.safetensors`, Tokenizer-Dateien) enthält —
   z. B. `https://www.kaggle.com/datasets/<user>/<slug>` oder
   `https://www.kaggle.com/models/<user>/<slug>`.
2. **`kaggle_output.json`** (Datei oder Inhalt): Basis-Modell, Adapter-Pfad, Loss,
   Datensatz-Hash (`sha256`), Seed, Bibliotheks-Versionen, GPU.

Damit ist das Ergebnis **extern verifizierbar** (§6): `dataset_hash_sha256` bindet den
Adapter an das exakte M1-Dataset, der Loss + Kaggle-Run belegen echtes Training.
Erst nach Rückgabe + Prüfung wird M1b als `belegt` (statt `Auftrag/unverifiziert-lokal`)
geführt.

## Belegte vs. Auftrag (Status-Trennung)

- **Belegt** (Quelle): QLoRA-Verfahren (Dettmers et al., <https://arxiv.org/abs/2305.14314>),
  LoRA (Hu et al., <https://arxiv.org/abs/2106.09685>), Slow Consolidation / Write-Back
  (arXiv:2608.22215 §3.4), Existenz der Modell-/Lib-IDs (HTTP 200, siehe Tabellen).
- **Auftrag** (Projekt): konkrete Hyperparameter, Adapter-Ausgabeformat,
  Rückgabe-Weg, `kaggle_output.json`-Felder.

## Ehrlicher Caveat

- Der Code wurde **lokal nicht trainiert getestet** (keine GPU, keine ML-Libs).
  Lokal verifiziert wurden nur Syntax (`py_compile`), Lint (`ruff`) und die
  reinen Python-Helfer (`normalize_messages`, `sha256_file`) über echte JSONL-Daten.
- Das erwartete `consolidation_sft.jsonl` stammt aus **M1** und liegt im Repo
  **noch nicht** vor; das Skript erkennt automatisch Chat-Formate
  (`messages`), ShareGPT (`conversations`/`from`+`value`) und `prompt`+`response`.

## V1 — Geschlossener Write-Back-Zyklus (`write_back_cycle.py`, Ollama lokal)

> **Status: `Auftrag / unverifiziert-lokal`.** Läuft nur auf **Kaggle (GPU)** und
> fährt den **echten** §10.3-Zyklus in einem Lauf:
> reale Fakten → **reale Writes** (§10) → `pending` → **SFT (Θ′)** → **Θ′-Probe**
> → `write_back` (Flush nur bei positivem Probe, fail-closed).

Der Driver nutzt als LLM einen **lokalen Ollama-Endpoint** auf der Kaggle-Maschine —
**kein API-Key, kein Secret**. Default: `http://127.0.0.1:11434/v1`, Modell
`qwen2.5:1.5b` (per `--llm-base-url` / `--llm-model` änderbar). Vorhandene ENV
(`OPENAI_BASE_URL`, `OPENAI_API_KEY`, `FWR_SMALL_MODEL`, `FWR_LARGE_MODEL`,
`HELA_MODEL`) hat **Vorrang**; der Endpoint wird real geprüft (`GET /v1/models`,
`HTTP 200`), sonst bricht das Skript **fail-closed** ab (kein Fake, Guardrail 7).

**Notebook-Zellen (vor dem Driver ausführen):**

```bash
# 0) inkompatibles torchao entfernen (peft v0.20.0 wirft bei torchao<0.16.0;
#    Kaggle liefert 0.10.0 → die LoRA-Injektion der nicht-4-bit Θ′-Probe bricht ab)
!pip uninstall -y torchao
# 1) Ollama installieren
!curl -fsSL https://ollama.com/install.sh | sh
# 2) Server im Hintergrund starten
!nohup ollama serve >/tmp/ollama.log 2>&1 &
# 3) Modell ziehen (einmalig)
!ollama pull qwen2.5:1.5b
```

> **Belegt (Quelle):** peft v0.20.0 `src/peft/import_utils.py::is_torchao_available`
> **raise**t `ImportError`, wenn `torchao < 0.16.0` installiert ist; das Training lief
> nur, weil dort der bnb-4-bit-Dispatcher zuerst greift — die **nicht**-4-bit Θ′-Probe
> erreicht `dispatch_torchao` (Kaggle: `torchao 0.10.0`) und bricht ab.
> Alternative zu Schritt 0: `!pip install -U "torchao>=0.16.0"`. Der Driver prüft
> das vorab und bricht sonst **fail-closed** mit klarer Meldung ab.

**Driver starten** (Repo vorher klonen; **kein Token inline** — Zugang per Kaggle-Secret
oder öffentlichem Clone):

```bash
python kaggle/write_back_cycle.py --n 20 --gpu 0 \
  --approver Batnini --approver Taoufik --workdir /kaggle/working \
  --llm-base-url http://127.0.0.1:11434/v1 --llm-model qwen2.5:1.5b
```

Ergebnis: `/kaggle/working/write_back_cycle_result.json` mit `flushed`/`kept`/`loss`/
`adapter_path` (zuzüglich `llm_base_url`, `llm_model`, `writes`, `pending`). §9.3:
`write-new`/`write-update` werden **nur** mit **≥ 2 distinkten** `--approver`-Namen
geschrieben; sonst bleibt der Write auf `ask` (klar gemeldet, nicht umgangen).

Nützliche Umgebungsvariablen: `OPENAI_BASE_URL`, `FWR_SMALL_MODEL`, `FWR_LARGE_MODEL`,
`HELA_MODEL`, `BASE_MODEL`, `SEED`.

---

## V2 — Read-only-Messlauf M1/M2/M3 (Diagnose, **kein** Training)

Zweck: klären, ob der B2′-Lauf (rsLoRA, r=64/α=256) wirklich **degeneriert** ist
(14/15 „Jamaica") oder ob nur die **Messung** kaputt war (N8-Kontamination:
`write_back_cycle.py:420-421` wrapt die Basis, bevor `:442` misst — der
`base_answer` misst also das Adapter-Modell). Rek 129 (`A1`–`A4`), `A3` bleibt offen.

**Eigenschaften (`m1_m2_m3_probe.py`):**

- **read-only** — kein Training, kein Write-Back, kein `self_update`; schreibt ausschließlich
  `status.json`, `manifest.json`, `per_item.jsonl` in `--out-dir` (+ HF-Cache).
  `write_back_cycle.py` wird **nicht** verwendet (trainiert + schreibt).
- **Reihenfolge fix** (Preregistration `m1_m2_m3_preregistration.md`): `M1` (Basis, unwrapped) →
  `M1_repeat` (Determinismus) → `M1b` (Basis, unwrapped, **Canary-Referenz auf derselben
  Instanz**) → `M2` (B2′) → `canary` (`disable_adapter()`, muss `M1b` item-für-item = 100 %) →
  `M2_repeat` → **Positivkontrolle** (M2 ≠ canary) → `M1c` (Basis) → `M3` (B2).
- **9 prä-registrierte Regeln** (Amendment A1): 1 P-1 deskriptiv · 2 Adapterschaden nicht
  spezifisch rsLoRA · 3 P-3 Base/Prompt/Daten · 4 Adapterschaden auf schwacher Base ·
  5 P-2a (N8) · 6 P-2b (Altlauf-Vergleich) · 7 Adapter hilft · 8 No-op · 9 **Vorbedingung**
  (Canary-Fail/Positivkontrolle-Fail/Determinismus-Fail/Noise>Budget/Degeneration ≥ 12/15/nicht
  zuordenbar) ⇒ `unentschieden`.
- **Fail-closed**: ohne CUDA, ohne `torch`/`peft`, `torchao<0.16`, abweichende SHA-Pins,
  unerwartetes `use_rslora`, `base_model_name_or_path ≠ --base-model` ⇒ `status.json` mit
  `status="nicht ausgefuehrt"` und **ohne** Zahlen.

**Befehl (Kaggle, GPU):**

```bash
python kaggle/m1_m2_m3_probe.py \
  --dataset probe15_questions.jsonl \
  --base-model Qwen/Qwen2.5-3B-Instruct \
  --base-revision <40-hex-commit> \
  --tokenizer-revision <40-hex-commit> \
  --adapter-b2prime /kaggle/working/adapters/b2prime \
  --adapter-b2      /kaggle/working/adapters/b2 \
  --expect-dataset-sha   c0ea0219c6a56b50601f85f211b14b5902d8103a73ecf37059560fe5d74b4328 \
  --expect-b2prime-sha   a595d437f4fcb0c6030840d9e70e7ff6818a5e490943aabe19f00c3dee6ba9c5 \
  --expect-b2-sha        e3be2c8518433696a6aa5b088a43823facc099b20c7beab385e9352ec3023f2e \
  --ref-b2prime-json write_back_cycle_result.json \
  --expect-ref-sha 5a9ed27a19a1881a8d06eab1e150df3eb476baa4979d4da0422acc9b62501304 \
  --expect-probes 15 \
  --repo-root /kaggle/working/knowledge-agent \
  --out-dir /kaggle/working/m1_m2_m3_out
```

Pins: Probe-Set `c0ea0219…` · B2′-Adapter `a595d437…` · B2-Adapter `e3be2c85…` ·
Altlauf-Result-JSON `5a9ed27a…` (**SHA256 der Datei, kein Git-Commit**). Das Repo wird
geklont (`git clone` ⇒ `knowledge-agent/`); `data/memory/acceptance_gate.py` wird für den
fail-closed Grader-Crosscheck gebraucht (`--repo-root`).

> **Ehrlicher Vorbehalt:** der B2′-Lauf pinte **keine** Base-Revision und lief mit ungepinntem
> Tokenizer (`write_back_cycle.py:411`) ⇒ `--base-revision`/`--tokenizer-revision` **müssen**
> dieselbe Auflösung wählen, sonst kann ein abweichendes Chat-Template die Antworten verändern.
> M1/M2/M3 messen **Memorization** der 15 Trainingszeilen (M3 hat das Ceiling 15/15) ⇒
> P-1 (rsLoRA-Überskalierung) vs. P-3 (Basis/Prompt/Daten) ist mit diesem Lauf **nicht**
> trennbar; der kausale Test ist ein kontrollierter Trainings-A/B (§9.1d → §9.3).
