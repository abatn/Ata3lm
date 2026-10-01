# Gedächtnis – Stufe 3 des 8-Stufen-Zyklus

> Lab-Prinzip: Projekt + Skills + Connectors + Knowledge. MD-first.
> Eltern-Dok: `knowledge/lifecycle/rekursion/wissenszyklus-8-stufen.md` (Stufe 3).
> Keine Erfindungen: Alle Aussagen stammen aus dem Auftrag oder aus den
> unten genannten Quellen. Auftrag-Begriffe sind als solche markiert
> (Auftrag = gesetzte Betriebsregel, kein Quellen-Beleg).
> Vorgabe (Auftrag): lokal, kostenlos, keine Cloud.

## 1. Definition (Auftrag)

**Gedächtnis** (Auftrags-Begriff für Stufe 3) bedeutet: Wissen lokal
speichern als **dualer Speicher Graph + Vektor**.

- **Graph-Anteil:** Knoten und Kanten (Entitäten + Beziehungen),
  Ontologie-geerdet.
- **Vektor-Anteil:** Embeddings für semantische Suche.
- **Ablage:** lokal unter `data/memory/` (MD-Abbild des lokalen Speichers;
  siehe `data/memory/README.md`).

Die Stufenfolge selbst (Stufe 3 = Gedächtnis) ist gesetzte Ordnung
(Auftrag), kein Paper-Claim.

## 2. Cognee-Mapping (aus Quellen abgeschrieben)

Cognee ist Open-Source AI-Memory und selbst-gehosteter Knowledge Graph
(Graph + Vektor + Embeddings, Ontologie-Grounding).

- **Drei Schichten:** Graph-DB + Vektor-DB + relationale Ablage.
- **Lokal eingebettet:** SQLite + LanceDB + Kuzu, ohne Zusatzdienste.
- **Pipeline:** Extract → Cognify → Load.
- **Isolation:** pro Workspace getrennt.

Belegt in:

- https://github.com/topoteretes/cognee
- https://docs.cognee.ai/how-to-guides/cognee-sdk/deployment

## 3. Graphiti-Mapping (aus Quellen abgeschrieben)

Graphiti baut temporale Wissensgraphen:

- **Fakten mit Validitätsfenstern:** jede Tatsache trägt einen
  Gültigkeitszeitraum.
- **Alte Fakten invalidiert statt gelöscht:** Widersprüche erzeugen
  Invalidierung, kein Löschen der Historie.
- **Episoden + Provenienz:** jede Änderung ist auf eine Episode
  (Quelleingabe) mit Herkunft zurückführbar.
- **Inkrementelle Updates:** neue Episoden werden laufend eingepflegt,
  ohne Neuaufbau des Graphen.
- **Hybrid-Retrieval:** semantische + Keyword- + Graph-Suche kombiniert.

Belegt in:

- https://github.com/getzep/graphiti (Apache 2.0)
- https://arxiv.org/html/2501.13956v1 (Graphiti als Engine des dort
  beschriebenen Systems; Benchmark-Ergebnisse wie DMR/LongMemEval werden
  hier NICHT selbst gemessen und NICHT mit Zahlen zitiert)

### 3.1 Abgrenzung lokal vs. Cloud (ehrlich getrennt, Auftrag + Quellen)

- **Graphiti-OSS ist self-hosted** und passt zur Vorgabe „lokal"
  (Quelle: Graphiti-Repo, Apache 2.0).
- **Zep Cloud ist ein gemanagter Dienst** und passt NICHT zur Vorgabe
  „lokal, kostenlos, keine Cloud" – wird daher NICHT verwendet.
   Diese Abgrenzung ist dokumentiert, nicht verschwiegen.

## 3.2 Dreischichtige Gedächtnis-Pipeline (Auftrag + Quellen)

Das Gedächtnis wird als **dreischichtige Pipeline** aufgebaut (MD-Abbild unter
`data/memory/`). Jede Schicht ist quellenbelegt:

| Schicht | Inhalt | Ordner | Quelle |
|---|---|---|---|
| **Tier 1 – Base Knowledge** | Identität, Ontologie (8 Stufen, 5 Phasen), Kernbeziehungen | `data/memory/tier1-base/` | SHIMI (arXiv:2504.06135), ARIADNE (arXiv:2105.09864), Graphiti (arXiv:2501.13956) |
| **Tier 2 – Concept Index** | Konzept-zu-Ort-Mapping, semantisch-bewusstes selektives Laden | `data/memory/tier2-index/` | SHIMI (arXiv:2504.06135), SwiftMem (arXiv:2601.08160), A-MEM (arXiv:2502.12110) |
| **Tier 3 – Working Memory** | begrenzter LRU-Cache, max. 15 aktive Items, Pinning | `data/memory/tier3-working/` | MemGPT (arXiv:2310.08560), Cortex (arXiv:2509.17360) |

