# Skill-Prozess-Lücken (Atomic MCP-Interface)

> Datum: 2026-10-03 · Status: **Auftrag** (Zuordnung) + **Belegt** (Atomic MCP-Interface).
> Ziel: jeder Skill nennt die Prozesse, die er aufruft (MCP-Tools als Schnittstelle).

## 1. Quelle (verifiziert)

- **Atomic (MCP-Interface):** „Atomic exposes five MCP tools" —
  https://atomicapp.ai/guides/mcp-server/ · https://github.com/kenforthewin/atomic
  (im Repo: `ergebnisse/mcp-memory.md:10`).
- Zuordnung (Auftrag): `skills/README.md` (Skill→Prozess).

## 2. Änderung

In alle **14 aktiven `SKILL.md`** wurde ein Abschnitt `## Prozesse (Aufrufe) [Auftrag]`
eingefügt (Prozess in `data/memory/` + MCP-Tools). Versionierung über
`skills/procedural_memory.propose_update(..., approved=True)` → `versions/vN/`.

| Skill | Prozess (`data/memory/`) | MCP-Tools | Version |
|---|---|---|---|
| collect-experience | `ingestion_hook.py` | memory.write | v2 |
| structure-knowledge | `fast_write_router.py` | memory.write | v2 |
| store-memory | `lru_cache.py` + `pipeline.py` | memory.search, memory.write | v2 |
| cognize | `reflective_agent.py` | memory.read, memory.search | v3 |
| reflect | `bias_monitor.py` | memory.read | v2 |
| non-cognitive | `trust.py` | memory.write | v2 |
| act | `pipeline.py` | memory.write | v2 |
| expand-knowledge | `shared_memory.py` + `pipeline.py` | memory.read, memory.write | v2 |
| recursive-improve | `pipeline.py` + `reflective_agent.py` | memory.search, memory.read | v2 |
| recursive-improve/konstrukt | `reflective_agent.py` | memory.read | v2 |
| recursive-improve/akt | `pipeline.py` | memory.write | v2 |
| recursive-improve/observe | `ingestion_hook.py` | memory.write | v2 |
| recursive-improve/compare | `evaluator_version.py` | memory.read | v2 |
| recursive-improve/revise | `reflective_agent.py` + `bias_monitor.py` | memory.write | v2 |

## 3. Test

`tests/test_skills.py` (offline):
- genau **14** aktive `SKILL.md`;
- jeder enthält `## Prozesse` und ein `memory.<tool>`;
- jedes genannte `*.py` existiert in `data/memory/` (bzw. `tier3-working/`, `shared/`).

## 4. Gate (§9)

- Skill-/Interface-Änderung → **approved** (Batnini, 2026-10-03).
- Versionierung je Skill (`versions/vN/`) + `AUDIT.md` (procedural_memory).
- Ehrlich: Die Prozess-Zuordnung ist **Auftrag** (aus `skills/README.md`), kein Paper-Claim.
