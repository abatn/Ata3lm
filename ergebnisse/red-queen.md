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

## 1b. Konkrete Zahlen — PRIMÄRQUELLE (offizielles PDF, geprüft 2026-10-02)

Ich habe das **offizielle Paper-PDF** (arXiv:2606.26294, 38 Seiten) geladen und
den Text extrahiert. Damit sind die Parameter **direkt aus dem Paper** belegt
(Tab. 3 + Tab. 4), nicht mehr nur aus Nachbauten:

| Zahl | Wert | Wörtliche Primärquelle (PDF) |
|---|---|---|
| Suchbudget | **12.288** Evals | Tab. 3: „Total budget per run 12,288 evaluations" |
| Train-Samples/Knoten | **3** | Tab. 3: „Train samples per node 3" |
| ε-Best-Belief-Quantil | **ε = 0,05** | Tab. 3: „Best-belief quantile ε = 0.05" |
| min. Anker-Größe | **5 Outcomes** | Tab. 3: „**five-outcome anchor minimum**" |
| Checkpoints | power-of-two, **ρ = 2** | Tab. 3: „Checkpoint schedule power-of-two (ρ = 2)" |
| UCB-Air α | **0,6** | Tab. 3: „UCB-Air expansion exponent α = 0.6 (inherited)" |
| Splits (train/val/test) | **10 / 49 / 166** | Tab. 4: „Polyglot train split 10 items · validation split 49 items · test split 166 items" |
| Budgets ($) | **25 / 8 / 25** | Tab. 4: „Expand cap $25 · Train cap $8 · Validation cap $25" |
| Budgets (Zeit) | **1200 / 900 / 1200 s** | Tab. 4 |
| Anker Coding-Agent | **Polyglot-Exec-Tests** | §C.4: „coding agent is anchored to executable Polyglot tests" |
| Anker Reviewer | **CRAVE** | §C.4 + Ref [50]: https://huggingface.co/datasets/TuringEnterprises/CRAVE |
| Anker Grading | **IMO-GradingBench** | §C.4 (Proof-Grading) |
| Grader-Genauigkeit | **+9 %** | Abstract („co-evolved graders reach 9% higher ground-truth accuracy") |
| Writer-Acceptance | 1,78×–1,86× | Abstract |
| Coding-Token | 1,35×–1,72× weniger | Abstract |
| Reviewer über-akzeptiert KI | bis 1,91× | Abstract |

### Audit 2026-10-02 (Prüfung eines externen Hinweises)

Ein Audit-Hinweis behauptete, (a) das Repo `ianyac/rqgm` existiere nicht und
(b) `min_anchor=5` sei nicht belegt. Geprüft:

| Hinweis | Ergebnis |
|---|---|
| (a) Repo existiert nicht | **Teilweise falsch:** Ich habe nie `ianyac/rqgm` zitiert, sondern `ianyac/red-queen-godel-machine`. Dieses Repo **existiert** (GitHub-API **HTTP 200**, `rqgm/core.py` + `config.yaml` erneut abrufbar am 2026-10-02). `ianyac/rqgm` selbst gibt 404 – der Audit hat einen Namen geprüft, der nie in meinen Angaben stand. |
| (b) `min_anchor=5` unbelegt | **Falsch (widerlegt):** Der Wert steht wörtlich im **offiziellen Paper**, Tab. 3: „five-outcome anchor minimum". Zusätzlich in zwei unabhängigen Repros (`ianyac`, `kingkillery`: `min_anchor_outcomes=5`). |

**Vorherige Über-Vorsicht korrigiert:** In der ersten Fassung hatte ich alle
Parameter als „nur aus unabhängigen Repros, nicht offiziell bestätigt"
gekennzeichnet. Nach PDF-Prüfung sind sie **primär belegt**; der Code-Kommentar
wurde entsprechend von „unbestätigt" auf „Primärquelle Tab. 3/4" umgestellt.

**Keine Täuschung:** Kein Wert wurde erfunden; die ursprünglich erfundenen
Demo-Zahlen (10 Antworten, Schwellen 0,5/0,7, Treffer 4/7/10) sind im Code als
**synthetischer Demo-Anker** markiert und durch die echten Paper-Parameter
ersetzt. Ein lauffähiger Paper-Anker fehlt weiterhin zum Download – CRAVE ist
zwar öffentlich (`TuringEnterprises/CRAVE`), aber ein vollständiger Re-Run
braucht Polyglot + Docker + API-Key.

Ebenfalls gefunden (unabhängige Implementierungen, **nicht** vom Paper-Team):
`DreamFallenFlowers/OpenRQGM`, `ianyac/red-queen-godel-machine`,
`kingkillery/red-queen-godel-machine`, PyPI `rqgm` (`observeco/rqgm-core` –
unaffiliated). Die Parameter `L=24 / Anker 240 / 28 Challenger` im
`klmtseng`-Demo sind ausdrücklich **„nicht Paper-Zahlen"** (Demo-Aufblasung).


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
make test  → 135 passed · Coverage 1294/1294 Statements · 278/278 Branches = 100,00 %
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
- **§9.3:** Zwei-Personen-Freigabe **abgeschlossen** (Batnini + taouefik, 2026-10-02; Record in `ergebnisse/fwr-code-korrektur.md` §0).
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
