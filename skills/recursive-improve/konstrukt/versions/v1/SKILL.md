---
name: konstrukt
description: Konstrukt-Unterphase des Rekursions-Loops (Revise→Konstrukt→Akt). Der Agent liest Working Memory und baut internes Wissen durch Erfahrung und intrinsische Motivation auf – als behaviorale Schemata (<context,action,emotion>, CCA primitiv/komposit). Nutze diesen Skill, wenn aus freigegebenem (π,I) plus Feedback neue Schemata für den nächsten Zyklus konstruiert werden sollen.
---

# Skill: konstrukt

## Zweck

Konstrukt liest den aktuellen Zustand (Working Memory `M(t)`) und schreibt
neue Schemata zurück (`M(t+1)`) – die kommunikative Schnittstelle für den
nächsten Zyklus. Eltern-Loop: `skills/recursive-improve/SKILL.md`;
Projekt-Doku: `knowledge/lifecycle/rekursion/konstrukt.md`;
Mechanik: `connectors/cca-framework.md`.

Quellen (MD-first, keine Erfindungen):

- JISEM 2025 (Konstruktivismus in MAS):
  https://jisem-journal.com/index.php/journal/article/view/12473
- PDF: https://jisem-journal.com/index.php/journal/article/download/12473/5791/20977
- CCA (Xue et al., IEEE CogMI 2024): https://researchr.org/publication/XueLM24-0

## Wann anwenden

- Nach `Revise` mit Freigabe (`approved`): freigegebenes `(π, I)` liegt vor.
- Wenn Feedback-Traces (Enaction-Ergebnis, Emotions-Feedback, enacted-vs-intended)
  in `M` vorliegen und zu Schemata verdichtet werden sollen.
- NICHT anwenden ohne lesbaren `M(t)`-Stand und ohne Provenienz-Pflicht
  (jedes Schema braucht Beleg + Quelle mit Link).

## Ablauf

### 1. Lesen (`M(t)`)

- Lade `(π, I)`, Ontologie, Working/Episodic Memory, letzten Compare-Bericht
  aus `ergebnisse/rekursion/`.
- Halte fest: Welche Schemata existieren bereits (primitiv vs. komposit),
  welche Valenzen/Gewichte tragen sie?

### 2. Konstruieren (JISEM-Schema + CCA-Hierarchie)

- **JISEM-Schritt (Schema-Selektion, Algorithmus 1):**
  1. Kontextvektor aus Perzeptionen konstruieren.
  2. Kontextbasierte Kandidaten-Selektion.
  3. Valenzbasierte Auswahl des zu enactenden Schemas.
  4. Aktionsteil enacten (das übernimmt `Akt` – hier nur vorbereiten).
  5. Update per intrinsischem Feedback aus Emotions-Modul vorsehen.
- **CCA-Schritt (Hierarchie):**
  - Neue enacted Interactions als **primitiv** ablegen.
  - Wiederkehrende Sequenzen (vorherige + aktuelle Interaction) als
    **komposite** Interaction bottom-up aufbauen (rudimentär → rekursiv).
  - Episodic Memory hierarchisch fortschreiben; Behavior Selection
    berücksichtigt Propositionen aus Sequential System UND Episodic Memory.
  - Selbstmotivation beachten: autotelisch (Sequenz erfolgreich enactet)
    + interactional (positiv bewertete Interaction bevorzugt).
- Verboten: Schemata ohne Feedback-Beleg erfinden; Schema-Format
  `<context,action,emotion>` ohne Freigabe verlassen.

### 3. Schreiben (`M(t+1)`)

- Schreibe neue/geänderte Schemata nach `M` zurück (Working Memory +
  materialisiert wie in `connectors/goedel-agent.md`: Runtime-Memory /
  `logic.py`-Analogon).
- Protokolliere pro Schema: Vorgänger-Trace, Feedback-Wert, Quelle mit Link.
- Lege ein File in `ergebnisse/rekursion/NNN-*.md` an
  (Template: `ergebnisse/rekursion/000-template.md`), Status `pending`
  bis menschliche Freigabe.

### 4. Übergabe an Akt

- `Akt` liest `M(t+1)` und führt `solver` mit den neuen Schemata aus.
- Enacted-vs-intended-Abgleich + Emotions-Feedback fließen als
  Self-Feedback in `t+1` zurück.

## Guardrails

1. Nur belegte Schemata schreiben (MD-first, keine Erfindungen).
2. Interface-/Format-Änderungen nur mit menschlicher Freigabe.
3. Intrinsische Valenz ersetzt NICHT `Compare` mit externem Signal
   (Validierungsset/Test) – Guardrail gegen „konfidente Fehlanpassung".
4. Jede Iteration → `ergebnisse/rekursion/NNN-*.md` mit Quelle (Link).

## Input / Output

Input:

- `M(t)`, Ziel `g`, Feedback-Traces, freigegebenes `(π, I)` aus Revise.

Output:

- `M(t+1)` (neue Schemata + Belege) + `ergebnisse/rekursion/NNN-*.md`.

## Referenzen

- `knowledge/lifecycle/rekursion/konstrukt.md`
- `knowledge/lifecycle/rekursion/index.md` (§2.1, §3 Kreis B)
- `connectors/cca-framework.md`
- `connectors/goedel-agent.md` (Materialisierung von `M`)
