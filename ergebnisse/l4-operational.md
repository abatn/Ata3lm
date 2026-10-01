# L4 Procedural Memory – operationalisiert (Update · Rollback · Audit)

> Datum: 2026-10-01
> Status: **Belegt** (Konzept) + **Auftrag** (Mechanik)
> Prinzip: Keine Erfindungen (§6).
> Code: `skills/procedural_memory.py` · Doku: `skills/README.md`
> Baut auf Rekursion 015/020 auf (konsolidierter Nachweis).

## 0. Quellen-Korrektur (wichtig)

Das im Auftrag genannte Zitat „versioned prompts, workflows, decision rules as
first-class architectural component" steht **NICHT wörtlich** in der Memory
Survey (arXiv:2603.07670). Belegt ist dort:

> „…treating memory as a **first-class system component** worthy of dedicated
> design, testing, and optimization" + „**temporal versioning** (prefer the
> newest record)."

Die Formulierung „**first-class, versioned resources**" (Prompts/Ressourcen) +
Version-Manager mit Rollback stammt aus dem **TEA-Protokoll** (arXiv:2506.12508);
„**first-class optimization object**" aus **Mem^p** (arXiv:2508.06433).
→ Attribution korrigiert (Survey/TEA/Mem^p), nicht die Memory Survey allein.

## 1. Quellen (verifiziert, HTTP 200)

| Quelle | Kernaussage | Link |
|---|---|---|
| **Memory Survey** | „memory as a **first-class system component**"; „temporal versioning (prefer the newest record)" | https://arxiv.org/abs/2603.07670 |
| **TEA-Protokoll** | Komponenten als „**first-class, versioned resources**"; Version-Manager: „…for analysis and **rollback**" | https://arxiv.org/abs/2506.12508 |
| **Mem^p** | procedural memory als „**first-class optimization object**" | https://arxiv.org/abs/2508.06433 |
| **AFTER** | Skill-Files als „first-class artifact outside the base prompt" | https://arxiv.org/abs/2606.23127 |
| **ProcMEM** | PPO-Gate (Verification) vor Skill-Aufnahme | https://arxiv.org/abs/2602.01869 |

## 2. Die drei Regeln

| Regel | Mechanik | Status |
|---|---|---|
| **Selektives Update** | `propose_update(skill, text, reason, approved)` — schreibt **nur** bei `approved` | **Belegt** (Mem^p; ProcMEM) |
| **Versionsrollback** | `rollback(skill, version)` → `versions/vN/SKILL.md` wiederherstellen (aktueller Stand vorher gesichert) | **Belegt** (TEA Version-Manager) |
| **Audit-Trail** | `skills/AUDIT.md` (Zeit·Skill·Aktion·Begründung) + `audit-diffs/*.diff` | **Belegt** (Mem^p/TEA) |

## 3. Test: Update + Rollback + Audit (reale Ausgabe)

```text
=== [3] Selektives Update (Human-Gate) ===
  ohne approved -> applied=False status=pending (kein approved (Human-Gate))
  Inhalt unverändert? True
  mit approved  -> applied=True status=approved version=v7
  Inhalt geändert?  True
=== [4] Rollback (versions/vN) ===
  rollback -> {'ok': True, 'restored': 'v1', 'saved_current_as': 'v8'}
  Inhalt wieder v1? True
```

**Echter Audit-Trail** (`skills/AUDIT.md`, Auszug — jede Änderung mit Begründung):

```text
| 2026-10-01T16:26:04 | skills/cognize/SKILL.md | snapshot v1   | Baseline (Procedural Memory L4 eingeführt) |
| 2026-10-01T16:29:52 | skills/cognize/SKILL.md | snapshot v2   | Update auf v2 |
| 2026-10-01T16:29:52 | skills/cognize/SKILL.md | update applied (v2) | Fester LLM→Symbolic→Commit-Loop dokumentiert (AWS Semantic Layer + Swansea) |
```

**Ergebnis:** Ohne `approved` **kein** Write (pending); mit `approved` angewandt
(+Snapshot +Audit); Rollback stellt v1 wieder her und sichert den aktuellen Stand
als v8 (kein Verlust).

## 4. Status-Trennung

| Aussage | Status |
|---|---|
| Memory/Prozeduren als First-Class | **Belegt** (Memory Survey/TEA/Mem^p) |
| Temporal versioning / Rollback | **Belegt** (Memory Survey; TEA) |
| Update nur mit Freigabe | **Belegt** (Mem^p; ProcMEM) |
| `versions/vN`-Mechanik + „L4"-Label | **Auftrag** |

## 5. Dateien

| Artefakt | Art |
|---|---|
| `skills/procedural_memory.py` | bestehend (snapshot/audit/propose_update/rollback) |
| `skills/README.md` | bestehend (L4-Doku) |
| `skills/AUDIT.md` | bereinigt (spurioses Duplikat entfernt) |
| `ergebnisse/l4-operational.md` | neu (dieses Dokument) |
| `ergebnisse/rekursion/025-*.md` | Provenienz |

## 6. Quellen (HTTP 200, 2026-10-01)

- https://arxiv.org/abs/2603.07670 (Memory Survey)
- https://arxiv.org/abs/2506.12508 (TEA-Protokoll)
- https://arxiv.org/abs/2508.06433 (Mem^p)
- https://arxiv.org/abs/2606.23127 (AFTER)
- https://arxiv.org/abs/2602.01869 (ProcMEM)
