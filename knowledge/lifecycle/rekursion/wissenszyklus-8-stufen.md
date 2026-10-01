# 8-Stufen-Zyklus – eingebettet in die Rekursion als Kommunikationsstruktur

> Lab-Prinzip: Projekt + Skills + Connectors + Knowledge. MD-first.
> Gesetz: `AGENTS.md` (Prinzipien 1–8). Eltern-Dok:
> `knowledge/lifecycle/rekursion/index.md`.
> Die Rekursion ist der Mechanismus, der die 8 Stufen miteinander
> kommunizieren lässt – durch rekursives Lesen, Modifizieren und
> Zurückschreiben desselben Zustands (Working Memory, Ontologie).
> Stufenfolge = Auftrag (gesetzte Ordnung); Einzelmechanismen = belegt
> (Quellen je Stufe, keine Erfindungen).

## Gesamtbild

```text
1 Erfahrung ─▶ 2 Wissen ─▶ 3 Gedächtnis ─▶ 4 Kognition ─▶ 5 Denken
  (schreibt M)   (liest M)    (schreibt O)    (liest O,       (schreibt
                                                   schreibt M)   Self-Feedback)
      │                                                        │
      ▼                                                        ▼
8 Wissen+ ◀── 7 Handeln ◀── 6 Nicht-Kognition ◀──────────────┘
(revidiertes Modell                       (schreibt M;
 nach M zurück →                             dämpft Handeln)
 neue Konstruktionen)

M = Working Memory, O = Ontologie (geteilte semantische Repräsentationen).
Kreise: Observe→Compare→Revise (Selbstbeobachtung);
Revise→Konstrukt→Akt (Kreis-Schluss).
```

## Die 8 Stufen (mit Lese-/Schreib-Semantik aus dem Auftrag)

### 1. Erfahrung (تجربة) — Rohdaten aus offiziellen Quellen sammeln → schreibt in Working Memory

