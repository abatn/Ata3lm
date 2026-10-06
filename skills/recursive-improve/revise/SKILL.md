---
name: revise
process: reflective_agent.py
description: "Revise-Unterphase des Rekursions-Loops (Compare→Revise→Konstrukt). Der Agent überarbeitet Regeln im Loop VALIDATE→REFLECT→PIVOT (Reflexion: Actor/Evaluator/Self-Reflection mit episodischem Memory; Closed-Loop Multi-Round) und schreibt das revidierte Modell nur mit menschlicher Freigabe nach Working Memory zurück. Nutze diesen Skill, wenn aus einem belegten Compare-Bericht eine (π,I)-Revision werden soll."
---

# Skill: revise

## Zweck

Überarbeiten, nicht neu erfinden. Projekt-Doku:
`knowledge/lifecycle/rekursion/revise.md`; Connector:
`connectors/reflexion-trace.md`.

Quellen:

- Reflexion: https://arxiv.org/abs/2303.11366
- Code: https://github.com/noahshinn/reflexion
- LoopRAG: https://www.mdpi.com/2075-5309/16/1/196
- SEAA (HMM-Trägheit, strukturelle Reflexion): https://arxiv.org/abs/2609.17331

## Wann anwenden

- Wenn ein belegter Compare-Bericht (Delta + Zahlen + Log) vorliegt.
- NICHT anwenden ohne Compare-Beleg oder ohne Human-Gate für `self_update`.

## Ablauf

### 1. VALIDATE

- Evaluator-Prüfung: Trajektorie `τ` gegen externes Signal (Grader/Test).
- Nur bei bestandenem Check (oder dokumentiertem Fehlschlag als Lernanlass)
  weiter; sonst zurück an Akt (mehr Evidenz nötig).

### 2. REFLECT

- Self-Reflection aus `(τ, r, mem)` erzeugen: verbaler Erfahrungstext `sr`
  (was lief schief, welche Aktion `a_i'` wäre richtig gewesen).
- `sr` in `mem` ablegen (Schranke `Ω` = 1–3 dokumentieren).

### 3. PIVOT

- Actor mit `sr`-Kontext neu planen ODER nur das invalidierte Suffix der
  Route ersetzen (TROVE-Prinzip – Quelle im Projekt-Dok).
- Regeln: Imports prüfen, Interfaces nicht ändern, minimale Diffs.
- Diff + `sr` + Quelle (Link) nach `ergebnisse/rekursion/NNN-*.md`,
  Status `pending` → auf `approved` warten.

### 2b. REFLECT → HMM-Trägheit (SEAA, strukturell)

**Quelle:** SEAA (Self-Emergence Agent Architecture), https://arxiv.org/abs/2609.17331.

Die Reflexion wirkt hier **strukturell**, nicht nur als Text:

- **Verhaltens-Trägheit:** Ein Hidden-Markov-Modell (HMM) kodiert die
  Verhaltens-/kognitive Trägheit als **editierbare Zustandsübergangsmatrix**.
- **Reflexion updated Parameter:** Der Output der Reflexion `sr` aktualisiert
  die **HMM-Übergangswahrscheinlichkeiten** – nicht nur den Prompt-Text.

**Exakte SEAA-Gleichung (Eq. 2):**
```text
P_{t+1} = Normalize( P_t + η · Δ(R_t) )
```
- `Δ(R_t)` = Richtungsmatrix, geparst aus dem Reflexionstext.
- `η` = Reflexions-Lernrate. **Wert (SEAA Table 2): η = 0.05.**
- Row-Normalisierung erhält die Stochasticität.

**Alternative Form (Eq. 3):** `P_t = softmax(log P_base + β·V_t)`, mit
`P_base` diagonal-dominant; **β = 4.0** (SEAA Table 2).

**SEAA-Hyperparameter (Table 2):** K=4 latente Zustände, η=0.05, β=4.0,
`P_base` = diag-dominant/row-stochastic, Bibliothek **hmmlearn**.

**Abgrenzung (Auftrag):** HMM gehört zu SEAA, **nicht** zu MARS
(siehe `knowledge/lifecycle/denken.md` §2/§3).

Details + Simulation (mit Eq. 2): `ergebnisse/hmm-revise.md`.

### 4. Zurückschreiben (nur mit Freigabe)

- Bei `approved`: `(πₜ₊₁, Iₜ₊₁)` + `mem` nach `M` schreiben (`self_update`).
- `continue_improve`: nächste Rekursionstiefe läuft mit neuer Logik;
  Konstrukt übernimmt das revidierte Modell als Startmodell (Kreis-Schluss).

## Guardrails

1. Kein `self_update` ohne `approved`.
2. Kein Revise ohne Compare-Bericht.
3. Keine Interface-Änderungen ohne Freigabe.
4. `mem`-Schranke einhalten + dokumentieren.
5. Jede Revision: Diff + Quelle (Link).

## Input / Output

Input: Compare-Bericht, `(τ, r, mem)`, aktuelles `(π, I)`.
Output: `(πₜ₊₁, Iₜ₊₁)` + `sr` + Diff + `ergebnisse/rekursion/NNN-*.md`.

## Referenzen

- `knowledge/lifecycle/rekursion/revise.md`
- `connectors/reflexion-trace.md`
- `connectors/goedel-agent.md`


## Prozesse (Aufrufe) [Auftrag]

Dieser Skill ruft folgende Prozesse in `data/memory/` auf (MCP-Interface nach Atomic: https://atomicapp.ai/guides/mcp-server/):

- `reflective_agent.py` + `bias_monitor.py` — (π,I)→(π+1,I+1)
- **MCP-Tools:** `memory.write`

Quelle (Auftrag): `skills/README.md` (Skill→Prozess), `ergebnisse/mcp-memory.md` (Atomic).
