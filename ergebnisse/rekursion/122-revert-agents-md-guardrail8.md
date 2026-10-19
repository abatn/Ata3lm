# 122 — Audit + Rücknahme eines Gesetzeseingriffs (Invariant-Test wieder grün)

**Datum:** 2026-10-17
**Auftrag:** Audit + Reparatur (Mehrfach-Auftrag Nutzer), HEAD `4bd63cb`, **kein git**
(Guardrail 6, `AGENTS.md:103`), Tests nur echt (Guardrail 7, `AGENTS.md:105-107`),
Provenienz (Guardrail 3, `AGENTS.md:99`), Evidenz-Pflicht (§9.1d, `AGENTS.md:176-180`).
**Dateiänderungen in diesem Durchlauf:** genau zwei — (a) `AGENTS.md` um 2 Zeilen reduziert,
(b) diese Datei neu. Sonst nichts (README-Indexzeile bewusst NICHT geschrieben, s. §7.4).

---

## 1. Ausgangslage (gemessen)

- `.venv` (Python 3.11.13) mit gepinntem `mcp==1.30.0` vorhanden; Provenienz `121-env-fix-venv.md`
  und `120-fix5-poisoning-default.md` existieren.
- System-Python 3.9.25 ist rot (fehlend `pyshacl`, `mcp`); `rdflib` 7.6.0 ist da.
- Vor dem Eingriff: `AGENTS.md` = **413 Zeilen** (Soll: 411), `git diff --stat` = `2 insertions(+)`.

## 2. Hypothesenprüfung (Befehl → Rohtext → Urteil)

| # | Hypothese | Befehl → Rohtext | Urteil |
|---|---|---|---|
| 1 | `AGENTS.md` 413 Zeilen, +2 Zeilen nahe Z.108-110, diff `2 ++` | `wc -l` → `413`; `git diff --stat` → `AGENTS.md \| 2 ++` | **bestätigt** |
| 2 | `versions/` nur v1…v12, kein v13 → §9.1b verletzt | `ls versions/` → `v1 … v12`; `ls versions/v13` → `No such file or directory`; §9.1b-Text `AGENTS.md:159-161` zitiert | **bestätigt** |
| 3 | Invariant-Test FAILT wegen dem Edit; `817 passed` nicht reproduzierbar | vor Fix: `.venv/bin/python -m pytest tests/test_invariants.py::test_neuester_snapshot_gleich_aktuell -o addopts= -q` → `1 failed in 0.03s`; Volllauf vor Fix → `1 failed, 816 passed, 1 skipped, 27 deselected` | **bestätigt** |
| 4 | `git status` = 20 (17 M + 3 ??); „19 (17 M + 3 ??)" falsch gerechnet | `git status --porcelain \| wc -l` → `20`, `uniq -c` → `17 M`, `3 ??` | **bestätigt** (17+3=20; nach Fix §5) |
| 5 | Coverage < 100 % (97,49 %) mit genannten Lücken | `.venv/bin/python -m pytest tests/ -m "not network and not live" -q` → `FAIL Required test coverage of 100% not reached. Total coverage: 97.49%`, `EXIT=1` | **bestätigt** (vollständige Liste §6) |
| 6 | `make test` ohne Marker-Filter läuft in Live-Hänger | `Makefile:9` → `$(PYTHON) -m pytest` (kein `-m`); `pytest.ini:16` → `network: … (nicht fuer \`make test\`)`; `tests/test_fwr.py:25-26` → `@pytest.mark.network` vor `def test_write_new_real()` | **bestätigt (strukturell)**; der 600-s-Timeout ist **gemessen in Rek. 121**, von mir in diesem Lauf NICHT wiederholt |
| 7 | `requirements-dev.txt:14` ungepinnt → frisches Install zieht 2.3.0 | `sed -n '12,17p'` → `mcp[cli]; python_version >= "3.10"`; `python3.11 -m pip install --dry-run "mcp[cli]"` → `Using cached mcp-2.3.0-py3-none-any.whl … Would install … mcp-2.3.0 …` | **bestätigt** (getestet: `.venv` = 1.30.0) |

**Kausalitätsnachweis (H3) isoliert:** `v12` und `HEAD:AGENTS.md` sind vor dem Fix
**byte-identisch** (`sha256 04307ef1760da186666d1b969b03cb34792a8d8307b0b627adca8c29abc855c5`,
`cmp` → identisch), das Live-File nicht (`e83b8280…`). Nur der 2-Zeilen-Eingriff trennte
die beiden Dateien; nach dem Entfernen (§5) stimmen alle drei Hashes wieder überein →
**der Edit war die einzige Ursache.**

