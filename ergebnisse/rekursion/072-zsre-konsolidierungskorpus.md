# Rekursion 072: §10.3-Konsolidierungskorpus aus dem ZsRE-Benchmark

> Datum: 2026-10-07 · Phasen: Konstrukt → Akt → Observe → Compare (Test).
> Ziel `g`: Für §10.3 (Write-Back / Slow Consolidation) einen **offiziellen**,
> reproduzierbaren SFT-Korpus bereitstellen — Fakten aus dem **ZsRE**-Benchmark
> im TRL-Chat-Format — und diesen als Datenquelle in die Kaggle-Trainingsstufe
> (`SFT_SOURCE`) einbinden. Status: **`approved`** (Batnini, 2026-10-07; §9 neue Quelle + Interfaces).

## 1. Quellen / Gesetz

Verifiziert real am **2026-10-07** (HTTP-Status per `curl`, kein Fake):

| Zweck | Referenz | HTTP | Link |
|---|---|---|---|
| Paper-Methode (Fakten aus ZsRE; write-back = (q,a)-Proben + sentence-level SFT) | arXiv:2608.22215v2 §3.4 + Appendix A.1 | 200 | <https://arxiv.org/html/2608.22215v2> |
| Dataset (train 8 400 000; validate 6 000; test 120 000; Felder `relation, question, subject, context, answers`) | `community-datasets/qa_zre` | 200 | <https://huggingface.co/api/datasets/community-datasets/qa_zre> |
| Ursprung | Levy, Seo, Choi & Zettlemoyer 2017, CoNLL, pp. 333–342 | 200 | <https://aclanthology.org/K17-1034/> |
| Chat-JSONL-Format | TRL dataset formats | 200 | <https://huggingface.co/docs/trl/dataset_formats> |
| Demo-Korpus (Capybara) | `LDJnr/Capybara` (16 006 train; `source`, `conversation`) | 200 | <https://huggingface.co/api/datasets/LDJnr/Capybara> |

Gesetz: `AGENTS.md` §10.3 (Write-Back), §9 (neue Quelle ⇒ `ask`, Interface-Gate),
§6 (keine Erfindungen), Guardrail 7 (echte Tests, kein Fake).

Paper-Beleg (Zitat-Extraktion aus dem HTML): „We derive the fact corpus from the
Zero-Shot Relation Extraction (**ZsRE**) benchmark [29]"; „Each selected fact is
converted into … independent question-level examples (…q…a…) and sentence-level
targets"; „A fact is removed from external memory only if consolidation is
validated".

## 2. Änderung (additiv)

| Datei | Inhalt |
|---|---|
| `data/memory/zsre_corpus.py` (neu) | `row_to_record(row)` (reine Mapping-Funktion) · `records_to_jsonl(records, out_path)` · `build_zsre_corpus(out_path, n=10000, split="train")`. |
| `tests/test_zsre_corpus.py` (neu) | 7 Tests: Mapping/Hash/Format + **echtes** `load_dataset` (skip nur ohne Netz). |
| `kaggle/train_slow_consolidation.py` | Neu: `SFT_SOURCE` (`zsre` \| `local` \| `capybara`), `load_zsre_rows`, `load_capybara_rows`, `canonical_sha256`; `main()` dispatcht; `kaggle_output.json` um `sft_source/source_note/dataset_*` erweitert. |
| `kaggle/train_slow_consolidation.ipynb` | Aus der `.py` regeneriert (identische Logik, 17 Zellen). |
| `connectors/fast-write-routing.md` | Neuer Abschnitt „§10.3-Konsolidierungskorpus aus ZsRE (neu — §9 `ask`)". |
| `kaggle/README.md` | Abschnitt „Datenquellen (`SFT_SOURCE`)" + verifizierte Links. |

**Interface-Änderung (§9-pflichtig, kenntlich gemacht):** `zsre_corpus`-Funktionen
und die neuen Kaggle-Helper/`SFT_SOURCE` sind NEU. Die neuen Kaggle-Parameter sind
rückwärtskompatibel (`SFT_SOURCE` Default `local` = altes Verhalten). Kein
Bestehendes gebrochen. **Nicht** selbst freigegeben (`pending`).

**Neue Quelle (§9):** `community-datasets/qa_zre` — **freigegeben** (Batnini, 2026-10-07); Ontologie-Eintrag ergänzt.

## 3. Was real ist vs. blockiert

- **Real (lokal ausgeführt, kein Fake):** HTTP-Verifikation aller Links; HTTP-API
  von `qa_zre` (num_examples/features) und `Capybara` (Format); Streaming-Load
  gegen den echten HF-Hub; Mapping/Hash/Format der Tests.
- **Nicht ausgeführt (ehrlich):** das Θ→Θ′-Training selbst — läuft auf Kaggle (GPU),
  nicht hier (`write_back`-Stub, Rekursion 070/071).
- **Ehrlich:** Die volle ZsRE-Menge ist verfügbar; `build_zsre_corpus` verwendet
  nur ein **gesampeltes `n`** (Default 10 000). Zeilen ohne nicht-leere Antwort
  werden gezählt (`skipped_empty`) und übersprungen — nichts erfunden.

## 4. Compare / Beleg (externes Signal: echte Tests)

Am 2026-10-07 real ausgeführt (`.venv/bin/python`, `datasets 4.5.0`, `hf_hub 1.33.0`):

```text
pytest tests/test_zsre_corpus.py -q --no-cov            -> 7 passed
   (davon test_build_zsre_corpus_real_or_skip: ECHT ausgeführt, nicht geskippt)
ruff check data/memory/zsre_corpus.py \
           tests/test_zsre_corpus.py \
           kaggle/train_slow_consolidation.py           -> All checks passed
```

Belegte Wirkung (Paper, nicht hier gemessen): ≤68 % redundante Writes reduziert,
QA-EM >98 %; externer Speicher nach Write-Back ~32 % (arXiv:2608.22215).

## 5. Offene Punkte

1. **Mensch-Gate §9:** neue Quelle `community-datasets/qa_zre` → `ask`; neue
   Interfaces (`zsre_corpus`, Kaggle-`SFT_SOURCE`) → `pending`.
2. **Kaggle:** realer Trainingslauf mit `SFT_SOURCE=zsre` + `kaggle_output.json`
   (kein Fake-Erfolg hier behauptet).
3. `trl` ist lokal **nicht** installiert (nur auf Kaggle nötig); JSONL-Format ist
   ohne `trl` erzeugbar (reines `messages`-JSONL).

## 6. Status

`pending` — kein `self_update` an Originaldateien, keine `AGENTS.md`-/
`tier1-base`-Änderung. Kein Git (G6). Keine Erfindung (G7): Links HTTP-200,
Tests real, Training als Kaggle-Teil gekennzeichnet.
