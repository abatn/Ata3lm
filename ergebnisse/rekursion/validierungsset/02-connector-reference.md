# Testfall 2: Connector-Referenz-Check

## Aufgabe

Verifiziere, dass alle 9 Connector-Namen in den 3 Kern-Dateien referenziert sind:

1. `AGENTS.md`
2. `knowledge/lifecycle/rekursion/index.md`
3. `knowledge/lifecycle/rekursion/wissenszyklus-8-stufen.md`

## Ground Truth

Folgende 9 Connector-Gruppen müssen in JEDEM der 3 Dateien mindestens einmal erwähnt sein:
AgentO, ARIADNE, HeLa-Mem, AWS Semantic Layer, Cognee, Zep/Graphiti, MARS/SEAA, HTAC/Agent-Dice, EvoPathBench, Bi-Temporale Modelle, Affective Computing.

## Bewertungskriterium

Ausgabe == 3/3 Dateien mit allen Connector-Namen vorhanden → **`passed`**
