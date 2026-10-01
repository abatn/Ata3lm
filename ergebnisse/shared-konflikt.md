# Shared Memory – Konfliktauflösung konkretisiert

> Datum: 2026-10-01
> Status: **Belegt** (Frontier/Mechanik-Idee) + **Auftrag** (konkrete Strategie)
> Prinzip: Keine Erfindungen (§6).
> Code: `data/memory/shared/shared_memory.py` · Doku: `data/memory/shared/README.md`
> Hinweis: Auftrag nennt `data/memory/shared_memory.py`; real: `data/memory/shared/shared_memory.py`.

## 1. Quellen (verifiziert, HTTP 200)

| Quelle | Kernaussage (wörtlich/nah) | Link |
|---|---|---|
| **Memory Survey** §6.5 | „shared vs. private memory boundaries"; „**consistency under concurrent writes**" | https://arxiv.org/abs/2603.07670 |
| **Memory Survey** §9.6 | „access control over shared stores, **consensus protocols for concurrent writes** … distributed memory with **merge semantics** … **wide open**" | https://arxiv.org/abs/2603.07670 |
| **Memory Survey** (Write-Path) | „**source attribution** (user statement > agent inference)" → Trust-Ordnung | https://arxiv.org/abs/2603.07670 |
| **Collaborative Memory** | private/shared-Tiers, asymmetrische Zugriffskontrolle, Provenienz | https://arxiv.org/abs/2505.18279 |
| **Graphiti** | bi-temporal: invalidieren statt löschen | https://arxiv.org/abs/2501.13956 |

> **Belegt:** Frontier-Direktion + „consistency under concurrent writes" + „source
> attribution" (Trust-Ordnung). **Auftrag:** die konkrete Auflösungsstrategie
> (Trust-Grenze, Supersede-Marker, Schema) — die Survey nennt sie „wide open".

## 2. Die drei Konkretisierungen

### 2.1 Konflikterkennungs-Trigger — **Belegt**
Zwei Agenten schreiben **unterschiedliche Werte für denselben Key**.
`conflict = cur is not None and cur.value != value`.
(Quelle: Survey §6.5 „consistency under concurrent writes".)

### 2.2 Auflösungsstrategie — Versionierung + Supersede + Trust-Score
- **Versionierung:** jeder Write → `v1, v2, …`.
- **Supersede-Marker:** alter Eintrag `status: superseded` + `invalid_at` (kein Löschen).
- **Trust-Score:** Agent mit **niedrigerem** Trust überschreibt **nicht**
  (`new_trust < cur.trust` → `phase: resolution`, aktueller Wert bleibt).
  Trust = Auftrag, motiviert durch Survey „source attribution".

### 2.3 Kollisionsvalidierung — **vor jedem Write** (Konsistenzprüfung)
`validate_write(agent, key, value)`: ACL → nicht-leer → **Schema** (erlaubte Werte).
Schlägt sie fehl → `phase: validation`, **kein** Write.

## 3. Ablauf

```text
write(agent, key, value)
   │
   ▼  Kollisionsvalidierung (VOR dem Write)
   [ACL? · nicht-leer? · Schema?] ── fail ─► {phase: validation, ok: false}
   ▼
   Trigger: existiert anderer Wert für key?
   ├─ nein ─────────────────────────────────► commit (vN)
   └─ ja ─► Trust: new_trust < cur.trust?
              ├─ ja  ─► {phase: resolution, ok: false}  (aktueller Wert bleibt)
              └─ nein ─► Supersede-Marker + commit (vN+1)
```

## 4. Selbsttest (reale Ausgabe)

```text
=== [1] Trigger: zwei Agenten, gleicher Key, verschiedene Werte ===
  agentA (trust 0.9) write -> ok, v1, conflict False
=== [2] Auflösung: Trust-Score (niedrigerer Trust verliert) ===
  agentB (trust 0.5) write -> ok=False, phase=resolution, "niedrigerer Trust 0.5 < 0.9; aktueller Wert bleibt"
  agentA (trust 0.9) write -> ok, v2, conflict True, superseded 1
=== [3] Kollisionsvalidierung VOR dem Write ===
  Schema-Verstoß (config.mode=turbo) -> ok=False, phase=validation, "Wert 'turbo' nicht erlaubt (Schema: ['fast','safe'])"
  leerer Wert                        -> ok=False, phase=validation, "leerer Wert"
=== [4] Sync + Historie ===
  v1 solver.current_version = berechne_durchschnitt | agentA (trust 0.9) | superseded
  v2 solver.current_version = berechne_median        | agentA (trust 0.9) | valid | supersedes v1
```

**Ergebnis:** Konflikt erkannt; niedriger Trust verliert; höherer/gleicher Trust
supersedet (Versionierung + Marker); Validierung blockt Schema-/Leer-Writes.

## 5. Status-Trennung

| Aussage | Status |
|---|---|
| Konsistenz bei Concurrent Writes nötig | **Belegt** (Survey §6.5) |
| Merge-Semantik/Consensus „wide open" | **Belegt** (Survey §9.6) |
| Trust-Ordnung (source attribution) | **Belegt** (Survey) |
| Supersede statt löschen | **Belegt** (Graphiti) |
| Konkrete Trigger/Trust-Grenze/Schema | **Auftrag** |

## 6. Dateien

| Artefakt | Art |
|---|---|
| `data/memory/shared/shared_memory.py` | erweitert (Trust + Kollisionsvalidierung) |
| `data/memory/shared/README.md` | erweitert |
| `ergebnisse/shared-konflikt.md` | neu (dieses Dokument) |
| `ergebnisse/rekursion/021-*.md` | Provenienz |

## 7. Quellen (HTTP 200, 2026-10-01)

- https://arxiv.org/abs/2603.07670 (Memory Survey §6.5/§9.6)
- https://arxiv.org/abs/2505.18279 (Collaborative Memory)
- https://arxiv.org/abs/2501.13956 (Graphiti)
