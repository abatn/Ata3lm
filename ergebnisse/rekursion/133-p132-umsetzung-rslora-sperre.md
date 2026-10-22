# Rekursion 133: P-132 umgesetzt — rsLoRA im Write-Back-Zyklus fail-closed gesperrt (Code + Tests + Doku)

> Datum: 2026-10-22 · Gesetz: `AGENTS.md` §6 (`:61-68`), §9 (`:116-124`), §9.1c (`:165-176`),
> §9.1d (`:178-182`), §9.3 (`:214-234`), §10.3 (`:271-276`) · Guardrails 1/2/3/4/5/6/7/8 (`:97-109`)
> Status: **approved** — Umsetzung eines §9.3-freigegebenen Antrags
> (`ergebnisse/proposals/P-132-rslora-sperre-write-back.md`, §9.3 Batnini + Taoufik, 2026-10-22);
> **kein** Lern-/`self_update`-Schritt (Gate bleibt `deny`, §9 `:120`).
> Anlass: `ergebnisse/rekursion/132-ab-rslora-p1-bestaetigt.md` (A/B, P-1 bestätigt),
> `ergebnisse/proposals/P-132-rslora-sperre-write-back.md` (Diff §3, Score §4, Drift §5).
> Keine neue Quelle, keine Interface-Änderung, keine Änderung an `AGENTS.md`/`data/memory/tier1-base/`.

---

## 1. Auftrag & Setup

- **Ziel `g`:** Den §10.3-Write-Back-Pfad auf die **kausal belegte** sichere Trainingskonfiguration
  festlegen (rsLoRA **aus** ⇒ α/r = 4 statt α/√r = 32), damit der Kollaps (1/15 = 6,7 %, Degeneration
  13/15) nicht erneut auftreten kann — Antrag P-132 §3 (Diff), freigegeben §9.3.
- **Task-Input:** freigegebener Diff P-132 §3a/§3b/§3c (Code: `kaggle/write_back_cycle.py`;
  Tests: `tests/test_write_back_lora_args.py` + neu `tests/test_write_back_cycle_rslora_guard.py`;
  Doku: `kaggle/README.md`).
- **Ausführung:** Agent (Code im Repo, read-write), **kein** Training, **kein** Kaggle-Lauf in dieser
  Iteration; der Lauf des Write-Back-Zyklus (Kaggle + Ollama) ist der nächste, separate Schritt (§8).

---

## 2. Beobachtung / Ausgangslage (Belege)

- **Befund des A/B (Rek 132 §4, unabhängig nachgerechnet):** Arm rsLoRA (α/√r = 32) ⇒ **1/15 = 6,7 %**
  + Degeneration 13/15 „Jamaica"; Arm non-rsLoRA (α/r = 4) ⇒ **15/15**, keine Degeneration — bei
  identischem Code, identischen Daten (SHA `18caaae7…`, Aggregat `8d42c0da…`), Seed 42 und identischer
  Umgebung (`torch 2.11.0+cu128`, T4).
- **Angriffspunkt im Code (belegt):** `kaggle/write_back_cycle.py:328-329` setzte `LORA_USE_RSLORA=1`,
  sobald `--use-rslora` übergeben wurde (CLI `:519-521`, Default `False`) ⇒ der Kollaps-Lauf B2′ lief
  über genau diesen Pfad; die Option war damit der einzige Weg zur schädlichen Konfiguration im
  Write-Back-Zyklus.

---

## 3. Umsetzung (Diff, wie in P-132 §3 freigegeben)

### 3a. `kaggle/write_back_cycle.py` (+27 / −1, jetzt 806 Zeilen)

