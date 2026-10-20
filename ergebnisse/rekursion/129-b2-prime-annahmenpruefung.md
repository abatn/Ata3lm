# Rekursion 129: B2′-Annahmenprüfung A1–A4 (Multi-Agent, read-only)

> Datum: 2026-10-20
> Phasen: Observe → Compare (kein Revise)
> Status: **pending** — M1 (saubere Base VOR Adapter, 15 Fakten, Kaggle-GPU) fehlt;
> §9-Gate `deny`.
> Quellen (belegt): `AGENTS.md` §6/§9/§9.1d/§9.3; `kaggle/write_back_cycle.py`;
> `kaggle/e2e_theta_probe.py`; `data/memory/slow_consolidation.py`;
> HF-Adapter `Batnini/knowledge-agent-write-back`;
> rsLoRA (α/√r): https://arxiv.org/abs/2312.03732 · SAGE: https://arxiv.org/abs/2609.36043
> PEFT-Doku: https://huggingface.co/docs/peft
> Kein git (Guardrail 6, `AGENTS.md:103`), kein Code-Fix, keine Fake-Antworten
> (Guardrail 7, `AGENTS.md:105-107`), nur `.venv` (Guardrail 8, `AGENTS.md:108-109`).

## 1. Auftrag

Prüfe A1–A4 gegen Gesetz und Rohtext; bestimme **genau eine** Ursache oder
`unentschieden`. M1 = Base **vor** `PeftModel.from_pretrained` auf den 15 Fakten
(Kaggle-GPU), M4 aus HF-Gewichten, M5 aus B2′-Rohdaten rekonstruieren.

## 2. Annahmen

| Annahme | Behauptung | Status | Beleg |
|---|---|---|---|
| **A1** | rsLoRA-Überskalierung ist Hauptkandidat P-1: α/√r=32, `max\|ΔW\|` 0,7431 vs. 0,1532 | **belegt (Messwerte)**; kausale Rangfolge **unentschieden** | B2′-Config `use_rslora=true,r=64,α=256`; B2 `use_rslora=false`; nachgerechnet: 32 vs. 4, `max\|ΔW\|` 0,7430766820907593 vs. 0,15320010483264923 (Differenz der Maxima 0,58987657725811005), 252 Paare, 0 nonfinite, 0 Nullpaare; elementweise Nullen im B@A-Produkt **211.071 (B2′) / 31.631.447 (B2)** — **identisch für ΔW** (scaling 32/4 endlich ≠ 0 ⇒ skaleninvariant); `lora_B`-Faktor-Nullen 6.706 (B2′, 103 Nullzeilen) / 988.485 (B2, 15.445 Nullzeilen); Verhältnis der globalen `max\|ΔW\|` 4,85036666849851 = 8 × 0,606295833562 (Rohmax) ⇒ **nur „konsistent mit P-1"**, nicht bewiesen |
| **A2** | N8-Kontamination (`_ThetaProbe:420` Wrap vor `:442` Base-Messung) invalidiert `base_answer`/`em_base`/`changed`/Δ und „Basis kennt alle 15" — **nicht** den adapter-seitigen Score `1/15` | **belegt (Kontamination)**; der adapter-seitige `1/15` bleibt ein gültiger Score, ist aber **kein Lernbeleg** (14/15 degeneriert: „Jamaica") | `kaggle/write_back_cycle.py:420` `PeftModel.from_pretrained(base)`, `:421` `self._base=base`, `:442` `base_answer=self._answer(self._base,...)`, `:443` `adapter_answer`, `:445` `passed=_grade(adapter_answer,gold)`; Code-Beleg des In-place-Wraps: `:420-421`/`:442-443`; `tests/test_e2e_theta_probe.py:8-10` belegt die PEFT-Doku (nicht empirisch), `:59-64` testet nur `e2e_theta_probe.py`, nicht `_ThetaProbe`; Rohdaten `wb_b2prime/write_back_cycle_result.json:421-526` (14× `answer==base_answer=="Jamaica"`, `:520-526` Comdial `2005`); Rek 128:56,58,75,102 und Rek 125:88-89,107 sind dadurch widerlegt |
| **A3** | saubere Base könnte „krank“ sein (P-3) | **unentschieden** | Kein M1 auf 15 Fakten/3B. Dokumentierte 0.5B/200-Läufe: `em_base=3/200` (`kaggle/e2e_theta_result.json:3-10`, post-N8, **Substring-Ära** — strict Grader erst Rek 115:15) und F6 `em_base=8/200` (Rek 103:24-26, ebenfalls Substring-Ära, `:50`); die 15-Fakt-`base_answer`-Werte sind kontaminiert. **Provenienzlücke Rek 077:** Probe-Quelle, Metrik und Adapter-Identität des post-N8-Laufs sind undokumentiert (`077:69-72` zitiert `933ee6f3` nur als *Ergebnisdatei*-Commit; Adapter-Commit nirgends; `103:41-43` nennt Adapter `53f3a25`, Ergebnis `ec08d221`) ⇒ 077 ↔ 103 ist dreifach konfundiert (Adapter-Commit, Trainingskorpus, Eval-Slice), kein „gleicher Adapter" |
| **A4** | Provenienzlücke: Result-JSON `use_rslora:false` vs. `kaggle_output:true` | **belegt**; Lücke ist **semantisch** (Args-Defaults statt effektiver Config) — nicht „größer als behauptet", aber gravierend | `/tmp/opencode/wb_b2prime/write_back_cycle_result.json:16-21`: `lora_r=null`, `lora_alpha=null`, `learning_rate=null`, `use_rslora=false`, `lora_plus_ratio=null`; `/tmp/opencode/wb_b2prime/kaggle_output.json:23-26`: `learning_rate=0.0002`, `lora_r=64`, `lora_alpha=256`, `lora_use_rslora=true`; `adapter_adapter_config.json:19,30,48`: `lora_alpha=256`, `r=64`, `use_rslora=true`; Mechanik: `write_back_cycle.py:735-740` schreibt `args.*` (argparse-Defaults `:519-522` = `--use-rslora` store_true ⇒ False; `:507-530` übrige Defaults None/None/None/False/None), effektive Config aus ENV/Trainer (`write_back_cycle.py:318,322-333`; `train_slow_consolidation.py:57-65`, `:528-536`) |

