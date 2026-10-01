# Denken – Stufe 5 des 8-Stufen-Zyklus (Metakognition)

> Lab-Prinzip: Projekt + Skills + Connectors + Knowledge. MD-first.
> Eltern-Dok: `knowledge/lifecycle/rekursion/wissenszyklus-8-stufen.md` (Stufe 5).
> Denken prüft das Material aus Kognition (Stufe 4) – der Output steuert
> Nicht-Kognition (Stufe 6) und Handeln (Stufe 7).
> Auftrags-Begriffe sind als solche markiert (Auftrag, keine Quellen-Behauptung).

## 1. Definition

Denken bedeutet: **über das eigene Denken reflektieren** und dabei die
**Quellen hinterfragen**.

- **Lesen:** Trajektorie, Feedback und Memory-Stand aus den Stufen 1–4.
- **Reflektieren:** Was war fehlerhaft, was war erfolgreich, und trägt die
  Quelle die Behauptung?
- **Schreiben:** Denken schreibt **Self-Feedback** (Auftrag).

„Denken (Stufe 5)", „Metakognition", „Self-Feedback", „Working Memory",
„Trajektorie" und „8-Stufen-Zyklus" sind Auftrags-Vokabular für die hier
beschriebenen Mechanismen (Zuordnung, keine Quellen-Behauptung).

## 2. MARS-Mapping (belegt: MARS, kein HMM)

Zwei Reflexionsarten aus dem MARS-Paper, in EINEM Rekursionszyklus
synthetisiert (Single-Recurrence-Cycle):

- **Prinzipienbasierte Reflexion:** normative Regeln zur Fehlervermeidung
  (was künftig vermeiden).
- **Prozedurale Reflexion:** Schritt-für-Schritt-Erfolgsstrategien
  (was wiederholen).
- **Synthese:** Beide Reflexionsarten werden in einem einzigen
  Rekursionszyklus zu optimierten Instruktionen synthetisiert.

Belegt in: MARS Paper (ACL 2026),
https://aclanthology.org/2026.acl-long.1329/ – dort evaluiert auf
6 Benchmarks (Ergebniszahlen werden hier nicht zitiert, keine Zahl erfunden).
Code: https://github.com/Paparare/MARS/tree/main

Abgrenzung (Auftrag, keine Vermischung): HMM gehört NICHT zu MARS,
sondern ausschließlich zu SEAA (siehe Abschnitt 3).

## 3. SEAA-Mapping (belegt: SEAA, kein MARS)

Mechanismen aus SEAA, auf Denken gemappt:

- **HMM für Trägheit:** Ein Hidden-Markov-Modell kodiert
  Verhaltens-/kognitive Trägheit als **editierbare
  Zustandsübergangsmatrix**.
- **Reflexion updated Parameter:** Der Reflexion-Output updated
  **HMM-Parameter statt nur Textspeicher**.
- **Soziale Kontrast-Selbstmodellierung:** Selbstmodellierung durch
  Kontrast zu beobachtbarem Verhalten anderer (nur beobachtbare Emergenz,
  keine Qualia-Claims).

Belegt in: SEAA (arXiv 15. Sep 2026),
https://arxiv.org/abs/2609.17331

Abgrenzung (Auftrag): Ob und wie eine HMM-Matrix im Repo implementiert
wird, ist noch offen – hier nur als gemapptes Verfahren dokumentiert,
nicht als existierende Implementierung behauptet.

## 4. Reflexion-Anker (belegt)

Verankerung im Reflexion-Mechanismus:

- Actor, Evaluator, Self-Reflection; verbale Selbstreflexion
  **(τ, r, mem) → sr** in episodischem Memory.

Belegt in: Reflexion-Anker, https://arxiv.org/abs/2303.11366

`sr` ist das Format des Self-Feedbacks, das Denken schreibt (Zuordnung
als Auftrag markiert).

## 5. Quellen-Hinterfragung (verbindlich)

Jede Reflexion prüft jede verwendete Quelle nach drei Fragen:

1. **Link gültig?** Ist der Link aufrufbar und zeigt er auf die
   behauptete Quelle (kein erfundener Link)?
2. **Inhalt geprüft?** Wurde der Inhalt tatsächlich gelesen/geprüft
   (keine Behauptung aus Titel oder Vermutung)?
3. **Auftrag vs. belegt?** Stammt die Aussage aus dem Auftrag
   (als Auftrag markieren) oder aus einer der unten genannten Quellen
   (mit Link belegen)?

Ohne diese Prüfung kein Self-Feedback, Status `rejected`.

