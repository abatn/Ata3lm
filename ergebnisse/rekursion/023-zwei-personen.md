# 023 – Zwei-Personen-Verifikation (approved-Flow)

> Datum: 2026-10-01
> Rekursionstiefe: System-Iteration (Governance/Approval), nicht Solver-t
> Phase: Revise (approved-Flow)
> Auslöser: menschlicher Auftrag vom 2026-10-01.

## 1. Zustand vorher / nachher

| Aspekt | vorher | nachher |
|---|---|---|
| Freigabe | eine Person | **mind. 2 distinkte natürliche Personen** |
| Status | pending/approved/rejected | + first_approved, second_approved |

## 2. Änderungen

- `data/memory/approval.py` (neu): `TwoPersonApproval` (pending → first_approved
  → second_approved → approved; distinkte Personen erzwungen).
- `AGENTS.md` §9.3.
- `ergebnisse/zwei-personen.md`.

## 3. Compare-Beleg (externes Signal)

`python3 data/memory/approval.py` (reale Ausgabe):
- Batnini → first_approved; Batnini erneut → rejected (distinkt).
- finalize mit 1 → rejected (< 2).
- Verifier2 → second_approved; finalize → approved.

## 4. Quellen (belegt, HTTP 200)

- EU-KI-VO Art. 14(5): „at least two natural persons" (Annex III 1(a)):
  https://ai-act-service-desk.ec.europa.eu/en/ai-act/article-14
- EU-KI-VO (VO (EU) 2024/1689): https://eur-lex.europa.eu/eli/reg/2024/1689/oj

## 5. Präzisierung (Auftrag vs. Belegt)

Art. 14(5) gilt nur für **Annex III 1(a)** (Remote-Biometrie) + Ausnahmen; die
Anwendung auf **alle** Rekursionen ist **Auftrag**.

## 6. Guardrails

- `AGENTS.md` geändert **auf ausdrücklichen menschlichen Auftrag** (§9.3).
- Distinkte Personen erzwungen; kein Auto-approve.

## 7. Freigabe

**Freigabe-Status für π₁:** `pending` (menschliche Freigabe ausstehend).
