# 019 – Trust & Governance: Privacy · Bias · Adversarial Robustness

> Datum: 2026-10-01
> Rekursionstiefe: System-Iteration (Governance), nicht Solver-t
> Phase: Konstrukt (3 Guards) + Revise (AGENTS.md §9.2)
> Auslöser: menschlicher Auftrag vom 2026-10-01.

## 1. Zustand vorher / nachher

| Guard | vorher | nachher |
|---|---|---|
| Privacy | nur Secret-Filter (ingestion_hook) | **PII-Erkennung + Anonymisierung** (`trust.py`) |
| Bias | – | **periodischer Check gegen Ground-Truth** |
| Adversarial | – | **Poisoning-Guard** (verified + trusted origin) |

## 2. Änderungen

- `data/memory/trust.py` (neu): `PIIFilter`, `PoisoningGuard`, `BiasCheck` + Demo.
- `AGENTS.md` §9.2 (Trust & Governance).
- `ergebnisse/trust-governance.md`.

## 3. Compare-Beleg (externes Signal)

`python3 data/memory/trust.py` (reale Ausgabe):
- PII erkannt (email, iban, phone) + anonymisiert (`[PII:<typ>]`).
- Poisoning-Guard: untrusted source → rejected; unverified → rejected; verified+trusted → admitted.
- Bias: drift 0.15 > τ=0.10 → **flag**.

## 4. Quellen (belegt, HTTP 200)

- SP-Mem (arXiv:2608.16551) · agentmemory (Privacy)
- DIB/Dynamic Memory Tagging (arXiv:2602.01558) · Memory Contagion (2606.23195) · MemAudit (2606.24595) (Bias)
- MPBench (2606.04329) · A-MemGuard (2510.02373) · TMA-NM (2606.24322) · MemPoison (2607.14651) (Adversarial)
- LTM-Security-Survey (2604.16548) · TrustAgent (2503.09648) (Governance/Umbrella)

## 5. Abgrenzung (Auftrag)

τ=0.10, konkrete PII-Regexe, Guard-Implementierung = **Auftrag**; Mechanik = **Belegt**.

## 6. Guardrails

- `AGENTS.md` geändert **auf ausdrücklichen menschlichen Auftrag** (§9.2).
- Kein Item wird gespeichert, das einen Guard nicht passiert (`rejected`).

## 7. Freigabe

**Freigabe-Status für π₁:** `approved: Batnini, 2026-10-01`.
