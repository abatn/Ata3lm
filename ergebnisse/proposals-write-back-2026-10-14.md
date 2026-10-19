# Proposals P-A bis P-D — Write-Back-Zyklus (Θ→Θ′)

> Datum: 2026-10-14 · Status: **umgesetzt** (f8000ab, Rek. 114-116; ursprünglich Human-Gate `ask`, §9)
> Template: `ergebnisse/proposal-template.md` · Gesetz: `AGENTS.md` §6, §7, §9, §9.1c/d, §10.2, §10.3
> Keine Code-Änderung in diesem Dokument. Implementierung erst nach Freigabe.

## Gemeinsame Baseline (Quelle benannt)

| Größe | Wert | Quelle |
|---|---|---|
| Write-Back-Lauf, substring | `em_base 8 → em_adapter 22` | **extern**: Kaggle-Lauf, `theta_answers.jsonl` (vom Nutzer gemeldet; lokal nicht gegengeprüft) |
| Write-Back-Lauf, strict | `0/0` → `abstain` | **extern**: wie oben |
| Eval-Datei | 200 Zeilen, git-getrackt | `ergebnisse/zsre-eval-f6.jsonl` (`wc -l`, `git ls-files` verifiziert) |
| Leakage | 20/20 Fragen, 8/8 `pending_keys` ⊂ Eval | Nutzer-Messung; Split-Quelle `kaggle/write_back_cycle.py:114`, `scripts/drift_calibrate.py:102` |
| Grader Flush | strict (seit Rek. 115) | `kaggle/write_back_cycle.py:417` (`_grade` = `acceptance_gate.grade`; Docstring Z. 359-360) |
| Grader Probe | strict (seit Rek. 115; Präfix-Sonderfall entfällt) | `kaggle/e2e_theta_probe.py:106` |
| Grader Gate | Default `strict` | `scripts/paired_gate.py` (Argparse `--mode`) |
| Kaskade-Setup | `FWR_SMALL_MODEL` = `FWR_LARGE_MODEL` | `kaggle/write_back_cycle.py:419-420` |
| Kaskade-Defaults | nano-30b / ultra-550b (verschieden) | `data/memory/fast_write_router.py:50-51` |
| Paper-Größen | „1.7B/8B cascade" | arXiv:2608.22215 (Abstract, Nutzer-Beleg; §3.3/§10.2 in dieser Sitzung nicht gelesen) |

**Drift-Hinweis (ehrlich):** Das Tool `governance-mcp drift_index` (τ=0.02) ist in dieser Sitzung **nicht verfügbar**. Drift wird deshalb **nicht gemessen**, sondern nach Freigabe ermittelt. Für rein additive Änderungen gilt `n/a` (Rek. 112 §4).

---

## PROPOSAL P-A — Einheitlicher Grader

### 0. Metadaten
| Feld | Wert |
|---|---|
| Datum | 2026-10-14 |
| Iteration | t → t+1 |
| Phase | Konstrukt (Vorschlag) |
| Betroffenes Artefakt | `data/memory/acceptance_gate.py` (neue Grader-Funktion), Aufrufer `kaggle/write_back_cycle.py`, `kaggle/e2e_theta_probe.py` |
| Komponenten-Typ | Code + Interface |

### 1. Ziel g
- Probe, Flush und Gate entscheiden mit **derselben** explizit gewählten Metrik.
- Task-Input: die Θ′-Antworten (`theta_answers.jsonl`, Schema `{question, gold, base_answer, adapter_answer}`).

### 2. Baseline (vorher)
| Feld | Wert |
|---|---|
| π | Basis `Qwen/Qwen2.5-0.5B-Instruct` + Write-Back-Adapter |
| Score (substring, extern) | `em_adapter 22` (em_base 8) |
| Score (strict, extern) | `0/0` → abstain (Abstain-Konsequenz **historisch**: seit `4bd63cb`/Rek. 118 entscheidet der Flush nur noch pro Fakt, kein Run-Level-Abstain) |
| Signal-Quelle | Eval-Set `ergebnisse/zsre-eval-f6.jsonl` (siehe P-B: nicht disjunkt) |
| Drift-Referenz | aktueller Git-Stand vor Iteration |