### A1/Code-Beleg

- `kaggle/write_back_cycle.py:735-740` schreibt nur `args` ins Result-JSON (argparse-Defaults
  `:507-530`, `:519-522`); die effektiven ENV-Defaults des Trainers stehen in
  `kaggle/train_slow_consolidation.py:57-65` (dort `:432-438` = LoraConfig-Konstruktion,
  **nicht** die Defaults); die effektive Config protokolliert `kaggle_output.json`
  (`train_slow_consolidation.py:528-536`).
- rsLoRA-Skalierung: α/√r = 256/8 = **32**; B2: α/r = 256/64 = **4**.
- B2′-Rohmaximum ist **0,606295833562×** B2 (0,02322114632 vs. 0,03830002621); der höhere
  effektive Wert kommt aus der 8×-Skalierung, nicht aus größeren Rohgewichten.
  Das stützt P-1 als Hypothese, beweist aber keine Ursache.
- **Nullmuster-Invarianz (belegt):** `ΔW = scaling · (B @ A)`; da `scaling` (32 / 4) endlich
  und ≠ 0 ist, ist das Nullmuster von `B@A` und `ΔW` **identisch** (211.071 / 31.631.447).
  Die Zahlen 6.706 / 988.485 sind Nullen in den **lora_B-Faktor**tensoren
  (103 / 15.445 vollständig-Nullzeilen) — ein anderes Objekt, kein Gegenwert zu 211.071.

## 3. M1/M2

- **M1: nicht ausgeführt.** Kein `nvidia-smi`, kein `/dev/nvidia*`; `.venv` ohne
  `torch`/`transformers`/`peft`/`trl`/`bitsandbytes`. `e2e_theta_probe.py:69`
  verlangt GPU; `write_back_cycle.py:408` bricht ohne GPU ab. Kein Fake.
- **M2: nicht ausgeführt.** M2 ist im Repo nicht als eigener Messpunkt definiert;
  der vorhandene `_ThetaProbe`-Pfad misst faktisch M2 statt M1.
- **Dokumentierte Base-Läufe (keiner ersetzt M1):** 0.5B/200 ZsRE `em_base=3/200`
  (`kaggle/e2e_theta_result.json:3-10`, post-N8, **Substring-Ära**) und 0.5B/200 F6
  `em_base=8/200` (Rek 103:24-26, **Substring-Ära**, `:50`). **Kein** 15-Fakten/3B-Base-Lauf.

