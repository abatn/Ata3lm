---
name: store-memory
process: pipeline.py
description: Strukturiertes Wissen als dualen Speicher (Graph-Knoten/Kanten + Embeddings) lokal unter data/memory/ ablegen, mit temporaler Gültigkeit und Provenienz. Nutze diesen Skill, wenn Wissen aus Stufe 2 (Wissen) in Stufe 3 (Gedächtnis) überführt werden soll – lokal, kostenlos, ohne Cloud.
---

# Skill: store-memory

> Lab-Prinzip, MD-first. Keine Erfindungen: alles aus Auftrag oder den
> verlinkten Quellen. Auftrag-Begriffe sind als solche markiert.

## Zweck

Strukturiertes Wissen in das Gedächtnis (Stufe 3, Auftrags-Begriff)
überführen und lokal ablegen.

Quellen (ausschließlich diese):

- https://github.com/topoteretes/cognee
- https://docs.cognee.ai/how-to-guides/cognee-sdk/deployment
- https://github.com/getzep/graphiti
- https://arxiv.org/html/2501.13956v1

Projekt-Doku: `knowledge/lifecycle/gedaechtnis.md`.

## Wann anwenden

- Wenn strukturiertes Wissen (Entitäten, Beziehungen, Quellverweise)
  aus der Wissens-Stufe vorliegt.
- Wenn ein Fakt mit Gültigkeit + Provenienz abzulegen ist.
- NICHT anwenden ohne Quellverweis; NICHT mit Cloud-Diensten.

## Ablauf

1. **Strukturiertes Wissen übernehmen**
   - Input prüfen: Entitäten, Beziehungen, Zeitangaben, Quelle vorhanden?
   - Fehlt Quelle oder Zeitangabe: anhalten, Lücke melden, nichts ablegen.
2. **Graph-Knoten/Kanten + Embeddings erzeugen**
   - Knoten = Entitäten, Kanten = Beziehungen (Cognee-Mapping:
     Extract → Cognify → Load; Ontologie-Grounding).
   - Vektor-Anteil: Embeddings für semantische Suche vorsehen
     (Cognee: Graph + Vektor + Embeddings).
3. **Lokal ablegen**
   - Ziel: `data/memory/` (SQLite/LanceDB-Analogon bzw. MD-Abbild).
   - Format und Pflichtfelder nach `data/memory/README.md`.
   - Workspace-Trennung beachten (Cognee-Mapping: Isolation pro
     Workspace); keine Zusatzdienste, keine Cloud.
4. **Temporale Gültigkeit + Provenienz vermerken**
   - Graphiti-Mapping: Validitätsfenster setzen; bei Widerspruch alte
     Fakten invalidieren statt löschen; Episode + Provenienz festhalten;
     inkrementelle Updates (anhängen, kein Neuaufbau);
     Hybrid-Retrieval (semantisch/Keyword/Graph) als Zugriffsweg
     vorsehen.

## Guardrails (verbindlich, vom Skill erzwungen)

1. **Lokal Self-hosted:** nur `data/memory/` bzw. lokal eingebettet
   (SQLite/LanceDB/Kuzu-Analogon); keine Cloud-Dienste für Speicher.
2. **Keine Cloud-Dienste:** gemanagte Dienste (insb. Zep Cloud) sind
   ausgeschlossen (passt NICHT zu lokal).
3. **Provenienz pro Fakt:** kein Schreibvorgang ohne Quelle + Episode +
   Gültigkeitsfenster.
4. **Keine Erfindungen:** nur Auftrag oder Quellen; neue Schemata nur mit
   Beleg-Trace + Quellen-Link + menschlicher Freigabe, sonst `rejected`.
5. **Stufen-Disziplin:** kein Handeln ohne Beobachten; Schreiben in die
   Ontologie ist das Signal für Kognition (Stufe 4), nicht umgekehrt.

## Input / Output

Input: strukturiertes Wissen (Entitäten, Beziehungen, Quelle, Zeitangabe).

Output: abgelegter Fakt in `data/memory/` mit Pflichtfeldern
Gültigkeit, Provenienz, Quelle.

## Referenzen

- `knowledge/lifecycle/gedaechtnis.md` (Stufe 3)
- `connectors/cognee-memory.md` (Mechanismen)
- `data/memory/README.md` (Ablagekonvention)


## Prozesse (Aufrufe) [Auftrag]

Dieser Skill ruft folgende Prozesse in `data/memory/` auf (MCP-Interface nach Atomic: https://atomicapp.ai/guides/mcp-server/):

- `lru_cache.py` + `pipeline.py` — Write (Stufe 3)
- **MCP-Tools:** `memory.search`, `memory.write`

Quelle (Auftrag): `skills/README.md` (Skill→Prozess), `ergebnisse/mcp-memory.md` (Atomic).
