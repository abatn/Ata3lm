# Observe – Unterphase der Rekursions-Kommunikation

> Lab-Prinzip: Projekt + Skills + Connectors + Knowledge. MD-first.
> Eltern-Dok: `knowledge/lifecycle/rekursion/index.md` (§2.3).
> Observe liest den Zustand – das ist der Input für Compare.
> Mechanismus: Experten-Traces beobachten und hierarchische Strukturen
> rekonstruieren (Learning by Observation teleoreaktiver Logikprogramme).

## 1. Definition (aus Quelle, kein Eigenbau)

„The learning system observes the traces of primitive skills taken from an
expert working on a known problem and learns new higher level skills based
on this information."

- Quelle: Salomaki, Choi, Nejati, Langley (2005):
  Learning Teleoreactive Logic Programs by Observation –
  https://aaai.org/papers/0021-fs05-07-021-learning-teleoreactive-logic-programs-by-observation/
- Überblick: https://exa.ai/library/publication/34qxkfcww51 (publ. 2005-01-01)

„Observer Agent (Learning-by-Observation)" ist Auftrags-Vokabular für genau
dieses lernende System; der Beiname ist Mapping, keine Paper-Behauptung.

## 2. Formalismus (belegt)

Teleoreaktive Logikprogramme = zwei Wissensbasen (aus Paper abgeschrieben):

1. **Concepts** – erkennen Situationsklassen, beschreiben Umgebung auf
   höherem Abstraktionsniveau.
2. **Skills** – hierarchische Skill-Menge, per Goals indiziert; höhere Skills
   verweisen auf Subskills (Zielhierarchie + reaktive Ausführung).

Verwandt (im Paper genannt, hier nur referenziert, nicht ausgeführt):
Teleo-Reactive Trees (Nilsson 1994), Icarus (Shapiro 2001), HTNs.

## 3. Lernverfahren (aus Paper abgeschrieben)

Input: Ziel des Experten + Anfangszustand + Sequenz primitiver
Expert-Aktionen (z. B. Blocks World: `(unstack C B)(putdown C)…`).

1. **State-Sequenz rekonstruieren:** aus Anfangszustand + primitiven Skills
   (Effekte bekannt) jeden Folgezustand nach Ausführung bestimmen.
2. **Rückwärts abarbeiten** (letzte Aktion zuerst), pro Schritt Wahl zwischen:
   - **Skill Chaining:** Aktuelle Skill enthält das Ziel als Effekt → neuer
     Skill mit Ziel als Kopf, Precondition der finalen Skill als Precondition,
     finale Primitive als einziger Subskill.
   - **Concept Chaining:** Aktuelle Skill enthält das Ziel NICHT → Ziel in
     Subgoals zerlegen (aus Concept-Definition), Reihenfolge der
     Subgoal-Erfüllung im State-Verlauf verfolgen, beitragende
     Subsequenzen rekursiv lernen; bereits erfüllte Subgoals werden
     Preconditions des neuen Skills.
3. **Irrelevantes ignorieren:** Skills ohne Beitrag zum Ziel werden
   übergangen (inkl. verschränkter Subtraces bei wechselnden Subgoals).
4. Pro Erklärungsknoten **eine Skill-Klausel** lernen (nur lokale Information
   für Conditions).

Komplementär (Ichise, Shapiro, Langley – hierarchische Skills aus
Observation, 3-stufig, hier nur referenziert):

1. Flache ungeordnete Regeln lernen (z. B. CN2),
2. per Condition-/Action-Promotion zu Klassifikations-Hierarchie
   kombinieren (ähnliche Aktionen gruppieren, Spezialfälle isolieren),
3. in hierarchisches reaktives Programm (Icarus) übersetzen + vereinfachen.

Domänen (nur zitiert): Blocks World, FreeCell, Tower of Hanoi, In-City-Driving.

## 4. Rekursionsschnittstelle (lesen → Input für Compare)

```text
M(t+1) ──Observe──▶ (s, r, Erklärungsstruktur)
   │                      │
   │ liest: Traces,       ▼
   │ Schemata, Goals   Compare prüft r gegen externe Referenz
```

- **Lesen:** Observe liest `M` (Akt-Traces, Schemata aus Konstrukt, Goals).
  Zwei Kanäle wie im Eltern-Dok: `self_inspect` (eigener Code/Skills) +
  `interact` (Umwelt-Feedback `r ← U(E, π)`).
- **Schreiben:** Erklärungsstruktur (welche Subsequenz erfüllt welches
  Subgoal) + rekonstruierte Skill-Kandidaten nach `M` zurück – noch OHNE
  Policy-Änderung (das ist Revise, mit Freigabe).
- **Weitergabe:** `r` + Beleg-Traces sind der Compare-Input.

## 5. Input / Output

Input: `M(t+1)` (Akt-Traces), Goals, primitive Skill-/Concept-Definitionen.

Output: `(s, r)` + Erklärungsstruktur + Skill-Kandidaten + File in
`ergebnisse/rekursion/NNN-*.md`.

## 6. Guardrails

1. Observe ändert keine Policy (nur lesen + Kandidaten vorschlagen).
2. Jeder Kandidat braucht Trace-Beleg (State-Sequenz + Expert-Aktion).
3. Irrelevante Aktionen explizit als ignoriert markieren (kein
   Hineininterpretieren).
4. Compare-Pflicht bleibt: Beobachtung ≠ Verifikation.

## 7. Quellen (keine Erfindungen)

- Salomaki et al. (2005), AAAI FS05 –
  https://aaai.org/papers/0021-fs05-07-021-learning-teleoreactive-logic-programs-by-observation/
- Überblick: https://exa.ai/library/publication/34qxkfcww51
- Choi & Langley (2005): Learning TRLP from Problem Solving, ILP05 –
  http://www.isle.org/~langley/papers/icarus.trlp.ilp05.pdf
- Langley et al. (2006): Learning HTNs by Observation, ICML06 –
  http://www.isle.org/~langley/papers/icarus.lbo.icml06.pdf
- Ichise, Shapiro, Langley: dreistufiges Verfahren –
  http://www.isle.org/~dgs/papers/lhso.DS02.pdf
- Skill: `skills/recursive-improve/observe/SKILL.md`
- Connector: `connectors/observer-agent.md`
