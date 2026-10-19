# 126 — A/B-Design Write-Back-Verbesserung (vor dem nächsten Kaggle-Lauf)

- **Datum:** 2026-10-19
- **Ziel `g`:** Vor dem nächsten Write-Back-Lauf ein A/B-Design festlegen, das die
  drei in Rek 125 belegten Maßnahmen (LoRA+ LR, rsLoRA-Scaling, Full Fine-Tuning)
  auf unserer Konfiguration testet — **ohne Code-Änderung an
  `kaggle/write_back_cycle.py`** (Interface-Stabilität, Guardrail 4).
  Quelle des Auftrags: Nutzer-Prompt 2026-10-19 („Write-Back-Verbesserung nach
  Rek 125").
- **Gesetz:** `AGENTS.md` §6 (keine Erfindungen), §9 (Gate), §9.1d (Evidenz),
  §9.3 (Zwei-Personen), §10.3 (Write-Back), Guardrail 3/4/6/7.
- **Status dieser Datei:** **A/B-Design-Dokumentation (Schritt 1 des Auftrags).**
  Kein `self_update`, keine Code-Änderung, kein Lauf. Schritt 2 (Code) und
  Schritt 3 (Kaggle-Lauf) sind **nicht** umgesetzt — sie warten auf Human-Gate
  (§9 Z.121) + §9.3 (§6 unten).

---

## 1. Ausgangslage — Rek 125 (gemessen)

Quelle: `ergebnisse/rekursion/125-write-back-3b-adapter-wirkungslos.md` (2026-10-19).

- **Befund (Rohtext `125:83-84`):** „bei allen 15 Proben ist `answer == base_answer`
  — der Adapter hat keine einzige Antwort verändert."
- **§9-Gate (Rohtext `125:11-12`):** Compare-Score **2/15 = 13,3 % ≪ 70 %** ⇒
  **deny** — kein `self_update`, keine positive Behauptung, dass Write-Back
  funktioniert (`125:183-185`).
- **Δ = 0** (`125:107`): `em_base = 2/15` · `em_adapter = 2/15` · `Δ = 0`.
- **Ursache laut Rek 125, teilweise belegt (`125:121-160`):** TMLR (arXiv:2405.09673)
  „r=16 learns less"; LoRA+ (arXiv:2402.12354) „same learning rate for A and B …
  not allow efficient feature learning"; rsLoRA (arXiv:2312.03732) Scaling
  α/r → α/√r. **Einschränkung (Rohtext `125:160`-Nähe + Indexzeile):** „Übertragung
  auf unsere Konfiguration nicht direkt getestet."
- **`125:212-219`:** „Vor einem Kaggle-Lauf muss ein A/B-Design festgelegt werden
  (Baseline vs. geänderte Parameter), sonst ist der Vergleich nicht aussagekräftig."
  → Diese Datei ist die Erfüllung dieser Pflicht.

---

## 2. Korrekturen an den Auftrags-Annahmen (belegt, Multi-Agent-Recherche 2026-10-19)

Der Nutzer-Auftrag 2026-10-19 enthielt Annahmen, die **nicht** mit dem Code/Quellen
übereinstimmen. Sie werden hier korrigiert (§6: keine unbelegten Annahmen).

| # | Auftrag (Annahme) | Befund (belegt) | Beleg |
|---|---|---|---|
| K1 | arXiv-Titel: „LoRA+: Learning Rate for LoRA Adapter" | **Falsch.** Echter Titel: „LoRA+: Efficient Low Rank Adaptation of Large Models" (Hayou, Ghosh, Yu; v1 19.02.2024). Kernsatz η_B = λ·η_A sinngemäß belegt (Abstract: „different learning rates … with a well-chosen ratio"), **nicht** wörtlich. | arxiv.org/abs/2402.12354 |
| K2 | arXiv-Titel: „rsLoRA: Rank-Stabilized LoRA" | **Falsch.** Echter Titel: „A Rank Stabilization Scaling Factor for Fine-Tuning with LoRA" (Kalajdzievski, solo; v1 28.11.2023). Kernsatz α/√r **nahezu wörtlich** belegt. | arxiv.org/abs/2312.03732 |
| K3 | arXiv:2405.09673 belege „r=16 lernt weniger; r=256 datensatzabhängig" | **Teilweise.** Titel „LoRA Learns Less and Forgets Less" (TMLR Featured, Aug 2024) stimmt; „substantially underperforms full finetuning" ist im Abstract. **Aber: r=16 und r=256 stehen NICHT im Abstract** — nur „rank that is 10-100X greater than typical LoRA configurations". Die konkreten Rangzahlen stammen aus dem Paper-Body, nicht aus dem Abstract. | arxiv.org/abs/2405.09673 |
| K4 | neue CLI-Args `--lora-r --lr-a --lr-b --lora-scaling --full-ft` in `kaggle/write_back_cycle.py` | **Die 5 Args existieren nicht** (Bestätigung des Auftrags). **Wichtiger:** `write_back_cycle.py` enthält **überhaupt keine LoRA-Hyperparameter** — es startet `train_slow_consolidation.py` als Subprocess und setzt nur `BASE_MODEL` + `SEED` (`kaggle/write_back_cycle.py:303-305`). Die HP stecken in `kaggle/train_slow_consolidation.py:49-52` als **ENV-Variablen** (`LEARNING_RATE=2e-4`, `LORA_R=16`, `LORA_ALPHA=32`, `LORA_DROPOUT=0.05`). | `write_back_cycle.py:303-317`; `train_slow_consolidation.py:49-52`, `:414-421`, `:429` |
| K5 | „Tests: `tests/test_write_back_cycle.py` erweitern" | **Datei existiert nicht.** WBC wird abgedeckt von `tests/test_heldout_split.py:20` (Import `write_back_cycle as wbc`; 6 Tests) und `tests/test_grader_consistency.py:46` (2 Tests). Nicht abgedeckt: `main()`, `_parse_args`, `_write_facts`, `_make_train_fn`, `_ThetaProbe`. | `ls tests/test_write_back_cycle.py` → No such file |

**Kernkonsequenz (K4):** Der umweltbasierte Pfad ist **offen** — `write_back_cycle.py:303`
lautet `env = dict(os.environ)` und kopiert die **gesamte** Umgebung an den
Subprocess weiter. `train_slow_consolidation.py:49-52` liest `LORA_R`, `LORA_ALPHA`,
`LEARNING_RATE` daraus. → Variante 2 (rsLoRA-Scaling) ist **ohne Code-Änderung**
per Umgebungsvariable steuerbar (§3, B2).

---

## 3. A/B-Design (festgelegt VOR jedem Lauf — §6/§9.1d)

**Metrik (primär, aus Auftrag):** `answer != base_answer` bei **≥ 1/15 Proben**
⇒ „Adapter hat Wirkung". (Rek 125: 0/15.) **Sekundär (§9):** Compare-Score via
`acceptance_gate.grade` (strict EM), Schwelle 70 % für `self_update` bleibt
unverändert bestehen — Wirkung ≠ Freigabe.

**Konstante Baseline (A = IST-Zustand, identisch für alle Läufe):**

| Parameter | Wert | Beleg |
|---|---|---|
| Base-Modell | `Qwen/Qwen2.5-3B-Instruct` | `125:30-37` (Lauf-Befehl) |
| `NUM_EPOCHS` | 15 | `125:30-37` |
| `LORA_R` | 16 | `train_slow_consolidation.py:50` |
| `LORA_ALPHA` | 32 | `train_slow_consolidation.py:51` |
| `LEARNING_RATE` | 2e-4 | `train_slow_consolidation.py:49` |
| `LORA_DROPOUT` | 0.05 | `train_slow_consolidation.py:52` |
| Proben | n = 50 Writes / 15 Probe-Fakten, Seed 42 | `125:30-37` |
| Scaling (abgeleitet) | α/r = 32/16 = **2** | peft-Default, `scaling=lora_alpha/r` |

### Varianten (A vs. B1/B2/B3)

| ID | Variante | Parameter | Quelle | Code nötig? | ENV-Pfad möglich? |
|---|---|---|---|---|---|
| **A** | Baseline (IST) | r=16, α=32, lr=2e-4, use_rslora=False, LoRA | Rek 125 (gemessen) | nein | — (IST) |
| **B1** | LoRA+ LR | η_A = 2e-4, η_B = λ·η_A, **λ=10** ⇒ η_B = 2e-3; r/α unverändert | arXiv:2402.12354 (§2 K1) | **ja** | **nein** — `train_slow_consolidation.py` hat nur **einen** `LEARNING_RATE` (Z.49); peft 0.21.2 bietet `create_loraplus_optimizer(..., loraplus_lr_ratio=λ)` (`peft/optimizers/loraplus.py:32-34,107`) mit 4 Parametergruppen, Übergabe via `SFTTrainer(optimizers=(opt, sched))` |
| **B2** | rsLoRA-Scaling | **r=64**, Scaling α/√r ⇒ α=32 ⇒ 32/√64 = **4** (IST-Baseline war 2) | arXiv:2312.03732 (§2 K2) | **nein** (siehe rechts) | **ja** — ohne Code: `LORA_R=64 LORA_ALPHA=256` ⇒ peft rechnet α/r = 256/64 = **4** (gleicher Wert wie rsLoRA). **Ehrlich:** peft-Flag `use_rslora=True` (seit 0.8.0, `lora/tuners/lora/config.py:661-671`) wird damit **nicht** gesetzt; der Skalen-Wert ist identisch, der Code-Pfad bleibt α/r. Sauberer Weg mit Code: `LoraConfig(use_rslora=True, r=64, lora_alpha=32)` (`lora/layer.py:278-281`) |
| **B3** | Full Fine-Tuning | kein LoRA, **kein** 4-bit-QLoRA (Gegenreferenz) | arXiv:2405.09673 (§2 K3) | **ja** | **nein** — `peft_config=None` (trl 1.14.2, `sft_trainer.py:906-912`, Default) + `BitsAndBytesConfig` weglassen; `train_slow_consolidation.py:414-421` hat `LoraConfig` fest verdrahtet, `:404-409` 4-bit |

**Reihenfolge (aus Auftrag, mit Begründung):** B2 zuerst — es ist die einzige
Variante **ohne Code-Änderung** (K4), ändert nichts an bestehenden Signaturen
(Guardrail 4) und testet eine der drei belegten Maßnahmen direkt. Danach B1
und B3 (brauchen Code, §5).

**Vergleichslogik (A vs. Bx, gemessen vs. nicht gemessen):** Jeder Lauf erzeugt
15 Paare `(base_answer, answer)` (strict EM via `acceptance_gate.grade`, identisch
zu Rek 125 §3.4). Verglichen wird **nur** Wirkung (`answer != base_answer`) und
Δ (em_adapter − em_base) **innerhalb** desselben Laufs — **nicht** über Läufe
hinweg (verschiedene Adapter, kein identischer Seed-Verlauf). Der Δ-Wert aus
Rek 125 (Δ=0) ist der A-Baseline-Wert.

---

## 4. Lauf-Befehl B2 (Dokumentation — wird NICHT von diesem Agenten ausgeführt)

Kaggle-Zelle, abgeleitet aus Rek 125 §2 (`125:30-37`) + ENV-Festlegung B2.
**Wirkung nur, wenn der Mensch ihn auf Kaggle startet (Gate, §6).**

```text
LORA_R=64 LORA_ALPHA=256 NUM_EPOCHS=15 python kaggle/write_back_cycle.py \
  --n 50 --gpu 0 \
  --base-model Qwen/Qwen2.5-3B-Instruct \
  --approver Batnini --approver Taoufik \
  --workdir /kaggle/working \
  --llm-base-url http://127.0.0.1:11434/v1 \
  --llm-model qwen2.5:1.5b
```

Erwartetes Ergebnis-Format (unverändert, Interface-Stabilität):
`write_back_cycle_result.json` mit `answer`/`base_answer` je Probe — identisches
Schema wie Rek 125 §3.4. Ergebnis → Rek 127 mit Rohdaten (§9.1d).

---

## 5. Was Schritt 2 (Code) bräuchte — und was NICHT geändert werden darf

**Guardrail 4 (Interface-Stabilität):** keine bestehende Signatur ändern.
Unverändert bleiben (belegt `write_back_cycle.py:428-704`):
`main(argv=None)`, `_parse_args(argv=None)`, `select_tasks`, `_write_facts`,
`_make_train_fn`/`train_fn`, `_ThetaProbe`, `_configure_llm_env`, `_grade is ag.grade`.

**Additive Änderungen (nur mit Gate, §6), minimaler Umfang:**

1. `write_back_cycle.py:_parse_args` — **nur anhängen** (Default = IST, damit
   bestehende Läufe unverändert laufen): `--lora-r` (None), `--lora-alpha` (None),
   `--learning-rate` (None), `--use-rslora` (store_true), `--full-ft` (store_true).
   **Nicht** `--lr-a/--lr-b` separat (peft erwartet `loraplus_lr_ratio`, kein Paar) —
   stattdessen `--lora-plus-ratio` (float, Default None).
2. `write_back_cycle.py:_make_train_fn`/`train_fn` — nur ENV-**Durchreichung**
   ergänzen, wenn das Arg gesetzt ist (`env["LORA_R"] = str(v)` etc.), wie bei
   `BASE_MODEL`/`SEED` (`:303-305`). Default `None` ⇒ **kein** `env`-Eintrag ⇒
   Default in `train_slow_consolidation.py:49-52` greift ⇒ IST-Zustand.
3. `train_slow_consolidation.py` — ENV-Variablen `LORA_USE_RSLORA`,
   `LORA_PLUS_RATIO`, `FULL_FT` ergänzen; in `LoraConfig` (`:414-421`)
   `use_rslora=…`; bei `FULL_FT`: `peft_config=None` + `BitsAndBytesConfig` weglassen
   (`:404-409`); bei `LORA_PLUS_RATIO`: `create_loraplus_optimizer` +
   `SFTTrainer(optimizers=(opt, sched))` (peft ≥0.13.0, in 0.21.2 vorhanden).
4. Tests: **neue** Datei `tests/test_write_back_cycle.py` (§2 K5: existiert nicht)
   **oder** Erweiterung `tests/test_heldout_split.py` (6 bestehende Tests) +
   `tests/test_grader_consistency.py` (2 Tests) — Prüfung: Defaults unverändert
   (A ≡ IST), Args-Defaults None ⇒ kein env-Eintrag, `--use-rslora` setzt ENV.

**Keine dieser Änderungen ist umgesetzt.** Guardrail 4 + §9 „Interface-Änderung ⇒
immer menschliches Gate" ⇒ Schritt 2 ist blockiert, bis Freigabe vorliegt.

---

## 6. Gate-Status und offene Punkte (ehrlich, §9.1d)

**Umsatzstand:**

| Schritt | Auftrag | Status |
|---|---|---|
| 1 — A/B-Design dokumentieren | `126-ab-design-write-back.md` | **erledigt (diese Datei)** — keine Freigabe nötig (reine Doku, kein self_update, kein Code) |
| 2 — Code (`--lora-r` etc.) | nur mit Human-Gate | **nicht umgesetzt** — wartet auf §9 Z.121 + §9.3 |
| 3 — Kaggle-Lauf (B2 zuerst) | nur nach Human-Gate + §9.3 | **nicht umgesetzt** — wartet auf Freigabe |

**Gate-Kriterien (aus Auftrag, verbindlich vor Schritt 2):**
- Human-Gate: Nutzer erteilt Freigabe (§9 Z.121).
- Zwei-Personen: **Batnini + Taoufik** (§9.3, `pending → first_approved →
  second_approved → approved`, ≥ 2 distinkte Personen).
- Interface-Stabilität: keine bestehende Signatur geändert (Guardrail 4).

**Verbot (unverändert):** kein `git add/commit/push` (Guardrail 6); keine
unbelegten Empfehlungen (§6); kein `self_update` ohne `approved` (§9).

**Offene Punkte (nicht gelöst, nicht erfunden):**
- Rek 125 §9-Gate = **deny**. Das verbietet `self_update` und positive Behauptungen
  über Write-Back. Dieses Design **behauptet nichts Positives** — es legt ein
  Experiment fest. Der neue Lauf (Schritt 3) ist ein **neues Experiment**, kein
  `self_update` — die Freigabe dafür ist **separat** und ausstehend.
- Wirkung ≠ Freigabe: Auch wenn B2 `answer != base_answer` bei ≥1/15 liefert,
  bleibt der §9-Score (70 %) die Schwelle für `self_update`.
- Grund für Rek-125-Adapter-Wirkungslosigkeit ist **nicht abschließend** belegt
  (3 Quellen, Übertragung ungetestet — Rohtext `125:160`-Nähe). B2 ist der erste
  direkte Test einer der drei Maßnahmen auf unserer Konfiguration.
- `use_rslora=True` (sauberer peft-Pfad) vs. ENV-Workaround `LORA_ALPHA=256`
  (gleicher Skalen-Wert, Flag=False): B2 nutzt den ENV-Pfad (**ohne** Code).
  Der Flag-Weg ist in §5 als Schritt-2-Änderung dokumentiert, nicht umgesetzt.
- Rek 127 (Ergebnis) und ggf. Rek 128 (Schritt 2) sind **offen**.

---

## 7. Quellen (korrigierte Titel, §6 — was belegt, was nicht)

| # | Quelle | Belegt (Originalformulierung) | NICHT belegt (Ehrlich-Hinweis) |
|---|---|---|---|
| 1 | arXiv:2312.03732 („A Rank Stabilization Scaling Factor for Fine-Tuning with LoRA", Kalajdzievski, 28.11.2023) | „LoRA adapters should be divided by a factor of the square root of the rank" (nahezu wörtlich) | Nicht: dass r=64 auf **unserem** ZsRE-Datensatz hilft |
| 2 | arXiv:2402.12354 („LoRA+: Efficient Low Rank Adaptation of Large Models", Hayou/Ghosh/Yu, 19.02.2024) | „different learning rates for the LoRA adapter matrices A and B with a well-chosen ratio"; Formel η_B=λ·η_A im Body | Nicht: λ=10 als optimal; nicht: Wirkung bei 3B/4-bit |
| 3 | arXiv:2405.09673 („LoRA Learns Less and Forgets Less", Biderman et al., TMLR Aug 2024) | „LoRA substantially underperforms full finetuning"; „rank that is 10-100X greater than typical LoRA configurations" | **Nicht im Abstract:** die Zahlen r=16 und r=256 (stammen aus dem Body, nicht aus dem Abstract) |
| 4 | peft 0.21.2 (`peft/optimizers/loraplus.py:32-34,107`; `tuners/lora/config.py:661-671`; `tuners/lora/layer.py:278-281`) | `create_loraplus_optimizer(..., loraplus_lr_ratio=λ)` (seit 0.13.0); `use_rslora=True` ⇒ `scaling = lora_alpha/math.sqrt(r)` (seit 0.8.0) | Nicht: dass peft in unserem Subprocess geladen wird (peft ist lazy-import in WBC `:376`) |
| 5 | trl 1.14.2 (`trl/trainer/sft_trainer.py:906-912,940-941`) | `peft_config=None` ⇒ Modell nicht gewrappt (Default); `load_in_4bit` „Works only with LoRA" | Nicht: dass Full-FT auf T4 (16 GB) mit 3B in 15 Epochen machbar ist (Speicher/Zeit **nicht gemessen**) |
| 6 | Projektcode (belegt, §2 K4/K5) | `write_back_cycle.py:303-305` (`env = dict(os.environ)`); `train_slow_consolidation.py:49-52,414-421,429` | Nicht: dass die ENV-Werte den Trainingsverlauf beeinflussen (das ist die **Hypothese** dieses Designs) |

**Keine externe Quelle wurde erfunden.** Alle Titel oben wurden über
`arxiv.org/abs/<ID>` abgerufen (2026-10-19); die Abweichungen zu den im
Nutzer-Auftrag behaupteten Titeln sind in §2 K1–K3 korrigiert.

---

## 8. Provenienz-Nachtrag (Guardrail 3, §9.1d)

- **Anlass:** Nutzer-Auftrag 2026-10-19 („Write-Back-Verbesserung nach Rek 125",
  Multi-Agent-Umsetzung, Schritt 1 = A/B-Design vor Lauf).
- **Verfahren:** 4 Multi-Agent-Recherchen (nur lesend, keine Änderungen, kein git):
  (i) Rek 125 vollständig gelesen; (ii) `write_back_cycle.py` CLI/Signaturen/ENV;
  (iii) 3 arXiv-Seiten abgerufen (Titel + Kernsätze); (iv) peft 0.21.2 + trl 1.14.2
  Implementierungspfade. Ergebnisse in §2 (Korrekturen) und §3/§5 (Design).
- **Werte-Herkunft:** Baseline-Werte aus `train_slow_consolidation.py:49-52`
  (Default-ENV, nicht geschätzt); Scaling α/r = 32/16 = 2 abgeleitet (peft-Default,
  `lora/layer.py`); B2-Wert 256/64 = 4 = 32/√64 rechnerisch geprüft (§3).
- **Was NICHT belegt ist:** ob B1/B2/B3 die Adapter-Wirkung auf ≥1/15 Proben
  heben (Hypothese, gemessen erst im Lauf nach §6-Gate); ob Full-FT auf T4
  läuft (nicht gemessen).
- **Was NICHT umgesetzt ist:** Schritt 2 (Code), Schritt 3 (Kaggle-Lauf),
  Rek 127, §9-Freigabe für den neuen Lauf.
- **Git-Integrität (Guardrail 6):** kein `git add/commit/push`. HEAD zum Zeitpunkt
  der Dokumentation: `5650b3c` (belegt via `git rev-parse --short HEAD`).
- **Freigabe:** **keine** — diese Datei ist Dokumentation (Schritt 1), kein
  `self_update` und keine Interface-Änderung. Schritt 2+3 benötigen
  Human-Gate + §9.3 (Batnini + Taoufik), §6.
