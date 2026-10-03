# Rekursion 042: CI-Integration (Doku · Artefakte · Security · Endpoint · Modelle · Snapshots · Drift)

> Datum: 2026-10-03 · Tiefe: `t=41 → t=42` · Phase: **Revise → Handeln**
> Freigabe: `approved: Batnini, 2026-10-03` (Auftrag „führe der plan mit multi agent").
> Ziel `g`: die in der CI fehlenden Elemente (A–O) integrieren — **ein Job, eine Umgebung 3.12**.

## 1. Quellen / Gesetz

- AGENTS.md §4 (Interface-Stabilität), §6 (Belege), §9.1b (Versionierung),
  §9.1c (Drift), §9.1d (Proposal), §9.2a/c (Privacy/Poisoning), §10.2 (Modelle),
  §11 (lokale Basis = Pflicht, extern optional), Guardrails 3/6/7.

## 2. Änderung (Diff)

| Datei | Änderung |
|---|---|
| `.github/workflows/ci.yml` | **ein** Job `verify` (3.12): Ruff → Markdown(advisory) → Link-/Artefakt-/Secret-Check → Preflight → Tests |
| `scripts/check_md_links.py`, `check_artifacts.py`, `check_secrets.py`, `ci_preflight.py`, `ci_drift.py` | **neu** |
| `tests/test_invariants.py`, `tests/test_models_live.py` | **neu** |
| `tests/test_mappings.py`, `tests/test_agents_law.py` | erweitert (Connector-Konsistenz; alle `vN`; Index-Vollständigkeit) |
| `.gitleaks.toml`, `.pymarkdown.json` | **neu** (Security-Allowlist; Markdown-Config) |
| `requirements-dev.txt`, `pytest.ini` | `pymarkdownlnt`; Marker `live` |
| `ergebnisse/ci-integration.md` | **neu** |

## 3. Compare-Beleg

```text
scripts: md_links 0 fehlend · artifacts 0 Fehler · secrets 0 Treffer · drift OK
offline neue Tests: 18 passed · ruff clean
```

## 4. Gate (§9)

- CI-/Interface-Änderung → **approved** (Batnini).
- §9.1d: Diff/Score/Drift siehe `ergebnisse/proposals-038-041.md` (Nachtrag 042).
- §9.1b: `AGENTS.md` **unverändert** → kein neuer Snapshot.
- §11: Endpoint-Ausfall → CI **rot**, kein Fake-Fallback.

## 5. Nächstes Self-Feedback (t+1)

- Optionaler Nightly-Job für Live-MCPs (D) und Nicht-Ubuntu (L).
