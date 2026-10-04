# Connector: Reflexion + TRACE-Abgrenzung + Closed-Loop (Revise)

> Lab-Prinzip, MD-first. Auftrag-Begriffe ohne Quelle werden als solche
> markiert, nicht als existierende Systeme behauptet.

## Identität (verifiziert)

- Reflexion: Shinn et al. (2023), NeurIPS 2023 –
  https://arxiv.org/abs/2303.11366
- Code: https://github.com/noahshinn/reflexion
- LoopRAG (Closed-Loop Multi-Round, PDCA): MDPI Buildings 16(1):196 –
  https://www.mdpi.com/2075-5309/16/1/196
- TROVE (selektives Suffix-Editieren): https://arxiv.org/abs/2609.05019
- TRACE-Eval (als Eval-Quelle): https://arxiv.org/html/2602.21230
- TRACE-Repo (nur Abgrenzung): https://github.com/Kepler1908/TRACE

## Reflexion-Mechanismus (aus Paper abgeschrieben)

- Actor `M_a` (τ), Evaluator `M_e` (r: skalar/sprachlich, extern/intern),
  Self-Reflection `M_sr` (`sr` aus (τ, r, mem)); `sr` als semantischer
  Gradient in episodischem `mem` (Ω meist 1–3); Loop bis Evaluator ok.
- Gains (zitiert): AlfWorld +22 %, HotPotQA +20 %, HumanEval +11 %;
  HumanEval 91 % pass@1.

## Abgrenzungen (ehrlich)

- **TRACE-Eval** = Trajectory-Aware Comprehensive Evaluation (Hierarchical
  Trajectory Utility: Effizienz + Evidence-Grounding; Scaffolded Capability
  Assessment) – Evaluations-Framework für Deep Research Agents, kein
  Revisions-Algorithmus. Nutzung hier: Compare-nahe Trajektorien-Bewertung.
- **Kepler1908/TRACE** = Agentic-RAG-Retrieval-Pipeline (Planner + 3-Kanal-
  RRF + Agent-Loop + Re-Planning) – kein Curator-Agent.
- **„TRACE (Curator-Agent)"** aus dem Auftrag: ohne verifizierte Quelle –
  hier als **Rolle** definiert (`mem`-Kurator: Reflexionen versionieren,
  Belege sichern), NICHT als externes System behauptet.

## Closed-Loop Multi-Round (belegt: LoopRAG)

- 4 Agenten-Rollen IN einer Task-Instanz: Plan (parsen + Task-Graph + Prompt-
  Konfig inkl. MCPO-Stabilisierung) → Do (Retrieval + Generierung) →
  Check (Konsistenz/Evidenz-Audit) → Act (Policy-/Retrieval-Update,
  Feedback in Plan) – bounded „plan–execute–check–revise"-Runden bis
  semantische Konvergenz.
- Belegte Zahlen (zitiert, Smart-Building-QA): Context-Recall 90 %,
  Response-Relevanz 72 %, Antwort-Accuracy 88 % (HotpotQA/MultiHop-RAG/
  Inhouse – nur zitiert).
- PIVOT-Analogie: TROVE – Route als vorläufig, nur invalidiertes Suffix
  ersetzen (atomare/komposite Skills, Outcome-Transitionsgraph).

## Mapping auf Revise

| Revise | Beleg |
|---|---|
| VALIDATE | Reflexion-Evaluator + externes Signal |
| REFLECT | Self-Reflection `M_sr` → `sr` in `mem` |
| PIVOT | Actor-Neuplanung / TROVE-Suffix-Edit; LoopRAG-Check→Act |
| Kuratieren | `mem`-Rolle (Auftrag-Begriff, kein System-Zitat) |

## Grenzen

- Reflexion braucht evaluierbares Feedback (Evaluator-Qualität = Flaschenhals).
- LoopRAG-Fokus: Task-interne Optimierung, kein Langzeit-Online-Learning
  (Paper-Scope, ehrlich übernommen).
- Dieser Connector schreibt nichts selbst; Anwendung → `ergebnisse/rekursion/`.

## Quellen

- https://arxiv.org/abs/2303.11366
- https://github.com/noahshinn/reflexion
- https://www.mdpi.com/2075-5309/16/1/196
- https://arxiv.org/abs/2609.05019
- https://arxiv.org/html/2602.21230
- https://github.com/Kepler1908/TRACE


## Prozess (Aufruf) [Auftrag]

Dieser Connector bedient: `reflective_agent.py` — Revise (Reflexion).

MCP-Interface / Ontologie-Validierung (SHACL, W3C): https://www.w3.org/TR/shacl/ · `ergebnisse/connector-prozess.md`.
