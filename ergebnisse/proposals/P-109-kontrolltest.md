## PROPOSAL 109 — Kontroll-Test: eval-Fragen im Training

### 0. Metadaten

| Feld | Wert |
|---|---|
| Datum | 2026-10-11 |
| Iteration | `t → t+1` |
| Phase | Revise (Kontroll-Test) |
| Betroffenes Artefakt | `kaggle/write_back_cycle.py` (Trainingsdaten-Aufbereitung) |
| Komponenten-Typ | Code / Daten |
| Autor | Knowledge-Agent |

### 1. Ziel `g`

- Ziel: **P-109 Kontroll-Test** — trennt "merken" von "generalisieren".
- Task-Input: dieselben 200 `eval_f6`-Fragen zusätzlich ins Trainingsset
  aufnehmen; feste Eval `eval_f6` unverändert.

### 2. Baseline (vorher)

| Feld | Wert |
|---|---|
| `π` (Modell/Policy) | `Qwen/Qwen2.5-0.5B-Instruct` (+ Adapter, Rek. 108/109) |
| Score (externes Signal) | `em_base = 8/200` = 4.0 %, `em_adapter = 9/200` = 4.5 %, `Δ = +1`, `p ≈ 1.0` |
| Signal-Quelle | `eval_f6` = 200 Fragen (`community-datasets/qa_zre`, validation, 0× "XXX") |
| Drift-Referenz | Baseline-Snapshot Rek. 103 (F6-GPU-Lauf, `rejected`) |

### 3. Änderung (Diff, line-level)

```diff
- train = build_train_set(DATA)              # 50k, 3 Epochen
+ train = build_train_set(DATA) + eval_f6    # + dieselben 200 eval_f6-Fragen
```

- Geänderte Komponenten: **1** (Ziel; mehrere nur mit Begründung — DREvo)
- Interface-Änderung? **nein**

### 4. Score-Änderung

| Testfall | Kriterium | vorher | nachher |
|---|---|---|---|
| 1 | striktes EM auf `eval_f6` | 9/200 | ausstehend |
| 2 | Teilstring-EM auf `eval_f6` | 9/200 | ausstehend |
| 3 | Bootstrap-KI 95 % um ΔEM | n/a | ausstehend |

- **Score vorher:** `9/200` = `4.5 %`
- **Score nachher:** ausstehend (Test noch nicht gelaufen; kein Erfinden)
- **Δ Score:** Erwartung **≥ +20/200** (vorab gesetzte Erfolgsschwelle) und
  außerhalb des Rauschens (Bootstrap-KI 95 %)

### 5. Drift (Δ zur Baseline)

- **Definition (Auftrag, praktische Messung):**
  `Δ = geänderte Zeilen / Gesamtzeilen des Artefakts`
  (line-level, vgl. DREvo; für Modell-Parameter: `‖πₜ − π₀‖ / ‖π₀‖`).
- **Drift-Wert:** ausstehend — zu messen via `governance-mcp drift_index`
  (Projekt nutzt JSD-DI); Datenänderung: 200 Fragen / 50 000 = 0,4 % der
  Trainingsmenge.
- **Drift-Bound / τ:** `τ = 0.02` (JSD-DI; Default §9.1c).
- **Überschritten?** ausstehend → wenn ja: **Human-Gate (ask)**.

### 6. Gate-Entscheid (§9)

| Bedingung | Wert | Ergebnis |
|---|---|---|
| Score | `4.5 %` (< 70 %) | deny (§9-Score-Regel) |
| Neue Quelle? | nein | — |
| Interface-Änderung? | nein | — |
| Drift ≤ τ? | ausstehend (τ = 0.02) | ask wenn nein |

- **Gate-Ergebnis:** `ask` — das automatische §9-Score-Gate würde wegen
  Score < 70 % auf `deny` stehen; als diagnostischer Kontroll-Test entscheidet
  der Mensch (`ask`).
- Quellen: SAGE arXiv:2609.36043 (per-item paired + one-sided paired test);
  Progress Mirage arXiv:2607.25152 (+Zenodo 10.5281/zenodo.21594735, Out-of-Band).

### 7. Freigabe

- Status: `pending`
- Human-Gate-Referenz: `ergebnisse/rekursion/109-*.md`
