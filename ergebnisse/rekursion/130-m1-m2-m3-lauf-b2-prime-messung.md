# Rekursion 130: M1/M2/M3-Lauf B2′ (Kaggle T4) — Ursache auf Adapter-/Trainingskonfiguration eingegrenzt

> Datum: 2026-10-20 · Phasen: Observe → Compare (echtes externes Signal: Kaggle-T4-GPU + HF-Artefakte)
> Status: **pending** — §9.3-Zwei-Personen-Freigabe **nicht gestartet**; §9-Gate **deny**.
> Quellen (belegt): HF `Batnini/knowledge-agent-write-back`, Pfad `probe/m1_m2_m3_2026-10-20/`
> · `status.json` SHA256 `69c27db37dc6eb2e40c9478bded89f2c9222917190846f412648c7955dd489e8`
> · `manifest.json` SHA256 `8c8697c00c42e2dd9a55a673f8db873df2395d8f3c70343c9d1b09c907aba96c`
> · `per_item.jsonl` SHA256 `95ceabbc835e86f12b4143399ad6d9dc851a42c0775bd7c0e1c7e62bbd7d4f82`
> (lokal gespiegelt unter `/tmp/opencode/probe_2026-10-20/`; dort liegt `SHA256SUMS` mit denselben
> drei Werten — die HF-Seite selbst ist lokal **nicht** prüfbar)
> · `kaggle/m1_m2_m3_probe.py` · `kaggle/m1_m2_m3_preregistration.md`
> · `data/memory/acceptance_gate.py:95-131` · `AGENTS.md` §6, §9 (`:116-124`), §9.1d (`:178-182`),
> §9.3 (`:231`), §10.1 (`:250`), §10.3 (`:271-276`), §10.7 (`:316`) · Rek 129 (`129:§2`, `129:§5`,
> `129:§7.1-7.3`), Rek 128 (`128:§1`, `128:§2`, `128:§5`).
> Kein git (Guardrail 6, `AGENTS.md:103`), kein `self_update` (Guardrail 1, `:97`), keine
> Fake-Messung (Guardrail 7, `:105-107`), nur `.venv` (Guardrail 8, `:108-109`), kein Code-Fix,
> kein Proposal (Proposal-Entwurf erst nach Go, §9.1d `:178-182`).

## 1. Auftrag & Setup

Diagnose der B2′-Annahmen A1–A4 aus Rek 129: **M1** (saubere Base vor dem Adapter-Wrap) auf den
15 write-new-Fakten, **M2** (B2′ = rsLoRA), **M3** (B2 = non-rsLoRA) — jeweils 3B, 15 Probes.

| Pin | Wert (Rohtext `manifest.json`) |
|---|---|
| Basis | `Qwen/Qwen2.5-3B-Instruct`, aufgelöster Commit `aa8e72537993ba99e69dfaafa59ed015b17504d1` (`resolved_commits.base_commit`, Quelle `config._commit_hash`) |
| Datensatz | `probe15_questions.jsonl`, SHA256 `c0ea0219c6a56b50601f85f211b14b5902d8103a73ecf37059560fe5d74b4328`, 15 Zeilen (`dataset`, `dataset_sha256`, `n_probes`) |
| B2′-Adapter | SHA256 `a595d437f4fcb0c6030840d9e70e7ff6818a5e490943aabe19f00c3dee6ba9c5`, `use_rslora=true`, r=64, α=256 |
| B2-Adapter | SHA256 `e3be2c8518433696a6aa5b088a43823facc099b20c7beab385e9352ec3023f2e`, `use_rslora=false`, r=64, α=256 |
| Umgebung | torch `2.11.0+cu128`, transformers `5.16.1`, peft `0.20.0`, torchao `0.18.0`, python `3.13.15`, Tesla T4 (sm_75), fp16 (`env`) |
| Decoding | `max_new_tokens=16`, `do_sample=false`, seed 42, `reseeded_before_each_pass=true` (`decoding`) |

## 2. Rohbelege — 8 Pässe (`manifest.json` → `counts`, `measurement_passes`)

