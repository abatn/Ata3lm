# P3b — CI-Korrekturen (F1–F5)

> Datum: 2026-10-05 · Status: **Auftrag** (Fixes). Freigabe: `approved` (Batnini). Guardrail 6: kein Commit.

## 1. Befunde (RED verifiziert) + Fixes

| # | Befund | Fix | Regel |
|---|---|---|---|
| **F1** | `ci_preflight.py` las nur `os.environ` → FAIL ohne Export | `_load_opencode_keys()` (wie `tests/conftest.py`); Env hat Vorrang, sonst `opencode.json`; **kein** Key-Output | §9.1d / Guardrail 7 |
| **F2a** | `ci_drift`/`gitleaks` nicht in `ci.yml` | beide verdrahtet (blockierend); `fetch-depth: 2` | §9.1d |
| **F2b** | **`ci_drift.py` war wirkungslos** (verglich Arbeitsbaum↔HEAD → in CI immer sauber) | Basis via `CI_DRIFT_BASE` (CI: `HEAD~1`) → prüft den **gepushten Commit** | §9.1d |
| **F3** | `AGENTS.md` MD034 (bare URLs) | bare URLs → `<…>`; MD034 = **0** (inhaltlich intakt) | §6 |
| **F3b** | §9.1b-Versionierung fehlte | `versions/v10/` (5 Dateien, `AGENTS.md` = neu) + `versions/README.md` (v1–v10) | §9.1b |
| **F4** | Doku-Sollzahlen veraltet (337/324) | **Nur Fußnote „Stand 064: 359"** in historische Docs — Zahlen NICHT überschrieben (Provenienz) | §3/§9.1d |
| **F5** | Doku/Provenienz | dieses Dokument + Rekursion 065 + Index-Zeile | Guardrail 3 |

## 2. Belege (echt)

```text
F1: ci_preflight ohne Export -> liest opencode.json -> echter Call OK („Pong"). Test: 2
F2: ci.yml enthält gitleaks-Action + ci_drift.py (CI_DRIFT_BASE=HEAD~1); Law-Test erweitert
F2b: CI_DRIFT_BASE=HEAD~1 -> prüft HEAD~1..HEAD (nicht leerer Arbeitsbaum-Diff)
F3: pymarkdown MD034 (AGENTS.md) = 0
F3b: versions/v10 + versions/README.md vorhanden
F4: Fußnote in 4 historischen Docs (Zahlen unverändert)
```

## 3. Gate (§9)

- CI-/Gesetzes-/Interface-Änderungen → **approved** (Batnini). §9.1b: `versions/v10` + README angelegt.
- Guardrail 6: **kein Commit**. Guardrail 7: echter Preflight-Call.
- **Offen (P3c):** echter Preflight in CI, beide Router-Modelle live, 8-Stufen mit echter Reflexion, externer MCP-Fallback.
