# Rekursion 078: N2 + N3 — Konsolidierung an Inhalt binden · Flush nur mit Erfolgsbeleg

> Datum: 2026-10-08 · Phasen: Konstrukt → Akt → Observe → Compare (echte Tests).
> **Befund-Quelle (verbindlich): Audit b09a0a9** (Datei `tests/test_network_boundaries.py`).
> N-Nummerierung = **Audit** (NICHT Rekursion 062–063).
> Ziel `g` (§10.3): (N2) ein konsolidierter Fakt darf eine **neue** Antwort nicht
> ausblenden; (N3) kein Flush ohne **Erfolgsbeleg**, Historien bleiben.
> Auftrag: „Knowledge-Agent härten — N1–N8 (Revision b09a0a9)", **Phase 2** (Fixes N2+N3).
> Status: **umgesetzt** · §9-Status: **`approved` (Batnini + Taoufik, 2026-10-08)** ·
> **kein Commit** (G6).

## 1. Soll/Norm (Audit + Fundstellen)

| Feld | Wert (Audit b09a0a9, verbindlich) |
|---|---|
| Befund N2 | **N2 · P1 · Konsolidierung nicht an Inhalt/Modell gebunden** |
| Befund N3 | **N3 · P1 · Flush ohne Erfolgsbeleg + Archivschutz** |
| Datei | `data/memory/slow_consolidation.py` (`collect_pending`, `mark_consolidated`, `flush`) · `data/memory/fast_write_router.py` (`discard_if_consolidated`) |
| **Soll N2** | State = `{key, fact_sha256, modell/adapter-version, probe_passed}`; Hash prüfen, nicht nur Key. Geänderter Fakt (gleicher Key) ⇒ wieder `pending`; geänderte Router-Antwort ⇒ nicht verworfen. |
| **Soll N3** | `flush` nur mit belegtem Erfolg; `*.superseded-*` (Historie) nie löschen. |
| Repro N2 | `test_consolidated_old_key_does_not_hide_updated_fact` · `test_router_does_not_discard_changed_answer_for_old_key` |
| Repro N3 | `test_flush_requires_success_evidence` · `test_flush_preserves_archive_when_called_with_filename` |

