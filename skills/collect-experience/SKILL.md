---
name: collect-experience
description: Sammelt Rohdaten aus offiziellen Quellen und legt sie unveraendert mit Quellen-Link in knowledge/raw/ ab (Stufe 1 ERFAHRUNG, ohne Deutung).
---

# Skill: collect-experience

> Stufe 1 ERFAHRUNG. Lab-Prinzip MD-first. Legende: `[Auftrag]` = per Auftrag /
> AGENTS.md gesetzt, nicht quellenbelegt. `[Quelle]` = aus den Quellen in
> `knowledge/lifecycle/experience.md` belegt. Keine weiteren Quellen behaupten.

## Ablauf [Auftrag]

1. **Quellen identifizieren [Auftrag]:**
   Nur offizielle, im Auftrag benannte Quellen verwenden.
   Jede Quelle mit vollständigem Link erfassen.

2. **Rohdaten einholen [Auftrag]:**
   Aufnehmen ohne zu deuten — keine Wertung, keine Zusammenfassung.
   Bewertung ist Compare und gehört nicht hierher.

3. **Unverändert + Quellen-Link in `knowledge/raw/` ablegen [Auftrag]:**
   - Datei unverändert speichern (kein Kürzen, kein Paraphrasieren).
   - Pflichtfelder je Einheit: Quelle (Link), Datum, Hash.
   - Dateiname und Felder folgen `knowledge/raw/README.md`.
   - Etikettierung nur mit AgentO-Vokabular
     (Agents, Tasks, Workflows, Ressourcen-Abhängigkeiten) [Quelle: Vokabular];
     die Ablage-Konvention selbst ist [Auftrag].
   - Ablage entspricht ARIADNE Tier 1 (rohe Interaktionen mit
     Transaktionszeit-Immutabilität) [Quelle];
     ARIADNE wird als Spezifikation behandelt (Einordnung: [Auftrag]).

4. **Working-Memory-Eintrag schreiben [Auftrag]:**
   Rohdaten + Provenienz nach Working Memory schreiben.
   Dieser Eintrag ist das Signal für den nächsten Durchlauf.
   Keine Deutung, keine Bewertung mitschreiben.

## Guardrails [Auftrag]

1. Unverändert speichern.
2. Jede Einheit mit Quellen-Link.
3. Keine Deutung (keine Wertung, keine Zusammenfassung).
4. Keine neuen Schemata / Aktionen / Interfaces ohne
   Beleg-Trace + Quellen-Link + menschliche Freigabe (sonst `rejected`).
5. Stufen-Disziplin: keine Stufe überspringen.

## Quellen

Keine eigenen Quellen in diesem Skill — es gelten ausschließlich die Quellen
aus `knowledge/lifecycle/experience.md`:

- AgentO: http://eprints.cs.univie.ac.at/8749/ und
  https://ucrisportal.univie.ac.at/en/publications/agento-an-ontology-for-modeling-agentic-ai-systems/
- ARIADNE: https://exa.ai/library/publication/khfxyt54hk1
- Optional: https://www.ijcai.org/proceedings/2025/0002.pdf
