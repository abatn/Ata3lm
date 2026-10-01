---
name: recursive-improve
description: Geschlossener Wahrnehmungs-Handlungs-Lern-Loop (Observe→Compare→Revise→Konstrukt→Akt) mit rekursivem Lesen, Modifizieren und Zurückschreiben desselben Zustands. Nutze diesen Skill, wenn ein Agenten-Modell sich selbst beobachten, extern verifizieren und revidieren soll – nach Gödel Agent (ACL 2025) via Python Monkey Patching, nur mit menschlicher Freigabe.
---

# Skill: recursive-improve

## Zweck

Der Agent durchläuft den geschlossenen Wahrnehmungs-Handlungs-Lern-Loop.
Rekursion = Kommunikationsstruktur zwischen Konstrukt, Akt, Observe,
Compare, Revise (Details: `knowledge/lifecycle/rekursion/index.md`).
Sub-Skill Konstrukt: `skills/recursive-improve/konstrukt/SKILL.md`.

Quellen (MD-first, keine Erfindungen):

- Paper (arXiv): https://arxiv.org/abs/2410.04444
- ACL 2025: https://aclanthology.org/2025.acl-long.1354/
- Code: https://github.com/Arvid-pku/Godel_Agent

## Wann anwenden

- Wenn `solver` / Policy `π` oder Lernlogik `I` verbessert werden soll.
- Wenn Umwelt-Feedback (`U(E, π)`) oder Validierungsset verfügbar ist.
- NICHT anwenden ohne Human-Gate und ohne externes Verifikationssignal.

## Geteilter Zustand

```text
S = (π, I, M)
π = Policy / solver
I = Lernlogik (SELF_IMPROVE / evolve)
M = Working Memory + Ontologie (gemeinsame Sprache aller Phasen)
```

Alle Phasen lesen/schreiben `M`. Im Gödel Agent entspricht `M` dem
Runtime-Memory + `logic.py` – Quelle: https://github.com/Arvid-pku/Godel_Agent.

## Ablauf

### Kreis A – rekursive Selbstbeobachtungsschleife (Observe → Compare → Revise)

1. **Observe**
   - `self_inspect`: eigenen Code aus Runtime-Memory lesen
     (`s ← SELF_INSPECT()`).
   - `interact`: Umwelt-Feedback einholen (`r ← U(E, π)`).
   - Fehler + Traces festhalten, nichts ändern.
   - Quelle: Paper §4.1, Algorithmus 1.

