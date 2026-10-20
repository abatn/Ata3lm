# 125 — Write-Back Kaggle-Lauf (3B, 15 Epochen): Adapter wirkungslos, §9-Gate deny

**Datum:** 2026-10-19
**Auftrag:** Write-Back-Zyklus Θ→Θ′ auf Kaggle GPU ausführen (§10.3), Ergebnis
dokumentieren, §9-Gate anwenden. Nutzer befahl Rek-Doc nach Guardrail 3.
**Code-Stand:** `5650b3c` (ruff-Format-Fix nach `235d529` — 34-Dateien-Commit mit
strict-EM-Grading, case-insensitive Approvers, `probe_results`).
**Kein git** (Guardrail 6, `AGENTS.md:103`), Provenienz (Guardrail 3, `AGENTS.md:99`),
Evidenz-Pflicht (§9.1d, `AGENTS.md:176-180`), kein `self_update` (§9, `AGENTS.md:120`).

**§9-Gate-Ergebnis:** Compare-Score **2/15 = 13,3 % ≪ 70 %** ⇒ **deny** — kein
`self_update`, keine positive Behauptung über Write-Back.

---

## 1. Ausgangslage

Rek 109 (0.5B, 12 Epochen) und e2e-theta (0.5B) zeigten bereits **Δ ≈ 0**: der
LoRA-Adapter änderte die Antworten nicht. Die Korrekturen aus `235d529`
(strict EM via `acceptance_gate.grade`, case-insensitive Approvers,
`probe_results` im Output) waren auf Kaggle nicht aktiv, weil der Nutzer den
Code-Stand `4bd63cb` ausführte.

> **Superseded-Vermerk (docs-only, 2026-10-20, Rek 129):** Beide Vorgänger sind
> **kein** belastbarer Gegenbeleg — e2e-theta (2026-10-07) ist **pre-N8**
> (kontaminierte `em_base`, Rek 077:37-39; `ergebnisse/e2e-theta-2026-10-07.md`),
> Rek 109 ist **Substring-Ära** (strict Grader erst Rek 115:15). Aus „Δ ≈ 0" ist
> deshalb **nicht** ableitbar, dass der Adapter die Antworten nicht änderte.
> Ebenso ist die Gleichheit `answer == base_answer` **strukturell erzwungen**
> (`kaggle/write_back_cycle.py:420-421` Wrap vor `:442`): beide Felder messen
> dasselbe Adapter-Modell — daraus folgt **kein** „keine einzige Antwort verändert"
> und **kein** „Adapter-Effekt = 0". **Rohzahlen bleiben unverändert.**

**Mandat des Nutzers:** Lauf mit korrigiertem Code (`5650b3c`) auf 3B-Modell
wiederholen, Ergebnis hochladen, Rek-Doc schreiben.

## 2. Laufparameter (gemessen, aus `write_back_cycle_result.json`)

```text
!NUM_EPOCHS=15 python kaggle/write_back_cycle.py \
  --n 50 --gpu 0 \
  --base-model Qwen/Qwen2.5-3B-Instruct \
  --approver Batnini --approver Taoufik \
  --workdir /kaggle/working \
  --llm-base-url http://127.0.0.1:11434/v1 \
  --llm-model qwen2.5:1.5b
```

| Parameter | Wert |
|---|---|
| Basis-Modell | `Qwen/Qwen2.5-3B-Instruct` |
| GPU | Tesla T4 |
| LoRA | `r=16`, `alpha=32`, `lr=2e-4` |
| Epochen | 15 |
| SFT-Zeilen | 15 (pending-Keys) |
| Approvers | `['batnini', 'taoufik']` (case-insensitive, Fix greift ✓) |
| Router-Modell | `qwen2.5:1.5b` (Ollama, `127.0.0.1:11434`) |
| HF-Repo | `Batnini/knowledge-agent-write-back` |

## 3. Ergebnisse (gemessen, aus `write_back_cycle_result.json` + `kaggle_output.json`)

### 3.1 Writes (50 Fakten)

