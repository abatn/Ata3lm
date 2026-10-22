# PROPOSAL 132 — Write-Back-Pfad: rsLoRA sperren (kausal belegter Kollaps), Lernwirkung mit Held-out-Set prüfen

> Datum: 2026-10-22 · Template: `ergebnisse/proposal-template.md`
> Gesetz: `AGENTS.md` §6 (Rohtext, `:61-68`), §9 (`:116-124`), §9.1c (`:165-176`), §9.1d (`:178-182`),
> §9.3 (`:214-234`), §10.3 (`:271-276`) · Guardrails 1/2/3/4/5/6/7 (`:97-107`)
> Status: **approved** — §9.3-Zwei-Personen-Freigabe erteilt (Batnini + Taoufik, 2026-10-22);
> Flow `pending → first_approved → second_approved → approved` (`:231`). Die Code-Änderung ist damit
> freigegeben; der Lernpfad (§9-Gate `self_update`) bleibt bis zur Umsetzung **deny**.
> Anlass: `ergebnisse/rekursion/132-ab-rslora-p1-bestaetigt.md` (A/B-Ergebnis, P-1 bestätigt),
> `ergebnisse/proposals/P-131-kontrollierter-rslora-ab.md` (freigegebener A/B, Batnini + Taoufik, 2026-10-21),
> `ergebnisse/rekursion/130-m1-m2-m3-lauf-b2-prime-messung.md` (Baseline), `ergebnisse/rekursion/129-b2-prime-annahmenpruefung.md`.
> **Ausführung: Mensch** (Code-Änderung im Repo + Kaggle-Lauf) — der Agent committet erst nach §9.3-Freigabe.

---

## 0. Metadaten

| Feld | Wert |
|---|---|
| Datum | 2026-10-22 |
| Iteration | `t → t+1` |
| Phase | Compare (externes Signal vorhanden) → Revise (Proposal) |
| Betroffenes Artefakt | `kaggle/write_back_cycle.py` (Code) · `tests/test_write_back_lora_args.py` + neu `tests/test_write_back_cycle_rslora_guard.py` (Tests) · `kaggle/README.md` (Doku) |
| Komponenten-Typ | **Code (Modelllebene-Pfad: Write-Back)** — eine Komponente (DREvo: ein Component pro Iteration, arXiv:2607.26722) |
| Autor | Knowledge-Agent (Freigabe §9.3 durch **Batnini + Taoufik**, 2026-10-22) |
| Vorherige Komponente | `P-131` (Messskript-Korrektur + A/B-Experiment) — abgeschlossen, §9.3-Freigabe 2026-10-21 |

**Warum genau eine Komponente:** Die Sperre des rsLoRA-Pfads ist der **einzige** Eingriff mit Wirkung auf
das Write-Back-Verhalten. Held-out-Set, A2-Implementierung und das P-131-Erratum sind **Mess-/Doku-Punkte**
und werden als Folgeanträge in §8 benannt, damit die Wirkung dieses Antrags attribuierbar bleibt.

---

## 1. Ziel `g`

- **Ziel:** Den Write-Back-Pfad (§10.3, `AGENTS.md:271-276`) auf die **kausal belegte** sichere
  Trainingskonfiguration festlegen (rsLoRA **aus** ⇒ α/r = 4 statt α/√r = 32) und die **Lernwirkung**
  von der **Memorization** trennbar machen (Held-out-Probe), damit der Flush (Fact aus externem Memory
  entfernen, `:275`) auf einer **belegten** Lernwirkung entscheidet statt auf Trainingsitems.
- **Task-Input (bereits gemessen, 2026-10-22, Kaggle T4):** 15 `write-new`-Fakten (SHA256 `18caaae7…`,
  Zeilen-Aggregat `8d42c0da…`), Basis `Qwen/Qwen2.5-3B-Instruct` @ `aa8e725…`, r=64, α=256, lr 2e-4,
  15 Epochen, Seed 42, `max_new_tokens=16`, `do_sample=false`.
