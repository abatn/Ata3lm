# Rekursion 088: Reale Live-Läufe — 8-Stufen/5-Phasen + größeres Kalibrierset (n=180)

> Datum: 2026-10-08 · Phasen: Konstrukt → Akt → Observe → Compare.
> Ziel `g`: echte Live-Verifikation (§7) von (a) 8-Stufen-Zyklus + 5-Phasen-Rekursion
> und (b) größerem Drift-Kalibrierset. Quellen: `AGENTS.md` §3, rekursion/index.md,
> §9.1c, §6. Status: **`approved`** (Batnini + Taoufik, 2026-10-08).

## 1. Live-Run 8 Stufen + 5 Phasen (echt)

- Driver: `scripts/live_run.py` (Retry ergänzt für transiente 503/429).
- Lauf: 3 reale ZsRE-Aufgaben, echter Endpoint (Small/Large/Router).
- Ergebnis `ergebnisse/live-run.json`: je Aufgabe `cycle.stages` (8), `cycle.gate`,
  `cycle.DI`, `recursion.phases` (5), `recursion.observed`, `recursion.score`.
- **Real:** echter Endpoint, keine Fakes. Endpoint war zwischenzeitlich **503
  überlastet** → Retry (`tests/_live.py`-Muster) war nötig.

## 2. Größeres Kalibrierset (n=180)

- Driver: `scripts/drift_calibrate_sahoo.py --per-domain 20 --cycles 3`.
- Ergebnis `ergebnisse/drift-calibration-sahoo.json`:

```json
{ "n": 180, "tau": 0.24012,
  "weights": { "sem": 0.0, "lex": 0.85, "struct": 0.0, "dist": 0.15 },
  "auc": 0.7604, "f1": 0.6496, "ci": { "lo": 0.17275, "hi": 0.21367 },
  "per_domain": { "code": {"no_drift":54,"drift":6},
                  "math": {"no_drift":59,"drift":1},
                  "truth": {"no_drift":6,"drift":54} } }
```

- **Robuster als n=54** (Rek. 085): AUC **0.699 → 0.760**; Gewichte jetzt
  `lex 0.85 + dist 0.15` (statt degeneriert `lex 1.0`).
- **Caveat (ehrlich):** weiterhin von Paper-Gewichten (0.38/0.12/0.21/0.29) entfernt;
  `math` liefert fast keinen Drift (1/60). `τ` gilt für die **GDI-Skala**.

## 3. Reproduzierbarkeit

```bash
.venv/bin/python scripts/live_run.py --tasks 3 --seed 42
.venv/bin/python scripts/drift_calibrate_sahoo.py --per-domain 20 --cycles 3
```

Hinweis: Das Artefakt `ergebnisse/drift-calibration-sahoo.json` enthält jetzt den
**n=180**-Lauf; die n=54-Werte bleiben in Rekursion 085 dokumentiert (Provenienz).

## 4. §9-Gate

**`approved`** (Batnini + Taoufik, 2026-10-08). Keine neue Quelle. `data/memory/` /
`scripts/` ⇒ **kein** `versions/vN`.
