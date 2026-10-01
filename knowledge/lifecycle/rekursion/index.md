# Rekursion – Kommunikationsstruktur des Knowledge-Agenten

> Lab-Prinzip: Projekt + Skills + Connectors + Knowledge. MD-first.
> Die Rekursion ist kein Lifecycle-Schritt neben anderen, sondern der
> Mechanismus, der Konstrukt, Akt, Observe, Compare und Revise
> miteinander kommunizieren lässt – durch rekursives Lesen,
> Modifizieren und Zurückschreiben desselben Zustands.

## 1. Definition

Rekursion = geschlossener Wahrnehmungs-Handlungs-Lern-Loop über einen
geteilten Agenten-Zustand `S = (π, I, M)`:

- `π` – Policy / aktuelles Lösungsmodell (was der Agent tut, z. B. `solver`)
- `I` – Lern-/Entscheidungslogik (wie der Agent sich ändert, z. B. `SELF_IMPROVE` / `evolve`)
- `M` – Working Memory + Ontologie (gemeinsame semantische Repräsentation)

Jeder Durchlauf liest `S`, modifiziert `S`, schreibt `S` zurück.
Die nächste Rekursionstiefe arbeitet bereits mit der modifizierten Logik.

Dieses Muster ist direkt aus dem Gödel Agent übernommen:

- Paper: https://arxiv.org/abs/2410.04444
- ACL 2025 (Long Paper 1354): https://aclanthology.org/2025.acl-long.1354/
- PDF: https://aclanthology.org/2025.acl-long.1354.pdf
- Code: https://github.com/Arvid-pku/Godel_Agent

Dort: `SELF_IMPROVE` ruft sich per `continue_improve` rekursiv selbst auf;
`SELF_INSPECT` liest Runtime-Memory, `self_update` schreibt per Monkey
Patching zurück (vgl. Paper §4.1, README `src/agent_module.py`).

## 2. Die 5 Unterphasen

### 2.1 Konstrukt

Aufbau / Generierung eines Modells `π₀` aus Ziel `g` und Wissen.
Detail-Doku: `knowledge/lifecycle/rekursion/konstrukt.md`.

- Input: Ziel, Ontologie, Working Memory
- Output: initiales `π` (z. B. `solver`-Funktion in `agent_module.py`)
- Gödel-Mapping: Initial Policy + Goal Prompt (`goal_prompt.md`)
  – Quelle: https://github.com/Arvid-pku/Godel_Agent (Project Structure)
- Konstruktivismus-Mapping: behaviorale Schemata `<context,action,emotion>`
  + Valenz (JISEM 2025) und hierarchische Interaktions-Schemata
  primitiv → komposit (CCA) – Quellen siehe `konstrukt.md`.

### 2.2 Akt

Ausführung von `π` in einer Umgebung, inkl. Hilfsaktionen
(Python/Bash ausführen, LLM aufrufen).
Detail-Doku: `knowledge/lifecycle/rekursion/akt.md`.

- Input: `π`, Task-Input
- Output: Traces, Artefakte, ggf. Fehler
- Gödel-Mapping: `EXECUTE` / `execute_action` + `solver(agent_instance, task_input)`
  – Quelle: Paper Algorithmus 1 (`EXECUTE`), README Development Tips
- ReAct-Mapping: Thought→Action→Observation interleaved; Skill-Loop
  DEFINE→EXPERIMENT→OBSERVE→RELATE (Auftrags-Phasen, gemappt) –
  Quellen siehe `akt.md`.

### 2.3 Observe

Selbst- und Umweltbeobachtung. Zwei Kanäle:
Detail-Doku: `knowledge/lifecycle/rekursion/observe.md`.

1. **Self-Inspect:** Lesen des eigenen Codes aus Runtime-Memory
   (lokale/globale Variablen, Funktionen, Klassen).
2. **Interact:** Sammeln von Umwelt-Feedback via Utility-Funktion `U(E, π)`.

- Output: Zustand `s`, Feedback `r`
- Gödel-Mapping: `self_inspect` (`SELF_INSPECT()`), `interact` (`r ← U(E, π)`)
  – Quelle: https://arxiv.org/abs/2410.04444 (§4.1, Algorithmus 1)
