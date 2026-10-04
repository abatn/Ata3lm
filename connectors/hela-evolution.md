# Connector: HeLa-Evolution (HeLa-Mem)

> Lab-Prinzip MD-first: keine Erfindungen. Alles hier Behauptete stammt aus
> dem Auftrag oder aus den Quellen im Abschnitt `Quellen`. Sätze mit dem
> Zusatz `(Status: Auftrag)` sind gesetzte Betriebsregeln, keine
> Quellen-Claims.

## Identität

- Name: HeLa-Mem (Status: Auftrag: Connector-Name in diesem Projekt:
  `hela-evolution`).
- Paper: https://aclanthology.org/2026.acl-long.625/
- Code: https://github.com/ReinerBRO/HeLa-Mem

## Mechanismen (nur aus den Quellen abgeschrieben, ohne Zusatzdetails)

- Hebbian Distillation: Hubs zu stabilem semantischem Wissen verdichten.
- Reflective Agent.
- Adaptive Forgetting für Skalierbarkeit.
- Keine weiteren Mechanismus-Details, keine Zahlen und keine Abläufe werden
  hier behauptet.

## Mapping auf Wissen+ (Status: Auftrag)

- Hebbian Distillation ist die Referenz für Verdichtung zu stabilem Wissen.
- Adaptive Forgetting ist die Referenz für Skalierbarkeit.
- Beide Mechanismen werden in WISSEN+ nur mit Compare-Beleg + menschlicher
  Freigabe angewendet; keine automatische Umschreibung des Modells.
- Projekt-Ablage für Anwendungen dieses Connectors: `knowledge/expansion/`
  nach der Konvention in `knowledge/expansion/README.md`.
- Rekursionsschnittstelle: Das revidierte Modell geht nach Working Memory /
  Ontologie und ist Input neuer Konstruktionen.

## Grenzen (Status: Auftrag, mit Quellen-Schranke)

- Dieser Connector liefert nur die dokumentierten Mechanismus-Namen;
  jede Projekt-Anwendung braucht Beleg-Trace + Quellen-Link + menschliche
  Freigabe, sonst `rejected`.
- Kein Löschen von Wissen: Invalidierung statt Löschung (Bi-Temporal-Regel
  aus Graphiti, siehe `knowledge/lifecycle/wissen-plus.md`).
- EvoPathBench ist nur Evaluations-Benchmark (Generalisierung auf
  Ungesehenes, Retention nach unbezogenem Lernen, Regel-Adaption bei
  Gegen-Evidenz via Accumulation- / Interference- / Reversal-Streams),
  kein Revisions-Algorithmus; Befunde nur wie in
  `knowledge/lifecycle/wissen-plus.md` zitiert.

## Quellen

- https://aclanthology.org/2026.acl-long.625/
- https://github.com/ReinerBRO/HeLa-Mem
- https://github.com/getzep/graphiti
- https://arxiv.org/abs/2609.24663


## Prozess (Aufruf) [Auftrag]

Dieser Connector bedient: `reflective_agent.py` — Wissen+ (Evolution).

MCP-Interface / Ontologie-Validierung (SHACL, W3C): https://www.w3.org/TR/shacl/ · `ergebnisse/connector-prozess.md`.
