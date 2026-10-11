# Rekursion 111: SAGE-basierter per-Item Acceptance-Gate (Code, additiv)

> Datum: 2026-10-11 · Phasen: Konstrukt → Akt (Code) → Compare (offen: echter Lauf)
> Ziel g (§9.1d/§6): Aggregat-Vergleich durch per-Item-gepaarten Test + Bootstrap-KI
> ersetzen (keine „konfidente Fehlanpassung").
> Status: **pending** (Code+Tests lokal; echter Eval-Lauf/Akzeptanz-Entscheid offen).
> Quelle (Belegt): SAGE arXiv:2609.36043 + `AGENTS.md` §9.1d/§6.

## 1. Anlass

Der Θ′-Vergleich in Rek. 103 war ein **naives Aggregat**: `em_base` 8/200 vs.
`em_adapter` 9/200 (Δ = +1, p ≈ 1.0). Ein Aggregat-Delta dieser Größe
**verschleiert Einzel-Regressionen**: Gewinne und Verluste auf Item-Ebene heben
sich in der Summe auf und erzeugen eine „konfidente Fehlanpassung" (§6) —
scheinbare Gleichheit ohne systematischen Beleg. Deshalb wird der Vergleich auf
einen **per-Item-gepaarten** Test mit **Bootstrap-Konfidenzintervall** umgestellt.

## 2. Artefakt (neu, additiv)

`data/memory/acceptance_gate.py` (neu, **nur stdlib**, deterministisch über `seed`):

| Funktion | Aufgabe |
|---|---|
| `per_item_compare(base, cand)` | **gepaarter** Per-Item-Vergleich zweier Antwort-Sets |
| `sign_test_p(wins, losses)` | **einseitiger** gepaarter Signifikanztest |
| `bootstrap_delta_ci(...)` | Bootstrap-Konfidenzintervall des Δ (SAS-Bootstrap als Technik) |
| `evaluate(...)` | liefert `{"decision": "accept\|reject\|abstain", "p", "delta", "ci", ...}` |

**Gate-Logik (SAGE):** committet **nur bei zuverlässigen Gewinnen**, sonst
`abstain` (kein Commit bei unzuverlässigem Signal).

Tests: `tests/test_acceptance_gate.py`.

**Additiv (Belegt):** **keine Interface-Änderung** an bestehenden Modulen und
**kein Wiring** in den Runner (separater §9-Antrag).

## 3. Evidenz (§9.1d: Score-Δ + Diff + Drift)

- **Baseline (Rek. 103, echt):** `em_base` 8/200, `em_adapter` 9/200, Δ = +1,
  p ≈ 1.0 ⇒ `rejected` (kein systematischer Gewinn).
- **Geplante Messung:** ΔEM **per Item** + **Bootstrap-KI 95 %** (SAGE;
  SAS-Bootstrap als Technik) — Entscheidung `accept` / `reject` / `abstain`.
- **Diff:** **neue Dateien** (Modul + Tests), **kein** Interface-/Signaturwechsel.
- Vorlage: `ergebnisse/proposal-template.md`.

## 4. Drift

Referenz: `governance-mcp` **`drift_index`** (Projekt-JSD-DI, τ = 0.02).
**Aktuell n/a** — die Änderung ist **additiv** (keine Modell-/Policy-Änderung),
also keine Drift-Referenz zu messen.

## 5. Bewertung

Additiv und **getestet**; die **WIRKUNG ist noch nicht belegt** (kein echter
Lauf). Die Existenz des Gates ersetzt **keine** Akzeptanz-Entscheidung — diese
liefert erst der reale per-Item-Eval.

## 6. Quellen (belegt)

- SAGE: arXiv:2609.36043 (28.09.2026), „A Statistical Acceptance Gate for
  Self-Evolving Agents" — per-item paired comparison + one-sided paired test;
  Commit nur bei zuverlässigen Gewinnen, sonst `abstain`.
- `AGENTS.md` §9.1d (Evidenz-Pflicht) / §6 (keine Erfindungen).
- Rek. 103 (`ergebnisse/rekursion/103-theta-prime-negativ.md`): 8/200 vs. 9/200,
  Δ = +1, p ≈ 1.0 ⇒ `rejected`.
- `ergebnisse/experiment-register.md`.

## 7. Nächster Schritt

- **Per-Item-Eval im echten Lauf (P-109)** → reale `accept`/`reject`/`abstain`-Entscheidung.
- **Optionales Wiring** des Gates in den Runner: **Human-Gate** (§9) vor der Umsetzung.
