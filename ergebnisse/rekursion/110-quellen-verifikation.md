# Rekursion 110: Verifikation externer Forschungsquellen

> Datum: 2026-10-11 · Phase: Observe → Compare (externe Verifikation §6)
> Ziel `g` (§2): prüfen, ob die im Bewertungsbericht genannten Quellen
> existieren (keine Erfindung, §6).
> Status: **`approved`** (Dokumentation; §9 „neue Quelle" durch Betreiber
> veranlasst).

## 1. Methode

Zu jeder im externen Bewertungsbericht genannten Quelle wurde am **2026-10-11**
ein **echter HTTP-Abruf/Websearch** durchgeführt (ACL Anthology, arXiv,
NeurIPS-Virtual, IEEE/ICASSP-Workshops, Zenodo, GitHub, exa.ai, dev.to). Erfasst
wurde je Quelle: **Existenz** (Status ✅/⚠️/❌) und der **reale Befund**
(Titel/Thema). Keine Quelle, Zahl oder Aussage wurde ergänzt, die nicht im Abruf
belegt ist (§6). Bei fehlender Auffindbarkeit steht „nicht verifizierbar".

## 2. Tabelle: Quelle | ✅/⚠️/❌ | Befund

| Quelle | Status | Befund (real) |
|---|---|---|
| TiMem | ✅ | ACL Findings 2026, aclanthology.org/2026.findings-acl.1091, arXiv:2601.02845; berichtet 75.30% LoCoMo und 76.88% LongMemEval-S. |
| SAGE | ✅ | arXiv:2609.36043 (28.09.2026) „A Statistical Acceptance Gate for Self-Evolving Agents": per-item paired comparison + one-sided paired test; verwirft unzuverlässige Edits. |
| SAHOO | ✅ | arXiv:2603.06333 (06.03.2026): GDI (Goal Drift Index) + constraint preservation + regression-risk; ICLR-2026-Workshop. |
| Dual-Layer | ✅ | arXiv:2608.22215 v2 (31.08.2026). |
| Kairos | ✅ | nips.cc/virtual/2025/129852 „Validation-Gated Hebbian Learning for Adaptive Agent Memory" (NeurIPS 2025 NORA-Workshop). |
| FadeMem | ✅ | arXiv:2601.18642; IEEE ICASSP 2026 (cmsworkshops.com PaperNum 12764): adaptive exponential decay, dual-layer, ~45% storage reduction. |
| TERSE Tool Catalog (TTC) | ✅ | TTC v1.0-Spec (exa.ai/library/publication/d8scnxv4xrs; dev.to-Artikel): 1.948→650 Token = 66.6% Reduktion. ACHTUNG: Spec/Blog, nicht peer-reviewed. |
| Progress Mirage / World-State Oracle | ✅ | arXiv:2607.25152 + Zenodo DOI 10.5281/zenodo.21594735: Out-of-Band-Evaluator, world-state oracle. |
| SAS Bootstrap Kappa | ⚠️ | Technik real (Efron-Bootstrap; Vierkant 1997 SAS-Macro; paired-bootstrap-Tutorial sxz.io 2026-09-11), aber KEIN einzelnes „Paper" mit diesem Namen. |
| agent-governance-mcp (WhyLab) | ⚠️ | github.com/neogenesislab/WhyLab-NeurIPS2026 real (MIT, public) = „Causal Audit Framework": C1 Drift-Detection, C2 Sensitivity/E-values, C3 Lyapunov-Damping. NICHT „Rule-Enforcement". |
| arXiv:2605.10108 | ⚠️ | real, aber = „GLiNER-Relex" (Joint NER + Relation Extraction) — NICHT Drift-Detection. Der Bericht ordnet das falsch zu. |
| Falsifiable Release Gates | ❌ | keine Quelle/kein Name angegeben ⇒ NICHT verifizierbar. |

## 3. Korrekturen

Zwei Zuordnungen des Berichts sind **falsch** und wurden korrigiert:

1. **arXiv:2605.10108** ist **„GLiNER-Relex"** (Joint NER + Relation
   Extraction) — **nicht** Drift-Detection. Der Bericht ordnet diese Kennung der
   Drift-Detection zu; das ist nicht der Inhalt der Quelle.
