# Gedächtnis-Verifikation (L0–L4)

> Datum: 2026-10-04 · Status: **Belegt** (Quelle) + **Auftrag** (Repo-Zuordnung).
> Ziel `g`: prüfen, welche Gedächtnis-Schichten **L0–L4** im Repo real existieren — mit
> `Datei:Zeile`. Lab-Prinzip §6: keine Erfindung; fehlende Schichten werden **klar** benannt.

## 1. Quelle (verifiziert)

- **Memory Architectures for AI Agents in 2026: A Survey, a Synthesis, and an Evaluation
  Framework** (Dmitrii Dmitrenko, 2026-06-10) — **„unified five-layer architecture"**;
  Companion-Dataset **doi 10.5281/zenodo.20562988** (Exa-Preprint; IEEE-IS-Einreichung).
  → **Korrektur (ehrlich):** Der Auftrag nennt „Memory Survey 2026 (Zenodo)"; die
  verifizierte Primärquelle ist der **Dmitrenko-Survey** (Five-Layer + Zenodo-Dataset).
- **Atkinson-Shiffrin (1968)** — Sensory → Short-Term (Working) → Long-Term; LTM zerfällt in
  **declarative (episodic + semantic)** und **procedural** (zitiert in arXiv:2601.09113).
- **L4:** Mem^p (arXiv:2508.06433), TEA (arXiv:2506.12508), Graph-based Agent Memory (arXiv:2602.05665).

## 2. Verifikations-Tabelle (Datei:Zeile)

| # | Schicht | Status | Beleg (`Datei:Zeile`) |
|---|---|---|---|
| **L0** | **Sensory** | **NICHT vorhanden** (Lücke) | — kein Memory-Layer; nur **Ingestion-Pfad** `data/memory/ingestion_hook.py:118` (`Encoding-Gate`), `:49` (`ingestion_log.jsonl`) |
| **L1** | **Working** | **vorhanden** | `data/memory/tier3-working/lru_cache.py:3` („Tier 3 – Working Memory: LRU-bounded Cache"), `:101` (`class WorkingMemory`) |
| **L2** | **Episodic** | **vorhanden** | `data/memory/reflective_agent.py:24` (`GRAPH_FILE` → `tier1-base/episodic_graph.json`), Datei `data/memory/tier1-base/episodic_graph.json` |
| **L3** | **Semantic** | **vorhanden** | `data/memory/tier2-index/concept-index.md` + `knowledge/structured/` (distilled/entity/relation) + `data/memory/mcp_memory_server.py:41` (`SCOPES["structured"]`) |
| **L4** | **Procedural** | **vorhanden** | `skills/procedural_memory.py:3` („Procedural Memory (L4)"), `skills/README.md:1`, 14× `skills/*/SKILL.md` |

## 3. Mapping Repo-Benennung ↔ L0–L4 (Auftrag)

Das Repo nutzt „**3 Tiers + L4 + Shared**" (`knowledge/lifecycle/gedaechtnis.md:68-80`).
Die Zuordnung zur L0–L4-Taxonomie:

| L0–L4 | Repo-Benennung | Ordner/Datei |
|---|---|---|
| L0 Sensory | — (fehlt) | — |
| L1 Working | **Tier 3** – Working Memory | `data/memory/tier3-working/` |
| L2 Episodic | Episodic Graph (in **Tier 1**) | `data/memory/tier1-base/episodic_graph.json` |
| L3 Semantic | **Tier 1** Ontologie + **Tier 2** Concept-Index + `knowledge/structured/` | `data/memory/tier1-base/ontology.md`, `data/memory/tier2-index/concept-index.md` |
| L4 Procedural | **L4** Procedural Memory | `skills/` |

- **Shared Tier** (`data/memory/shared/`, ACL+Sync) ist **zusätzlich** (kein L0–L4-Slot).

## 4. Fazit (ehrlich)

- **L1–L4 sind real implementiert** (Working, Episodic, Semantic, Procedural) — mit Code + Dateien.
- **L0 (Sensory) fehlt** als Memory-Schicht. Der **Ingestion-Pfad** (`ingestion_hook.py`) ist ein
  **Verarbeitungsschritt**, kein sensorischer Puffer → **Lücke**, nicht als vorhanden ausgegeben.
- **Quelle:** fünf-schichtige Architektur = Dmitrenko-Survey 2026 (Zenodo-Dataset 20562988);
  die konkreten Schicht-Namen stützen sich zusätzlich auf Atkinson-Shiffrin (1968).

## 5. Gate (§9)

- Reine **Verifikation + Doku** (keine Code-/Interface-Änderung) → kein Human-Gate nötig.
- Guardrail 3: Provenienz `ergebnisse/rekursion/053-memory-verifikation.md`.
- Guardrail 6: kein Commit ohne Erlaubnis. §9.1b: `AGENTS.md` unverändert.
