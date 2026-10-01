# inference-003 — Negativtest: Prämisse ohne Quellen-Link

```text
Regel-ID:     R1 (angewendet, aber Prämisse unbelegt)
Regel:        Supersede-Regel (Graphiti)
Input-Triples:
  - Solver finde_minimum --supersedes--> Solver berechne_median
    (Quelle: FEHLT)
Output-Triples:
  - (nicht materialisiert — Inferenz abgelehnt)
Quelle:       (fehlt)
Status:       rejected
Grund:        Mindestens eine Prämisse hat KEINEN Quellen-Link →
              Regel darf nicht angewendet werden. Ergebnis `rejected`, NICHT `belegt`.
```

## Zweck

Negativtest: Eine ansonsten gültig aussehende Prämisse wird **ohne Quellen-Link**
eingespeist. Der Skill muss sie als `rejected` dokumentieren (nicht als `belegt`).

- Erwartung: `rejected`.
- Tatsächlich: `rejected` (Grund: fehlender Quellen-Link).
- Damit ist Guardrail 3 des Skills (`Jede Inferenz braucht Prämissen-Beleg +
  Quellen-Link, sonst rejected`) erfüllt.