## 4. M4 (HF-Gewichte, nachgerechnet)

Quellen:
`/tmp/opencode/hf_b2prime/adapter/adapter_model.safetensors`
(SHA256 `a595d437f4fcb0c6030840d9e70e7ff6818a5e490943aabe19f00c3dee6ba9c5`) und
`/tmp/opencode/hf_b2/adapter/adapter_model.safetensors`
(SHA256 `e3be2c8518433696a6aa5b088a43823facc099b20c7beab385e9352ec3023f2e`).

```text
B2′: r=64, α=256, use_rslora=true, scaling=32
     252 Paare, 0 nonfinite, 0 Nullpaare
     B@A-Nullen elementweise 211.071  (== ΔW-Nullen, skalierungsinvariant)
     lora_B-Faktor-Nullen 6.706 (103 vollständige Nullzeilen)
     global max|ΔW| = 0.7430766820907593
     top: layers.1.mlp.gate_proj=0.74307668
          layers.1.mlp.up_proj=0.33065313
          layers.7.mlp.up_proj=0.23075072
          layers.5.mlp.gate_proj=0.15792614
          layers.7.mlp.gate_proj=0.12899424

B2:  r=64, α=256, use_rslora=false, scaling=4
     252 Paare, 0 nonfinite, 0 Nullpaare
     B@A-Nullen elementweise 31.631.447  (== ΔW-Nullen, skalierungsinvariant)
     lora_B-Faktor-Nullen 988.485 (15.445 vollständige Nullzeilen)
     global max|ΔW| = 0.15320010483264923
     top: layers.1.mlp.gate_proj=0.15320010
          layers.1.mlp.up_proj=0.07497478
          layers.6.mlp.up_proj=0.03462479
          layers.5.mlp.up_proj=0.02910355
          layers.5.mlp.gate_proj=0.02812499
```

Berechnung: BF16 lossless nach float32 dekodiert, `ΔW = scaling · (B @ A)`,
Maximum über alle 252 A/B-Paare. Keine System-Python-Ersatzrechnung.
Verifikation (read-only, `.venv`): `/tmp/opencode/verify_a1_a4_claims.py`,
`/tmp/opencode/verify_b2_prime_assumptions.py`.

## 5. M5 (Rekonstruktion)

```text
Datei: /tmp/opencode/consolidation_sft.jsonl
Zeilen: 15
Bytes: 5655
SHA256: 18caaae7c6f7f506a0cdd132d15f23c0e7044b07d894b73eb68b302605b01c7c
Row-Aggregat: 8d42c0dab6e5face548ef0df46c1b2b64fb809f05ea395db72d4e6bf4d108ef4
Rekonstruktion byte-identisch: True
```

Methode: `probe_results[i].question` → User, `.gold` → Assistant;
`pending_keys[i]` → `key`; `class` = `write-new` (alle 15; `writes.write-new` = 15);
`sha256=sha256(gold)`; kanonisches `messages`-JSON mit
`sort_keys=True,separators=(",",":")`, `ensure_ascii=False`; Record-Reihenfolge
`messages,hash,key,class,sha256`; Join `"\n"` + finales `"\n"`
(`data/memory/slow_consolidation.py:277-286`).

## 6. Befund

