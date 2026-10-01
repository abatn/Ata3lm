# Procedural Memory als First-Class-Architekturelement (L4)

> Datum: 2026-10-01
> Status: **Belegt** (Konzept) + **Auftrag** (Mechanik/Implementierung)
> Prinzip: Keine Erfindungen (§6). Jede Aussage mit Quelle oder als Auftrag.
> Code: `skills/procedural_memory.py` · Doku: `skills/README.md`

## 1. Quellen (verifiziert, HTTP 200)

| Quelle | Kernaussage (wörtlich/nah) | Link |
|---|---|---|
| **Mem^p** (ACL Findings 2026) | „treats procedural memory as a **first-class optimization object**"; Build/Retrieval/**Update**; Update-Strategien: „ordinary addition, validation filtering, reflection, and **dynamic discarding**"; „continuously updates, corrects, and **deprecates** its contents" | https://arxiv.org/abs/2508.06433 |
| **AFTER** | persistente Skill-Files als „**first-class artifact** outside the base prompt"; Skill-Refinement + Transfer | https://arxiv.org/abs/2606.23127 |
| **ProcMEM** | Skill-MDP; „**PPO-style Trust-Region Verification (PPO Gate)**" vor Aufnahme; „score-based maintenance" | https://arxiv.org/abs/2602.01869 |
| **LEGOMem** | modulare **procedural memory** (Workflows) für Multi-Agenten | https://arxiv.org/abs/2510.04851 |
| **Graph-based Agent Memory** | „Procedural Memory: Encodes **skills, routines, and immutable rules**." | https://arxiv.org/abs/2602.05665 |
| **Memory in the Age of AI Agents** | Memory als „**first-class primitive**" | https://arxiv.org/abs/2512.13564 |

## 2. L4 im Knowledge-Agent

| Layer | Inhalt | Ort |
|---|---|---|
| L1–L3 | Gedächtnis-Tiers (Base / Index / Working) | `data/memory/` |
| **L4** | **Procedural Memory** = Skills (Workflows, Decision Rules) | `skills/` |

**Belegt** ist „procedural memory as first-class". Die Bezeichnung **L4** ist die
Projekt-Zuordnung (**Auftrag**).

## 3. Die drei Maßnahmen

### 3.1 Versionierung — **Auftrag** (Mechanik), Belegt (Update-Zyklus)
- Jede Skill-Version: `skills/<name>/versions/vN/SKILL.md`.
- Baseline `v1` für alle **14 aktiven Skills** erstellt.
- Quelle (Mechanik-Idee): Mem^p Update/Dynamic-Discarding.

### 3.2 Audit — **Auftrag** (Mechanik), Belegt (Begründungspflicht)
- `skills/AUDIT.md`: Zeit · Skill · Aktion · Begründung.
- `skills/audit-diffs/*.diff`: Unified Diff je Änderung.
- Quelle: Mem^p (Build/Update dokumentiert), AFTER (Skill als Artefakt).

### 3.3 Selektives Update — **Belegt** (Mem^p / ProcMEM)
- `propose_update(..., approved=False)` → **pending**, **kein Write**.
- Nur mit `approved=True` wird geschrieben (Human-Gate, `AGENTS.md` §9).
- Quelle: Mem^p (Update-Strategien); ProcMEM (Verification-Gate vor Aufnahme).

## 4. Selbsttest (reale Ausgabe)

```text
=== [1] Versionierung: v1-Snapshot aller aktiven Skills ===
  skills/act/SKILL.md -> skills/act/versions/v1/SKILL.md
  ... (14 Skills) ...
  Snapshots: 14

=== [2] Audit-Log ===
  skills/AUDIT.md geschrieben.

=== [3] Selektives Update (Human-Gate) ===
  ohne approved -> applied=False status=pending (kein approved (Human-Gate))
  Inhalt unverändert? True
  mit approved  -> applied=True status=approved version=v1
  Inhalt geändert?  True
```

**Ergebnis:** 14 v1-Snapshots + Audit-Log erstellt; ohne `approved` **kein**
Write (pending), mit `approved` angewandt. Alle 14 aktiven `SKILL.md` bleiben
YAML-gültig.

## 5. Status-Trennung

| Aussage | Status |
|---|---|
| Procedural Memory als First-Class | **Belegt** (Mem^p/AFTER) |
| Update = addition/validation/discard/deprecate | **Belegt** (Mem^p) |
| Verification-Gate vor Skill-Aufnahme | **Belegt** (ProcMEM) |
| „L4"-Bezeichnung | **Auftrag** |
| Versionierung `versions/vN/`, Audit-Log, selektives Update | **Auftrag** |

## 6. Dateien

| Artefakt | Art |
|---|---|
| `skills/README.md` | neu (L4-Doku) |
| `skills/procedural_memory.py` | neu (Mechanismus) |
| `skills/AUDIT.md` | neu (Audit-Log) |
| `skills/<name>/versions/v1/SKILL.md` | neu (14 Snapshots) |
| `ergebnisse/procedural-memory.md` | neu (dieses Dokument) |
| `ergebnisse/rekursion/015-*.md` | Provenienz |

## 7. Quellen (alle HTTP 200, 2026-10-01)

- https://arxiv.org/abs/2508.06433 (Mem^p)
- https://aclanthology.org/2026.findings-acl.866.pdf (Mem^p, ACL Findings 2026)
- https://arxiv.org/abs/2606.23127 (AFTER)
- https://arxiv.org/abs/2602.01869 (ProcMEM)
- https://arxiv.org/abs/2510.04851 (LEGOMem)
- https://arxiv.org/abs/2512.13564 (Memory in the Age of AI Agents)
- https://arxiv.org/abs/2602.06052 (Survey: Self-Evolving Agents)
- https://arxiv.org/abs/2602.05665 (Graph-based Agent Memory)