| Ort | Änderung | Zweck |
|---|---|---|
| `:601-626` (neu, nach `_torchao_incompatible()`) | `_rslora_blocked() -> Optional[str]` — Meldung mit Beleg (P-132, P-131, 1/15 vs. 15/15, `Rek 132 §4`), HF-Artefakt-Pfad und Hinweis auf den Forschungspfad | eine Quelle der Wahrheit für Guard + Defense in Depth |
| `:637-640` (`main()`) | Guard **direkt nach** `_parse_args()`: `if args.use_rslora: print("FEHLER: …", file=sys.stderr); return 1` | fail-closed **vor** jedem Seiteneffekt (kein LLM-/GPU-ENV, kein Training, kein Flush) |
| `:328-330` (`_make_train_fn`) | `env["LORA_USE_RSLORA"] = "1"` → `raise RuntimeError(_rslora_blocked())` | Defense in Depth: der ENV wird auch bei Umgehung des `main`-Guards **nie** gesetzt (kein stiller Fallback) |

**Nicht geändert (bewusst):** CLI-Flag `--use-rslora` bleibt existieren (keine Interface-Änderung,
Guardrail 4 `:100`) ⇒ alte Aufrufe erhalten eine verständliche Fehlermeldung statt
`unrecognized arguments`; der Forschungspfad `kaggle/train_slow_consolidation.py:63` liest
`LORA_USE_RSLORA` unverändert ⇒ kontrollierte A/Bs bleiben möglich.

### 3b. Tests (+4 / −3 in `tests/test_write_back_lora_args.py`; neu `tests/test_write_back_cycle_rslora_guard.py`, 90 Zeilen, 3 Tests)

- **Angepasst:** `test_wbc_train_fn_sets_env_when_args_provided` — `use_rslora=False`, und die
  Assertion `captured_env["LORA_USE_RSLORA"] == "1"` → `"LORA_USE_RSLORA" not in captured_env`
  (der alte Test kodierte das nun gesperrte Verhalten).
- **Neu (3 Tests, ohne GPU/LLM, echte Codepfade — Guardrail 7):**
  1. `_rslora_blocked()` liefert eine Meldung mit `P-132`, `1/15`, `15/15` und dem Forschungspfad.
  2. `main(["--use-rslora"])` ⇒ Rückgabe `1`, `stderr` enthält `FEHLER` und `P-132` (Abbruch **vor**
     jedem Seiteneffekt ⇒ ohne GPU/LLM prüfbar).
  3. `_make_train_fn(..., use_rslora=True)` ⇒ `RuntimeError` mit derselben Meldung; `subprocess.run`
     wird **nicht** aufgerufen (kein Training gestartet).

### 3c. Doku (+9 / −0 in `kaggle/README.md`)

Hinweis im Abschnitt „V1 — Geschlossener Write-Back-Zyklus": rsLoRA im Write-Back-Zyklus gesperrt,
mit Beleg (P-131-Lauf 2026-10-22, 1/15 vs. 15/15), Verweis auf Rek 132 §4 und P-132 (§9.3-Freigabe),
und Hinweis, dass ENV `LORA_USE_RSLORA` im Forschungsskript verfügbar bleibt.

---

## 4. Verifikation (externe Signale, §6 / Guardrail 7)

