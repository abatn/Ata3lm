# Multi-Agent Memory Sharing (Shared Tier + Sync)

> Datum: 2026-10-01
> Status: **Belegt** (Konzept/Frontier) + **Auftrag** (Implementierung)
> Prinzip: Keine Erfindungen (§6).
> Code: `data/memory/shared/shared_memory.py` · Doku: `data/memory/shared/README.md`

## 1. Quellen (verifiziert, HTTP 200)

| Quelle | Kernaussage (wörtlich/nah) | Link |
|---|---|---|
| **Memory Survey** (§6.5) | „shared vs. private memory boundaries"; „consistency under concurrent writes"; „either all memory is shared … or each agent maintains its own store … **Neither extreme is satisfactory**." | https://arxiv.org/abs/2603.07670 |
| **Memory Survey** (§9.6) | „Multi-agent memory governance … **access control over shared stores, consensus protocols for concurrent writes** … distributed memory with **merge semantics** … **remain wide open**." | https://arxiv.org/abs/2603.07670 |
| **Collaborative Memory** | private/shared-Tiers, asymmetrische Zugriffskontrolle, unveränderliche Provenienz | https://arxiv.org/abs/2505.18279 |
| **Graphiti** (Projekt) | bi-temporal: alte Fakten invalidieren statt löschen | https://arxiv.org/abs/2501.13956 |

> **Belegt ist** die Frontier-Direktion (Survey §6.5/§9.6: Multi-Agent-Memory ist
> „wide open"). Die **konkrete** Tier-/ACL-/Sync-Mechanik ist **Auftrag**.

## 2. Shared Tier + Sync-Mechanismus

```text
Agenten (agentA, agentB, agentC)
        │  read / write (ACL)
        ▼
┌──────────────────────────────────────────────┐
│  data/memory/shared/  – SharedTier            │
│  key -> Entry{value, version, writer, ts,     │
│               status(valid|superseded)}       │
│  + History (append-only, bi-temporal)         │
└──────────────────────────────────────────────┘
        │  sync()
        ▼
  Konflikt-Erkennung: gleicher Key, verschiedene Werte
  → prefer newest; alter Eintrag superseded (NICHT gelöscht)
```

- **Shared Tier:** gemeinsamer Key-Store (`SharedTier`).
- **Versionierung:** jeder Write → `v1, v2, …`.
- **Konflikt-Erkennung:** gleicher Key, verschiedene Werte (verschiedene Agenten).
- **Konfliktlösung:** `prefer newest` (Memory Survey) + **Supersede-Marker**
  (bi-temporal, Graphiti) — kein Löschen.
- **ACL:** private/shared-Grenzen je Agent/Key.

## 3. Test: 2 Agenten, dieselbe Shared Tier (reale Ausgabe)

```text
=== [1] Zwei Agenten schreiben denselben Key (konkurrierend) ===
  agentA write -> {'ok': True, 'version': 1, 'conflict': False, 'superseded': None}
  agentB write -> {'ok': True, 'version': 2, 'conflict': True, 'superseded': 1}

=== [2] Sync: Konflikt-Erkennung ===
  {'conflicts': [{'key': 'solver.current_version',
                  'values': ['berechne_durchschnitt', 'berechne_median'],
                  'resolved_to': 'berechne_median',
                  'rule': 'prefer newest (Memory Survey)'}], 'keys': 1}

=== [3] Lesen (Sicht je Agent) ===
  agentA read: {'ok': True, 'value': 'berechne_median', 'version': 2, 'writer': 'agentB'}
  agentC read (kein Recht): {'ok': False, 'reason': "agentC: kein Leserecht ..."}
  agentC write (kein Recht): {'ok': False, 'reason': "agentC: kein Schreibrecht ..."}

=== [4] Versionierte Historie ===
  v1 solver.current_version = berechne_durchschnitt | agentA | superseded
  v2 solver.current_version = berechne_median | agentB | valid | supersedes v1
```

**Ergebnis:** Zwei Agenten schreiben konkurrierend → Konflikt **erkannt** und
per `prefer newest` gelöst (alter Eintrag superseded); ACL blockt unbefugten
Zugriff; Historie versioniert.

## 4. Status-Trennung

| Aussage | Status |
|---|---|
| Multi-Agent-Memory-Sharing als Frontier | **Belegt** (Survey §6.5/§9.6) |
| shared vs. private boundaries; concurrent writes | **Belegt** (Survey) |
| ACL / private/shared-Tiers | **Belegt** (Survey; Collaborative Memory) |
| Konfliktlösung „prefer newest" | **Belegt** (Survey) |
| Versionierung + Sync-Mechanik | **Auftrag** |

## 5. Grenze (ehrlich)

- **Ein-Prozess-Simulation** — kein verteiltes System, kein echter Consensus.
  Die Survey nennt Consensus/merge **wide open**; hier nur lokal modelliert.
- Kein Löschen: Konflikte invalidieren (superseded).

## 6. Dateien

| Artefakt | Art |
|---|---|
| `data/memory/shared/shared_memory.py` | neu (SharedTier) |
| `data/memory/shared/README.md` | neu |
| `ergebnisse/multi-agent-sharing.md` | neu (dieses Dokument) |
| `ergebnisse/rekursion/018-*.md` | Provenienz |

## 7. Quellen (HTTP 200, 2026-10-01)

- https://arxiv.org/abs/2603.07670 (Memory Survey §6.5/§9.6)
- https://arxiv.org/abs/2505.18279 (Collaborative Memory)
- https://arxiv.org/abs/2501.13956 (Graphiti)
