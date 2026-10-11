# Rekursion 109: Geschlossener Write-Back-Zyklus — echter Kaggle-Lauf (belegt)

> Datum: 2026-10-11 · Phasen: Konstrukt → Akt → Observe → Compare (externes Signal: Kaggle-T4 + HuggingFace)
> Ziel g (§2/§10.3): Beweis des geschlossenen Zyklus Sammeln → SFT → Θ′-Probe → Flush.
> Status: approved (Batnini + Taoufik, §9.3) — Artefakt extern verifiziert (HF).

## 1. Anlass / Ziel

Rekursion 108 lieferte den **Driver** (`kaggle/write_back_cycle.py`) für den
geschlossenen Zyklus, aber der Code war bis dahin **noch nicht real gelaufen** —
der Status war ausdrücklich `unverifiziert` (kein `torch`/`peft` lokal; zwei
Nachtrags-Befunde: lokales Ollama, inkompatibles `torchao`). Diese Iteration
dokumentiert den **echten** Lauf auf Kaggle (GPU) und dessen **externen** Beleg
über das HuggingFace-Repo (nicht Fake, nicht skriptet — §7).

Ziel `g`: Beweis, dass die Kette **Sammeln → SFT-Dataset → Training → Θ′-Probe →
Flush** (§10.3) end-to-end mechanisch durchläuft und ein konsistentes,
nachvollziehbares Artefakt produziert.

## 2. Setup (echter Lauf)

- **LLM:** lokales **Ollama** (`llm_base_url=http://127.0.0.1:11434/v1`,
  `llm_model=qwen2.5:1.5b`) — wie in Rek. 108 Nachtrag, kein externes Secret.
- **torchao-Upgrade** auf `>= 0.16` — sonst bricht `peft 0.20.0` in
  `is_torchao_available` ab (Befund Rek. 108 §9).
- **GPU:** `Tesla T4` (`compute_capability=sm_75`), `compute_dtype=float16`,
  `amp="disabled (fp16=False, bf16=False)"`.
- **Basis-Modell:** `Qwen/Qwen2.5-0.5B-Instruct` (LoRA: `lora_r=16`,
  `lora_alpha=32`).
- **Lauf-Parameter:** `n=20`, `seed=42`, `self_update=true`,
  `approvers=[Batnini, Taoufik]` (§9.3, zwei distinkte Personen).

## 3. Ergebnis (aus `write_back_cycle_result.json`)

**Writes (Summe 20):**

| Klasse | Anzahl |
|---|---|
| write-new | 8 |
| write-update | 9 |
| non-write | 1 |
| blocked | 2 |
| error | 0 |

Die **2 `blocked`** = `action="uncertain"`, `gate="ask"`,
`reason="Router uncertain -> Human-Gate (§10.4)"` (Fälle: *Abu Yusuf's place of
employment*; *product of Kargaly*).

**pending = 8** (`pending_keys`):

1. `what-is-the-home-arena-of-fc-kuusysi`
2. `which-is-the-cause-of-death-of-christopher-george`
3. `which-is-the-cause-of-death-of-colin-cramphorn`
4. `which-industry-is-msnbc-associated-with`
5. `who-was-in-charge-of-krak-w`
6. `who-was-in-charge-of-sopoaga-ministry`
7. `what-was-the-cause-of-death-for-mark-bernes`
8. `what-cause-of-death-was-listed-for-vedat-dalokay`

**Flush-Ergebnis:**

- `flushed` (2): `which-is-the-cause-of-death-of-christopher-george`,
  `which-industry-is-msnbc-associated-with`.
- `kept` (6): die übrigen sechs pending-Keys.

**Training / Pfade:**

| Feld | Wert |
|---|---|
| `loss` | `4.2931467692057295` |
| `adapter_path` | `/kaggle/working/slow_consolidation_train/adapter` |
| `dataset` | `/kaggle/working/consolidation_sft.jsonl` |
| `provenance_log` | `/kaggle/working/tier3/provenance.jsonl` |

**zsre-Validierung:** `{ok:true, path:/kaggle/working/zsre_validation.jsonl,
count:20, requested:20, split:"validation",
dataset:"community-datasets/qa_zre", rows_scanned:45, skipped_empty:25,
note:"volle Menge aus Quelle verfuegbar; hier gesampeltes n"}`.

**SFT-Hyperparameter / Umgebung (`kaggle_output.json`):**

