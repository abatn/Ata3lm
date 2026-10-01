# Revise – Unterphase der Rekursions-Kommunikation

> Lab-Prinzip: Projekt + Skills + Connectors + Knowledge. MD-first.
> Eltern-Dok: `knowledge/lifecycle/rekursion/index.md` (§2.5).
> Revise schreibt das revidierte Modell zurück in den Zustand – es fließt
> in neue Konstruktionen (schließt den Kreis: Revise → Konstrukt → Akt).

## 1. Mechanismus: Reflexion (aus Quelle, kein Eigenbau)

Reflexion = verbale Verstärkung statt Gewichts-Update: „Reflexion agents
verbally reflect on task feedback signals, then maintain their own
reflective text in an episodic memory buffer to induce better
decision-making in subsequent trials."

Drei Module (aus Paper abgeschrieben):

- **Actor `M_a`:** generiert Text + Aktionen (Trajektorie `τ_t`).
- **Evaluator `M_e`:** bewertet `τ_t` → Score `r_t` (skalar oder Sprache,
  extern oder intern simuliert).
- **Self-Reflection `M_sr`:** erzeugt verbale Selbstreflexion `sr_t` aus
  `(τ_t, r_t, mem)` – semantischer Gradient (konkrete Richtung statt Zahl).

Loop: `τ_0` → `r_0` → `sr_0` in `mem` → Actor mit `mem`-Kontext erneut,
bis Evaluator `τ_t` für korrekt befindet. Memory-Schranke `Ω` (meist 1–3).

Belegte Gains (nur zitiert): AlfWorld +22 %, HotPotQA +20 %, HumanEval
+11 % vs. starke Baselines; HumanEval 91 % pass@1.

- Quelle Paper: Shinn et al. (2023), NeurIPS 2023 –
  https://arxiv.org/abs/2303.11366
- Code: https://github.com/noahshinn/reflexion

## 2. Skill-Loop VALIDATE → REFLECT → PIVOT (Auftrag-Phasen)

Phasen-Namen aus dem Auftrag (keine Paper-Behauptung); REFLECT ist auf
Reflexion gemappt, Rest auf belegte Nachbar-Mechanismen:

| Auftrags-Schritt | Belegter Mechanismus |
|---|---|
| VALIDATE | Evaluator `M_e` + externes Signal (Grader/Test – vgl. Compare-Dok); erst bei bestandenem Check weiter |
| REFLECT | Self-Reflection `M_sr`: `(τ, r, mem) → sr` (verbaler Erfahrungstext in `mem`) |
| PIVOT | Actor mit `sr`-Kontext neu planen ODER Route gezielt editieren (nur invalidiertes Suffix ersetzen – vgl. TROVE-Prinzip, unten); Interface-Änderungen nur mit Freigabe |

## 3. Connectoren (ehrlich getrennt belegt)

- **Reflexion** (Revision per Sprache): siehe §1.
- **TRACE (as found):** Trajectory-Aware Comprehensive Evaluation –
  evaluiert die GESAMTE Trajektorie (Hierarchical Trajectory Utility:
  Prozess-Effizienz + kognitive Qualität/Evidence-Grounding statt nur
  Final-Accuracy; Scaffolded Capability Assessment für latente Fähigkeit).
  Das ist ein Evaluations-Framework, kein Revisions-Algorithmus –
  hier als Compare-nahe Bewertungsquelle genutzt, nicht als Rewrite-Regel.
  Quelle: https://arxiv.org/html/2602.21230 (Paper-Stand: Deep Research Agents).
- **TRACE (Repo, abweichend):** `Kepler1908/TRACE` ist eine Agentic-RAG-
  Retrieval-Pipeline (Planner + Multi-Tool-Search + Re-Planning) –
  https://github.com/Kepler1908/TRACE. Ebenfalls kein Curator-Agent;
  hier NICHT als Beleg für „Curator" verwendet.
- **„Curator-Agent":** Auftrag-Begriff ohne verifizierte Quelle – wird hier
  NICHT als existierendes System behauptet. Falls gemeint: kuratierende
  Rolle = `mem`-Pflege (Reflexionen versionieren, Beleg sichern) – als
  Rolle im Skill definiert, nicht als externes System zitiert.
- **Closed-Loop Multi-Round Planning (belegt):** LoopRAG – PDCA-Closed-Loop
  (Plan → Do → Check → Act) als Multi-Agenten-Rollen IN EINER Task-Instanz:
  „plan–execute–check–revise"-Iterationen bis semantische Konvergenz
  (bounded Runden). Quelle: LoopRAG, MDPI Buildings 16(1):196 –
  https://www.mdpi.com/2075-5309/16/1/196
- **Selektives Editieren (belegt, passend zu PIVOT):** TROVE – Route als
  vorläufig behandeln, nur das durch Runtime-Evidenz invalidierte Suffix
  ersetzen. Quelle: https://arxiv.org/abs/2609.05019

Details: `connectors/reflexion-trace.md`.

## 4. Rekursionsschnittstelle (zurückschreiben → neue Konstruktionen)

```text
Compare-Bericht + (τ, r, mem) ──Revise──▶ (πₜ₊₁, Iₜ₊₁) nach M ──▶ Konstrukt
   (freigegeben)                    │                    liest M(t+1),
                              self_update              baut neue Schemata
                           (nur mit Freigabe)
```

- **Schreiben:** `(π, I)`-Revision + `sr`-Text in `mem`/`M` zurück
  (Gödel: `self_update`, `action_adjust_logic`; materialisiert wie in
  `connectors/goedel-agent.md`).
- **Kreis-Schluss:** `continue_improve` ruft `SELF_IMPROVE` rekursiv –
  nächste Tiefe läuft mit neuer Logik; Konstrukt übernimmt `(πₜ₊₁, Iₜ₊₁)`
  als Startmodell.
- **Regeln (belegt, Goal Prompt):** Imports prüfen, Interfaces nicht ändern,
  unnötige Änderungen vermeiden.

## 5. Input / Output

Input: Compare-Bericht (belegt), `(τ, r, mem)`, aktuelles `(π, I)`.

Output: `(πₜ₊₁, Iₜ₊₁)` + `sr` + Diff + File in `ergebnisse/rekursion/NNN-*.md`
(Freigabe-Status Pflicht).

## 6. Guardrails

1. Kein `self_update` ohne `approved` (Human-Gate).
2. Kein Revise ohne belegten Compare-Bericht.
3. Keine Interface-Änderungen ohne Freigabe.
4. `mem`-Schranke einhalten (Kontext-Budget dokumentieren).
5. Provenienz: jede Revision mit Quelle (Link) + Diff.

## 7. Quellen (keine Erfindungen)

- https://arxiv.org/abs/2303.11366
- https://github.com/noahshinn/reflexion
- https://arxiv.org/html/2602.21230 (TRACE-Eval, als Eval-Quelle)
- https://github.com/Kepler1908/TRACE (Repo, nur zur Abgrenzung)
- https://www.mdpi.com/2075-5309/16/1/196 (LoopRAG Closed-Loop)
- https://arxiv.org/abs/2609.05019 (TROVE selektives Editieren)
- Skill: `skills/recursive-improve/revise/SKILL.md`
- Connector: `connectors/reflexion-trace.md`
