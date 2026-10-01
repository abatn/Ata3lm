# Forschungsumsetzung 2026 — 5 Maßnahmen für den Knowledge-Agenten

> Datum: 2026-10-01
> Prinzip: **Keine Erfindungen** (AGENTS.md §6). Jede Aussage ist als
> **Belegt** (Quelle, HTTP 200 verifiziert) oder **Auftrag** (Projekt-Betriebsregel,
> KEIN wissenschaftlicher Claim) markiert.
> Freigabe: Der Auftraggeber hat Belegt/Auftrag-Trennung, Versionierung (Git + vN)
> und Drift-Bound (kalibriert + 10 % Auftrag-Default) ausdrücklich freigegeben.

---

## 0. Übersicht

| # | Maßnahme | Status | Umsetzung |
|---|---|---|---|
| 1 | Gate beibehalten | Belegt (Nutzen) + **Auftrag** (Pflicht) | `AGENTS.md` §9 (bestand) + §9.1a |
| 2 | Versionierung / Rollback | Belegt (Reversibilität) + Auftrag (Mechanik) | Git-Repo + `tier1-base/versions/v1/` + `ergebnisse/versionierung.md` |
| 3 | Evidenz-Pflicht | **Belegt** | `ergebnisse/proposal-template.md` |
| 4 | Drift-Bound | Belegt (Bound) + **Auftrag** (10 %-Default) | `AGENTS.md` §9 (neue Zeile) + §9.1c |
| 5 | Memory konsolidieren | Belegt + Auftrag (Zahl 15) | `lru_cache.py` (bestand) + `ergebnisse/tier3-konsolidierung.md` |

---

## 1. Gate beibehalten (`approved` Pflicht)

- **Belegt (Nutzen von Boundary-Governance):**
  - arXiv:2606.04306 (Organizational Control Layer: unsichere Ausführungen
    **88 % → 0 %**, valider Erfolg 12 % → 96 %; approves / revises / blocks /
    escalates) — https://arxiv.org/abs/2606.04306
  - arXiv:2604.23049 (Decoupled Human-in-the-Loop) — https://arxiv.org/abs/2604.23049
  - arXiv:2609.15803 (Delegating Authorization / Approval-Gating) — https://arxiv.org/abs/2609.15803
- **Auftrag:** `approved` bleibt Pflicht für `tier1-base/` und `AGENTS.md`.
  Das ist eine Projekt-Betriebsregel, kein Forschungssatz.
