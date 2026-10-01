# skills/ – Procedural Memory (L4)

> Lab-Prinzip, MD-first. Procedural Memory ist ein **First-Class-Architekturelement
> (L4)** neben den 3 Gedächtnis-Tiers (`data/memory/`).
> Gesetz: `AGENTS.md` (§6 keine Erfindungen, §9 Human-Gate).

## 1. Was ist L4? (Belegt)

Skills sind die **Prozeduren** des Agenten (Workflows, Decision Rules). Sie
werden als eigenständiges, versioniertes Artefakt behandelt — nicht als
Prompt-Text.

- **Mem^p** (arXiv:2508.06433, ACL Findings 2026): „treats procedural memory as a
  **first-class optimization object**"; Build/Retrieval/**Update**; dynamische
  Update-Strategien (addition, validation filtering, reflection, **dynamic
  discarding/deprecate**).
- **AFTER** (arXiv:2606.23127): persistente Skill-Files als „**first-class
  artifact** outside the base prompt".
- **ProcMEM** (arXiv:2602.01869): **PPO-style trust-region verification (PPO Gate)**
  vor Aufnahme eines Skills.
- **Graph-based Agent Memory** (arXiv:2602.05665): „Procedural Memory: Encodes
  skills, routines, and immutable rules."

## 2. Struktur

```text
skills/
├── README.md                 # dieses Dokument
├── AUDIT.md                  # Audit-Log: jede Skill-Änderung (Aktion + Begründung)
├── audit-diffs/              # Unified Diffs je Änderung
├── procedural_memory.py      # Mechanismus (Versionierung/Audit/Update)
├── <name>/SKILL.md           # aktiver Skill
├── <name>/versions/vN/SKILL.md   # versionierte Snapshots
└── recursive-improve/
    ├── SKILL.md
    ├── <phase>/SKILL.md
    └── <phase>/versions/vN/SKILL.md
```

**Aktiv** = `SKILL.md` **ohne** `versions/` im Pfad. Aktuell **14 aktive Skills**
(8 Stufen-Skills + `recursive-improve/` 6). `versions/` ist reserviert.

## 3. Die drei Regeln

| Regel | Mechanik | Status |
|---|---|---|
| **Versionierung** | `skills/<name>/versions/vN/SKILL.md` (Snapshot vor jeder Änderung) | Auftrag |
| **Audit** | `skills/AUDIT.md` (Zeit, Skill, Aktion, Begründung) + `audit-diffs/*.diff` | Auftrag |
| **Selektives Update** | Nur Skills mit `approved` werden geschrieben (Human-Gate) | **Belegt** (Mem^p Update; ProcMEM Gate) |

**Mechanismus:** `skills/procedural_memory.py`
- `snapshot(skill, version, reason)` — versionierte Kopie
- `propose_update(skill, new_text, reason, approved)` — schreibt **nur** bei `approved`
- `audit(...)` — Audit-Zeile + Diff-Datei

## 4. Workflow einer Skill-Änderung

1. Vorschlag erzeugen: `propose_update(..., approved=False)` → **pending** (kein Write).
2. Menschliches Gate: `approved` (vgl. `AGENTS.md` §9).
3. Bei `approved`: Vorher-Stand wird als `vN` gesnapshottet, dann geschrieben; Audit + Diff.

## 5. Status-Trennung

| Aussage | Status |
|---|---|
| Procedural Memory als First-Class | **Belegt** (Mem^p/AFTER) |
| Update-Strategien (addition/discard/validation) | **Belegt** (Mem^p) |
| Verification-Gate vor Skill-Aufnahme | **Belegt** (ProcMEM) |
| Konkrete Versionierung/Audit-Mechanik | **Auftrag** |

## 6. Quellen (alle HTTP 200, 2026-10-01)

- https://arxiv.org/abs/2508.06433 (Mem^p)
- https://aclanthology.org/2026.findings-acl.866.pdf (Mem^p, ACL Findings 2026)
- https://arxiv.org/abs/2606.23127 (AFTER)
- https://arxiv.org/abs/2602.01869 (ProcMEM)
- https://arxiv.org/abs/2510.04851 (LEGOMem)
- https://arxiv.org/abs/2512.13564 (Memory in the Age of AI Agents)
- https://arxiv.org/abs/2602.06052 (Survey: Self-Evolving Agents)
- https://arxiv.org/abs/2602.05665 (Graph-based Agent Memory)