2. **Compare** (extern verifizieren – Pflicht)
   - `action_evaluate_on_task` NUR gegen Validierungsset / Tests /
     Ground Truth ausführen.
   - Delta-Bericht schreiben: Score vorher/nachher + Beleg (Log, Test-Output).
   - Rein internes Self-Scoring ist verboten (Guardrail gegen
     „konfidente Fehlanpassung").
   - Quelle: Paper §4.1 „Environmental Interaction".

3. **Revise** (nur mit Freigabe)
   - `action_adjust_logic` / `self_update`: `(πₜ, Iₜ) → (πₜ₊₁, Iₜ₊₁)`.
   - Regeln aus Goal Prompt: Imports prüfen, Interfaces nicht ändern,
     unnötige Änderungen vermeiden.
   - Diff + Change-Log nach `ergebnisse/rekursion/NNN-*.md` schreiben,
     auf menschliche Freigabe warten.
   - Quelle: Paper §4.1 + Goal Prompt Appendix A.

### Kreis B – schließt den Kreis (Revise → Konstrukt → Akt)

4. **Revise → Konstrukt**
   - Freigegebenes `(πₜ₊₁, Iₜ₊₁)` als neues Initialmodell übernehmen.
   - `continue_improve`: `SELF_IMPROVE(E, π, s, r, g)` rekursiv aufrufen –
     die nächste Tiefe läuft bereits mit der neuen Logik.
   - Quelle: Paper Algorithmus 1, Zeilen `continue_improve`.

5. **Konstrukt → Akt**
   - `solver(agent_instance, task_input)` mit neuer Logik ausführen.
   - Hilfsaktionen erlaubt: `action_run_code` (Python/Bash),
     `action_call_json_format_llm` (LLM-Assistenz).
   - Jede Ausführung loggen; bei Fehler: Sequenz stoppen, Fehlerinfo in
     nächste Rekursion mittragen, auf Original zurückfallen können.
   - Quelle: Paper §4.2 (Thinking Before Acting, Error Handling,
     Additional Tools).

6. **Self-Feedback**
   - `r` + Error-Traces sind das rekursive Signal für den nächsten
     `Observe`-Durchlauf.
   - Abbruchbedingung: kein `continue_improve` ohne belegte Verbesserung
     aus `Compare`.

## Guardrails (verbindlich, vom Skill erzwungen)

1. `self_update` nur nach menschlicher Freigabe des Diffs.
2. **Automatisches Gate (AGENTS.md: §9):** Score-basierte Entscheidung:
   - Score ≥ 95% + alle 8 Stufen "sicher" → automatisch erlaubt
   - Score 70–94% → Human-Gate erforderlich
   - Score < 70% → blockiert (keine Rekursion)
   - Neue Quellen, Interface-Änderungen, self_update → immer Human-Gate
   Siehe `AGENTS.md` §9 für vollständige Tabelle.
3. `Compare` nur mit externem Signal (Validierungsset/Test/Ground Truth).
4. Keine Interface-Änderungen ohne Freigabe.
4. Jede Iteration → ein File in `ergebnisse/rekursion/` mit Quelle
   (Paper-Link und/oder Code-Link).
5. Kein Loop ohne Rekursion: Hauptfunktion rekursiv denken
   (vgl. Paper: „we implement the main function as a recursive function").

## Input / Output

Input:

- Ziel `g`, Task-Input, aktuelles `(π, I, M)`, Referenz (Validierungsset).

Output:

- Neues `(π, I, M)` + `ergebnisse/rekursion/NNN-*.md`
  (Score, Diff, Quelle, Freigabe-Status).

## Minimal-Beispiel (Pseudocode, aus Paper Algorithmus 1 abgeleitet)

```python
# vgl. https://arxiv.org/abs/2410.04444, Algorithmus 1
s = SELF_INSPECT()        # Observe: self_state
r = U(E, pi_0)            # Observe: interact
pi, s = SELF_IMPROVE(pi, s, r, g)  # Compare→Revise→continue_improve

def SELF_IMPROVE(E, pi, s, r, g):
    actions = f(pi, s, r, g)          # thinking before acting
    for a in actions:
        pi, s, r = EXECUTE(E, pi, s, r, a)
    return pi, s

def EXECUTE(E, pi, s, r, a):
    if a.name == "self_state": s = SELF_INSPECT()
    elif a.name == "interact": r = U(E, pi)
    elif a.name == "self_update": pi, s = a.code        # nur mit Freigabe
    elif a.name == "continue_improve":
        pi, s = SELF_IMPROVE(E, pi, s, r, g)           # Rekursion
    return pi, s, r
```

## Referenzen

- `AGENTS.md` (Gesetz: 8 Prinzipien)
- `knowledge/lifecycle/rekursion/index.md` (Kommunikationsstruktur, 5 Phasen)
- `knowledge/lifecycle/rekursion/wissenszyklus-8-stufen.md` (8 Stufen)
- Unterphasen: `konstrukt.md`, `akt.md`, `observe.md`, `compare.md`, `revise.md`
- Sub-Skills: `konstrukt/`, `akt/`, `observe/`, `compare/`, `revise/` (je `SKILL.md`)
- `connectors/goedel-agent.md` (Connector-Doku, Datei-Mapping)
- `connectors/cca-framework.md` (Connector-Doku, Schemata-Hierarchie)
- `connectors/react.md` (Akt: ReAct + Microsoft-Rahmen)
- `connectors/observer-agent.md` (Observe: Learning by Observation)
- `connectors/consistency-gap.md` (Compare: Pass@k vs. Pass^k)
- `connectors/reflexion-trace.md` (Revise: Reflexion + Closed-Loop)
- `ergebnisse/rekursion/` (Iterations-Logs, Provenienz)
