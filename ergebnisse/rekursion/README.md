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
| 022 | `022-pii-minimierung.md` | System-Iteration (Trust/Privacy) | approved: Batnini, 2026-10-01 | siehe File |
| 023 | `023-zwei-personen.md` | System-Iteration (Governance/Approval) | approved: Batnini, 2026-10-01 | siehe File |
| 024 | `024-bias-drift.md` | System-Iteration (Governance/Monitoring) | approved: Batnini, 2026-10-01 | siehe File |
| 025 | `025-l4-operational.md` | System-Iteration (Skills/L4) | approved: Batnini, 2026-10-01 | siehe File |
| 026 | `026-shared-supersession.md` | System-Iteration (Shared Memory) | approved: Batnini, 2026-10-01 | siehe File |
| 027 | `027-drift-index.md` | System-Iteration (Governance/Monitoring) | approved: Batnini, 2026-10-01 | siehe File |
| 028 | `028-bi-temporal.md` | System-Iteration (Memory) | approved: Batnini, 2026-10-01 | siehe File |
| 029 | `029-forschungsluecken-4.md` | System-Iteration (Konsolidierung) | approved: Batnini, 2026-10-01 | siehe File |
| 030 | `030-governance-mcp.md` | System-Iteration (Governance/MCP) | approved: Batnini, 2026-10-01 (Score 8/8) | siehe File |
| 031 | `031-fwr-modell.md` | System-Iteration (Governance/FWR) | approved: Batnini, 2026-10-01 (Score 8/8) | siehe File |
| 032 | `032-fix-reflective-agent.md` | System-Iteration (Robustheit/HMM) | approved: Batnini, 2026-10-01 (Auftrag „Rekursion 032") | siehe File |
| 033 | `033-robuster-grader.md` | System-Iteration (Grader/JSON) | approved: Batnini, 2026-10-02 (Auftrag „nach AGENTS.md") | siehe File |
| 034 | `034-externer-grader-test.md` | System-Iteration (Grader/externer Endpoint) | approved: Batnini, 2026-10-02 (Auftrag „test und führe dein Plan") | siehe File |
| 035 | `035-experience-route.md` | System-Iteration (FWR/Experience-Route, A+D) | approved: Batnini, 2026-10-03 (A+D) | siehe File |
| 036 | `036-fwr-write-action.md` | System-Iteration (FWR-Write-Aktion §10.7) | approved: Batnini, 2026-10-03 (Human-Gate §9) | siehe File |
| 037 | `037-tier2-tier3.md` | System-Iteration (tier2→tier3 Hybrid, GAAMA) | approved: Batnini, 2026-10-03 (Human-Gate §9) | siehe File |
| 038 | `038-gaama-ladepfad.md` | System-Iteration (GAAMA-Ladepfad, Erfindung entfernt) | approved: Batnini, 2026-10-03 | siehe File |
| 039 | `039-gaama-mechanik-fwr.md` | System-Iteration (d=2, Hub-Dampening, §10.1-FWR) | approved: Batnini, 2026-10-03 | siehe File |
| 040 | `040-write-kette.md` | System-Iteration (Write-Kette §9.2c/a + §10.1) | approved: Batnini, 2026-10-03 | siehe File |
| 041 | `041-echte-verifikation.md` | System-Iteration (Fakes ersetzt, Guardrail 7) | approved: Batnini, 2026-10-03 | siehe File |
| 042 | `042-ci-integration.md` | System-Iteration (CI-Integration A–O) | approved: Batnini, 2026-10-03 | siehe File |

## Guardrail

Kein `self_update` ohne `approved`. Kein `Compare` ohne externes Signal.
Verstöße werden hier als `rejected` dokumentiert.