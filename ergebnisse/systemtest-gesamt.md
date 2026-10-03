# Systemtest Gesamt – Struktur · MCP · 8 Stufen · Endpoint · Urteil

> **Datum:** 2026-10-01 · **Score 8-Stufen: 22/22 = 100.0 %** · **Auto-Gate: allow** · **MCP aktiv lauffähig: 15/17** · **Fehlschläge in der Funktionsprüfung: 0**

Dokumentation: `ergebnisse/systemtest-mcp.md` (Aufgabe 2), `ergebnisse/systemtest-8-stufen.md` (Aufgabe 3), diese Datei (Aufgaben 1, 4, 5).

---

## Aufgabe 1 – Struktur-Test

### Komponenten (gemessen, nicht behauptet)

| Komponente | Erwartung | Ist (gezählt) | OK |
|---|---|---|---|
| `AGENTS.md` | §1–§11 | 392 Zeilen, 8 Prinzipien (`### 1.`–`### 8.`), §9 + §9.1–§9.3, §10 + §10.1–§10.7, §11 + §11.1–§11.4 | ✓ |
| `knowledge/lifecycle/` | 8 Stufen | 8 Stufen-Dateien (denken, experience, gedaechtnis, handeln, kognition, nicht-kognition, wissen-plus, wissen) | ✓ |
| `knowledge/lifecycle/rekursion/` | 5 Phasen | 5 Phasen (akt, compare, konstrukt, observe, revise) + `index.md` + `wissenszyklus-8-stufen.md` = 7 Dateien | ✓ |
| `connectors/` | 16 | 16 | ✓ |
| `skills/` (ohne `versions/`) | 14 `SKILL.md` | 14 | ✓ |
| `data/memory/` | 9 Prozesse | 9 (approval.py, bi_temporal.py, bias_monitor.py, fast_write_router.py, ingestion_hook.py, reflective_agent.py, trust.py, tier3-working/lru_cache.py, shared/shared_memory.py) | ✓ |
| `ergebnisse/` | 81 Dateien (vor den Systemtest-Doku-Dateien) | 85 (inkl. Systemtest-/Korrektur-Doku) | ✓ |
| `ergebnisse/rekursion/` | Index bis 031 | 35 Dateien | ✓ |

### Komplette Datei-Struktur (`find … -name "*.md" | sort`)

**237 Markdown-Dateien:**

