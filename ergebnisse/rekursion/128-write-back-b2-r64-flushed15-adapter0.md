# 128 — Kaggle-Lauf B2 (rsLoRA-Versuch): flushed=15 aber Adapter-Wirkung weiterhin 0

**Datum:** 2026-10-19
**Auftrag:** Kaggle-Lauf B2 auswerten (Rek 127 §5-Befehl), Rohdaten von HF
laden, Metrik `answer != base_answer` prüfen, Rek-Doc schreiben (Guardrail 3).
**Gate:** Batnini + Taoufik (Rek 127 §1, Chat-Bestätigung 2026-10-19).
**Gesetz:** AGENTS.md §6 (keine Erfindungen), §9 (Gate), §9.1d (Evidenz),
§10.3 (Write-Back), Guardrail 3/6/7.
**Kein git** (Guardrail 6), **kein `self_update`** (§9).

**Quelle (Rohtext):** HF-Repo `Batnini/knowledge-agent-write-back`,
Dateien `write_back_cycle_result.json` + `kaggle_output.json`
(Download 2026-10-19, `hf_hub_download`).

---

## 1. Laufparameter (gemessen, aus `kaggle_output.json`)

```text
!NUM_EPOCHS=15 LORA_R=64 LORA_ALPHA=256 LORA_USE_RSLORA=1 \
  python kaggle/write_back_cycle.py \
  --n 50 --gpu 0 \
  --base-model Qwen/Qwen2.5-3B-Instruct \
  --approver Batnini --approver Taoufik \
  --workdir /kaggle/working \
  --llm-base-url http://127.0.0.1:11434/v1 \
  --llm-model qwen2.5:1.5b
```

| Parameter | Rek 125 (Baseline) | B2 (dieser Lauf) | Quelle |
|---|---|---|---|
| `lora_r` | 16 | **64** | `kaggle_output.json: lora_r` |
| `lora_alpha` | 32 | **256** | `kaggle_output.json: lora_alpha` |
| `lora_use_rslora` | False | **None** (= Feld fehlt ⇒ alter Code-Stand) | `kaggle_output.json: lora_use_rslora` |
| `learning_rate` | 2e-4 | 2e-4 | `kaggle_output.json` |
| `num_train_epochs` | 15 | 15 | `kaggle_output.json` |
| `dataset_rows` | 15 | 15 | `kaggle_output.json` |
| `compute_dtype` | float16 | float16 | `kaggle_output.json` |

**Befund (§6):** `LORA_R=64` und `LORA_ALPHA=256` wurden über ENV angewendet
(`kaggle_output.json` bestätigt). **`LORA_USE_RSLORA=1` wurde NICHT
angewendet** — das Feld `lora_use_rslora` existiert nicht (=`None`), was
bedeutet, dass auf Kaggle der **alte Code-Stand** lief (ohne die Rek-127-
Änderungen). rsLoRA-Skalierung (α/√r) war in diesem Lauf **nicht aktiv**.

## 2. Ergebnisse (gemessen, aus `write_back_cycle_result.json`)

| Metrik | Rek 125 | B2 | Δ |
|---|---|---|---|
| Loss | 2.2958 | **1.3107** | −0,99 |
| Writes | 50 (15/16/6/13/0) | 50 (15/16/6/13/0) | 0 |
| pending | 15 | 15 | 0 |
| **flushed** | **2** | **15** | **+13** |
| **kept** | **13** | **0** | **−13** |
| **`answer != base_answer`** | **0/15** | **0/15** | **0** |
| em_base | 2/15 | **15/15** | +13 |
| em_adapter | 2/15 | **15/15** | +13 |
| **Δ (em_adapter − em_base)** | **0** | **0** | **0** |

## 3. Kritischer Befund: flushed=15 ist IRREFÜHREND (§6)

**`flushed=15` bedeutet NICHT, dass der Adapter 15 Fakten gelernt hat.**

Gemessene Einzelproben (alle 15, Rohtext `probe_results`):

```text
[ 0] changed=False base_ok=True adp_ok=True  gold=Grand Duke of Lithuania
[ 1] changed=False base_ok=True adp_ok=True  gold=30 September 2005
[ 2] changed=False base_ok=True adp_ok=True  gold=Bernie Wrightson
... (alle 15 identisch)
[14] changed=False base_ok=True adp_ok=True  gold=2005
```

**Zusammenfassung:**
- `em_base = 15/15` → Das **Basis-Modell kennt bereits ALLE 15 Gold-Antworten**.
- `answer != base_answer = 0/15` → Der **Adapter hat keine einzige Antwort verändert**.
- `flushed = 15` → Der Flush-Criterium `grade(adapter_answer, gold)` ist wahr,
  **weil base_answer == gold**, nicht weil der Adapter gelernt hat.

**Warum flushed=2 in Rek 125, aber flushed=15 hier?**

| | Rek 125 | B2 |
|---|---|---|
| em_base | **2/15** (Basis kennt nur 2) | **15/15** (Basis kennt alle 15) |
| em_adapter | 2/15 | 15/15 |
| flushed | 2 (= em_base) | 15 (= em_base) |
| Adapter-Effekt | 0 | 0 |

