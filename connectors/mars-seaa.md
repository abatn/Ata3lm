# Connector: MARS + SEAA (Denken, Stufe 5)

> Lab-Prinzip, MD-first. Auftrag-Begriffe ohne Quelle werden als solche
> markiert, nicht als existierende Systeme behauptet.
> Ausschließlich die unten genannten Quellen; keine weiteren behauptet,
> keine Zahlen/Details erfunden.

## Identität (verifiziert)

- MARS Paper (ACL 2026, Metacognitive Agent with Reflective
  Self-improvement): https://aclanthology.org/2026.acl-long.1329/
- MARS Code: https://github.com/Paparare/MARS/tree/main
- SEAA (arXiv 15. Sep 2026): https://arxiv.org/abs/2609.17331
- Reflexion-Anker (Shinn et al. 2023):
  https://arxiv.org/abs/2303.11366

## Mechanismen (aus Quellen abgeschrieben)

### MARS (kein HMM)

- **Prinzipienbasierte Reflexion:** normative Regeln zur Fehlervermeidung.
- **Prozedurale Reflexion:** Schritt-für-Schritt-Erfolgsstrategien.
- **Single-Recurrence-Cycle:** Beide Reflexionsarten werden in EINEM
  Rekursionszyklus zu optimierten Instruktionen synthetisiert.
- **Evaluation:** 6 Benchmarks (Ergebniszahlen werden hier nicht zitiert,
  keine Zahl erfunden).

### SEAA (HMM gehört hierher, nicht zu MARS)

- **HMM für Verhaltens-Trägheit:** Hidden-Markov-Modell kodiert
  Verhaltens-/kognitive Trägheit als editierbare
  Zustandsübergangsmatrix.
- **Reflexion-Loop updated HMM-Parameter:** Der Output der Reflexion
  aktualisiert HMM-Parameter statt nur Textspeicher.
- **Soziale Kontrast-Selbstmodellierung:** Selbstmodellierung durch
  Kontrast zu beobachtbarem Verhalten anderer.

### Reflexion-Anker

- Actor, Evaluator, Self-Reflection; verbale Selbstreflexion
  (τ, r, mem) → sr in episodischem Memory.

## Mapping auf Denken (Auftrag, keine Quellen-Behauptung)

| Denken (Stufe 5) | Beleg |
|---|---|
| Prinzipienbasiert reflektieren (was vermeiden) | MARS Paper |
| Prozedural reflektieren (was wiederholen) | MARS Paper |
| Synthese in EINEM Zyklus zu optimierten Instruktionen | MARS Single-Recurrence-Cycle |
| Self-Feedback (sr) aus (τ, r, mem) schreiben | Reflexion-Anker |
| Reflexion als HMM-Parameter-Update denken | SEAA |
| `sr` als Signal für Nicht-Kognition und Handeln | Auftrag (Stufen-Zuordnung) |

„Denken (Stufe 5)", „Self-Feedback", „Working Memory",
„Nicht-Kognition", „Handeln" und „8-Stufen-Zyklus" sind Auftrags-Vokabular
(Mapping, keine Quellen-Behauptung).

## Grenzen

- MARS und SEAA sauber trennen: HMM gehört zu SEAA, nicht zu MARS –
  nicht vermischen.
- SEAA: nur beobachtbare Emergenz behaupten, keine Qualia-Claims.
- Reflexion braucht evaluierbares Feedback (Trajektorie + externes
  Signal); ohne Quellen-Prüfung (Link gültig? Inhalt geprüft? Auftrag
  vs. belegt?) kein Self-Feedback, Status `rejected`.
- Dieser Connector schreibt nichts selbst; Anwendung → Skill
  `skills/reflect/SKILL.md`, Ablage → `knowledge/reflection/`.

## Quellen (ausschließlich diese, keine weiteren behauptet)

- https://aclanthology.org/2026.acl-long.1329/
- https://github.com/Paparare/MARS/tree/main
- https://arxiv.org/abs/2609.17331
- https://arxiv.org/abs/2303.11366


## Prozess (Aufruf) [Auftrag]

Dieser Connector bedient: `bias_monitor.py` — Denken (HMM-Trägheit).

MCP-Interface / Ontologie-Validierung (SHACL, W3C): https://www.w3.org/TR/shacl/ · `ergebnisse/connector-prozess.md`.
