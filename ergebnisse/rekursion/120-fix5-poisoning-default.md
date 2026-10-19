# Rekursion 120 — FIX 5 (Poisoning-Default) + FIX 6 (Kommentar)

## Kopf / Freigabe

- **FIX 5:** `write_gateway.store_file`/`store` Defaults fail-closed
  (`verified: bool = False`; `store`: zusätzlich `origin: str = "user"`).
- **FIX 6:** `mcp_memory_server.py` — Wert `verified=True` bleibt, nur
  Kommentar-Verdeutlichung (explizit gesetzt, gestützt auf Tri-Color-Gate).
- **Interface-Änderung nach §9** (Funktions-Signatur-Defaults geändert) →
  Human-Gate: **Freigabe menschliches Gate, Nutzer 2026-10-17, §9 AGENTS.md:120**
  (Tabelle: „Interface-Änderung | Immer menschliches Gate (ask)"; Auftrag).
- **Guardrail 6:** Alle Änderungen sind **uncommitted im Working Tree**
  (`git diff --cached` leer; kein `git add`/`commit`/`push`).
- Umsetzung: Implementierungs-Agent (Code + Tests). Verifikation/Messung:
  unabhängig durch den Ausführenden (dieser Eintrag), Zeilen alle selbst
  nachgelesen, Zahlen selbst gemessen bzw. in `/tmp`-Kopien reproduziert.

## Lauf (Befehle, die hier belegt werden)

Interpreter-Hinweis: Die Suite-Zahlen unten laufen mit **System-Python**
(`/usr/bin/python3`, ohne `pyshacl`/`mcp`); Kreuzcheck mit `/tmp/kvenv`
(mit `pyshacl 0.40.1` + `mcp 1.30.0`, installiert 2026-10-16 10:34/10:35
laut `dist-info`-Zeitstempel) siehe §„Nachher".

```
# 2-Dateien-Teilmenge (Nachher)
/usr/bin/python3 -m pytest tests/test_write_gateway.py tests/test_network_boundaries.py \
  -q -p no:cacheprovider -o addopts=
# Volle Suite (Nachher)
/usr/bin/python3 -m pytest tests/ --ignore=tests/test_shacl_inferenz.py \
  -m "not network and not live" -q -p no:cacheprovider -o addopts=
# Pipeline-Pfad
/usr/bin/python3 -m pytest tests/test_pipeline.py tests/test_d2_gdi_prewrite.py \
  tests/test_lifecycle_runner.py tests/test_recursion_runner.py -q -p no:cacheprovider -o addopts=
# Lint
/tmp/kvenv/bin/ruff check data/memory tests
```

## Warum (belegt)

Das fail-closed Poisoning-Gate (`data/memory/trust.py`) prüft Item-Quelle
und Verifikation:

- `trust.py:63` `class PoisoningGuard`; `trust.py:73` `def admit`;
  `trust.py:71` `trusted_sources = {"user", "tool:verified", "system"}`;
  `trust.py:75` `verified = bool(item.get("verified"))`;
  **`trust.py:78-79`** `if not verified:` → `admitted=False`
  („not verified (consensus/verification required)").
- Angebunden über `write_gateway.py:114-116` (`_gate_poisoning`), aufgerufen
  in `store_file` bei **`:463`** und in `store` bei **`:710`** — jeweils
  **vor** der Mutation (fail-closed).

Vor FIX 5 fütterten die Defaults von `write_gateway.store_file`/`store`
dieses Gate mit „geprüft", ohne dass geprüft wurde:

- `store_file`: vorher `verified: bool = True` (HEAD, `:407`);
- `store`: vorher `origin: str = "tool:verified"` + `verified: bool = True`
  (HEAD, `:607-608`).

Jeder Aufrufer, der `verified`/`origin` **nicht** explizit übergab, schrieb
damit Items, die das Gate als verifizierte Trusted-Origin durchließ — obwohl
keine Konsens-/Verifikation stattgefunden hatte. Das widerspricht §9.2c
(AGENTS.md:202-207: „Nur verifizierte Items werden gespeichert: trusted
origin **und** verified"; Write-Time Origin Binding) und dem §6-Verbot
belegloser Behauptungen (AGENTS.md:61-68). FIX 5 dreht die Defaults um:
fail-closed by default; wer verifizieren kann, ügibt es explizit.

## Was geändert wurde

### Phase A (bereits vor dieser Iteration uncommitted; Zeilen aus `git diff` + Nachlesen)

- **FIX 1 `questions=`** (Train-/Probenfrage konsistent, §10.3):
  `data/memory/slow_consolidation.py:427` (kw-only Param `questions=None`),
  `:479` (`collect_pending(..., questions=questions)`);
  `kaggle/write_back_cycle.py:628` (`questions_dict = _questions_by_key(tasks)`),
  `:631` (kwarg an `collect_pending`), `:651` (kwarg an `write_back`).
- **FIX 2 `probe_results` in allen Returns** (Evidenz §9.1d):
  `slow_consolidation.py:481`, `:494`, `:517`, `:542`;
  `write_back_cycle.py:676` (`"probe_results": write_back.get(...)`);
  Docstring-Vermerk `slow_consolidation.py:448-450`.
- **FIX 3 Approver-Kanonisierung `.strip().lower()`:**
  `data/memory/approval.py:55` (Duplikat-Check), `:71` (Append);
  `data/memory/provenance.py:69` (Mengenbildung der distinkten Approver);
  `kaggle/write_back_cycle.py:176` (`_resolve_approvers`).
- **FIX 4 Fallback-Label + `self_report`:**
  `data/memory/recursion_runner.py:137` (Signal-Label
  „Aufrufer-Report (kein externes Probe)" statt
  „externes Ground-Truth-Signal"), `:148` (`"self_report": self_report`).

### Phase B (diese Iteration)

- **`data/memory/write_gateway.py`:** `:407` `verified: bool = False`
  (`store_file`); `:607` `origin: str = "user"`; `:608` `verified: bool = False`
  (`store`). Gate-Logik **unverändert** (`:114-116`, `:463`, `:710`).
- **`data/memory/pipeline.py`:** §6-Vermerk im Docstring `:74-79`
  („Beibehaltung bisherigen Verhaltens, KEINE eigene Verifikation …
  Behauptung nur als Verhaltensbeibehaltung, nicht als geprüft (§6)")
  + explizite Übergabe `origin="tool:verified"` `:96` und `verified=True`
  `:97` im `write_gateway.store`-Call.
- **`data/memory/mcp_memory_server.py:228-231`:** nur Kommentar
  (FIX 6); Wert `verified=True` bleibt explizit (gestützt auf
  Tri-Color-Gate + Trust-DB: red → rejected, fehlende Trust-DB →
  fail-closed; grüne Vorschläge bleiben `status="proposed"`, §9.2c).
- **Tests:** `git diff tests/ | grep -c` (selbst nachgeprüft):
  **28 × `verified=True` ergänzt, 0 entfernt** (23 in
  `tests/test_write_gateway.py`, 5 in `tests/test_network_boundaries.py`);
  **zusätzlich 1 × `origin="tool:verified"`** in
  `tests/test_write_gateway.py:715` (`test_k8_ohne_refs_ehrlich_offen_kein_fake`,
  wegen `assert "tool:verified" in doc` `:718`). Betroffen: **26 Tests**
  (22 `test_write_gateway.py` + 4 `tests/test_network_boundaries.py`;
  `test_k8_revision_links_to_preceding_entity` mit 2 Call-Sites).
  Helfer `_structured_store` (`tests/test_write_gateway.py:679`) blieb
  **unverändert** (nur Call-Sites ergänzten Args). Zusätzlich
  `tests/test_slow_consolidation.py:258` (FIX-2-Assertion `probe_results`).

## §9.1d-Evidenz (AGENTS.md:176-180) — nur Gemessenes

### Vorher-Baseline (Phase-A-Basis, FIX 5/6 noch nicht angewandt)

Rekonstruktion: `git archive HEAD` nach `/tmp` (Working Tree blieb unberührt,
kein Stash) + Phase-A-Dateien aus dem Working Tree kopiert; verifiziert:
Defaults `verified=True` (`write_gateway.py:407`, `:608`), `origin="tool:verified"`
(`:607`), Pipeline ohne FIX-5-Call-Site.

- 2 Dateien: **`59 passed`**
- Volle Suite: **`12 failed, 793 passed, 4 skipped, 27 deselected, 2 errors`**
  (EXIT=1). Die 12 + 2 = Umgebung, nicht funktional:
  5× `tests/test_connector_binding.py` (`ModuleNotFoundError: pyshacl`),
  4× `tests/test_mcp_live_binding.py` + 3× `tests/test_skill_interpreter.py`
  (`mcp` fehlt bzw. Modus-Fallback `local-fallback` statt `mcp`),
  2 Errors = `tests/test_mcp_live_binding.py` (streamable_http).

### In-Prozess-Simulationen (unabhängig reproduziert, in `/tmp`-Kopie, keine Working-Tree-Dateiänderung)

Zum Vergleich mit den vorimplementierungen `__kwdefaults__`-Patch-Zahlen des
Implementierungs-Agenten habe ich die Szenarien in der `/tmp`-Kopie über
Datei-Default-Flips nachgestellt (gleiche Semantik wie `__kwdefaults__`):

| Szenario | Umfang | Ergebnis (gemessen) |
|---|---|---|
| nur-Flip (`verified` True→False, `origin` →`user`, kein Pipeline-Fix) | 2 Dateien | **`27 failed, 32 passed`** |
| nur-Flip, volle Suite | Suite | **`73 failed, 732 passed, 4 skipped, 27 deselected, 2 errors`** |
| FIX-5-komplett-Simulation (Flip + pipeline.py + mcp_memory_server.py) | Suite | **`38 failed, 767 passed, 4 skipped, 27 deselected, 2 errors`** = 12 Umgebung + **26 fachlich betroffen** (22 `test_write_gateway.py` + 4 `test_network_boundaries.py`) |
| verified-Flip allein vs. Flip+origin | 2 Dateien | **identische Failure-Menge** (26 = 26, `diff` leer; `origin`-Flip ohne Zusatzbruch) |
| origin-Flip allein (`verified` bleibt True) | 2 Dateien | `1 failed` (`test_k8_ohne_refs_ehrlich_offen_kein_fake`) |

Die 26 fachlich Betroffenen entsprechen exakt den 26 Tests, die im echten
Fix `verified=True` erhielten (oben gezählt). Differenz 73 → 38 = **35**
entfallene Failures durch die Pipeline-Call-Site-Fixes — Aufteilung
**gemessen** (`comm -23` der beiden Failure-Listen, nach Datei gruppiert):

- **34 außerhalb der beiden Direktdateien** (gemittelt über
  `recursion_runner.py:60` → `pipeline.route_and_store`): 11
  `tests/test_pipeline.py`, 6 `tests/test_recursion_runner.py`, 6
  `tests/test_lifecycle_runner.py`, 3 `tests/test_runner_state.py`, 3
  `tests/test_freigabe_pfad.py`, 3 `tests/test_d2_gdi_prewrite.py`, 1
  `tests/test_reflective.py`, 1 `tests/test_skill_interpreter.py`;
- **+1 in einer Direktdatei**: `tests/test_network_boundaries.py::test_oracle_success_drives_revision_without_self_report`
  (ebenfalls pipeline-vermittelt).

Die Aussage „**34 pipeline-vermittelt**" ist damit als Komponente
*außerhalb der beiden Direktdateien* **korrekt** (vom Auftraggeber 2026-10-17
bestätigt); die dagegen erhobene Zwischenbehauptung „off-by-one 34" war
**widerrufen**. Endpunkt-Zahlen 73 und 38 reproduzieren exakt
(73 − 38 = 35 = 34 + 1).

### Nachher (aktueller Working Tree, unabhängig vom Umsetzungs-Agenten nachgemessen)

- 2 Dateien: **`59 passed`** (EXIT=0 mit `-o addopts=`).
- Volle Suite (System-Python): **`12 failed, 793 passed, 4 skipped,
  27 deselected, 2 errors`** — **identisch zur Umgebungs-Baseline,
  0 fachliche Regression** (gleiche 12 + 2, gleiche Aufteilung).
- Kreuzcheck `/tmp/kvenv` (pyshacl + mcp vorhanden): **`810 passed,
  1 skipped, 27 deselected`**, 0 failed, 0 errors — belegt, dass die
  12 + 2 rein umgebungsbedingt (fehlende Pakete im System-Python) sind.
  Korrektur zur Planung: „`pip install pyshacl mcp` nicht ausgeführt" trifft
  für `/usr/bin/python3` zu, **nicht** für `/tmp/kvenv` — dort sind beide
  Pakete seit 2026-10-16 10:34/10:35 vorhanden (Ob diese Installation
  freigegeben war, ist hier nicht bekannt; gemessen wurde mit System-Python).
- Pipeline-Pfad mit echtem `origin="tool:verified"`:
  `pytest tests/test_pipeline.py tests/test_d2_gdi_prewrite.py
  tests/test_lifecycle_runner.py tests/test_recursion_runner.py`
  → **`65 passed`**.
- `ruff check data/memory tests` → **`All checks passed!`**.

### Coverage-Falle (gemessen)

`pytest.ini:14` = `--cov-fail-under=100`. Subset-Läufe ohne Umgehung rot,
obwohl alle Tests grün:

- Nachher-Zustand, 2 Dateien **ohne** `-o addopts=`: `59 passed`,
  EXIT=**1**, `Total coverage: 29.22 %` (System-Python; `/tmp/kvenv`:
  29.21 %). Mit `-o addopts=`: EXIT=**0**.
- **„32 passed / 23.30 %" (Planung): reproduziert** — Befehl
  `python -m pytest tests/test_slow_consolidation.py -q -p no:cacheprovider`
  (Standard-`addopts`, aktueller Working Tree): `32 passed`,
  `Total coverage: 23.30 %`, **EXIT=1**; nachgemessen in diesem Lauf
  (zuvor unabhängig vom Auftraggeber reproduziert). Die Zahl gehört zum
  **1-Dateien-Subset `tests/test_slow_consolidation.py`** (32 Tests).
- 2-Dateien-Subset unter Flip-Simulation ohne Umgehung: `27 failed,
  32 passed`, EXIT=1, `Total coverage: 26.67 %` — **andere Messbasis**
  (2 Dateien statt 1), daher andere Percentage; kein Widerspruch.

### Score / Δ / Drift

**Kein Compare-Score, kein Δ, kein Drift vorhanden** — es handelt sich um
eine Code-Änderung (Defaults/Call-Sites/Tests), keinen Modellvergleich.
§9.1d-Evidenz daher: Diff = uncommitted `git diff` (oben referenziert),
extern verifizierbares Signal = pytest-Suite-Zahlen (§6), Drift = n/a
(keine Modellparameter- oder Prompt-Änderung).

## Gemessen / Geschätzt / Offen

### Gemessen

Alle Zahlen in den vorigen Abschnitten: Baseline `59` / `12-793-4-27-2`;
Simulationen `27`, `73`, `38/767`, `26=26`, `1`; Nachher `59`,
`12-793-4-27-2`, `810/1/27` (kvenv), `65`, `All checks passed!`;
Testdiff `28` ergänzt / `0` entfernt / `1` origin / `26` Tests;
Coverage-Falle: `23.30 %` (`tests/test_slow_consolidation.py`, reproduziert),
`26.67 %`/`29.22 %` (2-Dateien-Subsets), EXIT=1 ohne Umgehung, 0 mit
`-o addopts=`; Delta-Split `73−38 = 35 = 34 + 1`.

### Geschätzt

Keine. Die frühere Schätzung „~8 brechende Tests" war **widerlegt** —
gemessen sind **26** betroffene Tests (plus die Simulations-Zahlen oben).

### Offen

- **(a) Umgebung:** `pyshacl`/`mcp` fehlen in `/usr/bin/python3`; die
  12 Failed + 2 Errors bleiben Umgebungs-Probleme. Eine Installation nur
  mit Freigabe; `/tmp/kvenv` enthält beide bereits (s. o.), wurde von mir
  nicht installiert.
- **(b) Semantik je Call-Site (teilweise offen):** Der Umsetzungs-Agent
  berichtet, alle 28 `verified=True`-Ergänzungen seien Fall A
  („erfolgreicher Write beabsichtigt → verified=True"); Fall B (echte
  Unverifiziert-Sperren) gab es nicht — die einschlägigen Tests
  `tests/test_write_gateway.py:68`
  (`test_store_file_poisoning_untrusted_und_unverified`) und
  `:721` (`test_k8_fail_closed_untrusted_und_unverified`) wurden per
  `grep` verifiziert und blieben **unverändert grün** (sie setzen
  `origin="web:untrusted"` bzw. `verified=False` explizit). Vom
  Ausführenden wurde die **Gesamtwirkung** gemessen (0 fachliche
  Regression), nicht jede der 28 Einzelstellen semantisch nachgelesen —
  Einzelstellen-Re-Prüfung bleibt **offen**.

## Mehr-Agenten-Hinweis

Umsetzung durch den Implementierungs-Agent; Verifikation/Messung und
Simulation-Reproduktion unabhängig durch den Ausführenden (dieser Lauf).
Externe Zwischenbehauptungen („38 nicht reproduzierbar", „off-by-one 34")
waren **widerrufen**; meine Reproduktionen stimmen mit den Endpunkt-Zahlen
des Implementierungs-Agenten überein (27, 73, 38/767, 26 fachlich betroffen).

## Freigabe (§9, Interface-Änderung)

| Gate | Status | Datum |
|---|---|---|
| Human-Gate (§9 AGENTS.md:120, Interface-Änderung) | **Freigabe menschliches Gate, Nutzer** | 2026-10-17 |

Nicht abgeschlossen: Einzelstellen-Semantik-Prüfung der 28 Call-Sites
(offen, s. o.); Installation der Umgebungs-Pakete nur mit Freigabe.
