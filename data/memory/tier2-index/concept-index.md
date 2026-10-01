# Tier 2 – Concept Index (Konzept-zu-Ort-Mapping)

> Schicht: Tier 2 (Concept Index) der 3-Schicht-Gedächtnis-Pipeline.
> Zweck: semantisch-bewusstes selektives Laden (semantic-aware selective loading).
> Quelle (semantische Hierarchie + Top-down-Traversal): SHIMI (arXiv:2504.06135) –
> "supports top-down traversal from abstract intent to specific entities",
> "selecting only branches semantically aligned with the query".
> Quelle (query-aware selective retrieval): SwiftMem (arXiv:2601.08160) –
> "narrows retrieval to query-relevant memory subsets".
> Quelle (dynamisches Indexing/Linking): A-MEM (arXiv:2502.12110).
> Lab-Prinzip: keine Erfindungen – nur Auftrag + Quellen.

## Prinzip

Der Concept Index mappt **Konzept → Ort (Datei/Pfad)**. Beim Laden wird nur der
zur Anfrage passende Zweig geladen (selektiv), nicht der ganze Speicher.

Quelle: SHIMI (https://arxiv.org/abs/2504.06135), SwiftMem (https://arxiv.org/abs/2601.08160).

## Mapping-Tabelle (Konzept → Ort)

| Konzept | Ort (Datei) | Tier |
|---|---|---|
| Identität / Rolle | `data/memory/tier1-base/identity.md` | 1 |
| 8 Stufen | `data/memory/tier1-base/ontology.md` | 1 |
| 5 Phasen | `data/memory/tier1-base/ontology.md` | 1 |
| Kernbeziehungen | `data/memory/tier1-base/core-relations.md` | 1 |
| Gesetz (Prinzipien) | `AGENTS.md` | 1 |
| Fast Write Routing | `connectors/fast-write-routing.md` | 1 |
| Lifecycle-Phasen | `knowledge/lifecycle/*.md` | 1 |
| Connectoren | `connectors/*.md` | 1 |
| Skills | `skills/*/SKILL.md` | 1 |
| Working Memory (aktiv) | `data/memory/tier3-working/` | 3 |

## Lade-Regel (Auftrag, quellenbasiert)

1. Anfrage → semantische Zuordnung zu Konzept(en).
2. Nur die passenden Orte laden (selektiv, nicht alles).
3. Geladene Seiten → Tier 3 (Working Memory).
4. Nicht-passende Zweige überspringen (Pruning).

Quelle: SHIMI "prunes large irrelevant subtrees", SwiftMem "narrows retrieval to
query-relevant memory subsets".

## Quellen

- SHIMI: https://arxiv.org/abs/2504.06135
- SwiftMem: https://arxiv.org/abs/2601.08160
- A-MEM: https://arxiv.org/abs/2502.12110
