# Rekursion 132: Kontrollierter A/B (P-131) — P-1 (rsLoRA-Überskalierung) bestätigt, Modell-Drift 93,7 % ⇒ Human-Gate

> Datum: 2026-10-22 · Gesetz: `AGENTS.md` §6 (`:61-68`), §9 (`:116-124`), §9.1c (`:165-176`),
> §9.1d (`:178-182`), §9.3 (`:214-234`), §10.3 (`:271-276`), §10.7 (`:304-331`) · Guardrails 1/2/3/5/6/7 (`:97-107`)
> Status: **pending** — Messung abgeschlossen und unabhängig nachgerechnet; **kein** `self_update`,
> **keine** Code-Änderung in dieser Iteration; §9-Gate-Ergebnis: **ask** — die menschliche Entscheidung
> liegt vor (Proposal **P-132**, §9.3 Batnini + Taoufik, 2026-10-22); der Lernpfad bleibt bis zur
> Umsetzung `deny`.
> Anlass: `ergebnisse/proposals/P-131-kontrollierter-rslora-ab.md` (`:approved`, §9.3 Batnini + Taoufik,
> 2026-10-21), Ausführungsregel §8 (`:261-264`), prä-registrierte Auswertung §4 (`:162-169`).
> Vorgänger: `ergebnisse/rekursion/131-ds15-datensatz-bereitstellung-kaggle-ab.md` (Bereitstellung),
> `ergebnisse/rekursion/130-m1-m2-m3-lauf-b2-prime-messung.md` (Baseline-Messung),
> `ergebnisse/rekursion/129-b2-prime-annahmenpruefung.md` (A1–A4).
> Commit-Freigabe: **Nutzer, 2026-10-22** (Guardrail 6 `:103-104`).

---

## 1. Auftrag & Setup

- **Ziel `g`:** Kausale Trennung der Hypothese **P-1** (rsLoRA-Überskalierung: `use_rslora=true` ⇒
  α/√r = 256/8 = **32** statt α/r = 256/64 = **4**, also 8× größere effektive Updateskalierung) von
  konkurrierenden Erklärungen („Lernrate zu hoch", „historischer Code-Stand") — `P-131:34-37`.
- **Task-Input (identisch in beiden Armen, einzige Treatment-Variable `LORA_USE_RSLORA`):**
  15 `write-new`-Fakten (SHA256 `18caaae7…`, Zeilen-Aggregat `8d42c0da…`), Basis
  `Qwen/Qwen2.5-3B-Instruct` @ Commit `aa8e72537993ba99e69dfaafa59ed015b17504d1`, r=64, α=256,
  lr 2e-4, 15 Epochen, Seed 42, `max_new_tokens=16`, `do_sample=false` — `P-131:38-40`.
- **Auflagen-Abgleich (`P-131:246-258`) — alle drei erfüllt und belegt:**

  | Auflage | Erfüllt? | Beleg |
  |---|---|---|
  | 1 — Datensatz byte-identisch `18caaae7…` / inhaltsgleich | **ja** | beide `kaggle_output.json`: `dataset_hash_sha256: 18caaae7…`, `dataset_row_hash_aggregate_sha256: 8d42c0da…`, `dataset_rows: 15`; Probe-`manifest.json:dataset_sha256` = `18caaae7…` |
  | 2 — Umgebung = Baseline | **ja** | beide `library_versions`: transformers 5.16.1, peft 0.20.0, trl 1.16.0, bitsandbytes 0.50.2, datasets 4.8.5, accelerate 1.14.0, **torch 2.11.0+cu128**; Probe-`manifest.json:env`: torch 2.11.0+cu128, **torchao 0.18.0** (≥0.16), T4, fp16, capability [7,5] |
  | 3 — Klon aktualisiert (≥ `41348ec`) | **ja** | Klon `Cloning into '/kaggle/working/Ata3lm'...` auf `origin/main` = `9ef6169` (Nachfolger von `41348ec`); Probe-`manifest.json:resolved_commits.base_commit` = `aa8e725…` (Basis), `base_commit_source: config._commit_hash` |

- **Was diese Iteration **nicht** tut:** kein `self_update`, keine Code-/Originaldatei-Änderung, kein
  Training, kein weiterer Lauf. Nur Auswertung + Dokumentation (Guardrails 5/6).

