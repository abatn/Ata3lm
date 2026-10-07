# Rekursion 071: M1 — Slow Consolidation Vorarbeit (§10.3)

> Datum: 2026-10-07 · Phasen: Konstrukt → Akt → Observe → Compare (Test).
> Ziel `g`: Die **Vorarbeit** für Slow Consolidation (Write-Back, Θ→Θ′) real
> bereitstellen: konsolidierbare Fakten aus dem externen Puffer sammeln, ein
> SFT-Dataset (Chat-Format) bauen, Erfolg verbuchen und den Puffer flushen.
> Das **eigentliche Θ→Θ′-Training läuft auf Kaggle** (M1b, Rekursion 070) —
> hier nur Sammeln/Formatieren/Verbuchen/Flush. Status: `pending` (Mensch-Gate §9).

## 1. Quellen / Gesetz

- `AGENTS.md` §10.3 (Write-Back / Slow Consolidation), §10.7 (write-new /
  write-update), §9.2c (trusted/verified), §9 (Interface-Freigabe).
- Paper (Belegt): **arXiv:2608.22215** §3.4 — <https://arxiv.org/abs/2608.22215>
  („erfolgreich ⇒ Flush, sonst bleibt"; externer Speicher ~32 % nach Write-Back).
- Kaggle-Teil: Rekursion `070-m1b-kaggle-training.md` (QLoRA, Θ→Θ′).

## 2. Änderung (additiv)

| Datei | Inhalt |
|---|---|
| `data/memory/slow_consolidation.py` (neu) | `collect_pending(tier3_dir, provenance_log, *, state_path=None, questions=None)` · `build_sft_dataset(pending, out_path)` · `mark_consolidated(keys, state_path, *, success=True)` · `flush(keys, tier3_dir, *, state_path=None)` · `write_back(...)` (**Kaggle-Stub**). |
| `data/memory/recursion_runner.py` | Neuer optionaler Parameter `consolidation_state_path` (Hook, lesend). |
| `data/memory/lifecycle_runner.py` | Neuer optionaler Parameter `consolidation_state_path` (Hook, lesend). |
| `tests/test_slow_consolidation.py` (neu) | 12 echte Tests (Dateisystem + echte PROV-O-Records). |

**Interface-Änderung (§9-pflichtig, kenntlich gemacht):** die neuen Funktionen und
die neuen optionalen Runner-Parameter sind im Docstring als §9-pflichtig markiert
und **nicht selbst freigegeben** (`pending`). Keine bestehende Signatur gebrochen
(alle neuen Parameter optional, Default `None` ⇒ unverändertes Verhalten).

## 3. Was real ist vs. Kaggle-Stub

- **Real (lokal, ausgeführt):** Sammeln (`collect_pending`), SFT-JSONL inkl.
  Inhalts-Hash je Zeile (`build_sft_dataset`), Verbuchen nur nach Erfolg
  (`mark_consolidated(success=...)`), Flush nur für verbuchte Keys (`flush`),
  optionale Runner-Hooks.
- **Kaggle-Stub (kein Fake):** `write_back(...)` wirft `NotImplementedError`
  („läuft auf Kaggle"). Es wird **kein** Training simuliert.
- **Caveat (ehrlich):** PROV-O bindet Inhalt-Hash + Aktivität, **nicht** den Prompt.
  `collect_pending` rekonstruiert die SFT-Frage aus dem Memory-Key (Slug) bzw. nutzt
  eine übergebene `questions`-Zuordnung; die Fakten (assistant-content) sind real.

## 4. Compare / Beleg (externes Signal: echte Tests)

Am 2026-10-07 real ausgeführt (`.venv/bin/python`, kein Fake):

```text
pytest tests/test_slow_consolidation.py -q --no-cov        -> 12 passed
pytest tests/test_recursion_runner.py tests/test_lifecycle_runner.py
       tests/test_runner_state.py -q --no-cov              -> 58 passed
ruff check data/memory/slow_consolidation.py
           data/memory/recursion_runner.py
           data/memory/lifecycle_runner.py
           tests/test_slow_consolidation.py                -> All checks passed
```

Belegte Wirkung (Paper, nicht hier gemessen): ≤ 68 % redundante Writes reduziert,
QA-EM > 98 %; externer Speicher nach Write-Back ~32 % (arXiv:2608.22215).

## 5. Offene Punkte

1. **Mensch-Gate §9:** neue Interfaces (`slow_consolidation`, Runner-Parameter) → `pending`.
2. **Kaggle (M1b):** reales Θ→Θ′-Training + `kaggle_output.json`/Adapter (Rekursion 070).
3. Der `pending_consolidation`-Hook im Runner ist rein **lesend** (kein Flush im Lauf).

## 6. Status

`pending` — kein `self_update` an Originaldateien, keine `AGENTS.md`-/
`tier1-base`-Änderung. Kein Git (G6). Keine Erfindung (G7): Kaggle-Training ist
als Stub gekennzeichnet, Zahlen sind echte Testergebnisse.

## 7. Θ→Θ′ real ausgeführt (Kaggle GPU) — Nachtrag 2026-10-07

Der in §6 als „Stub" gekennzeichnete Trainingsschritt wurde **real** auf Kaggle ausgeführt (Tesla T4):

| Feld | Wert |
|---|---|
| Loss | 4.39 → **0.7934** (1000 Steps, 1 Epoche, 53:04) |
| Basis-Modell | `Qwen/Qwen2.5-0.5B-Instruct`, QLoRA r16/α32, bf16 |
| Korpus | `consolidation_sft.jsonl`, **50.000** Zeilen (Subset der 4,2 M aus ZsRE) |
| `dataset_hash_sha256` | `de24a66743ff74e2d15b2a893c4881b54fecd440239e9b6ae687e8d2f70e301d` |
| **Adapter** | HuggingFace **`Batnini/knowledge-agent-sft-lora`**, Commit **`f02a60166c2ccd3926c7fc8b148d946809d3c703`** (HTTP 200 verifiziert) |
| Seed/Libs | 42 · transformers 5.19.0 / peft 0.21.2 / trl 1.14.2 |

**§10.3-Rückfluss (Flush nur nach Erfolg):** `collect_pending` → 3 Puffer-Fakten → `mark_consolidated(success=True)` → `flush(...)` ⇒ **removed 3, Puffer leer** (nur `README.md`); State: `data/memory/tier3-working/consolidation-state.json`.

**Quelle:** `AGENTS.md` §10.3 · arXiv:2608.22215 §3.4 · `kaggle_output.json`.

## 8. E2E-Verifikation Θ′ — **negativ** (2026-10-07)

Basis `Qwen/Qwen2.5-0.5B-Instruct` vs. Adapter `Batnini/knowledge-agent-sft-lora`, 200 ZsRE-Probes
(Kaggle T4, Seed 42): **`em_base = 22/200 (0.11)`, `em_adapter = 22/200 (0.11)`, `Δ = 0`**.
⇒ Die Hypothese „Θ′ internalisiert die Fakten" ist **NICHT belegt** → Status **`rejected`** (§6/§9).
Details/Ursachen: `ergebnisse/e2e-theta-2026-10-07.md`.
