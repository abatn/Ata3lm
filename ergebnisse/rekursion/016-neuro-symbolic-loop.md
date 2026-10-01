# 016 – LLM → Symbolic → Commit als fester Loop

> Datum: 2026-10-01
> Rekursionstiefe: System-Iteration (cognize-Skill), nicht Solver-t
> Phase: Revise (Skill erweitert) — via L4-Mechanik versioniert
> Auslöser: menschlicher Auftrag vom 2026-10-01.

## 1. Zustand vorher / nachher

| | vorher (cognize v1) | nachher (cognize v2) |
|---|---|---|
| Loop | Inferenz vor Validierung dokumentiert | **Fester Loop LLM→Symbolic→Commit** inkl. FAIL→LLM |
| Commit-Regel | implizit | Guardrail 8: kein Commit ohne PASS |

## 2. Änderungen

- `skills/cognize/SKILL.md`: neuer Abschnitt „Fester Loop: LLM → Symbolic → Commit";
  Ablauf/Guardrails/Quellen angepasst.
- Angewandt über `skills/procedural_memory.py` (`propose_update`, approved) →
  Snapshot `skills/cognize/versions/v2/` + Audit-Eintrag.
- `ergebnisse/neuro-symbolic-loop.md` neu.

## 3. Compare-Beleg (externes Signal)

- `propose_update` → `{'applied': True, 'version': 'v2'}` (reale Ausgabe).
- `skills/AUDIT.md` enthält die Update-Zeile; `cognize` YAML = OK.
- Quellen HTTP 200 (AWS Semantic Layer, Swansea Semantic Web Journal).

## 4. Quellen (belegt)

- AWS Semantic Layer: neuro-symbolisch (deterministisch + LLM), „validate actions",
  SHACL-Validatoren, auditable reasoning chains.
  https://docs.aws.amazon.com/prescriptive-guidance/latest/semantic-layer-agentic-ai-ontology-reasoning-virtual-knowledge-graph/semantic-layer-agentic-ai-ontology-reasoning-virtual-knowledge-graph.html
- Swansea (Robaldo & Batsakis): Inferenz vor Validierung (SHACL-SPARQL).
  https://www.semantic-web-journal.net/system/files/swj3959.pdf

## 5. Abgrenzung (Auftrag vs. Belegt)

- **Belegt:** neuro-symbolische Kombination, „validate actions", Inferenz vor Validierung.
- **Auftrag:** die explizite Rückkante **FAIL → LLM** (Loop-Fixierung) und die
  konkrete Ablage.

## 6. Guardrails

- `AGENTS.md` unverändert.
- Skill-Änderung nur über die L4-Mechanik (Version + Audit).

## 7. Freigabe

**Freigabe-Status für π₁:** `approved: Batnini, 2026-10-01`.
