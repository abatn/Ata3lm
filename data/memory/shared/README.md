# data/memory/shared – Multi-Agent Shared Memory Tier

> Lab-Prinzip, MD-first. Gemeinsame Schicht, auf die **mehrere Agenten** lesend
> und schreibend zugreifen. Lokal, keine Cloud.

## 1. Zweck (Belegt: Memory Survey)

Die **Memory Survey** (arXiv:2603.07670) nennt Multi-Agent-Memory als Frontier:
- §6.5 „Multi-agent collaboration": die zwei Kernprobleme sind
  **„shared vs. private memory boundaries"** und
  **„consistency under concurrent writes"**.
- §9.6 „Multi-agent memory governance": „access control over shared stores,
  consensus protocols for concurrent writes … distributed memory with **merge
  semantics** … remain **wide open**."

Ergänzend: **Collaborative Memory** (arXiv:2505.18279) — zwei Tiers
(**private** / **shared**), asymmetrische Zugriffskontrolle, unveränderliche
Provenienz.

## 2. Aufbau

```text
data/memory/shared/
├── README.md            # dieses Dokument
└── shared_memory.py     # SharedTier (ACL, Versionierung, Sync/Konflikt)
```

## 3. Mechanik (Belegt + Auftrag)

| Aspekt | Regel | Status |
|---|---|---|
| **Shared Tier** | gemeinsamer Key-Store, mehrere Agenten | Belegt (Survey §6.5) |
| **Private vs. Shared** | Zugriffskontrolle (ACL) je Agent/Key | Belegt (Survey §6.5; Collaborative Memory) |
| **Versionierung** | jeder Write erzeugt Version `v1, v2, …` | Auftrag |
| **Konflikt-Erkennung** | gleicher Key, verschiedene Werte (versch. Agenten) | Belegt (Survey §6.5 „concurrent writes") |
| **Konfliktlösung** | **prefer newest**; alter Eintrag **superseded** (nicht gelöscht) | Belegt (Survey: prefer newest; Graphiti bi-temporal) |
| **Sync** | erkennt Konflikte über die Historie | Auftrag |

## 4. API

- `SharedTier(acl)` — ACL: `agent -> {"read": set, "write": set}` (`"*"` = alle).
- `write(agent, key, value)` → `{ok, version, conflict, superseded}`
- `read(agent, key)` → `{ok, value, version, writer}` (oder Grund bei fehlendem Recht)
- `sync()` → `{conflicts: [...], keys}`
- `dump(path)` → JSONL-Historie

## 5. Grenze / Ehrlichkeit

- **Ein-Prozess-Simulation** (kein verteiltes System, kein echter Consensus).
  Die Survey nennt Consensus/merge **wide open** — hier nur lokal modelliert.
- Kein Löschen: Konflikte invalidieren (superseded), Historie bleibt.

## 6. Quellen (HTTP 200, 2026-10-01)

- https://arxiv.org/abs/2603.07670 (Memory Survey §6.5/§9.6)
- https://arxiv.org/abs/2505.18279 (Collaborative Memory)
- https://arxiv.org/abs/2501.13956 (Graphiti, bi-temporal – supersede statt löschen)
