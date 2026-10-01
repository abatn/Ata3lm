# 018 – Multi-Agent Memory Sharing (Shared Tier + Sync)

> Datum: 2026-10-01
> Rekursionstiefe: System-Iteration (Memory-Sharing), nicht Solver-t
> Phase: Konstrukt (neue Shared-Tier) + Revise (Sync)
> Auslöser: menschlicher Auftrag vom 2026-10-01.

## 1. Zustand vorher / nachher

| | vorher | nachher |
|---|---|---|
| Memory-Tiers | tier1/2/3 (Single-Agent) | + **shared/** (Multi-Agent) |
| Konflikt bei Concurrent Writes | nicht adressiert | erkannt + `prefer newest` (Supersede) |
| Zugriffskontrolle | – | ACL (private/shared) |

## 2. Änderungen

- `data/memory/shared/shared_memory.py` (neu): `SharedTier` mit ACL,
  Versionierung (`v1,v2,…`), Sync/Konflikt-Erkennung, Supersede (kein Löschen).
- `data/memory/shared/README.md` (neu).
- `ergebnisse/multi-agent-sharing.md` (neu).
- `.gitignore`: Runtime-Store ausgenommen.

## 3. Compare-Beleg (externes Signal)

`python3 data/memory/shared/shared_memory.py` (reale Ausgabe):
- agentA v1 = `berechne_durchschnitt`; agentB v2 = `berechne_median`.
- Sync: **Konflikt erkannt** → `resolved_to: berechne_median` (prefer newest).
- ACL: agentC (kein Recht) → read/write abgelehnt.
- Historie: v1 superseded, v2 valid (supersedes v1).

## 4. Quellen (belegt)

- Memory Survey (arXiv:2603.07670) §6.5 (shared vs. private; concurrent writes),
  §9.6 (Multi-agent memory governance — „wide open").
- Collaborative Memory (arXiv:2505.18279): private/shared-Tiers, ACL.
- Graphiti (arXiv:2501.13956): bi-temporal (supersede statt löschen).

## 5. Abgrenzung (Auftrag)

- Versionierungs-/Sync-/ACL-Mechanik = **Auftrag** (Survey nennt es „wide open",
  schreibt keine konkrete Mechanik vor).
- **Ein-Prozess-Simulation** (kein verteiltes System/Consensus).

## 6. Guardrails

- `AGENTS.md` unverändert; kein Löschen (Supersede); fail-soft-frei (reine Bibliothek).

## 7. Freigabe

**Freigabe-Status für π₁:** `pending` (menschliche Freigabe ausstehend).
