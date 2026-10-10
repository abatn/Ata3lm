# Rekursion 103: Θ′ (Write-Back) — echter Lauf, negatives Ergebnis

> Datum: 2026-10-10 · Phasen: Konstrukt → Akt → Observe → **Compare** (echtes
> externes Signal: Kaggle-T4 + HF).
> Ziel `g` (§2): prüfen, ob der LoRA-Adapter (Θ′) die ZsRE-Fakten **ohne Retrieval**
> beantwortet (Internalisierung, §10.3).
> Status: **`rejected`** — die Behauptung „Θ′ wirkt" ist **nicht** bestätigt
> (Geltungsbereich der AGENTS.md: Verstöße/Negativergebnisse → `rejected`).

## 1. Setup (echt, kein Fake)

- **Kaggle T4**; QLoRA (4-bit nf4, compute `float16`, **AMP aus** — Rek. 102);
  Basis `Qwen/Qwen2.5-0.5B-Instruct`, Adapter `Batnini/knowledge-agent-sft-lora`.
- **Training:** `train_f6.jsonl` (50 000 F6-subjektgebundene Zeilen;
  `dataset_hash_sha256=90d467e9…`), 3 Epochen, **lauf-t durch** (`loss=0.5733`,
  `kaggle_output.json`). → Beweis für den AMP/T4-Fix (Rek. 102).
- **Eval:** `eval_f6.jsonl` (200 F6-Fragen, `build_zsre_corpus(split="validation")`,
  **0 × „XXX"**).

## 2. Ergebnis (Compare, §6: externes Signal)

| Größe | Wert |
|---|---|
| `em_base` | 8 / 200 (0.040) |
| `em_adapter` | 9 / 200 (0.045) |
| **Δ** | **+1 (im Rauschen)** |

Unabhängige Nachrechnung (Substring-EM direkt aus `theta_answers_f6.jsonl`) = **identisch**
(8 / 9 / Δ +1). Beispiel: „What type of product does Armstrong Whitworth produce?"
→ gold `aircraft`, Basis „…British enginee…", Adapter „automobile engine" — **beide falsch**.

## 3. Bewertung / §9-Gate

- Compare-Score ≈ **1/200 ≈ 0,5 % ≪ 70 %** ⇒ **deny** (§9) → **kein** `self_update`,
  **keine** positive Behauptung.
- **Θ′ NICHT belegt** (Internalisierung messbar ≈ 0). Der **Training-Durchlauf**
  hingegen ist belegt (Fix aus Rek. 102 verifiziert).

## 4. Quellen (belegt)

- HF-Commits: `53f3a25ace569e51a7315baba34cd9a4e7dbecae` (Adapter) ·
  `ec08d221808f0675e5aa64ee1e251f6f2d369cbc` (Ergebnis) —
  Repo `Batnini/knowledge-agent-sft-lora`.
- Dateien: `theta_answers_f6.jsonl`, `e2e_theta_result_f6.json`, `kaggle_output.json`.
- `AGENTS.md` §10.3 / §10.5; Paper arXiv:2608.22215 §3.4.

## 5. Ehrliche Hypothesen (NICHT belegt — nur Auftrag für die nächste Iteration)

- **Modellgröße:** Paper/§10.2 nutzt qwen3-8B; hier 0.5B.
- **Umfang/Methodik:** 3 Epochen/50 k, strenge EM-Metrik.
(Das sind Hypothesen, kein Befund.)

## 6. Nächster Schritt (Gate)

- **Revise als Proposal** (§9.1d: Δ/Score/Diff) → **Human-Gate (`ask`)**.
- Umsetzung + Git erst **nach** Freigabe (§9 / Guardrail 6). Kein Fake (§6/Guardrail 7).

## 7. REFLECT (`sr`, Revise-Phase — VALIDATE bestanden/negativ)

> Mechanismus: Self-Reflection `(τ, r, mem) → sr` (Shinn et al. 2023,
> <https://arxiv.org/abs/2303.11366>); `VALIDATE → REFLECT → PIVOT`
> (`knowledge/lifecycle/rekursion/revise.md` §2). Freigabe: Batnini, 2026-10-10.

**VALIDATE:** Externes Signal liegt vor (Rek. III-Daten): `ΔEM = +1` (8→9/200),
`loss=0.5733`, `mean_token_accuracy≈0.84`, T4, `0 × „XXX"` ⇒ **Check nicht bestanden**.

**`sr` (verbale Reflexion, richtunggebend – kein Eigenbau, belegt):**
„Der Lauf bewies nur, dass die **Maschinerie** läuft (AMP/T4-Fix), **nicht** das
Lernen. Token-Accuracy 0,84 vs. Exact-Match ~0,04 zeigt: Das Modell erzeugt
**plausiblen Fließtext**, nicht die **spezifische** Antwort — Basis und Adapter
gleichermaßen. Der Engpass liegt also **nicht** in der Ausführung, sondern in
**Kapazität/Ziel** (0,5B, 3 Epochen, EM streng). Nächster Versuch muss **eine**
Variable kontrolliert ändern und dieselbe `eval_f6` nutzen."

**Mem-Schranke:** `mem` = Rek. 102 (Fix) + Rek. 103 (Negativ) — ≤ 3 Kontextpunkte (§6.4).

**PIVOT-Kandidat (NICHT ausgeführt — Human-Gate):** genau **eine** Variable:
(a) `BASE_MODEL` größer (T4-tauglich, z. B. 1.5B) **oder**
(b) Kontrolle: dieselben 200 Fragen **im Trainings-Set** (trennt „Merken" von „Generalisieren") **oder**
(c) Generierungs-/EM-Härte prüfen.
Diff + erneutes ΔEM nach Freigabe (§9.1d).
