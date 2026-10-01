# Shared Memory – Trust-basierte Supersession (Write-Time)

> Datum: 2026-10-01
> Status: **Belegt** (Mechanik) + **Auftrag** (Trust-Grenze)
> Prinzip: Keine Erfindungen (§6).
> Code: `data/memory/shared/shared_memory.py`
> Hinweis: Auftrag nennt `data/memory/shared_memory.py`; real: `data/memory/shared/shared_memory.py`.

## 1. Quellen (verifiziert, HTTP 200)

| Quelle | Kernaussage (wörtlich/nah) | Link |
|---|---|---|
| **LatticeMind** | „handles contradiction at **write time**"; Item-Status `{Proposed, Confirmed, **Contested, Superseded**}`; „symbolic checker" vor dem Write; „the stronger claim is confirmed and the weaker one is **preserved as SUPERSEDED or CONTESTED** with full provenance" | https://arxiv.org/abs/2608.08236 |
| **Governed Collaborative Memory** | „accepted record enters the shared layer with provenance, version lineage, and **supersede-not-erase semantics**" | https://arxiv.org/abs/2605.04264 |
| **Memory Survey** | „consistency under concurrent writes"; „source attribution" (Trust-Ordnung) | https://arxiv.org/abs/2603.07670 |

## 2. Formalisierung

```text
write(agent, key, value)
   │
   ▼  [1] Kollisionsvalidierung (symbolischer Checker, VOR dem Write)
   [ACL · nicht-leer · Schema] ── fail ─► {phase: validation}
   ▼
   [2] Write-Time-Konfliktlösung (Trust-Score)
   cur = aktueller CONFIRMED-Eintrag
   ├─ kein Konflikt            ─► status=confirmed
   └─ Konflikt (cur.value ≠ value)
        ├─ new_trust > cur.trust ─► cur.superseded_by = vN ; neu = confirmed
        ├─ new_trust < cur.trust ─► neu.status=superseded, neu.superseded_by = cur.v
        └─ Gleichstand           ─► neu.status = contested
```

- **Status (LatticeMind):** `confirmed | superseded | contested`.
- **Supersession:** Der unterlegene Eintrag wird `superseded` + **`superseded_by`** gesetzt
  — **nicht gelöscht** (Governed Collaborative Memory: „supersede-not-erase").

## 3. Selbsttest (reale Ausgabe) — 2 Agenten, gleicher Key

```text
=== [1] Write-Time-Konfliktlösung (Trust-Score entscheidet) ===
  agentA(0.5) -> outcome=confirmed       current=berechne_durchschnitt (v1)
  agentB(0.9) -> outcome=superseded_old  current=berechne_median (v2)
  agentC(0.3) -> outcome=superseded_new  current=berechne_median (v2)
=== [2] Kollisionsvalidierung VOR dem Write ===
  Schema-Verstoß -> phase=validation, "Wert 'turbo' nicht erlaubt"
  leerer Wert    -> phase=validation, "leerer Wert"
=== [3] Historie: Supersession (kein Löschen) ===
  v1 berechne_durchschnitt | agentA(0.5) | superseded | superseded_by v2
  v2 berechne_median        | agentB(0.9) | confirmed  | supersedes v1
  v3 berechne_summe         | agentC(0.3) | superseded | superseded_by v2
```

**Ergebnis:** Trust entscheidet (0.9 > 0.5); unterlegene Werte bleiben als
`superseded` mit **`superseded_by`** erhalten (kein Löschen); Validierung blockt
Schema-/Leer-Writes.

## 4. Status-Trennung

| Aussage | Status |
|---|---|
| Write-Time-Konfliktlösung | **Belegt** (LatticeMind) |
| Item-Status (confirmed/contested/superseded) | **Belegt** (LatticeMind) |
| Supersede-not-erase / version lineage | **Belegt** (Governed Collaborative Memory) |
| Symbolischer Checker vor dem Write | **Belegt** (LatticeMind) |
| Trust-Score als Entscheider + konkrete Grenze | **Auftrag** (Proxy für „evidence-weighted") |

## 5. Dateien

| Artefakt | Art |
|---|---|
| `data/memory/shared/shared_memory.py` | erweitert (Status + `superseded_by`) |
| `ergebnisse/shared-supersession.md` | neu (dieses Dokument) |
| `ergebnisse/rekursion/026-*.md` | Provenienz |

## 6. Quellen (HTTP 200, 2026-10-01)

- https://arxiv.org/abs/2608.08236 (LatticeMind)
- https://arxiv.org/abs/2605.04264 (Governed Collaborative Memory)
- https://arxiv.org/abs/2603.07670 (Memory Survey)