### 3. Änderung (Diff, geplant, line-level)
Geplant (noch nicht angewendet):
```diff
# data/memory/acceptance_gate.py (neu, additiv)
+ def grade(gold: str, pred: str, *, mode: str = "strict") -> bool:
+     """Ein Grader für Probe, Flush und Gate. Modus explizit."""
+     ...
# kaggle/write_back_cycle.py:359
- passed = bool(gold) and gold.lower() in adapter_answer.lower()
+ passed = grade(gold, adapter_answer, mode=GRADE_MODE)
# kaggle/e2e_theta_probe.py:102
- if g and (g in p or p[: len(g)] == g):
+ if grade(gold, pred, mode=GRADE_MODE):
```
- Geänderte Komponenten: **1** (Grader-Aufruf; Flush und Probe nutzen dieselbe Funktion).
- Interface-Änderung? **ja** (neuer Aufruf; `mode` als keyword-only Default `strict` → rückwärtskompatibel).

### 4. Score-Änderung (erwartet, nicht gemessen)
- Mit `mode=substring`: Flush-Entscheidung bleibt wie heute (Teilstring); Probe-Präfix-Sonderfall entfällt (redundant).
- Mit `mode=strict`: Flush-Entscheidung kann kippen (z. B. 22 → weniger). Wird nicht vorhergesagt, sondern gemessen.
- **Δ Score:** noch nicht gemessen.

### 5. Drift
- Definition: `Δ = geänderte Zeilen / Gesamtzeilen des Artefakts` (line-level).
- Geschätzter Zeilenanteil: klein; **nicht gemessen**.
- Drift-Bound: 10 % (§9.1c, Auftrag). Überschritten: **nicht ermittelt**.

### 6. Quellen
- `scripts/paired_gate.py` `grade()` (Modi `strict`, `substring`).
- SAGE arXiv:2609.36043 (per-item paired comparison).
- Rek. 113 §3 (strict `accept` vs. substring `abstain` auf F6-Antworten).

### 7. Gate (§9)
| Bedingung | Wert | Ergebnis |
|---|---|---|
| Score | Δ noch nicht gemessen | — |
| Neue Quelle? | nein | — |
| Interface-Änderung? | ja | **ask** |
| Drift ≤ Bound? | nicht ermittelt | **ask** |

**Gate-Ergebnis: `ask`.** Offene Entscheidung: Modus `strict` oder `substring` (siehe Rückfrage).

### 8. Freigabe
- Status: **umgesetzt** (f8000ab, Rek. 114-116).

---

## PROPOSAL P-B — Disjunkter Held-out-Split

### 0. Metadaten
| Feld | Wert |
|---|---|
| Iteration | t → t+1 |
| Phase | Konstrukt |
| Betroffenes Artefakt | `kaggle/write_back_cycle.py` (Korpus-Quelle), `scripts/drift_calibrate.py` (Split-Quelle), `data/memory/zsre_corpus.py` (Aufruf) |
| Komponenten-Typ | Code + Interface |

### 1. Ziel g
- Der Write-Back-Trainingskorpus stammt aus einem Split, dessen Items nicht in der Eval-Datei stehen.
- Eval-IDs werden vor dem Training ausgeschlossen. Dadurch misst ein Treffer Generalisierung statt Memorieren.

### 2. Baseline (vorher)
| Feld | Wert |
|---|---|
| Overlap | **20/20** Fragen, **8/8** `pending_keys` ⊂ `zsre-eval-f6.jsonl` (Nutzer-Messung) |
| Score | `em_adapter 22` (substring, extern) — **kein Beleg für Generalisierung** |
| Drift-Referenz | aktueller Git-Stand |

