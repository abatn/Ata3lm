# Memory-Pipeline – dreischichtiges Gedächtnis (2025–2026)

> Datum: 2026-10-01
> Zweck: Umbau von `data/memory/` (leer) zu einer dreischichtigen Gedächtnis-Pipeline.
> Lab-Prinzip: Keine Erfindungen – jede Schicht mit Quellen-Link (verifiziert HTTP 200).
> Geltung: unterliegt `AGENTS.md` (§6 Keine Erfindungen, §9 Gate).

---

## 1. Die 3 Schichten

| Schicht | Inhalt | Ordner | Quellen |
|---|---|---|---|
| **Tier 1 – Base Knowledge** | Identität, Ontologie (8 Stufen, 5 Phasen), Kernbeziehungen | `data/memory/tier1-base/` | SHIMI, ARIADNE, Graphiti |
| **Tier 2 – Concept Index** | Konzept-zu-Ort-Mapping, semantisch-bewusstes selektives Laden | `data/memory/tier2-index/` | SHIMI, SwiftMem, A-MEM |
| **Tier 3 – Working Memory** | begrenzter LRU-Cache, max. 15 aktive Items, Pinning | `data/memory/tier3-working/` | MemGPT, Cortex |

**Ablauf:**
```text
Anfrage ─▶ Tier 2 (Concept Index, selektiv) ─▶ passende Orte (Tier 1)
       ─▶ Tier 3 (Working Memory, max 15, LRU-Eviction außer pinned)
```

---

## 2. Gebaute Struktur (verifiziert)

```text
data/memory/
├── README.md ....................... Pipeline-Übersicht
├── tier1-base/
│   ├── identity.md ................. Identität + Ontologie-Anker
│   ├── ontology.md ................. 8 Stufen + 5 Phasen
│   └── core-relations.md ........... typisierte Kernbeziehungen
├── tier2-index/
│   └── concept-index.md ............ Konzept-zu-Ort-Mapping
└── tier3-working/
    └── README.md ................... LRU-Cache (max 15, Pinning)
```

---

## 3. Quellen (alle HTTP 200, verifiziert 2026-10-01)

| Schicht | Paper | Link | Zweck |
|---|---|---|---|
| Tier 1 | SHIMI | https://arxiv.org/abs/2504.06135 | semantische Hierarchie, Top-down-Traversal |
| Tier 1 | ARIADNE | https://arxiv.org/abs/2105.09864 | 3-Tier Memory (Semantic, bi-temporal) |
| Tier 1 | Graphiti (Zep) | https://arxiv.org/abs/2501.13956 | temporaler Graph, Validitätsfenster |
| Tier 2 | SHIMI | https://arxiv.org/abs/2504.06135 | Konzept-Hierarchie, Pruning |
| Tier 2 | SwiftMem | https://arxiv.org/abs/2601.08160 | query-aware selektive Retrieval |
| Tier 2 | A-MEM | https://arxiv.org/abs/2502.12110 | dynamisches Indexing/Linking |
| Tier 3 | MemGPT | https://arxiv.org/abs/2310.08560 | hierarchisches Memory, Working Context, **Pinning**, Eviction |
| Tier 3 | Cortex | https://arxiv.org/abs/2509.17360 | semantisches Caching, Eviction, Prefetching |
| — | RMM (ACL 2025) | https://aclanthology.org/2025.acl-long.413.pdf | Reflective Memory Management (Themen-Index) |

**Was die Quellen belegen (wörtlich):**
- **MemGPT:** „working context is a fixed-size read/write block"; „System instructions are read-only and **pinned** to main context"; „queue eviction policy".
- **SHIMI:** „models knowledge as a dynamically structured hierarchy of concepts"; „top-down traversal from abstract intent to specific entities"; „prunes large irrelevant subtrees".
- **SwiftMem:** „narrows retrieval to query-relevant memory subsets"; Temporal Index + Semantic DAG-Tag Index.
- **Cortex:** „semantic-aware cache hit"; „cost-efficient eviction policy"; „predictive prefetching".

---

## 4. AGENTS.md-Konformität

| Prinzip | Anwendung |
|---|---|
| §6 Keine Erfindungen | jede Schicht mit Paper-Link; Zahlen/Mechanismen nur aus Quellen |
| §9 Gate | neue Quelle → Human-Gate (ask) |
| §4 Brich die Muster | neues Schema (3-Tier) mit Beleg-Trace + Link + Freigabe |
| §10 Fast Write Routing | Router entscheidet, was in Tier 1/2/3 geschrieben wird |

---

## 5. Status

| Schicht | Status |
|---|---|
| Tier 1 (Base Knowledge) | ✅ befüllt (Identität, Ontologie, Kernbeziehungen) |
| Tier 2 (Concept Index) | ✅ befüllt (Mapping Konzept→Ort) |
| Tier 3 (Working Memory) | ✅ Struktur (0 aktive Items, max 15) |

**Ehrlich:** Die **Struktur** der Pipeline ist gebaut und quellenbelegt. Es sind
noch **keine Fakten** abgelegt (data/memory war leer); die Befüllung erfolgt über
`skills/store-memory/SKILL.md`.

**Geänderte Dateien:**
- `data/memory/README.md` (Pipeline-Übersicht)
- `data/memory/tier1-base/{identity,ontology,core-relations}.md` (neu)
- `data/memory/tier2-index/concept-index.md` (neu)
- `data/memory/tier3-working/README.md` (neu)
- `knowledge/lifecycle/gedaechtnis.md` (§3.2 + Quellen erweitert)