- **Nicht-Ziel (explizit):** keine Änderung an der Fast-Write-Router-Logik, kein Eingriff in
  `data/memory/slow_consolidation.py` (Flush-Semantik), kein Eingriff in die Forschungsoption
  `LORA_USE_RSLORA` in `kaggle/train_slow_consolidation.py` (kontrollierte A/Bs bleiben möglich),
  keine neue Quelle, kein `self_update` vor §9.3-Freigabe.

---

## 2. Baseline (vorher)

| Feld | Wert |
|---|---|
| `π` (Write-Back-Pfad heute) | Basis 3B + LoRA-Adapter; **rsLoRA war im Kollaps-Lauf aktiv** (`LORA_USE_RSLORA=1` ⇒ α/√r = 32) |
| Score (externes Signal) | **1/15 = 6,7 %** strict, **Degeneration 13/15** („Jamaica") — Arm B des A/B vom 2026-10-22 (`probe/ab_2026-10-22/per_item.jsonl` SHA `95ceabbc…`, `status.json` `1098481a…`, `manifest.json` `9ceca3cd…`) |
| Gegenarm (non-rsLoRA) | **15/15 = 100 %**, keine Degeneration (top_count 1/15) — Arm A (`ab_rsloRa0/adapter/adapter_model.safetensors` SHA `e3be2c85…`, `kaggle_output.json` `b49a5d0b…`, Loss 1,310697078704834) |
| Referenz-Basis | 0/15 (Basis kennt die 15 Gold-Texte nicht — Sollzustand des Write-Pfads, `AGENTS.md:250`, `:316-317`) |
| Modell-Drift π → π′ | `‖π′−π‖/‖π‖` = **0,936747 (93,7 %)** (aus den ΔW-Matrizen beider Arme, 252 Paare, 0 nonfinite) — Rek 132 §5 |
| Konfigurationsbeleg | `kaggle/write_back_cycle.py:328-329` setzt `LORA_USE_RSLORA=1`, wenn `--use-rslora` (CLI `:519-521`, Default `False`); der Kollaps-Lauf nutzte die Option ⇒ rsLoRA war **nur** in diesem Pfad wirksam |

**Belastbarkeitsgrenze der Baseline (§6, nicht verschwiegen):** Alle 15 Items sind **Trainingszeilen**
⇒ 15/15 belegt **Memorization**, nicht Generalisierung (`manifest.json:grenzen[0]`, `grenzen[1]`).

---

## 3. Änderung (Diff, line-level)

### 3a. `kaggle/write_back_cycle.py` — rsLoRA im Write-Back-Pfad fail-closed sperren

```diff
@@ kaggle/write_back_cycle.py:576-598 (nach _torchao_incompatible) @@
+def _rslora_blocked() -> Optional[str]:
+    """rsLoRA im Write-Back-Zyklus ist gesperrt (P-132; Belege: Rek 132 §4).
+
+    Quelle (Belegt): kontrollierter A/B (P-131, Lauf 2026-10-22) — identischer Code/Daten/Seed/
+    Umgebung, einzige Variable `LORA_USE_RSLORA`: Arm rsLoRA (α/√r = 32) → 1/15 = 6,7 % mit
+    Degeneration 13/15 "Jamaica"; Arm non-rsLoRA (α/r = 4) → 15/15 ohne Degeneration.
+    Belege: ergebnisse/rekursion/132-ab-rslora-p1-bestaetigt.md; HF `Batnini/knowledge-agent-write-back`
+    → `probe/ab_2026-10-22/`.
+    Für kontrollierte Forschung bleibt ENV `LORA_USE_RSLORA` in `kaggle/train_slow_consolidation.py`
+    verfügbar (dort ohne Write-Back-Flush).
+    """
+    return (
+        "rsLoRA (--use-rslora) ist im Write-Back-Zyklus gesperrt (P-132): der kontrollierte A/B "
+        "(P-131, Lauf 2026-10-22) belegt den Kollaps kausal – Arm rsLoRA (α/√r=32) 1/15 = 6,7 % mit "
+        "Degeneration 13/15 'Jamaica', Arm non-rsLoRA (α/r=4) 15/15 ohne Degeneration bei identischen "
+        "Daten/Code/Seed/Umgebung (Rek 132 §4). Für kontrollierte Forschung: ENV LORA_USE_RSLORA in "
+        "kaggle/train_slow_consolidation.py (dort ohne Write-Back-Flush)."
+    )
+
@@ kaggle/write_back_cycle.py:600-602 (main) @@
 def main(argv=None) -> int:
     args = _parse_args(argv)
+    # P-132: fail-closed vor jedem Seiteneffekt (kein LLM-/GPU-ENV, kein Training).
+    if args.use_rslora:
+        print(f"FEHLER: {_rslora_blocked()}", file=sys.stderr)
+        return 1
@@ kaggle/write_back_cycle.py:328-329 (_make_train_fn) @@
-        if use_rslora:
-            env["LORA_USE_RSLORA"] = "1"
+        if use_rslora:
+            # P-132: Defense in Depth – der Write-Back-Pfad setzt rsLoRA nicht.
+            raise RuntimeError(_rslora_blocked())
```

**Begründung je Hunk:** (i) *Guard vor allen Seiteneffekten* — der Lauf bricht ab, bevor LLM-/GPU-ENV
gesetzt oder ein Training gestartet wird (fail-closed, kein stiller Ersatz durch eine andere
Konfiguration); (ii) *Defense in Depth* in `_make_train_fn` — selbst bei Umgehung des `main`-Guards
wird `LORA_USE_RSLORA` **nicht** gesetzt, sondern geworfen (kein „stiller Fallback"); (iii) **keine
Signatur- und keine CLI-Änderung** — `--use-rslora` bleibt als Flag existieren (Guardrail 4, `:100`),
damit alte Aufrufe eine **verständliche** Fehlermeldung bekommen statt eines `unrecognized arguments`-Fehlers;
(iv) die **Forschungsoption bleibt**: `kaggle/train_slow_consolidation.py:63` liest `LORA_USE_RSLORA`
unverändert ⇒ kontrollierte A/Bs (inkl. Replikation von P-131) bleiben möglich.

### 3b. Tests

```diff
--- a/tests/test_write_back_lora_args.py
+++ b/tests/test_write_back_lora_args.py
@@ test_wbc_train_fn_sets_env_when_args_provided @@
-def test_wbc_train_fn_sets_env_when_args_provided(tmp_path):
-    """ENV wird gesetzt, wenn Args explizit übergeben werden."""
+def test_wbc_train_fn_sets_env_when_args_provided(tmp_path):
+    """ENV wird gesetzt, wenn Args explizit übergeben werden (rsLoRA gesperrt, P-132)."""
@@ Aufruf @@
-        use_rslora=True,
+        use_rslora=False,
@@ Assertions @@
-    assert captured_env["LORA_USE_RSLORA"] == "1"
+    assert "LORA_USE_RSLORA" not in captured_env
```

Neu: `tests/test_write_back_cycle_rslora_guard.py` (3 Tests, ohne GPU/LLM):
1. `_rslora_blocked()` liefert eine nicht-leere Meldung mit Verweis „P-132" und den Zahlen 1/15, 15/15.
2. `main(["--use-rslora"])` ⇒ Rückgabewert `1`, Meldung „FEHLER:" auf stderr (fail-closed **vor**
   LLM-/GPU-Prüfung ⇒ ohne GPU/LLM testbar).
3. `_make_train_fn(..., use_rslora=True)` ⇒ `RuntimeError` mit derselben Meldung **und** kein
   `LORA_USE_RSLORA` im ENV (Defense in Depth).
   Zusätzlich (bestehender Test bleibt): `kaggle/train_slow_consolidation.py` liest weiterhin
   `LORA_USE_RSLORA` (Forschungspfad unberührt) — `tests/test_write_back_lora_args.py:232`.

### 3c. Doku

```diff
--- a/kaggle/README.md
+++ b/kaggle/README.md
@@ Write-Back-Abschnitt @@
+> **P-132 (2026-10-22):** rsLoRA (`--use-rslora` / ENV `LORA_USE_RSLORA`) ist im **Write-Back-Zyklus**
+> (`kaggle/write_back_cycle.py`) **gesperrt** (fail-closed). Beleg: kontrollierter A/B (P-131, Lauf
+> 2026-10-22) — rsLoRA (α/√r = 32) ⇒ 1/15 = 6,7 % + Degeneration 13/15, non-rsLoRA (α/r = 4) ⇒ 15/15,
+> bei identischen Daten/Code/Seed/Umgebung (Rek 132 §4). Für kontrollierte Forschung bleibt ENV
+> `LORA_USE_RSLORA` in `kaggle/train_slow_consolidation.py` verfügbar.
```

- **Geänderte Komponenten:** 1 (Modelllebene-Pfad) + Tests/Doku zu derselben Komponente.
- **Interface-Änderung?** **nein** — keine Signatur, kein CLI-Flag, kein JSON-Schema geändert
  (Guardrail 4 erfüllt); `--use-rslora` existiert weiter, wird aber abgelehnt.

---

## 4. Score-Änderung (§9.1d)

| Testfall | Kriterium | vorher | nachher |
|---|---|---|---|
| 1 | adapter-seitiger strict-Score des Write-Back-Pfads | **1/15 = 6,7 %** (rsLoRA-Lauf 2026-10-22, `probe/ab_2026-10-22/`) | **15/15 = 100 %** (non-rsLoRA-Lauf 2026-10-22, `ab_rsloRa0/`) — **gemessen**, nicht erwartet |
| 2 | Degenerationsflag des Write-Back-Adapters | **true** (13/15 identische Antwort „Jamaica") | **false** (top_count 1/15) — **gemessen** |
| 3 | Modell-Drift π → π′ (Wechsel der Konfiguration) | — | **93,7 %** (Rek 132 §5) ⇒ §9.1c **ask** |
| 4 | `make test` nach der Code-Änderung | 857 passed, 1 skipped, Coverage 100,00 % | **Erwartung**: 857 + 3 passed, 1 skipped, Coverage 100,00 % (kein Regression) |

- **Score vorher:** 1/15 = **6,7 %** (externes Signal: echter Kaggle-T4-Lauf, HF-Artefakte, unabhängig
  nachgerechnet mit `data/memory/acceptance_gate.py:114-131`, Rek 132 §3).
- **Score nachher:** 15/15 = **100 %** — **gemessen** am 2026-10-22 (Arm A desselben A/B, identische
  Daten/Code/Seed/Umgebung; `ab_rsloRa0/kaggle_output.json` SHA `b49a5d0b…`, Loss 1,310697078704834;
  `ab_rsloRa0/adapter/adapter_model.safetensors` SHA `e3be2c85…`).
- **Δ Score:** **+93,3 pp** (6,7 % → 100 %).
- **Durchbruch der §9-Schwelle (`:118`)** — **aber kein automatisches allow**: §9 verlangt zusätzlich
  „alle 8 Stufen melden 'sicher'"; der 8-Stufen-Zyklus (`AGENTS.md:36-43`) wurde für den Write-Back-Lauf
  **nicht** abgearbeitet, und die 15 Items sind Trainingsitems (Memorization, §2) ⇒ **menschliches Gate**.

---

## 5. Drift (Δ zur Baseline)

- **Definition (Auftrag, praktische Messung):** `Δ = geänderte Zeilen / Gesamtzeilen des Artefakts`
  (line-level, DREvo arXiv:2607.26722, `AGENTS.md:178-182`).
- **Code/Doku (Planwerte, nach Umsetzung exakt nachzurechnen):**

  | Artefakt | geänderte Zeilen | Gesamtzeilen | Δ |
  |---|---|---|---|
  | `kaggle/write_back_cycle.py` | +27 / −1 | 806 | **3,35 %** |
  | `tests/test_write_back_lora_args.py` | +4 / −3 | 262 | **2,67 %** |
  | `tests/test_write_back_cycle_rslora_guard.py` (neu) | +90 | 0 → 90 | neue Datei |
  | `kaggle/README.md` | +9 / −0 | 323 | **2,79 %** |
  | **Gesamt (Code/Tests/Doku, ohne neue Datei)** | **+40 / −4** | **1391** | **3,02 %** |
  | **Gesamt inkl. neuer Testdatei** | **+130 / −4** | **1481** | **9,05 %** |

  **Ist-Messung nach der Umsetzung** (`git diff --numstat`, 2026-10-22): die Tabelle enthält die
  **gemessenen** Werte; die Planwerte der Antragsfassung (+24/−2, +3/−2, +6, +~45) sind damit
  überholt. Der Gesamt-Drift **einschließlich** der neuen Testdatei liegt mit 9,05 % **unter** dem
  10-%-Bound (`AGENTS.md:171-176`); ohne die neue Datei sind es 3,02 %.

  ⇒ **unter** dem Drift-Bound 10 % (`AGENTS.md:171-176`) — **kein** §9.1c-Auslöser durch Code.
- **Drift Modell-Parameter:** Der Eingriff **trainiert nichts**, erzeugt also keine neue Parameterdrift.
  Der **Konfigurationswechsel** π (rsLoRA) → π′ (non-rsLoRA) hat `‖π′−π‖/‖π‖` = **93,7 %**
  (Rek 132 §5) ⇒ **> 10 % ⇒ Human-Gate (ask)**, `AGENTS.md:124`, `:193-195` in `P-131`.
- **Hinweis:** Die Code-Änderung selbst erzeugt **keine** Parameterdrift — sie verhindert nur die
  Verwendung der schädlichen Konfiguration.

---

## 6. Evidenz / Quellen

- arXiv:2312.03732 — rsLoRA (Skalierung α/√r statt α/r; `use_rslora`) — https://arxiv.org/abs/2312.03732
- arXiv:2608.22215 §3.4 — Write-Back / Slow Consolidation (Θ → Θ′; Flush-Regel) — https://arxiv.org/abs/2608.22215
- arXiv:2609.08832 — Consistency Gap (Compare nur mit externem Signal) — https://arxiv.org/abs/2609.08832
- arXiv:2607.26722 — DREvo (function-level evidence anchoring, line-level diff) — https://arxiv.org/abs/2607.26722
- arXiv:2609.36043 — SAGE (Grader-/Referenz-Logik, Base-Rate-Guard) — https://arxiv.org/abs/2609.36043
- Code: `kaggle/write_back_cycle.py:296-299`, `:318-333`, `:519-521`, `:576-598`, `:600-640` ·
  `kaggle/train_slow_consolidation.py:55-65`, `:433-438` · `tests/test_write_back_lora_args.py:92-170`, `:232` ·
  `data/memory/acceptance_gate.py:114-131` · `data/memory/slow_consolidation.py` (Flush)
- Interne Referenz: `ergebnisse/rekursion/132-ab-rslora-p1-bestaetigt.md` (§3 unabhängige Nachrechnung,
  §4 Befund + Skriptentscheidung, §5 Drift), `ergebnisse/rekursion/131-ds15-datensatz-bereitstellung-kaggle-ab.md`
  (Auflagen), `ergebnisse/rekursion/130-m1-m2-m3-lauf-b2-prime-messung.md`, `ergebnisse/rekursion/129-b2-prime-annahmenpruefung.md`,
  `ergebnisse/proposals/P-131-kontrollierter-rslora-ab.md`
- Messartefakte (extern): HF `Batnini/knowledge-agent-write-back` → `probe/ab_2026-10-22/`
  (`status.json` `1098481a…`, `manifest.json` `9ceca3cd…`, `per_item.jsonl` `95ceabbc…`),
  `ab_rsloRa0/{adapter/adapter_model.safetensors e3be2c85…, adapter/adapter_config.json 56cc999b…,
  kaggle_output.json b49a5d0b…}`, `ab_rslora1/{adapter/adapter_model.safetensors a595d437…,
  adapter/adapter_config.json 3df21013…, kaggle_output.json c9feeccf…}`

---

## 7. Gate-Entscheidung (§9)

| Bedingung | Wert | Ergebnis |
|---|---|---|
| Score | 6,7 % → **100 %** (Δ +93,3 pp) | kein automatisches allow (8 Stufen nicht abgearbeitet; Memorization) |
| Score < 70 % (`:120`) | betrifft die **alte** rsLoRA-Konfiguration | **deny** für rsLoRA |
| Neue Quelle? | nein (arXiv:2312.03732, 2608.22215, 2609.08832, 2607.26722, 2609.36043 stehen in `AGENTS.md:393-411`) | — |
| Interface-Änderung? | nein (Signatur/CLI/JSON unverändert) | — |
| self_update an Originaldatei (`:123`) | **ja** (`kaggle/write_back_cycle.py` + Tests + Doku) | **immer menschliches Gate (ask)** |
| Drift ≤ Bound (`:124`, `:171-176`)? | Code 6,05 % ≤ 10 %; **Modell 93,7 % > 10 %** | **ask** |

- **Gate-Ergebnis: `ask`** — erforderlich: (1) **Human-Gate** des Nutzers (dieses Proposal),
  (2) **§9.3-Zwei-Personen-Freigabe** (mind. 2 distinkte Personen: Batnini + Taoufik; Flow
  `pending → first_approved → second_approved → approved`, `AGENTS.md:227-234`),
  (3) **kein** Commit und **kein** `self_update` vor dieser Freigabe.
- **Lernpfad (§9 `self_update`):** bleibt **deny** bis die menschliche Entscheidung über den
  Write-Back-Pfad vorliegt; dieser Antrag ändert **nicht** das Gate für Lernen aus sich heraus.

---

## 8. Freigabe

- **Status:** `approved` — Flow `pending → first_approved → second_approved → approved` (`AGENTS.md:231`):
  **first_approved: Batnini**, **second_approved: Taoufik**, 2026-10-22
  (2 distinkte Personen ✓, `AGENTS.md:233-234`).
- **Human-Gate-Referenz:** `ergebnisse/rekursion/132-ab-rslora-p1-bestaetigt.md`,
  `ergebnisse/rekursion/130-m1-m2-m3-lauf-b2-prime-messung.md`,
  `ergebnisse/rekursion/129-b2-prime-annahmenpruefung.md`
- **§9.3:** **gestartet und abgeschlossen** (2026-10-22) — die Freigabe deckt **die Code-Änderung**
  (rsLoRA-Sperre im Write-Back-Zyklus + Tests + Doku) und deren **Umsetzung + Commit**; sie deckt
  **nicht** das `self_update`/Lernen (Gate `deny` bleibt, §7).
- **Umsetzung (menschlich):** Diff §3 anwenden → `make test` (Erwartung §4 Testfall 4) → Commit mit
  Freigabe-Status → Kaggle-Lauf des Write-Back-Zyklus **ohne** `--use-rslora` (Laufprotokoll als
  Folgeantrag/Rekursion).
- **Nicht Teil dieses Antrags (bewusst, §0 „eine Komponente"):** (a) Implementierung der A2-Auswertungsregel
  in `kaggle/m1_m2_m3_probe.py` (Messung, kein Modell-Eingriff) — Folgeantrag; (b) **Held-out-Probe-Set**
  zur Trennung von Memorization und Lernwirkung (M3-Ceiling) — Folgeantrag mit eigenem Datensatz;
  (c) **Erratum** zur torchao-Herkunft in `P-131:253-256` (torchao steht nicht im Baseline-`library_versions`)
  — Korrektur am freigegebenen Proposal, eigene §9.3-Freigabe.

### Pflichtfelder (Kurzcheck)

- [x] Score vorher/nachher mit externem Signal (nachher = **gemessener** Wert des Kontrollarms, als solcher markiert)
- [x] Diff (line-level) — §3a Code, §3b Tests, §3c Doku
- [x] Drift-Wert + Bound-Vergleich — §5 (Code 6,05 %; Modell 93,7 % ⇒ ask)
- [x] Quelle(n) mit Link — §6 (arXiv + Code + HF-Artefakte)
- [x] Gate-Ergebnis + Freigabe-Status — §7 (`ask`), §8 (`approved`: Batnini + Taoufik, 2026-10-22, §9.3)
