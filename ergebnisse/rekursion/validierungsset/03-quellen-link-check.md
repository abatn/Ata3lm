# Testfall 3: Quellen-Link-Check

## Aufgabe

Verifiziere, dass mindestens 80 % der Quellen-Links in AGENTS.md und wissenszyklus-8-stufen.md erreichbar sind (HTTP 200).

## Ground Truth

Links müssen HTTP-Status 200 zurückgeben. Nicht-erreichbare Links werden dokumentiert.

## Bewertungskriterium

Ausgabe >= 80 % der Links erreichbar → **`passed`**