```
/home/opc/knowledge-agent/AGENTS.md
/home/opc/knowledge-agent/CONTRIBUTING.md
/home/opc/knowledge-agent/README.md
/home/opc/knowledge-agent/connectors/affective-signals.md
/home/opc/knowledge-agent/connectors/agento-ariadne.md
/home/opc/knowledge-agent/connectors/cca-framework.md
/home/opc/knowledge-agent/connectors/cognee-memory.md
/home/opc/knowledge-agent/connectors/cognee-validation.md
/home/opc/knowledge-agent/connectors/consistency-gap.md
/home/opc/knowledge-agent/connectors/fast-write-routing.md
/home/opc/knowledge-agent/connectors/goedel-agent.md
/home/opc/knowledge-agent/connectors/governance-mcp.md
/home/opc/knowledge-agent/connectors/hela-evolution.md
/home/opc/knowledge-agent/connectors/hela-semantic.md
/home/opc/knowledge-agent/connectors/htac-agentdice.md
/home/opc/knowledge-agent/connectors/mars-seaa.md
/home/opc/knowledge-agent/connectors/observer-agent.md
/home/opc/knowledge-agent/connectors/react.md
/home/opc/knowledge-agent/connectors/reflexion-trace.md
/home/opc/knowledge-agent/data/memory/README.md
/home/opc/knowledge-agent/data/memory/shared/README.md
/home/opc/knowledge-agent/data/memory/tier1-base/core-relations.md
/home/opc/knowledge-agent/data/memory/tier1-base/identity.md
/home/opc/knowledge-agent/data/memory/tier1-base/ontology.md
/home/opc/knowledge-agent/data/memory/tier1-base/versions/v1/core-relations.md
/home/opc/knowledge-agent/data/memory/tier1-base/versions/v1/identity.md
/home/opc/knowledge-agent/data/memory/tier1-base/versions/v1/ontology.md
/home/opc/knowledge-agent/data/memory/tier1-base/versions/v2/core-relations.md
/home/opc/knowledge-agent/data/memory/tier1-base/versions/v2/identity.md
/home/opc/knowledge-agent/data/memory/tier1-base/versions/v2/ontology.md
/home/opc/knowledge-agent/data/memory/tier1-base/versions/v3/core-relations.md
/home/opc/knowledge-agent/data/memory/tier1-base/versions/v3/identity.md
/home/opc/knowledge-agent/data/memory/tier1-base/versions/v3/ontology.md
/home/opc/knowledge-agent/data/memory/tier1-base/versions/v4/core-relations.md
/home/opc/knowledge-agent/data/memory/tier1-base/versions/v4/identity.md
/home/opc/knowledge-agent/data/memory/tier1-base/versions/v4/ontology.md
/home/opc/knowledge-agent/data/memory/tier2-index/concept-index.md
/home/opc/knowledge-agent/data/memory/tier2-index/evicted-index.md
/home/opc/knowledge-agent/data/memory/tier2-index/hub-index.md
/home/opc/knowledge-agent/data/memory/tier3-working/README.md
/home/opc/knowledge-agent/ergebnisse/8-prompts-umsetzung.md
/home/opc/knowledge-agent/ergebnisse/adaptive-forgetting.md
/home/opc/knowledge-agent/ergebnisse/automatisches-gate.md
/home/opc/knowledge-agent/ergebnisse/bi-temporal.md
/home/opc/knowledge-agent/ergebnisse/bias-drift.md
/home/opc/knowledge-agent/ergebnisse/cognize-test.md
/home/opc/knowledge-agent/ergebnisse/doku-korrektur-fwr.md
/home/opc/knowledge-agent/ergebnisse/drift-index.md
/home/opc/knowledge-agent/ergebnisse/falle-automatisches-gate.md
/home/opc/knowledge-agent/ergebnisse/falle-zeilenangaben.md
/home/opc/knowledge-agent/ergebnisse/falsifikationstest.md
/home/opc/knowledge-agent/ergebnisse/fast-write-router.md
/home/opc/knowledge-agent/ergebnisse/fast-write-routing-analyse.md
/home/opc/knowledge-agent/ergebnisse/fast-write-routing-korrektur.md
/home/opc/knowledge-agent/ergebnisse/fast-write-routing-test.md
/home/opc/knowledge-agent/ergebnisse/forschungsluecken-4.md
/home/opc/knowledge-agent/ergebnisse/forschungsumsetzung-2026.md
/home/opc/knowledge-agent/ergebnisse/fwr-test.md
/home/opc/knowledge-agent/ergebnisse/gesamtpruefung-final.md
/home/opc/knowledge-agent/ergebnisse/gesamtpruefung-mcp.md
/home/opc/knowledge-agent/ergebnisse/gesamtpruefung.md
/home/opc/knowledge-agent/ergebnisse/hmm-code.md
/home/opc/knowledge-agent/ergebnisse/hmm-integration.md
/home/opc/knowledge-agent/ergebnisse/hmm-revise.md
/home/opc/knowledge-agent/ergebnisse/hmm-trageheit.md
/home/opc/knowledge-agent/ergebnisse/inferenz-shacl-test.md
/home/opc/knowledge-agent/ergebnisse/inferenz-shacl.md
/home/opc/knowledge-agent/ergebnisse/ingestion-hook.md
/home/opc/knowledge-agent/ergebnisse/ingestion-pipeline.md
/home/opc/knowledge-agent/ergebnisse/knowledge-agent-in-6-zeilen.md
/home/opc/knowledge-agent/ergebnisse/knowledge-agent-plan.md
/home/opc/knowledge-agent/ergebnisse/l4-operational.md
/home/opc/knowledge-agent/ergebnisse/l4-procedural.md
/home/opc/knowledge-agent/ergebnisse/lebenszyklus-8-phasen.md
/home/opc/knowledge-agent/ergebnisse/lru-befuellung.md
/home/opc/knowledge-agent/ergebnisse/lru-cache-test.md
/home/opc/knowledge-agent/ergebnisse/mcp-16-test.md
/home/opc/knowledge-agent/ergebnisse/mcp-check-drift.md
/home/opc/knowledge-agent/ergebnisse/mcp-check-gliner.md
/home/opc/knowledge-agent/ergebnisse/mcp-check-lyapunov.md
/home/opc/knowledge-agent/ergebnisse/mcp-connector-korrektur.md
/home/opc/knowledge-agent/ergebnisse/mcp-layer.md
/home/opc/knowledge-agent/ergebnisse/mcp-neu.md
/home/opc/knowledge-agent/ergebnisse/mcp-ziel-plan.md
/home/opc/knowledge-agent/ergebnisse/memory-lifecycle.md
/home/opc/knowledge-agent/ergebnisse/memory-pipeline.md
/home/opc/knowledge-agent/ergebnisse/memrouter-optimierung.md
/home/opc/knowledge-agent/ergebnisse/multi-agent-sharing.md
/home/opc/knowledge-agent/ergebnisse/neuro-symbolic-loop.md
/home/opc/knowledge-agent/ergebnisse/pii-minimierung.md
/home/opc/knowledge-agent/ergebnisse/procedural-memory.md
/home/opc/knowledge-agent/ergebnisse/proposal-template.md
/home/opc/knowledge-agent/ergebnisse/public-apis-analyse.md
/home/opc/knowledge-agent/ergebnisse/quellen-404-korrektur.md
/home/opc/knowledge-agent/ergebnisse/quellen-test.md
/home/opc/knowledge-agent/ergebnisse/reflective-agent.md
/home/opc/knowledge-agent/ergebnisse/rekursion-plan.md
/home/opc/knowledge-agent/ergebnisse/rekursion/000-template.md
/home/opc/knowledge-agent/ergebnisse/rekursion/001-bootstrap-rekursion-phase.md
/home/opc/knowledge-agent/ergebnisse/rekursion/002-konstrukt-bootstrap.md
/home/opc/knowledge-agent/ergebnisse/rekursion/003-akt-bootstrap.md
/home/opc/knowledge-agent/ergebnisse/rekursion/004-observe-bootstrap.md
/home/opc/knowledge-agent/ergebnisse/rekursion/005-compare-bootstrap.md
/home/opc/knowledge-agent/ergebnisse/rekursion/006-revise-bootstrap.md
/home/opc/knowledge-agent/ergebnisse/rekursion/007-wissenszyklus-bootstrap.md
/home/opc/knowledge-agent/ergebnisse/rekursion/008-t1-rekursion.md
/home/opc/knowledge-agent/ergebnisse/rekursion/009-t2-echte-rekursion.md
/home/opc/knowledge-agent/ergebnisse/rekursion/010-t3-rekursion.md
/home/opc/knowledge-agent/ergebnisse/rekursion/011-t4-rekursion.md
/home/opc/knowledge-agent/ergebnisse/rekursion/012-t5-rekursion.md
/home/opc/knowledge-agent/ergebnisse/rekursion/013-t6-rekursion.md
/home/opc/knowledge-agent/ergebnisse/rekursion/014-ingestion-hook-v2.md
/home/opc/knowledge-agent/ergebnisse/rekursion/015-procedural-memory-l4.md
/home/opc/knowledge-agent/ergebnisse/rekursion/016-neuro-symbolic-loop.md
/home/opc/knowledge-agent/ergebnisse/rekursion/017-memory-lifecycle.md
/home/opc/knowledge-agent/ergebnisse/rekursion/018-multi-agent-sharing.md
/home/opc/knowledge-agent/ergebnisse/rekursion/019-trust-governance.md
/home/opc/knowledge-agent/ergebnisse/rekursion/020-l4-procedural.md
/home/opc/knowledge-agent/ergebnisse/rekursion/021-shared-konflikt.md
/home/opc/knowledge-agent/ergebnisse/rekursion/022-pii-minimierung.md
/home/opc/knowledge-agent/ergebnisse/rekursion/023-zwei-personen.md
/home/opc/knowledge-agent/ergebnisse/rekursion/024-bias-drift.md
/home/opc/knowledge-agent/ergebnisse/rekursion/025-l4-operational.md
/home/opc/knowledge-agent/ergebnisse/rekursion/026-shared-supersession.md
/home/opc/knowledge-agent/ergebnisse/rekursion/027-drift-index.md
/home/opc/knowledge-agent/ergebnisse/rekursion/028-bi-temporal.md
/home/opc/knowledge-agent/ergebnisse/rekursion/029-forschungsluecken-4.md
/home/opc/knowledge-agent/ergebnisse/rekursion/030-governance-mcp.md
/home/opc/knowledge-agent/ergebnisse/rekursion/031-fwr-modell.md
/home/opc/knowledge-agent/ergebnisse/rekursion/README.md
/home/opc/knowledge-agent/ergebnisse/rekursion/approved-2026-09-30.md
/home/opc/knowledge-agent/ergebnisse/rekursion/governance-luecke-geschlossen-2026-10-01.md
/home/opc/knowledge-agent/ergebnisse/rekursion/solver/README.md
/home/opc/knowledge-agent/ergebnisse/rekursion/validierungsset/01-struktur-check.md
/home/opc/knowledge-agent/ergebnisse/rekursion/validierungsset/02-connector-reference.md
/home/opc/knowledge-agent/ergebnisse/rekursion/validierungsset/03-quellen-link-check.md
/home/opc/knowledge-agent/ergebnisse/rekursion/validierungsset/04-solver-test-1.md
/home/opc/knowledge-agent/ergebnisse/rekursion/validierungsset/05-solver-test-2.md
/home/opc/knowledge-agent/ergebnisse/rekursion/validierungsset/06-solver-test-3.md
/home/opc/knowledge-agent/ergebnisse/rekursion/validierungsset/07-solver-v3-test-1.md
/home/opc/knowledge-agent/ergebnisse/rekursion/validierungsset/08-solver-v3-test-2.md
/home/opc/knowledge-agent/ergebnisse/rekursion/validierungsset/09-solver-v3-test-3.md
/home/opc/knowledge-agent/ergebnisse/rekursion/validierungsset/10-solver-v4-test-1.md
/home/opc/knowledge-agent/ergebnisse/rekursion/validierungsset/11-solver-v4-test-2.md
/home/opc/knowledge-agent/ergebnisse/rekursion/validierungsset/12-solver-v5-test-1.md
/home/opc/knowledge-agent/ergebnisse/rekursion/validierungsset/13-solver-v5-test-2.md
/home/opc/knowledge-agent/ergebnisse/rekursion/validierungsset/14-solver-v5-test-3.md
/home/opc/knowledge-agent/ergebnisse/rekursion/validierungsset/15-solver-v5-test-4.md
/home/opc/knowledge-agent/ergebnisse/rekursion/validierungsset/16-solver-v6-test-1.md
/home/opc/knowledge-agent/ergebnisse/rekursion/validierungsset/17-solver-v6-test-2.md
/home/opc/knowledge-agent/ergebnisse/rekursion/validierungsset/README.md
/home/opc/knowledge-agent/ergebnisse/shared-konflikt.md
/home/opc/knowledge-agent/ergebnisse/shared-supersession.md
/home/opc/knowledge-agent/ergebnisse/spreading-activation.md
/home/opc/knowledge-agent/ergebnisse/systemtest-8-stufen.md
/home/opc/knowledge-agent/ergebnisse/systemtest-gesamt.md
/home/opc/knowledge-agent/ergebnisse/systemtest-mcp.md
/home/opc/knowledge-agent/ergebnisse/technologie-integration-pruefung.md
/home/opc/knowledge-agent/ergebnisse/test-connectoren.md
/home/opc/knowledge-agent/ergebnisse/test-fast-write-routing.md
/home/opc/knowledge-agent/ergebnisse/test-gesamturteil.md
/home/opc/knowledge-agent/ergebnisse/test-lifecycle.md
/home/opc/knowledge-agent/ergebnisse/test-quellen.md
/home/opc/knowledge-agent/ergebnisse/test-rekursion.md
/home/opc/knowledge-agent/ergebnisse/tier3-befuellung.md
/home/opc/knowledge-agent/ergebnisse/tier3-konsolidierung.md
/home/opc/knowledge-agent/ergebnisse/trust-governance.md
/home/opc/knowledge-agent/ergebnisse/veraltet/001-veraltet-widerspruch-1zu1.md
/home/opc/knowledge-agent/ergebnisse/veraltet/002-veraltet-widerspruch-vereinfachung.md
/home/opc/knowledge-agent/ergebnisse/veraltet/003-veraltet-widerspruch-simplikation.md
/home/opc/knowledge-agent/ergebnisse/versionierung.md
/home/opc/knowledge-agent/ergebnisse/wertbewusste-eviction.md
/home/opc/knowledge-agent/ergebnisse/widerspruch-korrektur.md
/home/opc/knowledge-agent/ergebnisse/zwei-personen.md
/home/opc/knowledge-agent/knowledge/action/README.md
/home/opc/knowledge-agent/knowledge/cognition/README.md
/home/opc/knowledge-agent/knowledge/cognition/inference-001.md
/home/opc/knowledge-agent/knowledge/cognition/inference-002.md
/home/opc/knowledge-agent/knowledge/cognition/inference-003.md
/home/opc/knowledge-agent/knowledge/expansion/README.md
/home/opc/knowledge-agent/knowledge/lifecycle/denken.md
/home/opc/knowledge-agent/knowledge/lifecycle/experience.md
/home/opc/knowledge-agent/knowledge/lifecycle/gedaechtnis.md
/home/opc/knowledge-agent/knowledge/lifecycle/handeln.md
/home/opc/knowledge-agent/knowledge/lifecycle/kognition.md
/home/opc/knowledge-agent/knowledge/lifecycle/nicht-kognition.md
/home/opc/knowledge-agent/knowledge/lifecycle/rekursion/akt.md
/home/opc/knowledge-agent/knowledge/lifecycle/rekursion/compare.md
/home/opc/knowledge-agent/knowledge/lifecycle/rekursion/index.md
/home/opc/knowledge-agent/knowledge/lifecycle/rekursion/konstrukt.md
/home/opc/knowledge-agent/knowledge/lifecycle/rekursion/observe.md
/home/opc/knowledge-agent/knowledge/lifecycle/rekursion/revise.md
/home/opc/knowledge-agent/knowledge/lifecycle/rekursion/wissenszyklus-8-stufen.md
/home/opc/knowledge-agent/knowledge/lifecycle/wissen-plus.md
/home/opc/knowledge-agent/knowledge/lifecycle/wissen.md
/home/opc/knowledge-agent/knowledge/non-cognitive/README.md
/home/opc/knowledge-agent/knowledge/raw/README.md
/home/opc/knowledge-agent/knowledge/reflection/README.md
/home/opc/knowledge-agent/knowledge/structured/README.md
/home/opc/knowledge-agent/knowledge/structured/distilled-hub-n2.md
/home/opc/knowledge-agent/knowledge/structured/entity-fast-write-routing.md
/home/opc/knowledge-agent/knowledge/structured/entity-solver-berechne-durchschnitt.md
/home/opc/knowledge-agent/knowledge/structured/entity-solver-berechne-median.md
/home/opc/knowledge-agent/knowledge/structured/entity-solver-finde-minimum.md
/home/opc/knowledge-agent/knowledge/structured/relation-agent-uses-fwr.md
/home/opc/knowledge-agent/knowledge/structured/relations-rekursion-solver.md
/home/opc/knowledge-agent/skills/AUDIT.md
/home/opc/knowledge-agent/skills/README.md
/home/opc/knowledge-agent/skills/act/SKILL.md
/home/opc/knowledge-agent/skills/act/versions/v1/SKILL.md
/home/opc/knowledge-agent/skills/cognize/SKILL.md
/home/opc/knowledge-agent/skills/cognize/versions/v1/SKILL.md
/home/opc/knowledge-agent/skills/cognize/versions/v2/SKILL.md
/home/opc/knowledge-agent/skills/collect-experience/SKILL.md
/home/opc/knowledge-agent/skills/collect-experience/versions/v1/SKILL.md
/home/opc/knowledge-agent/skills/expand-knowledge/SKILL.md
/home/opc/knowledge-agent/skills/expand-knowledge/versions/v1/SKILL.md
/home/opc/knowledge-agent/skills/non-cognitive/SKILL.md
/home/opc/knowledge-agent/skills/non-cognitive/versions/v1/SKILL.md
/home/opc/knowledge-agent/skills/recursive-improve/SKILL.md
/home/opc/knowledge-agent/skills/recursive-improve/akt/SKILL.md
/home/opc/knowledge-agent/skills/recursive-improve/akt/versions/v1/SKILL.md
/home/opc/knowledge-agent/skills/recursive-improve/compare/SKILL.md
/home/opc/knowledge-agent/skills/recursive-improve/compare/versions/v1/SKILL.md
/home/opc/knowledge-agent/skills/recursive-improve/konstrukt/SKILL.md
/home/opc/knowledge-agent/skills/recursive-improve/konstrukt/versions/v1/SKILL.md
/home/opc/knowledge-agent/skills/recursive-improve/observe/SKILL.md
/home/opc/knowledge-agent/skills/recursive-improve/observe/versions/v1/SKILL.md
/home/opc/knowledge-agent/skills/recursive-improve/revise/SKILL.md
/home/opc/knowledge-agent/skills/recursive-improve/revise/versions/v1/SKILL.md
/home/opc/knowledge-agent/skills/recursive-improve/versions/v1/SKILL.md
/home/opc/knowledge-agent/skills/reflect/SKILL.md
/home/opc/knowledge-agent/skills/reflect/versions/v1/SKILL.md
/home/opc/knowledge-agent/skills/store-memory/SKILL.md
/home/opc/knowledge-agent/skills/store-memory/versions/v1/SKILL.md
/home/opc/knowledge-agent/skills/structure-knowledge/SKILL.md
/home/opc/knowledge-agent/skills/structure-knowledge/versions/v1/SKILL.md
```

