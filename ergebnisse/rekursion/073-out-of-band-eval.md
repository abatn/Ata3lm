# Rekursion 073: M3 — Out-of-Band-Evaluation (World-State-Oracle)

> Datum: 2026-10-07 · Phasen: Konstrukt → Akt → Observe → Compare (echte Tests).
> Ziel `g`: Compare soll **kein** Selbstreport-Signal akzeptieren (§6); es braucht
> ein **echtes externes Signal** (Code-Run/Datei/DB) — Out-of-Band-Evaluation.
> Status: **`pending`** (§9 `ask`: neue Quelle + Interface-Änderung; kein `self_update`).

## 1. Quellen (per `curl` real verifiziert, HTTP 200, 2026-10-07)

| Referenz | HTTP | Link |
|---|---|---|
| arXiv:2607.25152 („When Do Agent Loops Mistake Stagnation for Progress?", v2) | 200 | <https://arxiv.org/abs/2607.25152> |
| Zenodo `10.5281/zenodo.21594735` (Concept-DOI → records/21672574) | 200 | <https://doi.org/10.5281/zenodo.21594735> |

Abstract-Zitate wörtlich gegen die echte arXiv-Seite geprüft: „A world-state
oracle, unfakeable in principle …", „Self-report was thus uninformative.",
„out-of-band evaluation with real-world access is a structural requirement."
Gesetz: `AGENTS.md` §6, §1, §9 (neue Quelle/Interface ⇒ `ask`), Guardrail 2+7.

## 2. Änderung (additiv)

| Datei | Inhalt |
|---|---|
| `data/memory/world_state_oracle.py` (neu) | `evaluate(claim, probe)` → `{"ok","evidence","signal","reason","claim","successes","failures"}`; `NO_SIGNAL`/`Signal`. Ohne echtes Callable/bei Fehler ⇒ `ok=False`, `signal="kein externes Signal"` (kein Fake). |
| `data/memory/recursion_runner.py` | `_phase_compare` koppelt den Oracle: externes Signal hat Vorrang; Selbstreport nur `self_report`-Annotation; ohne Signal ⇒ `observed=False`, `gate=ask`. Neue optionale Parameter `world_state_probe`, `world_state_claim` (Default `None` ⇒ altes Verhalten). Interface-Änderung §9 kenntlich gemacht. |
| `tests/test_world_state_oracle.py` (neu) | 15 Tests: Probe True/False/`raise`/`None`/Nicht-Callable, Dict-Zähler, Compare-Kopplung (Probe False überstimmt 99/0), Legacy-Pfad. |
| `tests/test_recursion_runner.py` | bestehende Runner-Tests angepasst/erweitert. |
| `ergebnisse/out-of-band-eval.md` | Doku + Quellen + §9-Status. |

**Rückwärtskompatibel:** alle neuen Parameter optional, Default `None`; bestehende
Aufrufer erhalten `observed`/`score`/`gate` ohne `oracle` wie zuvor.

## 3. Real vs. blockiert (ehrlich)

- **Real:** `curl` HTTP-200 beider Links; Abstract-Wortlaut gematcht; 15 + 14
  Tests real ausgeführt; Probes sind echte Checks (Datei, Code, Exception); ruff clean.
- **Nicht abgeschlossen:** vollständiger `make test` — **bestehende** Live-LLM-Tests
  in `tests/test_evaluator_version.py` rufen das echte Endpoint mit bis zu 18
  Retries (`tests/_live.py`); laufen in dieser Umgebung nicht in endlicher Zeit.
  **Unabhängig von M3** (jene Datei unberührt), keine Regression.

## 4. Compare / Beleg (externes Signal: echte Tests)

```text
pytest tests/test_world_state_oracle.py --no-cov   -> 15 passed
pytest tests/test_recursion_runner.py   --no-cov   -> 14 passed
pytest {oracle,runner,gate_labels,governance,lifecycle_runner,
        write_gateway,memory,runner_state}         -> 145 passed
ruff check world_state_oracle.py test_world_state_oracle.py \
           recursion_runner.py                     -> All checks passed
```

## 5. Offene Punkte

1. **§9 Human-Gate:** neue Quelle (arXiv:2607.25152 + Zenodo) → `ask`;
   Interface-Änderung (`world_state_probe`/`world_state_claim`) → `ask`.
2. Ontologie-Eintrag der neuen Quelle erst nach menschlicher Freigabe.
3. Kein `self_update` an Originaldateien; `AGENTS.md`/`tier1-base` unverändert.

## 6. Status

**`pending`** (§9 `ask`) — kein `self_update`, kein Git (G6), keine Erfindung (G7).
