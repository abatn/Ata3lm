# PROPOSAL 131 — Kontrollierter A/B: rsLoRA-Überskalierung (P-1) vs. Alternativen

> Datum: 2026-10-20 · Template: `ergebnisse/proposal-template.md`
> Gesetz: `AGENTS.md` §6 (Rohtext), §9 (`:116-124`), §9.1c (`:165-176`), §9.1d (`:178-182`),
> §9.3 (`:214-234`), §10.3 (`:271-276`) · Guardrails 1/2/3/5/6/7/8 (`:97-109`)
> Status: **pending** — §9.3-Zwei-Personen-Freigabe **nicht gestartet**; §9-Gate `deny` (unverändert).
> Anlass: `ergebnisse/rekursion/130-m1-m2-m3-lauf-b2-prime-messung.md` (Messung), Rek 129 (A1–A4).
> Kein `self_update`, kein Git-Commit, kein Training durch den Agenten — Ausführung: Mensch auf Kaggle (GPU).

---

## 0. Metadaten

| Feld | Wert |
|---|---|
| Datum | 2026-10-20 |
| Iteration | `t → t+1` |
| Phase | Compare (externes Signal vorhanden) → Revise (Proposal) |
| Betroffenes Artefakt | `kaggle/m1_m2_m3_probe.py` (Messskript, Code) · `kaggle/m1_m2_m3_preregistration.md` (Regelwerk) · `kaggle/README.md` (Doku) · Modellebene: Adapter-Training (ENV `LORA_USE_RSLORA`) |
| Komponenten-Typ | Code (Messintegrität) + Experiment (Modellebene) |
| Autor | Knowledge-Agent (Freigabe durch Nutzer + §9.3 Batnini/Taoufik **ausstehend**) |

