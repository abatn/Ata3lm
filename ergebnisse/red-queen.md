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
| `GroundTruthAnchor.outcomes()/accuracy()` – Anker liefert (S, F) je Evaluator | „trusted ground-truth examples" / „Ground-Truth Anchor" |
| `best_belief(S, F, ε)` – BB_ε = I⁻¹_ε(1+S, 1+F), portiert aus `kingkillery/src/rqgm/beta.py` | Paper §3.1/§4; Tab. 3: ε = 0,05 |
| `load_anchor(kind)` – echte HF-Anker (CRAVE, IMO-GradingBench) | Paper §C.4 + HF-Datasets |
| `RedQueen.checkpoint(candidate, approved)` – Ersatz **nur** wenn BB_ε strikt größer (Gleichstand → Incumbent) | Paper §3.5: „the ε-best-belief evaluator is frozen … ties favour the incumbent" |
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
make test  → 189 passed · Coverage 1651/1651 Statements · 360/360 Branches = 100,00 %
```

Tests (`tests/test_evaluator_version.py`, 34) – u. a.:

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

## 8. Offen 1–3 abgeschlossen (2026-10-02)

### Offen 1 — ε-Best-Belief-Gate portiert

`best_belief(S, F, ε) = beta_ppf(ε, 1+S, 1+F)` (BB_ε, Paper §3.1/§4) wurde aus
**`kingkillery/red-queen-godel-machine`, `src/rqgm/beta.py`** portiert (pure
stdlib: `regularized_incomplete_beta` via Lentz-Kettenbruch + Bisektions-`beta_ppf`).
Der Ersatz-Vergleich nutzt **nicht mehr die Anker-Trefferquote**, sondern **BB_ε**:
Challenger nur bei **strikt größerem** BB_ε; Gleichstand → Incumbent (Paper §3.5).
Standard **ε = 0,05** (Tab. 3). Gegenprobe im Test gegen `scipy.special.betaincinv`
(Abweichung ≤ 1e-6).

### Offen 2 — Echte Anker geladen und gemessen

`load_anchor(kind)` lädt die echten HuggingFace-Anker (`datasets 4.5.0`, **kein**
Skript-Blocker → kein Fallback nötig):

| Anker | HF-ID | Rows | Ground Truth | Feature (Demo-Grader) |
|---|---|---|---|---|
| Grading | `Hwilner/imo-gradingbench` | 1000 | `Points == 7` („full credit 7 of 7", §C.4) | Länge der Antwort |
| Coding/Reviewer | `TuringEnterprises/CRAVE` | 908/132/134 | `label == APPROVE` | Patch-Länge |

**Reale Messung** (200 Grading-Items, 134 CRAVE-Test-Items; Grader = deterministische
Schwellwert-Regeln an a-priori-Quantilen — NICHT die LLM-Grader des Papers):

```text
ANKER: HF:Hwilner/imo-gradingbench | n: 200
  Baseline (alle akzeptieren): 0.31
  Checkpoint thr=4390: promoted=True  version=evaluator_v1 acc=0.395 BB=0.3402 gate=allow
  Checkpoint thr=5014: promoted=True  version=evaluator_v2 acc=0.515 BB=0.4570 gate=ask
  Checkpoint thr=6546: promoted=True  version=evaluator_v3 acc=0.585 BB=0.5268 gate=ask
  Final: evaluator_v3 acc 0.585 | gemessener Gewinn: 0.275 | Paper: 0.09

ANKER: HF:TuringEnterprises/CRAVE | n: 134
  Baseline (alle akzeptieren): 0.5
  Checkpoint thr=1603: promoted=True  version=evaluator_v1 acc=0.5373 BB=0.4663 gate=allow
  Checkpoint thr=3216: promoted=True  version=evaluator_v2 acc=0.5597 BB=0.4885 gate=ask
  Checkpoint thr=6731: promoted=False version=evaluator_v2 BB=0.4516 gate=deny
  Final: evaluator_v2 acc 0.5597 | gemessener Gewinn: 0.0597 | Paper: 0.09
