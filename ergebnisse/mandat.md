# Mandats-Formalisierung (EU Fidacy / Futurium)

> Datum: 2026-10-02 · Auftrag: „Implementiere die Mandats-Formalisierung … nach EU
> Fidacy (Futurium). Erfindung ist verboten." · Lab-Prinzip §6 · Human-Gate §9.

## 1. Quelle (HTTP 200, geprüft 2026-10-02)

| Quelle | Wörtlicher Beleg | Link |
|---|---|---|
| Futurium (EU-Kommission), „Verifiable Authority Boundaries for AI Agents and Autonomous Systems" (Lucas Lima) | „A bounded mandate … **the agent cannot create for itself**"; „A mandate can specify the permitted action, protected resource, recipient, amount or value ceiling, time window, use count and delegation depth."; „The outcome is **ALLOW, REVIEW or DENY**. An allowed consequential action can receive a short-lived, signed, single-use grant." | https://futurium.ec.europa.eu/en/apply-ai-alliance/community-content/verifiable-authority-boundaries-ai-agents-and-autonomous-systems |
| Futurium (EU-Kommission), „Europe's Next AI Infrastructure: Authority Before Action" | „A stronger architecture begins with a mandate issued by an **accountable person or organization**. That mandate defines the agent's identity, permitted actions, accessible resources, destination, financial limits, purpose, duration, **approval thresholds**, delegation rights and revocation status." | https://futurium.ec.europa.eu/en/apply-ai-alliance/community-content/europes-next-ai-infrastructure-authority-action |
| Fidacy-Docs: Mandate | „**A child mandate may only reduce its parent's authority.**"; „Per-transaction cap and a **step-up threshold** (above it, a human confirms)." | https://fidacy.com/docs/mandate |
| Fidacy-Docs: Action Authority | „A `DENY` is still signed, but it never includes a grant."; „a child agent can only **attenuate, never expand**" | https://fidacy.com/docs/action-authority |
| Fidacy-Docs: Concepts | `principal`, `agent`, `mandate`, `assessment`, `policy`; hash-chained evidence | https://fidacy.com/docs/concepts |

## 2. Flow (wörtlich aus der Quelle)

```text
Mandate  →  Independent Decision  →  Execution Grant  →  Evidence
(bounded)   (außerhalb des Modells)  (kurzlebig, single-use)  (hash-verkettet)
```

## 3. Umsetzung

| Datei | Inhalt |
|---|---|
| `data/memory/mandate.md` | **Mandat-Artefakt**: Identität (Batnini → knowledge-agent), erlaubte Aktionen, Ressourcen, Limits (10 %/1000×/12 Monate), Approval-Schwellen, Regel, Evidence |
| `data/memory/mandate.py` | `Mandate` (frozen) · `MandateRegistry.issue/attenuate/expand/revoke` · `assess()` → ALLOW/REVIEW/DENY · `issue_grant()` · `redeem()` (replay/expiry) · `evidence()` (Hash-Kette) |
| `tests/test_mandate.py` | 9 Tests, 100 % Line+Branch |

**Kernregel (Quelle wörtlich):** „A child mandate may only reduce its parent's
authority" → `attenuate()` erzwingt Teilmengen (Aktionen, Ressourcen, Limits);
`expand()` des Agenten liefert **immer** `{"allowed": false, "gate": "ask"}`.

## 4. Compare-Beleg (Selbsttest, extern)

```text
make test → 198 passed · 1747/1747 Statements · 392/392 Branches = 100,00 %

Mandats-Erweiterung simuliert:
  registry.expand(m, agent="knowledge-agent", amount_limit=999.0)
  → {"allowed": false, "gate": "ask",
     "reason": "Agent kann sein Mandat nicht erweitern – nur der Principal (Mensch) (§9)"}

attenuate() lehnt Erweiterungen ab (MandateError):
  Aktionen ⊄ Eltern · Ressourcen ⊄ Eltern · amount_limit> · max_uses> ·
  valid_until> · approval_threshold> · delegation_depth=0
```

## 5. Gate / Freigabe (§9)

- **Neue Quelle** (Futurium/Fidacy): §9 verlangt Human-Gate → durch den Auftrag erteilt.
- **Interface-Erweiterung** (neues Modul `mandate.py`): additiv, kein bestehender
  Prozess importiert es → keine Verhaltensänderung.
- **Kein `self_update`:** Der Agent erweitert sein Mandat nie selbst; Erweiterung
  nur durch den Principal → Gate `ask`.
- Provenienz: diese Datei + `data/memory/mandate.md`.

## 6. Ehrliche Grenzen

- Die konkreten Werte (10 %, 1000 Uses, 12 Monate, Schwellen) sind **Auftrag**
  (`data/memory/mandate.md`), nicht aus der Quelle; die Quelle liefert die
  **Struktur** (Felder, Flow, „attenuate never expand").
- Kein echtes kryptografisches Signatur-/JWK-Verfahren (die Quelle nennt Ed25519/JWS);
  hier nur SHA-256-Digest + Hash-Kette als **Nachweis-Mechanik**.
- Keine Anbindung an einen echten Executor (Payment/Email) — reine Software-Mechanik.
