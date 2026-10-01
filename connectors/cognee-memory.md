# Connector: Cognee-Memory (+ Graphiti temporal)

> Lab-Prinzip, MD-first. Behauptungen nur aus den verlinkten Quellen.
> „Gedächtnis", „dualer Speicher Graph + Vektor" und „Stufe 3" sind
> Auftrags-Vokabular (Mapping, keine Quellen-Behauptung).

## Identität

- Cognee: Open-Source AI-Memory, selbst-gehosteter Knowledge Graph –
  https://github.com/topoteretes/cognee
- Cognee-Doku (lokales Deployment): https://docs.cognee.ai/how-to-guides/cognee-sdk/deployment
- Graphiti: temporale Knowledge Graphen, Apache 2.0 –
  https://github.com/getzep/graphiti
- Zep-Paper (Graphiti als Engine): https://arxiv.org/html/2501.13956v1

## Mechanismen Cognee (aus Quellen abgeschrieben)

- Selbst-gehosteter Knowledge Graph: Graph + Vektor + Embeddings mit
  Ontologie-Grounding.
- Drei Schichten: Graph-DB, Vektor-DB, relational.
- Lokal eingebettet: SQLite + LanceDB + Kuzu, keine Zusatzdienste
  (laut Cognee-Doku, Deployment-Guide).
- Pipeline: Extract → Cognify → Load.
- Isolation pro Workspace.

## Mechanismen Graphiti (aus Quellen abgeschrieben)

- Temporale Wissensgraphen: Fakten mit Validitätsfenstern.
- Invalidierung statt Löschung bei Widersprüchen.
- Episoden + Provenienz pro Fakt.
- Inkrementelle Updates ohne Neuaufbau.
- Hybrid-Retrieval: semantisch + Keyword + Graph.
- Lizenz: Apache 2.0 (Graphiti-Repo).
- Zep-Paper beschreibt Graphiti als Engine; Messwerte (z. B.
  DMR/LongMemEval) werden hier NICHT selbst gemessen und NICHT mit
  Zahlen zitiert.

## Mapping auf Gedächtnis (Auftrag)

| Gedächtnis (Stufe 3, Auftrag) | Beleg |
|---|---|
| Dualer Speicher Graph + Vektor | Cognee: Graph + Vektor + Embeddings |
| Lokal ablegen (`data/memory/`) | Cognee lokal eingebettet (SQLite/LanceDB/Kuzu, keine Zusatzdienste) |
| Extract-Cognify-Load | Cognee-Pipeline |
| Isolation pro Ablage | Cognee: Isolation pro Workspace |
| Validitätsfenster + Invalidierung | Graphiti: Validitätsfenster, Invalidierung statt Löschung |
| Episoden + Provenienz | Graphiti: Episoden + Provenienz |
| Schreibt in Ontologie = Signal für Kognition | Auftrags-Schnittstelle (kein Quellen-Claim) |

## Grenzen (aus Quellen übernommen + Auftrag)

- Cognee/Graphiti führen hier nichts aus; Anwendung nur als MD-Abbild
  unter `data/memory/` (Auftrag: lokal, kostenlos, keine Cloud).
- Graphiti-OSS ist self-hosted und passt zur Vorgabe „lokal".
- Zep Cloud ist ein gemanagter Dienst und passt NICHT zur Vorgabe
  „lokal, kostenlos, keine Cloud" – wird NICHT verwendet (Abgrenzung
  dokumentiert, nicht verschwiegen).
- Keine Benchmark-Zahlen behauptet: Ergebnisse aus dem Zep-Paper werden
  nicht selbst gemessen und nicht mit Werten zitiert.
- Neue Aktionen/Schemata nur mit Beleg-Trace + Quellen-Link +
  menschlicher Freigabe, sonst `rejected` (Auftrag).

## Quellen (ausschließlich diese)

- https://github.com/topoteretes/cognee
- https://docs.cognee.ai/how-to-guides/cognee-sdk/deployment
- https://github.com/getzep/graphiti
- https://arxiv.org/html/2501.13956v1