**Ablauf:** Anfrage → Tier 2 (Concept Index, selektiv) → passende Orte →
Tier 3 (Working Memory, max 15, LRU-Eviction außer pinned).

Quellen (jede Schicht mit Link):
- SHIMI – semantische Hierarchie, Top-down-Traversal: https://arxiv.org/abs/2504.06135
- SwiftMem – query-aware selektive Retrieval: https://arxiv.org/abs/2601.08160
- A-MEM – dynamisches Indexing/Linking: https://arxiv.org/abs/2502.12110
- MemGPT – hierarchisches Memory, Working Context, Pinning, Eviction: https://arxiv.org/abs/2310.08560
- Cortex – semantisches Caching, Eviction, Prefetching: https://arxiv.org/abs/2509.17360
- ARIADNE – 3-Tier Memory (Semantic, bi-temporal): https://arxiv.org/abs/2105.09864
- Graphiti – temporaler Graph (Validitätsfenster): https://arxiv.org/abs/2501.13956

## 4. Rekursionsschnittstelle (Auftrag)

Gedächtnis schreibt in die Ontologie (Auftrags-Begriff für den
gemeinsamen Speicher `M`); dieser Schreibvorgang ist das Signal für
Kognition (Stufe 4 des 8-Stufen-Zyklus).

```text
Wissen ──Gedächtnis (Stufe 3)──▶ Ontologie in M
                                     │
                                     ▼
                              Kognition (Stufe 4) liest M
```

- **Lesen:** strukturiertes Wissen aus Stufe 2 (Wissen).
- **Schreiben:** Graph-Knoten/Kanten + Embeddings + Validitätsfenster +
  Provenienz nach `data/memory/`.
- **Signal:** erst nach Ablage darf Kognition lesen (Stufen-Disziplin:
  keine Stufe überspringen).

## 5. Input / Output

Input (Auftrag): strukturiertes Wissen (Entitäten, Beziehungen,
Quellverweise, Zeitangaben).

Output (Auftrag): abgelegte Fakten in `data/memory/` mit Pflichtfeldern
Gültigkeit, Provenienz, Quelle (vgl. `data/memory/README.md`).

## 6. Guardrails (Auftrag, verbindlich)

1. **Lokal Self-hosted:** Speicher nur lokal (SQLite/LanceDB-Analogon
   bzw. MD-Abbild unter `data/memory/`).
2. **Keine Cloud-Dienste für Speicher:** kein gemanagter Dienst
   (insb. kein Zep Cloud) für Ablage oder Retrieval.
3. **Provenienz pro Fakt:** jeder Fakt braucht Quelle + Episode +
   Gültigkeitsfenster; ohne diese drei kein Schreibvorgang.
4. **Keine Erfindungen:** nur Auftrag-Begriffe und Quellen-Aussagen
   ablegen; jede Grenzüberschreitung (neues Schema) braucht
   Beleg-Trace + Quellen-Link + menschliche Freigabe, sonst `rejected`.
5. **Interface-Stabilität:** keine Formatänderung von `data/memory/`
   ohne Freigabe.

## 7. Quellen (ausschließlich diese, keine weiteren behauptet)

- Cognee-Repo: https://github.com/topoteretes/cognee
- Cognee-Doku (lokales Deployment): https://docs.cognee.ai/how-to-guides/cognee-sdk/deployment
- Graphiti-Repo: https://github.com/getzep/graphiti
- Zep-Paper (Graphiti als Engine): https://arxiv.org/html/2501.13956v1
- SHIMI (Semantic Hierarchical Memory Index): https://arxiv.org/abs/2504.06135
- SwiftMem (query-aware agentic memory): https://arxiv.org/abs/2601.08160
- A-MEM (Agentic Memory for LLM Agents): https://arxiv.org/abs/2502.12110
- MemGPT (hierarchisches Memory, Working Context, Pinning): https://arxiv.org/abs/2310.08560
- Cortex (semantisches Caching, Eviction): https://arxiv.org/abs/2509.17360
- ARIADNE (3-Tier Memory): https://arxiv.org/abs/2105.09864
- Skill: `skills/store-memory/SKILL.md`
- Connector: `connectors/cognee-memory.md`
- Ablage: `data/memory/README.md`, `data/memory/tier1-base/`, `data/memory/tier2-index/`, `data/memory/tier3-working/`