- LbO-Mapping: Experten-Traces → hierarchische Skills (Skill vs. Concept
  Chaining, Salomaki et al. 2005) – Quellen siehe `observe.md`.

### 2.4 Compare

Vergleich von Beobachtung `r` gegen verifizierbare Referenz.
Detail-Doku: `knowledge/lifecycle/rekursion/compare.md`.

> Guardrail-relevant: Compare darf NICHT nur interne Repräsentationen
> vergleichen (sonst „konfidente Fehlanpassung"). Es muss auf externe,
> verifizierbare Signale zugreifen: Validierungsset, Tests, Ground Truth,
> `action_evaluate_on_task`.

- Input: `r`, Referenz (Validierungsset / Test / menschliches Urteil)
- Output: Delta-Bericht (besser / gleich / schlechter + Beleg)
- Gödel-Mapping: `action_evaluate_on_task` (nur nach erfolgreicher
  `solver`-Modifikation aufrufen) + Validierungsset als Feedback
  – Quelle: Paper §4.1 „Environmental Interaction", README Development Tips §2
- Konsistenz-Mapping: Pass@k vs. Pass^k, Consistency Gap = Mean@k − Pass^k
  (Duesterwald et al. 2026, ReAct auf AppWorld) – Quellen siehe `compare.md`.

### 2.5 Revise

Revision von `(π, I)` auf Basis des Compare-Berichts. Erzeugt
`(πₜ₊₁, Iₜ₊₁)` und schreibt sie in Runtime-Memory + Working Memory zurück.
Detail-Doku: `knowledge/lifecycle/rekursion/revise.md`.

- Input: Compare-Bericht, aktuelles `(π, I)`
- Output: neues `(π, I)`, Change-Log in `ergebnisse/rekursion/`
- Gödel-Mapping: `self_update` (`π, s ← a.code`), `action_adjust_logic`
  (Schnittstellen nicht ändern, Imports prüfen)
  – Quelle: Paper §4.1 „Self-Improvement via Dynamic Code Modification",
  Goal Prompt (Appendix A)
- Reflexions-Mapping: VALIDATE→REFLECT→PIVOT (Auftrags-Phasen; REFLECT =
  Reflexion `M_sr`, Closed-Loop Multi-Round via LoopRAG) – Quellen und
  TRACE-Abgrenzung siehe `revise.md`.

## 3. Kommunikationsstruktur (zwei geschlossene Kreise)

```text
KREIS A – rekursive Selbstbeobachtungsschleife:
  Observe → Compare → Revise → Observe …

KREIS B – schließt den Kreis zur Handlung:
  Revise → Konstrukt → Akt → Observe …

GESAMT:
  Konstrukt → Akt → Observe → Compare → Revise → (Konstrukt → Akt …)
                    ↑___________|  |
                    |  Self-Feedback als rekursives Signal
                    |  für den nächsten Durchlauf
                    └──────────────┘
```

- **Gemeinsame Sprache:** Ontologie + Working Memory (`M`) sind die
  geteilten semantischen Repräsentationen, die alle 5 Phasen lesen/schreiben.
  Im Gödel Agent entspricht das dem Runtime-Memory + `logic.py`
  (generierter Code) – Quelle: README Project Structure.
- **Rekursion statt Loop:** Die Hauptfunktion ist rekursiv implementiert
  (kein flacher Loop), damit bereits modifizierte Optimierungslogik in der
  nächsten Tiefe wirksam wird – Quelle: Paper §4 („we implement the main
  function as a recursive function").
- **Self-Feedback:** `r` + Error-Traces werden in den nächsten
  `SELF_IMPROVE`-Aufruf mitgeführt (Error Handling: Sequenz stoppen,
  Fehlerinfo mittragen) – Quelle: Paper §4.2.

## 4. Aktionen (kanonisch, aus Gödel Agent)

| Aktionsname | Phase | Funktion im Loop |
|---|---|---|
| `self_inspect` / `self_state` | Observe | `s ← SELF_INSPECT()` |
| `interact` | Observe | `r ← U(E, π)` |
| `action_evaluate_on_task` | Compare | Score auf Validierungsset / Task |
| `self_update` / `action_adjust_logic` | Revise | `(π, I)` neu schreiben |
| `continue_improve` | Revise → Konstrukt | `SELF_IMPROVE(E, π, s, r, g)` rekursiv |
| `action_run_code` / `action_call_json_format_llm` | Akt | Hilfsaktionen, Konvergenz beschleunigen |
| `thinking_before_acting` / `action_display_analysis` | alle | erst analysieren, dann handeln |

Quelle: Paper Algorithmus 1 + §4.2, Goal Prompt Appendix A,
Code: https://github.com/Arvid-pku/Godel_Agent (`src/agent_module.py`).

## 5. Guardrails (verbindlich)

1. **Menschliche Freigabe:** Kein `self_update` ohne explizites Human-Gate.
   Jede `Revise`-Änderung erzeugt einen Diff + Change-Log in
   `ergebnisse/rekursion/` und wartet auf Freigabe.
2. **Automatisches Gate (AGENTS.md: §9):** Score-basierte Entscheidung für Rekursion.
   - Score ≥ 95% + 8 Stufen "sicher" → automatisch erlaubt
   - Score 70–94% → Human-Gate erforderlich
   - Score < 70% → blockiert
   - Neue Quellen, Interface-Änderungen, self_update → immer Human-Gate
   Siehe `AGENTS.md` für vollständige Tabelle.
2. **Externe Verifikation:** `Compare` muss ein verifizierbares Signal
   nutzen (Validierungsset, Tests, Ground Truth). Rein internes
   Self-Scoring ist verboten (verhindert „konfidente Fehlanpassung").
3. **Schnittstellen-Stabilität:** Keine Interface-Änderungen ohne Freigabe
   (vgl. Goal Prompt: „do not change the interface of any function").
4. **Fehler-Rückfall:** Bei Fehlern Sequenz stoppen, Fehlerinfo mittragen,
   Originalzustand wiederherstellen können (vgl. Paper §4.2 Error Handling).
5. **Provenienz:** Jede Iteration in `ergebnisse/rekursion/NNN-*.md`
    mit Quelle (Paper-Link und/oder Code-Link). Keine Erfindungen (MD-first).
 6. **Fast Write Routing (§10):** Neue Erfahrungen durchlaufen zuerst den
    billigen Klassifikator (non-write / write-new / write-update).
    Operiert unterhalb des automatischen Gates (§9).
    Siehe `connectors/fast-write-routing.md` und `AGENTS.md §10`.

## 6. Quellen (keine Erfindungen)

- Yin et al. (2024, arXiv): Gödel Agent – https://arxiv.org/abs/2410.04444
- Yin et al. (2025, ACL Long 1354): https://aclanthology.org/2025.acl-long.1354/
- PDF: https://aclanthology.org/2025.acl-long.1354.pdf
- Code (Monkey Patching, `src/`-Struktur): https://github.com/Arvid-pku/Godel_Agent
- Monkey Patching (zitiert im Paper als Bimal 2012):
  https://web.archive.org/web/20120822051047/http://www.mindfiresolutions.com/Monkey-Patching-in-Python-1238.php
- ADAS (Basis der `task_*.py`-Evaluation, lt. README): https://github.com/ShengranHu/ADAS
- Gödel Machine (theoretischer Ursprung, vgl. Paper §1/§2, Schmidhuber 2003):
  nur via Paper referenziert, keine separate Behauptung hier.

## 7. Ablage (Lab-Prinzip)

- Gesetz: `AGENTS.md` (8 Prinzipien)
- Projekt (diese Datei): `knowledge/lifecycle/rekursion/index.md`
- Unterphasen: `konstrukt.md`, `akt.md`, `observe.md`, `compare.md`, `revise.md`
- Zyklus: `wissenszyklus-8-stufen.md` (8 Stufen, eingebettet in Rekursion)
- Skill: `skills/recursive-improve/SKILL.md`
- Sub-Skills: `konstrukt/`, `akt/`, `observe/`, `compare/`, `revise/` (je `SKILL.md`)
- Connectoren: `goedel-agent.md`, `cca-framework.md`, `react.md`,
    `observer-agent.md`, `consistency-gap.md`, `reflexion-trace.md`,
    `agento-ariadne.md`, `hela-semantic.md`, `hela-evolution.md`,
    `cognee-memory.md`, `cognee-validation.md`, `mars-seaa.md`,
    `htac-agentdice.md`, `affective-signals.md`,
    `fast-write-routing.md`

| Connector | Phase/Stufe | Connector-Datei | Kern-Referenz | Quellen-Link |
|---|---|---|---|---|
| AgentO (OWL/RDF) | Erfahrung (1) | `connectors/agento-ariadne.md:7-11` | AGENTS.md: — | https://arxiv.org/abs/2007.09454 |
| ARIADNE (3-Tier Memory) | Erfahrung (1) | `connectors/agento-ariadne.md:13-14` | AGENTS.md: — | https://arxiv.org/abs/2105.09864 |
| HeLa-Mem (Hebbian Distillation) | Wissen (2), Wissen+ (8) | `connectors/hela-semantic.md:7-9`, `connectors/hela-evolution.md:8-13` | AGENTS.md: — | https://github.com/ReinerBRO/HeLa-Mem, https://aclanthology.org/2026.acl-long.625/ |
| AWS Semantic Layer (Neurosymbolisch) | Wissen (2) | `connectors/hela-semantic.md:27-33`, `connectors/cognee-validation.md:11-14` | AGENTS.md: — | https://docs.aws.amazon.com/prescriptive-guidance/latest/semantic-layer-agentic-ai-ontology-reasoning-virtual-knowledge-graph/semantic-layer-agentic-ai-ontology-reasoning-virtual-knowledge-graph.html |
| Cognee (Graph+Vektor, dual) | Gedächtnis (3), Kognition (4) | `connectors/cognee-memory.md:7-9`, `connectors/cognee-validation.md:9-10` | AGENTS.md: — | https://github.com/topoteretes/cognee |
| Zep/Graphiti (temporal KG) | Gedächtnis (3) | `connectors/cognee-memory.md:12-13`, `connectors/hela-evolution.md:39-40` | AGENTS.md: — | https://github.com/getzep/graphiti |
| MARS (Metacognitive Agent) | Denken (5) | `connectors/mars-seaa.md:10-11` | AGENTS.md: — | https://github.com/Paparare/MARS |
| SEAA (HMM Trägheit) | Denken (5) | `connectors/mars-seaa.md:28-36` | AGENTS.md: — | https://arxiv.org/abs/2609.17331 |
| HTAC (Hierarchical Task-Aware) | Handeln (7) | `connectors/htac-agentdice.md:6-9` | AGENTS.md: — | https://icml.cc/virtual/2026/poster/63033 |
| Agent-Dice (Geometric Consensus) | Handeln (7) | `connectors/htac-agentdice.md:20-36` | AGENTS.md: — | https://github.com/Wuzheng02/Agent-Dice |
| EvoPathBench (Benchmark) | Wissen+ (8) | `connectors/hela-evolution.md:41-45`, `knowledge/lifecycle/wissen-plus.md:42-59` | AGENTS.md: — | https://arxiv.org/abs/2609.24663 |
| Bi-Temporal Modelle | Wissen+ (8) | `knowledge/lifecycle/wissen-plus.md:31-40` | AGENTS.md: — | https://github.com/getzep/graphiti |
| Affective Computing + Psycho-Linguistisch | Nicht-Kognition (6) | `connectors/affective-signals.md:1` | AGENTS.md: — | https://jisem-journal.com/index.php/journal/article/view/12473 |
| Fast Write Routing | Erfahrung (1) → Gedächtnis (3) | `connectors/fast-write-routing.md` | AGENTS.md: §10 | https://arxiv.org/abs/2608.22215 |

- Wissen: `ergebnisse/rekursion/` (jede Iteration ein File)
- Pläne: `ergebnisse/rekursion-plan.md`, `ergebnisse/knowledge-agent-plan.md`,
  `ergebnisse/lebenszyklus-8-phasen.md`
- Lifecycle-Phasen (8 Stufen, je Projekt-Dok + Skill + Connector + Knowledge):
  `knowledge/lifecycle/experience.md`, `wissen.md`, `gedaechtnis.md`,
  `kognition.md`, `nicht-kognition.md`, `denken.md`, `handeln.md`,
  `wissen-plus.md`
