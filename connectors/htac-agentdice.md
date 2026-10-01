# Connector: HTAC + Agent-Dice

> Lab-Prinzip: MD-first. Mechanismen sind aus den Quellen abgeschrieben,
> Übertragungen als `[Mapping/Auftrag]` markiert. Keine weiteren Quellen behauptet.

## 1. Identität **[Auftrag]**

Dieser Connector bindet zwei externe Mechanismus-Quellen an die
Lifecycle-Phase HANDELN (Stufe 7):

- HTAC für Experten-Komposition.
- Agent-Dice für konsensbasierte Fusion.

Er erfindet keine eigenen Mechanismen; er mappt nur.

## 2. Mechanismen aus den Quellen

### 2.1 HTAC

Quelle: HTAC (ICML 2026 Poster).

- Hierarchical Task-Aware Composition.
- Duale Task-Kodierung: Domain-Ebene und Task-Ebene.
- Dual-Level-Experten, bereitgestellt on demand.
- Adaptive Knowledge Composition per Attention.
- Task-Adapter.
- Benchmark-Kontext: Offline Continual World (Ergebnisse hier nicht behauptet).

### 2.2 Agent-Dice

Quellen: Agent-Dice Paper (ACL 2026 Findings), Agent-Dice Code.

- Parameter-Fusion via Directional Consensus.
- Stufe 1: Geometric-Consensus-Filtering.
- Stufe 2: Curvature-based Importance Weighting.
- Domänen laut Paper: Tool-Use- und GUI-Agenten (keine Zahlen/Details hier behauptet).

## 3. Mapping auf Handeln **[Mapping/Auftrag]**

- Duale Aufgabenkapselung (Domain/Task) strukturiert die Anwendung.
- Expertise wird on demand komponiert.
- Historisches Wissen wird adaptiv per Attention komponiert.
- Task-Adapter stützen Transfer ohne Vergessen.
- Geometric-Consensus-Filtering beschneidet widersprüchliche Updates.
- Krümmungs-Gewichtung verstärkt geteilte Semantik.
- Zusammen adressieren sie das Stabilitäts-Plastizitäts-Dilemma
  für Transfer ohne katastrophales Vergessen.

Hinweis: Die Auftrags-Formulierung „filtert widersprüchliche Updates"
ist ein Mapping auf Geometric-Consensus-Filtering, kein wörtliches
Quellen-Zitat.

## 4. Grenzen **[Auftrag]**

- Nur belegtes Wissen anwenden; keine unbelegten Anwendungen.
- Keine Benchmark-Zahlen, keine Implementierungsdetails und keine
  Wirkungsbehauptungen über die obigen Mechanismus-Namen hinaus.
- Neue Aktionen/Schemata/Interfaces nur mit Beleg-Trace + Quellen-Link
  + menschlicher Freigabe; sonst `rejected`.
- Kein Handeln ohne Stufen 1 und 6; kein `self_update` ohne `approved`.

## 5. Quellen

- HTAC (ICML 2026 Poster): https://icml.cc/virtual/2026/poster/63033
- Agent-Dice Paper (ACL 2026 Findings): https://aclanthology.org/2026.findings-acl.908/
- Agent-Dice Code: https://github.com/Wuzheng02/Agent-Dice
