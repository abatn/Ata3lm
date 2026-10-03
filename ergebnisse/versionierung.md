# Versionierung & Rollback (Aufgabe 2)

> Datum: 2026-10-01
> Status: **Belegt** (Reversibilität ist governance-relevant) + **Auftrag** (Mechanik)
> Quelle (Belegt): arXiv:2604.14717 – „Layered Mutability: Identity Drift and
> Governance in Self-Modifying AI Agents" (schwache Reversibilität → hohe
> Governance-Last; Hysterese-Ratio 0,68) — https://arxiv.org/abs/2604.14717
> Auftrag: Jede Änderung an `AGENTS.md` und `data/memory/tier1-base/` wird
> versioniert; Rollback ist ein Einzeiler. (Projekt-Betriebsregel.)

## 1. Zweck

Selbstmodifizierende Systeme brauchen einen Rückweg. Belegt ist, dass
**schwache Reversibilität** die Governance-Last erhöht und ein sichtbarer
„Revert" das Verhalten nicht immer wiederherstellt (Hysterese). Deshalb wird
jede Änderung an den beiden kritischen Artefakten versioniert.

- `AGENTS.md` (Gesetz)
- `data/memory/tier1-base/` (Identität, Ontologie, Kernbeziehungen, Episodic Graph)

## 2. Zwei Mechaniken (beide, wie beauftragt)

### Mechanik A — Git

- Repository: `/home/opc/knowledge-agent` (lokal initialisiert 2026-10-01).
- Remote: `https://github.com/abatn/Ata3lm` (privat).
- Branch: `main`.

### Mechanik B — `versions/vN/` (Datei-Snapshot, MD-first)

- Ablage: `data/memory/tier1-base/versions/vN/`
- Inhalt je Version: Kopie von `identity.md`, `ontology.md`,
  `core-relations.md`, `episodic_graph.json`.
- `v1` = Stand 2026-10-01 (Baseline).
- Die **lebenden** Dateien bleiben direkt in `data/memory/tier1-base/`
  (kein Pfad-Umbau → keine Interface-Änderung; bestehende Referenzen in
  `knowledge/` und `data/memory/README.md` bleiben gültig).

## 3. Rollback (Einzeiler)

```bash
# A) Gesamter Repo-Stand (Git)
git revert <commit>            # erzeugt Gegen-Commit (bevorzugt)
# oder, wenn kein Gegen-Commit gewünscht:
git reset --hard <commit>

# B) Nur Tier-1-Memory (Datei-Snapshot)
cp data/memory/tier1-base/versions/v1/*.md data/memory/tier1-base/
cp data/memory/tier1-base/versions/v1/episodic_graph.json data/memory/tier1-base/
```

> Hinweis: `git revert` ist gegenüber `reset --hard` zu bevorzugen, weil es die
> Historie erhält (Nachvollziehbarkeit). `reset --hard` verwirft Commits.

## 4. Aktueller Stand (2026-10-01)

| Ereignis | Hash / Ref |
|---|---|
| Baseline-Commit (Knowledge-Agent) | `0327ada` |
| Merge Remote-Initial (LICENSE, README) | `75b0a89` |
| Push nach `origin/main` | `2bf32b8..75b0a89` |
| Datei-Snapshot Tier-1 | `data/memory/tier1-base/versions/v1/` |
| Snapshot zu Iteration 031 (Gesetz-Änderung §10.2, `approved` 2026-10-01) | `data/memory/tier1-base/versions/v4/` |
| Snapshot 2026-10-03 (EOL-Modell-Fix §10.2 super-120b→ultra-550b, `approved` Batnini) | `data/memory/tier1-base/versions/v5/` (+ `AGENTS.md`) |
| Snapshot 2026-10-03 (Write-Aktion §10.2/§10.7 `apply_write_action`, `approved` Batnini A+D) | `data/memory/tier1-base/versions/v6/` (+ `AGENTS.md`) |
| Snapshot 2026-10-03 (GAAMA/Kairos-Connector, `approved` Batnini) | `data/memory/tier1-base/versions/v7/` (+ `AGENTS.md`) |
| Snapshot 2026-10-03 (Git-Sperre Guardrail 6: kein `add`/`commit`/`push` ohne Erlaubnis) | `data/memory/tier1-base/versions/v8/` (+ `AGENTS.md`) |
| Snapshot 2026-10-03 (Guardrail 7: echte Verifikation, Fakes verboten) | `data/memory/tier1-base/versions/v9/` (+ `AGENTS.md`) |

## 5. Regel für neue Versionen

1. Änderung an `AGENTS.md` oder `tier1-base/` → **Human-Gate `approved`** (§9).
2. Vor der Änderung: `mkdir -p .../versions/v(N+1)` + Kopie des Vorher-Stands
   (oder Commit der Änderung in Git).
3. Nach der Änderung: Commit + (optional) Push.
4. Diff + Score-Änderung + Drift dokumentieren (siehe `proposal-template.md`).

## 6. Quellen (keine Erfindungen)

- https://arxiv.org/abs/2604.14717 — Layered Mutability (Reversibilität, Hysterese)
- Projekt-intern: `AGENTS.md` §9.1(b); `skills/recursive-improve/` (Revise/self_update)
