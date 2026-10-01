# Akt – Unterphase der Rekursions-Kommunikation

> Lab-Prinzip: Projekt + Skills + Connectors + Knowledge. MD-first.
> Eltern-Dok: `knowledge/lifecycle/rekursion/index.md` (§2.2).
> Akt führt aus: Es schreibt Traces und Artefakte in den Zustand
> (Working Memory) – das ist das Signal für Observe/Compare im nächsten
> Durchlauf.

## 1. Definition

Akt = Ausführung von Policy `π` (`solver`) in einer Umgebung, wobei
Reasoning-Spuren und Aktionen interleaved erzeugt werden und jede Aktion
externe Information (Wissensbasis, Umgebung) zurückholen kann.

Mechanismus (aus Quelle, kein Eigenbau):

„ReAct prompts LLMs to generate both verbal reasoning traces and actions
pertaining to a task in an interleaved manner … to perform dynamic reasoning
to create, maintain, and adjust high-level plans for acting (reason to act),
while also interact with the external environments … to incorporate
additional information into reasoning (act to reason)."

- Quelle: Yao et al. (2023), ReAct, ICLR 2023 –
  https://arxiv.org/abs/2210.03629

Trainingsrahmen (Microsoft, aus Quelle abgeschrieben – getestet, validiert,
überwacht und verfeinert statt nur einmal ausgeführt):

- „Den Agent testen … Leistung in verschiedenen Szenarien bewerten
  (Unit-Tests, Benutzertests, A/B-Tests) … Den Agent validieren …
  Ausgaben mit erwarteten Ergebnissen oder Benchmarks vergleichen …
  Überwachen und verfeinern … Feedback sammeln … schrittweise
  Verbesserungen" –
  https://www.microsoft.com/de-de/microsoft-copilot/copilot-101/build-ai-agents
- „planen, handeln und verbessern" (KI-Codierungs-Agents in Workflows) –
  https://learn.microsoft.com/de-de/training/paths/gh-developing-agentic-systems-1

Mapping-Label „Handeln → Reflektieren → Verfeinern" (Auftrag) entspricht
diesen belegten Schritten: Handeln = ausführen, Reflektieren = testen/
validieren gegen Benchmarks, Verfeinern = überwachen + schrittweise
verbessern. Das Label selbst ist Auftrags-Vokabular, kein wörtliches
Microsoft-Zitat.

## 2. Skill-Loop DEFINE → EXPERIMENT → OBSERVE → RELATE (Auftrag-Phasen)

Die vier Loop-Schritte sind aus dem Auftrag übernommen (keine
Paper-Behauptung). Mapping auf belegte Mechanismen:

| Auftrags-Schritt | Belegter Mechanismus |
|---|---|
| DEFINE | Task-Definition + Grenzen + Tool-Zugriff festlegen (vgl. Microsoft: „festlegen, was der Agent tun soll … klare Grenzen … Zugriff auf die richtigen Informationen"); Initial Policy + Goal Prompt (Gödel) |
| EXPERIMENT | Action ausführen: `execute_action`, `action_run_code` (Python/Bash), Tool-/API-Aufrufe (ReAct: Action; Gödel §4.2 Additional Tools) |
| OBSERVE | Observation einsammeln: Tool-Outputs, Traces, Fehler (ReAct: Observation; Gödel: `interact`, `r ← U(E, π)`) |
| RELATE | Reasoning-Trace fortschreiben: Pläne induzieren/nachführen, Exceptions handhaben (ReAct: „reasoning traces help the model induce, track, and update action plans … handle exceptions") |

Belegte Aktions-Typen (ReAct + Gödel, keine Erfindung):

- `Thought` (Reasoning-Trace), `Action` (z. B. Wikipedia-API, Code-Run),
  `Observation` (externe Rückmeldung) – Quelle: ReAct Paper.
- `solver(agent_instance, task_input)`, `execute_action`,
  `action_run_code`, `action_call_json_format_llm` –
  Quelle: https://github.com/Arvid-pku/Godel_Agent.

Belegte Evaluations-Domänen (nur zitiert, nicht selbst gemessen):
HotpotQA, Fever, ALFWorld, WebShop – Quelle: ReAct Paper
(ALFWorld +34 %, WebShop +10 % absolut vs. Imitation/RL – Zahlen nur
zitiert).

## 3. Rekursionsschnittstelle (schreiben → Signal für Observe/Compare)

```text
M(t) + π ──Akt──▶ M(t+1) = M(t) + {Traces, Artefakte, Observations, Fehler}
                        │
                        ▼
              Observe liest M(t+1) ──▶ Compare verifiziert extern
```

- **Schreiben:** Jede Ausführung hängt an `M` an: Reasoning-Traces,
  Aktionen, Observations, Fehler-Traces. Materialisiert wie in
  `connectors/goedel-agent.md` (Runtime-Memory / `logic.py`-Analogon).
- **Signal:** Dieses angehängte Material ist der Input für Observe
  (`self_inspect` + `interact`) und das zu prüfende Objekt für Compare
  (`action_evaluate_on_task`).
- **Fehler-Regel (belegt, Gödel §4.2):** Sequenz stoppen, Fehlerinfo in
  nächste Rekursion mittragen, auf Original zurückfallen können.

## 4. Input / Output

Input: `M(t)`, `π` (Schemata aus Konstrukt), Task-Input, Tool-Zugriff.

Output: `M(t+1)` (Traces + Artefakte + Observations) + File in
`ergebnisse/rekursion/NNN-*.md` (Beleg: welche Aktion, welches Ergebnis).

## 5. Guardrails

1. Keine Aktion ohne definierte Grenzen/Tools (DEFINE zuerst).
2. Jede Aktion wird geloggt (sonst kein Observe/Compare möglich).
3. Externe Verifikation bleibt Pflicht – Akt-Erfolg ist kein Compare-Ersatz.
4. Menschliche Freigabe für neue Tools/Aktionen
   (vgl. Gödel Development Tips: `action_functions`-Eintrag + Implementierung).

## 6. Quellen (keine Erfindungen)

- Yao et al. (2023): ReAct, ICLR 2023 – https://arxiv.org/abs/2210.03629
- Projektseite: https://react-lm.github.io/
- Microsoft: KI-Agents erstellen/trainieren –
  https://www.microsoft.com/de-de/microsoft-copilot/copilot-101/build-ai-agents
- Microsoft Learn: agentische KI-Systeme –
  https://learn.microsoft.com/de-de/training/paths/gh-developing-agentic-systems-1
- Gödel-Code: https://github.com/Arvid-pku/Godel_Agent
- Skill: `skills/recursive-improve/akt/SKILL.md`
- Connector: `connectors/react.md`
