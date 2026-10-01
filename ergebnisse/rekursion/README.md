# Ergebnisse: Rekursion

> Lab-Prinzip: Keine Erfindungen – nur was tatsächlich in den Dateien steht.

Jede rekursive Verbesserung wird hier als eigenes File dokumentiert –
mit Quelle (Paper, Code). MD-first, keine Erfindungen.

## Konvention

Dateiname: `NNN-kurztitel.md` (z. B. `001-initialbaseline.md`).

Pflichtfelder pro Iteration (vgl. `skills/recursive-improve/SKILL.md`):

- Datum + Rekursionstiefe (z. B. `t=0 → t=1`)
- Phase: Observe / Compare / Revise (+ Konstrukt/Akt-Folgewirkung)
- Zustand vorher/nachher: `(π, I, M)`-Diff
- Compare-Beleg: externes Signal (Validierungsset, Test, Ground Truth)
  mit Score + Log-Auszug – kein rein internes Scoring
- Quelle: Paper-Link und/oder Code-Link
- Freigabe: `pending | approved:<wer, wann> | rejected:<grund>`
- Nächstes Self-Feedback: was fließt in `t+1` ein

## Index

| # | File | Tiefe | Status | Quelle |
|---|---|---|---|---|
| 000 | `000-template.md` | – | Template | – |
| 001 | `001-bootstrap-rekursion-phase.md` | `t=0` (Bootstrap, keine Code-Änderung) | approved: bootstrap | siehe File |
| 002 | `002-konstrukt-bootstrap.md` | `t=0.K` (Konstrukt-Einbau, Docs-only) | approved: Batnini, 2026-09-30 | siehe File |
| 003 | `003-akt-bootstrap.md` | `t=0.A` (Akt-Einbau, Docs-only) | approved: Batnini, 2026-09-30 | siehe File |
| 004 | `004-observe-bootstrap.md` | `t=0.O` (Observe-Einbau, Docs-only) | approved: Batnini, 2026-09-30 | siehe File |
| 005 | `005-compare-bootstrap.md` | `t=0.C` (Compare-Einbau, Docs-only) | approved: Batnini, 2026-09-30 | siehe File |
| 006 | `006-revise-bootstrap.md` | `t=0.R` (Revise-Einbau, Docs-only) | approved: Batnini, 2026-09-30 | siehe File |
| 007 | `007-wissenszyklus-bootstrap.md` | `t=0.W` (Gesetz+Zyklus, Docs-only) | approved: Batnini, 2026-09-30 | siehe File |
| 008 | `008-t1-rekursion.md` | `t=0 → t=1` | approved: Batnini, 2026-10-01 (Score 3/3) | siehe File |
| 009 | `009-t2-echte-rekursion.md` | `t=1 → t=2` | approved: Batnini, 2026-09-30 (π₁ Score 3/3) | siehe File |
| 010 | `010-t3-rekursion.md` | `t=2 → t=3` | approved: Batnini, 2026-09-30 (π₁ Score 4/4) | siehe File |
| 011 | `011-t4-rekursion.md` | `t=3 → t=4` | approved: Batnini, 2026-10-01 (π₁ Score 3/3) | siehe File |
| 012 | `012-t5-rekursion.md` | `t=4 → t=5` | approved: Batnini, 2026-10-01 | siehe File |
| 013 | `013-t6-rekursion.md` | `t=5 → t=6` | approved: Batnini, 2026-10-01 | siehe File |
| 014 | `014-ingestion-hook-v2.md` | System-Iteration (Memory) | approved: Batnini, 2026-10-01 | siehe File |
| 015 | `015-procedural-memory-l4.md` | System-Iteration (Skills) | approved: Batnini, 2026-10-01 | siehe File |
| 016 | `016-neuro-symbolic-loop.md` | System-Iteration (cognize) | approved: Batnini, 2026-10-01 | siehe File |
| 017 | `017-memory-lifecycle.md` | System-Iteration (Memory) | approved: Batnini, 2026-10-01 | siehe File |
| 018 | `018-multi-agent-sharing.md` | System-Iteration (Memory) | approved: Batnini, 2026-10-01 | siehe File |
| 019 | `019-trust-governance.md` | System-Iteration (Governance) | approved: Batnini, 2026-10-01 | siehe File |
| 020 | `020-l4-procedural.md` | System-Iteration (Skills/L4) | approved: Batnini, 2026-10-01 | siehe File |
| 021 | `021-shared-konflikt.md` | System-Iteration (Shared Memory) | approved: Batnini, 2026-10-01 | siehe File |

## Guardrail

Kein `self_update` ohne `approved`. Kein `Compare` ohne externes Signal.
Verstöße werden hier als `rejected` dokumentiert.