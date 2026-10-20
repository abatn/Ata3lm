# Preregistration M1/M2/M3 (read-only, Kaggle-GPU) — B2′-Annahmenprüfung

> Ort: **im Repo** (`kaggle/m1_m2_m3_preregistration.md`; Arbeitsfassung lag unter
> `/tmp/opencode/M1_M2_M3_PREREGISTRATION.md`). Repo-Stand: Commit `e93f230`.
> Grundlage: `AGENTS.md` §6 (Rohtext), §9 (`AGENTS.md:116-124`), §9.1d (`:178-182`),
> §9.3 (`:231`), Guardrails `:99-109`. Stand 2026-10-20.
> Hinweis: Die 9 Regeln sind in `ergebnisse/rekursion/129-b2-prime-annahmenpruefung.md` §7.2
> **übernommen** (Rek 129, Commit `487c282`). Amendment A1 (R3a/R3b) ist hier enthalten.
> **Amendment A2** (write-new-taugliche Regeln: „M1 schlecht ⇒ Basis defekt" ist für
> write-new-Fakten nicht informativ) ist **nicht freigegeben** und liegt als Proposal
> `ergebnisse/proposals/P-131-kontrollierter-rslora-ab.md` vor (§9.1d).
> Doc-Ziel der Indexzeile: **`ergebnisse/rekursion/README.md:156`** (die Wurzel-`README.md`
> hat nur 70 Zeilen und keine Rekursionstabelle).

## 0. Amendment A1 (2026-10-20) — R3a/R3b geschlossen

- **R3a:** Die Canary-Referenz ist **M1b** (Messung auf **derselben** Instanz, die danach
  gewrappt wird) — **nicht** M1. Damit ist der Canary immun gegen Cross-Instance-Rauschen
  (verschiedene Allokation ⇒ cuBLAS-/SDPA-Reihenfolge ⇒ Token-Divergenz), das sonst als
  „Canary-Fail ⇒ Regel 9" gewertet würde und die Diagnose zerstören würde.
  Zusätzlich: **M1_repeat** (Deterministische-Baseline, gleiche Instanz) und
  **M1c** (gepaarte Referenz für M3) + Cross-Instance-Noise als eigener, rein
  informeller Zähler.
- **R3b:** **Positivkontrolle** M2 (Adapter an) vs. canary (Adapter aus) auf derselben
  Instanz. `differing_items ≥ 1` ⇒ Adapter war aktiv. `= 0` ⇒ PC-Fail ⇒ Regel 9,
  **außer** Logit-Witness (pre-/post-wrap `max|Δlogits| > 0`) **und** Struktur-Witness
  (`lora_B ≠ 0`) zeigen einen geladenen, trainierten Adapter ⇒ dann Regel 8 (No-op).
- **Regeln 1–8: Wortlaut unverändert**, nur ihre Eingangsgrößen werden präzisiert
  (gepaarte Basisreferenzen M1b/M1c statt M1).
- **Aufgelöste Commits** der geladenen Basis/Tokenizer werden protokolliert
  (`config._commit_hash`, `tokenizer.init_kwargs._commit_hash`); optionale Pins
  `--expect-base-commit` / `--expect-tokenizer-commit` brechen bei Abweichung ab.

## 1. Artefakt-Pins (Vorbedingung, sonst Abbruch)

| Artefakt | Wert |
|---|---|
| Probe-Set (Quelle der Wahrheit) | `/tmp/opencode/consolidation_sft.jsonl`, 15 Zeilen, 5655 B, SHA256 `18caaae7c6f7f506a0cdd132d15f23c0e7044b07d894b73eb68b302605b01c7c` |
| abgeleitetes Probe-Set (Join-Form) | `/tmp/opencode/probe15_questions.jsonl`, 15 Zeilen, 2160 B, SHA256 `c0ea0219c6a56b50601f85f211b14b5902d8103a73ecf37059560fe5d74b4328` |
| B2′-Adapter | `hf_b2prime/adapter/adapter_model.safetensors`, SHA256 `a595d437f4fcb0c6030840d9e70e7ff6818a5e490943aabe19f00c3dee6ba9c5` |
| B2-Adapter | `hf_b2/adapter/adapter_model.safetensors`, SHA256 `e3be2c8518433696a6aa5b088a43823facc099b20c7beab385e9352ec3023f2e` |
| Altlauf-Referenz (Regel 6) | `wb_b2prime/write_back_cycle_result.json`, SHA256 `5a9ed27a19a1881a8d06eab1e150df3eb476baa4979d4da0422acc9b62501304` — **SHA256 der Datei, KEIN Git-Commit** |
| Basis | `Qwen/Qwen2.5-3B-Instruct` + `--base-revision` **und** `--tokenizer-revision` (Pflicht) |
| Messskript | `/tmp/opencode/m1_m2_m3_probe.py` (read-only) |

