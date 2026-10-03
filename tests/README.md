# tests/ – pytest-Setup für den gesamten Knowledge-Agenten

> Stand: 2026-10-03 · Aufruf: `make test` (oder `python3 -m pytest`) ·
> Quelle: Python-Standard **pytest** – https://docs.pytest.org/en/stable/

## Ausführen

```bash
make test                 # Makefile → python3 -m pytest (bevorzugt .venv)
python3 -m pytest         # dasselbe, ohne make
python3 -m pytest tests/test_reflective.py -v
```

Voraussetzungen (gemessen 2026-10-03): `pytest 8.4.2`, `pytest-cov`, `coverage`,
`numpy`, `datasets` (HF), `scipy`, `openai`; **Repo-venv `.venv` (Python 3.12)**.

**Mindest-Score:** `pytest.ini` → `--cov-fail-under=100`.
Gemessen 2026-10-03: **100,00 %** – 2203/2203 Statements **und 550/550 Branches**
über den gesamten Repo-Code (`data/memory/**`, `skills/**`,
`ergebnisse/rekursion/solver/**`).

**Was „100 %" heißt:** **Line + Branch**-Coverage (`branch = True` in
`.coveragerc`, `--cov-branch` in `pytest.ini`). Ausgenommen sind nur
`__main__`-Blöcke und einzelne, begründete `# pragma: no cover`-Zeilen
(optionale reale Dependency wie GLiNER sowie Fault-Injection-Pfade, die
Guardrail 7 verbietet). Details: `ergebnisse/ci-setup.md`, `ergebnisse/branch-coverage.md`.

## Echte Verifikation (AGENTS.md Guardrail 7, Auftrag 2026-10-03)

**Keine Fakes, keine skripteten Antworten.** Tests/Compare laufen gegen das
**echte** NVIDIA-Endpoint und **echte** HF-Anker:

- `conftest.py` liest Key/BaseURL aus `~/.config/opencode/opencode.json`
  (Provider `nvidia-llama-nemotron`) → kein Platzhalter, keine Netz-Sperre.
- `_live.py::call(fn, ...)` ruft die echte Funktion und wiederholt **nur
  transiente** Fehler (503/429/…) mit Backoff.
- Fehlerpfade werden mit **echten** Fehlerbedingungen getestet (z. B.
  `OPENAI_BASE_URL=http://127.0.0.1:9` → echter Verbindungsfehler).
- Parsing ist als **reine Funktion** abgetrennt (mit echten Strings testbar):
  `fast_write_router._decide`, `reflective_agent._matrix_from_raw`/`_summary_from_raw`,
  `evaluator_version._parse_grader_verdict`/`_parse_pair_winner`/`_parse_class_grade`.
- Schreibpfade (Logs, Tier 2/3, `knowledge/structured`) zeigen in `tmp_path`.

**Konsequenz:** Der Lauf braucht Netz + Endpoint und dauert ~15 Min. Transiente
Endpoint-Ausfälle können einzelne Läufe scheitern lassen (Retry mildert).

## Dateien

| Datei | Inhalt | Tests |
|---|---|---|
| `conftest.py` | `sys.path`; **echtes** Endpoint aus `opencode.json` | – |
| `_live.py` | `call(fn, ...)` – echte Calls + Retry transienter Fehler | – |
| `test_fwr.py` | FWR-Kaskade real (non-write/write-new/write-update/uncertain), `_ask` real, `_decide` (rein), MemRouter | 11 |
| `test_governance.py` | Zwei-Personen-Flow (§9.3) inkl. Diff-Bindung + Gesetzestext §9/§9.1 | 13 |
| `test_memory.py` | 3 Tiers, v1–v4, PII/Poisoning/Bias-Guards, JSD/Drift | 14 |
| `test_bi_temporal.py` | valid time × transaction time, Supersede statt Löschen | 5 |
| `test_shared_memory.py` | ACL, Trust-Konflikt, Schema, Sync, Dump | 8 |
| `test_lru_cache.py` | LRU-/Value-Eviction, Adaptive Forgetting, Tier-2-Auslagerung | 10 |
| `test_ingestion.py` | Privacy/Secret-Filter, Encoding-Gate, GLiNER (real geprüft), Graph, Enrichment, Lifecycle, `route_experience` (real) | 18 |
| `test_reflective.py` | HMM-Trägheit (SEAA) real + NOOP, Hub/Forgetting, Destillation (real), Dual-Path-Retrieval, Lyapunov | 24 |
| `test_procedural_memory.py` | Skill-Snapshots, Human-Gate-Update, Rollback (`tmp_path`) | 7 |
| `test_evaluator_version.py` | Red-Queen: ε-Best-Belief, **echte HF-Anker**, Selective Erasure, Loop, **realer LLM-Grader** (json-repair/Retry/Schema), Statistik, Bootstrap-κ | 53 |
| `test_solvers.py` | 9 historische Solver-Snapshots | 20 |
| `test_pipeline.py` | Element-Pipeline: Mandat→FWR→Trust→Approval→Write→Drift, tier2→tier3, export_shared | 13 |
| `test_fwr_write.py` | Write-Aktion (§10.7): non-write→Historie, write-new→structured+tier3, write-update→tier1-Supersede | 6 |
| `test_tier2_tier3.py` | Ladepfad tier2→tier3: GAAMA-Hybrid (Cosine+PPR, d=2, Hub-Dampening), Validation-Gate | 15 |
| `test_gaama_extract.py` | GAAMA-Extraktion: Schema/Kanten (5 Typen), **realer LLM**, Graph, §10.1-Routing, §9.2c-Write-Kette | 10 |
| `test_mappings.py` | Doku-Enforcement: Skill→Prozess + Connector→Prozess + Connector-Konsistenz | 4 |
| `test_mcp_memory.py` | MCP-Memory-Server: 5 Tools + Tri-Color-Trust (echtes mcp-SDK, skip sonst) | 8 |
| `test_mandate.py` | Mandat: attenuate-nie-expand, ALLOW/REVIEW/DENY, Grant, Evidence | 9 |
| `test_agents_law.py` | AGENTS.md-Konformität (§1–§11, Guardrails, Provenienz, Versionierung, CI) | 10 |
| `test_invariants.py` | Snapshots `versions/vN` lückenlos, neuester = aktuell, Skills-Versionen, `structured/`-Pflichtfelder | 4 |
| `test_models_live.py` | Modell-IDs live (HTTP 200) — Marker `network` | 2 |
| `../pytest.ini` · `../.coveragerc` · `../Makefile` | Konfiguration, Mindest-Score, Coverage, `make test` | – |
| `../scripts/*.py` | CI-Checks: `check_md_links`, `check_artifacts`, `check_secrets`, `ci_preflight`, `ci_drift` | – |

Gesamt: **264 Tests (venv 3.12), 100 %** – real gegen Endpoint + HF-Anker.
CI-Details: `ergebnisse/ci-integration.md` (ein Job `verify`, Python 3.12).

## Was NICHT abgedeckt ist

- Nicht-Python-Dateien (Markdown/Docs/JSON) – Coverage misst Code.
- Fault-Injection-Pfade (skriptete Antworten) – per Guardrail 7 verboten;
  betroffene Zweige sind begründet als `# pragma: no cover` markiert.
