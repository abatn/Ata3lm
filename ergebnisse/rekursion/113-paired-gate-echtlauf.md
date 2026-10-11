# Rekursion 113: Paired-Gate — erster echter Lauf (lokal, CPU) auf F6-Antworten

> Datum: 2026-10-11 · Phasen: Konstrukt → Akt → Observe → **Compare** (externes Signal: echte F6-Antworten + Gold-Grader)
> Ziel `g` (§9.1d/§6): den SAGE-Gate (`scripts/paired_gate.py`) **real** auf echten
> Θ′-Antworten ausführen und den Entscheid gegen den Naiv-Aggregat-Befund prüfen.
> Status: **approved** (echter lokaler Lauf; kein Fake). Quellen (Belegt): SAGE
> arXiv:2609.36043; AGENTS.md §9.1d/§6; Rek. 103/111/112.

## 1. Anlass

Rek. 111/112 lieferten Gate-Kern + CLI. Diese Iteration führt den Gate **real** aus —
ohne GPU (reine Statistik/Grader), auf den echten F6-Antworten (`theta_answers_f6.jsonl`,
200 Zeilen, HF `Batnini/knowledge-agent-sft-lora`; aus dem F6-GPU-Lauf, Rek. 103).
Schema je Zeile: `{question, gold, base_answer, adapter_answer}`.

## 2. Aufruf (real, lokal)

```bash
python scripts/paired_gate.py --answers theta_answers_f6.jsonl --mode strict \
  --out ergebnisse/paired-gate-strict.json
python scripts/paired_gate.py --answers theta_answers_f6.jsonl --mode substring \
  --out ergebnisse/paired-gate-substring.json
```

## 3. Ergebnis (Compare, §6)

| Modus | `em_base` | `em_adapter` | `delta` | `p_win` | `p_loss` | `ci` (95 %) | **Entscheid** |
|---|---|---|---|---|---|---|---|
| **strict** (normalisiertes EM) | 0/200 | 6/200 | +0,030 | **0,015625** | 1,0 | [0,01; 0,055] | **accept** |
| **substring** | 8/200 | 9/200 | +0,005 | 0,50 | 0,7256 | [−0,025; 0,04] | **abstain** |

- **strict:** Adapter gewinnt **6 vs. 0** entschiedene Paare ⇒ p = 1/64 ≤ 0,05 ⇒ **accept**.
- **substring:** +1 (im Rauschen) ⇒ **abstain** — **deckt sich exakt mit Rek. 103**
  (8→9, Δ+1, p≈1,0, `rejected`).
- **Belege:** `ergebnisse/paired-gate-strict.json`, `ergebnisse/paired-gate-substring.json`.

## 4. Bewertung (ehrlich)

- Der Gate **läuft real** und liefert je Metrik einen nachvollziehbaren, **per-Item**
  begründeten Entscheid (§6: Grader = Code, Gold aus Daten).
- **Kein starker „gelernt"-Claim:** der `accept` (strict) beruht auf nur **6 von 200**
  Items (≈3 %), bei `em_base = 0` (striktes EM ist hart). Ein Aggregat-Blick hätte
  „+1" als Fortschritt verkauft; der per-Item-Blick zeigt, dass die Wahl der Metrik
  den Entscheid dreht.
- **Caveat:** Vorzeichentest nimmt Unabhängigkeit an; bei ~200 Items mit klumpigen
  LoRA-Effekten ist `p` als grobe Schranke zu lesen (kein Nachweis von Kausalität).

## 5. Quellen (belegt)

- SAGE arXiv:2609.36043 (per-item paired comparison + one-sided paired test).
- AGENTS.md §9.1d (Evidenz: Score-Δ/Diff/Drift), §6 (externes Signal).
- Rek. 103 (F6-Baseline), Rek. 111 (Gate-Kern), Rek. 112 (CLI).
- HF `Batnini/knowledge-agent-sft-lora` (`theta_answers_f6.jsonl`, 200 Zeilen).

## 6. Nächster Schritt

- Derselbe Gate auf dem **Write-Back-Adapter** (`write_back_cycle.py`) im Kaggle-Lauf (P-109).
- Wiring des Gates in den Runner = Interface-Änderung ⇒ separater Human-Gate-Antrag (§9).