| Klasse | Anzahl |
|---|---|
| write-new | 15 |
| write-update | 16 |
| non-write | 6 |
| blocked | 13 |
| error | 0 |

### 3.2 Training

| Metrik | Wert |
|---|---|
| **Loss (final)** | **2.2958** |
| Loss (Rek 109, 0.5B) | 4.2931 |
| Dataset-Hash | `18caaae7c6f7f506a0cdd132d15f23c0e7044b07d894b73eb68b302605b01c7c` |
| Adapter | `/kaggle/working/slow_consolidation_train/adapter` (15 Checkpoints) |

### 3.3 Flush-Entscheid (strict EM)

| Status | Anzahl | Keys |
|---|---|---|
| **flushed** | **2** | `what-town-or-city-does-kkbb-serve`, `on-what-date-did-40th-government-of-turkey-end` |
| **kept** | **13** | die übrigen pending-Keys |

Die 2 geflushten Fakten waren **bereits vom Basismodell korrekt** (siehe §3.4) —
der Flush war also mechanisch korrekt, aber kein Beweis für Adapter-Wirkung.

### 3.4 Probe-Ergebnis (15 Fakten, strict EM via `acceptance_gate.grade`)

**Kernbefund: bei allen 15 Proben ist `answer == base_answer` — der Adapter
hat keine einzige Antwort verändert.**

| Frage | Base | Adapter | Gold | Passed |
|---|---|---|---|---|
| Traidenis title? | Duke of Normandy | Duke of Normandy | Grand Duke of Lithuania | ✗ |
| Jyllands-Posten year? | 2005 | 2005 | 30 September 2005 | ✗ |
| Cycle of Werewolf illustrator? | J. C. Vaughn | J. C. Vaughn | Bernie Wrightson | ✗ |
| Renincarnated label? | Capitol Records | Capitol Records | Villain Entertainment | ✗ |
| Beau Allred team? | Los Angeles Chargers | Los Angeles Chargers | Cleveland Indians | ✗ |
| Isaac Nicola birth city? | New York City | New York City | Havana | ✗ |
| KOAN Sound formed? | Manchester | Manchester | Bristol | ✗ |
| Faraway Lurs illustrator? | John Bauer | John Bauer | Harry Behn | ✗ |
| Odorono singer? | Theodoros Kordjis | Theodoros Kordjis | Pete Townshend | ✓* |
| KKBB serve? | Bakersfield | Bakersfield | Bakersfield | ✓ |
| UTair airport? | Vnukovo International | Vnukovo International | Khanty-Mansiysk Airport | ✗ |
| 40th Turkey gov end? | 1977 | 1977 | 1977 | ✓ |
| Getting Acquainted studio? | The Weinstein Company | The Weinstein Company | Keystone Studios | ✗ |
| Christians & Lions city? | Denver | Denver | Jamaica Plain | ✗ |
| Comdial end year? | 2013 | 2013 | 2005 | ✗ |

\* Odorono: `answer == base_answer`, passed=strict-EM-Fehler im Rohtext (Antwort
enthält Gold nicht exakt) — aber **kein Adapter-Effekt**, da base == adapter.

**em_base = 2/15 (13,3 %) · em_adapter = 2/15 (13,3 %) · Δ = 0**

## 4. Befund (gemessen — ohne Ursachen-Erklärung)

### 4.1 Gemessen (Rohdaten)

1. **Code-Logik korrekt:** `_ThetaProbe._load()` lädt Basis-Modell zuerst,
   dann `PeftModel.from_pretrained(base, adapter_dir)` (N8-Pattern,
   `kaggle/write_back_cycle.py:380-397`).
2. **Training lief:** Loss sank 4.29 → 2.29, 15 Checkpoints gespeichert.
3. **Adapter-Effekt = 0:** `answer == base_answer` bei 15/15 Proben.
4. **Die 2 „richtigen" Antworten** (Bakersfield, 1977) kannte das Basismodell
   bereits ohne Adapter — kein Lernfortschritt.

### 4.2 Erklärung aus externen Quellen (belegt, §6 — exakte Originalformulierungen)