Abbruch (Status `nicht ausgefuehrt`), wenn: kein CUDA, `torch`/`peft` fehlt,
`torchao < 0.16.0` (bricht LoRA-Injektion, Beleg `kaggle/write_back_cycle.py:576-584`),
SHA abweicht, `use_rslora`/r/α unerwartet, `base_model_name_or_path != --base-model`,
Probe-Anzahl ≠ `--expect-probes`, Fragen nicht eindeutig, VRAM-Leck nach Freigabe.

## 2. Ablauf (Reihenfolge fix, 8 Durchläufe = 120 Generationen)

1. **M1** — Base-Instanz #1, 15 Probes, **vor** jedem Wrap (Muster `kaggle/e2e_theta_probe.py:122-124`).
2. **M1_repeat** — dieselbe Instanz #1 → Deterministische-Baseline; muss 15/15 identisch sein.
   Instanz #1 wird danach freigegeben.
3. **M1b** — Base-Instanz #2, **unwrapped** → **Canary-Referenz** (gleiche Instanz!).
4. **M2** — dieselbe Instanz #2 + B2′ (rsLoRA, `use_rslora=true`, r64/α256).
5. **Canary** — dieselbe Instanz #2, `disable_adapter()` → muss **M1b** item-für-item
   (String-Gleichheit) reproduzieren. Schwelle 100 %.
6. **M2_repeat** — dieselbe Instanz #2, Adapter wieder aktiv → Adapter-Pfad-Determinismus
   (und Beweis, dass `disable_adapter()` den Zustand zurücksetzt).
7. **M1c** — Base-Instanz #3, **unwrapped** → gepaarte Referenz für M3.
8. **M3** — dieselbe Instanz #3 + B2 (`use_rslora=false`, r64/α256).

Verboten und im Skript nicht enthalten: `kaggle/write_back_cycle.py` (trainiert + schreibt),
`self_update`, `route_and_store`, `slow_consolidation.write_back`, `train_fn`,
jede Erzeugung von Zahlen ohne GPU.

### 2.1 Rausch-Definitionen (prä-registriert)

- **Deterministische-Baseline** (M1 ↔ M1_repeat, gleiche Instanz): muss **15/15** sein,
  sonst Regel 9 (Messkette nondeterministisch ⇒ alle Item-Vergleiche hinfällig).
- **Cross-Instance-Noise** (M1 ↔ M1b, verschiedene Instanzen): **informativ**, Budget ≤ 2/15;
  Überschreitung ⇒ Regel 9. Dieser Wert wird **nie** als Diagnose verwendet.
- **Canary** (M1b ↔ canary, gleiche Instanz): Schwelle 100 %.

## 3. Schwellen (deskriptiv, keine Signifikanz)

- `gut` = strict-EM ≥ ⌈0,733·n⌉ (n=15 ⇒ 11/15 = 73,3 %; überschreitet die §9-70-%-Schwelle),
  `schlecht` = ≤ ⌊0,267·n⌋ (n=15 ⇒ 4/15 = 26,7 %), dazwischen `mixed`.
- `besser/schlechter` = ≥ ⌈0,2·n⌉ Items (n=15 ⇒ 3/15 = 20 pp). 1–2 Items = kein belastbarer Unterschied.
- Degenerationsflag: identische Antwort bei ≥ ⌈0,8·n⌉ Items (n=15 ⇒ 12/15).
- n = 15 ⇒ 1 Item = 6,7 pp. **Keine Signifikanzbehauptung.**
- Metrik primär `strict` (`data/memory/acceptance_gate.py:114-131`), `substring` nur Sensitivität.

## 4. Die 9 Regeln (prä-registriert, Präzedenz = Reihenfolge)