### 3. Änderung (Diff, geplant)
```diff
# kaggle/write_back_cycle.py:114
- tasks = build_zsre_corpus(..., n=n, split="validation")
+ tasks = build_zsre_corpus(..., n=n, split=TRAIN_SPLIT, exclude_ids=EVAL_IDS)
# ein Test: assert overlap(tasks, eval_ids) == 0
```
- Geänderte Komponenten: **1** (Split-/Ausschluss-Parameter).
- Interface-Änderung? **ja** (neuer Parameter `exclude_ids`, keyword-only mit Default `None` → rückwärtskompatibel).

### 4. Score-Änderung (erwartet, nicht gemessen)
- Nach Umstellung: neuer Lauf auf disjunktem Set. Vergleich zur Baseline 8/22 nur gültig, wenn Grader (P-A) fixiert ist.
- **Δ Score:** noch nicht gemessen.
- **Kontrollprobe (P-109-Gegenprobe):** derselbe Lauf auf dem alten Overlap-Set liefert den Memorier-Effekt als Differenz.

### 5. Drift
- Geänderte Zeilen: geschätzt klein; **nicht gemessen**. Drift-Bound 10 % (§9.1c). Ergebnis: **nicht ermittelt**.

### 6. Quellen
- `ergebnisse/zsre-eval-f6.jsonl` (200 Zeilen, git-getrackt).
- Kaggle-Lauf (extern, Nutzer-Messung 20/20, 8/8).
- `ergebnisse/rekursion/103-theta-prime-negativ.md:17` (`eval_f6`, `split="validation"`).

### 7. Gate (§9)
| Bedingung | Wert | Ergebnis |
|---|---|---|
| Score | Δ nicht gemessen | — |
| Neue Quelle? | nein | — |
| Interface-Änderung? | ja | **ask** |
| Drift ≤ Bound? | nicht ermittelt | **ask** |

**Gate-Ergebnis: `ask`.**

### 8. Freigabe
- Status: **umgesetzt** (f8000ab, Rek. 114-116).
- **Offen:** Herkunft von `train_f6` (50 000 Zeilen, Rek. 103) ist **nicht verifiziert**; Disjunktheit dazu ist unbekannt.

---

## PROPOSAL P-C — Kaskade ehrlich

### 0. Metadaten
| Feld | Wert |
|---|---|
| Iteration | t → t+1 |
| Phase | Konstrukt |
| Betroffenes Artefakt | `kaggle/write_back_cycle.py:419-420` (ENV-Setup) oder `AGENTS.md` §10.2 (Behauptung) |
| Komponenten-Typ | Code/Doku + Interface |

### 1. Ziel g
Eine von zwei Varianten, **Entscheidung durch den Menschen**:
- **Variante A:** Kaskade umsetzen. `FWR_SMALL_MODEL` und `FWR_LARGE_MODEL` werden getrennt gesetzt, Laufzeitwerte protokolliert.
- **Variante B:** §10.2-Behauptung streichen oder korrigieren, weil die Kaskade in diesem Lauf nicht wirkt.

### 2. Baseline (vorher)
| Feld | Wert |
|---|---|
| Setup | `FWR_SMALL_MODEL` = `FWR_LARGE_MODEL` = `--llm-model` (`write_back_cycle.py:419-420`) |
| Defaults | nano-30b / ultra-550b (`fast_write_router.py:50-51`) |
| Paper | „1.7B/8B cascade" (arXiv:2608.22215 Abstract) |
| Score | keine Kaskade-spezifische Messung |

### 3. Änderung (Diff, geplant)
**Variante A:**
```diff
# kaggle/write_back_cycle.py:419-420
- os.environ["FWR_SMALL_MODEL"] = llm_model
- os.environ["FWR_LARGE_MODEL"] = llm_model
+ os.environ["FWR_SMALL_MODEL"] = small_model or llm_model
+ os.environ["FWR_LARGE_MODEL"] = large_model or llm_model
+ # Laufzeit-Protokoll: beide Werte in write_back_cycle_result.json
```
**Variante B:**
```diff
# AGENTS.md §10.2
- Stufe 1 (qwen3-1.7B) / Stufe 2 (qwen3-8B)  
+ (Kaskade nicht realisiert; Setup = Einzelmodell)
```
- Geänderte Komponenten: **1**.
- Interface-Änderung? A: **ja** (neue Parameter `small_model`, `large_model`, keyword-only mit Default → rückwärtskompatibel). B: **nein** (Doku).

