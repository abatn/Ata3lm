# L4 Procedural Memory – operationalisiert (First-Class)

> Datum: 2026-10-01
> Status: **Belegt** (Konzept) + **Auftrag** (Mechanik)
> Prinzip: Keine Erfindungen (§6).
> Code: `skills/procedural_memory.py` · Doku: `skills/README.md`

## 0. Quellen-Korrektur (wichtig)

Das im Auftrag genannte Zitat „versioned prompts, workflows, decision rules as
first-class architectural component" steht **NICHT wörtlich** in der Memory
Survey (arXiv:2603.07670). Belegt ist dort:

> „…treating memory as a **first-class system component** worthy of dedicated
> design, testing, and optimization" und „**temporal versioning** (prefer the
> newest record)". (Memory Survey)

Die Formulierung „**first-class, versioned resources**" (Prompts/Ressourcen) +
Version-Manager mit Rollback stammt aus dem **TEA-Protokoll** (arXiv:2506.12508);
„**first-class optimization object**" aus **Mem^p** (arXiv:2508.06433).
→ Attribution entsprechend korrigiert.

## 1. Quellen (verifiziert, HTTP 200)

| Quelle | Kernaussage | Link |
|---|---|---|
| **Memory Survey** | „memory as a **first-class system component**"; „temporal versioning (prefer the newest record)" | https://arxiv.org/abs/2603.07670 |
| **TEA-Protokoll** | Komponenten als „**first-class, versioned resources**"; Version-Manager: „access to historical records for analysis and **rollback**" | https://arxiv.org/abs/2506.12508 |
| **Mem^p** | procedural memory als „**first-class optimization object**"; Update-Strategien | https://arxiv.org/abs/2508.06433 |
| **AFTER** | Skill-Files als „first-class artifact outside the base prompt" | https://arxiv.org/abs/2606.23127 |
| **ProcMEM** | PPO-Gate (Verification) vor Skill-Aufnahme | https://arxiv.org/abs/2602.01869 |

## 2. Die drei Operationalisierungen

| # | Regel | Mechanik | Status |
|---|---|---|---|
| 1 | **Selektives Update** | `propose_update(skill, text, reason, approved)` — schreibt **nur** bei `approved` (Human-Gate) | **Belegt** (Mem^p Update; ProcMEM Gate) |
| 2 | **Versionsrollback** | `rollback(skill, version)` — frühere `versions/vN/SKILL.md` wiederherstellen; aktueller Stand vorher gesichert | **Belegt** (TEA Version-Manager) |
| 3 | **Audit-Trail** | `skills/AUDIT.md` (Zeit·Skill·Aktion·Begründung) + `skills/audit-diffs/*.diff` | **Belegt** (Mem^p Build/Update; TEA version history) |

## 3. Selbsttest (reale Ausgabe)

```text
=== [1] Versionierung: v1-Snapshot aller aktiven Skills ===  Snapshots: 14
=== [2] Audit-Log ===  skills/AUDIT.md geschrieben.
=== [3] Selektives Update (Human-Gate) ===
  ohne approved -> applied=False status=pending (kein approved (Human-Gate))
  Inhalt unverändert? True
  mit approved  -> applied=True status=approved version=v3
  Inhalt geändert?  True
=== [4] Rollback (versions/vN) ===
  rollback -> {'ok': True, 'restored': 'v1', 'saved_current_as': 'v4'}
  Inhalt wieder v1? True
```

**Ergebnis:** Update nur mit `approved`; Rollback stellt v1 wieder her und sichert
den aktuellen Stand als v4 (kein Verlust); jede Änderung im Audit-Log.

## 4. Status-Trennung

| Aussage | Status |
|---|---|
| Memory/Prozeduren als First-Class | **Belegt** (Memory Survey/TEA/Mem^p) |
| Temporal versioning / Rollback | **Belegt** (Memory Survey; TEA) |
| Update nur mit Freigabe (Gate) | **Belegt** (Mem^p; ProcMEM) |
| Konkrete `versions/vN/`-Mechanik + „L4"-Label | **Auftrag** |

## 5. Dateien

| Artefakt | Art |
|---|---|
| `skills/procedural_memory.py` | erweitert (`rollback`) |
| `skills/README.md` | erweitert (Rollback + Quellen) |
| `ergebnisse/l4-procedural.md` | neu (dieses Dokument) |
| `ergebnisse/rekursion/020-*.md` | Provenienz |

## 6. Quellen (HTTP 200, 2026-10-01)

- https://arxiv.org/abs/2603.07670 (Memory Survey)
- https://arxiv.org/abs/2506.12508 (TEA-Protokoll)
- https://arxiv.org/abs/2508.06433 (Mem^p)
- https://arxiv.org/abs/2606.23127 (AFTER)
- https://arxiv.org/abs/2602.01869 (ProcMEM)
