# Shared-Memory-Verifikation (ACL · Trust · Sync · Supersession)

> Datum: 2026-10-04 · Status: **Belegt** (Quelle) + **Auftrag** (Repo-Zuordnung).
> Ziel `g`: prüfen, welche Shared-Memory-Komponenten im Repo real existieren — mit `Datei:Zeile`.
> Lab-Prinzip §6: keine Erfindung; Lücken werden **klar** benannt.

## 1. Quelle (verifiziert)

- **Collaborative Memory: Multi-User Memory Sharing in LLM Agents with Dynamic Access
  Control** — Rezazadeh, Li, Lou, Zhao, Wei, Bao (**ICML 2025**, arXiv:2505.18279).
  Wörtlich: „asymmetric, time-evolving access controls encoded as **bipartite graphs** linking
  users, agents, and resources"; „two memory tiers: (1) **private memory** … (2) **shared
  memory**"; „each fragment carries **immutable provenance attributes**"; „**read policies** …";
  „**write policies** determine fragment retention and sharing".

## 2. Verifikations-Tabelle (`Datei:Zeile`)

| Komponente | Status | Beleg |
|---|---|---|
| **ACL** | **vorhanden** | `data/memory/shared/shared_memory.py:70` (`def _can(agent,key,mode)`), `:65` (`self.acl`), `:77` (Write-Check), `:134` (Read-Check), `:73` (`"*" in allowed or key in allowed`) |
| **Trust** | **vorhanden** | `shared_memory.py:46` (`Entry.trust`), `:66` (`self.trust`), `:93` (`new_trust`), `:105` („stärkerer Trust gewinnt"), `:142` (Trust-Ausgabe) |
| **Sync** | **vorhanden** | `shared_memory.py:146` (`def sync()`), `:164` (`def dump(path)`) |
| **Supersession** | **vorhanden** | `shared_memory.py:105-109` (`status="superseded"`, `superseded_by`, `supersedes`), `:115`, `:49`, `:159` (Regel „versioning + trust-supersession") |
| **Integration** | **vorhanden** | `data/memory/pipeline.py:38,41` (`export_shared` → `tier.dump`), `data/memory/connector_binding.py:97` (`shared_memory.SharedTier()`), Test `tests/test_pipeline.py:230` |

## 3. Details

- **ACL:** `_can(agent, key, mode)` liest `self.acl.get(agent)` und prüft `allowed` je `read`/`write`;
  Write verweigert bei fehlender Berechtigung (`validate_write`).
- **Trust:** je Agent eine Trust-Zahl; beim Write in den `Entry` geschrieben; **stärkerer Trust
  gewinnt** (`:105`).
- **Sync:** `sync()` löst Konflikte über Version + Trust; `dump(path)` persistiert (JSONL).
- **Supersession:** Der unterlegene Eintrag wird **nicht gelöscht**, sondern markiert
  (`status="superseded"`, `superseded_by=v`) — analog AGENTS.md §10.7 (invalidieren, nicht löschen).

## 4. Fazit (ehrlich)

- **ACL, Trust, Sync, Supersession** sind **real implementiert** (`shared_memory.py`) + verdrahtet
  (`pipeline.export_shared`).
- **Nicht implementiert (Lücke):** die **bipartiten Zugriffsgraphen** des Papers
  (user↔agent, agent↔resource) und der **private Tier** — das Repo nutzt ein **vereinfachtes
  `acl`-dict** + einen Shared-Tier. Die Zuordnung ist **Auftrag**, kein 1:1-Paper-Nachbau.

## 5. Gate (§9)

- Reine **Verifikation + Doku** (keine Code-/Interface-Änderung) → kein Human-Gate nötig.
- Guardrail 3: Provenienz `ergebnisse/rekursion/054-shared-memory-verifikation.md`.
- Guardrail 6: kein Commit ohne Erlaubnis. §9.1b: `AGENTS.md` unverändert.