| Prüfung | Ergebnis |
|---|---|
| `make test` (`.venv`, Guardrail 8) | **860 passed, 1 skipped**, Coverage **100,00 %** — Erwartung P-132 §4 Testfall 4 („857 + 3 passed") **erfüllt** |
| Neue Tests einzeln | `tests/test_write_back_cycle_rslora_guard.py` + `tests/test_write_back_lora_args.py` ⇒ **15 passed** |
| `ruff check .` / `ruff format --check .` | `All checks passed!` / `126 files already formatted` |
| `scripts/check_md_links.py` | 68 relative Links – 0 fehlend |
| `scripts/check_artifacts.py` / `scripts/check_secrets.py` | 0 Fehler / 0 Treffer |
| `tests/test_agents_law.py` (Provenienz + Index) | 10 passed |

**Score-Änderung (§9.1d):** kein **neuer** Messwert — der Write-Back-Score des gesperrten Pfads ist
der **bereits gemessene** Kontrollarm 15/15 = 100 % (Rek 132 §3/§4, `probe/ab_2026-10-22/`); der Code
selbst erzeugt keinen Messwert, er verhindert nur die schädliche Konfiguration. Der Lauf des
Write-Back-Zyklus (Kaggle + Ollama) zur Bestätigung des Flush-Verhaltens ist **offen** (§8).

**Drift (§9.1c/§9.1d, Ist-Messung `git diff --numstat`):**

| Artefakt | +/− | Δ |
|---|---|---|
| `kaggle/write_back_cycle.py` | +27 / −1 (806 Z.) | 3,35 % |
| `tests/test_write_back_lora_args.py` | +4 / −3 (262 Z.) | 2,67 % |
| `tests/test_write_back_cycle_rslora_guard.py` (neu) | +90 | neue Datei |
| `kaggle/README.md` | +9 / −0 (323 Z.) | 2,79 % |
| **Gesamt (ohne neue Datei)** | **+40 / −4** (1391 Z.) | **3,02 %** |
| **Gesamt inkl. neuer Datei** | **+130 / −4** (1481 Z.) | **9,05 %** |

⇒ **unter** dem Drift-Bound 10 % (`AGENTS.md:171-176`) ⇒ **kein** §9.1c-Auslöser durch Code.
**Drift Modell-Parameter:** die Änderung trainiert nichts ⇒ **keine** neue Parameterdrift; der
Konfigurationswechsel π (rsLoRA) → π′ (non-rsLoRA) bleibt bei **93,7 %** (Rek 132 §5) — bereits
durch das §9.3-freigegebene Proposal P-132 (Gate `ask`) behandelt.

---

## 5. Gate (§9, `:116-124`)

| Bedingung | Wert | Ergebnis |
|---|---|---|
| Score ≥ 95 % **und** alle 8 Stufen „sicher" (`:118`) | 15/15 (gemessen, Kontrollarm), 8-Stufen-Zyklus für den Write-Back-Lauf **nicht** abgearbeitet | **kein** automatisches allow |
| Score < 70 % (`:120`) | rsLoRA-Konfiguration 6,7 % | **deny** (unverändert) |
| Neue Quelle (`:121`) | nein | — |
| Interface-Änderung (`:122`) | nein (Signatur/CLI/JSON unverändert) | — |
| self_update an Originaldatei (`:123`) | **ja** ⇒ §9.3-Freigabe **liegt vor** (P-132, Batnini + Taoufik, 2026-10-22) | freigegeben |
| Drift > 10 % (`:124`) | Code 9,05 % ≤ 10 %; Modell 93,7 % (bereits behandelt) | — |

⇒ **Lernpfad bleibt `deny`** (§9 `:120`): diese Iteration ändert die Trainingskonfiguration des
Write-Back-Pfads, **nicht** das Lern-Gate des Agenten. Eine Freigabe des Lernpfads braucht einen
eigenen Antrag mit eigenem Score.

---

## 6. Was diese Iteration **nicht** belegt (ehrlich, §6)

1. **Kein Lauf des Write-Back-Zyklus** in dieser Iteration ⇒ der Flush-Pfad (N8: Basis vor dem Wrap,
   `kaggle/write_back_cycle.py:420-421`/`:442-445`) wurde **nicht** erneut verifiziert; der Canary
   15/15 des Probe-Laufs (Rek 132 §3) belegt die adapter-freie Basismessung, **nicht** den Flush.
2. **Der Kollaps-Adapter bleibt im Repo/HF** (`ab_rslora1/adapter/adapter_model.safetensors`
   `a595d437…`, HF-Revision `f704f4a…`) — er ist **Historie** (Rek 129/130/132), wird nicht mehr
   verwendet, aber nicht gelöscht (Provenienz, `AGENTS.md:99`).
3. **Memorization bleibt ungelöst:** die 15 Items sind Trainingsitems; die Sperre verhindert den
   Kollaps, sie beweist **keine** Generalisierung (Rek 132 §7.1/§7.2) — dafür ist ein
   Held-out-Probe-Set nötig (Folgeantrag, P-132 §8).
4. **A2-Auswertungsregel** ist weiterhin nicht im Messskript implementiert (Rek 132 §7.3) — der
   nächste Messlauf meldet weiterhin regel-9-konform `unentschieden`, die A/B-Entscheidung wird
   weiterhin aus den Rohzählern abgeleitet.

---

## 7. Nächster Schritt (zulässig, §8 in P-132)

1. **Kaggle-Lauf des Write-Back-Zyklus** (GPU + Ollama lokal auf der Kaggle-Maschine,
   `kaggle/README.md` „V1"-Abschnitt) **ohne** `--use-rslora` ⇒ Laufprotokoll (`write_back_cycle_result.json`)
   mit echten Writes, Probe (Basis vor dem Wrap) und Flush-Entscheid als neue Rekursion (133-Folge)
   mit Rohartefakten; der Agent wertet sie mit `data/memory/acceptance_gate.py:114-131` aus.
2. **Folgeanträge** (je eigene §9.3-Freigabe): (a) A2-Regel ins Messskript, (b) Held-out-Probe-Set,
   (c) Erratum zur torchao-Herkunft in `P-131:253-256`.
3. **Danach** ein Antrag zum Lernpfad selbst (Gate `deny` → `ask`), weil erst mit einem
   Held-out-Nachweis die „8 Stufen sicher"-Bedingung (§9 `:118`) prüfbar wird.

---

## 8. Self-Feedback t+1

- **Was ich gelernt:** Ein belegter Kausalbefund wird erst dann wirksam, wenn er **im Code** als
  Sperre steht (fail-closed, Defense in Depth, an *zwei* Stellen) und durch Tests abgesichert ist,
  die ohne GPU/LLM laufen — sonst bleibt die Erkenntnis eine Doku.
- **Was unverändert bleibt:** §6 (keine Erfindung), Guardrail 7 (echte Läufe/Tests, keine Fakes),
  Guardrail 4 (keine Interface-Änderung trotz Sperre), §9.3 (zwei distinkte Personen),
  Guardrail 6 (Commit nur mit Erlaubnis), §10.3 (Flush-Semantik unangetastet).

---

## 9. Quellen

- `AGENTS.md:61-68` (§6), `:95-109` (Guardrails 1–8), `:116-124` (§9), `:165-176` (§9.1c), `:178-182` (§9.1d), `:214-234` (§9.3), `:271-276` (§10.3)
- `ergebnisse/proposals/P-132-rslora-sperre-write-back.md` (approved, §9.3 Batnini + Taoufik, 2026-10-22; Diff §3, Score §4, Drift §5, Freigabe §8)
- `ergebnisse/rekursion/132-ab-rslora-p1-bestaetigt.md` (A/B-Ergebnis §2–§7), `ergebnisse/rekursion/131-ds15-datensatz-bereitstellung-kaggle-ab.md` (Auflagen), `ergebnisse/rekursion/130-m1-m2-m3-lauf-b2-prime-messung.md`, `ergebnisse/rekursion/129-b2-prime-annahmenpruefung.md`
- Code: `kaggle/write_back_cycle.py:296-299`, `:318-333`, `:420-421`, `:442-445`, `:519-521`, `:576-598`, `:601-640` · `kaggle/train_slow_consolidation.py:55-65` · `tests/test_write_back_lora_args.py:92-170`, `:232` · `tests/test_write_back_cycle_rslora_guard.py` (neu) · `data/memory/acceptance_gate.py:114-131`
- Messartefakte (extern): HF `Batnini/knowledge-agent-write-back` → `probe/ab_2026-10-22/` (`status.json` `1098481a…`, `manifest.json` `9ceca3cd…`, `per_item.jsonl` `95ceabbc…`), `ab_rsloRa0/` (`e3be2c85…`), `ab_rslora1/` (`a595d437…`)
- arXiv:2312.03732 (rsLoRA) · arXiv:2608.22215 §3.4 (Write-Back/Slow Consolidation) · arXiv:2609.08832 (Consistency Gap) · arXiv:2607.26722 (DREvo, Evidenz-Pflicht) · arXiv:2609.36043 (SAGE)