| Feld | Wert |
|---|---|
| `dataset_rows` | 8 |
| `dataset_row_hash_count` | 8 |
| `dataset_hash_sha256` | `981a984e09bef2a305a6da19b592b54c2822ac0469d9f307825bae94d97f5ecf` |
| `dataset_row_hash_aggregate_sha256` | `e46edfbf0ea597bac7fe3d5d5c3e4abd56f24684c023c0017ff6e38ba3de4980` |
| `num_train_epochs` | 3.0 |
| `max_length` | 1024 |
| `learning_rate` | 0.0002 |
| `lora_r` / `lora_alpha` | 16 / 32 |
| `compute_dtype` | float16 |
| `amp` | disabled (fp16=False, bf16=False) |
| `compute_capability` | sm_75 |
| `gpu` | Tesla T4 |
| `started_utc` / `finished_utc` | 2026-10-11T10:33:55Z / 2026-10-11T10:34:21Z |
| `python` | 3.13.15 |
| `library_versions` | transformers 5.16.1 · peft 0.20.0 · trl 1.15.0 · bitsandbytes 0.50.2 · datasets 4.8.5 · accelerate 1.14.0 · torch 2.11.0+cu128 |

## 4. Compare (§6 — externes Signal)

**HF-Repo** `Batnini/knowledge-agent-write-back`, Revision
`c421ba59c2389c8d4a91bc55846799daeb4b226a`, public,
`lastModified 2026-10-11T10:40:37Z`; **beide JSONs gelesen**.

**Dateien auf HF:**
`adapter/` (`adapter_config.json`, `adapter_model.safetensors`, tokenizer),
`adapter/checkpoint-1..3/`, `kaggle_output.json`, `write_back_cycle_result.json`.

**Konsistenz-Checks (nachgerechnet, alle grün):**

- `pending(8) == dataset_rows(8) == dataset_row_hash_count(8)`.
- `flushed(2) + kept(6) == pending(8)`.
- Writes-Summe `8+9+1+2 = 20 == n`.

**Link (Θ′, Beleg-Artefakt):**
<https://huggingface.co/Batnini/knowledge-agent-write-back/tree/main/adapter>

## 5. Bewertung

- **Mechanik: belegt.** Der geschlossene Zyklus (Sammeln → SFT → Θ′-Probe →
  Flush) läuft real durch; pending/Dataset/Row-Hashes und Flush-Bilanz sind
  intern und gegen das HF-Artefakt konsistent (§6 eingehalten).
- **Wirkung: schwach.** `loss = 4.29` ist hoch; nur **2 von 8** Probe-Kandidaten
  wurden **positiv** (⇒ `flushed`), 6 blieben `kept`. Das ist **kein** Beleg für
  Lernerfolg — **kein** „Modell hat gelernt"-Claim (§6).
- **Gate-Verhalten: belegt.** 2 `blocked` mit `gate="ask"` und Grund
  `Router uncertain -> Human-Gate (§10.4)` — die Schranke greift wie
  spezifiziert.

## 6. Ehrlicher Caveat / offen

- **`probe_fn` = Teilstring-Test** — ein **schwaches** Signal. „Positiv" heißt
  hier nur, dass ein Teilstring in der Generation vorkommt; das belegt **keine**
  semantische Korrektheit. Die mageren 2/8 sind entsprechend **vorsichtig** zu
  lesen.
- **`status`-Feld im JSON** ist der **statische Skript-String**
  `"Auftrag/unverifiziert-lokal"` (im Code verdrahtet) — **NICHT** der
  Laufstatus. Die tatsächliche Verifikation kommt **allein** aus dem HF-Artefakt
  (§4).
- **Laufstatus dieser Iteration:** `approved` (Batnini + Taoufik, §9.3) mit
  externem HF-Beleg; **offen** bleiben belastbarere Probe-Metriken (mehr als
  Teilstring) und eine Wirkungsaussage über den SFT-Schritt.

## 7. Quellen (belegt)

- `AGENTS.md` §10.3 (Write-Back / Slow Consolidation), §6 (keine Erfindungen,
  Compare nur mit externem Signal), §9.3 (Zwei-Personen-Verifikation).
- arXiv:2608.22215 §3.4 (Write-Back: erfolgreicher Probe ⇒ Flush, sonst bleibt).
- HF-Repo `Batnini/knowledge-agent-write-back`, sha
  `c421ba59c2389c8d4a91bc55846799daeb4b226a`
  (<https://huggingface.co/Batnini/knowledge-agent-write-back/tree/main/adapter>).
- Lauf-Artefakte: `write_back_cycle_result.json`, `kaggle_output.json`
  (im HF-Repo, gelesen).