| Pass | Instanz | strict | substring | gold_in_raw | Zählerbasis |
|---|---|---|---|---|---|
| `M1_base` | base#1 | **0/15** | 0/15 | 0/15 | `manifest.json:counts.M1_base` |
| `M1_repeat` | base#1 | **0/15** | 0/15 | 0/15 | `counts.M1_repeat` |
| `M1b_base` | base#2 | **0/15** | 0/15 | 0/15 | `counts.M1b_base` |
| `M2_b2prime` | base#2 | **1/15** | 1/15 | 1/15 | `counts.M2_b2prime` |
| `canary_disable_adapter` | base#2 | **0/15** | 0/15 | 0/15 | `counts.canary_disable_adapter` |
| `M2_repeat` | base#2 | **1/15** | 1/15 | 1/15 | `counts.M2_repeat` |
| `M1c_base` | base#3 | **0/15** | 0/15 | 0/15 | `counts.M1c_base` |
| `M3_b2` | base#3 | **15/15** | 15/15 | 15/15 | `counts.M3_b2` |

Vorbedingungen (alle bestanden, `precondition_failed: null`):

| Witness | Wert | Beleg |
|---|---|---|
| Determinismus (M1 ↔ M1_repeat, gleiche Instanz) | 15/15, `status=pass` | `determinism_baseline` |
| Cross-Instance-Noise (M1 ↔ M1b) | 15/15, `within_budget=true` | `cross_instance_noise` |
| Canary `disable_adapter()` (M1b ↔ canary, **dieselbe** Instanz) | **15/15**, `status=pass` | `canary` |
| Positivkontrolle M2 ↔ canary | **15/15 Items verschieden**, `status=pass` | `positive_control.w1_generation` |
| Logit-Witness pre-/post-wrap | `max_abs_logit_delta = 25.0888671875`, `argmax_changed=true` | `positive_control.w2_logit` |
| Adapter-Pfad-Determinismus (M2 ↔ M2_repeat) | 15/15 | `positive_control.w4_adapter_path_determinism` |

Formatkontrolle (`format_control.per_pass`): M2 **`collapse=true`**, `top_answer="Jamaica"`,
`top_count=13` (≥ Schwelle 12 ⇒ Degenerationsflag); M1/M1b/M1c `collapse=false`
(`top_count=1`, d. h. **15 verschiedene** Antworten — keine Basis-Degeneration); M3
`collapse=false` (15 verschiedene Gold-Antworten).
Rohtext B2′: `per_item.jsonl:46-60` = 15 M2-Items: 13× `"Jamaica"` (`:46-51`, `:53-59`),
`:52` = `"KFC Airways"`, `:60` = `"2005"`.

Regel 6 (P-2b, `regel6_reference`): Referenz `write_back_cycle_result.json` SHA256
`5a9ed27a19a1881a8d06eab1e150df3eb476baa4979d4da0422acc9b62501304` (SHA256 der Datei,
**kein** Git-Commit) → `items_identical_to_altlauf=14`, `items_differing=1` (Item
„What was the name of the city or state where KOAN Sound was formed?": alt „Jamaica" → neu
„KFC Airways"). ±1 Item ist allein kein Beleg; der Altlauf pinnte **keine** Base-Revision
⇒ eine Abweichung kann ein Pinning-Artefakt sein (`regel6_reference.interpretation`).

Basis-Verhalten (Rohtext `per_item.jsonl:1-15`): die **saubere** 3B-Base beantwortet die
15 write-new-Fakten **nicht** (0/15) — 12 Verweigerungen/„keine Information"
(`:1`, `:3`, `:4`, `:5`, `:6`, `:8`, `:9`, `:10`, `:12`, `:13`, `:14`, `:15`) und
3 Fehlantworten **ohne** Verweigerung (`:2` „The Jyllands-Posten Muhammad cartoons
controversy started in September 20…", `:7` „KOAN Sound was formed in San Francisco,
California.", `:11` „UTair Aviation operates flights from several airports across Russia…").
Sie **degeneriert nicht** (15 verschiedene Antworten, `top_count=1`).

## 3. Unabhängige Nachrechnung (read-only, `.venv`, Repo-Grader)

Mit dem Repo-Grader `data/memory/acceptance_gate.py:114-131` (`grade(..., mode="strict"/
"substring")`, `_normalize` `:110-111`, `extract_answer` `:98-107`) über
`/tmp/opencode/probe_2026-10-20/per_item.jsonl` (120 Zeilen = 8 Pässe × 15 Items) neu
berechnet: **alle 8 Pässe identisch zum Manifest** (strict/substring/gold_in_raw_output je
Pass, z. B. `M2_b2prime` 1/1/1, `M3_b2` 15/15/15, `M1_base` 0/0/0). Regel-6-Vergleich
(M2 ↔ Altlauf) reproduziert: 14 identisch, 1 abweichend. Das Skript nutzte seinen eigenen,
**funktional identischen** Grader (`kaggle/m1_m2_m3_probe.py:43-66` ↔ `acceptance_gate.py:95-131`);
die in §4 M1 genannte unabhängige Crosscheck-Bestätigung fehlte im Lauf und ist hier
nachgeholt.

**Korrektur zur Auftragsbeschreibung (Wortlaut, kein Messwert):** Die Basisantworten sind
**nicht** „13× ‚I'm sorry…'“ — 13× „Jamaica" ist der **B2′-Adapter** (`per_item.jsonl:46-59`,
`format_control.per_pass.M2_b2prime.top_count=13`); die Basis liefert 15 **verschiedene**
Antworten (`top_count=1`). `format_control.per_pass.M2_b2prime.top_answer` ist im Manifest
`"Jamaica"` — die Basis-Top-Antwort lautet `"I'm sorry, but there seems to be an error in your
question. The"` (1×). Beide Rohwerte unverändert übernommen.

