---
name: observe
description: Observe-Unterphase des Rekursions-Loops (Akt→Observe→Compare). Der Agent beobachtet Experten-Traces und rekonstruiert hierarchische Strukturen (teleoreaktive Logikprogramme: Skill Chaining vs. Concept Chaining) ohne die Policy zu ändern. Nutze diesen Skill, wenn aus Akt-Traces Skill-Kandidaten plus Erklärungsstruktur für Compare extrahiert werden sollen.
---

# Skill: observe

## Zweck

Lesen, nicht ändern. Projekt-Doku:
`knowledge/lifecycle/rekursion/observe.md`; Connector:
`connectors/observer-agent.md`.

Quellen:

- AAAI 2005: https://aaai.org/papers/0021-fs05-07-021-learning-teleoreactive-logic-programs-by-observation/
- Überblick: https://exa.ai/library/publication/34qxkfcww51

## Wann anwenden

- Wenn Akt-Traces in `M` liegen und Goals + primitive Skill-/Concept-
  Definitionen bekannt sind.
- NICHT anwenden ohne Trace-Beleg; NICHT zur Policy-Änderung (das ist Revise).

## Ablauf

### 1. Lesen

- Lade aus `M`: Akt-Traces, Schemata, Goals.
- Kanäle: `self_inspect` (eigene Skills/Code) + `interact` (`r ← U(E, π)`).

### 2. State-Sequenz rekonstruieren

- Aus Anfangszustand + bekannten Skill-Effekten jeden Folgezustand
  nachstellen (wie im Paper: State-Sequenz aus Primitive-Sequenz).

### 3. Rückwärts erklären

- Letzte Aktion zuerst; pro Schritt entscheiden:
  - **Skill Chaining** (Aktion enthält Ziel als Effekt) → Skill-Kandidat
    mit Ziel-Kopf + Precondition der finalen Skill.
  - **Concept Chaining** (sonst) → Ziel in Subgoals zerlegen,
    Erfüllungsreihenfolge im Verlauf verfolgen, Subsequenzen rekursiv
    lernen; Erfülltes → Preconditions.
- Irrelevante Aktionen als ignoriert markieren (nicht umdeuten).

### 4. Schreiben (Kandidaten, keine Policy)

- Erklärungsstruktur (Subsequenz → Subgoal) + Skill-Kandidaten nach `M`.
- File in `ergebnisse/rekursion/NNN-*.md`: Goal, Trace-Beleg, Kandidaten,
  Quelle mit Link.

## Guardrails

1. Keine Policy-Änderung in Observe.
2. Jeder Kandidat braucht State-Sequenz-Beleg.
3. Ignoriertes explizit kennzeichnen.
4. Beobachtung ≠ Verifikation (Compare folgt).

## Input / Output

Input: `M(t+1)` (Akt-Traces), Goals, Skill-/Concept-Definitionen.
Output: `(s, r)` + Erklärungsstruktur + Kandidaten + `ergebnisse/rekursion/NNN-*.md`.

## Referenzen

- `knowledge/lifecycle/rekursion/observe.md`
- `connectors/observer-agent.md`
