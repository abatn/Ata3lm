# Rekursion 084: Drift-Kalibrierung — Ergebnis (SAHOO Gl. 14–16)

> Datum: 2026-10-08 · Phasen: Konstrukt → Akt → Observe → Compare (echtes externes Signal).
> Ziel `g` (§9.1c): Die Drift-Schwelle **kalibrieren** (nicht willkürlich setzen).
> Quelle: **arXiv:2603.06333** (SAHOO, in `AGENTS.md` §9.1c zitiert), Appendix B
> Gl. 14 (Gewichte), Gl. 15 (Schwelle), Gl. 16 (Bootstrap-CI) · externes
> Grader-Signal per §6. Status: **`approved`** (Batnini + Taoufik, 2026-10-08).

## 1. Datensatz (real, extern)

- `theta_answers.jsonl` = **200** Probes aus dem echten **Θ→Θ′-Schritt**
  (Base `Qwen/Qwen2.5-0.5B-Instruct` vs. Adapter `Batnini/knowledge-agent-sft-lora`),
  erzeugt von `kaggle/e2e_theta_probe.py` (Antwort-Dump), Kaggle T4.
  HF: `Batnini/knowledge-agent-sft-lora` Commit **`f941289e`** (HTTP 200 verifiziert).
- **Klassen** (externer Grader = gold): Adapter korrekt `22` (kein Drift, `y=0`),
  Adapter falsch `178` (Drift, `y=1`). Beide Klassen vorhanden ⇒ identifizierbar.

## 2. Verfahren (wörtlich nach Quelle)

- Gl. 8–11: vier Signale (semantic/lexical/structural/distributional) über
  `data/memory/drift_calibration.signal_vector` (Embeddings: `nvidia/nemotron-3-embed-1b`).
- Gl. 14: `calibrate_weights` (AUC-Maximierung) · Gl. 15: `calibrate_tau` (F1-Max)
  · Gl. 16: `bootstrap_ci` (B≈2000).

## 3. Ergebnis (real)

```json
{ "n": 200, "tau": 0.10390,
  "weights": { "sem": 1.0, "lex": 0.0, "struct": 0.0, "dist": 0.0 },
  "auc": 0.6845, "f1": 0.9468, "ci": { "lo": 0.16414, "hi": 0.17578 } }
```

Datei: `ergebnisse/drift-calibration-result.json`. Skript: `scripts/drift_calibrate.py`.

## 4. Real vs. Caveat (ehrlich)

- **Real:** echte Daten (HF), echter externer Grader (§6), kein Fake; reproduzierbar
  via `python scripts/drift_calibrate.py --answers theta_answers.jsonl`.
- **Caveat 1 — Klassen-Ungleichheit:** 178/200 sind „Drift" ⇒ `F1=0.947` ist
  **aufgebläht**; belastbarer ist **AUC 0.684** (moderat).
- **Caveat 2 — Skala:** `τ=0.104` gilt für die **GDI-Skala** (Gl. 12); die alte
  JSD-`BiasDriftMonitor`-`τ=0.10` ist eine **andere** Skala ⇒ **nicht** blind ersetzen.
- **Caveat 3 — CI/τ:** die Bootstrap-CI `[0.164, 0.176]` liegt über `τ` — Spannung;
  bei mehr/weniger balancierten Daten neu kalibrieren.
- **Negativer Zwischenlauf (verworfen):** ein erster Lauf mit „Memory hilft" erzeugte
  **nur** „kein Drift" (alle `y=0`) ⇒ nicht identifizierbar (`τ=0`, `auc=0`) — dokumentiert,
  **nicht** verwendet.

## 5. §9-Gate

**`approved`** (Batnini + Taoufik, 2026-10-08; ≥ 2 Personen, §9.3). Keine neue Quelle
(SAHOO in `AGENTS.md` §9.1c). `data/memory/`-Code/Artefakt ⇒ **kein** `versions/vN`.
Kein `self_update` an Originaldateien.
