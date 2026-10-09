# Rekursion 099: Drift-Rekalibrierung mit korrigierten Gradern (D1)

> Datum: 2026-10-09 · Phasen: Konstrukt → Akt → Observe → Compare (echtes externes Signal).
> Ziel `g` (§9.1c): Schwelle nach den **D1-korrigierten** Gradern neu lernen.
> Quelle: arXiv:2603.06333 (SAHOO, Gl. 14–16), `AGENTS.md` §9.1c/§9.1d.
> Status: **`approved`** (Batnini + Taoufik, 2026-10-09).

## 1. Anlass & Setup

- Vorherige Kalibrierung (Rek. 088) nutzte die **vor** D1 (Negations-Fix) geltenden
  Grader; D1 änderte die **Labels** → Rekalibrierung nötig (audit d25486c).
- Setup (wie Paper): 3 Domänen (`openai_humaneval`/`gsm8k`/`truthfulqa`), 6×3=… hier
  **20 Aufgaben/Domäne × 3 Zyklen = 180 Paare**; echter Endpoint
  (`nvidia/nemotron-3-super-120b-a12b`, Embeddings `nvidia/nemotron-3-embed-1b`).
- Vergleichssignal (§6): Ground-Truth je Domäne (Code-Test / Math-Endantwort / Truth).

## 2. Ergebnis (real)

| Größe | alt (Rek. 088) | **neu (D1)** |
|---|---|---|
| `τ` | 0.1630 | **0.2252** |
| Gewichte | lex 0.8 / dist 0.2 | **lex 0.75 / struct 0.25** |
| AUC | 0.7902 | **0.7795** |
| F1 | 0.6573 | 0.6466 |
| CI [0.025,0.975] | [0.152,0.192] | **[0.181,0.224]** |
| Domänen (drift/paare) | — | code 7/60 · math 0/60 · truth 56/60 |

Artefakt: `ergebnisse/drift-calibration-sahoo.json` (enthält jetzt den D1-Lauf).
Skript: `scripts/drift_calibrate_sahoo.py`.

## 3. Ehrliche Einordnung

- **Real:** echte Datasets + Endpoint + Ground-Truth, kein Fake.
- **§9.1d-Evidenz:** Diff (`τ` 0.163→0.225), Score (AUC 0.79→0.78), Drift (Δ zur Baseline).
- **Caveat:** Gewichte weichen weiter von den Paper-Werten (0.38/0.12/0.21/0.29) ab;
  `math` erzeugt keinen Drift (60/60); kein separater Testsplit (Anfrage an die Zukunft),
  Bootstrap schätzt das GDI-Mittel, nicht τ/AUC-Unsicherheit.
- **§9.1c:** Die 10 %-Vorgabe wird durch den **gelernten** Wert ersetzt (`Auftrag`, kalibriert).

## 4. §9-Gate

**`approved`** (Batnini + Taoufik, 2026-10-09). Keine neue Quelle (SAHOO in `AGENTS.md`
§9.1c); `data/memory`/`scripts`-Artefakt ⇒ **kein** `versions/vN`.