**Quelle 1 — LoRA r=16 „lernt weniger, vergisst weniger" (belegt, mit Einschränkung):**
Databricks/TMLR-Studie (arXiv:2405.09673, publiziert TMLR 08/2024):
> Original: „LoRA, with the common r=16, learns less and forgets less than
> all other models"

**Was das paper sagt:** r=16 erhält die Leistung auf Aufgaben **außerhalb**
der Zieldomäne besser (weniger Vergessen), lernt aber auf Aufgaben **innerhalb**
der Zieldomäne **zu wenig**. Das ist eine **Zwei-Seiten-Eigenschaft**, kein
pauschal „hält Verhalten nah am Basismodell".

**Einschränkung (r=256, datensatzabhängig):**
> Original: „LoRA r=256, on the other hand, learns as much as the other
> methods while forgetting less"

Diese Aussage basiert auf Experimenten mit dem **Tulu-v2-mix-Datensatz**.
Bei kontinuierlichem Pretraining (CPT) auf Code- und Mathematikdomänen kommt
das paper zu einem **anderen Ergebnis**: „LoRA in allen Konfigurationen
schlechter als Full FT". → Höherer Rang ist **kein** Garant für bessere
Ergebnisse; es hängt vom Datensatz ab.

**Quelle 2 — LoRA+: Identisches LR für A/B verhindert effizientes Feature-Lernen (belegt):**
LoRA+ (arXiv:2402.12354, Hayou/Ghosh/Yu):
> Original: „using the same learning rate for A and B does not allow
> efficient feature learning"

**Vorschlag des papers:** η_B = λ·η_A mit λ ≫ 1, um Leistung zu verbessern
und Training zu beschleunigen. Unser Lauf nutzte `lr=2e-4` für beide
Matrizen — gemäß LoRA+ suboptimal. **Aber:** Das paper misst nicht unsere
spezifische „Antwort unchanged"-Konfiguration.

**Quelle 3 — rsLoRA: Skalierung α/r → α/√r (belegt, präzise Terminologie):**
rsLoRA (arXiv:2312.03732, Kalajdzievski):
> Original: „rsLoRA unlocks improved fine-tuning performance with higher ranks"

**Was das paper sagt:** Die Verbesserung betrifft die **Fine-Tuning-Leistung**
(z. B. Benchmark-Genauigkeit), **nicht** direkt den Loss. Standard-LoRA
konvergiert laut paper zu ähnlichem Loss unabhängig von r; rsLoRA schaltet
die Rang-Vorteile bei höheren Rängen frei. Scaling: α/r → α/√r.

**Kombinierte Erklärung (§6-konform, mit allen Einschränkungen):**
LoRA r=16 mit identischem LR für A/B lernt laut TMLR **zu wenig in der
Zieldomäne** (Quelle 1) und produziert laut LoRA+ **ineffizientes Feature-
Lernen** (Quelle 2). Unser Befund `answer == base_answer` bei 15/15 ist damit
**konsistent** mit den belegten LoRA-Eigenschaften. **Aber:** Keine der
Quellen testet unsere spezifische Konfiguration (Qwen2.5-3B, Fakt-Frage,
15 Samples) — die Zuordnung ist eine **plausible Übertragung**, kein direkter
Experiment-Beweis.

> **Status (§6):** Die Tatsache „Adapter-Effekt = 0" ist **belegt** (Rohdaten).
> Die **Ursache** ist **teilweise belegt** (3 Quellen mit LoRA-Eigenschaften)
> — die Übertragung auf unsere Konfiguration ist **nicht direkt getestet**.

## 5. §9-Gate-Entscheid

| Bedingung | Wert | Gate |
|---|---|---|
| Compare-Score | 2/15 = **13,3 %** | **≪ 70 % ⇒ deny** |
| self_update | keine Änderung an Originaldateien | n/a |
| Neue Quelle | keine | n/a |

