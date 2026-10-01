# knowledge/action — Anwendungen (Stufe 7 Handeln)

> Lab-Prinzip: MD-first. Jede Anwendung braucht Beleg-Trace + Quellen-Link.
> Auftrag-Begriffe mit `[Auftrag]` markiert.

## Status **[Auftrag]**

- Verzeichnis angelegt.
- Wartet auf `t=1` (noch keine Anwendung dokumentiert).

## Konvention: Anwendungs-Format **[Auftrag]**

Eine Datei pro Anwendung: `YYYY-MM-DD-<kurztitel>.md`.

Pflichtfelder:

1. `Ziel (g)`: Ziel + Task-Input.
2. `Wissen`: Verweis auf belegtes Wissen (mit Quelle).
3. `Komposition`: welche Expertise wie komponiert wurde
   (Domain-/Task-Ebene, Experten, Adapter — soweit aus Auftrag/Quellen ableitbar).
4. `Aktion`: was mit welchem Solver/Tool angewendet wurde.
5. `Ergebnis`: Beobachtung des Ausgangs (keine Deutung).
6. `Konsens-Filter`: welche widersprüchlichen Updates gefiltert wurden
   (`[Mapping/Auftrag]` auf Geometric-Consensus-Filtering).
7. `Quelle`: Beleg-Trace + mindestens einer der zulässigen Quellen-Links.
8. `Status`: `angelegt` / `belegt` / `rejected`.

Regeln **[Auftrag]**:

- Nur belegtes Wissen anwenden.
- Neue Aufgaben nur via Komposition belegter Experten.
- Ohne Beleg-Trace + Quellen-Link: `rejected`.
- Aktion + Ergebnis zusätzlich nach Working Memory (Signal für Wissen+).

## Zulässige Quellen (keine weiteren behaupten)

- HTAC (ICML 2026 Poster): https://icml.cc/virtual/2026/poster/63033
- Agent-Dice Paper (ACL 2026 Findings): https://aclanthology.org/2026.findings-acl.908/
- Agent-Dice Code: https://github.com/Wuzheng02/Agent-Dice
