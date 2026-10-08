# PROPOSAL C — N3: Flush nur mit Erfolgsbeleg + Archivschutz

> **Phase 0 — NUR Entwurf (Auftrag „Knowledge-Agent härten N1–N8"). NICHT implementieren
> vor §9 `approved` (≥ 2 Personen, §9.3). Befund-Quelle (verbindlich): Audit b09a0a9.**

## 0. Metadaten

| Feld | Wert |
|---|---|
| Datum | 2026-10-08 |
| Iteration | `t → t+1` (geplant, Phase 2) |
| Phase | Konstrukt (Entwurf) |
| Betroffenes Artefakt | `data/memory/slow_consolidation.py` |
| Komponenten-Typ | Code |
| Autor | Knowledge-Agent (Auftrag N1–N8) |

### Befund (Soll/Ist, Audit b09a0a9 — verbindlich)

**N3 · P1 · Flush ohne Erfolgsbeleg + Archivschutz.**
Datei: `slow_consolidation.py` ~`:205` (`state_path` optional) · ~`:238` (`flush`).
**Soll:** `state_path` verpflichtend; `*.superseded-*` nie löschen.
**Ist:** `flush(keys, tier3_dir, *, state_path=None)`: ohne `state_path` ist `done = None` ⇒ **jeder** Key wird gelöscht, **ohne** Erfolgsbeleg (der Guard greift nur, wenn `state_path` gesetzt ist). Zweitens enthält der Löschpfad keine Prüfung auf Archivnamen — wird ein Archivname als Key übergeben (z. B. aus einem Dateinamen rekonstruiert), wird die `*.superseded-*`-Historie gelöscht (§10.7: „invalidieren, nicht löschen").
Repro (Phase 2): `test_flush_requires_success_evidence` · `test_flush_preserves_archive_when_called_with_filename`.

## 1. Ziel `g`

- Ziel: Kein Flush ohne verbuchten Konsolidierungserfolg; Archiv-Stände (`*.superseded-*`) bleiben unter allen Umständen erhalten.
- Task-Input: Repro-Fälle aus `tests/test_network_boundaries.py` (Audit b09a0a9).

## 2. Baseline (vorher)

| Feld | Wert |
|---|---|
| `π` (Modell/Policy) | Rev. `b09a0a9`, `slow_consolidation.py` |
| Score (externes Signal) | `0/2` = `0 %` — **gemäß Audit-Befund** (Repro-Tests entstehen mit Phase 2) |
| Signal-Quelle | 2 benannte Repro-Fälle (Audit) |
| Drift-Referenz | Git-Hash `b09a0a9` |

## 3. Änderung (Diff-Skizze, line-level — Richtung, kein Final-Patch)

```diff
-def flush(keys, tier3_dir, *, state_path=None) -> dict:
-    """... Ist `state_path` gesetzt, werden nur dort verbuchte Keys entfernt ..."""
-    done = set(_load_state(state_path)["consolidated"]) if state_path is not None else None
+def flush(keys, tier3_dir, *, state_path) -> dict:
+    """N3: state_path ist VERPFLICHTEND – kein Flush ohne Erfolgsbeleg (§10.3)."""
+    if state_path is None:
+        return {"ok": False, "removed": [], "reason": "Flush ohne Erfolgsbeleg verweigert (N3/§10.3)"}
+    done = set(_load_state(state_path)["consolidated"])
     ...
     for k in keys or []:
+        if ".superseded-" in k:            # N3: Archiv = Historie, NIE löschen (§10.7)
+            blocked.append(k)
+            continue
-        if done is not None and k not in done:
+        if k not in done:                  # ohne Beleg: blocked, kein Löschen
             blocked.append(k)
             continue
```

- Geänderte Komponenten: **1**.
- Interface-Änderung? **ja** — `state_path` wird verpflichtend (Signatur) ⇒ **immer Human-Gate (§9)**.

## 4. Score-Änderung

| Testfall | Kriterium | vorher | nachher (Ziel) |
|---|---|---|---|
| `test_flush_requires_success_evidence` | ohne Beleg kein Löschen | fail (Audit-Ist) | pass |
| `test_flush_preserves_archive_when_called_with_filename` | `*.superseded-*` bleibt erhalten | fail (Audit-Ist) | pass |

- **Score vorher:** `0/2` = `0 %` (Audit-Befund) · **Score nachher (Ziel):** `2/2` = `100 %`
- **Δ Score (Ziel):** `+100` Prozentpunkte

## 5. Drift (Δ zur Baseline)

- **Definition (Auftrag):** `Δ = geänderte Zeilen / Gesamtzeilen des Artefakts`.
- **Drift-Wert (Schätzung):** ~8–12/292 ≈ **3–4 %**.
- **Drift-Bound:** 10 % (Default, §9.1c). **Überschritten?** nein (Schätzung; Messung in Phase 2).

## 6. Evidenz / Quellen

- Quelle 1: AGENTS.md §10.3 („erfolgreich konsolidiert ⇒ flush; fehlgeschlagen ⇒ bleibt") — intern.
- Quelle 2: AGENTS.md §10.7 („supersedieren = invalidieren, NICHT löschen") — intern.
- Interne Referenz: `data/memory/slow_consolidation.py:205-260` · Audit b09a0a9.

## 7. Gate-Entscheidung (§9)

| Bedingung | Wert | Ergebnis |
|---|---|---|
| Score | `0 % → 100 %` (Ziel) | ask |
| Neue Quelle? | nein | — |
| Interface-Änderung? | **ja** (Signatur) | **ask** |
| Drift ≤ Bound? | ja (≈ 4 % ≤ 10 %) | — |

- **Gate-Ergebnis:** **`ask`** (Phase 2 nur nach §9 `approved`, ≥ 2 Personen).

## 8. Freigabe

- Status: `pending`
- Human-Gate-Referenz: Rekursion entsteht mit Phase-2-Umsetzung.
