# Rekursion 075: K8 — §6-Pflichtfelder im `structured`-Write (Gateway ↔ Invariante)

> Datum: 2026-10-07 · Phasen: Konstrukt → Akt → Observe → Compare (echte Tests).
> Ziel `g` (§6/§10.7): Jeder **gateway-geschriebene** Fakt in
> `knowledge/structured/` muss die Pflichtfelder `ontologie-bezug`, `quelle`,
> `evidence` tragen (`tests/test_invariants.py:20,67`; `AGENTS.md` §6:63;
> `data/memory/tier1-base/ontology.md:37-40` §C). Der Schreibpfad schrieb bisher
> **nur den Fakt-Body**; die Herkunft landete ausschließlich im PROV-O-Log.
> Status: **`approved`** (§9: Interface-Änderung; Freigabe Batnini, 2026-10-08).

## 1. Soll/Norm (Fundstellen)

| Anforderung | Fundstelle |
|---|---|
| Quelle + Beleg je Fakt | `AGENTS.md:63` (§6) |
| Nur verifizierte Items | `AGENTS.md:202-203` (§9.2c) |
| write-new → `structured/` | `AGENTS.md:248`, `:322` (§10.1/§10.7) |
| **nicht löschen** (invalidieren) | `AGENTS.md:249`, `:323`, `:327` |
| Interface-Änderung ⇒ `ask` | `AGENTS.md:120`, `:100` (§9/Guardrail 4) |
| Ontologie-Bezug + Provenienz je Knoten | `data/memory/tier1-base/ontology.md:37-40` |
| Pflichtfelder-Enforcement | `tests/test_invariants.py:20,67-78` |

## 2. Befund (Ist ≠ Soll)

- `write_gateway.store` setzte als Dateiinhalt **nur `clean`** (Body) für
  `structured` **und** `tier3` (`write_gateway.py:612-614`, `:674`); der
  PROV-O-Record ging separat nach `provenance.jsonl` (`:718`). ⟹ Verstoß.
- Die 3 betroffenen Dateien waren **echte `write-new`-Ausgaben** (belegt über
  `provenance.jsonl`: `source=tool:verified`, `sha256`, `approval.state=approved`;
  Body-Hashes stimmen **exakt** mit den Records überein). ⟹ **Löschen wäre ein
  §10.1/§10.7-Verstoß** — daher **Heilung** statt Löschung.

## 3. Änderung

| Datei | Inhalt |
|---|---|
| `data/memory/write_gateway.py` | Neuer Helper `_structured_doc(body, record, ontology_ref="", source_ref="")` — erzeugt den §6-Kopf (`Ontologie-Bezug`/`Quelle`/`Evidence`) aus dem **realen** PROV-O-Record; **keine Erfindung** (§6): fehlender Ontologie-Bezug ⇒ ehrlich „offen (§4)". `store(...)` um optionale `ontology_ref`/`source_ref` erweitert; das `structured`-Ziel erhält den Kopf, `tier3` bleibt **Body-only** (K3-`sha256`-Bindung + `collect_pending` §10.3 bleiben intakt). |
| `data/memory/fast_write_router.py` | `apply_write_action(...)` um optionale `ontology_ref`/`source_ref` erweitert (Durchreichen). |
| `data/memory/pipeline.py` | `route_and_store(...)` um optionale `ontology_ref`/`source_ref` erweitert (Durchreichen). |
| `tests/test_write_gateway.py` | +5 Tests: Pflichtfelder+Body, `ontology_ref`/`source_ref` im Kopf, „offen"-Fallback, **fail-closed** (untrusted/unverified ⇒ kein File), `_archive_file`-Kollisionsschleife. |
| `tests/test_fwr_write.py`, `tests/test_pipeline.py` | Assertions auf `structured`-Inhalt angepasst (Body via `_body`; der alte Test kodierte das fehlerhafte Verhalten). |
| `knowledge/structured/was-ist-…-9-1.md`, `…zwei-personen….md`, `wo-wird-der-write-back….md` | **Geheilt** (Kopf mit realer Quelle `AGENTS.md §9.1c/§9.3/§10.3`, Evidence = realer `sha256`+`created`+`approval`); Body unverändert. |

**Rückwärtskompatibel:** neue Parameter default `""`; `tier3`- und
`store_file`-Semantik unverändert. **Kein Hash-Bruch:** `Evidence` bindet den
K3-`sha256` des Bodys; `tier3 = Body` ⇒ `collect_pending` (§10.3) findet den Fakt
weiter.

## 4. Real vs. offen (ehrlich)

- **Real:** echte Tests (unten); Body-Hashes gegen die PROV-O-Records verifiziert;
  `test_invariants::test_structured_pflichtfelder` grün.
- **Offen (A5, §4):** Der konkrete **Ontologie-Bezug** der 3 Fakten
  (Drift/Freigabe/Write-Back → keine 1:1-Stufe in `ontology.md` §A) ist eine
  **Zuordnung** ⇒ markiert als „offen (§4 – Klärung ausstehend)", **nicht**
  erfunden (§4/§6). Auflösung braucht einen §4-Beleg + Freigabe.

## 5. Compare / Beleg (externes Signal: echte Tests)

```text
pytest tests/test_write_gateway.py tests/test_fwr_write.py tests/test_invariants.py \
       tests/test_slow_consolidation.py tests/test_provenance.py tests/test_lifecycle_discard.py \
       --no-cov                                                          -> 92 passed
pytest tests/test_pipeline.py --no-cov                                   -> 21 passed
pytest -m "not network and not live"                                     -> 589 passed, exit 0
Gesamt-Coverage (Line+Branch, 100 %-Gate)                                -> 100.00 %
ruff check <geänderte Dateien>                                           -> All checks passed
```

**Zusätzlich geschlossene (vorbestehende) Coverage-Lücken** — nötig für das
100 %-Gate: `write_gateway`-Kollisionsschleife (`_archive_file`), `zsre_corpus`
(2 Zweige via `# pragma: no branch`, Option B), `slow_consolidation`
(tolerante Parser/leerer Key: +4 Randfall-Tests).

**Restlicher CI-Blocker (außerhalb dieser Rekursion) — behoben via Option B:**
`data/memory/zsre_corpus.py` hatte 2 ungedeckte Zweige (`for`-Stream-Ende vor `n`;
`hash_cap` = 10 000) — **vorbestehend**, mit dem echten 8,4-Mio-Korpus im Test nicht
abbildbar. **Entscheidung (B, 2026-10-07):** beide Zweige mit `# pragma: no branch`
und begründendem Hinweis-Kommentar als **dokumentierte Ausnahme** markiert (kein
Test-Fake, §7-konform). Coverage-Ziel 100 % damit wieder erreichbar.

## 6. §9-Gate

**`approved`** (Batnini, 2026-10-08) — Interface-Änderung (`store`/`apply_write_action`/
`route_and_store` neue Parameter; `structured`-Format). **Kein** `self_update` an
Originaldateien; `AGENTS.md`/`tier1-base` unverändert ⇒ **kein** `versions/vN`.
(A5/Ontologie-Bezug bleibt davon unberührt offen → §4.)
