# Bi-temporale Semantik für Memory-Einträge

> Datum: 2026-10-01
> Status: **Belegt** (Mechanik) + **Auftrag** (Implementierung)
> Prinzip: Keine Erfindungen (§6).
> Code: `data/memory/bi_temporal.py` · Ontologie: `data/memory/tier1-base/ontology.md` §E

## 1. Quellen (verifiziert, HTTP 200)

| Quelle | Kernaussage (wörtlich/nah) | Link |
|---|---|---|
| **Engram** | Fakten tragen zwei Zeitachsen: **valid time** (`valid_at`/`invalid_at`, „when the claim is true in the world") und **transaction time** (`created_at`/`expired_at`, „when we learned or retracted it"), plus `supersedes`; „never hard-delete a contradicted fact — invalidate it … and keep the history"; Read-Path: bi-temporaler **as-of**-Filter | https://arxiv.org/abs/2606.09900 · https://github.com/ly-wang19/engram |
| **Graphiti** (Projekt) | bi-temporal (Fakten mit Validitätsfenstern) | https://arxiv.org/abs/2501.13956 |

## 2. Zwei Zeitstempel

| Achse | Felder | Frage |
|---|---|---|
| **valid time** | `valid_from` / `valid_to` | Wann gilt der Fakt **in der Welt**? |
| **transaction time** | `recorded_at` / `superseded_at` | Wann wurde er **gespeichert/verworfen**? |

## 3. Retroaktives Update + As-of-Abfragen

```text
assert_fact(s, p, o_new, valid_from, recorded_at)
   │  Widerspruch? (gleiches s,p, anderes o)
   └─ ja: alter Fakt → valid_to = o_new.valid_from, superseded_at = recorded_at  (NICHT gelöscht)
          neuer Fakt → valid_from, recorded_at, supersedes = alter Fakt

as_of(valid_time, knowledge_time)  → „was glaubten wir am knowledge_time über valid_time?"
world_state_as_of(valid_time)      → nur valid time (was war wahr)
knowledge_as_of(knowledge_time)    → nur transaction time (was glaubten wir)
```

## 4. Selbsttest (reale Ausgabe) — Änderung simulieren

```text
=== [1] Retroaktives Update (Ivan: Globex → Moonshot) ===
  assert (Ivan works_at Globex)   -> index=0
  assert (Ivan works_at Moonshot) -> index=1, superseded=0
=== [2] Beide Zeitstempel je Fakt ===
  F0: Ivan works_at Globex
       valid_time:        2024-01-01 .. 2024-03-01
       transaction_time:  2024-01-01 .. 2024-03-15
  F1: Ivan works_at Moonshot
       valid_time:        2024-03-01 .. offen
       transaction_time:  2024-03-15 .. offen  (supersedes F0)
=== [3] As-of-Time-Abfragen ===
  as_of(valid=2024-02-01, knowledge=2024-02-01) -> Ivan works_at Globex
  as_of(valid=2024-04-01, knowledge=2024-04-01) -> Ivan works_at Moonshot
  as_of(valid=2024-02-01, knowledge=2024-04-01) -> (kein Fakt)
  world_state_as_of(2024-02-01) -> ['Globex']
  knowledge_as_of(2024-04-01)   -> ['Moonshot']
```

**Ergebnis:** Alter Fakt bleibt mit `valid_to`+`superseded_at` (nicht gelöscht); neuer mit
`valid_from`+`supersedes`; as-of-Abfragen liefern den jeweils korrekten Fakt.

## 5. Status-Trennung

| Aussage | Status |
|---|---|
| Zwei Zeitachsen (valid + transaction) | **Belegt** (Engram) |
| Retroaktives Update, invalidieren statt löschen | **Belegt** (Engram) |
| As-of-Time-Abfragen | **Belegt** (Engram) |
| Feldnamen/Datentypen, Store-Implementierung | **Auftrag** |

## 6. Dateien

| Artefakt | Art |
|---|---|
| `data/memory/bi_temporal.py` | neu (`BiTemporalStore`) |
| `data/memory/tier1-base/ontology.md` §E | erweitert |
| `data/memory/tier1-base/versions/v3/` | Snapshot (Versionierungs-Regel) |
| `ergebnisse/bi-temporal.md` | neu (dieses Dokument) |
| `ergebnisse/rekursion/028-*.md` | Provenienz |

## 7. Quellen (HTTP 200, 2026-10-01)

- https://arxiv.org/abs/2606.09900 (Engram)
- https://github.com/ly-wang19/engram
- https://arxiv.org/abs/2501.13956 (Graphiti)
