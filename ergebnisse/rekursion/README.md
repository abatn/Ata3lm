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
| 043 | `043-mcp-kontext.md` | System-Iteration (MCP-Kontext: TTC/Lazy-Gating) | approved: Batnini, 2026-10-03 | siehe File |
| 044 | `044-mcp-aktivierung.md` | System-Iteration (MCP-Aktivierung 12 Server) | approved: Batnini, 2026-10-03 | siehe File |
| 045 | `045-mcp-kalibrierung.md` | System-Iteration (MCP-Kalibrierung Ist vs. Paper) | approved: Batnini, 2026-10-03 | siehe File |
| 046 | `046-shacl-inferenz-echt.md` | System-Iteration (SHACL-Inferenz, echte Engine) | approved: Batnini, 2026-10-04 | siehe File |
| 047 | `047-spreading-activation.md` | System-Iteration (HeLa-Mem Spreading Activation) | approved: Batnini, 2026-10-04 | siehe File |
| 048 | `048-lifecycle-runner.md` | System-Iteration (8-Stufen-Runner) | approved: Batnini, 2026-10-04 | siehe File |
| 049 | `049-skill-interpreter.md` | System-Iteration (Skill-Interpreter) | approved: Batnini, 2026-10-04 | siehe File |
| 050 | `050-skill-interpreter-agent.md` | System-Iteration (ReAct-Loop + MCP-Executor) | approved: Batnini, 2026-10-04 | siehe File |
| 051 | `051-connector-binding.md` | System-Iteration (Connector-Binding SHACL/W3C) | approved: Batnini, 2026-10-04 | siehe File |
| 052 | `052-mcp-live-binding.md` | System-Iteration (MCP-Live-Binding + Governance) | approved: Batnini, 2026-10-04 | siehe File |
| 053 | `053-memory-verifikation.md` | System-Iteration (Gedächtnis-Verifikation L0–L4) | approved: Batnini, 2026-10-04 | siehe File |
| 054 | `054-shared-memory-verifikation.md` | System-Iteration (Shared-Memory-Verifikation) | approved: Batnini, 2026-10-04 | siehe File |
| 055 | `055-verifikation-verifikation.md` | System-Iteration (Zwei-Personen-Gate-Verifikation) | approved: Batnini, 2026-10-04 | siehe File |
| 056 | `056-reverse-engineering-vollstaendig.md` | System-Iteration (Reverse Engineering 8 Schichten) | approved: Batnini, 2026-10-04 | siehe File |
| 057 | `057-recursion-runner.md` | System-Iteration (5-Phasen-Runner SEAA) | approved: Batnini, 2026-10-04 | siehe File |
| 058 | `058-fixes-p1.md` | System-Iteration (E2E-Fixes P1: F2/F1/S1) | approved: Batnini, 2026-10-05 | siehe File |
| 059 | `059-fixes-p2.md` | System-Iteration (E2E-Fixes P2: F3/S2/S3) | approved: Batnini, 2026-10-05 | siehe File |
| 060 | `060-fixes-p3.md` | System-Iteration (E2E-Fixes P3: F4/F5/A9) | approved: Batnini, 2026-10-05 | siehe File |
| 061 | `061-e2e-pruefung.md` | System-Iteration (E2E-Prüfung N1–N7, Revision e1a61b9) | approved: Batnini, 2026-10-05 | siehe File |
| 062 | `062-p1-n1-n2-n5-n3.md` | System-Iteration (P1-Fixes N1/N2/N5/N3) | approved: Batnini, 2026-10-05 | siehe File |
| 063 | `063-p2-n4-n6-n7.md` | System-Iteration (P2-Fixes N4/N6/N7) | approved: Batnini, 2026-10-05 | siehe File |
| 064 | `064-p3a-s1-s6.md` | System-Iteration (P3a-Struktur S1a/S1b/S3/S4/S5/S6) | approved: Batnini, 2026-10-05 | siehe File |
| 065 | `065-p3b-ci.md` | System-Iteration (P3b-CI F1–F5) | approved: Batnini, 2026-10-05 | siehe File |
| 066 | `066-p3d-s1-korrekt.md` | System-Iteration (P3d/S1-korrekt: Drift-Referenz §9.1c/§9.2b) | approved: Batnini, 2026-10-05 („go mit Bedingung 1–3") | siehe File |
| 067 | `067-k4-skill-binding.md` | System-Iteration (K4: Skills maschinell an Executoren gebunden) | **approved**: Batnini, 2026-10-06 | siehe File |
| 068 | `068-mcp-trace-audit.md` | System-Iteration (K7: DomainRejection fail-closed + OTel-Spans + Audit) | **approved**: Batnini, 2026-10-06 | siehe File |
| 069 | `069-p1p2-kopplung-3.md` | System-Iteration (P1/P2-Kopplung, 3. Prüfung: R04/R05/R06/R07/R10/R16/R17/R18/R19) | **approved**: Batnini, 2026-10-06 | siehe File |
| 070 | `070-m1b-kaggle-training.md` | System-Iteration (M1b: Kaggle-Trainingscode Θ→Θ′) | pending (unverifiziert-lokal, Kaggle) | siehe File |
| 071 | `071-m1-slow-consolidation.md` | System-Iteration (M1: Slow-Consolidation-Vorarbeit §10.3) | **approved**: Batnini, 2026-10-07 | siehe File |
| 072 | `072-zsre-konsolidierungskorpus.md` | System-Iteration (ZsRE-Konsolidierungskorpus §10.3) | **approved**: Batnini, 2026-10-07 | siehe File |
| 073 | `073-out-of-band-eval.md` | System-Iteration (M3: Out-of-Band-Evaluation / World-State-Oracle §6) | pending (§9 `ask`: neue Quelle + Interface) | siehe File |
| 074 | `074-m4-lifecycle.md` | System-Iteration (M4: Geschlossener Lifecycle, Router senses consolidation §10.1/§10.3) | pending (§9 `ask`: Interface) | siehe File |
| 075 | `075-k8-structured-pflichtfelder.md` | System-Iteration (K8: §6-Pflichtfelder im `structured`-Write, Gateway↔Invariante) | **approved**: Batnini, 2026-10-08 | siehe File |
| 076 | `076-n1-provenienz-transaktion.md` | System-Iteration (N1: Provenienz + Datenwrite = EINE Transaktion, Phase 1 autonom) | umgesetzt; Review im Gesamt-STOPP ausstehend | siehe File |
| 077 | `077-n8-theta-basismessung.md` | System-Iteration (N8: Basismessung vor `PeftModel.from_pretrained`, Phase 1 autonom) | umgesetzt; §9 `ask` offen (neue Quellen + GPU-Gesamtlauf) | siehe File |
| 078 | `078-n2-n3-konsolidierung-flush.md` | System-Iteration (N2/N3: Konsolidierung an Inhalt gebunden + Flush nur mit Erfolgsbeleg/Archivschutz, Phase 2) | **approved**: Batnini + Taoufik, 2026-10-08 | siehe File |
| 079 | `079-n4-n6-n5-approval-provrevision-mcp.md` | System-Iteration (N4/N6/N5: Freigabe bindet §6-Kopf · PROV-Revisionskette · MCP-§6-Pflichtfelder, Phase 2) | **approved**: Batnini + Taoufik, 2026-10-08 | siehe File |
| 080 | `080-n7-oracle-evidenz-revise.md` | System-Iteration (N7: bei `world_state_probe` entscheidet die Oracle-Evidenz die Revision, Phase 2) | **approved**: Batnini + Taoufik, 2026-10-08 | siehe File |

## Guardrail

Kein `self_update` ohne `approved`. Kein `Compare` ohne externes Signal.
Verstöße werden hier als `rejected` dokumentiert.