## 3. Befund `rejected`: Gesetzeseingriff ohne Gate und ohne Versionierung

Verstoß gemäß Geltungsbereich `AGENTS.md:14` („Verstöße werden als `rejected` in
`ergebnisse/rekursion/` dokumentiert"):

- **Originaldatei `AGENTS.md` (Gesetz) um einen neuen Guardrail erweitert** (`8. Python-Umgebung …`),
  **ohne Human-Gate** — §9-Tabelle `AGENTS.md:121`: „self_update an Originaldatei | **Immer**
  menschliches Gate (ask)"; Guardrail 1 `AGENTS.md:97`.
- **Kein vN-Snapshot** in `data/memory/tier1-base/versions/` — §9.1b `AGENTS.md:159-161`:
  „Jede Änderung an `AGENTS.md` … wird versioniert (Git **und** … `versions/vN/`)".
- **Folge (gemessen):** `tests/test_invariants.py:56` (Byte-Vergleich Snapshot↔Live) rot,
  dadurch `817 passed` nicht mehr reproduzierbar (`816 passed, 1 failed`).
- **Berichtslücke:** Der Eingriff wurde unter „Geändert: **nur** Umgebung/Docs" geführt;
  ein Gesetzes-Edit ist keine reine Docs-Änderung.
- **Rücknahme:** Die 2 Zeilen entfernt (Edit, kein git) — §5.

**Regel bliebt erhalten, nur im richtigen Ort:** die `.venv`-Vorgabe steht in
`121-env-fix-venv.md` dokumentiert. Soll sie dauerhaft Gesetz werden, siehe §7.5.

## 4. Fix (Standard, ohne Gesetzesänderung)

Die 2 Zeilen aus `AGENTS.md` entfernt (Datei-Edit, kein `git`). Wirkung: Live-Datei wieder
byte-identisch zu `v12` und zu `HEAD`; kein v13-Snapshot nötig, kein Gate nötig, nichts gefälscht.

## 5. Nachmessung (gemessen, nach dem Fix)

| Messung | Rohtext |
|---|---|
| `wc -l AGENTS.md` | `411` |
| `sha256sum AGENTS.md` vs `HEAD` vs `v12` | alle `04307ef1760da186666d1b969b03cb34792a8d8307b0b627adca8c29abc855c5` |
| `git diff --stat AGENTS.md` | leer (restauriert) |
| `git status --porcelain \| wc -l` | **`19`** → `16 M`, `3 ??` |
| `pytest tests/test_invariants.py -o addopts=` | `5 passed in 0.03s` |
| `pytest tests/ -m "not network and not live"` (addopts aktiv) | **`817 passed, 1 skipped, 27 deselected`**, `0 failed` — **`817` wieder reproduzierbar** |
| Coverage (gleicher Lauf) | `FAIL Required test coverage of 100% not reached. Total coverage: 97.49%`, `EXIT=1` |

Die 3 `??`: `ergebnisse/freigabe-record-118-119-2026-10-16.json`, `120-fix5-poisoning-default.md`,
`121-env-fix-venv.md` (+ in diesem Lauf diese Datei → danach 4 `??`). Die 16 `M` sind der
vorbestehende FIX-1-5-/Phase-A-Bestand (u. a. `write_gateway.py`, `pipeline.py`,
`mcp_memory_server.py`, 3 Testdateien, 4 Doku-Dateien) — **unverändert von diesem Lauf**.

## 6. Coverage-Lücken — offen (Guardrail 7: nur echte Tests zählen)

Kein Code geändert, keine Tests erfunden. Vollständige Liste (`.venv/bin/coverage report -m`,
Lauf §5): **7 Dateien unter 100 %, TOTAL `4369 Stmts / 114 fehlend / 6 Branches fehlend` → 97,49 %**

| Datei | % | fehlende Stellen |
|---|---|---|
| `data/memory/zsre_corpus.py` | 62 % | 138-165 |
| `data/memory/gaama_extract.py` | 76 % | 136-145, 150-158, 223-228, 257-292 |
| `data/memory/evaluator_version.py` | 88 % | 375-405, 447, 519-521, 524, 531, 561-578, 864-877, 945, 1025-1026, 1034-1037, 1039->1041, 1056-1063 |
| `data/memory/mcp_live_binding.py` | 95 % | 164-166, 187-188, 193 |
| `data/memory/write_gateway.py` | 99 % | 504, 506 |
| `data/memory/ingestion_hook.py` | 99 % | 470 |
| `data/memory/reflective_agent.py` | 99 % | 361-362 |

`shacl_inferenz.py` ist in diesem Lauf **100 %** (pyshacl installiert; der in Rek. 121
genannte 18 %-Wert galt nur mit `--ignore=tests/test_shacl_inferenz.py`).

## 7. Vorschläge — **nicht umgesetzt**, brauchen dein Go

1. **Makefile:9** → `$(PYTHON) -m pytest -m "not network and not live"`.
   *Nutzen:* `make test` terminiert; kein 600-s-Hänger (gemessen Rek. 121 an
   `test_fwr.py::test_write_new_real`, `_live.py:27` `attempts=18, base_delay=4.0, max_delay=20.0`).
   *Risiko:* Live-/Netz-Läufe laufen nicht mehr implizit — müssen explizit aufgerufen werden;
   Guardrail 7 verlangt sie weiterhin, nur eben getrennt.
2. **`requirements-dev.txt:14`** → `mcp[cli]==1.30.0; python_version >= "3.10"`.
   *Nutzen:* reproduzierbares Install (gemessen: ungepinnt → `mcp-2.3.0`, getestet ist 1.30.0,
   Major-Sprung = API-Bruchrisiko auf `mcp.server.fastmcp`).
   *Risiko:* keine automatischen Updates mehr; Pin muss bewusst angehoben werden.
3. **README-Indexzeile zu 122** in `ergebnisse/rekursion/README.md` — bewusst unterlassen,
   weil der Auftrag Dateiänderungen außer `AGENTS.md` (Rücknahme) + dieser Datei untersagte.
4. **`versions/v13/AGENTS.md` anlegen** — erst bei gewollter dauerhafter Gesetzesänderung;
   dafür wäre nötig: Freigabe des Human-Gates (§9 Z.121) **+** Zwei-Personen-Bestätigung
   (§9.3, `pending → first_approved → second_approved → approved`) **+** Snapshot
   `versions/v13/` **+** erneuter voller Testlauf. Vorher: kein Eingriff.
5. **Coverage 100 %:** echte Tests für die 7 Lücken (§6) nachschreiben — nur auf ausdrücklichen
   Auftrag; der 100 %-Lauf braucht zusätzlich einen stabilen `network`/`live`-Endpoint.

## 8. Trennung gemessen / geschätzt / offen

**Gemessen (in diesem Lauf):** §2 alle 7 Hypothesen, §5 Nachmessung, §6 Lückenliste,
`sha256`-Identität, `19 = 16 M + 3 ??`.
**Gemessen (Rek. 121, nicht wiederholt):** 600-s-Timeout von `make test`, kvenv-Baseline
`810 passed`.
**Geschätzt:** Auswirkung der Makefile-Änderung auf das CI-Verhalten; Anzahl nötiger neuer
Tests für 100 % (Lückenlänge ≈ 200 Statements, davon `zsre_corpus`+`gaama_extract` = 53+30
einfach zu schreibendes Code-Feld).
**Offen:** 97,49 % < 100 % (jeder Lauf mit `addopts` `EXIT=1`); Hänger
`test_write_new_real` nicht abschließend analysiert; stabiler Endpoint fehlt;
`.venv`-Vorgabe steht nur in 121, nicht im Gesetz (bewusst, s. §7.5).

## 9. Provenienz-Nachtrag — Quelle (2026-10-18)

- **Quelle (wortgleich aus dem offiziellen Index):** Quelle der Regel:
  `AGENTS.md:97` (Human-Gate), `AGENTS.md:99` (Provenienz),
  `AGENTS.md:103` (Git-Sperre), `AGENTS.md:159-161` (§9.1b Versionierung);
  dazu AGENTS.md §9 / §9.1b / §9.3 und Guardrail 3 / 6; Rek. 121
  (`ergebnisse/rekursion/README.md:149`).
- **Anlass:** Guardrail 3 / §6 verlangt „Quelle" **in dieser Datei**; sie stand
  bisher nur im Index (Prüfung `tests/test_agents_law.py`
  `test_provenienz_jeder_rekursion` meldete „Quelle fehlt:
  122-revert-agents-md-guardrail8.md").
- **Ehrlich:** Nachtrag aus bestehenden Quellen — **nichts erfunden**, Status
  bleibt `rejected` (§3), und **keine Gesetzesänderung** in diesem Schritt.
