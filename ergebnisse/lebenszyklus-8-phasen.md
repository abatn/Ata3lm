# Lauf-Protokoll: 8 Lifecycle-Phasen (Multi-Agent-Lauf, t=0.L)

> Lab-Prinzip: Projekt + Skills + Connectors + Knowledge. MD-first.
> 8 Subagenten parallel, ein Subagent pro Phase (je Projekt + Skill +
> Connector + Knowledge-README = 32 Dateien). Koordination + Verifikation:
> Haupt-Agent. Keine Code-Änderung (Docs-only), kein `self_update`.

## Ergebnis (alle 8 Phasen angelegt)

| Stufe | Projekt | Skill | Connector | Knowledge |
|---|---|---|---|---|
| 1 Erfahrung (تجربة) | `knowledge/lifecycle/experience.md` | `skills/collect-experience/SKILL.md` | `connectors/agento-ariadne.md` | `knowledge/raw/README.md` |
| 2 Wissen (معرفة) | `knowledge/lifecycle/wissen.md` | `skills/structure-knowledge/SKILL.md` | `connectors/hela-semantic.md` | `knowledge/structured/README.md` |
| 3 Gedächtnis (ذاكرة) | `knowledge/lifecycle/gedaechtnis.md` | `skills/store-memory/SKILL.md` | `connectors/cognee-memory.md` | `data/memory/README.md` |
| 4 Kognition (إدراك) | `knowledge/lifecycle/kognition.md` | `skills/cognize/SKILL.md` | `connectors/cognee-validation.md` | `knowledge/cognition/README.md` |
| 6 Nicht-Kognition (لا-إدراك) | `knowledge/lifecycle/nicht-kognition.md` | `skills/non-cognitive/SKILL.md` | `connectors/affective-signals.md` | `knowledge/non-cognitive/README.md` |
| 5 Denken (فكر) | `knowledge/lifecycle/denken.md` | `skills/reflect/SKILL.md` | `connectors/mars-seaa.md` | `knowledge/reflection/README.md` |
| 7 Handeln (فعل) | `knowledge/lifecycle/handeln.md` | `skills/act/SKILL.md` | `connectors/htac-agentdice.md` | `knowledge/action/README.md` |
| 8 Wissen+ (معرفة+) | `knowledge/lifecycle/wissen-plus.md` | `skills/expand-knowledge/SKILL.md` | `connectors/hela-evolution.md` | `knowledge/expansion/README.md` |

## Verifikation durch Haupt-Agent (Compare)

- **Link-Allowlist:** alle URLs in den 32 Dateien gegen verifizierte
  Quellenliste geprüft – keine fremden Links, keine erfundenen Quellen.
- **Zahlen-Check:** einziger numerischer Schwellenwert (Fuzzy-Matching
  0.80) ist als Vorgabe (Auftrag) markiert, kein Quellen-Fakt.
- **Auftrag-Markierung:** jeder Subagent hat Auftrag-Anteile deklariert
  (Stufenfolge, Loop-Namen, Mappings, Signaltypen) – in den Files als
  `[Auftrag]` / „Vorgabe (Auftrag)" gekennzeichnet.
- **Abgrenzungen (ehrlich):** Zep Cloud ≠ lokal (nicht verwendet);
  HMM ∈ SEAA (nicht MARS); TRACE-Eval ≠ Revisions-Algorithmus;
  „Curator" = Rolle; Sentiment/Stress = Signaltypen (Auftrag).

## Quellen (zu den 7 Connectoren + Anker)

- AgentO: http://eprints.cs.univie.ac.at/8749/
- ARIADNE: https://exa.ai/library/publication/khfxyt54hk1
- HeLa-Mem: https://aclanthology.org/2026.acl-long.625/,
  https://github.com/ReinerBRO/HeLa-Mem
- AWS Semantic Layer:
  https://docs.aws.amazon.com/prescriptive-guidance/latest/semantic-layer-agentic-ai-ontology-reasoning-virtual-knowledge-graph/semantic-layer-agentic-ai-ontology-reasoning-virtual-knowledge-graph.html
- Cognee: https://github.com/topoteretes/cognee
- Graphiti: https://github.com/getzep/graphiti
- Zep-Paper: https://arxiv.org/html/2501.13956v1
- MARS: https://aclanthology.org/2026.acl-long.1329/,
  https://github.com/Paparare/MARS/tree/main
- SEAA: https://arxiv.org/abs/2609.17331
- HTAC: https://icml.cc/virtual/2026/poster/63033
- Agent-Dice: https://aclanthology.org/2026.findings-acl.908/,
  https://github.com/Wuzheng02/Agent-Dice
- EvoPathBench: https://arxiv.org/abs/2609.24663
- JISEM: https://jisem-journal.com/index.php/journal/article/view/12473
- CCA: https://researchr.org/publication/XueLM24-0

## Status / Freigabe

- `pending: menschliche Freigabe des 8-Phasen-Einbaus ausstehend`
- Nach Freigabe: t=1-Befüllung der Knowledge-Verzeichnisse
  (`raw/` zuerst, dann der Stufenfolge nach), erste Iteration als
  `ergebnisse/rekursion/008-*.md`.
