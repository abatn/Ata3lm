# cognize-Test (minimaler, belegbarer Fall)

> Datum: 2026-10-01
> Zweck: `skills/cognize/SKILL.md` real ausführen — belegte Inferenz schreiben,
> ungestützte Kandidaten und einen Negativtest als `rejected` dokumentieren.
> Prinzip: Keine Erfindungen (§6); nur belegte Prämissen.

## 1. Geladene Ontologie + Prämissen

**Ontologie (Tier 1):** 8 Stufen + 5 Phasen (`data/memory/tier1-base/ontology.md`);
bi-temporale Regel `Fakt --valid_at/invalid_at--> Zeitfenster`
(`core-relations.md`, Quelle: Graphiti, https://arxiv.org/abs/2501.13956).

**Belegte Prämissen (aus `knowledge/structured/`):**

| # | Triple | Quelle (Datei) | Quellen-Link |
|---|---|---|---|
| P1 | `Solver berechne_median --supersedes--> Solver berechne_durchschnitt` | `relations-rekursion-solver.md` | https://arxiv.org/abs/2501.13956 |
| P2 | `Solver berechne_median . gueltig_von = 2026-10-01` | `entity-solver-berechne-median.md` | https://docs.python.org/3/library/functions.html#sorted |

## 2. Ausführung (Inferenz-Schritt 3 des Skills)

- **Regel R1** (Graphiti-Supersede): Wenn `X --supersedes--> Y` und
  `X.gueltig_von = d`, dann `Y --invalid_at--> d`.
- Angewendet auf P1 + P2 → materialisiert ein **neues Triple**.

## 3. Ergebnis

| Fall | Kandidat | Status | Grund |
|---|---|---|---|
| C1 (belegt) | `Solver berechne_durchschnitt --invalid_at--> 2026-10-01` | **belegt** | P1+P2 mit Quellen-Link; Regel R1 (Graphiti) |
| C2 (ungestützt) | `Fast Write Routing --improves--> Solver berechne_median` | **rejected** | keine belegte Prämisse, kein Quellen-Link |
| C3 (Negativtest) | `Solver finde_minimum --supersedes--> Solver berechne_median` (Prämisse **ohne** Quellen-Link) | **rejected** | fehlender Quellen-Link |

## 4. Geschriebene Dateien (`knowledge/cognition/`)

| Datei | Status |
|---|---|
| `inference-001.md` | `belegt` (Prämissen + Quellen-Link + Regel-ID R1) |
| `inference-002.md` | `rejected` (unbelegt) |
| `inference-003.md` | `rejected` (Negativtest: Prämisse ohne Quellen-Link) |

## 5. Verifikation (reale Ausgabe)

```text
Dateien in knowledge/cognition/: 3

inference-001.md       Status=belegt   Regel-ID=True Prämissen=True Quellen-Link=True  Grund=False
inference-002.md       Status=rejected Regel-ID=True Prämissen=True Quellen-Link=False Grund=True
inference-003.md       Status=rejected Regel-ID=True Prämissen=True Quellen-Link=False Grund=True

Alle Regeln erfüllt: inference-001 = belegt (mit Quelle/Prämissen); inference-002/003 = rejected (mit Grund)
```

## 6. Testkriterien des Auftrags

| Kriterium | Erfüllt? |
|---|---|
| Ontologie + belegte Prämisse geladen (`entity-*.md` mit Quellen-Link) | ✅ |
| Neue Verknüpfung mit `Status: belegt` + Prämissen + Quellen-Link geschrieben | ✅ (`inference-001.md`) |
| Ungestützte Kandidaten als `rejected` mit Grund dokumentiert | ✅ (`inference-002.md`) |
| Negativtest: Prämisse ohne Quellen-Link → `rejected`, nicht `belegt` | ✅ (`inference-003.md`) |

## Quellen (HTTP 200)

- https://arxiv.org/abs/2501.13956 (Graphiti, bi-temporale Kanten)
- https://docs.python.org/3/library/functions.html#sorted
