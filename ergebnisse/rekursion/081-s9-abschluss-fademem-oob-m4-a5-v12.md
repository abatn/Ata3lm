# Rekursion 081: §9-Abschluss — FadeMem + Out-of-Band (OOB) + M4 + A5 + `versions/v12`

> Datum: 2026-10-08 · Phasen: Konstrukt → Akt → Observe → Compare (echte Tests).
> Ziel `g`: die offenen §9-Punkte mit vorliegender menschlicher Freigabe
> (**Batnini + Taoufik, 2 distinkte Personen, 2026-10-08**) abschließen: zwei
> belegte Quellen in die Ontologie aufnehmen (FadeMem, OOB), die A5-Ontologie-
> Bezüge schließen, die Rekursionen 073/074 und `fademem.md` auf `approved`
> setzen und die Tier-1-Änderung nach §9.1b als `versions/v12` versionieren.
> Status: **`approved`** (Batnini + Taoufik, 2026-10-08).

## 1. Soll / Ist

| Punkt | Soll | Ist (vorher) | Ist (nachher) |
|---|---|---|---|
| FadeMem-Quelle | in `ontology.md` §C | fehlt | Zeile ergänzt (IEEE DOI + arXiv) |
| OOB-/World-State-Oracle-Quelle | in `ontology.md` §C | fehlt | Zeile ergänzt (Zenodo DOI + arXiv) |
| A5-Ontologie-Bezüge (3 `structured/`) | `offen (§4 – Klärung ausstehend)` | offen | Stufe + §-Bezug + Freigabe |
| 073 OOB-Eval | `pending`/`ask` | pending | `approved` |
| 074 M4-Lifecycle | `pending`/`ask` | ask | `approved` |
| `fademem.md` | `ask (neue Quelle)` | ask | `approved` (Default-Wechsel offen) |
| Versionierung §9.1b | `versions/v12` | fehlt | 5 byte-identische Kopien |

## 2. Quellen (real, per `curl`/DOI geprüft — bereits in 073/`fademem.md`)

| Referenz | Link |
|---|---|
| FadeMem (ICASSP 2026), IEEE DOI `10.1109/icassp55912.2026.11462095` | <https://arxiv.org/abs/2601.18642> |
| OOB / World-State-Oracle, Zenodo DOI `10.5281/zenodo.21594735` | <https://arxiv.org/abs/2607.25152> |

Beide sind **keine** Erfindung: Volltexte + DOIs wurden bereits in
`ergebnisse/fademem.md` (curl HTTP 200/202, 2026-10-07) und
`ergebnisse/rekursion/073-out-of-band-eval.md` (curl HTTP 200, 2026-10-07) belegt.

## 3. Änderungen

| Datei | Inhalt |
|---|---|
| `data/memory/tier1-base/ontology.md` | §C: 2 Zeilen ergänzt (FadeMem, OOB) nach der ZsRE-Zeile. |
| `knowledge/structured/was-ist-die-standard-drift-grenze-in-agents-md-abschnitt-9-1.md` | A5-Bezug → „Denken (5) — Drift-/Damping (§9.1c)“. |
| `knowledge/structured/welche-zwei-personen-bestaetigen-den-approved-flow.md` | A5-Bezug → „Handeln (7) — Freigabe vor Handeln (§9.3)“. |
| `knowledge/structured/wo-wird-der-write-back-slow-consolidation-geregelt.md` | A5-Bezug → „Wissen+ (8) — Modell-Rückschreiben (§10.3)“. |
| `ergebnisse/rekursion/073-out-of-band-eval.md` | §9-Status `pending` → `approved` (Batnini + Taoufik, 2026-10-08). |
| `ergebnisse/rekursion/074-m4-lifecycle.md` | §9-Status `ask` → `approved` (Batnini + Taoufik, 2026-10-08). |
| `ergebnisse/fademem.md` | §9-Status `ask (neue Quelle)` → `approved`; Default-Wechsel bleibt offen. |
| `data/memory/tier1-base/versions/v12/` | Neu: byte-identische Kopien (§9.1b) von `AGENTS.md`, `identity.md`, `ontology.md`, `core-relations.md`, `episodic_graph.json`. |
| `data/memory/tier1-base/versions/README.md` | Tabellenzeile `v12`. |
| `ergebnisse/rekursion/081-…md` | Diese Doku + Index-Zeile. |

**Unverändert:** `AGENTS.md` (root) — keine Gesetzesänderung. Kein `.py`-Code
geändert, daher keine ruff-Relevanz.

## 4. Compare / Beleg (externes Signal: echte Tests + `cmp`)

```text
pytest tests/test_invariants.py tests/test_agents_law.py -q --no-cov -> 15 passed
pytest -m "not network and not live" -q --no-cov                    -> 585 passed, 27 deselected
cmp v12/{AGENTS.md,identity.md,ontology.md,core-relations.md,episodic_graph.json}
        vs. Quelle                                                   -> identisch (5/5)
```

## 5. §9-Status

**`approved`** (Batnini + Taoufik, 2 distinkte Personen, 2026-10-08). Kein Git
(Guardrail 6), keine Erfindung (Guardrail 7).
