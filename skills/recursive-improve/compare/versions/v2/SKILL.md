---
name: compare
description: Compare-Unterphase des Rekursions-Loops (Observe→Compare→Revise). Der Agent berechnet Ähnlichkeit und Konsistenz (Pass@k vs. Pass^k, Consistency Gap = Mean@k − Pass^k) ausschließlich auf externen verifizierbaren Signalen (Grader, Code-Ausführung, DB). Nutze diesen Skill, wenn aus Observe-Output ein belegter Delta-Bericht für Revise werden soll.
---

# Skill: compare

## Zweck

Verifizieren, nicht raten. Projekt-Doku:
`knowledge/lifecycle/rekursion/compare.md`; Connector:
`connectors/consistency-gap.md`.

Quellen:

- Paper: https://arxiv.org/abs/2609.08832
- Blog: https://huggingface.co/blog/ibm-research/altk-evolve-consistency

## Wann anwenden

- Wenn `(s, r)` + Traces aus Observe vorliegen UND eine externe Referenz
  (Grader/Test/DB/Ground Truth) verfügbar ist.
- NICHT anwenden mit nur internem Scoring (→ als `rejected` loggen).

## Ablauf

### 1. Referenzen fixieren

- Externes Signal wählen: Grader (z. B. AppWorld-Grader), Code-Run
  (Interpreter/Compiler), DB-/Ground-Truth-Abgleich, Validierungsset.
- k (Wiederholungen) + n (Tasks) + Grader-Version notieren.

### 2. Ähnlichkeit berechnen

- Trajektorien-/Ergebnis-Übereinstimmung über Läufe bestimmen;
  Flip-anfällige Entscheidungspunkte markieren (Analyzer-Logik:
  pro Entscheidungspunkt k Completions resamplen, Default k=5).

### 3. Konsistenz berechnen

- Tabelle: Mean@k, Pass@k, Pass^k, Gap = Mean@k − Pass^k.
- Es gilt Pass^k ≤ Mean@k ≤ Pass@k (Verletzung → Messfehler, neu messen).
- Beide Werte berichten + begründen, welcher zählt
  (Retry möglich → Pass@k; Produktion → Pass^k).

### 4. Delta-Bericht schreiben

- besser/gleich/schlechter + Zahlen + Log-Beleg nach
  `ergebnisse/rekursion/NNN-*.md` (Quelle mit Link).
- Ohne Beleg kein `continue_improve` (Abbruchbedingung).

## Guardrails

1. Kein externes Signal → kein gültiges Compare.
2. k/n/Grader immer angeben.
3. Pass@k vs. Pass^k nie vermischen.
4. Kein Revise ohne Delta-Bericht.

## Input / Output

Input: `(s, r)`, Traces, externe Referenz.
Output: Metrik-Tabelle + Delta-Bericht + `ergebnisse/rekursion/NNN-*.md`.

## Referenzen

- `knowledge/lifecycle/rekursion/compare.md`
- `connectors/consistency-gap.md`


## Prozesse (Aufrufe) [Auftrag]

Dieser Skill ruft folgende Prozesse in `data/memory/` auf (MCP-Interface nach Atomic: https://atomicapp.ai/guides/mcp-server/):

- `evaluator_version.py` — externes Signal/Score
- **MCP-Tools:** `memory.read`

Quelle (Auftrag): `skills/README.md` (Skill→Prozess), `ergebnisse/mcp-memory.md` (Atomic).
