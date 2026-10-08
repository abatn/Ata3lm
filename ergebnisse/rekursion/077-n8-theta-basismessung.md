# Rekursion 077: N8 — Basisvergleich lädt Adapter vor Messung (kaggle/e2e_theta_probe.py)

> Datum: 2026-10-08 · Phasen: Konstrukt → Akt → Observe → Compare (echte Tests).
> **Befund-Quelle (verbindlich): Audit b09a0a9** (Datei `tests/test_network_boundaries.py`).
> N-Nummerierung = **Audit** (NICHT Rekursion 062–063).
> Ziel `g` (§10.3): `em_base` misst das **unveränderte** Basismodell — sonst ist der
> Vergleich `em_adapter > em_base` (arXiv:2608.22215 §3.4) wertlos (Δ = 0).
> Akzeptanz: `em_base` = unverändert (Messung VOR Adapter-Erzeugung).
> Auftrag: „Knowledge-Agent härten — N1–N8 (Revision b09a0a9)", Phase 1
> (autonom, reine Mechanik; KEIN Commit).
> Status: **umgesetzt** (kein Interface) · Freigabe: **`pending`** — §9 `ask` offen (Formatänderung `elapsed_s` + GPU-Lauf).

## 1. Soll/Norm (Audit + Fundstellen)

| Feld | Wert (Audit b09a0a9, verbindlich) |
|---|---|
| Befund | **N8 · P1 · Basisvergleich lädt Adapter vor Messung** |
| Datei | `kaggle/e2e_theta_probe.py` ~`:72-73`, ~`:97` |
| Nachweis | **statisch/source-belegt** (PEFT in-place) |
| Repro | statisch: `tests/test_e2e_theta_probe.py::test_n8_basismessung_vor_peftmodel_vor_em_adapter` |

Norm: AGENTS.md §10.3; arXiv:2608.22215 §3.4 (beide bereits im Projekt).
Quellen (PEFT-Doku — **bereits im Repo, KEINE neue Quelle**; PEFT/TRL bereits in
`kaggle/train_slow_consolidation.py:64-65,306-308` ⇒ kein Ontologie-Eintrag nötig):
- <https://huggingface.co/docs/peft/en/package_reference/peft_model>
  (`PeftModel` wickelt das Basismodul ein; `disable_adapter`: „Use this to run
  inference on the base model")
- <https://huggingface.co/docs/peft/en/package_reference/lora>
  (LoRA „injects … into each layer")

## 2. Befund (Ist ≠ Soll)

- `e2e_theta_probe.py:72-73`: `base = AutoModelForCausalLM…` **und direkt danach**
  `adapter = PeftModel.from_pretrained(base, …)`; `em_base = exact_match(base)`
  (~`:97`) lief also **nach** dem Adapter-Laden. PEFT wickelt **dasselbe** `base`-
  Objekt in-place ein ⟹ Basismessung misst **MIT** Adapter.
- **Empirisch konsistent:** Kaggle-Lauf 2026-10-07 (`ergebnisse/e2e-theta-2026-10-07.md`):
  `em_base == em_adapter == 22/200`, `Δ = 0` (Symptom einer kontaminierten
  Basismessung; allein kein Beweis).

## 3. Änderung (Diff-Skizze)

Option 1 des Auftrags („Basismessung VOR `PeftModel.from_pretrained`"):

```diff
     base = AutoModelForCausalLM.from_pretrained(…).cuda().eval()
-    adapter = PeftModel.from_pretrained(base, args.adapter).eval().cuda()
     …
     t0 = time.time()
+    # N8: Basismessung VOR PeftModel.from_pretrained (PEFT-Doku s. §1)
     em_base = exact_match(base)
+    adapter = PeftModel.from_pretrained(base, args.adapter).eval().cuda()
     em_adapter = exact_match(adapter)
```

| Datei | Inhalt |
|---|---|
| `kaggle/e2e_theta_probe.py` | Reihenfolge geändert (Option 1); Kommentar mit belegten Quellen; `elapsed_s` umschließt seitdem auch die Adapter-Ladezeit (im Code vermerkt). |
| `tests/test_e2e_theta_probe.py` (neu) | +3: AST-Reihenfolge `em_base < PeftModel < em_adapter` auf der **realen** Datei (Red→Green); `load_rows` gegen echte JSONL (×2). |

- Interface-Änderung? **nein** (CLI-Parameter + Output-Schema/Feldnamen unverändert);
  **Formatänderung** — `elapsed_s` umfasst jetzt auch die Adapter-Ladezeit (Umfang
  vermerkt, s. §4) ⇒ §9/Guardrail 4, Human-Gate.

## 4. Real vs. offen (ehrlich)

- **Real:** Struktur-Test auf der realen Datei (altes Skript rot, neues grün);
  `load_rows` gegen echte JSONL.
- **Offen (ehrlich):** Laufzeit-Akzeptanz „`em_base` = unverändert" nur im echten
  GPU-Lauf (Kaggle) prüfbar — `torch`/`peft` lokal **nicht** installiert; Fake-Modell
  verboten (Guardrail 7). Der Struktur-Test garantiert die Reihenfolge, **nicht** die
  PEFT-Laufzeitsemantik (belegt über die PEFT-Doku, §1). GPU-Gesamtlauf = Human-Gate-
  Position des Auftrags, **offen**.

## 5. Compare / Beleg (externes Signal: echte Tests)

```text
Rot (altes Skript): pytest tests/test_e2e_theta_probe.py -k n8 --no-cov -> 1 failed
Grün (neues Skript): pytest tests/test_e2e_theta_probe.py --no-cov      -> 3 passed
Ruff check + format --check                                             -> All checks passed
Laufzeit-Nachweis em_base unverändert -> offen (GPU-Gesamtlauf, §9 ask)
```

## 6. §9-Gate

**`ask` (offen)** — zwei Punkte:
1. **Interface-/Formatänderung** — `elapsed_s` umfasst jetzt auch die Adapter-Lade-
   zeit (Format-/Semantikänderung des Outputs, s. §3/§4) ⇒ §9/Guardrail 4 („keine
   Format-/Schnittstellenänderung ohne Freigabe"), Freigabe (≥ 2 Personen, §9.3) **offen**.
   **Keine neue Quelle:** PEFT-Doku bereits im Repo
   (`kaggle/train_slow_consolidation.py:64-65,306-308`); kein Ontologie-Eintrag nötig.
2. GPU-Gesamtlauf (Laufzeit-Akzeptanz) = Human-Gate-Position des Auftrags, offen.

Kein `self_update` an Originaldateien, **kein Commit** (G6). **Freigabe-Status:
`pending`** (umgesetzt gem. Auftrag Phase 1; §9 `ask` offen, wie oben).