---

## 2. Rohbelege

### 2.1 Die zwei A/B-Läufe (Kaggle T4, 2026-10-22)

| Feld | Arm A (`ab_rsloRa0`) | Arm B (`ab_rslora1`) | Baseline-Referenz |
|---|---|---|---|
| `lora_use_rslora` | **false** | **true** | B2: false · B2′: true |
| `loss` | **1.310697078704834** | **5.190721893310547** | B2: 1.310697078704834 · B2′: 5.190721893310547 |
| `lora_r` / `lora_alpha` | 64 / 256 | 64 / 256 | 64 / 256 |
| `learning_rate` / `num_train_epochs` / `seed` / `max_length` | 2e-4 / 15.0 / 42 / 1024 | 2e-4 / 15.0 / 42 / 1024 | identisch |
| `dataset_hash_sha256` / `dataset_row_hash_aggregate_sha256` / `dataset_rows` | `18caaae7…` / `8d42c0da…` / 15 | `18caaae7…` / `8d42c0da…` / 15 | identisch |
| `compute_dtype` / `compute_capability` / `gpu` | float16 / sm_75 / Tesla T4 | float16 / sm_75 / Tesla T4 | identisch |
| `library_versions` | 7 Pakete = Baseline (s. §1) | identisch | identisch |
| `started_utc` → `finished_utc` | 06:47:42Z → 06:50:37Z | 06:50:58Z → 06:52:42Z | — |
| `adapter_model.safetensors` SHA256 | `e3be2c8518433696a6aa5b088a43823facc099b20c7beab385e9352ec3023f2e` | `a595d437f4fcb0c6030840d9e70e7ff6818a5e490943aabe19f00c3dee6ba9c5` | B2: `e3be2c85…` · B2′: `a595d437…` |
| `adapter_config.json` SHA256 | `56cc999b782b44a4f2f50b76100a9fa848eaecf3b333677fa243b50257a4c2cf` | `3df2101372f92c100dd3c15275af0f05faeb8f36f0cce7e41d24134203abe129` | — |
| `kaggle_output.json` SHA256 | `b49a5d0b3397a52aa0e95713897fe72ad7862095be891f9848b2764cda12f0bb` | `c9feeccfa641957a99d50ccbf992e083a1b131b964e3a4b8fc23cabd02fb08d1` | — |

**Befund aus der Tabelle (Fakt, keine Deutung):** Beide Arme erzeugen Loss-Werte, die **exakt** den
historischen Läufen entsprechen, und die Adapter-Gewichte sind **byte-identisch** mit den historischen
Adaptern (B2 = `e3be2c85…`, B2′ = `a595d437…`; `P-131:51` nennt für B2′ `a595d437…`, Rek 129 §M5
rekonstruierte `18caaae7…` byte-identisch). Beide `adapter_config.json`: r=64, α=256, dropout 0.05,
`target_modules` = 7 Module (identische Menge), `use_rslora` false/true.

### 2.2 Der Messlauf (Probe, gleiche Session, nach den Fixes `41348ec`)

Artefakte: HF `Batnini/knowledge-agent-write-back`, Pfad `probe/ab_2026-10-22/`
(`status.json` `1098481a959ebd6b6179618d51f6b448a92a542c24e0e94958b83fabedb89bb0` (123 B),
`manifest.json` `9ceca3cda545b8a3d4d9851bad66dce16e5d34fb296791013861630412d6aac0` (9696 B),
`per_item.jsonl` `95ceabbc835e86f12b4143399ad6d9dc851a42c0775bd7c0e1c7e62bbd7d4f82` (38313 B, 120 Rohzeilen)).

`status.json` (wörtlich):
```json
{"status": "ausgefuehrt", "decision": "unentschieden", "rule": 9, "precondition_failed": ["m2_collapse"]}
```