### 4. Score-Änderung
- Keine Änderung der Score-Erwartung. **Δ n/a**, da kein Score betroffen ist.

### 5. Drift
- A: geänderte Zeilen klein; **nicht gemessen**. B: rein Doku, Drift **n/a**.

### 6. Quellen
- arXiv:2608.22215 Abstract („1.7B/8B cascade", Nutzer-Beleg). §3.3/§10.2 **nicht gelesen** → ein genauer Paper-Beleg für die Stufenzuordnung ist **offen**.
- Code: `kaggle/write_back_cycle.py:419-420`, `data/memory/fast_write_router.py:50-51`.

### 7. Gate (§9)
| Bedingung | Wert | Ergebnis |
|---|---|---|
| Score | n/a | — |
| Neue Quelle? | nein | — |
| Interface-Änderung? | A: ja / B: nein | **ask** (A) |
| Drift ≤ Bound? | nicht ermittelt | **ask** |

**Gate-Ergebnis: `ask`.** Entscheidung: Variante A oder B (siehe Rückfrage).

### 8. Freigabe
- Status: **umgesetzt** (f8000ab, Rek. 114-116).

---

## PROPOSAL P-D — §9.1d-Nachtrag

### 0. Metadaten
| Feld | Wert |
|---|---|
| Iteration | t → t+1 |
| Phase | Observe / Doku |
| Betroffenes Artefakt | `ergebnisse/rekursion/109-write-back-cycle-lauf.md`, `ergebnisse/rekursion/113-paired-gate-echtlauf.md` (Nachtrag), künftige Rek.-Doks |
| Komponenten-Typ | Doku |

### 1. Ziel g
Jede Rekursion enthält Score-Δ, Diff und Drift gemäß `ergebnisse/proposal-template.md`. Für Rek. 109 und 113 wird ein ehrlicher Nachtrag geschrieben.

### 2. Baseline (vorher)
- Rek. 109: Score (2/8 flushed, Teilstring), kein Diff, kein Drift.
- Rek. 113: `accept` (strict, 6/0) und `abstain` (substring), kein Diff, kein Drift.

### 3. Änderung (Diff, geplant)
```diff
# ergebnisse/rekursion/109-...md  + "## Nachtrag §9.1d"
+ Diff: nicht gemessen (kein Code-Diff in dieser Iteration dokumentiert)
+ Drift: nicht gemessen (governance-mcp nicht verfügbar)
```
- Interface-Änderung? **nein** (Doku).

### 4. Score-Änderung
- Keine neuen Messungen. **Δ n/a**.

### 5. Drift
- **n/a** (Doku-Änderung).

### 6. Quellen
- `ergebnisse/proposal-template.md` (§9.1d).
- AGENTS.md §9.1d (Evidenz-Pflicht), §6 (keine Erfindung).

### 7. Gate (§9)
| Bedingung | Wert | Ergebnis |
|---|---|---|
| Score | n/a | — |
| Interface? | nein | — |
| Drift | n/a | — |

**Gate-Ergebnis: `ask`** (vorsichtshalber, da freigegebene Iterationen nachträglich verändert werden).

### 8. Freigabe
- Status: **umgesetzt** (f8000ab, Rek. 114-116).

---

## Offene Entscheidungen (vor Start, §9)

1. **P-A-Modus:** `strict` oder `substring`?
2. **P-C-Variante:** A (Kaskade umsetzen) oder B (Behauptung streichen)?

Bei self_update zusätzlich zwei Freigaben (§9.3: Batnini + Taoufik).

## Nicht verifiziert / offen

- Externe Baseline (substring 8→22, strict 0/0) ist nur gemeldet, lokal nicht gegengeprüft.
- `train_f6`-Herkunft und Disjunktheit: unbekannt.
- Drift: nicht messbar in dieser Sitzung.
- arXiv:2608.22215 §3.3/§10.2: nicht gelesen.
