# Proposal-Template (Aufgabe 3 — Evidenz-Pflicht)

> Zweck: Jeder Vorschlag (Rekursion / `self_update`) enthält **Score-Änderung,
> Diff und Drift (Δ zur Baseline)** — damit ein Reviewer ohne Archäologie
> entscheiden kann.
> Status: **Belegt**. Quellen:
> - arXiv:2607.26722 (DREvo): function-level evidence anchoring, line-level diff,
>   Einzelkomponenten-Änderungen (ein Component pro Iteration → Attribution) —
>   https://arxiv.org/abs/2607.26722
> - Projektintern: Consistency Gap, Gap = Mean@k − Pass^k — arXiv:2609.08832
> - Gate: `AGENTS.md` §9 / §9.1

---

## PROPOSAL `NNN` — <Kurztitel>

### 0. Metadaten

| Feld | Wert |
|---|---|
| Datum | YYYY-MM-DD |
| Iteration | `t → t+1` |
| Phase | Konstrukt / Akt / Observe / Compare / Revise |
| Betroffenes Artefakt | `pfad/zur/datei` |
| Komponenten-Typ | Code / Doku / Memory / Interface |
| Autor | <wer> |

### 1. Ziel `g`

- Ziel: <was soll erreicht werden>
- Task-Input: <konkreter Input>

### 2. Baseline (vorher)

| Feld | Wert |
|---|---|
| `π` (Modell/Policy) | <Version/Datei> |
| Score (externes Signal) | `<k>/<n>` = `<p> %` |
| Signal-Quelle | Validierungsset / Test / Ground Truth |
| Drift-Referenz | <Baseline-Snapshot (Git-Hash / versions/vN)> |

### 3. Änderung (Diff, line-level)

```diff
- <alte Zeile(n)>
+ <neue Zeile(n)>
```

- Geänderte Komponenten: **1** (Ziel; mehrere nur mit Begründung — DREvo)
- Interface-Änderung? **ja/nein** (wenn ja → immer Human-Gate, §9)

### 4. Score-Änderung

| Testfall | Kriterium | vorher | nachher |
|---|---|---|---|
| 1 | ... | fail | pass |
| 2 | ... | pass | pass |

- **Score vorher:** `<k>/<n>` = `<p> %`
- **Score nachher:** `<k>/<n>` = `<p> %`
- **Δ Score:** `<±p>` Prozentpunkte

### 5. Drift (Δ zur Baseline)

- **Definition (Auftrag, praktische Messung):**
  `Δ = geänderte Zeilen / Gesamtzeilen des Artefakts`
  (line-level, vgl. DREvo; für Modell-Parameter: `‖πₜ − π₀‖ / ‖π₀‖`).
- **Drift-Wert:** `Δ = <wert> %`
- **Drift-Bound:** Default `10 %` (**Auftrag**, §9.1c); kalibriert zu ersetzen
  (arXiv:2603.06333 lernt Thresholds; Spectral-Paper: ρ(J_T) < 1 ⇒ bounded).
- **Überschritten?** ja/nein → wenn ja: **Human-Gate (ask)**.

### 6. Evidenz / Quellen

- Quelle 1: <Paper-Link, HTTP 200>
- Quelle 2: <Code-Link>
- Interne Referenz: <Datei:Zeile>

### 7. Gate-Entscheidung (§9)

| Bedingung | Wert | Ergebnis |
|---|---|---|
| Score | `<p> %` | allow / ask / deny |
| Neue Quelle? | ja/nein | ask wenn ja |
| Interface-Änderung? | ja/nein | ask wenn ja |
| Drift ≤ Bound? | ja/nein | ask wenn nein |

- **Gate-Ergebnis:** `allow` / `ask` / `deny`

### 8. Freigabe

- Status: `pending | approved:<wer, wann> | rejected:<grund>`
- Human-Gate-Referenz: `ergebnisse/rekursion/NNN-*.md`

---

## Pflichtfelder (Kurzcheck)

- [ ] Score vorher/nachher mit externem Signal
- [ ] Diff (line-level)
- [ ] Drift-Wert + Bound-Vergleich
- [ ] Quelle(n) mit Link
- [ ] Gate-Ergebnis + Freigabe-Status
