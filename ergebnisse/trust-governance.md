# Trust & Governance: Privacy · Bias · Adversarial Robustness

> Datum: 2026-10-01
> Status: **Belegt** (Mechanik) + **Auftrag** (Schwellen/Implementierung)
> Prinzip: Keine Erfindungen (§6).
> Code: `data/memory/trust.py` · Gesetz: `AGENTS.md` §9.2

## 1. Quellen (verifiziert, HTTP 200)

| Thema | Quelle | Kernaussage (wörtlich/nah) | Link |
|---|---|---|---|
| **Privacy** | **SP-Mem** | „identify and **separate sensitive information** from raw user inputs … store **sanitized content** and exact private values in isolated structures" | https://arxiv.org/abs/2608.16551 |
| **Privacy** | agentmemory | „API keys, secrets, `<private>` tags **stripped before storage**" | https://github.com/rohitg00/agentmemory |
| **Bias** | **DIB / Dynamic Memory Tagging** | „**Periodic Bias Evaluation** … deploy the DIB benchmark to evaluate the agent's current implicit bias state"; Fairness-Tag **vor** dem Memory-Write; Bias ↓ > 50 % | https://arxiv.org/abs/2602.01558 |
| **Bias** | Memory Contagion | Evaluator-Bias propagiert cross-temporal über Memory; „**no observed safe threshold**" | https://arxiv.org/abs/2606.23195 |
| **Bias** | MemAudit | Memory-Audit gegen **hidden Ground-Truth** | https://arxiv.org/abs/2606.24595 |
| **Adversarial** | **MPBench** | Vuln **„V-S1: No Write-Path Validation"**; „source isolation"; „write-path provenance tracking" | https://arxiv.org/abs/2606.04329 |
| **Adversarial** | **A-MemGuard** | **Consensus-based validation**; ASR ↓ > 95 % | https://arxiv.org/abs/2510.02373 |
| **Adversarial** | **TMA-NM** | „**write-time origin binding is necessary**"; untrusted-origin non-actionable | https://arxiv.org/abs/2606.24322 |
| **Adversarial** | MemPoison | L1/L2/L3-Poisoning-Taxonomie | https://arxiv.org/abs/2607.14651 |
| **Governance** | LTM-Security-Survey | „storage-time provenance, versioning, policy-aware retention"; Verifiable Memory Governance | https://arxiv.org/abs/2604.16548 |
| **Umbrella** | TrustAgent | Trustworthy Agents: memory (poisoning/privacy/misuse), Dimensionen safety/privacy/fairness/robustness | https://arxiv.org/abs/2503.09648 |

## 2. Die drei Guards (vor dem Store)

```text
Item (Kandidat)
   │
   ▼
[1] Privacy   – PII erkennen → anonymisieren ([PII:<typ>])        SP-Mem
   ▼
[2] Poisoning – trusted origin UND verified? sonst rejected      MPBench/A-MemGuard/TMA-NM
   ▼
[3] (periodisch) Bias – Score vs. Ground-Truth-Checkpoint (τ)    DIB/DMT
   ▼
Store
```

### 2.1 Privacy — **Belegt** (SP-Mem; agentmemory)
- PII-Typen: E-Mail, Telefon, Kreditkarte, IBAN → `[PII:<typ>]`.
- Kein LLM; spezifische Muster vor greedy `phone`.
- Implementierung: `PIIFilter.detect()/anonymize()`.

### 2.2 Adversarial Robustness — **Belegt** (MPBench/A-MemGuard/TMA-NM)
- **Poisoning-Guard:** nur `source ∈ trusted_sources` **und** `verified=True`.
- Sonst `rejected` mit Grund (origin-bound; consensus/verification).
- Implementierung: `PoisoningGuard.admit(item)`.

### 2.3 Bias — **Belegt** (DIB/DMT)
- **Periodischer** Check des Bias-Scores gegen einen **Ground-Truth-Checkpoint**.
- Abweichung > τ → Flag.
- Implementierung: `BiasCheck(checkpoint, tau).check(current)`.

## 3. Selbsttest (reale Ausgabe)

```text
=== [1] Privacy: PII-Erkennung + Anonymisierung (SP-Mem) ===
  erkannt: ['email', 'iban', 'phone']
  anonymisiert: Kontakt: [PII:email], Tel [PII:phone], IBAN [PII:iban]

=== [2] Adversarial: Poisoning-Guard (MPBench/A-MemGuard/TMA-NM) ===
  user           verified=True  -> admitted=True  | verified + trusted origin
  web:untrusted  verified=True  -> admitted=False | untrusted source 'web:untrusted' (origin-bound)
  user           verified=False -> admitted=False | not verified (consensus/verification required)

=== [3] Bias: periodischer Check gegen Ground-Truth (DIB/DMT) ===
  current=0.06 -> drift 0.01 -> ok
  current=0.09 -> drift 0.04 -> ok
  current=0.20 -> drift 0.15 -> FLAG
```

**Ergebnis:** PII anonymisiert; unverifizierte/untrusted Items **rejected**;
Bias-Drift über τ geflaggt.

## 4. Status-Trennung

| Aussage | Status |
|---|---|
| PII vor dem Store separieren/anonymisieren | **Belegt** (SP-Mem/agentmemory) |
| Periodische Bias-Checks gegen Ground-Truth | **Belegt** (DIB/DMT; MemAudit) |
| Nur verifizierte Items speichern (Poisoning-Guard) | **Belegt** (MPBench/A-MemGuard/TMA-NM) |
| τ = 0.10; konkrete PII-Regexe | **Auftrag** |

## 5. Dateien

| Artefakt | Art |
|---|---|
| `AGENTS.md` §9.2 | erweitert |
| `data/memory/trust.py` | neu (3 Guards + Demo) |
| `ergebnisse/trust-governance.md` | neu (dieses Dokument) |
| `ergebnisse/rekursion/019-*.md` | Provenienz |

## 6. Quellen (alle HTTP 200, 2026-10-01)

- https://arxiv.org/abs/2608.16551 (SP-Mem) · https://github.com/rohitg00/agentmemory
- https://arxiv.org/abs/2602.01558 (DIB/DMT) · https://arxiv.org/abs/2606.23195 · https://arxiv.org/abs/2606.24595
- https://arxiv.org/abs/2606.04329 (MPBench) · https://arxiv.org/abs/2510.02373 (A-MemGuard) · https://arxiv.org/abs/2606.24322 (TMA-NM) · https://arxiv.org/abs/2607.14651 (MemPoison)
- https://arxiv.org/abs/2604.16548 (LTM-Security) · https://arxiv.org/abs/2503.09648 (TrustAgent)
