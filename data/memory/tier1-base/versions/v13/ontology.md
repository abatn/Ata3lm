# Tier 1 – Base Knowledge: Ontologie

> Schicht: Tier 1 (Base Knowledge) der 3-Schicht-Gedächtnis-Pipeline.
> Quelle (semantische Hierarchie): SHIMI (arXiv:2504.06135).
> Quelle (Ontologie + bi-temporal): ARIADNE Tier 2 (arXiv:2105.09864), Graphiti (arXiv:2501.13956).
> Lab-Prinzip: keine Erfindungen – nur Auftrag + Quellen.

## A. Die 8 Stufen (semantische Knoten)

| # | Stufe | Schreib-/Leserichtung |
|---|---|---|
| 1 | Erfahrung | schreibt in Working Memory |
| 2 | Wissen | liest aus Working Memory |
| 3 | Gedächtnis | schreibt in Ontologie |
| 4 | Kognition | liest Ontologie, schreibt M |
| 5 | Denken | schreibt Self-Feedback |
| 6 | Nicht-Kognition | schreibt in Working Memory |
| 7 | Handeln | schreibt Aktion in Working Memory |
| 8 | Wissen+ | schreibt revidiertes Modell zurück |

Quelle: `knowledge/lifecycle/rekursion/wissenszyklus-8-stufen.md`.

## B. Die 5 Phasen (rekursive Kanten)

| Phase | Funktion |
|---|---|
| Konstrukt | baut Modell π aus Ziel g |
| Akt | führt π aus |
| Observe | sammelt Zustand s + Feedback r |
| Compare | vergleicht r mit externem Signal |
| Revise | schreibt (π, I) zurück |

Quelle: `knowledge/lifecycle/rekursion/index.md`.

## C. Ontologie-Grounding (Auftrag + Quelle)

Jeder Knoten trägt (nach ARIADNE Tier 2 / Graphiti):
- **Ontologie-Bezug** (Konzept/URI),
- **Gültigkeitsfenster** (`gueltig_von` / `gueltig_bis`) – bi-temporal,
- **Provenienz** (Episode + Quelle).

Quellen:
- ARIADNE 3-Tier (Tier 2 Semantic, bi-temporale Felder): https://arxiv.org/abs/2105.09864
- Graphiti (Fakten mit Validitätsfenstern): https://arxiv.org/abs/2501.13956
- SHIMI (semantische Hierarchie): https://arxiv.org/abs/2504.06135
- ZsRE (`community-datasets/qa_zre`; §10.3-Konsolidierungskorpus, `approved` Batnini 2026-10-07): https://huggingface.co/datasets/community-datasets/qa_zre · Levy et al. 2017 https://aclanthology.org/K17-1034
- FadeMem (adaptiver Exponential-Decay, Tier-3-Eviction; §9 approved Batnini+Taoufik 2026-10-08): IEEE DOI 10.1109/icassp55912.2026.11462095 · https://arxiv.org/abs/2601.18642
- Out-of-Band-Evaluation / World-State-Oracle (Compare-Ground-Truth §6; §9 approved Batnini+Taoufik 2026-10-08): Zenodo DOI 10.5281/zenodo.21594735 · https://arxiv.org/abs/2607.25152

## D. Memory-Lifecycle (Belegt: HeLa-Mem + Memory Survey)

> Quellen: **HeLa-Mem** (arXiv:2604.16839 §3.3), **Memory Survey** (arXiv:2603.07670).
> Implementierung: `data/memory/reflective_agent.py`. Doku: `ergebnisse/memory-lifecycle.md`.

| Operator | Regel | Status/Quelle |
|---|---|---|
| **Konsolidierung** | Hub `D(v) > δ_hub` → Hub + Nachbarn werden zu **semantischem Eintrag** (Hebbian Distillation) | Belegt (HeLa-Mem) |
| **Forgetting** | **3 Bedingungen gleichzeitig:** `weight < δ_prune` **und** `age > δ_age` **und** `access == 0` | Belegt (HeLa-Mem) |
| **Konfliktlösung** | Bei Widerspruch: alter Fakt wird **superseded** (`invalid_at`), **nicht gelöscht**; neuer gilt (prefer newest) | Belegt (Memory Survey; Graphiti bi-temporal) |

**Parameter (Auftrag):** `δ_hub`, `δ_prune=0.05`, `δ_age=60` Tage; `τ=60`, `η=0.02`, `λ=0.995` (belegt, HeLa-Mem).

**Funktionen:** `detect_hubs`, `distill`/`write_semantic` (Konsolidierung);
`detect_forgetting` (3 Bedingungen); `resolve_conflict` (Supersede-Marker);
`simulate_lifecycle` (Demo).

## E. Bi-temporale Semantik (Belegt: Engram)

> Quelle: **Engram** (arXiv:2606.09900) — valid time + transaction time + `supersedes`;
> „never hard-delete a contradicted fact — invalidate it … and keep the history".
> Implementierung: `data/memory/bi_temporal.py`. Doku: `ergebnisse/bi-temporal.md`.

Jeder Fakt trägt **zwei Zeitachsen**:
- **valid time** (`valid_from` / `valid_to`): wann gilt der Fakt **in der Welt**?
- **transaction time** (`recorded_at` / `superseded_at`): wann wurde er **gespeichert/verworfen**?

**Retroaktives Update:** Bei Widerspruch (gleiches s,p, anderes o) → alter Fakt bleibt
mit `valid_to` + `superseded_at` (nicht gelöscht), neuer mit `valid_from` (+ `supersedes`).

**As-of-Abfragen:** `as_of(valid_time, knowledge_time)` („was glaubten wir am knowledge_time
über valid_time?"); zusätzlich `world_state_as_of` (nur valid) + `knowledge_as_of` (nur transaction).
