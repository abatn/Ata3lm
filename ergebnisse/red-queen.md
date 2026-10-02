# Red-Queen-Ko-Evolution: versionierte Evaluatoren mit Ground-Truth-Anker

> Datum: 2026-10-01 · Auftrag: „Implementiere die Red-Queen-Ko-Evolution …
> nach Cambridge (Juli 2026). Erfindung ist verboten." · Lab-Prinzip §6: nur was
> in der Quelle steht; Projekt-Gesetz §9 für die Verhaltensänderung.

## 1. Quelle (verifiziert 2026-10-01, alle HTTP 200)

| Quelle | Belegte Aussage (wörtlich) | Link |
|---|---|---|
| The Red Queen Gödel Machine: Co-Evolving Agents and Their Evaluators (arXiv:2606.26294, Cambridge + NVIDIA + Flower Labs + MBZUAI + Inria, Preprint 24.06.2026) | „search is organized into **epochs** with a fixed within-epoch evaluation criterion, while the utility can be updated at **epoch boundaries**"; „At checkpoints, a stronger evaluator can replace the old one if it performs better on **trusted ground-truth examples**"; „**Selective Erasure** … all utility records … produced by the old evaluator are deleted … data from 'evaluator-independent' sources … is retained"; „co-evolved graders reach **9% higher ground-truth accuracy**" | https://arxiv.org/abs/2606.26294 |
| University of Cambridge, Dept. of CS & Technology, News 21.07.2026 | „As the agent gets better, the evaluation also gets harder, and the bar keeps rising"; „At checkpoints, a stronger evaluator can replace the old one if it performs better on trusted ground-truth examples. Scores from the old evaluator are then removed." | https://www.cst.cam.ac.uk/news/red-queen-hypothesis-new-way-forward-self-improving-ai |

**Die 9 %** stehen nur als dokumentierte Kennzahl im Code
(`CAMBRIDGE_GRADER_GAIN = 0.09`) – sie wird hier **nicht** simuliert und **nicht**
als eigene Messung ausgegeben.

## 2. Was gebaut wurde

`data/memory/evaluator_version.py` (additiv, kein bestehender Prozess aufgerufen):

| Baustein | Quelle (RQGM) |
|---|---|
| `EvaluatorVersion(version, verdict_fn)` – Versionen `evaluator_v1`, `v2`, … | „Evaluator slot"; Versionierung ist Projekt-Umsetzung der Epochen |
| `GroundTruthAnchor.accuracy()` – vertrauenswürdige, menschlich geprüfte Checkpoints | „trusted ground-truth examples" / „Ground-Truth Anchor" |
| `RedQueen.checkpoint(candidate, approved)` – Ersatz **nur** wenn Kandidat auf dem Anker besser | „a stronger evaluator can replace the old one if it performs better on trusted ground-truth examples" |
| `RedQueen.selective_erasure(old)` – löscht Records des alten Evaluators, behält evaluator-unabhängige | „all utility records … produced by the old evaluator are deleted … evaluator-independent sources … retained" |
| `RedQueen.report()['evaluator_ceiling_avoided']` | Ziel des Auftrags: „Verhindert das Evaluator-Ceiling" (RQGM-Motivation: fixer Evaluator = Decke) |

**§9-Anbindung:** Der Evaluator-Wechsel ist ein `self_update` → nur mit
`approved`. Ohne `approved` bleibt der Kandidat `pending` (`gate="ask"`),
obwohl er besser ist – es wird nichts stillschweigend ersetzt.

## 3. Simulation: 3 Evaluator-Versionen mit steigender Schwierigkeit

Anker (Auftrag, **keine** Paper-Zahl): 10 Proofs mit `quality`, Ground-Truth =
`quality ≥ 0.7`. Evaluatoren: v1 akzeptiert alles, v2 ab 0.5, v3 ab 0.7.

Rohtext (`python3 data/memory/evaluator_version.py`, gekürzt):

