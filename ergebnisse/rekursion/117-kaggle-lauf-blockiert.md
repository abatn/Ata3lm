# Rekursion 117: Kaggle-Lauf Θ→Θ′ (blockiert, kein Ergebnis)

- **Datum:** 2026-10-14
- **Phase:** Compare (Versuch) – **nicht ausgeführt**
- **Freigabe (§9.3):** Batnini + Taoufik, Diff-SHA `8f205d99b66ffe7b` (**historisch** – dieser
  SHA war der Stand am 2026-10-14; aktueller Stand `4bd63cb`), `state = approved`.
  Record: `ergebnisse/freigabe-record-115-2026-10-14.json` (gesetzt über `data/memory/approval.py`:
  `approve` ×2 + `finalize`, Verlauf im Record).

## 1. Ziel g

Write-Back Θ→Θ′ (§10.3) und Routing (§10.1/§10.2) auf held-out-Eval mit einheitlicher
strict-Bewertung und zwei Kaskaden-Modellen. Ergebnis: Score (em_base/em_adapter), Δ, Drift.

## 2. Befund der Umgebung (Beweis)

| Voraussetzung (Setup-Auftrag) | Befund | Beleg |
|---|---|---|
| GPU (Kaggle T4) | keine GPU (`nvidia-smi` nicht vorhanden) | Shell-Check 2026-10-14 |
| Kaggle-Umgebung `/kaggle/working` | nicht vorhanden | `ls /kaggle` → fehlt |
| `torch` (System + Projekt-venv) | System-Python: `2.8.0+cpu` installiert, `torch.cuda.is_available() = False`; Projekt-venv `/tmp/kvenv`: nicht installiert (`ModuleNotFoundError`); `nvidia-smi` nicht vorhanden → **kein GPU-Training** | `python3 -c "import torch"`, `/tmp/kvenv/bin/python -c "import torch"`, `which nvidia-smi` (Check 2026-10-16) |
| Ollama `qwen2.5:1.5b` / `qwen2.5:7b` | nicht vorhanden; vorhanden: `qwen2.5-coder:7b`, `qwen-local:latest` | `GET localhost:11434/api/tags` |
| Held-out-Eval | vorhanden: 200 Zeilen | `ergebnisse/zsre-eval-f6.jsonl` |
| Internet | erreichbar (HTTP 200 huggingface.co) | Shell-Check |

Ohne GPU kann `kaggle/write_back_cycle.py` (Training des Adapters) nicht laufen —
`kaggle/train_slow_consolidation.py:351-353` bricht mit „Keine GPU gefunden" ab;
zusätzlich fail-closed die Θ′-Probe bei `torch.cuda.is_available()` False
(`kaggle/write_back_cycle.py:379-380`).
Ohne Training gibt es keinen Adapter, also keinen `em_adapter` und kein Δ.

## 3. Ergebnis

- **Score (strict em_base / em_adapter): nicht gemessen.**
- **Δ: nicht gemessen.**
- **Drift: nicht gemessen** (kein Lauf).
- **Artefakte** `theta_answers.jsonl`, `paired_gate_result.json`, Adapter: **nicht erzeugt**.
- **Compare-Gate (§9):** nicht auswertbar → kein „gelernt"-Claim. Kein Θ′-Befund.

## 4. Diff (§9.1d)

Code-Änderungen dieser Iteration: keine. Stand = Freigabe-SHA `8f205d99b66ffe7b`
(**historisch**, Stand am 2026-10-14; aktueller Git-Stand `4bd63cb` nach Rek. 118/119;
siehe Rek. 115, §3 dort). Drift: `n/a` (rein additiv, kein Lauf).

## 5. Offen (ehrlich)

1. Kaggle-Notebook mit T4-GPU, Internet ON ausführen (Setup + LAUF 1/LAUF 2 wie in der Auftragsbeschreibung).
2. Oder lokal: GPU + `torch` + `peft` + `ollama pull qwen2.5:1.5b` / `qwen2.5:7b` installieren.
3. Erst danach Score, Δ, Drift und Artefakt-Links dokumentieren.

## 6. Nicht behauptet (§6/§7)

Kein Θ′-Ergebnis, keine Verbesserung, keine Wirkung der Konsolidierung. Der Grader-Test
(845 passed, 100 % Coverage, Rek. 115) belegt nur die Code-Konsistenz, nicht die Modellwirkung.
