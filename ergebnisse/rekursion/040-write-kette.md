# Rekursion 040: Write-Kette §9.2c → §9.2a → §10.1 → Write

> Datum: 2026-10-03 · Tiefe: `t=39 → t=40` · Phase: **Handeln → Wissen+**
> Freigabe: `approved: Batnini, 2026-10-03` („führe die nächste Phase … nach AGENTS.md").
> Ziel `g`: persistente Write-Kette für extrahierte Facts gesetzeskonform schließen.

## 1. Quellen

- AGENTS.md **§9.2c** (Poisoning-Guard: „Nur **verifizierte** Items werden gespeichert:
  trusted origin **und** verified"), **§9.2a** (PII vor Store), **§10.1** (FWR zuerst).
- Implementierung: `data/memory/trust.py` (`PoisoningGuard`, `PIIFilter`),
  `data/memory/fast_write_router.py` (`classify`, `apply_write_action`).

## 2. Änderung (Diff)

| Datei | Änderung |
|---|---|
| `data/memory/gaama_extract.py` | + `persist_extracted_facts(...)` — Kette §9.2c → §9.2a → §10.1 → Write (guard/classify_fn/write_fn injizierbar) |
| `tests/test_gaama_extract.py` | +2 Tests (Gate+PII+FWR; non-write) |
| `ergebnisse/tier2-tier3.md`, `ergebnisse/gaama-schema.md`, `connectors/gaama.md`, `tests/README.md`, `ergebnisse/verbindungen-diagramm.md` | nachgezogen |

## 3. Compare-Beleg (extern)

```text
make test -> 262 passed · Coverage 100,00 % (Line+Branch) · ruff clean
```

**Score** = 262/262 = **100 %**. **Drift:** additiv (neue Funktion + Tests); unter
Drift-Bound (10 %).

## 4. Gate (§9)

- Neue Funktion (Interface-Erweiterung) → Freigabe erteilt.
- §9.1d: Diff/Score/Drift in `ergebnisse/proposals-038-041.md` (Proposal 040). §9.1b: `AGENTS.md` unverändert → kein Snapshot.
- §9.2c-Gate wirkt real: untrusted/nicht-verifiziert → `admitted=False`, **kein** Write.

## 5. Nächstes Self-Feedback (t+1)

- Live-Lauf mit echtem LLM-Extraktor (externes Compare-Signal §6) — optional.
- Kognition (Stufe 4): GAAMA-Retrieval in den `reflective_agent`-Antwortpfad einbinden.
