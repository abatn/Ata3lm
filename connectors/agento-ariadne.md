# Connector: AgentO + ARIADNE

> Lab-Prinzip MD-first. Legende: `[Auftrag]` = per Auftrag / AGENTS.md gesetzt,
> nicht quellenbelegt. `[Quelle]` = aus den unten genannten Quellen belegt.
> NUR die unter „Quellen" genannten Quellen werden zitiert.

## 1. Identität [Auftrag]

Dieser Connector verbindet Stufe 1 ERFAHRUNG mit zwei externen Vorgaben:

- AgentO als Vokabular-Quelle (wie werden Agents / Tasks / Workflows /
  Abhängigkeiten benannt).
- ARIADNE als Spezifikation für die Ablage-Funktion (Rohes unverändert
  festhalten, Tier 1).

Die Verbindung selbst (dass genau diese zwei Vorgaben für Stufe 1 gelten)
ist per Auftrag gesetzt (Status: [Auftrag]).

## 2. Mechanismus aus Quellen abgeschrieben [Quelle]

### AgentO [Quelle]

- OWL/RDF-Ontologie + Knowledge Graph für agentische Workflows.
- Standardisiertes Vokabular: Agents, Tasks, Workflows,
  Ressourcen-Abhängigkeiten.
- 66 Workflows aus 4 Frameworks per LLM-Verfahren.
- Use Cases: deklarative Rekonstruktion, Cross-Kontext-Reuse, Audit.

### ARIADNE [Quelle, als Spezifikation kennzeichnen]

ARIADNE wird hier als Spezifikation behandelt (Einordnung: [Auftrag]).

- Herkunft: DAEDALUS-Projekt, Univ. Oradea.
- 3-Tier:
  - Tier 1 Episodic = rohe Interaktionen (Conversations, Dokumente,
    API-Responses) mit Transaktionszeit-Immutabilität.
  - Tier 2 Semantic = Entities + Edge-Nodes mit bi-temporalen Feldern.
  - Tier 3 Community = Leiden-Cluster.

### Optional [Quelle]

- AriGraph / Ariadne IJCAI 2025: semantisches + episodisches Memory-Graph.

## 3. Mapping auf Erfahrung [Auftrag]

- AgentO → Benennung: Erfahrungs-Rohdaten werden mit dem AgentO-Vokabular
  etikettiert (Agents, Tasks, Workflows, Ressourcen-Abhängigkeiten).
- ARIADNE Tier 1 → Ablage: Erfahrungs-Rohdaten werden wie Tier-1-Episoden
  behandelt (roh, unverändert, mit Transaktionszeit-Immutabilität als
  Ablage-Prinzip).
- Tier 2 / Tier 3 werden in Stufe 1 nicht befüllt (Stufen-Disziplin).
- Output von Stufe 1 (Rohdaten + Provenienz) geht nach Working Memory als
  Signal für den nächsten Durchlauf.

Jeder Spiegelstrich in diesem Abschnitt ist [Auftrag], nicht Quellen-Aussage.

## 4. Grenzen aus Quellen übernommen [Auftrag + Quelle]

- Es wird nichts über AgentO hinaus behauptet: keine weiteren Frameworks,
  keine weiteren Zahlen, keine weiteren Use Cases als die oben genannten
  (Selbstbeschränkung: [Auftrag]; Stand: [Quelle]).
- Es wird nichts über ARIADNE hinaus behauptet: keine Implementierungs-,
  Performance- oder Reifegrad-Aussage; ARIADNE gilt hier nur als
  Spezifikation, nicht als belegte Implementierung (Status: [Auftrag]).
- Neue Schemata, Aktionen oder Interfaces nur mit Beleg-Trace + Quellen-Link
  + menschlicher Freigabe, sonst `rejected` (Status: [Auftrag]).
- Keine Deutung in Stufe 1; Bewertung ist Compare (Status: [Auftrag]).

## 5. Quellen

NUR diese Quellen (keine weiteren behauptet):

- AgentO:
  - http://eprints.cs.univie.ac.at/8749/
  - https://ucrisportal.univie.ac.at/en/publications/agento-an-ontology-for-modeling-agentic-ai-systems/
- ARIADNE (Spezifikation):
  - https://exa.ai/library/publication/khfxyt54hk1
- Optional:
  - https://www.ijcai.org/proceedings/2025/0002.pdf
