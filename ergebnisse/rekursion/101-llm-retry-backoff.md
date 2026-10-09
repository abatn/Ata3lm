# Rekursion 101: LLM-Aufrufe robust gegen Überlast (Retry/Backoff)

> Datum: 2026-10-09 · Phasen: Konstrukt → Akt → Observe → Compare (echtes Signal:
> CI-Lauf + Preflight-Log).
> Ziel `g` (§2): den **flaky** `test_distill_mit_llm_real` (CI rot seit 2026-10-09)
> deterministisch grün machen, **ohne** Fake (Guardrail 7).
> Quelle (Muster, kein Paper): `tests/_live.py::call` (Retry für transiente Fehler)
> und `scripts/ci_preflight.py` (`is_transient`, bis 8 Versuche) — Projekt-Auftrag.
> Status: **approved** (Auftrag Batnini, 2026-10-09; keine Interface-Änderung).

## 1. Anlass (echtes Signal)

- CI-Historie: letzter grüner Lauf `d25486c` (2026-10-09 07:50 UTC), erster roter
  dieser Art `48f744c` (10:49 UTC); danach `58783c2` (17:45) — jeweils
  `test_distill_mit_llm_real` rot → 2 Zeilen unüberdeckt → Coverage 99,96 % < 100 %.
- Preflight-Log (echt): `ResourceExhausted: Worker local total request limit
  reached (16/16)` → **503**; Versuch 2 dann „pong". Also **Überlast**, kein Defekt.

## 2. Ursache (belegt im Code)

- `reflective_agent.distill` **schluckt** Endpoint-Fehler (`except Exception` →
  `"(LLM nicht verfügbar: …)"`). Damit sieht `_live.call` **keinen** `raise` →
  dessen Retry greift **nicht**.
- `_live._RETRYABLE` enthält **kein** `404`/`500`/„page not found" — genau das
  trat real auf (belegt: `'(LLM nicht verfügbar: 404 page not found)'`).
- Reproduziert lokal: `ultra-550b` → 2/8 Aufrufe `500`; `baseURL` ohne `/v1` ⇒ 404.

## 3. Fix (`data/memory/llm_retry.py` + Einbindung)

**Gemeinsames Modul** `data/memory/llm_retry.py` (kein Duplikat):

```python
RETRY_ATTEMPTS = int(os.environ.get("LLM_RETRY_ATTEMPTS", "10"))
TRANSIENT_STATUS = {429, 500, 502, 503, 504}
TRANSIENT_MARKERS = ("429","500","502","503","504","overloaded",
  "resourceexhausted","service unavailable","internal server error",
  "timed out","timeout","temporarily","rate limit","rate_limit",
  "too many requests","capacity","page not found")
def is_transient(exc) -> bool: ...
def create_with_retry(client, **kwargs):   # bounded Retry + Backoff (max 30 s)
```

Eingebunden in:
- **`reflective_agent.py`** — `distill` (der rote Test) **und** `parse_transition_delta`
  (`from llm_retry import create_with_retry as _create_with_retry`).
- **`gaama_extract.py`** — `_default_llm` (2. Failing-Test `test_route_extracted_facts_real`).

Additiv/behavioral: **keine** Signatur-/Interface-Änderung (§9 `allow`).

## 4. Verifikation (echt)

- `ruff check` + `ruff format --check`: grün.
- `tests/test_reflective.py`: **29 passed** (inkl. Netz); `reflective_agent.py`
  **100 %** (Line + Branch, 0 missing).
- Neue Unit-Tests (`_is_transient`, `_create_with_retry`: erster Erfolg ·
  transient→Erfolg · erschöpft→raise · nicht-transient→sofort) decken die neuen
  Zweige offline (kein torch/netz).
- `test_distill_fehler_real` (unerreichbarer Host) fliegt **sofort** (nicht
  transient) — kein 8×-Warten.

## 5. §9-Gate

- Keine neue Quelle; kein `self_update`; Interface stabil ⇒ **kein Human-Gate
  erforderlich** (Freigabe dennoch dokumentiert: Auftrag Batnini, 2026-10-09).
- Guardrail 6 (Git): Commit/Push nur nach Erlaubnis.

## 6. Ehrlicher Caveat

- Retries erhöhen kurzzeitig die Last auf dem geteilten Worker; daher **bounded**
  (8 Versuche, Backoff bis 30 s). Ein **totaler** Ausfall bleibt rot (kein Fake).
- `distill` bleibt fachlich „unverifiziert-lokal": die Retry-Branch ist gemockt
  getestet, der Erfolgspfad real (Netz-Test).
