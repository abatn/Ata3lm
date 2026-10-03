# FWR-Write-Aktion (3 Klassen → echte Writes)

> Datum: 2026-10-03 · Lab-Prinzip §6 (keine Erfindungen) · Human-Gate §9.
> Modul: `data/memory/fast_write_router.py` (`apply_write_action`).

## 1. Quellen (getrennt: Paper vs. Auftrag)

| Was | Quelle | Status |
|---|---|---|
| Taxonomie `non-write` / `write-new` / `write-update` (verhaltensbasiert) | Dual-Layer Agentic Memory, **arXiv:2608.22215 §3.1** | **Belegt** |
| Dual-Layer: parametrisch Θ + extern E, Slow Consolidation | arXiv:2608.22215 (Abstract/§3.4) | **Belegt** |
| **Binärer** Router „write or discard", 3 Klassen sind *Labels* | arXiv:2608.22215 **§3.3** („bypasses explicit three-way classification") | **Belegt** |
| Write-**Ziel**-Zuordnung (welcher Ordner) | **AGENTS.md §10.7** | **Auftrag** (Projekt) |
| Gate: neue Quelle / `self_update` → ask | **AGENTS.md §9, §10.4** | **Auftrag** |

**Ehrlicher Caveat:** Das Paper routet operational **binär** (write/discard). Die
3-Klassen-**Aktionen** stammen aus AGENTS.md §10.7 (Auftrag), nicht aus dem Paper.
Nichts wird als Paper-Claim ausgegeben, was nicht dort steht.

## 2. Write-Aktion (AGENTS.md §10.7, wörtlich)

| Klasse | Aktion | Ziel |
|---|---|---|
| **non-write** | nur Historie | `ergebnisse/` (`*.non-write.jsonl`) — **kein** Memory-Write |
| **write-new** | neuer Fakt | `knowledge/structured/` **+** `data/memory/tier3-working/` |
| **write-update** | aktualisieren + supersedieren | `knowledge/structured/` aktualisieren · alten `tier1-base/`-Eintrag **invalidieren, NICHT löschen** |
| unbekannt | kein Write | `gate=ask` (§10.4) |

**Gate:** `non-write` → `none` · `write-new` → `ask` (neue Quelle) · `write-update` → `ask` (`self_update`).

Supersede (invalidate, nicht löschen): alter Inhalt wird nach
`<key>.superseded-<ts>.md` **archiviert**, der neue Fakt aktiv geschrieben und ein
`supersede.jsonl`-Record angelegt.

## 3. Test (3 Klassen → echte Writes, offline)

`tests/test_fwr_write.py` — 6 Tests, kein Netz (reine Dateisystem-Logik):

```text
non-write    -> nur ergebnisse/*.non-write.jsonl, KEIN structured/tier3
write-new    -> knowledge/structured/<key>.md + tier3-working/<key>.md
write-update -> structured aktualisiert + tier1: alt archiviert (.superseded-*.md), supersede.jsonl
unbekannt    -> ok=False, gate=ask, keine Writes
```

## 4. Simulationslauf (echte Writes, Demo-Verzeichnis)

```text
non-write   -> {"ok":true,"action":"non-write","gate":"none","written":["ergebnisse/was-ist-die-hauptstadt-von-frankreich.non-write.jsonl"],"superseded":null}
write-new   -> {"ok":true,"action":"write-new","gate":"ask","written":["knowledge/structured/was-ist-die-hauptstadt-von-xylophonia.md","tier3-working/was-ist-die-hauptstadt-von-xylophonia.md"],"superseded":null}
write-update-> {"ok":true,"action":"write-update","gate":"ask","written":["knowledge/structured/was-ist-die-hauptstadt-von-frankreich.md"],"superseded":true}

--- Dateibaum ---
  ergebnisse/was-ist-die-hauptstadt-von-frankreich.non-write.jsonl
  knowledge/structured/was-ist-die-hauptstadt-von-frankreich.md
  knowledge/structured/was-ist-die-hauptstadt-von-xylophonia.md
  tier1-base/supersede.jsonl
  tier1-base/was-ist-die-hauptstadt-von-frankreich.md
  tier1-base/was-ist-die-hauptstadt-von-frankreich.superseded-1728000000.md
  tier3-working/was-ist-die-hauptstadt-von-xylophonia.md
```

## 5. Suite-Beleg

```text
make test -> 244 passed · Coverage 100,00 % (Line+Branch) · ruff clean
```

## 6. Human-Gate §9

- **write-new** (neue Quelle, §10.4) und **write-update** (`self_update`, §9) liefern
  `gate=ask` — Speicherung erst nach Freigabe.
- Änderung additiv (neue Funktion), kein Löschen am Hub-Pfad; Hub-Abweichung
  bleibt dokumentiert in `ergebnisse/verbindungen-diagramm.md` §6.
- Provenienz: `ergebnisse/rekursion/035-experience-route.md` (A+D).
