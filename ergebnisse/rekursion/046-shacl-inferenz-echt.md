# Rekursion 046: SHACL-Inferenz-Pipeline mit echter Engine

> Datum: 2026-10-04 · Tiefe: `t=45 → t=46` · Phase: **Compare → Revise**
> Freigabe: Batnini (Auftrag „go"); §9-Interface-Änderung (venv) ausdrücklich erteilt.
> Ziel `g`: SHACL-Inferenz-Pipeline mit **echter** Engine verifizieren (statt Simulation).

## 1. Quellen (verifiziert, §6)

- **swj3959** — Robaldo & Batsakis, *Semantic Web Journal* (33 S., PDF HTTP 200).
  Zitat wörtlich (S. 5): „… iteratively applies SHACL-SPARQL rules until the inferred
  graph reaches closure, prior to validation." und „… programmatically re-executes the
  SHACL-SPARQL rules until no new triples are produced, and then validates …".
- W3C SHACL-AF §8.3/§8.4 (Gegenprüfung): §8.4 „only covers a single 'iteration' … left
  to future work".

**Korrektur (§6):** „max 10 Runden wie SHACL-AF §8.3" ist **nicht belegt**. Offiziell:
pyshacl `RULES_ITERATE_LIMIT = 100` (unsere Engine), TopBraid Default 1, Triply Default 0,
W3C SHACL 1.2 impl.-abhängig, HF ohne Wert → Cap wird **aus pyshacl importiert** (= 100).

## 2. Änderung (Diff)

| Datei | Änderung |
|---|---|
| `data/memory/shacl_inferenz.py` | **neu**: `run_rules_to_fixpoint` (rdflib), `validate`/`pipeline` (pyshacl) |
| `tests/test_shacl_inferenz.py` | **neu**: 3 Tests (Zeitintervall, transitive Hülle, Cap) |
| `requirements-dev.txt` | `rdflib==7.6.0`, `pyshacl==0.40.1` |
| `ergebnisse/inferenz-shacl.md` | erweitert (echte Ausführung) |
| `ergebnisse/inferenz-shacl-test.md` | Simulations-Hinweis korrigiert |

## 3. Compare-Beleg (extern, echt)

```text
SHACL allein (explizit): conforms = True    # i2 (Ende<Beginn) verpasst
Nach Inferenz (Fixpunkt): conforms = False  # i2 erkannt
Runde 1: ex:i2 hasNegativeDuration true · Runde 2: Fixpunkt (0 neu)
pytest: 281 passed · Coverage 100 % (2257/564)
```

**Score** = 3/3 Tests = 100 %. **Drift:** additiv (1 Modul, 1 Test, 2 Docs).

## 4. Gate (§9)

- Interface-Änderung (neues Modul + venv-Pakete) → **approved** (Batnini).
- Guardrail 6: kein Commit ohne Erlaubnis. Guardrail 7: echte Engine, keine Simulation.
- §9.1b: `AGENTS.md` unverändert → kein Snapshot.
- Ehrliche Grenze: Iterations-Cap = Auftrag (nicht Paper); Fixpunkt garantiert endlich
  (Triple-Bound R×P×R, swj3959).
