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
| 077 | `077-n8-theta-basismessung.md` | System-Iteration (N8: Basismessung vor `PeftModel.from_pretrained`; GPU extern verifiziert) | **approved**: Batnini + Taoufik, 2026-10-08 | siehe File |
| 078 | `078-n2-n3-konsolidierung-flush.md` | System-Iteration (N2/N3: Konsolidierung an Inhalt gebunden + Flush nur mit Erfolgsbeleg/Archivschutz, Phase 2) | **approved**: Batnini + Taoufik, 2026-10-08 | siehe File |
| 079 | `079-n4-n6-n5-approval-provrevision-mcp.md` | System-Iteration (N4/N6/N5: Freigabe bindet §6-Kopf · PROV-Revisionskette · MCP-§6-Pflichtfelder, Phase 2) | **approved**: Batnini + Taoufik, 2026-10-08 | siehe File |
| 080 | `080-n7-oracle-evidenz-revise.md` | System-Iteration (N7: bei `world_state_probe` entscheidet die Oracle-Evidenz die Revision, Phase 2) | **approved**: Batnini + Taoufik, 2026-10-08 | siehe File |
| 081 | `081-s9-abschluss-fademem-oob-m4-a5-v12.md` | §9-Abschluss (FadeMem + OOB in Ontologie, A5-Bezüge, 073/074/`fademem` approved, `versions/v12`) | **approved**: Batnini + Taoufik, 2026-10-08 | siehe File |
| 082 | `082-gdi-sahoo.md` | System-Iteration (GDI exakt nach arXiv:2603.06333, Gl. 5–16; JSD-Monitor bleibt) | **approved**: Batnini + Taoufik, 2026-10-08 | siehe File |
| 083 | `083-drift-kalibrierung-harness.md` | System-Iteration (Kalibrier-Harness Text→GDI→Gl. 14–16, externes Grader-Signal §6) | **approved**: Batnini + Taoufik, 2026-10-08 | siehe File |
| 084 | `084-drift-kalibrierung-ergebnis.md` | System-Iteration (reales Kalibrierergebnis Θ vs. Θ′: τ=0.104, AUC 0.684) | **approved**: Batnini + Taoufik, 2026-10-08 | siehe File |
| 085 | `085-sahoo-3domanen-kalibrierung.md` | System-Iteration (SAHOO 3 Domänen: τ=0.218, AUC 0.699) | **approved**: Batnini + Taoufik, 2026-10-08 | siehe File |
| 086 | `086-fwr-gstar-gate.md` | System-Iteration (Eskalationsgate `g* = V_large − V_small` §3.3.2, λ Tabelle 1) | **approved**: Batnini + Taoufik, 2026-10-08 | siehe File |
| 087 | `087-live-run-driver.md` | System-Iteration (Live-Run-Driver 8 Stufen + 5 Phasen, §6 externes Signal) | **approved**: Batnini + Taoufik, 2026-10-08 | siehe File |
| 088 | `088-laeufe-ergebnisse.md` | System-Iteration (Live-Run 3 Aufgaben + größeres Kalibrierset n=180: τ=0.240, AUC 0.760) | **approved**: Batnini + Taoufik, 2026-10-08 | siehe File |
| 089 | `089-f1-f2-f3-consolidation-binding.md` | System-Iteration (F1/F2/F3: Konsolidierung fail-closed an Inhalt + positiven Probe gebunden) | **approved**: Batnini + Taoufik, 2026-10-08 | siehe File |
| 090 | `090-f4-mcp-k8-evidence-hash.md` | System-Iteration (F4: MCP-K8-Kopf erst nach PII-Sanitisierung; Evidence-Hash == Body-Hash) | **approved**: Batnini + Taoufik, 2026-10-08 | siehe File |
| 091 | `091-f5-grader-korrektheit.md` | System-Iteration (F5: Kalibrier-Grader Math=Endantwort nach `####`, Truth=verneinter Treffer falsch; Rekalibrierung nötig) | pending (§9 `ask`: Label-Semantik) | siehe File |
| 092 | `092-f6-subjekt.md` | System-Iteration (F6: ZsRE-Fragen an Subjekt gebunden – `XXX` → `subject`; Formatänderung §9) | **approved**: Batnini + Taoufik, 2026-10-08 | siehe File |
| 093 | `093-gdi-betrieb.md` | System-Iteration (Item 3: kalibriertes GDI Gl. 12–16 im Betriebspfad, `load_calibration`/`observe_gdi` + Runner-Schalter; Interface §9) | **approved**: Batnini + Taoufik, 2026-10-08 | siehe File |
| 094 | `094-freigabe-erfolgspfad.md` | System-Iteration (Freigabe-Erfolgspfad: `self_update`/`approvers` in `run_recursion` + CLI `--approver` im Live-Driver; Interface §9) | **approved**: Batnini + Taoufik, 2026-10-08 | siehe File |
| 095 | `095-live-lokal.md` | System-Iteration (voller Live-Lauf lokal via Ollama/qwen2.5-1.5b, kein Endpoint) | **approved**: Batnini + Taoufik, 2026-10-09 | siehe File |
| 096 | `096-d2-gdi-prewrite.md` | System-Iteration (D2/Audit d25486c: kalibriertes GDI-Gate **vor** der Mutation, Stufe 3) | **approved**: Batnini + Taoufik | siehe File |
| 097 | `097-d1-negation.md` | System-Iteration (D1/Audit d25486c: explizite Verneinung `false`/`untrue`/`wrong`/`nicht wahr`/`falsch` ⇒ falsch; Truth-Grader) | **approved**: Batnini + Taoufik | siehe File |
| 098 | `098-d3-localstart.md` | System-Iteration (D3/Audit d25486c: lokaler Start nutzt `HELA_MODEL` für Reflexion/Oracle + `--require-success` ⇒ Exit 1 bei erfolglosem Lauf) | **approved**: Batnini + Taoufik | siehe File |
| 099 | `099-drift-rekalibrierung-d1.md` | System-Iteration (Drift-Rekalibrierung mit D1-Gradern: τ=0.225, AUC 0.780) | **approved**: Batnini + Taoufik, 2026-10-09 | siehe File |
| 100 | `100-kaggle-train-cli-t4-fp16.md` | System-Iteration (Kaggle-SFT: echte CLI `--dataset/--out/--gpu/--source` + T4⇒fp16 via Compute Capability; §9 additiv) | **approved**: Batnini (Auftrag 2026-10-09) | siehe File |
| 101 | `101-llm-retry-backoff.md` | System-Iteration (LLM-Aufrufe robust gegen Überlast: `_create_with_retry` in `distill`/`parse_transition_delta`; CI-Flake behoben) | **approved**: Batnini (Auftrag 2026-10-09) | siehe File |
| 102 | `102-kaggle-sft-precision-fp16.md` | System-Iteration (Kaggle-SFT: Einzel-Präzision fp16 beim Modell-Load — bf16-Config vs. fp16-GradScaler behoben) | **approved**: Batnini (Auftrag 2026-10-10) | siehe File |
| 103 | `103-theta-prime-negativ.md` | System-Iteration (Θ′-Write-Back echter Lauf: `ΔEM=+1` (8→9/200) → **`rejected`**: nicht internalisiert; §9 deny) | **rejected** (Compare < 70 %) | siehe File |
| 104 | `104-fixes-e1-e4.md` | System-Iteration (E1–E4: reflective_agent ENV, llm_retry 404-Trennung, zsre-Subjektbindung; Audit e2e-699dda4) | **approved** (Score 793/793 = 100 %) | Audit e2e-699dda4; AGENTS.md §10.2/§11, §6, §9 |
| 105 | `105-e1-e2-e2e.md` | System-Iteration (E1/E2 echter lokaler Live-Lauf: E1 wirkt (`model.reflection=qwen-local`); 3/3 nicht reproduziert — FWR `uncertain`/Oracle „I don't know", nicht E1; E2-404-Fallback belegt) | **approved** (technischer Pfad) + Caveat | `live_run.py:40-45,273`; AGENTS.md §10.2/§11/§9.3 |
| 106 | `106-write-back-review-fixes.md` | System-Iteration (Review-Funde 1–4 an `write_back`: Provenienz + Evidenz/Proposal + ehrliche Docstrings; additiv/fail-closed) | **approved**: Batnini + Taoufik, 2026-10-11 (§9.3) | arXiv:2608.22215 §3.4; connectors/gaama.md; AGENTS.md §10.3 |

## Guardrail

Kein `self_update` ohne `approved`. Kein `Compare` ohne externes Signal.
Verstöße werden hier als `rejected` dokumentiert.