**Warum zwei Komponenten (DREvo-Anforderung „ein Component pro Iteration"):** Die beiden
Komponenten haben **verschiedene Wirkebenen** und sind attributionstrennbar: (1) die
Messskript-Komponente verändert **nur die Zuordnung** von Messwerten zu Regeln (kein Messwert
ändert sich), (2) die Experiment-Komponente ist die **einzige Behandlungsvariable** des A/B.
Beide A/B-Arme laufen mit **identischem Code**, damit die Attribution der Wirkung erhalten bleibt.

---

## 1. Ziel `g`

- **Ziel:** kausale Trennung der Hypothese **P-1** (rsLoRA-Überskalierung: `use_rslora=true` ⇒
  Skalierung α/√r = 256/8 = **32** statt α/r = 256/64 = **4**, also 8× größere effektive
  Updateskalierung) von den konkurrierenden Erklärungen („Lernrate 2e-4 zu hoch", „historischer
  Code-Stand des B2-Laufs"), die der Vergleich B2′ ↔ B2 (Rek 130 §5) **offen** lässt.
- **Task-Input:** dieselben 15 `write-new`-Fakten (Dataset-Hash `18caaae7…`, 15 Zeilen, 5655 B),
  Basis `Qwen/Qwen2.5-3B-Instruct` @ Commit `aa8e72537993ba99e69dfaafa59ed015b17504d1`,
  r=64, α=256, lr 2e-4, 15 Epochen, Seed 42, `max_new_tokens=16`, `do_sample=false`.

**Nicht-Ziel (explizit):** keine Verbesserung des Flush-/Gate-Scores, keine neue Konsolidationslogik,
keine Änderung an `write_back_cycle.py`, kein `self_update` von Originaldateien.

---

## 2. Baseline (vorher)

| Feld | Wert |
|---|---|
| `π` (Modell/Policy) | Basis 3B + B2′-Adapter (rsLoRA, `use_rslora=true`) — HF `Batnini/knowledge-agent-write-back`, Pfad `adapter/`, Revision `f704f4a12df53966095604cce824c0d7785b1446`, Gewicht-SHA256 `a595d437…` |
| Score (externes Signal) | **1/15 = 6,7 %** (adapter-seitig; strict = substring = `gold_in_raw_output`) |
| Signal-Quelle | echter Kaggle-T4-Lauf 2026-10-20 (torch 2.11.0+cu128, transformers 5.16.1, peft 0.20.0, torchao 0.18.0, fp16, sm_75) → HF-Artefakte `probe/m1_m2_m3_2026-10-20/` (`manifest.json` SHA256 `8c8697c0…`, `per_item.jsonl` SHA256 `95ceabbc…`, `status.json` SHA256 `69c27db3…`); **unabhängig nachgerechnet** mit `data/memory/acceptance_gate.py:114-131` über die 120 Rohzeilen (alle 8 Pässe identisch) — Rek 130 §3 |
| Drift-Referenz | `π₀` = B2′-Adapter (HF `f704f4a…`); Kontrollarm = B2-Adapter (HF `04ed1333…`, `use_rslora=false`) mit **15/15** im selben Mess-Setup (Rek 130 `per_item.jsonl:106-120`) |

**Zusatz-Baseline (Kontext, kein Score):**

| Beobachtung | Wert | Beleg |
|---|---|---|
| Basis (M1/M1b/M1c) | 0/15 (12 Verweigerungen + 3 Fehlantworten, **keine** Degeneration, `top_count=1`) | `per_item.jsonl:1-15` |
| B2′-Antworten | 13× „Jamaica" + 1× „KFC Airways" + 1× „2005" | `per_item.jsonl:46-60` |
| Canary `disable_adapter()` (M1b ↔ canary, gleiche Instanz) | **15/15** | `manifest.json:canary` |
| Determinismus (M1 ↔ M1_repeat) / Cross-Instance-Noise (M1 ↔ M1b) | 15/15 / 15/15 (0 Rauschen) | `manifest.json:determinism_baseline`, `:cross_instance_noise` |
| Positivkontrolle M2 ↔ canary | 15/15 Items verschieden, Logit-Delta 25,0888671875, `argmax_changed=true` | `manifest.json:positive_control` |
| Loss B2′ vs. B2 | 5,190721893310547 vs. 1,310697078704834 | `wb_b2prime/kaggle_output.json:7`, `wb_b2/kaggle_output.json:7` |
| Regel-6-Abgleich (M2 ↔ Altlauf) | 14/15 identisch (1 Abweichung: KOAN Sound „Jamaica" → „KFC Airways") | `manifest.json:regel6_reference` |

**Belastbarkeitsgrenze der Baseline (§6, nicht verschwiegen):** Die Maschinenentscheidung des
Laufs („Regel 3 / P-3") war **nicht regelkonform** — Regel 9 (Degeneration in M1/M1b/M2/M3, ≥ 12/15)
hätte greifen müssen (`kaggle/m1_m2_m3_preregistration.md:99` vs. `kaggle/m1_m2_m3_probe.py:575-576`,
Rek 130 §4 M4). Die Baseline ist deshalb **ein Messwert-Set, keine Diagnose**; Diagnose =
`unentschieden` (Rek 130 §6).

---

## 3. Änderung (Diff, line-level)

### 3a. Messintegrität (Code + Doku) — in dieser Iteration umgesetzt, Freigabe steht aus

```diff
--- a/kaggle/m1_m2_m3_probe.py
+++ b/kaggle/m1_m2_m3_probe.py
@@ Vorbedingungsblock @@
     if coll["M1_base"]["collapse"] or coll["M1b_base"]["collapse"]:
         failed.append("base_collapse")
+    # Regel 9 (Preregistration:99) verlangt Degeneration in M1/M1b/M2/M3.
+    if coll["M2_b2prime"]["collapse"]:
+        failed.append("m2_collapse")
+    if coll["M3_b2"]["collapse"]:
+        failed.append("m3_collapse")

@@ Regel-9-Meldungen @@
         if coll["M1_base"]["collapse"] or coll["M1b_base"]["collapse"]:
             rules.append((9, "Base degeneriert (identische Antwort bei >= COLLAPSE_MIN) — Diagnose blockiert"))
+        if coll["M2_b2prime"]["collapse"]:
+            rules.append((9, f"M2 degeneriert ({coll['M2_b2prime']['top_count']}/{n} identische Antwort …) — Diagnose blockiert, kein P-1/P-2/P-3-Zweig"))
+        if coll["M3_b2"]["collapse"]:
+            rules.append((9, f"M3 degeneriert ({coll['M3_b2']['top_count']}/{n} identische Antwort …) — Diagnose blockiert, kein P-1/P-2/P-3-Zweig"))

@@ Struktur-Witness @@
-        for name, mod in inst2.named_modules():
-            if name.endswith("lora_A") and hasattr(mod, "weight"):
-                lora_modules_total += 1
-                bmod = getattr(mod, "lora_B", None)
+        for _name, mod in inst2.named_modules():
+            a_dict = getattr(mod, "lora_A", None)
+            b_dict = getattr(mod, "lora_B", None)
+            if a_dict is None or b_dict is None:
+                continue
+            lora_modules_total += 1
+            for lora_b in b_dict.values():
+                weight = getattr(lora_b, "weight", None)
                 …
```

Begründung je Zeile: (i) Regel 9 war im Skript **unvollständig** umgesetzt (nur Basis geprüft)
⇒ der Lauf meldete fälschlich eine Diagnose; (ii) der Struktur-Witness prüfte
`name.endswith("lora_A")`, PEFT registriert aber `…lora_A.<adapter_name>` in einem `nn.ModuleDict`
(`peft/tuners/lora/layer.py:134`, `:263`; Muster wörtlich `peft/utils/other.py:1096`) ⇒ der
Zähler war **immer 0** und ist ein Zeuge, kein Adapter-Befund (Rek 130 §4 M3). Der Zeuge wird
adapter-name-agnostisch über den LoraLayer (`lora_A` **und** `lora_B` vorhanden) gezählt.
Doku-Fixes: `kaggle/README.md` (Klonname = Repo-Name `Ata3lm`; `--repo-root` muss auf die
Klonwurzel zeigen, sonst `grader_crosscheck: skipped` — Rek 130 §4 M1) und
`kaggle/m1_m2_m3_preregistration.md` (veraltete Kopfzeilen — Rek 130 §4 M5).

### 3b. Experiment (Modellebene) — **beantragt, nicht ausgeführt**

```diff
# Kaggle-ENV des B2′-Laufs (wb_b2prime/kaggle_output.json:23-26)
- LORA_USE_RSLORA=1        # => use_rslora=true  => Skalierung α/√r = 256/8 = 32
+ LORA_USE_RSLORA=0        # => use_rslora=false => Skalierung α/r  = 256/64 = 4
```

Alles andere **identisch**: Code-Stand (aktuell, inkl. Rek-127-CLI), Dataset-Hash `18caaae7…`,
`NUM_EPOCHS=15`, `LORA_R=64`, `LORA_ALPHA=256`, `learning_rate=2e-4`, Seed 42, Basis-Commit
`aa8e725…`, `target_modules` (7 Module, feste Reihenfolge), `lora_dropout=0.05`, fp16/T4.
Der zweite Arm ist ein **zusätzlicher** Lauf auf demselben Code-Stand — er ersetzt **nicht** den
historischen B2-Lauf (dieser lief auf altem Code, Rek 128 §1/§5).

- **Geänderte Komponenten:** 2 (Begründung s. §0)
- **Interface-Änderung?** **nein** — `LORA_USE_RSLORA` existiert bereits (Rek 127, `train_slow_consolidation.py`),
  CLI-/JSON-Schema unverändert ⇒ kein §9-Interface-Gate. §9.3 gilt trotzdem (Modellebene).

---

## 4. Score-Änderung

| Testfall | Kriterium | vorher | nachher |
|---|---|---|---|
| 1 | adapter-seitiger strict-Score, Arm `LORA_USE_RSLORA=1` | **1/15 = 6,7 %** | **Erwartung** (keine Messung): ≥ 11/15 = 73,3 % |
| 2 | Degenerationsflag Arm `=1` (identische Antwort bei ≥ 12/15) | **true** (13/15) | **Erwartung**: `false` |
| 3 | adapter-seitiger strict-Score, Arm `LORA_USE_RSLORA=0` (Kontrollarm, neuer Lauf) | 15/15 (historisch, M3) | **Erwartung**: 15/15 |
| 4 | Canary `disable_adapter()` (M1b ↔ canary, gleiche Instanz) | 15/15 | **Pflicht**: 15/15, sonst Abbruch (Regel 9) |
| 5 | Deterministische Basis (M1 ↔ M1_repeat) / Cross-Instance-Noise (M1 ↔ M1b) | 15/15 / 15/15 | **Pflicht**: 15/15 / ≤ 2/15 Abweichung |
| 6 | Regel-9-Konformität des Messlaufs | **verletzt** (M4: „Regel 3" statt „Regel 9") | **Pflicht**: `unentschieden` bei Degeneration, keine P-1/P-2/P-3-Zuordnung |

- **Score vorher:** `1/15` = **6,7 %** (externes Signal: Kaggle-T4, HF-Artefakte, unabhängig nachgerechnet)
- **Score nachher:** **noch nicht gemessen** — die Spalte „nachher" enthält ausschließlich
  **Erwartungen aus den prä-registrierten Kriterien**, keine Tatsachen (§6).
- **Δ Score:** **offen** bis zum Lauf; Zielkorridor Δ ≥ +66,7 pp (1/15 → ≥ 11/15).

**Vorab registrierte Auswertungsregel (Amendment A2, hier nur beantragt — nicht angewendet):**

| Beobachtung im A/B | Schluss |
|---|---|
| Arm `=1`: ≤ 4/15 **oder** Degeneration; Arm `=0`: ≥ 11/15 **und** keine Degeneration | **P-1 bestätigt** (rsLoRA-Überskalierung verursacht den Kollaps) |
| Arm `=1`: ≤ 4/15 **oder** Degeneration; Arm `=0`: ≤ 4/15 **oder** Degeneration | P-1 **widerlegt**; Schaden ist trainings- bzw. lernratenspezifisch (nicht rsLoRA) → lr-Sweep (2e-4 vs. 2e-5, **Hypothese**, bisher nicht gemessen) |
| beide Arme ≥ 11/15 und keine Degeneration | P-1 **widerlegt**; der historische B2′-Kollaps war ein Code-/Umgebungsartefakt |
| Arm `=1`: ≤ 4/15 **oder** Degeneration; Arm `=0`: mixed (5–10/15) | **unentschieden** (keine Ursache belegt) |

**Amendment A2 der Regeltabelle (beantragt, write-new-tauglich):** Regel 3 („M1b schlecht ⇒ P-3
Base/Prompt/Daten") ist für `write-new`-Fakten **nicht informativ**, weil Basis-Unwissen der
Sollzustand des Write-Pfads ist (§10.1 `:250`, §10.7 `:316`, §10.3 `:271-276`) — Rek 130 §5 (E1).
Vorschlag: Regel 3 nur anwenden, wenn **zusätzlich** die Basis **mit** Memory (Write-Back-Quelle)
antworten kann; der Primär-Diskriminator wird **M3 vs. M2 innerhalb derselben Messung**
(gleiche Basis/Daten/Decoding → nur der Adapter unterscheidet sich).

---

## 5. Drift (Δ zur Baseline)

- **Definition (Auftrag, praktische Messung):** `Δ = geänderte Zeilen / Gesamtzeilen des Artefakts`
  (line-level, vgl. DREvo, `AGENTS.md:178-182`); für Modell-Parameter `‖πₜ − π₀‖ / ‖π₀‖`.
- **Drift-Wert (Code/Doku dieser Iteration):**
  | Artefakt | geänderte Zeilen | Gesamtzeilen | Δ |
  |---|---|---|---|
  | `kaggle/m1_m2_m3_probe.py` | 41 + / 11 − | 824 | **6,31 %** |
  | `kaggle/m1_m2_m3_preregistration.md` | 7 + / 3 − | 122 | **8,20 %** |
  | `kaggle/README.md` | 6 + / 3 − | 314 | **2,87 %** |
  | **Gesamt (Code/Doku)** | **54 + / 17 −** | **1260** | **5,63 %** |
- **Drift-Bound:** Default **10 %** (Auftrag, §9.1c `:171-176`) ⇒ **nicht überschritten**
  (schlechtester Einzelwert 8,20 % < 10 %).
- **Drift Modell-Parameter:** **nicht vorab messbar** (der A/B erzeugt neue Adapter). Nach dem Lauf
  zu berichten: `‖πₜ − π₀‖/‖π₀‖` je Arm gegen `π₀` = B2′-Adapter (`f704f4a…`). Überschreitung
  > 10 % ⇒ **Human-Gate (ask)**, §9.1c.
- **Hinweis:** Die Code-Änderung selbst erzeugt **keine** Parameterdrift — sie verändert nur die
  Regel-Zuordnung; der Messwert-Satz des Baseline-Laufs bleibt unverändert (Rek 130 §3).

---

## 6. Evidenz / Quellen

- arXiv:2312.03732 — rsLoRA (Skalierung α/√r statt α/r; `use_rslora`, α/√r) — https://arxiv.org/abs/2312.03732
- arXiv:2608.22215 §3.4 — Write-Back / Slow Consolidation (Θ → Θ′) (Kontext des A/B-Ziels) — https://arxiv.org/abs/2608.22215
- arXiv:2609.08832 — Consistency Gap (Compare nur mit externem Signal) — https://arxiv.org/abs/2609.08832
- Code: `kaggle/m1_m2_m3_probe.py` (Messskript), `kaggle/m1_m2_m3_preregistration.md:99` (Regel 9),
  `kaggle/write_back_cycle.py:420-421` / `:442-445` (N8: Basis vor dem Wrap; `passed` = `grade(adapter_answer, gold)`),
  `kaggle/e2e_theta_probe.py:122-124` (Muster Basis vor Wrap), `data/memory/acceptance_gate.py:114-131` (Grader)
- Interne Referenz: `ergebnisse/rekursion/130-m1-m2-m3-lauf-b2-prime-messung.md` (§2–§6),
  `ergebnisse/rekursion/129-b2-prime-annahmenpruefung.md` (A1–A4, §7.1–§7.3), Rek 128 (B2, Code-Stand), Rek 127 (CLI-Args)
- Messartefakte (extern): HF `Batnini/knowledge-agent-write-back`, Pfad `probe/m1_m2_m3_2026-10-20/`
  (`status.json` `69c27db3…`, `manifest.json` `8c8697c0…`, `per_item.jsonl` `95ceabbc…`)

---

## 7. Gate-Entscheidung (§9)

| Bedingung | Wert | Ergebnis |
|---|---|---|
| Score | **6,7 %** (< 70 %, `AGENTS.md:120`) | **deny** für `self_update`/Lernen |
| Neue Quelle? | nein (alle genannten Quellen stehen in `AGENTS.md:393-411`) | — |
| Interface-Änderung? | nein (`LORA_USE_RSLORA` existiert, CLI/Schema unverändert) | — |
| Drift ≤ Bound? | Code/Doku ja (5,63 % ≪ 10 %); **Modell-Drift offen** (nach Lauf) | **ask** |

- **Gate-Ergebnis: `ask`** — der Score verbietet Lernen/`self_update` (deny), die Messung selbst
  (A/B-Experiment + Messskript-Korrektur) bleibt erlaubt, **aber** nur nach:
  1. **Human-Gate** des Nutzers (dieses Proposal),
  2. **§9.3-Zwei-Personen-Freigabe** (mind. 2 distinkte Personen: Batnini + Taoufik;
     Flow `pending → first_approved → second_approved → approved`, `AGENTS.md:231`),
  3. **kein** Commit und **kein** `self_update` vor dieser Freigabe.
- Erfüllt der A/B-Testfall 1–6 aus §4, ist das **Ergebnis** des Experiments (kein Gate-Wechsel
  während des Laufs) und wird als eigene Rekursion mit `pending` dokumentiert.

---

## 8. Freigabe

- **Status:** `pending`
- **Human-Gate-Referenz:** `ergebnisse/rekursion/130-m1-m2-m3-lauf-b2-prime-messung.md`,
  `ergebnisse/rekursion/129-b2-prime-annahmenpruefung.md`
- **§9.3:** nicht gestartet — Freigaben von Batnini und Taoufik stehen aus
- **Bereits umgesetzt (wartet auf Commit-Freigabe):** 3a (Messskript 2 Stellen, README,
  Prereg-Kopfzeilen) — reine Messintegrität, kein Eingriff in `write_back_cycle.py`, kein Training
- **Ausführung (menschlich, Kaggle GPU):** zwei Läufe mit identischem Code, nur `LORA_USE_RSLORA`
  0 bzw. 1; Messung je Lauf mit `kaggle/m1_m2_m3_probe.py` (nach Fix 3a: Regel-9-konform) plus
  Write-Back-Messung mit Basis **vor** dem Wrap (`kaggle/write_back_cycle.py:420-421`/`:442-445`)
  und Canary `disable_adapter()` 15/15

### Pflichtfelder (Kurzcheck)

- [x] Score vorher/nachher mit externem Signal (nachher = **Erwartung**, klar als solche markiert)
- [x] Diff (line-level) — §3a (Code/Doku) und §3b (Modellebene)
- [x] Drift-Wert + Bound-Vergleich — §5 (5,63 % Code/Doku; Modell-Drift offen, nach Lauf zu berichten)
- [x] Quelle(n) mit Link — §6 (arXiv + Code + HF-Artefakte)
- [x] Gate-Ergebnis + Freigabe-Status — §7 (`ask`), §8 (`pending`)