```

**Ehrlich:** Das sind **eigene** Zahlen auf echten Ground-Truth-Daten
(+27,5 pp Grading, +6,0 pp CRAVE) – **nicht** die +9 % des Papers (die mit
LLM-Gradern entstanden). Das Gate verhält sich korrekt: es befördert v1→v2→v3
beim Grading und **lehnt** beim Coding den dritten Kandidaten ab (BB 0,4516 <
0,4885), weil schlechter.

### Offen 3 — Wiring-Status (§9 / §9.3)

- **§9.3 bestätigt:** Zwei-Personen-Freigabe `approved` (Batnini + taouefik,
  2026-10-02; Record `ergebnisse/fwr-code-korrektur.md` §0).
- **Evaluator-Replacement-Pfad:** Das ε-BB-Gate ist im Replacement-Pfad
  (`RedQueen.checkpoint`) eingebaut – strikt besser, ties keep incumbent,
  Selective Erasure.
- **Loop-Einbau (2026-10-02, §9.3 freigegeben):** `reflective_agent.run_once()`
  importiert `evaluator_version` und fährt den `RedQueenLoop` (8 Epochen,
  Checkpoints 1/2/4/8); das Ergebnis steht als `"rqgm"` im Report. Der Einbau ist
  **opt-in** über `RQGM_LOOP=1` – das Standardverhalten bleibt unverändert.
  Freigabe-Record (2 von 2):

```text
pending           : {"subject": "Red-Queen Loop-Einbau (Verhaltensänderung, §9/§9.3)", "state": "pending", "approvers": [], "count": 0}
approve(Batnini)  : {"ok": true, "state": "first_approved", "approvers": ["Batnini"]}
approve(taouefik) : {"ok": true, "state": "second_approved", "approvers": ["Batnini", "taouefik"]}
finalize          : {"ok": true, "state": "approved", "approvers": ["Batnini", "taouefik"]}
Endstatus         : {"state": "approved", "approvers": ["Batnini", "taouefik"], "count": 2}
```

  Test: `test_reflective.py::test_run_once_mit_rqgm_loop` (8 Epochen,
  `current=evaluator_v3`) und `test_run_once` (`rqgm is None` ohne Flag).

### Quellen (HTTP 200, 2026-10-02)

https://arxiv.org/abs/2606.26294 · https://github.com/kingkillery/red-queen-godel-machine
(src/rqgm/beta.py, src/rqgm/search.py) · https://github.com/ianyac/red-queen-godel-machine ·
https://huggingface.co/datasets/TuringEnterprises/CRAVE ·
https://huggingface.co/datasets/Hwilner/imo-gradingbench

## 9. Verbleibende Punkte geschlossen (2026-10-02)

### 9.1 RQGM_LOOP dauerhaft aktiv

`reflective_agent.run_once()` fährt den Red-Queen-Loop jetzt **standardmäßig**
(`os.environ.get("RQGM_LOOP", "1") != "0"`). Der explizite Aus-Schalter
`RQGM_LOOP=0` bleibt für Debug/Tests. Test-Matrix:

| Zustand | Erwartung | Test |
|---|---|---|
| Default (unset) | `rqgm` im Report, `current=evaluator_v3` | `test_run_once_rqgm_default_an` |
| `RQGM_LOOP=0` | `rqgm is None` | `test_run_once` |
| `RQGM_LOOP=1` | `rqgm` im Report | `test_run_once_mit_rqgm_loop` |

### 9.2 Lint/Formatter (Ruff + pre-commit + CI)

- `pyproject.toml`: `[tool.ruff]` line-length 120, target `py39`,
  `select = ["E","F","W","I"]`, `ignore = ["E501"]` (Zeilenlänge macht der Formatter).
- `.pre-commit-config.yaml`: `ruff` + `ruff-format` (Rev `v0.16.10`, verifiziertes Tag).
- `.github/workflows/ci.yml` (ersetzt `lint.yml`): Job **`lint`** (`ruff check` +
  `ruff format --check`) **und Job `test`** (`make test`, Matrix Python 3.9 + 3.12,
  installiert `requirements-dev.txt`). Damit prüft die CI den **kompletten**
  Knowledge-Agenten: Lint + 189 Tests + 100 % Line/Branch-Coverage.
  Ergänzend `tests/test_agents_law.py` (AGENTS.md §1–§11, Guardrails, Provenienz
  jeder Rekursion, Versionierung, Tiers/Connectors, RQGM-Verdrahtung, CI-Inhalt).
  **CI-Lauf `lint` war grün** (Run 37018230627); Test-Job neu hinzugefügt.
- Ergebnis: `ruff check .` → **All checks passed**; `ruff format --check .` →
  **33 Python-Dateien formatiert** (45 wurden einmalig formatiert).
  **Markdown ausgeschlossen** (`exclude = ["*.md", "**/versions/**"]`), weil Ruff
  sonst Python-Codeblöcke in Doku, **unveränderlichen Versions-Snapshots** und im
  Validierungsset umformatiert hätte.
- Quellen (HTTP 200): https://docs.astral.sh/ruff/ ·
  https://docs.astral.sh/ruff/configuration/ · https://pre-commit.com/

### 9.3 Echte LLM-Grader (zweiter Call als Judge)

`make_llm_grader(rule_grader, …)` in `evaluator_version.py`:

- **Zweiter LLM-Call** mit JSON-Verdict `{passed, score, reason}`,
  **Pydantic-validiert** (`GraderVerdict`, score 0..1).
- **Deterministisch:** `temperature=0.0`, feste `max_tokens`
  (`RQGM_GRADER_MAX_TOKENS`, Default 1024), Modell `RQGM_GRADER_MODEL`.
- **Robust:** erstes JSON-Objekt wird aus der Antwort extrahiert
  (`_extract_json`); `content` **oder** `reasoning_content` wird gelesen.
- **Fail-soft:** API-Fehler/ungültiges Schema → Regel-Grader + Log-Eintrag.
- Quellen: arXiv:2606.26294 §5 (Grader-Evolution) ·
  OpenAI Structured Outputs (https://platform.openai.com/docs/guides/structured-outputs)

**Reale Messung** (8 IMO-Grading-Items, `nvidia/nemotron-3-super-120b-a12b`):

```text
Modell: nvidia/nemotron-3-super-120b-a12b | max_tokens: 1024 | Fallbacks: 15 / 24
Baseline: 0.125 -> Final: 0.625 | Gewinn: 0.5
  thr=4371 promoted=True  acc=0.25  BB=0.0977
  thr=4631 promoted=False acc=None  BB=0.0977   (Gleichstand -> Incumbent bleibt)
  thr=4983 promoted=True  acc=0.625 BB=0.3449
