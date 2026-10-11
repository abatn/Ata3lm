# Rekursion 112: Anbindung des SAGE-Paired-Gates an die Θ′-Probe (CLI)

> Datum: 2026-10-11 · Phasen: Konstrukt → Akt (Code) → Compare (offen: echter Lauf)
> Ziel `g` (§9.1d/§6): den Θ′-Vergleich der Probe **per Item** entscheiden
> (`accept`/`reject`/`abstain`) statt über ein naives Aggregat (`em_base < em_adapter`).
> Status: **pending** (CLI + Tests lokal; echter Probe-Lauf offen).
> Quellen (Belegt): SAGE arXiv:2609.36043; AGENTS.md §9.1d/§6; Rek. 103/111.

## 1. Anlass

Rek. 111 lieferte den Gate-Kern (`data/memory/acceptance_gate.py`). Der Θ′-Probe-Dump
(`kaggle/e2e_theta_probe.py --answers-out`) schreibt je Zeile
`{question, gold, base_answer, adapter_answer}` und bewertete bisher nur
**aggregiert** (Zähler). Diese Iteration verbindet beides — **additiv**.

## 2. Artefakt (neu)

`scripts/paired_gate.py` (nur Standardbibliothek):
- `norm` / `grade(gold, pred, mode)` — **externer Grader** (§6): `strict`
  (normalisiertes Exact-Match) oder `substring` (wie die bisherige Probe).
- `load_rows` — liest die Probe-JSONL.
- `evaluate_rows` — per-Item-Grader → `acceptance_gate.evaluate(...)` → Entscheid.
- CLI: `--answers --mode {strict,substring} --alpha --n-resamples --seed --out`.

Aufruf (nach echtem Probe-Lauf auf Kaggle):

```bash
python scripts/paired_gate.py --answers theta_answers.jsonl \
  --mode strict --out paired_gate_result.json
```

## 3. Evidenz (§9.1d)

- **Baseline (Rek. 103):** `em_base 8/200`, `em_adapter 9/200`, `Δ=+1`, `p≈1.0`
  ⇒ Gate-Ergebnis wäre **`abstain`** (kein systematischer Gewinn).
- **Diff:** neue Dateien (`scripts/paired_gate.py`, `tests/test_paired_gate.py`);
  **keine** Interface-Änderung an bestehenden Modulen/Runnern.
- **Messung (geplant):** `decision`, `p_win`, `p_loss`, `delta`, `ci` (Bootstrap 95 %)
  auf `eval_f6` — im echten Lauf (P-109).

## 4. Drift (Δ zur Baseline)

- Nur Dokument/Additiv — **keine** Modell-/Policy-Änderung ⇒ Drift n/a.
- Referenz: `governance-mcp drift_index` (Projekt-JSD-DI, τ = 0.02, §9.1c).

## 5. Bewertung

- **Additiv, getestet** (12 Tests); der Gate ersetzt Aggregat-Fehlschlüsse
  („konfidente Fehlanpassung", §6).
- **Wirkung offen:** erst der echte Lauf zeigt den Entscheid (kein Fake).

## 6. Quellen (belegt)

- SAGE arXiv:2609.36043 (per-item paired comparison + one-sided paired test).
- AGENTS.md §9.1d (Evidenz-Pflicht), §6 (externes Signal), §9 (Gate).
- Rek. 103 (Baseline), Rek. 111 (Gate-Kern), `ergebnisse/experiment-register.md`.

## 7. Nächster Schritt

- **Wiring in den Runner** (Probe ruft den Gate direkt) = **Interface-Änderung**
  ⇒ separater Human-Gate-Antrag (§9).
- Echter Probe-Lauf (Kontroll-Test, P-109) mit per-Item-Entscheid.