`manifest.json` (Auszug, wörtlich): `n_probes: 15` · `decoding: {max_new_tokens: 16, do_sample: false,
seed: 42, reseeded_before_each_pass: true}` · `dataset_sha256: 18caaae7…` ·
`adapter_b2prime_sha256: a595d437…` · `adapter_b2_sha256: e3be2c85…` · `env: {python 3.13.15,
torch 2.11.0+cu128, transformers 5.16.1, peft 0.20.0, torchao 0.18.0, gpu Tesla T4, dtype float16}` ·
`thresholds: {good 11, bad 4, diff 3, collapse_min 12, cross_instance_noise_budget 2}` ·
`canary: {matched 15/15, same_instance true, status pass}` · `determinism_baseline: {matched 15/15, pass}` ·
`cross_instance_noise: {matched 15/15, within_budget true}` · `positive_control: {w1_generation
{matched 0/15}, …}` · `grader_crosscheck: "ok (repo acceptance_gate.py identisch, 120 Paare x 2 Modi)"` ·
`regel6_reference: {reference: null, available: false}` (kein Referenz-Altlauf übergeben ⇒ Regel 6
nicht ausgeführt) · `resolved_commits.tokenizer_commit: null (unresolved)` ·
`fingerprints.tokenizer_chat_template_sha256: cd8e9439f0570856fd70470bf8889ebd8b5d1107207f67a5efb46e342330527f` ·
`decision.rules: [{nr 9, "M2 degeneriert (13/15 identische Antwort 'Jamaica') — Diagnose blockiert, kein
P-1/P-2/P-3-Zweig"}, {nr 5, "P-2a: N8 invalidiert base_answer/em_base/changed/Delta"}, {nr 6, "P-2b: nicht
ausgefuehrt (kein Referenz-Altlauf uebergeben)"}]`.

`format_control.per_pass` (Auszug): `M2_b2prime {collapse true, top_answer "Jamaica", top_count 13}` ·
`M3_b2 {collapse false, top_answer "Grand Duke of Lithuania", top_count 1}` · `M1_base/M1b_base/M1c_base
{collapse false, top_count 1}`.

**Skript-Ausgabe (wörtlich):**
```
Canary (vs M1b, gleiche Instanz): 15/15
Positivkontrolle M2 vs canary: differing_items=15 (Logit-Delta 25.088867, lora_B_nonzero 252)
```

---

## 3. Unabhängige Nachrechnung (read-only, Repo-Grader)

Methode wie Rek 130 §3: die 120 Rohzeilen aus `per_item.jsonl` wurden **nicht** aus den Skript-Zählern
übernommen, sondern mit dem Repo-Grader `data/memory/acceptance_gate.py:grade` (`:114-131`) neu bewertet
(Interpreter: `.venv`; keine Modellaufrufe, keine Erfindung).

| Pass | n | strict | substring | gold_in_raw_output | Skript-Zähler |
|---|---|---|---|---|---|
| `M1_base` | 15 | 0 | 0 | 0 | 0/0/0 ✔ |
| `M1_repeat` | 15 | 0 | 0 | 0 | 0/0/0 ✔ |
| `M1b_base` | 15 | 0 | 0 | 0 | 0/0/0 ✔ |
| `M1c_base` | 15 | 0 | 0 | 0 | 0/0/0 ✔ |
| `M2_b2prime` (Arm B, rsLoRA) | 15 | **1** | 1 | 1 | 1/1/1 ✔ |
| `M2_repeat` | 15 | 1 | 1 | 1 | 1/1/1 ✔ |
| `canary_disable_adapter` | 15 | 0 | 0 | 0 | 0/0/0 ✔ |
| `M3_b2` (Arm A, non-rsLoRA) | 15 | **15** | 15 | 15 | 15/15/15 ✔ |

**Abweichung Skript ↔ Nachrechnung: keine** (alle 8 Pässe, alle 3 Metriken).