```

**Ehrlich:** Das sind **eigene** Zahlen auf echtem Ground-Truth-Anker
(+50 pp auf 8 Items mit LLM-Judge + Fail-soft) – **nicht** die +9 % des Papers.
Der Endpoint lieferte in **15 von 24** Calls kein gültiges JSON (Reasoning-Modell
→ Fließtext); genau dafür greift die Fail-soft-Regel. Das Gate verhält sich
korrekt (Gleichstand hält den Incumbent).

### Quellen (HTTP 200, 2026-10-02)

https://docs.astral.sh/ruff/ · https://docs.astral.sh/ruff/configuration/ ·
https://pre-commit.com/ · https://platform.openai.com/docs/guides/structured-outputs ·
https://arxiv.org/abs/2606.26294 · https://huggingface.co/datasets/Hwilner/imo-gradingbench

## 10. Methodische Einordnung der „+50 pp" (Statistik, 2026-10-02)

### 10.1 Ausgangsgröße — ehrliche Abgrenzung

Die früher genannten **„+50 pp"** waren die **Accuracy-Differenz** von
Baseline („alle akzeptieren", 0.125) zum Loop-Endergebnis (0.625) auf **8**
IMO-Grading-Items. Fairer (gleiche Schwelle) ist der Vergleich
**Regel-Grader vs. LLM-Grader**: 0.500 → 0.625 = **+12,5 pp**.

**Wichtig:** Die im Auftrag angenommene „Hedges' g ≈ 0.625" ist **nicht** g,
sondern die Accuracy-Differenz. Das aus den Rohdaten berechnete **g = 0.314**.

### 10.2 Hedges' g (exakt + Näherung)

- Gepaart, ν = n − 1 = **7** (nicht n₁+n₂−2).
- `J(7)` exakt = Γ(ν/2)/(√(ν/2)·Γ((ν−1)/2)) = **0.8882**; Näherung
  `1 − 3/(4ν−1)` = **0.8889** (metafor::cmicalc).
- Cohen's d (gepaart) = mean(Δ)/sd(Δ) = **0.354** → **g = J(7)·d = 0.314**.

### 10.3 Power-Analyse (G*Power-Analog, Faul et al. 2007)

```text
power_paired_t(g=0.314, n=8, alpha=0.05, zweiseitig) = 0.117
benötigtes n für Power = 0.80                       = 82
```

→ n=8 ist **massiv unterpowert** (nur 11,7 % Chance, einen echten Effekt dieser
Größe zu finden).

### 10.4 95%-KI für g (nichtzentrales t, Steiger & Fouladi 1997)

```text
95%-KI g = [-0.333, 0.940]   (enthält 0 -> nicht signifikant bei n=8)
```

### 10.5 Cohen's κ (LLM-Grader vs. IMO-Ground-Truth, dieselben 8 Items)

```text
κ = 0.250   SE = 0.342 (vereinfachte Fleiss-Formel)   95%-KI = (-0.421, 0.921)
Landis & Koch: "fair"
```

Ehrlich: die **volle Fleiss-Cohen-Everitt-Kovarianz** ist **nicht** modelliert;
implementiert ist die vereinfachte asymptotische SE. Das KI ist bei n=8 extrem
breit.

### 10.6 Bias-Checks: Position tauschen (3×) + Repetition

8 Items × 3 Ordnungen (A,B) → (B,A) → (A,B), paarweiser LLM-Judge
(`make_llm_pairwise_judge`):

```text
Flip-Rate (Sieger-Identität wechselt):              0.000
Position-Consistency (gleiche Identität in allen 3): 1.000
Repetition-Stability (Position Ordnung 1 vs. 3):     1.000
Pairwise-Fallbacks:                                  0/24
```

→ **Kein Positions-Bias** auf diesen 8 Items (der Judge bevorzugte in allen
Ordnungen die vollständige Antwort), Output **repetierbar**. Die in der
Literatur berichtete hohe Flip-Rate (bis 39 %) trat hier **nicht** auf –
ehrlich als **Nicht-Befund** dokumentiert (kleines n, paarweise Aufgabe).

### 10.7 Fazit

Bei n=8 ist **keine belastbare Aussage** möglich: Power 0.117, g-KI enthält 0,
κ-KI extrem breit. Die **+9 % des Papers** werden **nicht** reproduziert; die
eigenen Zahlen sind mit dieser Stichprobe statistisch nicht unterscheidbar von
Zufall. Nächster Schritt für eine belastbare Messung: n ≈ 82 Items.

### Quellen (HTTP 200 am 2026-10-02)

| Quelle | Verwendung | Link |
|---|---|---|
| Faul et al. 2007 (G*Power 3) | Post-hoc-Power, n für 0.80 | https://link.springer.com/article/10.3758/BF03193146 |
| NIST Dataplot (Hedges' g) | g = J(ν)·d | https://www.itl.nist.gov/div898/software/dataplot/refman2/auxillar/hedgeg.htm |
| metafor::cmicalc | J(ν) ≈ 1 − 3/(4ν−1) | https://wviechtb.github.io/metafor/reference/cmicalc.html |
| Landis & Koch 1977 | κ-Interpretation | https://doi.org/10.2307/2529310 |
| Steiger & Fouladi 1997 | KI via nichtzentrales t | Buchkapitel (What if There Were no Significance Tests?, 221–257) |
| Fleiss, Cohen & Everitt 1969 | asymptotische κ-SE | Psychol. Bull. 72(5):323–327 (DOI 10.1037/h0028106 blockt Bots: 403) |
| lechmazur/position_bias · sbezjak/llm-benchmark | Positions-Bias-Methodik | https://github.com/lechmazur/position_bias · https://github.com/sbezjak/llm-benchmark |

### 10.8 Nachtrag: Bootstrap-KI für κ (ersetzt die asymptotische SE)

**Warum nicht Wilson:** Wilson-Score-Intervalle setzen eine **Proportion** in
[0,1] mit Varianz `p(1−p)/n` voraus. κ hat Wertebereich **[−1,1]** und eine
komplexere Varianz, die die Randverteilungen der Konfusionsmatrix einbezieht.
Der Agent darf κ **nie** über Wilson routen; ein Guard-Test
(`test_bootstrap_konstanten_und_kein_wilson`) prüft, dass keine
Wilson-Implementierung existiert. Fleiss, Cohen & Everitt (1969) dient **nur**
als Begründung dieser Komplexität – **nicht** als Grundlage der KI-Berechnung.

**Methode:** case-level Bootstrap (`bootstrap_kappa_ci`), **B = 10.000**,
`seed = 0` (bit-reproduzierbar), **BCa** (Default), Percentile als Fallback bei
degenerierter Verteilung (NaN). Quelle: `scipy.stats.bootstrap`
(`method='BCa'`) · Efron & Tibshirani 1993, S. 184–188 (B ≥ 1000 für KI; 200
nur für SE).

**Reales Ergebnis** (dieselben 8 IMO-Grading-Items, LLM-Grader vs. Ground-Truth):

```text
Bootstrap-KI κ (B=10000, seed=0, method=BCa):
  kappa=0.091  95%-KI=[0.000, 0.714]  (0.7s)
  degenerate_share=0.4235  warning=True
  asymptotisch (alt): kappa=0.091 KI=(-0.397, 0.579)
  bit-reproduzierbar: True