## 4. Mängel des Laufs (ehrlich, §6)

- **M1 — Grader-Crosscheck lief nicht.** `manifest.json:grader_crosscheck` =
  `"crosscheck skipped: FileNotFoundError: [Errno 2] No such file or directory:
  '/kaggle/working/knowledge-agent/data/memory/acceptance_gate.py'"`. Der fehlende Pfad ist
  **belegt**; die **Ursache ist unbestimmt** — die Repo-Doku nennt `--repo-root
  /kaggle/working/knowledge-agent` (`kaggle/README.md:297`) und „Das Repo wird geklont
  (`git clone` ⇒ `knowledge-agent/`)" (`:303`); der im Kaggle-Working-Dir tatsächlich
  vorhandene Klonname ist durch die Artefakte **nicht** belegt. *Folge:* der Lauf nutzte den
  Skript-eigenen Grader; die unabhängige Crosscheck-Bestätigung fehlte im Lauf — in §3
  nachgeholt (read-only, Repo-Grader).
- **M2 — `tokenizer_commit` unresolved.** `manifest.json:resolved_commits.tokenizer_commit=null`,
  `tokenizer_commit_source="unresolved"` ⇒ die Tokenizer-Revision ist nicht attestiert;
  abgesichert nur über `fingerprints.tokenizer_chat_template_sha256=cd8e9439…` (Chat-Template
  gehasht) und die angeforderte Revision `aa8e725…` (Basis-Commit). *Folge:* gering, aber
  nicht behoben.
