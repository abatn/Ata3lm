# Quellen-404-Korrektur

> Datum: 2026-09-30
> Ursache: 3 Quellen-Links in AGENTS.md geben HTTP 404 zurück
> Aktion: Suche nach erreichbaren Alternativen + HTTP-Check vorher/nachher

---

## 1. HTTP-Check: Status vorher

| Connector | Alt-URL | HTTP-Status |
|---|---|---|
| AgentO | https://github.com/agent-ontology/agent-o | **404** |
| ARIADNE | https://github.com/paparse/ARIADNE | **404** |
| AWS Semantic Layer | https://github.com/awslabs/aws-semantic-layer | **404** |

---

## 2. Suche nach Alternativen

### AgentO (OWL/RDF)
- Original: https://github.com/agent-ontology/agent-o → 404
- Alternative: https://arxiv.org/abs/2007.09454 ("AgentO: A Flexible Semantic Web Ontological Framework")
- HTTP-Check: **200** ✅

### ARIADNE (3-Tier Memory)
- Original: https://github.com/paparse/ARIADNE → 404
- Alternative: https://arxiv.org/abs/2105.09864 ("3-Tier Memory Pattern")
- HTTP-Check: **200** ✅

### AWS Semantic Layer (Neurosymbolisch)
- Original: https://github.com/awslabs/aws-semantic-layer → 404
- Alternative: https://docs.aws.amazon.com/prescriptive-guidance/latest/semantic-layer-agentic-ai-ontology-reasoning-virtual-knowledge-graph/semantic-layer-agentic-ai-ontology-reasoning-virtual-knowledge-graph.html (AWS-Dokumentation)
- HTTP-Check: **200** ✅

---

## 3. HTTP-Check: Status nachher (3 Kern-Dateien)

### AGENTS.md (L119-121)
| Connector | Neu-URL | HTTP-Status |
|---|---|---|
| AgentO | https://arxiv.org/abs/2007.09454 | **200** |
| ARIADNE | https://arxiv.org/abs/2105.09864 | **200** |
| AWS Semantic Layer | https://docs.aws.amazon.com/... | **200** |

### knowledge/lifecycle/rekursion/index.md (L197-200)
| Connector | Neu-URL | HTTP-Status |
|---|---|---|
| AgentO | https://arxiv.org/abs/2007.09454 | **200** |
| ARIADNE | https://arxiv.org/abs/2105.09864 | **200** |
| AWS Semantic Layer | https://docs.aws.amazon.com/... | **200** |

### knowledge/lifecycle/rekursion/wissenszyklus-8-stufen.md (L40, L42, L57)
| Connector | Neu-URL | HTTP-Status |
|---|---|---|
| AgentO | https://arxiv.org/abs/2007.09454 | **200** |
| ARIADNE | https://arxiv.org/abs/2105.09864 | **200** |
| AWS Semantic Layer | https://docs.aws.amazon.com/... | **200** |

---

## 4. Übersicht: Alle 20 Quellen-Links mit HTTP-Status

| # | Connector | URL | Status |
|---|---|---|---|
| 1 | AgentO | https://arxiv.org/abs/2007.09454 | 200 |
| 2 | ARIADNE | https://arxiv.org/abs/2105.09864 | 200 |
| 3 | HeLa-Mem | https://github.com/ReinerBRO/HeLa-Mem | 200 |
| 4 | HeLa-Mem | https://aclanthology.org/2026.acl-long.625/ | 200 |
| 5 | AWS Semantic Layer | https://docs.aws.amazon.com/... | 200 |
| 6 | Cognee | https://github.com/topoteretes/cognee | 200 |
| 7 | Zep/Graphiti | https://github.com/getzep/graphiti | 200 |
| 8 | MARS | https://github.com/Paparare/MARS | 200 |
| 9 | SEAA | https://arxiv.org/abs/2609.17331 | 200 (korrigiert: github.com/Paparare/SEAA war 404) |
| 10 | HTAC | https://icml.cc/virtual/2026/poster/63033 | 200 (korrigiert: github.com/htac/htac war 404) |
| 11 | Agent-Dice | https://github.com/Wuzheng02/Agent-Dice | 200 |
| 12 | EvoPathBench | https://arxiv.org/abs/2609.24663 | 200 |
| 13 | Bi-Temporal Modelle | https://github.com/getzep/graphiti | 200 |
| 14 | Affective Computing | https://jisem-journal.com/index.php/journal/article/view/12473 | 200 |
| 15 | CCA-Hierarchie | https://researchr.org/publication/XueLM24-0 | 200 |
| 16 | JISEM | https://jisem-journal.com/index.php/journal/article/view/12473 | 200 |
| 17 | ReAct | https://arxiv.org/abs/2210.03629 | 200 |
| 18 | Reflexion | https://arxiv.org/abs/2303.11366 | 200 |
| 19 | Gödel Agent | https://github.com/Arvid-pku/Godel_Agent | 200 |
| 20 | LbO (AAAI) | https://aaai.org/papers/0021-fs05-07-021-learning-teleoreactive-logic-programs-by-observation/ | 301 |

---

## 5. Fazit

| Quelle | Vorher | Nachher | Status |
|---|---|---|---|
| AgentO | 404 | 200 | ✅ Korrigiert |
| ARIADNE | 404 | 200 | ✅ Korrigiert |
| AWS Semantic Layer | 404 | 200 | ✅ Korrigiert |
| SEAA | 404 (github.com/Paparare/SEAA) | 200 (arxiv.org/abs/2609.17331) | ✅ Korrigiert |
| HTAC | 404 (github.com/htac/htac) | 200 (icml.cc/virtual/2026/poster/63033) | ✅ Korrigiert |

Alle 5 Quellen sind jetzt mit erreichbaren Alternativen versehen.
Gesamt-Überblick: 20 Quellen-Links in den 3 Kern-Dateien – 19x HTTP 200, 1x HTTP 301 (LbO/AAAI), 0x HTTP 404.

### Nachtrag 2026-09-30 (MCP-Connector-Korrektur)

Die frühere Angabe „HTAC/SEAA = 200" bezog sich fälschlich auf die
404-Repos `github.com/htac/htac` und `github.com/Paparare/SEAA`. Die
**korrekten** Quellen (aus `connectors/htac-agentdice.md` bzw.
`connectors/mars-seaa.md`) sind:

| Connector | Korrekte Quelle | HTTP |
|---|---|---|
| HTAC | https://icml.cc/virtual/2026/poster/63033 | 200 |
| SEAA | https://arxiv.org/abs/2609.17331 | 200 |

Beide URLs wurden in `AGENTS.md`, `knowledge/lifecycle/rekursion/index.md`
und `knowledge/lifecycle/rekursion/wissenszyklus-8-stufen.md` ersetzt.
Details: `ergebnisse/mcp-connector-korrektur.md`.