```text
Epoche 1 : evaluator_v1 | Anker 0.4 | gate allow
Checkpoint 2 (ohne approved): pending | gate ask
Epoche 2 : evaluator_v2 | Anker 0.7 | ersetzt evaluator_v1 | geloescht 1
Epoche 3 : evaluator_v3 | Anker 1.0 | ersetzt evaluator_v2 | geloescht 1
Report   : {"current": "evaluator_v3",
            "versions": [{"version": "evaluator_v1", "accuracy": 0.4},
                         {"version": "evaluator_v2", "accuracy": 0.7},
                         {"version": "evaluator_v3", "accuracy": 1.0}],
            "archive_size": 2, "evaluator_ceiling_avoided": true}
Archiv   : [('gt-unit-1', 'evaluator_v1', True), ('gt-unit-2', 'evaluator_v2', True)]
Paper    : 0.09
```

Lesart:

1. **Epoche 1** startet mit `evaluator_v1` (Anker 0.4).
2. Checkpoint 2: v2 ist besser (0.7), aber **ohne `approved`** → `pending`
   (§9), nichts ersetzt.
3. Mit `approved` → `evaluator_v2` ersetzt `evaluator_v1`; **Selective Erasure**
   löscht 1 v1-Record.
4. Checkpoint 3 → `evaluator_v3` (Anker 1.0), löscht 1 v2-Record.
5. Die **evaluator-unabhängigen** Anker-Records (`gt-unit-1/2`) überleben beide
   Erasures – wie in der Quelle.

## 4. Test + Compare-Beleg

```text
make test  → 132 passed · Coverage 1272/1272 Statements · 274/274 Branches = 100,00 %
```

Neue Tests (`tests/test_evaluator_version.py`, 10):

| Test | Prüft |
|---|---|
| `test_accuracy_und_leerer_anker` | Anker-Genauigkeit + leerer Anker → 0.0 |
| `test_checkpoint_initial_setzt_evaluator_v1` | Versionierung startet bei `evaluator_v1` |
| `test_checkpoint_schwaecheren_kandidat_ablehnen` | schlechterer Kandidat → `deny`, kein Wechsel |
| `test_checkpoint_besser_ohne_approved_ist_pending` | besser, aber §9 → `pending`/`ask` |
| `test_checkpoint_besser_mit_approved_promoted_und_erasure` | Promotion + Erasure |
| `test_selective_erasure_behaelt_andere_evaluatoren` | fremde Evaluator-Records + Anker bleiben |
| `test_record_ohne_und_mit_evaluator` | Record-Pfad |
| `test_simulate_3_evaluatoren_steigende_schwierigkeit` | v1 < v2 < v3, Ceiling vermieden, 9 %-Kennzahl |
| `test_report_ohne_evaluator` | Report ohne aktiven Evaluator |

## 5. Gate / Drift (§9)

- **Keine Verhaltensänderung:** Das Modul ist **nicht verdrahtet** (kein
  bestehender Prozess importiert es). Ein Einbau in `reflective_agent`/den
  Rekursions-Loop wäre eine eigene Verhaltensänderung → eigenes Human-Gate.
- **Neue Quelle:** arXiv:2606.26294 ist neu (nicht in der Ontologie). §9 verlangt
  dafür ein menschliches Gate – der Auftrag selbst ist diese Entscheidung; das
  Modul hält die Quelle als Kommentar, `AGENTS.md` wird **nicht** geändert.
- **§9.3:** zweite Freigabe-Person weiterhin offen (wie 031/032).
- **Drift:** nur neue Dateien (Modul + Test + Doku); keine bestehende
  Python-Datei geändert → Drift 0 %.

## 6. Ehrliche Grenzen

- Die **9 %** sind eine Paper-Kennzahl, **keine** eigene Messung. Hier wurde
  keine 9 %-Verbesserung erzeugt – die Simulation zeigt nur das Mechanik-Muster
  (0.4 → 0.7 → 1.0) auf einem Auftrags-Anker.
- Der Anker ist synthetisch (Auftrag). Echte Ground-Truth-Checkpoints fehlen.
- Kein echter LLM-Evaluator: `verdict_fn` ist deterministisch; die RQGM nutzt
  gelernte Evaluatoren.

## 7. Reproduktion

```bash
python3 data/memory/evaluator_version.py
python3 -m pytest tests/test_evaluator_version.py -v
make test
```