```

**Degenerate-Share:** 42,35 % der Resamples hatten einen **konstanten Stream**
(κ undefiniert → 0.0). Ab `DEGENERATE_WARN_THRESHOLD = 0.05` (Auftrag) wird
gewarnt, weil SciPy bei degenerierter Bootstrap-Verteilung NaN liefert und die
KI dann **nicht interpretierbar** ist. Genau das ist hier der Fall → die
Bootstrap-KI **[0.000, 0.714]** ist bei n=8 **nicht belastbar**.

**Vergleich der beiden KI-Methoden** (gleiche Daten):

| Methode | 95%-KI | Bewertung |
|---|---|---|
| asymptotisch (Fleiss-SE, alt) | (−0.397, 0.579) | unterstellt Normalverteilung, bei n=8 unzuverlässig |
| Bootstrap BCa (neu, Default) | (0.000, 0.714) | verteilungsfrei, aber degeneriert (42 % konstante Streams) |

**Ehrlich:** Bei n=8 ist **keine** κ-Aussage belastbar – weder asymptotisch noch
Bootstrap. Für eine stabile Bootstrap-KI braucht es deutlich mehr Items.

**Quellen (geprüft 2026-10-02):**

| Quelle | Verwendung | Status |
|---|---|---|
| https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.bootstrap.html | Bootstrap-Engine (BCa/Percentile, random_state) | HTTP 200 |
| Efron & Tibshirani (1993), *An Introduction to the Bootstrap*, S. 184–188 | B ≥ 1000 für KI | Buch |
| https://www.taylorfrancis.com/books/mono/10.1201/9780429246593/… | Buch-Nachweis | HTTP 200 |
| Wilson (1927), JASA — DOI 10.1080/01621459.1927.10502953 | nur Gegenbeispiel (Proportion) | DOI **403** (Bots) → bibliografisch |
| Fleiss, Cohen & Everitt (1969) | Begründung κ-Varianz (nicht KI-Grundlage) | DOI 403 → bibliografisch |
| **„Clearway"** (`degenerate_share`, `bootstrap_resamples`) | vom Auftraggeber genannt | **NICHT verifizierbar**: PyPI-JSON `{"message":"Not Found"}` → **nicht zitiert** |

### 10.9 Stabile κ-Statistik mit n≥50 (4-Klassen, 2026-10-02)

**Erster Lauf n=50** (unten) → Präzision reichte nicht. **Finaler Lauf n=90**
(§10.9.1): benötigte n = 79 → **90 reicht**. Die **n=30-Ausnahme wurde NICHT
genutzt** – sie wäre nur mit `prec_kappa`-Nachweis zulässig.

**Sample-Size-Validierung** (`kappa_required_n`, Methode analog
`presize::prec_kappa`/`kappaSize`; **R war nicht installiert** → simplified-SE
algebraisch portiert, Abweichung dokumentiert). Human-Klassen der ersten 50:
Incorrect 14 · Partial 8 · Almost 4 · Correct 24.

```text
benötigte n für 95%-KI-Breite < 0.30 (simplified-SE):
  kappa=0.4 -> n=94     kappa=0.5 -> n=87     kappa=0.6 -> n=77
