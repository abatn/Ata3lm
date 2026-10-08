# Rekursion 076: N1 — Provenienz + Datenwrite getrennte Transaktion (write_gateway)

> Datum: 2026-10-08 · Phasen: Konstrukt → Akt → Observe → Compare (echte Tests).
> **Befund-Quelle (verbindlich): Audit b09a0a9** (Datei `tests/test_network_boundaries.py`).
> N-Nummerierung = **Audit** (NICHT Rekursion 062–063).
> Ziel `g` (§6/K3): Provenienz + Datenwrite = EINE Transaktion.
> Akzeptanz: `provenance_log` = Verzeichnis ⇒ **kein Write**.
> Auftrag: „Knowledge-Agent härten — N1–N8 (Revision b09a0a9)", Phase 1
> (autonom, reine Mechanik; KEIN Commit).
> Status: **umgesetzt** (kein Interface) · Freigabe: **`pending`** — Review im Gesamt-STOPP.

## 1. Soll/Norm (Audit + Fundstellen)

| Feld | Wert (Audit b09a0a9, verbindlich) |
|---|---|
| Befund | **N1 · P1 · Provenienz + Datenwrite getrennte Transaktion** |
| Datei | `data/memory/write_gateway.py` (store_file append ~`:504` · store append ~`:756`; Write via `_commit` ~`:712`) |
| **Soll** | Log-Fehler ⇒ **Rollback** ODER **kein Write**. |
| **Ist** | `IsADirectoryError` nach Write, kein Record. |
| Repro | `test_gateway_provenance_io_failure_cannot_leave_unrecorded_write` |

Norm: K3 (kein Write ohne Beleg), `AGENTS.md` §6/§9.2c; Transaktions-Design
R08/A3 (`_commit`-Docstring); K2 „EIN Mutation-Punkt" (`write_gateway.py:169`).

## 2. Befund (Ist ≠ Soll)

- `store()` schrieb via `_commit` (`:712`) und protokollierte **erst danach**
  (`:756`; ebenso `:733` im R09-Teilpfad; `store_file` `:504`). Log nicht
  beschreibbar ⇒ **`IsADirectoryError` nach Write, kein Record** (K3-Bruch).
- Reproduziert mit echten Fehlern (kein Mock): Log = Verzeichnis; Log-Elternpfad =
  Datei (`NotADirectoryError`); alter Code wirft die Exception **nach** der Mutation.

## 3. Änderung (Diff-Skizze)

| Datei | Inhalt |
|---|---|
| `data/memory/write_gateway.py` | `_commit(..., append_targets=())`: R08-Vorprüfung + A3-Backups/Rollback decken **auch** das Provenienz-Log ab; Record-Zeile wird **in derselben Transaktion** geappendet (Daten + Provenienz: beide oder keins). Format-Zwilling `_record_line()` (byte-gleich zu `provenance.append_record`, gegen Format-Drift getestet). `store_file`/`store` reichen `(log, _record_line(record))` durch; die separaten `append_record`-Aufrufe (inkl. `:733`) entfallen. `steps`-Reihenfolge + Ergebnis-Dicts unverändert. |
| `tests/test_network_boundaries.py` (neu) | Kanonische Repro-Datei des Audit: N1-Abnahmefall (4 echte Fehlerfälle: beide Pfade × Verweigern/Rollback) + Repro-Inventar N2–N8. |
| `tests/test_write_gateway.py` | +5 feinkörnige Tests (Verweigern ×2, Rollback, R09-Teilpfad genau-einmal, Format-Zwilling). |

```diff
-    res = _commit(write_targets, now, supersede_existing=(cls == "write-update"))
+    log = Path(provenance_log) if provenance_log is not None else Path(tier3_dir) / "provenance.jsonl"
+    res = _commit(write_targets, now, supersede_existing=(cls == "write-update"),
+                  append_targets=[(log, _record_line(record))])
     ...
-    provenance.append_record(log, record)
```

- Geänderte Komponenten: **1** (`write_gateway.py`; Tests ergänzt).
- Interface-Änderung? **nein** (Signaturen `store_file`/`store` + Ergebnis-Dicts
  unverändert; `_commit`/`_record_line` intern).

## 4. Real vs. offen (ehrlich)

- **Real:** echte Dateisystem-Fehler (House-Style, keine Mocks); Red→Green belegt
  (alter Code: Repro rot inkl. unkontrollierter Exception; neuer Code: grün).
- **Grenzen:** `shared_tier`-Schritt bleibt außerhalb der Transaktion (bewusst
  unverändert, eigener `ok`-Rückgabewert); R08+A3 decken TOCTOU wie im
  bestehenden A3-Design ab.

## 5. Compare / Beleg (externes Signal: echte Tests)

```text
Rot (alter Code): pytest tests/test_network_boundaries.py --no-cov  -> 1 failed
    (Fall 3/4: NotADirectoryError nach Write, Datei bleibt NEU ohne Record)
Grün (neuer Code): pytest tests/test_network_boundaries.py --no-cov -> 1 passed
Feinkorn: pytest tests/test_write_gateway.py tests/test_e2e_theta_probe.py --no-cov
                                                          -> 51 passed
Ruff check + format --check (alle geänderten Dateien)     -> All checks passed
Repo-Checks: check_md_links/check_artifacts/check_secrets  -> 0 Fehler, 0 Treffer
Gesamtlauf: pytest -m "not network and not live"           -> 598 passed, 2 deselected,
                                                              exit 0 · Coverage 100.00 %
```

## 6. §9-Gate

**kein Gate nötig** — Phase 1 (Auftrag): reine Mechanik, keine Interface-/Format-
Änderung, kein `self_update` an Originaldateien (`AGENTS.md`/`tier1-base` unberührt
⇒ kein `versions/vN`). **Kein Commit** (G6).
**Freigabe-Status: `pending`** — menschliche Review-Freigabe im Gesamt-STOPP.
