# CI-Integration (ein Job, Python 3.12) — nach AGENTS.md

> Datum: 2026-10-03 · Status: **Auftrag** (Betriebsregel) + **Belegt** (Regeln aus AGENTS.md).
> Ziel: Lücken der alten CI schließen (Doku, Artefakte, Security, Endpoint, Modelle,
> Snapshots, Drift, Provenienz) — **alles in einem Job / einer Umgebung**.

## 1. Entscheidung: eine Umgebung (Python 3.12)

- `mcp[cli]` hat `requires-python >= 3.10` (`requirements-dev.txt:13`) → 3.9 kann die
  volle Menge nicht. Daher **keine 3.9-Matrix**, ein Job `verify` auf **3.12**.
- Quelle/Regel: AGENTS.md §4 (Interface-Stabilität), §11 (lokale Basis = Pflicht).

## 2. Job `verify` (Reihenfolge, `.github/workflows/ci.yml`)

| Schritt | Zweck | Element |
|---|---|---|
| `ruff check` + `ruff format --check` | Lint/Format (`.py`) | — |
| `pymarkdown … scan .` (advisory) | Markdown-Lint (Legacy-Doku → nicht blockierend) | **A** |
| `scripts/check_md_links.py` | interne Links gültig | **A** |
| `scripts/check_artifacts.py` | JSON/YAML/TOML parsen, `.dot`→`dot -Tsvg` | **C** |
| `scripts/check_secrets.py` | Secret-/Key-Muster (mit Beispiel-Allowlist) | **G** |
| `scripts/ci_preflight.py` | echter Endpoint-Call (Gate) | **E** |
| `make test` (wenn Preflight ok) | echte Tests, 100 % | §6/Guardrail 7 |
| sonst: „blockiert" | **kein** Fake-Fallback (§11) | **E** |

## 3. Neue Tests (offline, regelgebunden)

| Test | Prüft | Regel |
|---|---|---|
| `tests/test_invariants.py` | `versions/vN` lückenlos + Inhalt; neuester Snapshot = `AGENTS.md`; Skills-Versionen; `structured/`-Pflichtfelder | §9.1b, §6 |
| `tests/test_models_live.py` (Marker `network`) | Modell-IDs live (HTTP 200) | §6, §10.2 |
| `tests/test_mappings.py` (+`test_connectors_konsistenz`) | Connector-Refs existieren; Header-Zahl = reale Anzahl | §6 |
| `tests/test_agents_law.py` (+`test_versionierung_alle_vN`, +`test_rekursion_index_vollstaendig`) | **alle** `vN`; jede Rekursion im Index | §9.1b, Guardrail 3 |

## 4. Grenzen (ehrlich)

- **K Branch Protection:** privat/Free → Repo public **oder** GitHub Pro nötig.
- **L Windows/macOS:** nicht in der Matrix (Kosten).
- **D Live-MCPs** (Graphiti/Cognee/…): nicht pro Push; optionaler Nightly-Job.
- **E Endpoint-Ausfall:** CI wird **rot** (keine echten Tests möglich, kein Fake) — §11.

## 5. Quellen

- AGENTS.md §4, §6, §9, §9.1b/c/d, §9.2a/c, §10.2, §11, Guardrails 3/6/7.
- CI: `.github/workflows/ci.yml` · Skripte: `scripts/`.
