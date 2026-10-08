# PROPOSAL B — N2: Konsolidierung an Inhalt/Modell binden (statt nur Key)

> **Implementiert (Phase 2) — §9-Freigabe `approved` (Batnini + Taoufik, 2026-10-08).**
> Umsetzung + Belege: `ergebnisse/rekursion/078-n2-n3-konsolidierung-flush.md`.
> Befund-Quelle (verbindlich): Audit b09a0a9. (Ursprünglich Phase-0-Entwurf.)

## 0. Metadaten

| Feld | Wert |
|---|---|
| Datum | 2026-10-08 |
| Iteration | `t → t+1` (geplant, Phase 2) |
| Phase | Konstrukt (Entwurf) |
| Betroffenes Artefakt | `data/memory/slow_consolidation.py` · `data/memory/fast_write_router.py` |
| Komponenten-Typ | Code (Memory-State-Schema) |
| Autor | Knowledge-Agent (Auftrag N1–N8) |

### Befund (Soll/Ist, Audit b09a0a9 — verbindlich)

**N2 · P1 · Konsolidierung nicht an Inhalt/Modell gebunden.**
Datei: `slow_consolidation.py` ~`:129` (`collect_pending`) · `fast_write_router.py` ~`:111` (`discard_if_consolidated`).
**Soll:** State = `{key, fact_sha256, modell/adapter-version, probe_passed}`; Hash prüfen, nicht nur Key.
**Ist:** State ist eine reine Key-Liste (`_load_state(state_path)["consolidated"]`); `collect_pending` und `discard_if_consolidated` entscheiden über `key in done`. Ein **geänderter** Fakt zum selben Key bleibt nach alter Konsolidierung versteckt; der Router verwirft eine geänderte Antwort zum alten Key.
Repro (Phase 2): `test_consolidated_old_key_does_not_hide_updated_fact` · `test_router_does_not_discard_changed_answer_for_old_key`.

## 1. Ziel `g`

- Ziel: Konsolidierungs-State bindet an **Inhalt** (`fact_sha256`) + Modell/Adapter-Version + `probe_passed`; ein geänderter Fakt wird wieder konsolidierbar, eine geänderte Router-Antwort nicht mehr verworfen.
- Task-Input: Repro-Fälle aus `tests/test_network_boundaries.py` (Audit b09a0a9).

## 2. Baseline (vorher)

| Feld | Wert |
|---|---|
| `π` (Modell/Policy) | Rev. `b09a0a9`, `slow_consolidation.py`/`fast_write_router.py` |
| Score (externes Signal) | `0/2` = `0 %` — **gemäß Audit-Befund** (nicht lokal gemessen; Repro-Tests entstehen mit Phase 2) |
| Signal-Quelle | 2 benannte Repro-Fälle (Audit) |
| Drift-Referenz | Git-Hash `b09a0a9` |

## 3. Änderung (Diff-Skizze, line-level — Richtung, kein Final-Patch)

```diff
 # slow_consolidation.py (~:129 ff., collect_pending)
-    done = set(_load_state(state_path)["consolidated"]) if state_path is not None else set()
+    state = _load_state(state_path) if state_path is not None else {}
     ...
-        # Filter: key in done  ->  skip
+        # N2-Filter: nur skippen wenn (key, fact_sha256, modell, probe_passed) passt
+        if _consolidated_for(state, key, sha, MODEL_VERSION) and _probe_passed(state, key):
+            continue
 # mark_consolidated: State-Eintrag wird zu
-    {key: ...}  ->  {"key": key, "fact_sha256": sha, "model": MODEL_VERSION, "probe_passed": bool}
 # fast_write_router.py (~:111, discard_if_consolidated)
-    done = set(...); if key in done: return non-write
+    # N2: Hash-Vergleich statt Key-Match; ungleicher Hash -> KEIN Discard
+    if not _same_fact_and_model(state, key, fact, MODEL_VERSION): return None
```

- Geänderte Komponenten: **2** (Begründung: ein State-Schema, zwei Konsumenten — DREvo-Einzelkomponentenregel gilt pro Modul).
- Interface-Änderung? **ja** — State-Schema (Datei-Inhalt) + evtl. Signaturen ⇒ **immer Human-Gate (§9)**.

## 4. Score-Änderung

| Testfall | Kriterium | vorher | nachher (Ziel) |
|---|---|---|---|
| `test_consolidated_old_key_does_not_hide_updated_fact` | geänderter Fakt erscheint wieder als pending | fail (Audit-Ist) | pass |
| `test_router_does_not_discard_changed_answer_for_old_key` | geänderte Antwort wird nicht verworfen | fail (Audit-Ist) | pass |

- **Score vorher:** `0/2` = `0 %` (Audit-Befund) · **Score nachher (Ziel):** `2/2` = `100 %`
- **Δ Score (Ziel):** `+100` Prozentpunkte (externe Messung erst nach Phase-2-Umsetzung)

## 5. Drift (Δ zur Baseline)

- **Definition (Auftrag):** `Δ = geänderte Zeilen / Gesamtzeilen des Artefakts`.
- **Drift-Wert (Schätzung):** ~20/292 (`slow_consolidation`) + ~12/420 (`fast_write_router`) ≈ **4,5 %** (Summe 712 Zeilen).
- **Drift-Bound:** 10 % (Default, §9.1c). **Überschritten?** nein (Schätzung; gemessen wird in Phase 2).

## 6. Evidenz / Quellen

- Quelle 1: AGENTS.md §10.3 (Write-Back/„nur nach Erfolg") — intern, bereits Norm.
- Quelle 2: arXiv:2608.22215 §3.4 (Router suppresses redundant writes) — **bereits im Projekt** (§10).
- Interne Referenz: `data/memory/slow_consolidation.py:129-150,205-235` · `data/memory/fast_write_router.py:103-131` · Audit b09a0a9.

## 7. Gate-Entscheidung (§9)

| Bedingung | Wert | Ergebnis |
|---|---|---|
| Score | `0 % → 100 %` (Ziel) | ask (nach Compare neu bewerten) |
| Neue Quelle? | nein | — |
| Interface-Änderung? | **ja** (State-Schema) | **ask** |
| Drift ≤ Bound? | ja (≈ 4,5 % ≤ 10 %) | — |

- **Gate-Ergebnis:** **`ask`** (Phase 2 nur nach §9 `approved`, ≥ 2 Personen).

## 8. Freigabe

- Status: **`implementiert (approved)`** — §9-Freigabe: Batnini + Taoufik, 2026-10-08.
- Human-Gate-Referenz: `ergebnisse/rekursion/078-n2-n3-konsolidierung-flush.md`.