`flushed` folgt **exakt `em_base`** — der Flush misst die Wissenslücke des
**Basis-Modells**, nicht die Wirkung des Adapters. Die Pending-Fakten waren
diesmal solche, die das 3B-Basis-Modell bereits kennt (Unterschied zu Rek 125:
andere Router-Klassifikationen / ZsRE-Sample-Variation bei gleichem Seed).

## 4. Was dieser Lauf belegt (und was nicht)

| Aussage | Status |
|---|---|
| `LORA_R=64 LORA_ALPHA=256` wurden angewendet | **belegt** (`kaggle_output.json`) |
| Loss 1.31 (Rek 125: 2.29) | **belegt** (Rohtext) |
| flushed=15, kept=0 | **belegt** (Rohtext) |
| **Adapter-Effekt = 0** (`answer == base_answer` bei 15/15) | **belegt** (Rohtext, `probe_results`) |
| em_base = 15/15 (Basis kennt alle Gold) | **belegt** (Rohtext) |
| **rsLoRA war NICHT aktiv** (`use_rslora=None` ⇒ alter Code) | **belegt** (`kaggle_output.json`) |
| `LORA_USE_RSLORA=1` erreichte das Train-Skript nicht | **belegt** (Feld fehlt) |
| r=64 + α=256 verändert Adapter-Wirkung | **widerlegt** (0/15 geändert) |
| Write-Back steigert QA-EM | **nicht belegt** (Δ = 0) |
| flushed=15 = Adapter hat 15 gelernt | **widerlegt** (flushed = em_base, nicht Adapter-Leistung) |

## 5. Ursache des fehlenden rsLoRA (§6)

**Rohtext:** `kaggle_output.json` → `"lora_use_rslora": None`

Die Rek-17-Änderungen (`use_rslora=LORA_USE_RSLORA` in `LoraConfig`,
neue ENV-Variablen) waren auf Kaggle **nicht aktiv**. Der Nutzer führte den
Befehl mit `LORA_USE_RSLORA=1` aus, aber der **alte Code** auf Kaggle las
diese ENV-Variablen nicht (Feld existiert nicht im Output).

**Konsequenz:** B2 testete **nur r=64 + α=256**, nicht rsLoRA. Der
α/√r-Vorteil (arXiv:2312.03732) wurde **nicht getestet**.

## 6. §9-Gate-Entscheid

| Bedingung | Wert | Gate |
|---|---|---|
| Compare-Score (`answer != base_answer`) | **0/15 = 0 %** | **≪ 70 % ⇒ deny** |
| self_update | keine Änderung an Originaldateien | n/a |
| Neue Quelle | keine | n/a |

**Entscheidung: deny.** Kein `self_update`. Keine positive Behauptung, dass
Write-Back funktioniert. **Auch mit r=64 + α=256 bleibt der Adapter wirkungslos.**

## 7. Offene Fragen (pending, §6)

1. **Ist r=64 + α=256 überhaupt der Knackpunkt?** Der Lauf zeigt: auch mit
   4× höherem Rang bleibt `answer == base_answer`. Mögliche Ursachen (nicht
   getestet, keine Behauptung):
   - Die 15 Pending-Fakten waren **zu leicht** (Basis kennt sie bereits →
     kein Lernsignal, Gradient ≈ 0).
   - Trainingssignal reicht nicht (15 Zeilen × 15 Epochen auf 3B).
   - Andere HP (LR, Epochenzahl, Target-Module).
2. **Flush-Logik misst Adapter-Wirkung NICHT** — `flushed` folgt `em_base`.
   Für einen echten Adapter-Test bräuchte man `em_base < em_adapter`
   (Basis kennt Fakt NICHT, Adapter kennt ihn JETZT).
3. **rsLoRA-Test ausstehend** — Code muss erst auf Kaggle aktualisiert werden
   (Rek-17-Änderungen hochladen), dann Lauf mit `LORA_USE_RSLORA=1`.

## 8. Nächste Schritte

1. **Code-Update auf Kaggle:** Rek-17-Änderungen (`write_back_cycle.py`,
   `train_slow_consolidation.py`) als Dataset hochladen / Notebook-Upload.
2. **B2' (rsLoRA):** Lauf mit aktualisiertem Code + `LORA_USE_RSLORA=1`,
   um α/√r tatsächlich zu testen.
3. **A/B mit Basis-Lücke:** Fakten wählen, die das Basis-Modell **nicht**
   kennt (em_base < 100 %), sonst misst `flushed` nur Basis-Wissen.
4. **Kein `self_update`** ohne erneutes §9-Gate (Score ≥ 70 % nötig).

## 9. Quellen

| Quelle | Verwendung |
|---|---|
| arXiv:2312.03732 (rsLoRA, α/√r) | Wurde in diesem Lauf NICHT getestet (Code-Update fehlte) |
| arXiv:2405.09673 (TMLR) | r=64/α=256 ≠ automatisch besser (datensatzabhängig) |
| HF `Batnini/knowledge-agent-write-back` | Rohdaten `write_back_cycle_result.json`, `kaggle_output.json` |
| AGENTS.md §6/§9/§9.1d/§10.3, Guardrail 3/6/7 | Gesetz |
