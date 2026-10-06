---
name: act
process: pipeline.py
description: Wendet belegtes Wissen auf neue Aufgaben an (Stufe 7 Handeln) via Experten-Komposition, Konsens-Filterung und Logging nach Working Memory und knowledge/action/.
---

# Act-Skill — Handeln (Stufe 7)

> Lab-Prinzip: MD-first. Keine Erfindungen. `[Auftrag]` = aus dem Auftrag,
> `[Mapping/Auftrag]` = Auftrags-Übertragung belegter Mechanismen auf Handeln.

## Ablauf **[Auftrag]**

1. **Wissen + Ziel laden.**
   Belegtes Wissen und Ziel `g` + Task-Input laden. Ohne `g` kein Lauf.
2. **Passende Expertise komponieren.**
   `[Mapping/Auftrag]` nach HTAC: duale Aufgabenkapselung (Domain-/Task-Ebene),
   Experten on demand, adaptive Komposition historischen Wissens per Attention,
   Task-Adapter gegen Vergessen.
3. **Anwenden (Solver / Tool).**
   Nur belegtes Wissen anwenden; neue Aufgaben nur via Komposition
   belegter Experten.
4. **Widersprüchliche Updates filtern (Konsens-Prinzip).**
   `[Mapping/Auftrag]` nach Agent-Dice: Die Auftrags-Formulierung
   „filtert widersprüchliche Updates" ist ein Mapping auf
   Geometric-Consensus-Filtering (kein wörtliches Quellen-Zitat);
   Krümmungs-Gewichtung verstärkt geteilte Semantik.
5. **Aktion + Ergebnis loggen.**
   Aktion + Ergebnis in Working Memory schreiben (Signal für Wissen+).
6. **In `knowledge/action/` mit Quelle dokumentieren.**
   Anwendungs-Eintrag mit Beleg-Trace + Quellen-Link anlegen,
   siehe `knowledge/action/README.md`.

## Input / Output **[Auftrag]**

- Input: belegtes Wissen, Ziel `g` + Task-Input, Kompositions-Vorgabe.
- Output: Aktion + Ergebnis im Working Memory; Eintrag in `knowledge/action/`.

## Guardrails **[Auftrag]**

1. Kein Handeln ohne Stufen 1 und 6.
2. Keine unbelegten Anwendungen — ohne Beleg-Trace + Quellen-Link: `rejected`.
3. Widersprüchliche Updates filtern (Konsens-Prinzip).
4. Keine Format-/Schnittstellenänderung ohne Freigabe.
5. Kein `self_update` ohne `approved`.

## Quellen

Nur diese Quellen zulässig; keine Zahlen/Details erfinden:

- HTAC (ICML 2026 Poster): https://icml.cc/virtual/2026/poster/63033
- Agent-Dice Paper (ACL 2026 Findings): https://aclanthology.org/2026.findings-acl.908/
- Agent-Dice Code: https://github.com/Wuzheng02/Agent-Dice


## Prozesse (Aufrufe) [Auftrag]

Dieser Skill ruft folgende Prozesse in `data/memory/` auf (MCP-Interface nach Atomic: https://atomicapp.ai/guides/mcp-server/):

- `pipeline.py` — Kette (Stufe 7)
- **MCP-Tools:** `memory.write`

Quelle (Auftrag): `skills/README.md` (Skill→Prozess), `ergebnisse/mcp-memory.md` (Atomic).
