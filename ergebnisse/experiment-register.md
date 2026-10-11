# Experiment-Register — Knowledge-Agent

> Datum: 2026-10-11
> Zweck: Kontrollierte, forschungskonforme Experimente — **eine Variable pro
> Iteration**, feste Eval (`eval_f6`), externes Signal (Grader = Code). Jede
> Iteration erhält ein eigenes Rekursions-Doc mit Score-Δ, Diff und Drift (§9.1d).
> Status: Auftrag (Betriebsregel). Quellen (verifiziert): SAGE arXiv:2609.36043;
> SAHOO arXiv:2603.06333; Dual-Layer arXiv:2608.22215; Progress Mirage
> arXiv:2607.25152 (+Zenodo 10.5281/zenodo.21594735, Out-of-Band); Kairos
> nips.cc/virtual/2025/129852; FadeMem arXiv:2601.18642; TiMem
> aclanthology.org/2026.findings-acl.1091.

## Warum

Mechanik ist belegt, Wirkung offen:
- **Belegt (Mechanik, Rek. 108/109):** Write-Back-Zyklus läuft — Treiber
  `kaggle/write_back_cycle.py`, Basismodell `Qwen/Qwen2.5-0.5B-Instruct`,
  Schwellen: Probe = Teilstring-Test.
- **Offen (Wirkung, Rek. 103):** F6-GPU-Lauf (Θ′-Probe) ergab `em_base = 8/200`,
  `em_adapter = 9/200`, `Δ = +1`, `p ≈ 1.0` ⇒ **rejected** (kein systematischer
  Gewinn). Feste Eval: `eval_f6` = 200 Fragen (`community-datasets/qa_zre`,
  validation, 0× "XXX").

Resultat: Der Zyklus *schreibt*, aber die Wirkung ist nicht nachgewiesen.
Dieses Register trennt die offenen Variablen (eine pro Iteration).

## Experimente

| ID | Variable (nur diese) | Hypothese | Messgröße | Gate |
|---|---|---|---|---|
| P-109 Kontroll-Test (eval-Fragen im Training) | dieselben 200 `eval_f6`-Fragen zusätzlich ins Trainingsset | trennt "merken" von "generalisieren" | ΔEM (sollte springen) | §9 |
| P-110 Modell 0.5B→1.5B | Modellgröße | Kapazität ist Engpass | ΔEM | §9 |
| P-111 Datenmenge/Epochen | 50k→mehr, 3→5 | zu wenig Training | ΔEM | §9 |
| P-112 EM strikt vs Teilstring | Metrik | Metrik verschleiert | ΔEM strikt | §9 |

## Protokoll

- Feste Eval `eval_f6` (200 Fragen) + fixe Seeds + Lib-Pins.
- Hash-Artefakte auf HF hochladen; Bootstrap-KI 95 %.
- Grader = Code (striktes EM + Teilstring-EM), **nicht** LLM-Gefühl.
- Je Iteration eigenes Rekursions-Doc (`ergebnisse/rekursion/NNN-*.md`) mit
  Score-Δ / Diff / Drift (§9.1d).
- Erfolgsschwelle vorab (Vorschlag, Auftrag): `ΔEM = EM(Adapter) − EM(Base)
  ≥ +20/200` **und** außerhalb des Rauschens (Bootstrap-KI 95 %).

## Governance

- **Human-Gate vor jedem Kaggle-Start.**
- §9-Score-Gate.
- Zwei-Personen-Verifikation nur für echte Write-Freigabe (§9.3).
- Git nur nach Freigabe (G6); kein Fake (G7).

## Reihenfolge / Empfehlung

**P-109 zuerst** — billigster diskriminierender Test (trennt "merken" von
"generalisieren").