Norm: `AGENTS.md` §10.3 (Write-Back, „erfolgreich ⇒ Flush / sonst bleibt") ·
§10.7 („supersedieren = invalidieren, NICHT löschen") · §9.2c (nur trusted+verified)
· §6 (kein Write ohne Beleg). Paper: arXiv:2608.22215 §3.4 (bereits im Gesetz, §10).

## 2. Befund (Ist ≠ Soll)

- **N2:** State war eine reine Key-Liste (`{"consolidated":[keys]}`). `collect_pending`
  filterte per `key in done`; `discard_if_consolidated` matchte per Key. Ein Fakt mit
  **neuem Hash** unter **altem Key** (write-update + Retraining-Kandidat) wurde damit
  dauerhaft als „konsolidiert" versteckt — die neue Fassung erschien nie wieder als
  `pending` und wurde vom Router als `non-write` verworfen.
- **N3:** `flush(..., state_path=None)` setzte `done = None` ⇒ **jeder** Key wurde
  gelöscht, **ohne** Erfolgsbeleg (Guard griff nur **mit** `state_path`). Zusätzlich
  hatte der Löschpfad keinen Archiv-Schutz; ein aus einem Dateinamen rekonstruierter
  Key kann einen `*.superseded-*`-Stand treffen (§10.7-Bruch).

## 3. Änderung (Diff-Skizze, line-level)

```diff
 # slow_consolidation.py
 def _load_state(state_path):            # N2: {consolidated:[keys], entries:{key:{fact_sha256,model,probe_passed}}}
-    return {"consolidated": [...]}      # altes Format bleibt lesbar ⇒ Hash „unbekannt"
+    return {"consolidated": [...], "entries": {...}}
+def _is_consolidated(entry, current_sha):   # neu: Hash-Gleichheit, Legacy ⇒ Key-Match
 # collect_pending
-    if key in done: continue
+    if key in done and _is_consolidated(entries.get(key), provenance.content_hash(fact)): continue
 # mark_consolidated(keys, state_path, *, success=True, facts=None, model=None, probe_passed=True)
+    entry["fact_sha256"] = provenance.content_hash(str(facts[k]))   # N2-Inhaltsbindung
 # flush
-    done = ... if state_path is not None else None      # ohne Beleg ⇒ löschte alles
+    if state_path is None: return {"ok": False, ..., "blocked": raw}   # N3: verweigern
+    if ".superseded-" in k: blocked.append(k); continue                # N3: Archiv bleibt
```

| Datei | Inhalt |
|---|---|
| `data/memory/slow_consolidation.py` | `_load_state` liefert `entries` (rückwärtskompatibel); neuer Helper `_is_consolidated`; `collect_pending` prüft den **aktuellen** Fakt-Hash; `mark_consolidated` verbucht `fact_sha256`/`model`/`probe_passed` je Key; `flush` verweigert ohne `state_path` und schützt `.superseded-`. |
| `data/memory/fast_write_router.py` | `discard_if_consolidated` vergleicht den übergebenen Fakt-Hash mit `entries[].fact_sha256`; Legacy-State ⇒ Key-Match (unverändert). |
| `tests/test_network_boundaries.py` | +4 verbindliche Repro-Fälle N2/N3 (echte tmp-Dateien). |
| `tests/test_slow_consolidation.py` | N3-Kontrakt angepasst (ohne Beleg ⇒ verweigern) · + Legacy-/Meta-Tests für das erweiterte State-Schema. |

- Geänderte Komponenten: **2** (ein State-Schema, zwei Konsumenten).
- Interface-Änderung? **ja** — State-Schema + `mark_consolidated`-Parameter +
  `flush`-Kontrakt (`state_path` erforderlich) ⇒ §9-pflichtig, **kenntlich gemacht**
  (Docstrings + `ergebnisse/proposal-b-n2.md` / `-c-n3.md`).

## 4. Real vs. offen (ehrlich)

- **Real:** echte Dateisystem-Tests (kein Mock, keine Fake-Antworten, G7); Repro
  wurde **zuerst rot** gegen die HEAD-Module verifiziert (§5), dann grün.
- **Rückwärtskompatibilität:** altes State-Format `{"consolidated":[keys]}` sowie der
  reale State `data/memory/tier3-working/consolidation-state.json` werden weiter
  gelesen (Hash „unbekannt" ⇒ Key-Match); `_is_consolidated` deckt beide Zweige.
  `state_path=None` bleibt für `collect_pending`/`discard_if_consolidated`
  verhaltensgleich.
- **Offen/geändert (N3-Kontrakt):** `flush` ohne `state_path` verweigert jetzt
  (vorher: löschen). Zwei Alt-Tests in `tests/test_slow_consolidation.py` wurden an
  den neuen, vom Audit geforderten Kontrakt angepasst (kein Abschwächen: sie prüfen
  jetzt gerade die N3-Verweigerung).
- **Kein `self_update`** an `AGENTS.md`/`data/memory/tier1-base/`; reale
  `consolidation-state.json` **unangetastet**.

## 5. Compare / Beleg (externes Signal: echte Tests)

**Rot (HEAD-Module, echte Ausführung der 4 Repro-Szenarien via `importlib`):**

```text
[OLD] N2 collect : FAIL (Bug reproduziert)   # geänderter Fakt wurde versteckt
[OLD] N2 router  : FAIL (Bug reproduziert)   # geänderte Antwort verworfen
[OLD] N3 flush   : FAIL (Bug reproduziert)   # ohne Beleg gelöscht
[OLD] N3 archive : FAIL (Bug reproduziert)   # Archiv/aktiver Eintrag getroffen
```

**Grün (neue Module):**

```text
pytest tests/test_network_boundaries.py -k "consolidated_old_key or router_does_not_discard
        or flush_requires or flush_preserves" --no-cov -q     -> 4 passed
pytest tests/test_slow_consolidation.py tests/test_lifecycle_discard.py
       tests/test_network_boundaries.py tests/test_fwr_write.py --no-cov -q -> 40 passed
pytest -m "not network and not live" -q --no-cov -p no:cacheprovider      -> 580 passed, 26 deselected
ruff check  <4 geänderte Code-/Testdateien>                               -> All checks passed
ruff format --check <4 geänderte Code-/Testdateien>                       -> 4 files already formatted
Coverage Datenmodul: data/memory/slow_consolidation.py                    -> 100 % (Line + Branch)
```

Repro-Kommandos (verbindlich): `pytest tests/test_network_boundaries.py` (N2/N3-Fälle).

## 6. Drift (Δ zur Baseline, §9.1c)

| Artefakt | geänderte Zeilen (numstat: +/−) | Dateizeilen | Roh-Anteil |
|---|---|---|---|
| `slow_consolidation.py` | 102 + 26 = 128 | 368 | ~34,8 % |
| `fast_write_router.py` | 30 + 16 = 46 | 434 | ~10,6 % |
| **Summe** | **174** | **802** | **~21,7 %** |

- Der **Roh-Anteil** (inkl. umfangreicher Docstrings/Kommentare) liegt **über** dem
  10 %-Default des §9.1c. Die **logische** Änderung (Funktionskörper ohne Doku) ist
  der weit kleinere Teil (Größenordnung < 10 %); die Roh-Schätzung der Proposals
  (~4,5 % bzw. 3–4 %) war zu niedrig und wird hiermit korrigiert.
- **Gate-Anbindung:** Nach §9.1c „Drift > Bound ⇒ Human-Gate (ask)". Dieses
  Human-Gate ist durch die vorliegende **Zwei-Personen-Freigabe** (Batnini + Taoufik,
  2026-10-08) belegt; die Drift ist hier **transparent ausgewiesen** (kein Verstecken).
  Reviewer-Hinweis: Sollte die Freigabe nur die Interface-/Formatänderung decken,
  ist der Drift-Punkt separat zu bestätigen.

## 7. §9-Gate

- **Interface-/Formatänderung** (State-Schema, Signaturen, `flush`-Kontrakt):
  **erforderlich** und **`approved`** — Batnini + Taoufik, 2026-10-08 (§9.3, ≥ 2 Personen).
- **Neue Quelle?** nein — nur `AGENTS.md` §10.3/§10.7 + arXiv:2608.22215 §3.4
  (beide bereits im Gesetz); kein Ontologie-Eintrag nötig.
- **self_update an Originaldateien?** nein (`AGENTS.md`/`tier1-base` unberührt).
- **Kein Commit** (Guardrail 6). Reviewer-Kommandos: `git status --short`, `git diff --stat`.

**§9-Status: `approved` (Batnini + Taoufik, 2026-10-08).**

## 8. Nächstes Self-Feedback (t+1)

- `mark_consolidated` bindet jetzt optional `model`/`adapter_version`; der Router
  gated aktuell nur über den **Inhalt-Hash**. Fließt in t+1: Modell-/Adapter-Version
  auch im Router-Gate prüfen (Write-Back-Θ′↔Adapter-Konsistenz).
- README-Index-Eintrag für 078 bleibt offen (Datei-Scope dieses Auftrags erlaubt nur
  die genannten Dateien).
