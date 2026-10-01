# Memory-Lifecycle: Konsolidierung, Forgetting, Konfliktlösung

> Datum: 2026-10-01
> Status: **Belegt** (Mechanik) + **Auftrag** (Schwellen/Implementierung)
> Prinzip: Keine Erfindungen (§6). Jede Aussage mit Quelle oder als Auftrag.
> Code: `data/memory/reflective_agent.py` · Ontologie: `data/memory/tier1-base/ontology.md` §D

## 1. Quellen (verifiziert, HTTP 200)

| Quelle | Kernaussage (wörtlich/nah) | Link |
|---|---|---|
| **HeLa-Mem** (ACL 2026) | **Hub Detection:** `D(v_i) = Σ w_ij > δ_hub` → Hebbian Distillation (Cluster → semantischer Eintrag). **Adaptive Forgetting:** „flagged for removal only if it **simultaneously** satisfies three criteria: (1) total edge weight below **δ_prune**, (2) inactive duration exceeds **δ_age**, (3) **zero recent access**." | https://arxiv.org/abs/2604.16839 |
| **Memory Survey** | „Robust systems need **temporal versioning (prefer the newest record)**, source attribution, **contradiction detection (flag conflicts for resolution)**, and periodic consolidation"; Konsolidierung = Episoden → semantisches Wissen | https://arxiv.org/abs/2603.07670 |
| **Graphiti** (Projekt) | bi-temporal: „old facts are **invalidated — not deleted**" | https://arxiv.org/abs/2501.13956 |

> **Ehrliche Zuordnung:** Konsolidierung + Forgetting = **HeLa-Mem**. Die
> **Konfliktlösung** (Supersede) stammt aus der **Memory Survey** (+ Graphiti
> bi-temporal), **nicht** aus HeLa-Mem.

## 2. Die drei Operatoren

### 2.1 Konsolidierung — **Belegt** (HeLa-Mem)
- **Regel:** Hub `D(v) > δ_hub` → Hub + stark verbundene Nachbarn werden per
  LLM zu einem **deklarativen semantischen Eintrag** synthetisiert.
- **Implementierung:** `detect_hubs()`, `distill()`, `write_semantic()`,
  `update_index()` (`reflective_agent.py`).
- **Ablage:** `knowledge/structured/distilled-hub-<id>.md` + `tier2-index/hub-index.md`.

### 2.2 Forgetting — **Belegt** (HeLa-Mem), 3 Bedingungen
- **Regel:** Ein Knoten wird **nur** vergessen, wenn **alle drei** gelten:
  `weight < δ_prune` **und** `age > δ_age` **und** `access == 0`.
- **Korrektur:** Die frühere `detect_forgetting` prüfte nur **eine** Bedingung
  (weight) — jetzt **drei** (quellenkonform).
- **Implementierung:** `detect_forgetting(graph, now_days)`.
- **Parameter:** `δ_prune=0.05`, `δ_age=60` Tage (**Auftrag**); `τ=60` (**belegt**).

### 2.3 Konfliktlösung — **Belegt** (Memory Survey + Graphiti)
- **Regel:** Bei Widerspruch (gleiches Subjekt+Prädikat, anderes Objekt) wird der
  alte Fakt **superseded** (`status: superseded`, `invalid_at` gesetzt) — **nicht
  gelöscht**; der neue Fakt gilt (prefer newest).
- **Implementierung:** `resolve_conflict(facts, s, p, o, now_iso)`.

## 3. Selbsttest (reale Ausgabe)

```json
{
  "consolidation": { "hubs": ["hub_n2"], "action": "hebbian-distillation" },
  "forgetting": {
    "forgotten": ["isolated_n5"],
    "conditions": "weight<delta_prune AND age>delta_age AND access==0"
  },
  "conflict": {
    "conflict": true,
    "superseded": [{"s":"solver","p":"current_version","o":"berechne_durchschnitt",
                    "status":"superseded","valid_from":"2026-09-30","invalid_at":"2026-10-01"}],
    "added": {"s":"solver","p":"current_version","o":"berechne_median",
              "status":"valid","valid_from":"2026-10-01","invalid_at":null}
  }
}
```

- **Konsolidierung:** Hub `hub_n2` (D=1.8) → destilliert.
- **Forgetting:** `isolated_n5` (weight 0.01, 100 Tage inaktiv, 0 Zugriffe) → vergessen.
- **Konflikt:** `current_version` wechselt `durchschnitt` → `median`; alter Fakt
  superseded, neuer valid.

## 4. Status-Trennung

| Aussage | Status |
|---|---|
| Hub-Konsolidierung (Hebbian Distillation) | **Belegt** (HeLa-Mem) |
| Adaptive Forgetting = 3 Bedingungen gleichzeitig | **Belegt** (HeLa-Mem) |
| Konfliktlösung via Supersede / prefer newest | **Belegt** (Memory Survey + Graphiti) |
| Schwellen δ_prune/δ_age | **Auftrag** |
| Implementierung in `reflective_agent.py` | **Auftrag** |

## 5. Dateien

| Artefakt | Art |
|---|---|
| `data/memory/reflective_agent.py` | erweitert (3-Bed.-Forgetting, `resolve_conflict`, `simulate_lifecycle`) |
| `data/memory/tier1-base/ontology.md` §D | erweitert |
| `data/memory/tier1-base/versions/v2/` | Snapshot (Versionierungs-Regel) |
| `ergebnisse/memory-lifecycle.md` | neu (dieses Dokument) |
| `ergebnisse/rekursion/017-*.md` | Provenienz |

## 6. Quellen (HTTP 200, 2026-10-01)

- https://arxiv.org/abs/2604.16839 (HeLa-Mem)
- https://aclanthology.org/2026.acl-long.625/ (HeLa-Mem, ACL 2026)
- https://arxiv.org/abs/2603.07670 (Memory Survey)
- https://arxiv.org/abs/2501.13956 (Graphiti, bi-temporal)