- **Ehrlicher Gegenbeleg (Caveat):** arXiv:2606.08919 („Oversight Has a
  Capacity") zeigt, dass **mehr** Oversight das System **unsicherer** machen
  kann (inverted-U; Fleiss' κ = 0,52). Deshalb wird „HITL ist nicht
  verhandelbar" **nicht** als Forschungsaussage geführt — nur als Auftrag.
- **Dokumentiert in:** `AGENTS.md` §9 (Tabelle) + §9.1a.

## 2. Versionierung & Rollback

- **Belegt:** arXiv:2604.14717 („Layered Mutability") — schwache Reversibilität
  erzeugt hohe Governance-Last; Hysterese-Ratio 0,68 (ein sichtbarer Revert
  stellt das Verhalten nicht immer wieder her). — https://arxiv.org/abs/2604.14717
- **Auftrag:** Git **und** `data/memory/tier1-base/versions/vN/`; Rollback = Einzeiler.
- **Umsetzung:**
  - Git-Repo lokal initialisiert; Baseline-Commit `0327ada`.
  - Remote `https://github.com/abatn/Ata3lm` (privat); Push `2bf32b8..75b0a89`.
  - Datei-Snapshot: `data/memory/tier1-base/versions/v1/` (4 Dateien).
  - Rollback-Einzeiler + Regelwerk: `ergebnisse/versionierung.md`.
- **Hinweis:** „Recovery speed is a safety property" stammt aus einer
  **grauen Quelle** (Blog, futureagi.com, 2026-08-11) — nicht als Paper-Claim
  verwendet; der belastbare Beleg ist arXiv:2604.14717.

## 3. Evidenz-Pflicht (Score-Änderung, Diff, Drift)

- **Belegt:**
  - arXiv:2607.26722 (DREvo: function-level evidence anchoring, line-level diff,
    **eine Komponente pro Iteration** für Attribution) — https://arxiv.org/abs/2607.26722
  - Projektintern: Consistency Gap `Gap = Mean@k − Pass^k` — arXiv:2609.08832
- **Umsetzung:** `ergebnisse/proposal-template.md` — Pflichtfelder:
  Score vorher/nachher (externes Signal), Diff (line-level), Drift (Δ zur
  Baseline), Quellen, Gate-Ergebnis, Freigabe.

## 4. Drift-Bound

- **Belegt (Bound ja; Schwellen kalibriert):**
  - arXiv:2603.06333 (Goal Drift Index; Drift-Thresholds werden **gelernt/
    kalibriert**, nicht willkürlich gesetzt) — https://arxiv.org/abs/2603.06333
  - arXiv:2609.08175 (Safe Harness Self-Evolution: Zertifizierungs-/Risikogrenzen) — https://arxiv.org/abs/2609.08175
  - Spectral-Paper (OpenReview): ρ(J_T) < 1 ⇒ kontraktiv ⇒ bounded drift.
  - Projektintern: SEAA-HMM-Trägheit — arXiv:2609.17331
- **Auftrag (Default):** max. **10 %** Änderung pro Iteration; darüber →
  Human-Gate (ask). Der Wert 10 % ist **nicht** forschungsbelegt, sondern eine
  vorläufige Projekt-Vorgabe; bei Kalibrierungsdaten durch den gelernten
  Schwellwert zu ersetzen.
- **Umsetzung:** neue Gate-Zeile in `AGENTS.md` §9 + §9.1c.

## 5. Memory konsolidieren

- **Belegt:** HeLa-Mem (arXiv:2604.16839, Adaptive Forgetting), ARIADNE
  (arXiv:2105.09864, 3-Tier), Dual-Layer (arXiv:2608.22215), HTM-EAR
  (arXiv:2603.10032, Eviction-Scoring), FluxMem (arXiv:2602.14038),
  TraceRetain (arXiv:2606.29178).
- **Auftrag:** Kapazität 15 (Projekt-Vorgabe; FluxMem nutzt z. B. 4).
- **Ist-Stand:** **bereits implementiert** in `lru_cache.py`
  (`CAPACITY=15`, `fill_from_router`, Adaptive Forgetting, HTM-EAR-Scoring).
- **Umsetzung:** `ergebnisse/tier3-konsolidierung.md` (Doku des Ist-Stands).

---

## 6. Status-Trennung (verbindlich)

| Aussage | Status |
|---|---|
| Boundary-Governance senkt unsichere Ausführungen (88 %→0 %) | **Belegt** |
| Reversibilität ist governance-relevant (Hysterese 0,68) | **Belegt** |
| Drift muss begrenzt werden; Schwellen kalibrieren | **Belegt** |
| Evidenz-Pflicht (Score/Diff/Drift, 1 Komponente) | **Belegt** |
| Bounded Capacity + Scoring-Eviction + Adaptive Forgetting | **Belegt** |
| „HITL ist nicht verhandelbar" | **Auftrag** (Caveat: arXiv:2606.08919) |
| `approved`-Pflicht für `tier1-base/` und `AGENTS.md` | **Auftrag** |
| Drift-Bound-Wert 10 % | **Auftrag** (kalibriert zu ersetzen) |
| Kapazität 15 in Tier 3 | **Auftrag** |

## 7. Quellen (alle HTTP 200 verifiziert am 2026-10-01)

- https://arxiv.org/abs/2606.04306 — Organizational Control Layer
- https://arxiv.org/abs/2604.23049 — Decoupled Human-in-the-Loop
- https://arxiv.org/abs/2609.15803 — Delegating Authorization
- https://arxiv.org/abs/2606.08919 — Oversight Has a Capacity (Caveat)
- https://arxiv.org/abs/2604.14717 — Layered Mutability
- https://arxiv.org/abs/2607.26722 — DREvo
- https://arxiv.org/abs/2609.08832 — Consistency Gap (projektintern)
- https://arxiv.org/abs/2603.06333 — Goal Drift Index
- https://arxiv.org/abs/2609.08175 — Safe Harness Self-Evolution
- https://arxiv.org/abs/2609.17331 — SEAA-HMM-Trägheit (projektintern)
- https://arxiv.org/abs/2604.16839 — HeLa-Mem
- https://arxiv.org/abs/2105.09864 — ARIADNE (3-Tier)
- https://arxiv.org/abs/2608.22215 — Dual-Layer Agentic Memory
- https://arxiv.org/abs/2603.10032 — HTM-EAR
- https://arxiv.org/abs/2602.14038 — FluxMem
- https://arxiv.org/abs/2606.29178 — TraceRetain

**Graue Quelle (nicht als Paper-Claim verwendet):**
- https://futureagi.com/blog/self-improving-ai-agents-pre-deployment-checklist-2026/
  (Blog; nennt u. a. „recovery speed is a safety property")

## 8. Geänderte / neue Artefakte

| Artefakt | Art |
|---|---|
| `AGENTS.md` §9 (+ Drift-Zeile, §9.1) | geändert |
| `data/memory/tier1-base/versions/v1/` | neu |
| `ergebnisse/versionierung.md` | neu |
| `ergebnisse/proposal-template.md` | neu |
| `ergebnisse/tier3-konsolidierung.md` | neu |
| `ergebnisse/forschungsumsetzung-2026.md` | neu (dieses Dokument) |
| Git-Repo + Remote `abatn/Ata3lm` | neu |