```

→ **n=50 reicht NICHT** (Aufgabe: „Wenn nein → n erhöhen"). Erforderlich wären
~77–94 Items; die presize/kappaSize-Warnung (Large-Sample unsicher für N<50) ist
damit ernst genommen, aber 50 ist noch unter der nötigen Breite.

**Realer Lauf** (`stable_kappa_run`, 4-Klassen-LLM-Grader vs. humanes `Reward`,
50 Items, 773 s):

```text
kappa = 0.027      BCa-95%-KI = [-0.110, 0.160]
seed = 0   B = 10.000   method = BCa
degenerate_share = 0.0000   -> Interpretation: ok   (KEINE willkürliche Schwelle)
LLM-Klassen: {Incorrect: 40, Correct: 7, Partial: 3}
Fallbacks: 34 / 50
```

**Bootstrap vs. asymptotisch** explizit: hier nur **Bootstrap BCa** (Seed 0, B
10.000). `degenerate_share = 0.0` → keine degenerierte Verteilung, keine NaN.

**Ehrliche Einordnung:** κ = 0.027 ist **praktisch Zufall**, und das Ergebnis ist
**fallback-dominiert**: 34/50 LLM-Aufrufe lieferten kein gültiges JSON → der
Regel-Fallback („Incorrect") prägte 40 der 50 Urteile. Die **bindende Grenze ist
nicht die Stichprobe, sondern die JSON-Zuverlässigkeit des Endpoints**. Eine
belastbare κ-Aussage braucht (a) mehr Items (≥ 87) **und** (b) einen zuverlässig
strukturierten Grader. Die **+9 % des Papers werden weiterhin nicht reproduziert**.

**Provenienz:** Seed 0 · B 10.000 · BCa · Modell `nvidia/nemotron-3-super-120b-a12b`
· 50 Items der HF-Dataset-Splits (imo-gradingbench, train).

**Quellen (HTTP 200, 2026-10-02):**

| Quelle | Verwendung | Status |
|---|---|---|
| https://search.r-project.org/CRAN/refmans/presize/html/prec_kappa.html | Sample-Size/Präzision (Methode) | HTTP 200 |
| https://cran.r-project.org/web/packages/kappaSize/index.html (+ PDF) | kappaSize (Rotondi & Donner 2012) | HTTP 200 |
| https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.bootstrap.html | BCa-Bootstrap | HTTP 200 |
| https://huggingface.co/datasets/Hwilner/imo-gradingbench | 1.000 humane IMO-Bewertungen (4 Klassen) | HTTP 200 |

Abweichung: `prec_kappa`/`kappaSize` nutzen die volle kappaSize-Varianz; hier ist
die **simplified-SE** algebraisch invertiert (R fehlte). Die n-Schätzung ist daher
eine **Näherung**, keine exakte presize-Ausgabe.

#### 10.9.1 Finaler Lauf n = 90 (Präzision erfüllt)

Human-Klassen der ersten 90 Items: **Incorrect 21 · Partial 35 · Almost 9 · Correct 25**.
Sample-Size-Validierung (`kappa_required_n`, simplified-SE): **benötigte n = 79**
(für κ=0.5, 95%-KI-Breite < 0.30) → **n=90 reicht** (Präzisionsziel erfüllt).

```text
STABILER Lauf n=90 (4-Klassen-LLM-Grader vs. Reward, 1516 s)
  kappa = 0.028      BCa-95%-KI = [-0.055, 0.110]
  seed = 0   B = 10.000   method = BCa
  degenerate_share = 0.0000   -> Interpretation: ok   (keine willkürliche Schwelle)
  LLM-Klassen: {Incorrect: 79, Correct: 3, Partial: 7, Almost: 1}
  Fallbacks: 70 / 90