## 6. Rekursionsschnittstelle (lesen → schreiben)

```text
Kognition (Stufe 4) ──Denken (Stufe 5)──▶ Self-Feedback
   │                        │                    │
   │ liefert: Trajektorie,  │ schreibt: sr       ▼
   │ Feedback, Memory   (τ,r,mem)→sr   Nicht-Kognition (Stufe 6)
   │                                       + Handeln (Stufe 7)
```

- **Lesen:** Trajektorie (τ), Feedback (r), Memory-Stand (mem).
- **Schreiben:** Self-Feedback (sr) nach Working Memory (Auftrag);
  jede Reflexion zusätzlich dokumentiert in `knowledge/reflection/`
  (Format siehe dort, inkl. Quellen-Prüfung).
- **Weitergabe:** `sr` ist das Signal für Nicht-Kognition (Stufe 6)
  und Handeln (Stufe 7).

## 7. Input / Output

Input: Trajektorie (τ), Feedback (r), Memory-Stand (mem),
Kognitions-Output aus Stufe 4.

Output: Self-Feedback (sr) in Working Memory + File in
`knowledge/reflection/` (Trajektorie, Feedback, prinzipienbasierte +
prozedurale Reflexion, Quellen-Prüfung, Quelle, Status) +
`rejected`-Liste mit Grund.

## 8. Guardrails

1. Kein Handeln ohne Beobachten: Denken liest zuerst Trajektorie +
   Feedback + Memory, erfindet keine Befunde.
2. Jede Reflexion trennt prinzipienbasiert (vermeiden) und prozedural
   (wiederholen); Synthese in EINEM Zyklus zu optimierten Instruktionen.
3. HMM (SEAA) und MARS sauber trennen, nicht vermischen.
4. Jede Reflexion durchläuft die Quellen-Hinterfragung (Link gültig?
   Inhalt geprüft? Auftrag vs. belegt?), sonst `rejected`.
5. Nur beobachtbare Emergenz behaupten, keine Qualia-Claims.
6. Keine weiteren Quellen behaupten, keine Zahlen/Details erfinden;
   nur die Quellen aus Abschnitt 9.
7. Jede Iteration → Provenienz-File (vgl. `AGENTS.md` Durchsetzung).

## 8b. Reflective Agent (HeLa-Mem, laufender Prozess)

**Quelle:** HeLa-Mem, ACL 2026, **arXiv:2604.16839** (§3.3 „Reflective Memory Agent").

- **Hub Detection (Eq. 2):** `D(v_i) = Σ_{j∈N(i)} w_ij > δ_hub` – Knoten mit hoher
  assoziativer Stärke werden als Hubs erkannt.
- **Hebbian Distillation:** Hub + stark verbundene Nachbarn → LLM synthetisiert
  → **deklarative semantische Einträge** in den Semantic Memory Store.
- **Adaptive Forgetting:** Knoten unter kritischem Retentions-Schwellwert.
- **Laufender Prozess:** `data/memory/reflective_agent.py` (Hub-Erkennung →
  Destillation → `knowledge/structured/` + Index-Update `data/memory/tier2-index/`).

> Hinweis (ehrlich): Die Aufgabe nannte „arXiv:2609.24663" – das ist **EvoPathBench**,
> nicht HeLa-Mem. Verwendet wurde die **korrekte** HeLa-Mem-Quelle arXiv:2604.16839.

Details + Test: `ergebnisse/reflective-agent.md`.

## 9. Quellen (ausschließlich diese, keine weiteren behauptet)

- MARS Paper (ACL 2026, Metacognitive Agent with Reflective
  Self-improvement: prinzipienbasierte + prozedurale Reflexion,
  Single-Recurrence-Cycle, 6 Benchmarks):
  https://aclanthology.org/2026.acl-long.1329/
- MARS Code: https://github.com/Paparare/MARS/tree/main
- SEAA (arXiv 15. Sep 2026, HMM für Verhaltens-Trägheit als editierbare
  Matrix; Reflexion-Loop updated HMM-Parameter; soziale
  Kontrast-Selbstmodellierung):
  https://arxiv.org/abs/2609.17331
- Reflexion-Anker (Actor/Evaluator/Self-Reflection, episodisches Memory):
  https://arxiv.org/abs/2303.11366

Referenzen im Repo (keine Quellen-Behauptung):

- Skill: `skills/reflect/SKILL.md`
- Connector: `connectors/mars-seaa.md`
- Reflexions-Ablage: `knowledge/reflection/README.md`