- **M3 — Skript-Bug im Struktur-Witness (belegt, kein Adapter-Befund).**
  `kaggle/m1_m2_m3_probe.py:422` prüft `name.endswith("lora_A")`; PEFT registriert die Adapter
  unter dem Schlüssel des Adapter-Namens in einem `nn.ModuleDict`
  (`peft/tuners/lora/layer.py:134` `self.lora_A = nn.ModuleDict({})`, `:263`
  `self.lora_A[adapter_name] = …`) ⇒ der Modulpfad lautet `…lora_A.<adapter_name>`
  (`peft/utils/other.py:1096` nennt das Muster wörtlich „foo.bar.lora_A.default") ⇒
  `endswith("lora_A")` greift **nie**, also sind `lora_modules_total=0` und `lora_B_nonzero=0`
  **konsequenzbedingt** und tragen **keine** Aussage über den Adapter
  (`manifest.json:positive_control.w3_structural`). Der Adapter-Befund stützt sich stattdessen
  auf W1 (15/15 verschieden) + W2 (Logit-Delta 25,088867) + die Adapter-Gewichte selbst.
  *Caveat:* das Namensschema ist in der lokalen peft-Quellkopie **0.21.2** verifiziert, der Lauf
  nutzte peft **0.20.0** (dort nicht lokal verfügbar); der Nullbefund im Manifest stützt sich
  zusätzlich auf die Skriptlogik.
- **M4 — Regel 9 (Degeneration) war nicht implementiert ⇒ die Maschinenentscheidung ist nicht
  regelkonform.** `kaggle/m1_m2_m3_preregistration.md:99` (= `129:§7.2`) legt Regel 9 fest:
  „Degeneration in M1/M1b/M2/M3 (identische Antwort bei ≥ 12/15) ⇒ `unentschieden` — Vorbedingung,
  kein P-1/P-2/P-3-Zweig". Das Skript prüft im Vorbedingungsblock **nur** die Basis
  (`kaggle/m1_m2_m3_probe.py:575-576`: `coll["M1_base"]["collapse"] or coll["M1b_base"]["collapse"]`).
  M2 hat aber 13 identische Antworten (≥ 12) ⇒ **Regel 9 hätte greifen müssen**; stattdessen
  meldeten `status.json`/`manifest.json:decision` „Regel 3 / P-3". *Folge:* die automatisierte
  Diagnose ist zurückzunehmen; die regelkonforme Konsequenz ist `unentschieden`.
- **M5 (Doku, offen) —** `kaggle/m1_m2_m3_preregistration.md:3` behauptet „Ort: `/tmp/opencode/`
  (Arbeitsstand, **kein Repo-File**)" und `:6-7` „Rek 129 enthält aktuell 4 Annahmen, keine 9
  Regeln" — beides ist seit dem Übernehmen der Regeln (`129:§7.2`) veraltet.

## 5. Interpretation — Ursache eingegrenzt, P-1 nicht bewiesen

**Was der Lauf entschieden hat:** `status.json` und `manifest.json:decision` melden `rule 3`,
`"P-3 Base/Prompt/Daten (Kandidat)"`, Text `"M1b=0/15, M2=1/15, M3=15/15"` — nach
`kaggle/m1_m2_m3_preregistration.md:93` (Regel 3: „M1b schlecht, M2 und M3 ≥ M1b ⇒ P-3
Base/Prompt/Daten als Hauptkandidat (nur nach Formatkontrolle)"). **Diese Entscheidung wird
zurückgenommen**: (i) Regel 9 hätte greifen müssen (M4), (ii) Regel 3 ist für write-new-Fakten
**nicht informativ** (Erratum E1, s. u.).

**Erratum E1 — Regel 3 ist für write-new-Fakten nicht anwendbar (nachrangig zu M4).**
Die 15 Items sind **write-new** (alle `class=write-new`, `129:§5:106`; Basis 0/15,
`per_item.jsonl:1-15`). Der Auslöser von Regel 3 („M1b schlecht") ist für write-new-Fakten
**trivial erfüllt**: die Basis kennt den Fakt nicht — das ist der Sollzustand des
Write-Back-Pfads (§10.1 `:250` write-new/write-update/non-write; §10.7 `:316`; §10.3 `:271-276`
konsumiert diese Klassen). Ein Basisscore 0/15 ist hier **kein** Pathologiesignal. (Die Basis
verweigert 12/15 und antwortet 3/15 falsch — Zeilen 2, 7, 11 —; nach §10.1/§10.7 wären diese
drei „write-update", die Datensatz-Klasse bleibt `write-new`.) ⇒ Regel 3 trägt hier **keine**
Diagnose; die Entscheidung „P-3" des Laufs ist zurückzunehmen.

**Der tragfähige Diskriminator ist M3 vs. M2 innerhalb derselben Messung:** gleiche Basis,
gleicher Datensatz (SHA `18caaae7…`, `129:§7:148-149`), gleiche 15 Items, gleiches Decoding —
nur der Adapter unterscheidet sich ⇒ **M3 = 15/15** (non-rsLoRA, `per_item.jsonl:106-120`,
exakte Gold-Strings) vs. **M2 = 1/15 mit Degeneration** (rsLoRA, `per_item.jsonl:46-60`).
Eine Base-/Prompt-/Daten-Pathologie kann diesen **Unterschied zwischen den Armen nicht erklären**
(die Basis ist in beiden Armen identisch; der Canary 15/15 isoliert den Adapter-Pfad). P-3 ist
damit als **Erklärung des Arm-Unterschieds** ausgeschlossen; P-3 bleibt als Aussage über die
absolute Stärke der Basis (0/15) bestehen.

**Zwei Grenzen des Befunds (aus `manifest.json:grenzen`, nicht verschwiegen):**
(i) die 15 Probe-Zeilen **sind die Trainingszeilen** (Dataset `18caaae7…`) ⇒ M2/M3 messen
**Memorization**, keine Generalisierung; (ii) „M3 hat ein Ceiling … ⇒ M3 kann P-1 vs. P-3
nicht trennen; diskriminativ wäre ein Held-out-Probe-Set". Der Befund trennt also
**adapter-verursachten Kollaps** von **Basis-Pathologie** — nicht „welche Adapter-Eigenschaft".

**Konfigurations-Diff der beiden Läufe (`manifest.json:b2prime_cfg` / `b2_cfg`):** einziger
inhaltlicher Unterschied `use_rslora true` vs. `false` (⇒ Skalierung α/√r = 256/8 = **32** vs.
α/r = 256/64 = **4**); die Reihenfolge im `target_modules`-Array unterscheidet sich
(`up_proj, gate_proj, o_proj, v_proj, down_proj, q_proj, k_proj` vs.
`o_proj, up_proj, k_proj, gate_proj, down_proj, v_proj, q_proj`), die **Menge** ist identisch;
sonst gleich (r=64, α=256, `lora_dropout=0.05`, lr 2e-4, 15 Epochen, Seed 42, Basis,
Dataset-Hash `18caaae7…` — B2′ `kaggle_output.json:4` Basis, `:12` Dataset-Hash, `:19-21`
Zeilen/Seed/Epochs, `:23-26` lr/r/α/rsLoRA, `:29` dtype). Loss: B2′ **5,190721893310547**
(`wb_b2prime/kaggle_output.json:7`) vs. B2 **1,310697078704834** (`wb_b2/kaggle_output.json:7`;
Rek 128 §2 nennt gerundet 1,3107).

**Ursache:** **Adapter-/Trainingskonfiguration.** P-1 (rsLoRA-Überskalierung) ist
**deskriptiv gestützt, aber NICHT bewiesen**: (a) `max|ΔW|` 0,7430766820907593 vs.
0,15320010483264923 = 4,85036666849851 = 8 × 0,606295833562 (Rek 129 `A1`; `129:§4:65-87`),
(b) Loss 5,19 vs. 1,31, (c) Degeneration 13× identische Antwort, (d) M3 15/15 im selben
**Mess-Setup** (Basis/Daten/Decoding identisch — das B2-**Training** lief auf einem älteren
Code-Stand). **Nicht bewiesen, weil** der B2-Arm auf einem **älteren Code-Stand** lief
(`lora_use_rslora` fehlt, Rek 128 §1/§5 ⇒ keine identische Codebasis) und die alternative
Erklärung „zu hohe Lernrate (lr 2e-4)" den Loss 5,19 ebenfalls erklären könnte — das ist eine
**Hypothese, nicht gemessen** (kein lr-Sweep in den Artefakten). ⇒ **Der kontrollierte
A/B-Lauf (gleicher Code, nur `LORA_USE_RSLORA` 0 vs. 1) fehlt.**

## 6. Entscheidung, Gate, Governance

```text
Ursache (formal, nach den 9 prä-registrierten Regeln) = unentschieden
  → Regel 9 hätte gegriffen (M2-Degeneration 13 ≥ 12; M4); Maschinenentscheidung
    „Regel 3 / P-3" zurückgenommen; Regel 3 zusätzlich per Erratum E1 nicht anwendbar
Ursache (Interpretation, §5) = Adapter-/Trainingskonfiguration;
  P-1 deskriptiv gestützt, NICHT bewiesen (kontrollierter A/B fehlt)
Gate = deny
§9.3 = nicht gestartet (pending → first_approved → second_approved → approved fehlt)
self_update = keiner · Git = gesperrt · Code-Fix = keiner
```

Gate-Rechnung: B2′ `1/15 = 6,7 % < 70 %` ⇒ **deny** (`AGENTS.md:120`); unverändert gegenüber
Rek 129 (`129:§7`).

## 7. Nächster zulässiger Schritt

**§9.1d-Proposal** nach `ergebnisse/proposal-template.md` mit **Score-Änderung, Diff und Drift**
(`AGENTS.md:178-182`) — **erst nach deinem Go**; Inhalt (Entwurf, nicht beantragt):
kontrollierter Trainings-A/B (gleicher Code, identische Daten/lr/Epochs/Seed, **nur**
`LORA_USE_RSLORA` 0 vs. 1 ⇒ α/r = 4 vs. α/√r = 32), optional zusätzlich lr-Sweep
(2e-4 vs. 2e-5 — Hypothese aus §5, bisher nicht gemessen); **Erfolgskriterium**:
adapter-seitiger strict-Score ≥ 11/15 **und** keine Degeneration (≥ 12/15 identische
Antworten); **Verifikation**: Write-Back-Messung mit Base **vor** dem Wrap (N8-Fix,
`kaggle/e2e_theta_probe.py:122-123`) plus Canary `disable_adapter()` 15/15.
Danach §9.3 (`AGENTS.md:231`, Batnini + Taoufik) → erst dann Code-Fix.

> **Stand 2026-10-21:** Proposal **P-131** angelegt und **freigegeben**:
> `ergebnisse/proposals/P-131-kontrollierter-rslora-ab.md` — §9.3 **approved** (first_approved:
> Batnini, second_approved: Taoufik, 2026-10-21; `AGENTS.md:231`); Gate für Lernen/`self_update`
> bleibt `deny` (6,7 %); Drift Code/Doku 5,63 % ≪ 10 %-Bound; **Amendment A2** der Regeltabelle
> bleibt beantragt. Die drei Mess-Mängel aus §8 sind behoben und gepusht (`41348ec`), CI grün
> (`e3b95cf`). **Auflagen vor dem Lauf** (P-131 §8): Datensatz-Identität (SHA `18caaae7…` bzw.
> kanonischer Digest `e481dd2f…`), Umgebung = Baseline (`trl==1.16.0` fehlte im Kaggle-Image),
> Klon-Update (`git pull`) — der erste Startversuch am 2026-10-21 trainierte **nicht**
> (fehlendes `trl`, falscher Datensatz-Hash `de24a667…`, veralteter Klon) ⇒ kein Artefakt,
> kein Schaden, kein `self_update`.

## 8. Self-Feedback t+1

- Drei Skript-/Doku-Mängel sind zusammen zu beheben (nach Go, zusammen mit `ruff`,
  `check_md_links`, `check_artifacts`, `check_secrets`, `ci_drift` und `tests/test_agents_law.py`):
  (1) Regel 9 unvollständig implementiert (`kaggle/m1_m2_m3_probe.py:575-576` prüft nur
  M1/M1b ⇒ M2/M3-Degeneration unentdeckt); (2) Struktur-Witness-Prädikat
  (`kaggle/m1_m2_m3_probe.py:422` `endswith("lora_A")` → adapter-name-agnostisch, z. B.
  `"lora_A" in name.split(".")`); (3) `--repo-root`-Pfad im Repo-README (`kaggle/README.md:297,303`)
  und die veralteten Kopfzeilen der Prereg-Kopie (`:3`, `:6-7`).
- Preregistrierte Regeln müssen **aufgabenspezifisch** formuliert werden: „M1 schlecht ⇒ Base
  defekt" ist für write-new-Fakten nicht informativ und gehört vor dem nächsten Lauf korrigiert
  (Amendment A2), sonst erzeugt jeder write-back-Lauf denselben Fehlschluss.
- `tokenizer_commit` sollte nicht `unresolved` bleiben (Tokenizersnapshot + `revision`
  mitgeben), damit Commit-Pins vollständig attestiert sind.

> **Stand 2026-10-20 (nach Go des Nutzers):** (1) Regel-9-Prüfung um **M2/M3** ergänzt
> (`kaggle/m1_m2_m3_probe.py:575-580` und die Regel-9-Meldungen) — die Maschinenentscheidung
> des Baseline-Laufs wäre damit regelkonform „unentschieden" gewesen; (2) Witness zählt jetzt den
> **LoraLayer** (trägt `lora_A` **und** `lora_B`) statt des Namensprädikats — adapter-name-agnostisch
> und korrekt für `…lora_A.<adapter_name>` (`peft/tuners/lora/layer.py:134`, `:263`);
> (3) `kaggle/README.md` nennt den Klonnamen korrekt (`Ata3lm` = Repo-Name) und warnt vor
> `--repo-root` auf dem falschen Pfad (`grader_crosscheck: skipped`), Prereg-Kopfzeilen sind
> aktualisiert (Repo-Stand, Regelübernahme in Rek 129 §7.2, Amendment A2 **nicht** freigegeben).
> Alle drei Änderungen sind **Messintegrität**, kein Eingriff in `write_back_cycle.py`;
> Commit-Freigabe steht aus.
