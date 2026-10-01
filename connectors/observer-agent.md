# Connector: Observer Agent (Learning by Observation teleoreaktiver Logikprogramme)

> Lab-Prinzip, MD-first. „Observer Agent" ist Auftrags-Vokabular für das im
> Paper beschriebene lernende System (Mapping, keine Paper-Behauptung).

## Identität

- Salomaki, Choi, Nejati, Langley (2005): Learning Teleoreactive Logic
  Programs by Observation, AAAI Fall Symposium FS05 –
  https://aaai.org/papers/0021-fs05-07-021-learning-teleoreactive-logic-programs-by-observation/
- Überblick: https://exa.ai/library/publication/34qxkfcww51
- Vorarbeit Problem-Solving: Choi & Langley (2005), ILP05 –
  http://www.isle.org/~langley/papers/icarus.trlp.ilp05.pdf
- HTN-Variante: Langley et al. (2006), ICML06 –
  http://www.isle.org/~langley/papers/icarus.lbo.icml06.pdf
- Dreistufige Variante: Ichise, Shapiro, Langley (flache Regeln → Hierarchie
  → Icarus) – http://www.isle.org/~dgs/papers/lhso.DS02.pdf

## Mechanismus (aus Paper abgeschrieben)

- Repräsentation: Concepts (Situationsklassen) + hierarchische Skills
  (per Goals indiziert, Subskills-Feld).
- Input: Goal + Anfangszustand + Expert-Sequenz primitiver Skills.
- State-Rekonstruktion aus Skill-Effekten; Rückwärts-Lernen mit
  Skill Chaining (Ziel im Effekt) vs. Concept Chaining (Subgoal-Zerlegung,
  rekursiv); irrelevante Schritte ignorieren; eine Klausel pro
  Erklärungsknoten (lokale Conditions).
- Domänen (zitiert): Blocks World, FreeCell, Tower of Hanoi, In-City-Driving.
- Architektur-Basis (im Paper genannt): Choi et al. (2004) hierarchische
  Skill-Repräsentation + Means-Ends-Problem-Solver (Newell et al. 1960);
  verwandte Formalismen: Nilsson (1994) Teleo-Reactive, Icarus (Shapiro 2001).

## Mapping auf Observe

| Observe | Beleg |
|---|---|
| Traces beobachten | Expert-Sequenz + State-Rekonstruktion |
| Hierarchie rekonstruieren | Concept/Skill Chaining, rekursiv |
| Keine Policy-Änderung | Paper trennt Lernen von Ausführung (Impasse-gesteuerter Solver separat) |

## Grenzen (aus Paper übernommen)

- Hintergrundwissen nötig (Concept-/Primitive-Definitionen, Effekte).
- Annahme: Goal wird erst im Final State wahr; Precondition erst im
  vorletzten State (sonst kein Lernbeleg – ehrlich dokumentiert).
- Frühe Ergebnisse in zwei Domänen („promising early results" – kein
  Allgemeingültigkeits-Claim).

## Quellen

- https://aaai.org/papers/0021-fs05-07-021-learning-teleoreactive-logic-programs-by-observation/
- https://exa.ai/library/publication/34qxkfcww51
- http://www.isle.org/~langley/papers/icarus.trlp.ilp05.pdf
- http://www.isle.org/~langley/papers/icarus.lbo.icml06.pdf
- http://www.isle.org/~dgs/papers/lhso.DS02.pdf