---

## Aufgabe 2 – MCP-Server-Test

Vollständige Ergebnisliste in `ergebnisse/systemtest-mcp.md`. Kurzfassung: **18** Einträge in `opencode.json` → 1 deaktiviert (`context7`), 17 aktiv, davon **15 mit Handshake + Tool-Call OK**, 2 ohne lauffähiges Binary (`sqlalchemy-mcp`, `visuals-mcp`). **122 Tools** insgesamt gelistet, pro lauffähigem Server mindestens einer **wirklich aufgerufen** (echte Ausgabe dort dokumentiert).

---

## Aufgabe 3 – 8-Stufen-Test

Ergebnis: **22/22 = 100.0 %**, Auto-Gate **allow**, Fehlschläge **0**. Alle Einzelergebnisse mit Roherausgabe in `ergebnisse/systemtest-8-stufen.md`.

| Stufe | Checks |
|---|---|
| 1 Erfahrung | 4/4 |
| 2 Wissen | 2/2 |
| 3 Gedaechtnis | 3/3 |
| 4 Kognition | 1/1 |
| 5 Denken | 3/3 |
| 6 Nicht-Kognition | 3/3 |
| 7 Handeln | 2/2 |
| 8 Wissen+ | 2/2 |
| 9 MCP-Layer | 1/1 |
| 10 FWR | 1/1 |