- **A2 ist die belegte Ursache der Fehlbeobachtung, nicht die Ursache des `1/15`:**
  `base_answer` und `adapter_answer` kommen aus demselben in-place gewrappten Modul;
  `answer == base_answer` ist strukturell erzwungen und **kein** Beweis für Nullwirkung.
  Der adapter-seitige Score `1/15` (`:445`) bleibt gültig, ist aber **kein Lernbeleg**
  (14/15 degeneriert: „Jamaica"; der einzige Treffer Comdial `2005` ist base-kontaminiert).
- **A1 ist numerisch belegt, aber nicht kausal:** Die 8×-Skalierung und der
  höhere effektive `max|ΔW|` sind real; das Verhältnis 4,85036666849851 = 8 × 0,606295833562
  ist vollständig durch die Skalierung erklärt (Rohmax von B2′ ist **kleiner**);
  ob die Skalierung die B2′-Ausgabe pathologisch macht, ist ohne M1 offen.
- **A3 ist nicht belegbar:** Ohne saubere 15-Fakt-Base ist „kranke Base“ weder
  bestätigt noch ausgeschlossen. Zusätzlich ist der post-N8-Lauf in Rek 077 in
  Probe-Quelle, Metrik und Adapter-Identität undokumentiert ⇒ `em_base=3/200` ist
  **kein** Ersatz für M1.
- **A4 ist belegt (semantische Lücke):** Das Result-JSON protokolliert Wrapper-Argumente,
  nicht die effektive Trainingskonfiguration (`write_back_cycle.py:735-740`);
  `lora_r/lora_alpha/learning_rate` sind dort `null`, `use_rslora=false` ist der
  argparse-Default (`--use-rslora` store_true, `:519-522`), nicht der Trainingswert.

## 7. Entscheidung

```text
Ursache = unentschieden
Gate = deny
§9.3 = in dieser Audit-Iteration nicht gestartet
Git = gesperrt
Änderungen = in dieser Audit-Iteration nur dieses Provenienz-Dokument (docs-only)
```

§9.3-Klarstellung: Der ausgewertete B2′-Lauf selbst lief mit `self_update=true` und
`approvers=[batnini, taoufik]` (Rohtext `wb_b2prime/write_back_cycle_result.json:11-15`,
15 write-new + 16 write-update) — das ist die Historie des Laufs, nicht die Freigabe
dieser Audit-Iteration.

Gate-Rechnung: B2′ `passed=1/15 = 6,7 % < 70 %` ⇒ `deny` (`AGENTS.md:120`).
B2 `15/15` ist ein **adapter-seitiger** Score auf den **15 Trainingszeilen** selbst
(Dataset-Hash `18caaae7…` identisch zu den Proben) — also **keine** saubere Base-Baseline
und **kein** Lern-/Generalisierungsbeleg; „Basis kennt alle 15" ist nicht belegt
(`write_back_cycle.py:420-421,442-443`).

### 7.1 Messpunkte M1–M5

| M | Definition | Status |
|---|---|---|
| M1 | frische Base-Instanz, 15 Proben, **vor** jedem `PeftModel`-Wrap (Muster `kaggle/e2e_theta_probe.py:122-123`) | **nicht ausgeführt** (keine GPU) |
| M2 | frische Base-Instanz #2 + B2′ (rsLoRA, `use_rslora=true`, r=64/α=256, Scaling 32) | **nicht ausgeführt** (keine GPU) |
| M3 | frische Base-Instanz #3 + B2 (`use_rslora=false`, r=64/α=256, Scaling 4) — historischer Code-Stand, **Ceiling** (B2 traf die 15 Trainingszeilen exakt) | **nicht ausgeführt** (keine GPU) |
| M4 | Nachrechnung aus den HF-Adaptern (BF16→float32, `ΔW = scaling · (B @ A)`, 252 Paare) | ausgeführt (§4) |
| M5 | Rekonstruktion des SFT-Datensatzes (byte-identisch, SHA `18caaae7…`) | ausgeführt (§5) |

### 7.2 Vorab registrierte Entscheidungsregeln (9)

Quelle: Preregistration (Arbeitsstand, kein Repo-File) `/tmp/opencode/M1_M2_M3_PREREGISTRATION.md`
(Amendment A1: Canary-Referenz = M1b auf derselben Instanz; Positivkontrolle ergänzt;
gepaarte Basisreferenzen M1b/M1c). Schwellen: `gut` ≥ ⌈0,733·n⌉, `schlecht` ≤ ⌊0,267·n⌋,
`besser/schlechter` ≥ ⌈0,2·n⌉, Degeneration ≥ ⌈0,8·n⌉ identische Antworten
(n=15 ⇒ 11/4/3/12; 1 Item = 6,7 pp; **keine** Signifikanz).

| Nr. | Bedingung | Ergebnis |
|---|---|---|
| 1 | M1b gut, M2 schlecht, M3 ≥ M1c − 2/15 | P-1 deskriptiv **konsistent** (nicht bewiesen; M3 = historischer Code-Stand + Ceiling) |
| 2 | M1b gut, M2 schlecht, M3 schlecht | Adapterschaden, **nicht** spezifisch rsLoRA |
| 3 | M1b schlecht, M2/M3 ≥ M1b | P-3 (Base/Prompt/Daten) als Hauptkandidat (nur nach Formatkontrolle) |
| 4 | M1b schlecht, M2/M3 ≤ M1b − 3/15 | Adapterschaden auf schwacher Base (Kandidat) |
| 5 | P-2a | N8 invalidiert `base_answer`, `em_base`, `changed`, Δ — **nicht** den adapter-seitigen Score |
| 6 | P-2b | M2 reproduziert das Altlauf-15-Tupel nicht ⇒ Artefakt-/Eval-Mismatch; ±1 Item ist kein Beleg |
| 7 | M2 ≥ M1b + 3/15 | Adapter hilft deskriptiv; P-1 nicht gestützt; Gate bleibt `deny` bei M2 < 11/15 |
| 8 | M2 ≈ M1b (± ≤ 2/15) **und** Positivkontrolle bestanden | No-op (Sub-Branch: M2 ≡ canary ⇒ Regel 9, außer Logit-Delta > 0 und `lora_B ≠ 0`) |
| 9 | Canary-Fail **oder** Positivkontrolle-Fail **oder** Deterministische-Baseline-Fail **oder** Cross-Instance-Noise > 2/15 **oder** Degeneration (≥ 12/15 identisch) **oder** nicht zuordenbar | `unentschieden` — **Vorbedingung**, kein P-1/P-2/P-3-Zweig |

### 7.3 Querverweis: 10-07 vs. 077 vs. 103 (Metrik-Ären, kein Widerspruch)

- `ergebnisse/e2e-theta-2026-10-07.md:28-32` = **vor** N8: `em_base=22` kontaminiert
  (`em_base == em_adapter == 22/200`, Rek 077:37-39) ⇒ das dortige **Δ = 0 ist als
  Vergleich ungültig** und belegt **keine** Adapter-Nullwirkung.
- `kaggle/e2e_theta_result.json:3-10` / Rek 077:69-72 = **nach** N8: `em_base=3`,
  `em_adapter=22`, Δ = +19 — **Substring-Ära** (strict Grader erst Rek 115:15),
  Probe-Quelle/Metrik/Adapter-Commit **undokumentiert**.
- Rek 103:24-26 = 0.5B/200 **F6**: `em_base=8`, `em_adapter=9`, Δ = +1 — ebenfalls
  Substring-Ära (`:50`), Adapter-Commit `53f3a25` (`:41`).
⇒ 077 ↔ 103 ist **dreifach konfundiert** (Adapter-Commit, Trainingskorpus, Eval-Slice);
  die Werte sind **kein** Widerspruch und **keine** gegenseitige Widerlegung.

## 8. Nächster zulässiger Schritt

**M1/M2/M3-Lauf auf Kaggle (read-only, Ausführung durch den Menschen):**
getrennte Base-Instanz pro Arm, Base **vor** `PeftModel.from_pretrained`
(Muster `kaggle/e2e_theta_probe.py:122-124`), Canary `disable_adapter()` gegen die
**ungewrapte Messung derselben Instanz** (M1b), Positivkontrolle M2 ≠ canary.
`kaggle/write_back_cycle.py` wird **nicht** wiederverwendet (trainiert + schreibt).

Bis dahin: kein Code-Fix, kein Proposal, kein Commit. Ein Proposal erst nach
`ergebnisse/proposal-template.md` mit Score-Änderung/Diff/Drift
(`AGENTS.md:178-182`) und §9.3-Freigabe
(`pending → first_approved → second_approved → approved`, Batnini + Taoufik,
`AGENTS.md:231`).

## 9. Self-Feedback t+1

- `_ThetaProbe` braucht einen Test, der `base` vor dem Wrap kopiert oder eine
  separate Base-Instanz lädt; `tests/test_e2e_theta_probe.py` deckt diesen Pfad
  nicht ab.
- Result-JSON muss die **effektive** Trainingskonfiguration aus
  `kaggle_output.json`/`adapter_config.json` übernehmen, nicht die `args`-Defaults.

## 10. Doc-Korrekturen (docs-only, 2026-10-20)

Freigabestufe: Dokumentation (kein Code, kein git, kein Commit). **Rohwerte unverändert.**

| Datei | Stelle | Korrektur |
|---|---|---|
| `129-b2-prime-annahmenpruefung.md` | `:10` | SAGE/rsLoRA-Mislabel: `2312.03732` = rsLoRA (`126:48`), SAGE = `2609.36043` (`110:23`, `acceptance_gate.py:3`) |
| `129-b2-prime-annahmenpruefung.md` | `:25` | „diff 0.0" → Differenz der Maxima **0,58987657725811005**; „0 zero" → **0 Nullpaare** + elementweise B@A-Nullen 211.071/31.631.447 (skalierungsinvariant) + `lora_B`-Nullen 6.706/988.485 |
| `129-b2-prime-annahmenpruefung.md` | `:26` | A2: N8 invalidiert `base_answer`/`em_base`/`changed`/Δ und „Basis kennt alle 15" — **nicht** den adapter-seitigen `1/15` (`:445`); Code-Beleg statt PEFT-Doku-Zitat |
| `129-b2-prime-annahmenpruefung.md` | `:27` | A3: zwei dokumentierte 0.5B/200-Läufe (ZsRE 3/200, F6 8/200), beide Substring-Ära; **keiner** ersetzt M1; Provenienzlücke Rek 077 (Probe-Quelle/Metrik/Adapter-Commit) |
| `129-b2-prime-annahmenpruefung.md` | `:28` | A4: Lücke ist **semantisch** (Args-Defaults `:735-740`, `:519-522`), nicht „größer als behauptet" |
| `129-b2-prime-annahmenpruefung.md` | `:53-55` | „Der einzige saubere Base-Lauf" → zwei dokumentierte Läufe, kein M1-Ersatz |
| `129-b2-prime-annahmenpruefung.md` | `:65-87` | M4-Blöcke: „0 zero" → „0 Nullpaare" + Nullenzahlen (B@A 211.071/31.631.447; `lora_B` 6.706/988.485) |
| `129-b2-prime-annahmenpruefung.md` | `:114-137` | §6/§7: A2 ≠ Ursache des `1/15`; A4 semantisch; B2 `15/15` = adapter-seitiger Score auf Trainingszeilen (kein Baseline-/Lernbeleg); §9.3/Änderungen auf „diese Audit-Iteration" begrenzt |
| `129-b2-prime-annahmenpruefung.md` | neu §7.1–7.3 | M1–M5-Definitionen, 9 prä-registrierte Regeln, Querverweis 10-07/077/103 |
| `ergebnisse/rekursion/README.md:156` | Indexzeile 129 | Kurzfassung an die korrigierten A1–A4 angepasst |
| `ergebnisse/rekursion/README.md:155` | Indexzeile 128 | „Adapter-Effekt weiterhin 0/15", „Basis kennt ALLE 15 Gold", „ohne Einfluss auf Adapter-Wirkung“ → „nicht entscheidbar“ (In-place-Wrap, Rek 129 §10) |
| `ergebnisse/e2e-theta-2026-10-07.md` | nach `:4` | Superseded-Vermerk: Lauf **vor** N8, `em_base` kontaminiert, Δ=0 als Vergleich ungültig; post-N8 `3`/`22` (Δ=+19), Substring-Ära; Rohzahlen unverändert |
| `071-m1-slow-consolidation.md` | nach `:95` | Superseded-Vermerk: pre-N8-Interpretation; Δ=0 kein Wirkungsbeleg |
| `125-write-back-3b-adapter-wirkungslos.md` | `:18` | „Δ ≈ 0" nicht mehr als Adapter-Nachweis; beide Vorgänger pre-N8/Substring-Ära |
| `128-write-back-b2-r64-flushed15-adapter0.md` | `:1`, `:56`, `:75`, `:102` | `em_base` = JSON-Feld `base_answer` (adapter-seitig gemessen); „Basis kennt alle 15" **nicht** belegt; Titel: B2 lief **ohne** rsLoRA |
| `127-write-back-lora-cli-args.md` | `:131` | Überschrift „B2 (rsLoRA)" → „B2′ (rsLoRA)" + Korrektur-Nachtrag; der rsLoRA-Lauf ist **B2′**, der spätere Lauf „B2" lief mit altem Code ohne `use_rslora` (Rek 128:34) |
| `kaggle/m1_m2_m3_probe.py` + `kaggle/m1_m2_m3_preregistration.md` | neu | Read-only-Messskript (M1/M1b/M1c/M2/M3 + Canary + Positivkontrolle, **kein** Training/Write-Back) und prä-registrierte Regeln (Amendment A1) aus `/tmp` ins Repo übernommen, damit der Kaggle-Lauf per `git clone` reproduzierbar ist; SHA256 im Manifest |
| `kaggle/README.md` | „Dateien" + Abschnitt „V2" | Ablauf, Pins, fail-closed-Verhalten und Grenzen des Messlaufs dokumentiert |

Quellen der Korrekturen: Rohtext der Adapter (`a595d437…`/`e3be2c85…`), der Läufe
(`wb_b2prime/…`, `wb_b2/…`), Code (`write_back_cycle.py:318,322-333,420-421,442-445,507-530,519-522,735-740`),
`acceptance_gate.py:95-131`, `train_slow_consolidation.py:57-65,528-536`, Rek 077/103/115/125/126/128.

## 11. M1/M2/M3-Lauf — Vorbereitung (Ausführung durch den Menschen, GPU)

**Skript (read-only, jetzt im Repo):** `kaggle/m1_m2_m3_probe.py`
(SHA256 `f505d0fc12fc289fc36142b3161b0e3b9297013e035dbd779174c1880cb4f933`, 794 Z.)
**Preregistration:** `kaggle/m1_m2_m3_preregistration.md`
(SHA256 `472bf0727bc3bde8f6346143553478aa69028935d6d47c94e9c09b966a20efae`; Amendment A1: R3a/R3b)
— im Repo, damit der Lauf auf Kaggle per `git clone` reproduzierbar ist (kein Training, kein Write-Back).

Dateien (in Kaggle hochzuladen):

| Datei | Rolle | SHA256 |
|---|---|---|
| `m1_m2_m3_probe.py` | Messskript (read-only) | `f505d0fc12fc289fc36142b3161b0e3b9297013e035dbd779174c1880cb4f933` |
| `probe15_questions.jsonl` | 15 Probes (question/gold/key) | `c0ea0219c6a56b50601f85f211b14b5902d8103a73ecf37059560fe5d74b4328` |
| `consolidation_sft.jsonl` | Quelle der Wahrheit (messages-Format) | `18caaae7c6f7f506a0cdd132d15f23c0e7044b07d894b73eb68b302605b01c7c` |
| B2′-Adapter (`adapter_model.safetensors` + `adapter_config.json`) | M2 | `a595d437f4fcb0c6030840d9e70e7ff6818a5e490943aabe19f00c3dee6ba9c5` |
| B2-Adapter (`adapter_model.safetensors` + `adapter_config.json`) | M3 | `e3be2c8518433696a6aa5b088a43823facc099b20c7beab385e9352ec3023f2e` |
| `write_back_cycle_result.json` (B2′-Altlauf) | Regel 6 (P-2b) | `5a9ed27a19a1881a8d06eab1e150df3eb476baa4979d4da0422acc9b62501304` — **SHA256 der Datei, kein Git-Commit** |

Befehl (Kaggle, GPU; `--base-revision`/`--tokenizer-revision` **Pflicht**):

```bash
python kaggle/m1_m2_m3_probe.py \
  --dataset probe15_questions.jsonl \
  --base-model Qwen/Qwen2.5-3B-Instruct \
  --base-revision <40-hex-commit> \
  --tokenizer-revision <40-hex-commit> \
  --adapter-b2prime /kaggle/working/adapters/b2prime \
  --adapter-b2      /kaggle/working/adapters/b2 \
  --expect-dataset-sha   c0ea0219c6a56b50601f85f211b14b5902d8103a73ecf37059560fe5d74b4328 \
  --expect-b2prime-sha   a595d437f4fcb0c6030840d9e70e7ff6818a5e490943aabe19f00c3dee6ba9c5 \
  --expect-b2-sha        e3be2c8518433696a6aa5b088a43823facc099b20c7beab385e9352ec3023f2e \
  --ref-b2prime-json write_back_cycle_result.json \
  --expect-ref-sha 5a9ed27a19a1881a8d06eab1e150df3eb476baa4979d4da0422acc9b62501304 \
  --expect-probes 15 \
  --out-dir /kaggle/working/m1_m2_m3_out \
  --repo-root /kaggle/working/knowledge-agent
```

Erwartete Artefakte in `--out-dir`: `status.json`, `manifest.json`, `per_item.jsonl`.
Ohne GPU schreibt das Skript `status.json` mit `status="nicht ausgefuehrt"` — **keine** Zahlen.
Nach Rückgabe: 9 prä-registrierte Regeln anwenden, `Ursache` bestimmen, **Rek 130** mit den
Rohartefakten anlegen, Gate neu bewerten (unverändert `deny`, `AGENTS.md:120`), §9.1d-Proposal
erst mit Score-Änderung/Diff/Drift (`AGENTS.md:178-182`) nach `ergebnisse/proposal-template.md`.