**Vorbedingungen zuerst** (Deterministische-Baseline → Cross-Instance-Noise-Budget →
Canary → Positivkontrolle → Basislast nicht degeneriert). Sind sie nicht alle erfüllt,
gilt **Regel 9** und es wird **keine** P-1/P-2/P-3-Diagnose gestellt. Sind sie erfüllt,
werden Regeln 1–8 geprüft — mit gepaarten Basisreferenzen (**M1b** für M2, **M1c** für M3).

| Nr. | Bedingung | Ergebnis |
|---|---|---|
| **1** | M1b gut, M2 schlecht, M3 ≥ M1c − 2/15 | P-1 deskriptiv **konsistent** (nicht bewiesen; M3 = historischer Code-Stand, Ceiling) |
| **2** | M1b gut, M2 schlecht, M3 schlecht | Adapterschaden, **nicht** spezifisch rsLoRA (Code-/Env-Konfundierung vorher ausschließen) |
| **3** | M1b schlecht, M2 und M3 ≥ M1b | P-3 Base/Prompt/Daten als Hauptkandidat (nur nach Formatkontrolle) |
| **4** | M1b schlecht, M2 und M3 ≤ M1b − 3/15 | Adapterschaden auf schwacher Base (Kandidat) |
| **5** | P-2a (Eigenschaft des Altlaufs) | N8 invalidiert `base_answer`, `em_base`, `changed`, Δ — **nicht** den adapter-seitigen Score |
| **6** | P-2b (nur falls M2 das 15-Tupel des Altlaufs nicht reproduziert) | Messkette nicht reproduzierbar ⇒ Artefakt-/Eval-/Umgebungs-Mismatch; ±1 Item ist kein Beleg |
| **7** | M2 ≥ M1b + 3/15 | Adapter hilft deskriptiv; P-1 nicht gestützt; §9-Gate bleibt `deny`, solange M2 < 11/15 |
| **8** | M2 ≈ M1b (± ≤ 2/15) **und** Positivkontrolle bestanden (M2 ≠ canary auf ≥ 1 Item) | No-op. Sub-Branch: M2 ≡ canary ⇒ Regel 9, **außer** Logit-Delta > 0 und `lora_B ≠ 0` ⇒ dann „Adapter geladen + trainiert, aber ohne Wirkung auf diesem Probe-Set" |
| **9** | Canary-Fail **oder** Positivkontrolle-Fail **oder** Deterministische-Baseline-Fail **oder** Cross-Instance-Noise > 2/15 **oder** Degeneration in M1/M1b/M2/M3 (identische Antwort bei ≥ 12/15) **oder** Ergebnis nicht zuordenbar | `unentschieden` — **Vorbedingung**, kein Zweig; keine P-1/P-2/P-3-Diagnose |

**Bekannte Grenzen (vorab registriert):**
- Die 15 Zeilen sind **Trainingszeilen** (Dataset `18caaae7…`) ⇒ M2/M3 messen **Memorization**,
  keine Generalisierung.
- **M3 hat ein Ceiling:** Im Altlauf B2 beantwortet der Adapter alle 15 Gold-Strings
  **exakt** (strict 15/15) ⇒ M3 wird voraussichtlich 15/15 und **kann P-1 vs. P-3 nicht
  trennen**. Für eine Trennung ist ein **Held-out-Probe-Set** nötig (z. B. 200 ZsRE,
  `em_base` 3/200 in `kaggle/e2e_theta_result.json:3-10`) — optional als Zusatzlauf,
  **nicht** Teil dieses Laufs.
- Format-Beispiel geprüft: gold `Jamaica Plain` vs. Antwort `Jamaica` ⇒ **strict FAIL und
  substring FAIL** (Grader prüft `gold ⊂ antwort`, `acceptance_gate.py:123-130`).

## 5. Ausgaben des Laufs (nur in `--out-dir`)

`status.json`, `manifest.json` (Hashes, **aufgelöste Commits**, Fingerprints, Env,
Grader-Crosscheck, alle Zählwerte, `measurement_passes`, `determinism_baseline`,
`cross_instance_noise`, `canary`, `positive_control`, `format_control`, `decision`),
`per_item.jsonl` (je Item: `pass`, `instance`, key/question/gold/raw_output/strict/
substring/gold_in_raw_output für alle 8 Durchläufe).