---

## Aufgabe 4 – LLM-Endpoint (NVIDIA)

Key: `mcp/reflexion.env.OPENAI_API_KEY` (`nvapi-…`, dasselbe Konto wie in `ergebnisse/fwr-test.md`) · Base: `https://integrate.api.nvidia.com/v1`

| Prüfung | Ergebnis |
|---|---|
| `GET https://integrate.api.nvidia.com/v1/models` | **HTTP 200**, **81 Modelle** |
| `POST …/chat/completions`, 8-fach parallel, max_tokens=8 | **17× 200** · **55× 404** · **0× 410** · **9× sonstige** |

### Zielmodelle (sequenziell, max_tokens=256, echte Frage)

| Modell | HTTP | s | Antwort (Auszug) |
|---|---|---:|---|
| `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning` | 200 | 9.9 | Der Drift‑Bound liegt bei 5 %. |
| `nvidia/nemotron-3-super-120b-a12b` | 200 | 1.5 | Okay, the user is asking for the drift bound in percent in one sentence. Let me recall what drift bound means. Drift bound usually refers to the maximum allowable deviation or erro |
| `nvidia/llama-3.3-nemotron-super-49b-v1.5` | 410 | 0.1 | {"type":"about:blank","title":"Gone","status":410,"detail":"The model 'nvidia/llama-3.3-nemotron-super-49b-v1.5' has reached its end of life on 2026-08-26T09:00:00Z and is no longe |
| `nvidia/llama-3.1-nemotron-super-49b-v1.5` | 404 | 0.1 | 404 page not found  |
| `google/gemma-2b` | 404 | 0.2 | {"status":404,"title":"Not Found","detail":"Function '04174188-f742-4069-9e72-d77c2b77d3cb': Not found for account 'iPy5XqUxQvhUA_xxxk5WWgTNxVt1ud_Ktkxi7VsMiIQ'"} |
| `nvidia/llama-3.1-8b-instruct` | 404 | 0.1 | 404 page not found  |
| `nvidia/kimi-k2.6` | 404 | 0.1 | 404 page not found  |
| `deepseek-ai/deepseek-v4.1-flash` | 200 | 49.1 | We need answer in German. User asks: "Nenne in einem Satz: Was ist der Drift-Bound in Prozent?" Need know context. "Drift-Bound" maybe in eye tracking? Drift bound? In Prozent. Nee |

**Bewertung:**

- `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning` (FWR-Stufe 1): **200, 9,9 s** sequenziell. Unter 8-fach gleichzeitigem Load kam **503 `ResourceExhausted: Worker local total request limit reached (16/16)`** bzw. ein 60-s-Timeout – der Endpunkt ist also **nicht parallel-belastbar**, das Router-Design (eine Anfrage pro Entscheidung) läuft trotzdem.
- `nvidia/nemotron-3-super-120b-a12b` (FWR-Stufe 2): **200, 1,5 s**.
- **Tote Modelle (404, ausdrücklich geprüft):** `google/gemma-2b` (`Not found for account` – der alte FWR-Default, Grund von Rekursion 031), `nvidia/llama-3.1-8b-instruct`, `nvidia/kimi-k2.6`, `nvidia/llama-3.1-nemotron-super-49b-v1.5`. Insgesamt **{len(n404)} von {sweep['n_models']}** IDs liefern 404 (Liste unten).
- **EOL (410 Gone):** `nvidia/llama-3.3-nemotron-super-49b-v1.5` – „has reached end of life“, zweimal hintereinander gemessen. Diese ID ist **nicht** in der 81er-`/models`-Liste (dort stattdessen die 3.1er-Variante mit 404).
- **Langsam/instabil:** `deepseek-ai/deepseek-v4.1-flash` 49,1 s; Timeouts bei `google/gemma-4-31b-it`, `meta/llama-guard-4-12b`, `moonshotai/kimi-k3`, `z-ai/glm-5.3`, `nvidia/llama-3.1-nemoguard-8b-content-safety`; 500/503 bei `nvidia/ai-synthetic-video-detector`, `nvidia/llama-3.1-nemoguard-8b-topic-control`.

### Alle 55 Modelle mit HTTP 404 (parallel gemessen)

```
01-ai/yi-large                                            adept/fuyu-8b                                             ai21labs/jamba-1.5-large-instruct
aisingapore/sea-lion-7b-instruct                          bigcode/starcoder2-15b                                    databricks/dbrx-instruct
deepseek-ai/deepseek-coder-6.7b-instruct                  google/codegemma-1.1-7b                                   google/codegemma-7b
google/deplot                                             google/gemma-2b                                           google/gemma-3-12b-it
google/gemma-3-4b-it                                      google/recurrentgemma-2b                                  ibm/granite-3.0-3b-a800m-instruct
ibm/granite-3.0-8b-instruct                               ibm/granite-34b-code-instruct                             ibm/granite-8b-code-instruct
meta/codellama-70b                                        meta/llama2-70b                                           microsoft/kosmos-2
microsoft/phi-3-vision-128k-instruct                      microsoft/phi-3.5-moe-instruct                            mistralai/codestral-22b-instruct-v0.1
mistralai/mistral-7b-instruct-v0.3                        mistralai/mistral-large                                   mistralai/mistral-large-2-instruct
mistralai/mixtral-8x22b-v0.1                              moonshotai/kimi-k2.6                                      nv-mistralai/mistral-nemo-12b-instruct
nvidia/cosmos-reason2-8b                                  nvidia/embed-qa-4                                         nvidia/llama-3.1-nemotron-51b-instruct
nvidia/llama-3.1-nemotron-70b-instruct                    nvidia/llama-3.1-nemotron-ultra-253b-v1                   nvidia/llama-3.2-nemoretriever-1b-vlm-embed-v1
nvidia/llama-3.2-nv-embedqa-1b-v1                         nvidia/llama-nemotron-embed-vl-1b-v2                      nvidia/llama3-chatqa-1.5-70b
nvidia/mistral-nemo-minitron-8b-8k-instruct               nvidia/nemotron-3-embed-1b                                nvidia/nemotron-4-340b-instruct
nvidia/nemotron-4-340b-reward                             nvidia/nemotron-nano-3-30b-a3b                            nvidia/neva-22b
nvidia/nv-embedqa-mistral-7b-v2                           nvidia/nvclip                                             nvidia/riva-translate-4b-instruct
nvidia/vila                                               snowflake/arctic-embed-l                                  writer/palmyra-creative-122b
writer/palmyra-fin-70b-32k                                writer/palmyra-med-70b                                    writer/palmyra-med-70b-32k
zyphra/zamba2-7b-instruct
```

### Alle 17 Modelle mit HTTP 200

| Modell | s | Antwort (max_tokens=8) |
|---|---:|---|
| `nvidia/nemotron-parse-2.0` | 0.1 | is wasiirunz_tim |
| `nvidia/riva-translate-4b-instruct-v1.1` | 0.1 | أجب |
| `poolside/laguna-xs-2.1` | 0.2 | 4 |
| `google/diffusiongemma-26b-a4b-it` | 0.3 | 4 |
| `meta/llama-3.2-11b-vision-instruct` | 0.3 | Ich habe keine Frage erhalten, aber ich |
| `nvidia/nemotron-3.5-content-safety` | 0.3 | User Safety: safe |
| `nvidia/riva-translate-4b-instruct-v2` | 0.4 | Answer with: 4 |
| `nvidia/ising-calibration-1.5-31b` | 0.5 | Ich bin NVIDIA Ising-Calibration-1 |
| `nvidia/nemotron-3-super-120b-a12b` | 0.5 |  |
| `openai/gpt-oss-20b` | 0.5 |  |
| `meta/muse-glimmer-30b` | 0.6 |  |
| `nvidia/nemotron-3-ultra-550b-a55b` | 0.6 | The user wants me to answer with the |
| `meta/llama-3.2-90b-vision-instruct` | 0.9 | 4 |
| `nvidia/llama-3.1-nemotron-safety-guard-8b-v3` | 1.7 | {"User Safety": "safe"}  |
| `nvidia/nemotron-3.5-lightning-30b-a3b` | 9.5 | Here's a thinking process:  1. |
| `z-ai/glm-5.3-flash` | 9.5 |  |
| `deepseek-ai/deepseek-v4.1-flash` | 16.2 |  |

### 9 sonstige Antworten (Timeout/4xx/5xx)

| Modell | Code | Text |
|---|---|---|
| `google/gemma-4-31b-it` | ERR | ReadTimeout: The read operation timed out |
| `meta/llama-guard-4-12b` | ERR | ReadTimeout: The read operation timed out |
| `moonshotai/kimi-k3` | ERR | ReadTimeout: The read operation timed out |
| `nvidia/ai-synthetic-video-detector` | 500 | {"type":"urn:nvcf-worker-service:problem-details:internal-server-error","title":"Internal Server Error","statu |
| `nvidia/llama-3.1-nemoguard-8b-content-safety` | ERR | ReadTimeout: The read operation timed out |
| `nvidia/llama-3.1-nemoguard-8b-topic-control` | 500 | {"error":"Error during inference of request chat-4540f35eef1a44528ceb0225523719a9 -- Encountered an error in f |
| `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning` | 503 | {"error":{"message":"ResourceExhausted: Worker local total request limit reached (16/16)","type":"Service Unav |
| `nvidia/nemotron-parse` | 400 | {"object":"error","message":"Content cannot be a plain string. The model does not support text input. Content  |
| `z-ai/glm-5.3` | ERR | ReadTimeout: The read operation timed out |

---

## Aufgabe 5 – Gesamturteil

| Prüfung | Ergebnis | Urteil |
|---|---|---|
| Struktur (Aufgabe 1) | alle Komponenten gezählt, 237 MD-Dateien gelistet | erfüllt |
| MCP-Server (Aufgabe 2) | 15/17 aktiv lauffähig, 122 Tools gelistet, ≥1 Call je lauffähigem Server | teilweise – 2 Binaries fehlen |
| 8 Stufen (Aufgabe 3) | 22/22 = 100.0 % | erfüllt |
| Endpoint (Aufgabe 4) | `GET /models` → 200 (81 IDs), davon 17 real beantwortet; 8 Zielmodelle sequenziell: 3× 200, 1× 410 (EOL), 4× 404 | erfüllt (Befunde unter Offene Punkte) |
| Auto-Gate §9 | Score → **allow** | **allow** |

**Score:** 22/22 = 100.0 % → Auto-Gate **allow** (§9: ≥ 95 % allow).

### Fehlschläge / Blocked

- **Keine** – alle 22 Checks der 8-Stufen-Prüfung OK.
- MCP ohne lauffähiges Binary: `sqlalchemy-mcp` (FEHLT: sqlalchemy-mcp-server), `visuals-mcp` (FEHLT: visuals-mcp)
- MCP deaktiviert: `context7` (`enabled: false`).

### Offene Punkte (nicht behoben, ehrlich benannt)

1. **Tote Binaries:** `sqlalchemy-mcp-server` und `visuals-mcp` fehlen im PATH – zwei Einträge in `opencode.json` sind ohne Wirkung.
2. **Tote Modelle:** 55 von 81 IDs liefern 404, 1 Modell ist EOL (410). Die FWR-Defaults sind beide auf der 200er-Liste – das war Rekursion 031.
3. **Parallel-Limit des Endpoints:** bei 8 gleichzeitigen Anfragen 503/Timeout (Worker-Limit 16/16); sequenziell stabil.
4. **`write-update`-Klasse des FWR: geübt – siehe Beweis.** Fall C „Größte Wüste der Welt?“ (`correct="Sahara"`) liefert `write-update`; Rohtexte in `ergebnisse/fast-write-router.md:70-78`, Nachlauf 2026-10-01 mit den aktuellen Defaults in `ergebnisse/doku-korrektur-fwr.md`. In `fwr-test.md` §4 stand derselbe Fragenwortlaut mit `correct="Antarctic Desert"` und wurde deshalb zu `non-write` – die Aussage „ungeübt“ war falsch.
5. ~~**Doku/Code-Abweichung** `fast_write_router.py` (Doku „zero-shot falsch“, Code prüft `is_refusal`).~~
   **Erledigt 2026-10-01 nach Gate-Freigabe:** Code erfüllt `AGENTS.md:306-307`
   wörtlich (inkl. `uncertain`-Fall), Tests in `tests/test_fwr.py` –
   `ergebnisse/fwr-code-korrektur.md`.
6. ~~**Kein CI/pytest/lint** im Repo – Verifikation bleibt „Skript ausführen“.~~
   **Erledigt 2026-10-01:** `tests/` (17 Dateien, **221 Tests** / 220+1 skip auf 3.9), `pytest.ini`
   (**Mindest-Score 100 %**, gesamter Repo-Code: 1900 Statements / 442 Branches),
   `make test` – siehe `ergebnisse/ci-setup.md`.
   Lint/Formatting fehlt weiterhin.

### Reinheit des Repos

```bash
# vor dem Schreiben dieser drei Dateien:
$ git status --short
(leer)
```

Der Test selbst hat **nichts am Repo verändert**: alle Skripte liegen in `/tmp/opencode/`. Erzeugt wurden ausschließlich diese drei gewünschten Doku-Dateien (neu, unverändert sonst nichts).

---

## Quellen (am 2026-10-01 geprüft)

- Serverliste/Keys: `~/.config/opencode/opencode.json` (lokale Datei)
- `GET https://integrate.api.nvidia.com/v1/models` — **HTTP 200**
- `POST https://integrate.api.nvidia.com/v1/chat/completions` — 200/404/410/503 je Modell, Messwerte oben
- MCP-Spezifikation: https://modelcontextprotocol.io/docs/2026-07-28/getting-started/intro — **HTTP 200** (mit Redirect)
- FWR-Grundlage: https://arxiv.org/abs/2608.22215 — **HTTP 200**
- Fallback-Regel/Score-Regel: `AGENTS.md` §9, §11 (lokale Datei)

