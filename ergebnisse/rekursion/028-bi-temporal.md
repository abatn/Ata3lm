# 028 – Bi-temporale Semantik (valid time × transaction time)

> Datum: 2026-10-01
> Rekursionstiefe: System-Iteration (Memory), nicht Solver-t
> Phase: Konstrukt (bi-temporaler Store) + Revise (Ontologie §E)
> Auslöser: menschlicher Auftrag vom 2026-10-01.

## 1. Zustand vorher / nachher

| Aspekt | vorher | nachher |
|---|---|---|
| Zeitachsen | einfache Gültigkeitsfenster (Graphiti) | **valid time × transaction time** explizit |
| Update | supersede (invalid_at) | + **retroaktiv** (valid_to + superseded_at) |
| Abfrage | – | **as_of(valid, knowledge)** + world/knowledge-as-of |

## 2. Änderungen

- `data/memory/bi_temporal.py` (neu): `BiTemporalStore`, `Fact`, `assert_fact`, `as_of`,
  `world_state_as_of`, `knowledge_as_of`.
- `data/memory/tier1-base/ontology.md` §E + `versions/v3` (Snapshot).
- `ergebnisse/bi-temporal.md`.

## 3. Compare-Beleg (externes Signal)

`python3 data/memory/bi_temporal.py` (reale Ausgabe):
- Globex → valid 2024-01-01..2024-03-01, transaction 2024-01-01..2024-03-15 (superseded).
- Moonshot → valid_from 2024-03-01, supersedes F0.
- as_of(2024-02-01, 2024-02-01) → Globex; as_of(2024-02-01, 2024-04-01) → kein Fakt.

## 4. Quellen (belegt, HTTP 200)

- Engram (arXiv:2606.09900; github.com/ly-wang19/engram): valid/transaction time, supersedes, as-of.
- Graphiti (arXiv:2501.13956): bi-temporal.

## 5. Abgrenzung (Auftrag)

Feldnamen/Datentypen + Store-Implementierung = **Auftrag**; Mechanik = **Belegt**.

## 6. Guardrails

- `AGENTS.md` unverändert; tier1-base versioniert (v3-Snapshot); kein Löschen (invalidate).

## 7. Freigabe

**Freigabe-Status für π₁:** `approved: Batnini, 2026-10-01`.
