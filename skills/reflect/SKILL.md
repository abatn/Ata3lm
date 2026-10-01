---
name: reflect
description: Reflektiere über eine Agenten-Trajektorie (Metakognition, Stufe 5): prinzipienbasiert (Fehler vermeiden) + prozedural (Erfolg wiederholen) reflektieren, Quellen hinterfragen, Self-Feedback (sr) schreiben. Nutze diesen Skill, wenn Trajektorie + Feedback + Memory zu optimierten Instruktionen synthetisiert werden sollen – nach MARS, SEAA und Reflexion (Shinn et al. 2023).
---

# Skill: reflect

## Zweck

Der Agent reflektiert über sein eigenes Denken (Denken, Stufe 5 –
Auftrag) und schreibt Self-Feedback (sr) (Auftrag).

Quellen (MD-first, keine Erfindungen – ausschließlich diese):

- MARS Paper (ACL 2026): https://aclanthology.org/2026.acl-long.1329/
- MARS Code: https://github.com/Paparare/MARS/tree/main
- SEAA (arXiv 15. Sep 2026): https://arxiv.org/abs/2609.17331
- Reflexion-Anker: https://arxiv.org/abs/2303.11366

Details: `knowledge/lifecycle/denken.md`, `connectors/mars-seaa.md`.

## Wann anwenden

- Wenn Trajektorie (τ) + Feedback (r) + Memory (mem) vorliegen und ein
  Self-Feedback (sr) für Nicht-Kognition (Stufe 6) und Handeln (Stufe 7)
  erzeugt werden soll (Stufen-Zuordnung als Auftrag markiert).
- NICHT anwenden ohne Trajektorie/Feedback und ohne Quellen-Prüfung.

## Ablauf

1. **Trajektorie + Feedback + Memory laden**
   - `τ` (Ablauf: Aktionen, Beobachtungen), `r` (externes Feedback /
     Evaluator-Signal), `mem` (episodischer Memory-Stand) lesen,
     nichts ändern.
   - Quelle: Reflexion-Anker (τ, r, mem) → sr,
     https://arxiv.org/abs/2303.11366
2. **Prinzipienbasiert + prozedural reflektieren**
   - Prinzipienbasiert: normative Regeln zur Fehlervermeidung
     formulieren (was vermeiden).
   - Prozedural: Schritt-für-Schritt-Erfolgsstrategien formulieren
     (was wiederholen).
   - Beide in EINEM Rekursionszyklus zu optimierten Instruktionen
     synthetisieren (Single-Recurrence-Cycle).
   - Quelle: MARS Paper,
     https://aclanthology.org/2026.acl-long.1329/
3. **Quellen hinterfragen**
   - Jede verwendete Quelle prüfen: Link gültig? Inhalt geprüft?
     Auftrag vs. belegt?
   - Ohne bestandene Prüfung: Status `rejected`, kein Self-Feedback.
4. **Self-Feedback (sr) schreiben**
   - `sr` aus (τ, r, mem) erzeugen; Format: verbale Selbstreflexion in
     episodischem Memory (Reflexion-Anker).
   - SEAA-Anteil (sauber von MARS getrennt): Reflexion-Output als
     Update von HMM-Parametern denken (editierbare
     Zustandsübergangsmatrix für Verhaltens-/kognitive Trägheit),
     nicht nur als Textspeicher; soziale Kontrast-Selbstmodellierung
     nur als beobachtbare Emergenz, keine Qualia-Claims.
   - Quelle: SEAA, https://arxiv.org/abs/2609.17331
5. **In `knowledge/reflection/` mit Quelle dokumentieren**
   - File nach Konvention in `knowledge/reflection/README.md` anlegen:
     Trajektorie, Feedback, beide Reflexionsarten, Quellen-Prüfung,
     Quelle, Status.
   - `sr` nach Working Memory weiterreichen (Auftrag) als Signal für
     Nicht-Kognition und Handeln.

## Guardrails (verbindlich, vom Skill erzwungen)

1. Kein Self-Feedback ohne gelesene Trajektorie + Feedback + Memory.
2. Prinzipienbasiert (vermeiden) und prozedural (wiederholen) immer
   trennen; Synthese in EINEM Zyklus.
3. HMM (SEAA) und MARS sauber trennen, nicht vermischen.
4. Jede Reflexion durchläuft die Quellen-Hinterfragung (Link gültig?
   Inhalt geprüft? Auftrag vs. belegt?), sonst `rejected`.
5. Nur beobachtbare Emergenz behaupten, keine Qualia-Claims.
6. Keine weiteren Quellen behaupten, keine Zahlen/Details erfinden.
7. Jede Iteration → ein File in `knowledge/reflection/` mit Quelle.

## Input / Output

Input:

- Trajektorie (τ), Feedback (r), Memory-Stand (mem).

Output:

- Self-Feedback (sr) + File in `knowledge/reflection/`
  (Reflexions-Format, Quellen-Prüfung, Quelle, Status).

## Referenzen im Repo (keine Quellen-Behauptung)

- `knowledge/lifecycle/denken.md` (Stufe 5, Projekt-Doku)
- `connectors/mars-seaa.md` (Mechanismen, Mapping, Grenzen)
- `knowledge/reflection/README.md` (Reflexions-Format, Pflichtfelder)