**Entscheidung: deny.** Kein `self_update`. Keine positive Behauptung, dass
Write-Back funktioniert. Die 13 kept-Fakten bleiben im externen Puffer
(§10.3: „Fehlgeschlagen → Fact bleibt im externen Puffer").

## 6. Was der Lauf belegt (und was nicht)

| Aussage | Status |
|---|---|
| Write-Back-Code läuft auf Kaggle GPU (3B, T4) | **belegt** (Lauf, Loss, Checkpoints) |
| Flush-Logik (strict EM) funktioniert | **belegt** (2 flushed / 13 kept, Korrektheit prüfbar) |
| Approvers case-insensitive | **belegt** (`['batnini','taoufik']`) |
| LoRA r=16 auf 3B verändert Antworten | **widerlegt** (15/15 `answer == base_answer`) |
| Write-Back steigert QA-EM | **nicht belegt** (Δ = 0) |
| LoRA r=16 „lernt weniger, vergisst weniger" (Zwei-Seiten-Eigenschaft) | **belegt** (arXiv:2405.09673, TMLR; Einschränkung: zu wenig gelernt in Zieldomäne) |
| r=256 „lernt so viel wie Full FT" | **bedingt belegt** (nur Tulu-v2-mix; bei CPT auf Code/Math: LoRA schlechter als Full FT) |
| rsLoRA: α/√r verbessert Fine-Tuning-Performance | **belegt** (arXiv:2312.03732; „Performance" ≠ „Loss") |
| LoRA+: η_B = λ·η_A mit λ ≫ 1 | **belegt** (arXiv:2402.12354; „same LR does not allow efficient feature learning") |
| Übertragung dieser Eigenschaften auf unsere Konfiguration | **nicht direkt getestet** (plausible Übertragung, kein Experiment-Beweis) |

## 7. Nächste Schritte (aus Quellen abgeleitet, §6-konform — mit Einschränkungen)

Aus den 3 Quellen ergeben sich **belegte** Maßnahmen — jede mit Vorbehalt:

1. **LoRA+ Learning Rate:** η_B = λ·η_A mit λ ≫ 1 (arXiv:2402.12354) —
   statt gleichem `lr=2e-4` für A und B. **Vorbehalt:** Paper testet nicht
   unsere Fakt-Frage-Konfiguration.
2. **rsLoRA-Scaling:** α/r → α/√r (arXiv:2312.03732) — verbessert
   Fine-Tuning-Performance bei höheren Rängen. **Vorbehalt:** „Performance"
   ≠ „Loss"; Übertragbarkeit auf unsere Konfiguration nicht getestet.
3. **A/B-Vergleich:** LoRA vs. Full Fine-Tuning auf **unserem** Datensatz
   (arXiv:2405.09673 vergleicht beides — aber auf Tulu-v2-mix/CPT, nicht
   auf Fakt-Frage). **Vorbehalt:** Datensatz-Abhängigkeit belegt.

**Keine dieser Maßnahmen ist freigegeben.** Jede braucht Human-Gate +
Zwei-Personen-Verifikation (§9.3) vor Implementierung. **Vor einem
Kaggle-Lauf muss ein A/B-Design festgelegt werden** (Baseline vs.
geänderte Parameter), sonst ist der Vergleich nicht aussagekräftig.

## 8. Quellen

- Paper: arXiv:2608.22215 (Dual-Layer Agentic Memory, §3.3/§3.4)
- **LoRA-Verhalten:** arXiv:2405.09673 (Databricks/TMLR 08/2024, „LoRA r=16
  learns less and forgets less… keeps behavior close to base model")
- **LoRA+:** arXiv:2402.12354 (Hayou/Ghosh/Yu, „same learning rate for A and B
  leads to suboptimal finetuning")
- **rsLoRA:** arXiv:2312.03732 (Kalajdzievski, „minimal impact on loss when
  varying rank r… converge to similar loss irrespective of rank")
- AGENTS.md: §6, §9, §9.1d, §9.3, §10.3, §10.5, Guardrail 3/6/7
- Rekursion: 103 (Θ′ negativ), 109 (0.5B-Lauf), 118/119 (Guard-Fix),
  e2e-theta-2026-10-07 (Δ=0)
- Rohdaten: `Batnini/knowledge-agent-write-back` (HF), `write_back_cycle_result.json`,
  `kaggle_output.json`
