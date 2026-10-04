# Connector: ReAct (Reasoning + Acting) + Microsoft-Trainingsrahmen

> Lab-Prinzip, MD-first. Behauptungen nur aus den verlinkten Quellen.
> „Handeln → Reflektieren → Verfeinern" ist Auftrags-Mapping auf die
> belegten Microsoft-Schritte (Testen/Validieren/Überwachen+Verfeinern),
> kein wörtliches Zitat.

## Identität

- ReAct: Yao et al. (2023), ICLR 2023 –
  https://arxiv.org/abs/2210.03629
- Projektseite: https://react-lm.github.io/
- Microsoft-Training: KI-Agents erstellen und trainieren –
  https://www.microsoft.com/de-de/microsoft-copilot/copilot-101/build-ai-agents
- Microsoft Learn: agentische KI-Systeme (planen, handeln, verbessern) –
  https://learn.microsoft.com/de-de/training/paths/gh-developing-agentic-systems-1

## Mechanismus ReAct (aus Paper abgeschrieben)

- Interleaved `Thought → Action → Observation`: Reasoning-Traces zum
  Induzieren/Nachführen von Aktionsplänen + Exception-Handling
  (reason to act); Aktionen holen externe Information ein (act to reason).
- Domänen (zitiert): HotpotQA + Wikipedia-API (Halluzinations-/Fehler-
  propagations-Reduktion vs. CoT), Fever, ALFWorld, WebShop.
- Best-Overall laut Paper: ReAct+CoT-Kombination (internes + externes Wissen).
- Nebeneffekt (belegt): Interpretierbarkeit/Diagnostizierbarkeit –
  interne vs. externe Information im Trace unterscheidbar.

## Microsoft-Schritte (aus Quelle abgeschrieben)

1. Aufgabe definieren, Framework wählen, Informationszugriff geben,
   Richtlinien setzen.
2. Trainingsdaten sammeln/bereinigen/kennzeichnen.
3. Testen (Unit-/Benutzer-/A/B-Tests) → Validieren (gegen erwartete
   Ergebnisse/Benchmarks) → Überwachen + schrittweise verfeinern.
4. Menschliche Beteiligung: Team schulen, Ausgaben prüfen/anpassen,
   verantwortungsvolle KI-Prinzipien einhalten.

## Mapping auf Akt-Phasen

| Akt | Beleg |
|---|---|
| DEFINE | Microsoft Schritt 1 + Learn „planen" |
| EXPERIMENT | ReAct Action; Gödel `execute_action`/`action_run_code` |
| OBSERVE | ReAct Observation; Gödel `interact` |
| RELATE | ReAct Thought (reason to act); Microsoft „verfeinern" |

## Grenzen

- ReAct-Prompting: komplexe Tasks mit großen Aktionsräumen brauchen mehr
  Demos (Kontextlimit); Fine-Tuning als Ausweg nur initial erprobt (Paper).
- Dieser Connector führt nichts aus; Anwendung → `ergebnisse/rekursion/`.

## Quellen

- https://arxiv.org/abs/2210.03629
- https://react-lm.github.io/
- https://www.microsoft.com/de-de/microsoft-copilot/copilot-101/build-ai-agents
- https://learn.microsoft.com/de-de/training/paths/gh-developing-agentic-systems-1


## Prozess (Aufruf) [Auftrag]

Dieser Connector bedient: `pipeline.py` — Akt (Ausführen).

MCP-Interface / Ontologie-Validierung (SHACL, W3C): https://www.w3.org/TR/shacl/ · `ergebnisse/connector-prozess.md`.