2. **agent-governance-mcp (WhyLab-NeurIPS2026)** ist ein **Causal Audit
   Framework** (C1 Drift-Detection, C2 Sensitivity/E-values, C3
   Lyapunov-Damping) — **nicht** „Rule-Enforcement". Der Bericht beschreibt die
   Funktion falsch.

## 4. Nicht verifizierbar

- **Falsifiable Release Gates:** Es wurde im Bericht **keine Quelle und kein
  Name** angegeben ⇒ **nicht verifizierbar** (§6: keine Erfindung).
- **SAS Bootstrap Kappa:** Die **Technik** ist real (Efron-Bootstrap; Vierkant
  1997 SAS-Macro; paired-bootstrap-Tutorial sxz.io 2026-09-11), es existiert
  jedoch **kein einzelnes Paper** mit diesem Namen ⇒ als „Paper" **nicht
  verifizierbar**; nur als Technik belegt.

## 5. Konsequenz für das Projekt

- **SAGE** (per-item paired comparison + one-sided paired test) **bestätigt
  Rek. 103**: das dortige Kriterium ist genau ein per-item gepaarter Test.
- **Progress Mirage / World-State Oracle** (Out-of-Band-Evaluator) **bestätigt**
  das Erfordernis eines **externen Signals** (§6 / Guardrail 2: kein Compare
  ohne verifizierbares Signal).
- **FadeMem / TiMem** sind **valide Memory-Baselines** (adaptive Zerfalls- bzw.
  Retrieval-Verfahren) für künftige Vergleiche.
- **Rek. 103 bleibt `rejected`** (Θ′ Δ+1, p=1.0) — die Verifikation der Quellen
  ändert den Befund dieser Rekursion nicht.

**Zusätzliche (separate) Ebene — Code-Aussagen des Berichts sind veraltet:**
Die Aussagen **E1–E4 offen** und **„write_back wirft NotImplementedError"** sind
**veraltet/falsch**; im Repo gefixt:

- **E1** `reflective_agent._hela_models()` (Rek. 105)
- **E2** `llm_retry` 404-Fallback (Rek. 105)
- **E3** `zsre_corpus` Subjektbindung (Rek. 107)
- **E4** `ipynb main([])` (Rek. 107)
- **`write_back` implementiert** (`slow_consolidation.py:417`), geschlossener
  Lauf belegt (Rek. 108/109; HF `Batnini/knowledge-agent-write-back`).

## 6. Quellen-Liste (nur die geprüften URLs)

- TiMem: <https://aclanthology.org/2026.findings-acl.1091>, <https://arxiv.org/abs/2601.02845>
- SAGE: <https://arxiv.org/abs/2609.36043>
- SAHOO: <https://arxiv.org/abs/2603.06333>
- Dual-Layer: <https://arxiv.org/abs/2608.22215>
- Kairos: <https://nips.cc/virtual/2025/129852>
- FadeMem: <https://arxiv.org/abs/2601.18642>, <https://cmsworkshops.com> (PaperNum 12764)
- TERSE Tool Catalog (TTC): <https://exa.ai/library/publication/d8scnxv4xrs>, dev.to-Artikel (TTC v1.0-Spec)
- Progress Mirage / World-State Oracle: <https://arxiv.org/abs/2607.25152>, Zenodo DOI 10.5281/zenodo.21594735
- SAS Bootstrap Kappa: Efron-Bootstrap; Vierkant 1997 (SAS-Macro); paired-bootstrap-Tutorial <https://sxz.io> (2026-09-11)
- agent-governance-mcp (WhyLab): <https://github.com/neogenesislab/WhyLab-NeurIPS2026>
- arXiv:2605.10108 (GLiNER-Relex): <https://arxiv.org/abs/2605.10108>

## 7. Nächster Schritt

- **Experiment-Register** anlegen (separate Datei).
- **P-109** als separater Proposal-Eintrag (separate Datei).
- Diese Verifikation ist **Beleg** (Trace) für §6; keine Änderung an
  `AGENTS.md` oder `data/memory/*`.
