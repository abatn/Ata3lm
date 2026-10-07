# Rekursion 074: M4 — Geschlossener Lifecycle (Router „senses consolidation" → discard)

> Datum: 2026-10-07 · Phasen: Konstrukt → Akt → Observe → Compare (echte Tests).
> Ziel `g` (§10.1/§10.3): Nach **erfolgreicher** Konsolidierung (M1, Adapter
> `Batnini/knowledge-agent-sft-lora`) soll der **Fast Write Router**
> bereits-konsolidierte Fakten als **`non-write`** behandeln (nicht erneut extern
> speichern). Quelle steht **im Gesetz**: arXiv:2608.22215 §3.4 — „the router
> adaptively suppress redundant writes as the model's epistemic boundaries evolve".
> Status: **`ask`** (§9: Interface-Änderung; kein `self_update`).

## 1. Quellen (per `curl` real verifiziert)

| Referenz | HTTP | Link |
|---|---|---|
| arXiv:2608.22215 („Dual-Layer Agentic Memory with Fast Write Routing and Slow Consolidation", §3.4) | 200 | <https://arxiv.org/abs/2608.22215> |

Wörtliches Zitat §3.4 (im Gesetz AGENTS.md §10.1/§10.3 referenziert): „the router
adaptively suppress redundant writes as the model's epistemic boundaries evolve".
Gesetz: `AGENTS.md` §10.1, §10.3, §9 (Interface-Änderung ⇒ `ask`), Guardrail 7.
Keine neue Quelle → **kein** neuer Ontologie-Eintrag nötig.

## 2. Änderung (additiv, rückwärtskompatibel)

| Datei | Inhalt |
|---|---|
| `data/memory/fast_write_router.py` | Neuer Hook `discard_if_consolidated(fact, question=None, state_path=None)` + `_slug`. Liest den Konsolidierungs-State (`slow_consolidation._load_state`, `consolidation-state.json`); Treffer ⇒ `{"class":"non-write","gate":"none","reason":"bereits konsolidiert (§10.3)","consolidated_key":…}`, sonst `None`. `classify(..., state_path=None)` schließt bei Treffer die Kaskade kurz (`stage=0`, kein LLM). `apply_write_action(..., state_path=None)` stuft eine angeforderte `write-new`/`write-update` auf `non-write` herab (`discarded=True`). |
| `tests/test_lifecycle_discard.py` (neu) | 9 Tests: (a) konsolidiert ⇒ `non-write` (Hook/classify/apply), (b) nicht-konsolidiert ⇒ unverändert (Gate hält bei `ask`, mit Freigabe schreibt es), (c) Default `None` ⇒ kein Effekt, plus Randfälle (leerer/fehlender State, ohne Frage/Fakt, **echter** Projekt-State). Kein Netz. |
| `ergebnisse/rekursion/074-m4-lifecycle.md` | Diese Doku + Quellen + §9-Status. |
| `ergebnisse/rekursion/README.md` | Index-Zeile 074. |

**Rückwärtskompatibel:** Default `state_path=None` ⇒ exakt altes Verhalten
(`discard_if_consolidated` → `None`); kein bestehender Aufrufer/Tests bricht.

**§9-Gate (Auftrag):** `gate="none"` ist der bestehende Legacy-Alias von
`fast_write_router` (`gate_labels._CANONICAL: "none" → allow`), **kein** neuer
Labelraum. Non-write ⇒ `allow`; kein Human-Gate nötig.

## 3. Real vs. blockiert (ehrlich)

- **Real:** Quellen-`curl` HTTP-200; `discard_if_consolidated` liest den echten
  Konsolidierungs-State (inkl. Projekt-Datei); 9 neue Tests + 8 `test_fwr_write`
  offline; `test_fwr.py` **voll** (12, inkl. echter LLM-Calls) grün; ruff clean.
- **Zuordnung = Auftrag:** Key-Zuordnung `_slug(question)` ist an
  `collect_pending`/§10.7 gebunden (Projektregel), kein Paper-Claim. Das Paper
  routet operational binär „write or discard" (§3.3); das `non-write`-Label ist
  Projekt-§10.7.
- **Nicht abgeschlossen:** vollständiger `make test` (100 %-Coverage über alle
  Module) hier nicht gefahren — die **Live-LLM**-Tests des Repos laufen langsam;
  M4-Code selbst ist offline vollständig (inkl. Branches) abgedeckt.

## 4. Compare / Beleg (externes Signal: echte Tests)

```text
pytest tests/test_lifecycle_discard.py tests/test_fwr_write.py --no-cov -> 17 passed
pytest tests/test_fwr.py --no-cov                                        -> 12 passed (inkl. live)
pytest tests/test_fwr.py -k "modelle or refusal or memrouter or embed_router
        or compare_router or decide or import_ohne" --no-cov            ->  7 passed
ruff check fast_write_router.py test_lifecycle_discard.py                -> All checks passed
```

## 5. Offene Punkte

1. **§9 Human-Gate:** Interface-Änderung (`state_path`, neuer Hook) → `ask`.
2. Kein `self_update` an Originaldateien; `AGENTS.md`/`tier1-base` unverändert.
3. Voller `make test` (Coverage-Gate) steht aus (siehe §3).

## 6. Status

`ask` — kein `self_update`, kein Git (G6), keine Erfindung (G7).
