# M3 — Out-of-Band-Evaluation (World-State-Oracle)

> Datum: 2026-10-07 · Lab-Prinzip §6 (keine Erfindungen) · §1 (beobachten ohne
> zu deuten) · Guardrail 2 (kein Compare ohne verifizierbares Signal) ·
> Guardrail 7 (echte Tests, kein Fake).
> Modul: `data/memory/world_state_oracle.py` · Hook:
> `data/memory/recursion_runner.py:_phase_compare` · Test:
> `tests/test_world_state_oracle.py`.
> Status §9: **`ask`** (neue Quelle + Interface-Änderung).

## 1. Problem

Ein Agent, der seinen **eigenen** Fortschritt bewertet (Selbstreport
`successes`/`failures`), kann Stagnation für Fortschritt halten
(„progress mirage"). Der Selbstreport ist **kein** zulässiges Compare-Signal
(§6, „konfidente Fehlanpassung"). Compare braucht ein **externes**, vom Agenten
unabhängiges Ergebnis: einen echten Code-Run / Datei-Check / DB-Query
(Out-of-Band-Evaluation).

## 2. Quellen (per `curl` real verifiziert, 2026-10-07)

| Zweck | Referenz | HTTP | Link |
|---|---|---|---|
| Paper (World-State-Oracle; Out-of-Band-Evaluation strukturell nötig) | **arXiv:2607.25152** (v2, 29.09.2026) | 200 | <https://arxiv.org/abs/2607.25152> |
| Deposit desselben Papers (Concept-DOI → neueste Version) | **Zenodo `10.5281/zenodo.21594735`** | 200 | <https://doi.org/10.5281/zenodo.21594735> |

**Verifikation:** `curl -L` liefert für beide Links HTTP `200`. Der Concept-DOI
`10.5281/zenodo.21594735` löst auf `zenodo.org/records/21672574` auf; der
Zenodo-Datensatz trägt denselben Titel wie die arXiv-Seite (gematcht, 2026-10-07).

**Wörtliches Zitat aus dem Abstract (gegen die echte arXiv-Seite geprüft):**

> „A **world-state oracle**, unfakeable in principle, is enforced by container
> and network isolation and verified at every run."

> „When an agent grades its own work, self-evaluation bias takes hold: plausible
> changes are accepted as progress while real-world outcomes stagnate or
> regress. … Self-report was thus uninformative."

> „For open-ended objectives whose success signal lives outside the transcript,
> scaling up the judge is not enough; **out-of-band evaluation with real-world
> access is a structural requirement**."

## 3. Status-Trennung (§9.1)

| Aussage | Status |
|---|---|
| Existenz + Notwendigkeit eines World-State-Oracle; Out-of-Band-Evaluation nötig; Selbstreport uninformativ | **Belegt** (arXiv:2607.25152 / Zenodo) |
| Übersetzung des Probe-Ergebnisses in einen Score (`successes`/`failures`) und in das Gate-Band (≥ 95 % allow · 70–94 % ask · < 70 % deny) | **Auftrag** (Projekt, §9) |
| Interface-Änderung: neue optionale Parameter `world_state_probe` / `world_state_claim` | **Auftrag** (§9, kenntlich gemacht im Docstring) |

Nichts wird als Paper-Claim ausgegeben, was nicht im Paper steht.

## 4. `world_state_oracle.evaluate(claim, probe)`

`probe` ist ein **echtes** Callable (Code-Run, Datei-Check, DB-Query). Rückgabe:

```text
{"ok", "evidence", "signal", "reason", "claim", "successes", "failures"}
```

- `probe` liefert Wahrheitswert → `ok = bool(raw)`, Zähler 1/0 bzw. 0/1.
- `probe` liefert `{"ok": bool, ...}` → `ok` maßgeblich; `successes`/`failures`/
  `evidence` optional (Defaults 1/0 bzw. 0/1 bzw. das Dict selbst).
- **Kein echtes Signal (§1/§6, Guardrail 7):** `probe is None` / nicht callable →
  `ok=False`, `signal="kein externes Signal"`, `reason="… kein echtes
  Probe-Callable"`. Probe wirft eine Exception → `ok=False`,
  `signal="kein externes Signal"`, `reason="Probe-Fehler: …"`. Der Selbstreport
  ersetzt das fehlende Signal **nicht**.

`signal` ist `"externes Signal (World-State-Oracle)"` nur bei `ok=True`.

## 5. Hook in `recursion_runner._phase_compare` (§6)

- Ist `world_state_probe` gesetzt, entscheidet **allein** das Out-of-Band-Ergebnis
  (`world_state_oracle.evaluate`) über `Compare.observed`; der Selbstreport
  (`successes`/`failures`) wird als `self_report` **nur Annotation** geführt.
- Liefert das Probe **kein** Signal (`ok=False`): `observed=False`, Score `0.0`,
  `gate="ask"`, Meldung „kein externes Signal (Oracle) – Selbstreport nur
  Annotation, kein Ground-Truth-Claim (§1/§6)". **Kein** Ground-Truth-Claim.
- Ohne `world_state_probe` bleibt der bisherige Pfad **unverändert**
  (Rückwärtskompatibilität; bestehende Aufrufer/Tests liefern weiterhin
  `observed`/`score`/`gate` ohne `oracle`).

**Interface-Änderung (§9-pflichtig, kenntlich gemacht):** neue optionale
Parameter `world_state_probe`, `world_state_claim` (`world_state_claim` Default:
`fact`). Beide Default `None` ⇒ altes Verhalten. Docstring-Marker in
`recursion_runner.run_recursion` („Interface-Änderung … M3").

## 6. Compare / Beleg (externes Signal: echte Tests)

Real ausgeführt am 2026-10-07 (`.venv/bin/python`, kein Fake):

```text
pytest tests/test_world_state_oracle.py   --no-cov   -> 15 passed
pytest tests/test_recursion_runner.py     --no-cov   -> 14 passed
ruff check world_state_oracle.py test_world_state_oracle.py recursion_runner.py
                                                      -> All checks passed
```

Die Probes im Test sind **echt**: Datei schreiben+lesen (`tmp_path/state.txt`),
Code ausführen (`2+2==4`), Exception auslösen, `None`/Nicht-Callable. Testfälle
(a) Probe True → externes Signal; (b) Probe False / `raise` / `None` /
Nicht-Callable → kein Signal; (c) Compare koppelt den Oracle (Probe False
überstimmt Selbstreport 99/0 → `observed=False`, `gate=ask`; Probe ok → Score,
Gate, `oracle.claim`; Legacy-Pfad ohne Probe unverändert).

**Regressionsnachweis (offline, gleiche Module/Umfeld):**

```text
pytest test_world_state_oracle test_recursion_runner test_gate_labels \
       test_governance test_lifecycle_runner test_write_gateway \
       test_memory test_runner_state                       -> 145 passed
```

**Ehrlicher Hinweis:** Der **vollständige** Suite-Lauf (`make test`) konnte in
dieser Umgebung nicht in endlicher Zeit abschließen: mehrere **bereits
bestehende** Live-LLM-Tests in `tests/test_evaluator_version.py` u. a. rufen das
echte NVIDIA-Endpoint mit bis zu 18 Retries (`tests/_live.py`) auf. Das ist
**unabhängig** von M3 (M3 berührt jene Datei nicht) und keine Regression.

## 7. Offene Punkte / Human-Gate §9

1. **Neue Quelle** (arXiv:2607.25152 + Zenodo `10.5281/zenodo.21594735`) → nicht
   in der Ontologie ⇒ **§9 `ask`** (menschliche Freigabe vor Persistierung).
2. **Interface-Änderung** (`world_state_probe`, `world_state_claim`) ⇒ **§9 `ask`**.
3. Kein `self_update` an Originaldateien; `AGENTS.md`/`tier1-base` unverändert.
4. Kein Git (G6). Keine Erfindung (G7): Links HTTP-200, Zitate gegen die echte
   Abstract geprüft, Tests real.

## 8. Status

**`ask`** — neue Quelle + Interface-Änderung, menschliche Freigabe ausstehend.
Provenienz: `ergebnisse/rekursion/073-out-of-band-eval.md`.