```

**Ehrliche Einordnung:** Die **Stichprobengröße ist jetzt ausreichend** (90 ≥ 79),
aber das Ergebnis ist **stark fallback-dominiert**: **70 von 90** LLM-Aufrufen
lieferten kein gültiges JSON → der Regel-Fallback („Incorrect") prägte 79 der 90
Urteile. κ = 0.028 (praktisch Zufall) ist daher **nicht als Grader-Genauigkeit
interpretierbar**. Die bindende Grenze ist die **JSON-Zuverlässigkeit des
Endpoints**, nicht mehr n. Die **+9 % des Papers bleiben NICHT reproduziert**.
`degenerate_share = 0.0` zeigt: das Problem ist **nicht** die Bootstrap-Verteilung,
sondern der Grader-Output.

**Provenienz n=90:** Seed 0 · B 10.000 · BCa · `nvidia/nemotron-3-super-120b-a12b`
· 90 Items (imo-gradingbench, train) · Dauer 1516 s.

### 10.10 Robuster Grader (Rekursion 033): JSON-Quote verbessert

`make_llm_class_grader` nutzt jetzt **json-repair** (Prosa/Truncation) + **Retry**
(`max_attempts`, strengerer Prompt) + **Mehrheitsentscheid** (`votes`) + optional
**`json_schema` strict**. Beleg (5 Items, 1 Versuch):

```text
use_schema=False: 5/5 Fallbacks
use_schema=True : 3/5 Fallbacks  (2 valide: Almost, Correct)  -> messbare Verbesserung
```

Der robuste n=90-Lauf erreichte 75/90 mit 50 Fallbacks (78 % -> ~67 %), lief aber
in die Zeitgrenze -> **kein finales kappa**. Der vollstaendige Fix bleibt
**server-seitige constrained decoding** (vLLM/XGrammar/NIM `guided_json`) oder ein
Instruct-Modell. Details: `ergebnisse/rekursion/033-robuster-grader.md`. Die
**+9 % des Papers bleiben NICHT reproduziert**.

### 10.11 Externer Grader-Test (Rekursion 034): JSON gelöst, Genauigkeit modelllimitiert

Gegen zwei vom Auftraggeber bereitgestellte Ollama-Endpoints (`qwen3:14b`,
`qwen2.5:14b`) lief unser Grader unverändert:

```text
JSON-Quote (5 Items):  0/5 Fallbacks mit use_schema=True  -> JSON-Problem GELÖST
Genauigkeit (5 Items): 0/5 Übereinstimmung (Human: Incorrect/Partial/Partial/Almost/Almost)
                       beide 14B-Modelle vergeben fast immer "Correct"
```

Diagnose (Item 1, Human **Incorrect**): die Antwort behauptet „I have successfully
proven the statement" – ein langer, selbstsicherer, aber fehlerhafter Beweis. Der
14B-Grader **prüft die Mathematik nicht**. Ein geschärfter Rubric-Prompt änderte
nichts. ⇒ **nicht mehr das JSON, sondern die Modellstärke ist die Grenze**. Nächstes:
Qwen3-30B-A3B-Instruct (4-bit, 2×T4) oder gpt-oss-20b. Details:
`ergebnisse/rekursion/034-externer-grader-test.md`. Die **+9 % bleiben NICHT reproduziert**.