- Phasen-Mapping: Observe (Traces/States festhalten) + Akt-Observation.
- Mechanismen: ReAct-Observation (extern einholen,
  https://arxiv.org/abs/2210.03629); LbO-State-Rekonstruktion
  (Salomaki et al. 2005,
  https://aaai.org/papers/0021-fs05-07-021-learning-teleoreactive-logic-programs-by-observation/).
- Connector: AgentO (OWL/RDF) – `connectors/agento-ariadne.md:7-11`,
   https://arxiv.org/abs/2007.09454; ARIADNE (3-Tier Memory) –
   `connectors/agento-ariadne.md:13-14`,
   https://arxiv.org/abs/2105.09864.
- Regel (Prinzip 1): aufnehmen ohne deuten – keine Wertung auf dieser Stufe.

### 2. Wissen (معرفة) — Rohdaten in `knowledge/` strukturieren → liest aus Working Memory

- Phasen-Mapping: Konstrukt (Schemata bauen: JISEM
  `<context,action,emotion>` + Valenz,
  https://jisem-journal.com/index.php/journal/article/view/12473;
  CCA-Hierarchie primitiv→komposit,
  https://researchr.org/publication/XueLM24-0).
- Output: strukturierte Docs unter `knowledge/` (diese Stufe erzeugt u. a.
  genau solche Files). Connector: HeLa-Mem (Hebbian Distillation) –
  `connectors/hela-semantic.md:7-9`,
  https://github.com/ReinerBRO/HeLa-Mem; AWS Semantic Layer
  (Neurosymbolisch) – `connectors/hela-semantic.md:27-33`,
  https://docs.aws.amazon.com/prescriptive-guidance/latest/semantic-layer-agentic-ai-ontology-reasoning-virtual-knowledge-graph/semantic-layer-agentic-ai-ontology-reasoning-virtual-knowledge-graph.html.

### 3. Gedächtnis (ذاكرة) — Wissen im Memory-Connector speichern → schreibt in Ontologie

- Phasen-Mapping: Konstrukt-Schreiben (`M(t) → M(t+1)`), CCA Episodic
  Memory (hierarchisch strukturierte enacted Interactions).
- Materialisierung: Runtime-Memory / `logic.py`-Analogon
  (`connectors/goedel-agent.md`,
  https://github.com/Arvid-pku/Godel_Agent); Reflexion-`mem` (Ω 1–3,
  https://arxiv.org/abs/2303.11366).
- Ontologie = geteilte Begriffe + Relationen; jede Ablage mit
  Provenienz-Link. Connector: Cognee (Graph+Vektor, dual) –
  `connectors/cognee-memory.md:7-9`,
  https://github.com/topoteretes/cognee; Zep/Graphiti (temporal KG) –
  `connectors/cognee-memory.md:12-13`,
  https://github.com/getzep/graphiti.

### 4. Kognition (إدراك) — verstehen, verknüpfen, Schlussfolgern → liest Ontologie, schreibt neue Verknüpfungen

- Phasen-Mapping: Observe-Erklärung (Skill vs. Concept Chaining, LbO) +
  ReAct-Thought (Pläne induzieren/nachführen).
- Mechanismen: CCA Behavior Selection (Propositionen aus Sequential System
  vs. Episodic Memory); hierarchische Skill-Rekonstruktion (LbO).
- Connector: Cognee (Graph+Vektor, dual) – `connectors/cognee-memory.md:7-9`,
  https://github.com/topoteretes/cognee; Affective Computing + Psycho-Linguistic –
  `connectors/affective-signals.md:1`.
- Output: neue Verknüpfungen (M) + historische Aufzeichnung.

### 5. Denken (فكر) — über das eigene Denken reflektieren (Metakognition) → schreibt Self-Feedback

- Phasen-Mapping: Revise-REFLECT.
- Mechanismus (belegt): Self-Reflection `(τ, r, mem) → sr` als semantischer
  Gradient in episodischem Memory (Reflexion, Shinn et al. 2023).
- Self-Feedback = rekursives Signal für den nächsten Durchlauf
  (mitgeführte `r` + Error-Traces, vgl. Gödel §4.2).
- Connector: MARS (Metacognitive Agent) – `connectors/mars-seaa.md:10-11`,
  https://github.com/Paparare/MARS; SEAA (HMM Trägheit) –
  `connectors/mars-seaa.md:28-36`, https://arxiv.org/abs/2609.17331.

### 6. Nicht-Kognition (لا-إدراك) — Emotionen, Triebe, unbewusste Vorgänge, Stress, Zeitdruck, implizite Bias → schreibt in Working Memory

- Eigene Stufe mit Schreibrecht (Auftrag); sie **dämpft** Handeln, steuert
  es nie allein.
- Belegt: Emotions-Modul + Valenz als intrinsisches Feedback (JISEM 2025);
  autotelische + interactionale Motivation/Proclivity (CCA 2024).
- **Nicht belegt:** Stress, Zeitdruck, implizite Bias, unbewusste Vorgänge
  werden NUR als protokollierte Kontextfaktoren (Einflussfaktoren-Log:
  was lag vor, was wurde vorsichtiger getan) behandelt – kein
  psychologisches Gesetz, keine Wirkungsbehauptung.
- Format: `[Einflussfaktor, Kontext, Auswirkung (Dämpfung), Beleg]` –
  ohne Beleg kein Eintrag.
- Connector: Psycho-Linguistische Frameworks + Affective Computing –
  `connectors/affective-signals.md:1`,
  https://jisem-journal.com/index.php/journal/article/view/12473.

### 7. Handeln (فعل) — Wissen anwenden → schreibt Aktion in Working Memory

- Phasen-Mapping: Akt (DEFINE→EXPERIMENT→OBSERVE→RELATE) + Konstrukt→Akt.
- Mechanismen: ReAct Thought/Action/Observation interleaved; Microsoft
  Testen→Validieren→Überwachen/Verfeinern
  (https://www.microsoft.com/de-de/microsoft-copilot/copilot-101/build-ai-agents).
- Regel (Stufen-Disziplin): kein Handeln ohne Beobachten (Stufe 1) und ohne
  Stufe 6 geprüft zu haben.
- Connector: HTAC (Hierarchical Task-Aware) – `connectors/htac-agentdice.md:6-9`,
  https://icml.cc/virtual/2026/poster/63033; Agent-Dice (Geometric Consensus) –
  `connectors/htac-agentdice.md:20-36`, https://github.com/Wuzheng02/Agent-Dice.

### 8. Wissen+ (معرفة+) — Wissensbasis erweitern → schreibt revidiertes Modell zurück → neue Konstruktionen (Kreis-Schluss)

- Phasen-Mapping: Revise (VALIDATE→REFLECT→PIVOT) + Compare-Delta
  (Pass@k vs. Pass^k, Gap = Mean@k − Pass^k,
  https://arxiv.org/abs/2609.08832) + `continue_improve`-Rekursion.
- Output: `(πₜ₊₁, Iₜ₊₁)` + `sr` + Diff nach `M` und
  `ergebnisse/rekursion/NNN-*.md`; Konstrukt übernimmt als Startmodell.
- Guardrails: Human-Gate (`approved`), Automatisches Gate (AGENTS.md: §9), externes Signal, Provenienz.
- Connector: HeLa-Mem (Hebbian Distillation) –
  `knowledge/lifecycle/wissen-plus.md:31-40`, https://github.com/ReinerBRO/HeLa-Mem;
  Bi-Temporal Modelle – `knowledge/lifecycle/wissen-plus.md:31-40`, https://github.com/getzep/graphiti;
  EvoPathBench (Benchmark) –
  `connectors/hela-evolution.md:41-45`, `knowledge/lifecycle/wissen-plus.md:42-59`, https://arxiv.org/abs/2609.24663.

## Stufen ↔ Phasen-Tabelle

| Stufe | Phase(n) | Liest | Schreibt |
|---|---|---|---|
| 1 Erfahrung | Observe, Akt-Obs | Quellen/Umgebung | Working Memory (Rohdaten) |
| 2 Wissen | Konstrukt | Working Memory | `knowledge/`-Struktur |
| 3 Gedächtnis | Konstrukt | Wissen | Ontologie + Memory-Connector |
| 4 Kognition | Observe, Akt-Relate | Ontologie | neue Verknüpfungen (M) |
| 5 Denken | Revise-Reflect | (τ, r, mem) | Self-Feedback (mem/M) |
| 6 Nicht-Kognition | **alle Phasen** (dämpft durch alle) | M + Kontext | Einflussfaktoren-Log (M) |
| 7 Handeln | Akt | M (Wissen+Modell) | Aktion + Traces (M) |
| 8 Wissen+ | **Compare, Revise** | M + Referenz | revidiertes Modell (M, knowledge/) |

**Zusätzlich:**
- **Stufe 1** löst `Observe` aus (phase 3.3) → dann `Akt-Obs` (phase 2.2) → schreibt Working Memory.
- **Stufe 2** → `Konstrukt` (phase 2.1).
- **Stufe 3** → `Konstrukt` (phase 2.1).
- **Stufe 4** → `Observe` (phase 2.3) → dann `Akt-Relate` (phase 2.2).
- **Stufe 5** → `Revise-Reflect` (phase 2.5).
- **Stufe 6** → greift auf **alle Phasen** (durch `Working Memory`) zu, unterdrückt aber `Handeln` (phase 2.2).
- **Stufe 7** → `Akt` (phase 2.2).
- **Stufe 8** → `Compare` (phase 2.4) + `Revise` (phase 2.5).

## Quellen

- Auftrag (Stufenfolge + arabische Termini + Prinzipien): Auftragstext,
  Gesetz in `AGENTS.md` (kein Paper-Claim).
- https://arxiv.org/abs/2210.03629 (ReAct)
- https://aaai.org/papers/0021-fs05-07-021-learning-teleoreactive-logic-programs-by-observation/ (LbO)
- https://jisem-journal.com/index.php/journal/article/view/12473 (Emotion/Valenz)
- https://researchr.org/publication/XueLM24-0 (CCA)
- https://arxiv.org/abs/2303.11366 (Reflexion)
- https://arxiv.org/abs/2609.08832 (Consistency Gap)
- https://github.com/Arvid-pku/Godel_Agent (Gödel-Mechanik)
- https://www.microsoft.com/de-de/microsoft-copilot/copilot-101/build-ai-agents (Handeln-Rahmen)
