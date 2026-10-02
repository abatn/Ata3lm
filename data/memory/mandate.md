# data/memory/mandate.md — Mandat des Knowledge-Agenten

> Quelle (HTTP 200, geprüft 2026-10-02): EU Fidacy (Futurium, EU-Kommission) +
> Fidacy-Docs. Wörtlich: „A bounded mandate … the agent cannot create for itself";
> „a child agent can only attenuate, never expand"; „A mandate can specify the
> permitted action, protected resource, recipient, amount or value ceiling, time
> window, use count and delegation depth."
> Flow: `Mandate → Independent Decision → Execution Grant → Evidence`.
> Lab-Prinzip §6: nur was in der Quelle steht; die konkreten Werte sind Auftrag.

## 1. Identität

| Feld | Wert |
|---|---|
| `principal` (verantwortliche Person/Org) | **Batnini** |
| `agent` (Workload-Identität) | `knowledge-agent` |
| `mandate_id` | `mandate-kag-0001` |
| `parent_id` | — (Wurzelmandat) |
| `delegation_depth` | **0** (keine Weiterdelegation) |

## 2. Erlaubte Aktionen (allowlist)

- `read:repo`, `write:ergebnisse`, `write:data/memory`, `write:knowledge/structured`
- `run:tests`, `git:commit` (nur nach §9-Gate)

## 3. Ressourcen (allowlist)

- `data/memory/**`, `ergebnisse/**`, `knowledge/structured/**`, `tests/**`, `connectors/**`
- **Nicht** erlaubt: externe Endpoints schreiben, Secrets lesen, `AGENTS.md` ändern
  (nur mit Human-Freigabe).

## 4. Limits

| Limit | Wert |
|---|---|
| `amount_limit` (max. Änderung/Einheit) | **10 %** pro Iteration (Drift-Bound §9.1c) |
| `max_uses` | 1000 |
| `valid_from` / `valid_until` | 2026-10-02 → **2027-10-02** (12 Monate) |
| `approval_threshold` | **immer** für: neue Quelle, Interface-Änderung, `self_update`, Drift > 10 % |

## 5. Approval-Schwellen (§9/§9.3)

- `ALLOW` → autom. (Score ≥ 95 %, alle Stufen „sicher")
- `REVIEW` → **Human-Gate** (Grenzfall, neue Quelle, Interface, `self_update`)
- `DENY` → blockiert
- Zwei-Personen-Verifikation (`Batnini` + `taouefik`) für `approved`.

## 6. Regel (wörtlich aus der Quelle)

> „A child mandate may only reduce its parent's authority." — Ein Agent kann sein
> Mandat **nicht erweitern**; nur der **Principal (Mensch)** darf ein neues Mandat
> ausstellen. Erweiterungsversuch → **Gate `ask`** (kein `self_update` ohne `approved`).

## 7. Evidence

Jede Entscheidung/Grant wird hash-verkettet protokolliert (`mandate.py`,
`evidence()`): `record → hash(prev + canonical(record))` — nachträgliche Änderung
erkennbar. Implementierung + Test: `ergebnisse/mandat.md`.