Weitere unabhängig nachgerechnete Größen:
- **Degeneration:** `M2_b2prime` top_count **13/15** („Jamaica") ⇒ `collapse = true` (Schwelle 12);
  `M3_b2` top_count **1/15** ⇒ keine Degeneration; `M1/M1b/M1c/canary` je 1/15.
- **Canary** (M1b ↔ canary, gleiche Instanz): **15/15** identisch ⇒ Basis-Messung ist adapter-frei
  und deterministisch.
- **Determinismus** (M1 ↔ M1_repeat): **15/15**; **Cross-Instance-Noise** (M1 ↔ M1b): **15/15**
  (0 Abweichungen, Budget 2/15).
- **Positivkontrolle** (M2 ↔ canary): **15/15** Items verschieden, Logit-Delta 25,088867, `lora_B`-Nullen
  252 (identisch zum Baseline-Lauf, `P-131:64`).
- **Grader-Crosscheck** (neu, in Rek 130 ausgefallen): `ok (repo acceptance_gate.py identisch, 120 Paare x 2 Modi)`.
- **Reproduktion:** `per_item.jsonl` des A/B-Laufs ist **byte-identisch** mit dem Lauf vom 2026-10-20
  (beide `95ceabbc835e86f12b4143399ad6d9dc851a42c0775bd7c0e1c7e62bbd7d4f82`, `cmp` ⇒ identisch).
- **Write-Back-Messung mit Basis vor dem Wrap** (`P-131:263`, Muster `kaggle/write_back_cycle.py:420-421`
  /`:442-445`): erfüllt durch den Canary-Pass `with inst2.disable_adapter():` auf **derselben** Instanz
  (`kaggle/m1_m2_m3_probe.py:406-417`) — die Basis wird adapter-frei und instanzgleich gemessen
  (Canary 15/15 identisch zu M1b), d. h. `em_base`/`changed`/Δ der N8-Messung sind **nicht** kontaminiert
  (Rek 129 §A2). Der **volle** `write_back_cycle.py`-Zyklus (Router/Reflective-Agent) ist auf Kaggle nicht
  ausführbar (lokaler Ollama-Endpoint, `--llm-base-url`) und laut `P-131:42-43` ohnehin Nicht-Ziel.

---

## 4. Befund — P-1 bestätigt (und was das Skript meldet)

### 4.1 Anwendung der prä-registrierten Auswertungsregel (`P-131:162-169`)

| Beobachtung im A/B | gemessen | erfüllt? |
|---|---|---|
| Arm `=1` (rsLoRA): ≤ 4/15 **oder** Degeneration | **1/15** **und** Degeneration 13/15 | **ja** |
| Arm `=0` (non-rsLoRA): ≥ 11/15 **und** keine Degeneration | **15/15** **und** top_count 1/15 | **ja** |

⇒ **P-1 bestätigt** (Zeile 1 der Tabelle): *„rsLoRA-Überskalierung verursacht den Kollaps"*.

Die Zeilen 2–4 der Tabelle (`P-131:167-169`) sind **nicht** einschlägig (nur ein Arm degeneriert;
der andere 15/15).

### 4.2 Die Skriptentscheidung ist `unentschieden` (Regel 9) — Begründung, nicht Verschweigen

Das Messskript meldet `decision: unentschieden`, `rule: 9`, `precondition_failed: [m2_collapse]`.
Das ist die Regel des **Diagnose-Preregistrations** (`kaggle/m1_m2_m3_preregistration.md:99`): bei
Degeneration in M1/M1b/M2/M3 wird **keine** Ursache zugeordnet (Ziel von Rek 130 §4 M4: die damalige
falsche „Regel 3 / P-3"-Zuordnung verhindern). Der Lauf ist damit **regel-9-konform** (Testfall 6
`P-131:155` erfüllt: `unentschieden`, keine P-1/P-2/P-3-Zuordnung).

**Verhältnis der beiden Regeln (transparent, ohne Messwertänderung):**
- Regel 9 beantwortet die **Diagnosefrage** „welche Komponente verursachte den Kollaps?" — das ist bei
  **einem** degenerierten Lauf nicht entscheidbar, weil Degeneration selbst kein Attribut ist.
- Die **A/B-Regel (A2)** beantwortet die **Kausalfrage** anhand des **Kontrasts zweier Arme** mit
  identischem Code/Daten/Seed/Umgebung und genau einer veränderten Variablen (`use_rslora`) — der
  Attributionsweg ist der Kontrast, nicht der degenerierte Einzellauf.
- A2 war im Proposal als „hier nur **beantragt — nicht angewendet**" markiert (`P-131:162`) und mit
  dem Proposal (§9.3, Batnini + Taoufik, 2026-10-21) **freigegeben**; das Messskript implementiert A2
  **nicht** ⇒ **Implementierungslücke**, dokumentiert in §7.3. Die A/B-Entscheidung nach `P-131:162-169`
  wird hier aus den gemessenen Zählern abgeleitet; **kein Messwert wurde verändert**.

### 4.3 Mechanik (aus den Adaptergewichten berechnet, nicht angenommen)

Mit `r=64`, `α=256`: Skalierung Arm A = α/r = **4**, Arm B = α/√r = **32**, Verhältnis **8,000000**.
Aus den beiden `adapter_model.safetensors` (252 Modulpaare = 7 `target_modules` × 36 Layer,
0 nonfinite):

| Größe | Arm A (non-rsLoRA) | Arm B (rsLoRA) | Verhältnis |
|---|---|---|---|
| `max|ΔW|` | 0,15320010 | 0,74307668 | 4,85036666849851 (8 × 0,606295833562) |
| `‖ΔW‖_F` | 13,356301 | 105,620618 | A/B = 0,126455 |

Die Werte `0,15320010` / `0,74307668` / 252 Paare / 0 nonfinite / 4,85036666849851 sind **identisch** zu
den in Rek 129 §A1 unabhängig berechneten Werten für B2 / B2′ — die Mechanik ist damit unabhängig
bestätigt (Skalierung 32 statt 4 ⇒ 8× größere effektive Updateskalierung ⇒ Kollaps).

---

## 5. Score, Δ, Drift (§9.1d, `AGENTS.md:178-182`)

- **Score (externes Signal, unabhängig nachgerechnet):**
  - Arm B (rsLoRA, `use_rslora=true`): **1/15 = 6,7 %** (strict), Degeneration 13/15.
  - Arm A (non-rsLoRA, `use_rslora=false`): **15/15 = 100 %** (strict), keine Degeneration.
  - Referenz-Basis (unverändert): 0/15 (Basis kennt die 15 Gold-Texte nicht — Sollzustand des
    Write-Pfads, `AGENTS.md:250`, `:316-317`).
- **Δ Score gegenüber Baseline (B2′ = Arm B, 1/15 = 6,7 %):** **+93,3 pp** (1/15 → 15/15) für die
  non-rsLoRA-Konfiguration; Δ des rsLoRA-Arms zur Baseline = **0 pp** (identischer Adapter, identischer
  Score). Erwartungskorridor `P-131:150-160` (≥ 11/15) für Arm A: **erfüllt** (15/15).
- **Drift Modell-Parameter** (gefordert in `P-131:193-195`): π₀ = B2′-Adapter (`a595d437…`).
  `‖π_A − π₀‖/‖π₀‖` = **0,936747 (93,7 %)** — berechnet aus den ΔW-Matrizen beider Arme
  (Σ‖ΔW_A − ΔW_B‖²_F / Σ‖ΔW_B‖²_F, 252 Paare, 0 nonfinite).
  **⇒ 93,7 % ≫ Drift-Bound 10 % ⇒ Human-Gate (ask)**, `AGENTS.md:124`, `:171-176`.
- **Drift Code/Doku:** **0** — diese Iteration ändert keine Code- oder Originaldatei; neue Artefakte:
  diese Datei + 1 Indexzeile im README.

---

## 6. Gate (§9, `:116-124`) — Ergebnis: `ask`

| Bedingung | Wert | Ergebnis |
|---|---|---|
| Score ≥ 95 % **und** alle 8 Stufen „sicher" (`:118`) | Arm A 15/15 = 100 %, **aber** 8-Stufen-Zyklus für diesen Lauf **nicht** abgearbeitet + Memorizations-Bremse (§7.1) | **kein** automatisches allow |
| Score 70–94 % (`:119`) | — | nicht einschlägig (100 % bzw. 6,7 %) |
| Score < 70 % (`:120`) | rsLoRA-Arm 6,7 % | **deny** für diese Konfiguration |
| Neue Quelle (`:121`) | nein (arXiv:2312.03732, 2608.22215, 2609.36043 stehen in `AGENTS.md:393-411`) | — |
| Interface-Änderung (`:122`) | nein in dieser Iteration | — |
| self_update an Originaldatei (`:123`) | **Vorschlag** in §8: rsLoRA **nicht** als Default setzen ⇒ immer menschliches Gate | **ask** |
| Drift > 10 % (`:124`, `:171-176`) | Modell-Drift **93,7 %** | **ask** |

⇒ **Gate-Ergebnis: `ask`** — die Entscheidung „rsLoRA nicht als Standard" ist ein `self_update` an
Originaldateien und braucht nach §9 (`:123`) **immer** menschliche Freigabe; zusätzlich §9.3
(`:227-234`, zwei distinkte Personen). **Bis dahin bleibt der Lernpfad `deny`.**

---

## 7. Grenzen (ehrlich, §6)

1. **Memorization:** die 15 Zeilen sind **Trainingszeilen** (Dataset `18caaae7…`) ⇒ M2/M3 messen
   Memorization, keine Generalisierung (`manifest.json:grenzen[0]`). Ein Held-out-Probe-Set wäre der
   nächste Schritt für eine verwertbare „Lernwirkung"-Aussage.
2. **Ceiling:** Arm A beantwortet alle 15 Gold-Texte exakt (15/15) ⇒ M3 kann „Wissen" nicht von
   „Auswendiglernen" trennen (`manifest.json:grenzen[1]`).
3. **Implementierungslücke A2:** das Messskript implementiert die freigegebene A2-Auswertungsregel
   **nicht** (`P-131:162` „nicht angewendet"); die A/B-Entscheidung in §4.1 wurde aus den Rohzählern
   abgeleitet. Nachzuziehen wäre ein Code-Änderungs-Iterationsschritt (eigene Freigabe).
4. **Regel 6 nicht ausgeführt** (`regel6_reference.available: false`): kein Referenz-Altlauf übergeben
   (historischer B2′-Altlauf lag in dieser Session nicht vor) ⇒ der Abgleich gegen den Altlauf 2026-10-20
   ersetzt ihn inhaltlich (byte-identische `per_item.jsonl`, §3).
5. **`tokenizer_commit: null` (unresolved)** — der Tokenizer-Commit ist weiterhin nicht auflösbar; als
   Anker dient `fingerprints.tokenizer_chat_template_sha256: cd8e9439…` (`manifest.json:resolved_commits`).
6. **n = 15 ⇒ 1 Item = 6,7 pp, keine Signifikanz** (`manifest.json:thresholds.hinweis`).
7. **P-131 Auflage 2, Herleitung torchao:** die Auflage nennt als Beleg das Baseline-`library_versions`;
   dort steht torchao **nicht** (nur 7 Pakete). Die Forderung `torchao ≥ 0.16` ist durch
   `kaggle/write_back_cycle.py:576-584` und `kaggle/m1_m2_m3_probe.py:192-199` belegt (der Lauf
   verwendete torchao 0.18.0) — die **Herleitung im Proposal** bleibt zu korrigieren (Erratum, §9.3).
8. **Rek 129 §A1 („nur konsistent mit P-1, nicht bewiesen")** ist mit diesem Lauf **überholt**: der
   A/B kontrolliert die einzige Variable (`use_rslora`) unter identischem Code/Daten/Seed/Umgebung und
   reproduziert beide historischen Adapter bit-identisch.

---

## 8. Entscheidung, Vorschlag, nächster Schritt

- **Entscheidung (Messung):** **P-1 bestätigt** — die rsLoRA-Überskalierung (α/√r = 32 statt α/r = 4,
  8×) verursacht den Kollaps des Write-Back-Adapters (1/15 = 6,7 %, Degeneration 13/15 „Jamaica");
  die non-rsLoRA-Konfiguration liefert 15/15 ohne Degeneration bei identischen Daten, identischem Code,
  identischem Seed und identischer Umgebung.
- **Vorschlag (als **P-132** eingereicht und §9.3-freigegeben: Batnini + Taoufik, 2026-10-22; die
  Code-Änderung ist damit freigegeben, die Umsetzung steht aus — weiterhin **kein** `self_update`
  ohne ausgeführten Diff + Freigabe-Protokoll, §9/§9.3):**
  1. `LORA_USE_RSLORA` **nicht** als Standard (Default 0 bleibt) — bzw. rsLoRA im Write-Back-Pfad
     **abschalten** (`kaggle/train_slow_consolidation.py:63`, `kaggle/write_back_cycle.py` --use-rslora).
  2. Write-Back-Messung (Basis vor dem Wrap) beibehalten (Canary 15/15 belegt die adapter-freie Basis).
  3. **Held-out-Probe-Set** ergänzen, um Memorization von Lernwirkung zu trennen.
  4. A2-Regel in `kaggle/m1_m2_m3_probe.py` implementieren (Reinplementierung der Auswertung, kein
     Eingriff in Messwerte) und P-131-§8-Herkunft des torchao-Belegs als Erratum korrigieren.
  → Umsetzung als **Proposal** (§9.1d: Score-Änderung, Diff, Drift) mit erneuter §9.3-Freigabe.
- **Nächster Schritt:** Proposal P-132 (Punkte 1–4) formulieren; bis dahin keine Änderung an
  Originaldateien, Lernpfad bleibt `deny`.

---

## 9. Self-Feedback t+1

- **Was ich gelernt:** Ein kontrollierter A/B mit *einer* veränderten Variablen und bit-identischer
  Reproduktion der historischen Artefakte ist stärker als jede statistische Argumentation — hier
  trägt der **Kontrast** (1/15 + Degeneration vs. 15/15 ohne Degeneration) bei identischem Code, Daten,
  Seed und Umgebung. Ebenso: eine freigegebene Auswertungsregel, die das Messskript nicht implementiert,
  ist eine **Lücke**, die offengelegt gehört (Rek 131 → A/B; jetzt: A2 vs. Skript-Regel 9).
- **Was unverändert bleibt:** §6 (keine Erfindung, Compare nur mit externem Signal), Guardrail 7 (echte
  Läufe, echte Artefakte, unabhängige Nachrechnung), §9.3 (zwei distinkte Personen für Freigaben),
  Guardrail 6 (Git nur mit Erlaubnis — **hier offen**).

---

## 10. Quellen

- `AGENTS.md:61-68` (§6), `:95-109` (Guardrails 1–8), `:116-124` (§9), `:165-176` (§9.1c), `:178-182` (§9.1d), `:214-234` (§9.3), `:250`/`:271-276`/`:304-331` (§10.1/§10.3/§10.7)
- `ergebnisse/proposals/P-131-kontrollierter-rslora-ab.md` (approved §9.3 Batnini + Taoufik 2026-10-21): `:34-43`, `:48-72`, `:126-142`, `:148-169`, `:180-197`, `:216-233`, `:237-264`
- `ergebnisse/rekursion/129-b2-prime-annahmenpruefung.md` (§A1–A4, 9 Regeln, §M5), `ergebnisse/rekursion/130-m1-m2-m3-lauf-b2-prime-messung.md` (Baseline, M1–M5, Erratum E1), `ergebnisse/rekursion/131-ds15-datensatz-bereitstellung-kaggle-ab.md` (Bereitstellung, Auflagen-Abgleich)
- Code: `kaggle/train_slow_consolidation.py:53-65`, `:192-212`, `:215-222`, `:394`, `:448-449` · `kaggle/m1_m2_m3_probe.py:152-156`, `:192-199`, `:406-417`, `:580-621` · `kaggle/m1_m2_m3_preregistration.md:99` · `kaggle/write_back_cycle.py:420-421`, `:442-445`, `:576-584` · `data/memory/acceptance_gate.py:114-131`
- Gesetzestests: `tests/test_agents_law.py:46-55`, `:77-85`
- Messartefakte (extern): HF `Batnini/knowledge-agent-write-back` → `probe/ab_2026-10-22/`
  (`status.json` `1098481a…`, `manifest.json` `9ceca3cd…`, `per_item.jsonl` `95ceabbc…`),
  `ab_rsloRa0/{adapter/adapter_model.safetensors e3be2c85…, adapter/adapter_config.json 56cc999b…,
  kaggle_output.json b49a5d0b…}`, `ab_rslora1/{adapter/adapter_model.safetensors a595d437…,
  adapter/adapter_config.json 3df21013…, kaggle_output.json c9feeccf…}`; Baseline-Adapter
  `adapter/` Revision `f704f4a12df53966095604cce824c0d7785b1446` (B2′) und `04ed1333…` (B2);
  Baseline-Probe `probe/m1_m2_m3_2026-10-20/`
- arXiv:2312.03732 (rsLoRA, α/√r) · arXiv:2608.22215 §3.4 (Write-Back/Slow Consolidation) · arXiv:2609.36043 (SAGE, Grader/Referenz-Logik) · arXiv:2609.08832 (Consistency Gap)
