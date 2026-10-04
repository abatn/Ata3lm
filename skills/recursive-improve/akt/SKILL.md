---
name: akt
description: "Akt-Unterphase des Rekursions-Loops (Konstrukt→Akt→Observe). Der Agent führt Aktionen aus im Loop DEFINE→EXPERIMENT→OBSERVE→RELATE (ReAct: Thought/Action/Observation interleaved) und schreibt Traces plus Artefakte nach Working Memory – das Signal für Observe/Compare im nächsten Durchlauf. Nutze diesen Skill, wenn ein definiertes Modell in einer Umgebung ausgeführt werden soll."
---

# Skill: akt

## Zweck

Ausführen, nicht bewerten. Projekt-Doku:
`knowledge/lifecycle/rekursion/akt.md`; Connector: `connectors/react.md`.

Quellen:

- ReAct: https://arxiv.org/abs/2210.03629
- Microsoft: https://www.microsoft.com/de-de/microsoft-copilot/copilot-101/build-ai-agents

## Wann anwenden

- Wenn `π` (Schemata aus Konstrukt) + Task-Input + Tool-Zugriff vorliegen.
- NICHT anwenden ohne DEFINE (Grenzen/Tools unklar) oder ohne Logging.

## Ablauf

### 1. DEFINE

- Task, Grenzen (was darf der Agent, was nicht), Tool-Zugriff, Wissensquellen,
  Erfolgskriterium festhalten (vgl. Microsoft: Aufgabe definieren, Grenzen,
  Informationen, Richtlinien).
- Initial Policy + Goal Prompt bereitstellen (Gödel-Mapping).

### 2. EXPERIMENT

- Aktion ausführen: `solver` / `execute_action` / `action_run_code`
  (Python/Bash) / Tool- oder API-Call.
- Reasoning-Trace VOR der Aktion notieren (ReAct-Thought):
  Plan-Hypothese + erwartete Observation.

### 3. OBSERVE

- Observation einsammeln: Tool-Output, Score-Rohwert, Fehler-Trace.
- Nichts bewerten – nur festhalten (Bewertung ist Compare).

### 4. RELATE

- Trace fortschreiben: Plan induzieren/nachführen, Exceptions vermerken
  (ReAct: reason to act + act to reason).
- Bei Fehler: Sequenz stoppen, Fehlerinfo für `t+1` sichern
  (Gödel §4.2 Error Handling).

## Schreiben nach M

Hänge an `M` an: Thought → Action → Observation pro Schritt, Artefakte,
Fehler-Traces. Lege ein File in `ergebnisse/rekursion/NNN-*.md` an
(Aktion, Ergebnis roh, Quelle mit Link).

## Guardrails

1. DEFINE zuerst, dann handeln.
2. Alles loggen – ungeloggte Aktionen sind für Observe verloren.
3. Akt-Erfolg ≠ Compare-Beleg (externe Verifikation bleibt Pflicht).
4. Neue Tools/Aktionen nur mit Freigabe.

## Input / Output

Input: `M(t)`, `π`, Task-Input, Tool-Zugriff.
Output: `M(t+1)` (Traces + Artefakte) + `ergebnisse/rekursion/NNN-*.md`.

## Referenzen

- `knowledge/lifecycle/rekursion/akt.md`
- `connectors/react.md`
- `connectors/goedel-agent.md`


## Prozesse (Aufrufe) [Auftrag]

Dieser Skill ruft folgende Prozesse in `data/memory/` auf (MCP-Interface nach Atomic: https://atomicapp.ai/guides/mcp-server/):

- `pipeline.py` — π ausführen
- **MCP-Tools:** `memory.write`

Quelle (Auftrag): `skills/README.md` (Skill→Prozess), `ergebnisse/mcp-memory.md` (Atomic).
