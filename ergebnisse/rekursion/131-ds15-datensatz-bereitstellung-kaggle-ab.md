# Rekursion 131: DS15-Bereitstellung für den kontrollierten A/B (P-131) — Datensatz-Identität hergestellt, Lauf offen

> Datum: 2026-10-22 · Gesetz: `AGENTS.md` §6 (`:61-68`), §9 (`:116-124`), §9.1d (`:178-182`),
> §9.3 (`:214-234`), §10.3 (`:271-276`), §10.7 (`:304-331`) · Guardrails 1/2/3/5/6/7 (`:97-107`)
> Status: **pending** — Beobachtung + Bereitstellung dokumentiert; **kein** Compare-Signal in dieser
> Iteration, der A/B-Lauf ist **offen**; §9-Gate für Lernen/`self_update` bleibt **deny** (1/15 = 6,7 %).
> Anlass: `ergebnisse/proposals/P-131-kontrollierter-rslora-ab.md` (`:approved`, §9.3 Batnini + Taoufik,
> 2026-10-21), Auflage 1 (`:247-252`); Vorgänger: `ergebnisse/rekursion/130-m1-m2-m3-lauf-b2-prime-messung.md`.
> Kein `self_update`, keine Änderung an Originaldateien, kein Code-Fix — nur Dokumentation + Indexzeile.
> Commit-Freigabe: **Nutzer, 2026-10-22** (Guardrail 6 `:103-104`).

---

## 1. Auftrag & Setup

- **Ziel `g`:** Die Vorbedingung des freigegebenen A/B herstellen, damit der Lauf **attribuierbar** ist:
  exakt dieselben 15 `write-new`-Fakten wie in der Baseline (`P-131:38-40`), in der Baseline-Umgebung
  (`P-131:253-256`), auf dem gefixten Klon (`P-131:257-258`) — Behandlungsvariable bleibt **allein**
  `LORA_USE_RSLORA` 0 vs. 1 (`P-131:126-138`).
- **Task-Input:** Basis `Qwen/Qwen2.5-3B-Instruct` @ Commit `aa8e72537993ba99e69dfaafa59ed015b17504d1`,
  r=64, α=256, lr 2e-4, 15 Epochen, Seed 42, `max_new_tokens=16`, `do_sample=false`
  (`P-131:38-40`; Baseline-Artefakt `wb_b2prime/kaggle_output.json`).
- **Was diese Iteration tut:** Nur die Daten- und Umgebungs-Vorbedingungen bereitstellen und den
  fehlgeschlagenen Startversuch vom 2026-10-22 als Beobachtung festhalten (§1 Beobachten ohne zu deuten,
  `AGENTS.md:19-27`). **Kein** Training, **kein** Compare, **kein** Gate-Wechsel.

---

## 2. Beobachtung (Startversuch 2026-10-22, Kaggle) — Rohbelege wörtlich

Aus dem Kaggle-Notebook-Log (T4-Session, Repo-Klon `93639e2` erfolgreich: `Cloning into
'/kaggle/working/Ata3lm'...`):

| Beobachtung | Rohbeleg |
|---|---|
| Datensatz-Datei auf Kaggle | `de24a66743ff74e2d15b2a893c4881b54fecd440239e9b6ae687e8d2f70e301d  /kaggle/working/ds15.jsonl` |
| Tokenizing train dataset | `Tokenizing train dataset: 100%\|█\| 4200000/4200000 [22:43<00:00, 3079.93 examples` |
| Truncating train dataset | `Truncating train dataset: 100%\|█\| 4200000/4200000 [06:36<00:00, 10595.58 example` |
| Trainingsfortschritt | `0%\| \| 726/3937500 [44:29<4082:47:32, 3.73s/it]` |
| torch-Build (Setup-Zelle) | `torch 2.11.0+cpu cuda False` |
| Paketstände (Setup-Zelle) | `transformers 5.16.1` · `peft 0.20.0` · `trl 1.16.0` · `datasets 4.8.5` · `accelerate 1.14.0` · `bitsandbytes 0.50.2` · `torchao 0.10.0` |

**Rechnung (Herleitung dieses Agenten, nachvollziehbar aus den Belegen):**

- 4.200.000 Zeilen × 15 Epochen ÷ (PER_DEVICE_BATCH 4 × GRAD_ACCUM 4 = 16)
  (`kaggle/train_slow_consolidation.py:55-56`, `:448-449`) = **3.937.500 Steps** — exakt die von tqdm
  gemeldete Gesamtzahl ⇒ die Zeilenzahl 4.200.000 ist die/train Dataset-Größe.
- 3,73 s/it × 3.937.500 = 14.687.000 s ≈ **4.082 h ≈ 170 Tage** (tqdm-ETA `4082:47:32`) ⇒ das
  12-h-Sessionlimit ist um Faktor ≈ 340 überschritten; schon **eine** Epoche wären
  262.500 × 3,73 s ≈ 16,3 h.
- Ursache: das Kaggle-Input-Dataset `abdelkaderbatnini/consolidation-sft` enthält den **Vollkorpus**
  (SHA `de24a667…`), nicht die M1-Datei mit 15 Items. `load_dataset_rows`
  (`kaggle/train_slow_consolidation.py:192-212`) liest die Datei **vollständig**; ein `--max-rows`-Cap
  existiert **nicht** (CLI nur `--source/--dataset/--out/--epochs/--gpu`, `:321-334`).
- Der Startversuch wurde vom Menschen abgebrochen; es entstand **kein** Adapter-Artefakt, **kein**
  Messwert, **kein** Compare.

**Bewertung (Compare, §6):** Der Startversuch verletzt Auflage 1 von P-131 wörtlich — „der hochgeladene
Stand `de24a667…` erfüllt das **nicht** ⇒ sonst kein attribuierbarer Vergleich (§6, Guardrail 5/7)"
(`P-131:247-252`). Der Lauf war damit **nicht** verwertbar; die Baseline bleibt der Vergleichspunkt
(`wb_b2prime/kaggle_output.json`: `dataset_rows: 15`, `dataset_hash_sha256: 18caaae7…`).

---

## 3. Maßnahme — DS15-Zelle (byte-identisch, hash-verifiziert)

Bereitgestellt wird **eine** Notebook-Zelle (Python, ohne `!`), die die 15-Item-Datei **aus dem
M1-Artefakt** schreibt und **fail-closed** gegen beide Baseline-Hashes prüft. Lokal verifiziert:
Ausführung erzeugt eine **byte-identische** Datei (`identical bytes: True`) und beide `assert` bestehen.

```python
import hashlib, json, pathlib
RAW = '''{"messages": [{"role": "user", "content": "What was the title that Traidenis held?"}, {"role": "assistant", "content": "Grand Duke of Lithuania"}], "hash": "fff721e2040788e3c560ebf0ede6be113bea02316caea2860d7ac53efb9609ee", "key": "what-was-the-title-that-traidenis-held", "class": "write-new", "sha256": "0ca84859894098269f5c3af597ba74a8a1207d12f45529b79b4b1d0ed5e0d664"}
{"messages": [{"role": "user", "content": "What year did Jyllands-Posten Muhammad cartoons controversy start?"}, {"role": "assistant", "content": "30 September 2005"}], "hash": "7ed26005d6eb17392c6b5ad516557e0f6ef381fec3c62cd8950c563a7013ed35", "key": "what-year-did-jyllands-posten-muhammad-cartoons-controversy-", "class": "write-new", "sha256": "cb1e9f5c51283966a2015eba21aeac7a1ffd8730fcdae665bd147377f1303cc3"}
{"messages": [{"role": "user", "content": "Who is the illustrator of Cycle of the Werewolf?"}, {"role": "assistant", "content": "Bernie Wrightson"}], "hash": "705c921ec44089981059f5d395c91143e9c72c6591f494269e3b1af5adad7e61", "key": "who-is-the-illustrator-of-cycle-of-the-werewolf", "class": "write-new", "sha256": "36ece386718a6c5945682709b46423477073e1f33798748ea5fd869cd57be991"}
{"messages": [{"role": "user", "content": "Which was the record label for Renincarnated?"}, {"role": "assistant", "content": "Villain Entertainment"}], "hash": "d3ead4f1ce02140312d4db00a9907d1f2e0c52831ddfb24e290797f726155681", "key": "which-was-the-record-label-for-renincarnated", "class": "write-new", "sha256": "17296df718f06018b119bdaee532a883294223155110b4f66b248af68657038d"}
{"messages": [{"role": "user", "content": "What team is Beau Allred affiliated with?"}, {"role": "assistant", "content": "Cleveland Indians"}], "hash": "3e3c38814056be56a72d22deab17c48c4e388636bf8f733d88de798550afa977", "key": "what-team-is-beau-allred-affiliated-with", "class": "write-new", "sha256": "379f517f5275c18e232c57654f1f434cc582e54b9dcd40c5c5474a324c324580"}
{"messages": [{"role": "user", "content": "What was Isaac Nicola's city of birth?"}, {"role": "assistant", "content": "Havana"}], "hash": "9a2e90866036a10bc18334eeb314469127a67de0b69669a770b742114e91255f", "key": "what-was-isaac-nicola-s-city-of-birth", "class": "write-new", "sha256": "448e0e834f8a40d59868289e7b39648881076d6413a7fc611c3e46079ded58f3"}
{"messages": [{"role": "user", "content": "What was the name of the city or state where KOAN Sound was formed?"}, {"role": "assistant", "content": "Bristol"}], "hash": "a32e2d23f3c1c149181aa6b84d37e5c1a292f24eefb10f51cecd65c7bd659689", "key": "what-was-the-name-of-the-city-or-state-where-koan-sound-was-", "class": "write-new", "sha256": "13d4b96b6ee361b737e22404aeecca45f322ba7d4c2c425b8f31cc85f2d3808a"}
{"messages": [{"role": "user", "content": "What person illustrated The Faraway Lurs?"}, {"role": "assistant", "content": "Harry Behn"}], "hash": "98185e874520dd154c307faa44c9423255047ca06391c1b50eac2d40d82443d2", "key": "what-person-illustrated-the-faraway-lurs", "class": "write-new", "sha256": "5458dc99346db1445e286b1bed034154082adeb2d6f281b8c79edead3075690e"}
{"messages": [{"role": "user", "content": "What is the name of the singer or writer of Odorono?"}, {"role": "assistant", "content": "Pete Townshend"}], "hash": "0df4258fa40979ab1028bb46a22e5ad484f68e76ba1ad15d73b8d9cae30f3ea5", "key": "what-is-the-name-of-the-singer-or-writer-of-odorono", "class": "write-new", "sha256": "c96dddab7d650f9fbe4598d08a86ee803b24adaf23776bcadf9c9349c8b68684"}
{"messages": [{"role": "user", "content": "What town or city does KKBB serve?"}, {"role": "assistant", "content": "Bakersfield"}], "hash": "a2ebfef45fefa1e547748a682b22bbc108f4770766cb4fbf43281c5e6c3268db", "key": "what-town-or-city-does-kkbb-serve", "class": "write-new", "sha256": "c0e997af8e806032f73f2735f6045c85f8cb9da0cdb78b0da63757e682d6ab8c"}
{"messages": [{"role": "user", "content": "At what airport can you find UTair Aviation?"}, {"role": "assistant", "content": "Khanty-Mansiysk Airport"}], "hash": "c9a99c58024bc5fd3ba38660bfd18005e71fb47fc9c0f265423a288c8c1f2dc9", "key": "at-what-airport-can-you-find-utair-aviation", "class": "write-new", "sha256": "6f413607b23094923ffe21bcef39725eb60745130d1faae86fc82f63fae5422d"}
{"messages": [{"role": "user", "content": "On what date did 40th government of Turkey end?"}, {"role": "assistant", "content": "1977"}], "hash": "bead11a2eeed353c9817b771a0c5d219299a74bd98185af351dcdb70b148e24c", "key": "on-what-date-did-40th-government-of-turkey-end", "class": "write-new", "sha256": "576c85c584f60555c2a024cbb99dfbbdb5f58c3bdcf28dbc8ea315fd46a388f3"}
{"messages": [{"role": "user", "content": "What was the production company for Getting Acquainted?"}, {"role": "assistant", "content": "Keystone Studios"}], "hash": "76a28fe90bb268f32456d29eaf86a6d66ea500fb60b46e163289e451f18f3219", "key": "what-was-the-production-company-for-getting-acquainted", "class": "write-new", "sha256": "4a4190ba1cf116e72e337aecfeaa2ad69ea2da2661be7824725d72dc8b768395"}
{"messages": [{"role": "user", "content": "What city was Christians & Lions formed in?"}, {"role": "assistant", "content": "Jamaica Plain"}], "hash": "51e3f9d2897e66310cf2b088f84799e67719d2ecfe3dd388bf3210aff682ff92", "key": "what-city-was-christians-lions-formed-in", "class": "write-new", "sha256": "52aef49f277acec8e2ce2dde852d2cabba03e624dd82675f6d8bfa0054ead5ef"}
{"messages": [{"role": "user", "content": "What year was the end of Comdial?"}, {"role": "assistant", "content": "2005"}], "hash": "0432fe557846721e8a73d439bc02bd91e2800584a1901e2baa67b1fc2f691b7d", "key": "what-year-was-the-end-of-comdial", "class": "write-new", "sha256": "a20a2b7bb0842d5cf8a0c06c626421fd51ec103925c1819a51271f2779afa730"}
'''
p = pathlib.Path('/kaggle/working/ds15.jsonl')
p.parent.mkdir(parents=True, exist_ok=True)
p.write_text(RAW, encoding='utf-8')
b = p.read_bytes()
row_agg = hashlib.sha256('\n'.join(
    hashlib.sha256(json.dumps(json.loads(l)['messages'], ensure_ascii=False, sort_keys=True, separators=(',',':')).encode('utf-8')).hexdigest()
    for l in b.decode('utf-8').splitlines() if l.strip()
).encode('utf-8')).hexdigest()
BYTE_SHA = '18caaae7c6f7f506a0cdd132d15f23c0e7044b07d894b73eb68b302605b01c7c'
ROW_AGG  = '8d42c0dab6e5face548ef0df46c1b2b64fb809f05ea395db72d4e6bf4d108ef4'
assert hashlib.sha256(b).hexdigest() == BYTE_SHA, ('byte_sha', hashlib.sha256(b).hexdigest())
assert row_agg == ROW_AGG, ('row_agg', row_agg)
assert len(b.decode('utf-8').splitlines()) == 15
print('OK rows=15 bytes=%d byte_sha=18caaae7 row_agg=8d42c0da' % len(b))
```

**Verifikationsprotokoll (lokal ausgeführt, `.venv`/System-Python, read-only):**

```
byte_sha256      : 18caaae7c6f7f506a0cdd132d15f23c0e7044b07d894b73eb68b302605b01c7c
bytes            : 5655
rows             : 15
row_agg_sha256   : 8d42c0dab6e5face548ef0df46c1b2b64fb809f05ea395db72d4e6bf4d108ef4
classes          : ['write-new']
OK rows=15 bytes=5655 byte_sha=18caaae7 row_agg=8d42c0da
identical bytes: True
```

- Quelle der Datei: M1-Artefakt `consolidation_sft.jsonl` (15 Items, `class=write-new`),
  Byte-SHA `18caaae7…` — identisch mit dem Baseline-Lauf (`wb_b2prime/kaggle_output.json`:
  `dataset_hash_sha256: 18caaae7…`, `dataset_rows: 15`).
- Das Zeilen-Aggregat `8d42c0da…` entsteht mit **derselben** Algorithmik wie im Trainingsskript
  (`kaggle/train_slow_consolidation.py:215-222` kanonische Serialisierung der `messages`,
  `:394` Aggregat) — damit ist der Vergleich **inhaltsgleich** belegt, nicht nur zeichengleich.
- Kein „skripteter/fake“ Datensatz (Guardrail 7 `:105-107`): geschrieben wird das reale M1-Artefakt,
  geprüft per SHA256; das Compare-Signal bleibt der **echte** T4-Lauf (§6 `:61-68`).

---

## 4. Anforderungs-Abgleich (P-131 §8 Auflagen)

| Auflage (`P-131:246-258`) | Ist-Stand 2026-10-22 | Beleg | Status |
|---|---|---|---|
| 1 — Datensatz byte-identisch `18caaae7…` **oder** inhaltsgleich (Digest `e481dd2f…`) | Input-Datei war `de24a667…` (4.200.000 Z.) → **verletzt**; DS15-Zelle stellt `18caaae7…`/`8d42c0da…` her | §2, §3 | **erfüllt durch DS15-Zelle** (noch nicht ausgeführt) |
| 2 — Umgebung = Baseline (transformers 5.16.1, peft 0.20.0, trl 1.16.0, bitsandbytes 0.50.2, datasets 4.8.5, accelerate 1.14.0, torch 2.11.0+cu128, torchao ≥ 0.16) | 6 von 8 Paketen deckungsgleich; `torch 2.11.0+cpu` und `torchao 0.10.0` **abweichend** | §2-Belegzeile; Baseline `wb_b2prime/kaggle_output.json:library_versions` | **offen** (Reparatur-Zelle, §8) |
| 3 — Klon aktualisiert (`git -C /kaggle/working/Ata3lm pull --ff-only`, ≥ `41348ec`) | Klon von heute (`Cloning into '/kaggle/working/Ata3lm'...`) auf `93639e2` | §2-Belegzeile; `origin/main` = `93639e2` | **erfüllt** (per `git log --oneline -1` im Notebook nachzuweisen) |

**Ehrliche Grenze:** ob im abgelaufenen Training die CUDA- oder die CPU-Build von torch verwendet wurde,
ist aus dem Log **nicht** belegbar (die Versionszeile stammt aus der Setup-Zelle, der Trainingsstart
aus einer späteren Zelle) — wird im nächsten Lauf mit `torch.__version__` **im selben Lauf** protokolliert.

---

## 5. Write-Back-Bezug (§10.3, `:271-276`)

- Die 15 Items sind `class=write-new` (verifiziert) — also genau die Fakten, die im Write-Back-Pfad
  per SFT von externem Memory in Θ konsolidiert werden (§10.7 `:316-317`).
- Der A/B ändert **nichts** am Write-Back-Pfad: keine neue Konsolidierungslogik, keine Änderung an
  `write_back_cycle.py`, kein `self_update` — so ausdrücklich als Nicht-Ziel festgelegt (`P-131:42-43`).
  Der **Flush** (Fact aus externem Memory entfernen) ist **nicht** Teil des A/B.
- Gemessen wird je Arm (§8 „Ausführung", `P-131:261-264`): regel-9-konformer Probe
  (`kaggle/m1_m2_m3_probe.py`, fail-closed mit `--expect-dataset-sha` `:152`) + Write-Back-Messung mit
  **Basis vor dem Wrap** (`kaggle/write_back_cycle.py:420-421`, `:442-445`, `passed` = `grade(adapter_answer, gold)`)
  + Canary `disable_adapter()` 15/15.
- Der Pin-Handshake des Probes ist fail-closed: `--expect-dataset-sha` (`:152`), `--expect-b2prime-sha` /
  `--expect-b2-sha` (`:153-154`), optional `--expect-base-commit` / `--expect-tokenizer-commit` (`:155-156`).

---

## 6. Score, Δ, Drift (§9.1d, `AGENTS.md:178-182`)

- **Score:** **kein neuer Score** — in dieser Iteration wurde kein Messlauf mit externem Signal
  durchgeführt (Guardrail 2 `:98`). Der Score der Baseline bleibt 1/15 = 6,7 % (`P-131:52`).
- **Δ Score:** **offen** bis zum A/B-Lauf; Erwartungswerte stehen prä-registriert in `P-131:148-169`.
- **Drift:** keine Änderung an Code oder Originaldateien ⇒ **Parameterdrift 0**, Code-Drift 0. Am
  bestehenden Artefakt `ergebnisse/rekursion/README.md` kommt **eine** Indexzeile hinzu; neu ist
  ausschließlich diese Datei. Der Drift-Bound (10 %, `:171-176`) ist damit **nicht** berührt.
- **Gate (§9 `:116-124`):** Score 6,7 % < 70 % ⇒ **deny** für Lernen/`self_update`; die Messung selbst
  bleibt erlaubt (Human-Gate + §9.3-Freigabe liegen vor, `P-131:225-231`).

---

## 7. Offene Punkte (ehrlich, §6)

1. **P-131 Auflage 2, Herleitung torchao:** Die Auflage nennt als Beleg „Baseline:
   `wb_b2prime/kaggle_output.json` `library_versions`" — im Baseline-Artefakt ist torchao **nicht**
   enthalten (dort: transformers, peft, trl, bitsandbytes, datasets, accelerate, torch). Die **Forderung**
   `torchao ≥ 0.16` bleibt gültig, belegt durch `kaggle/write_back_cycle.py:576-584` (peft v0.20.0,
   `dispatch_torchao` bei der LoRA-Injektion der Θ′-Probe) und den fail-closed Check
   `kaggle/m1_m2_m3_probe.py:192-199`; die **Herleitung im Proposal** ist zu korrigieren.
   Das Proposal ist freigegeben ⇒ **keine** stille Änderung; Korrektur nur als Erratum mit erneuter
   §9.3-Freigabe (`AGENTS.md:227-234`).
2. **Umgebungs-Reparatur torch:** `pip install --index-url …/cu128 torch` hat den Build **nicht**
   ersetzt (Log: `torch 2.11.0+cpu`). Ein In-Process-Reload scheitert (bekannter Fehler:
   `RuntimeError: Only a single TORCH_LIBRARY can be used to register the namespace triton`) ⇒
   Reparaturlauf in einer **frischen** Session bzw. nach Kernel-Neustart; Protokoll mit
   `torch.__version__` im selben Lauf.
3. **Klon-Commit-Beleg** im Notebook nachholen (`git log --oneline -1` ⇒ `93639e2`).
4. **Adapter-Rückgabe:** `/kaggle/working` wird beim Session-Ende gelöscht ⇒ beide Adapter +
   `kaggle_output.json` müssen **innerhalb derselben Session** gesichert werden, sonst kein Artefakt.

---

## 8. Nächster zulässiger Schritt (menschlich, Kaggle GPU)

Zellfolge für **einen** Arm; danach derselbe Ablauf mit `LORA_USE_RSLORA=1` (P-131:126-138, 261-264):

1. **Zelle A (Python):** DS15-Zelle aus §3 → erwartet `OK rows=15 bytes=5655 byte_sha=18caaae7 row_agg=8d42c0da`.
2. **Zelle B (Shell, frische Session/Kernel-Neustart):** `!pip install -q --force-reinstall --no-deps --index-url https://download.pytorch.org/whl/cu128 torch && pip install -q 'torchao>=0.16.0'` → danach `python -c "import torch,importlib.metadata as m;print(torch.__version__, torch.cuda.is_available(), m.version('torchao'))"` ⇒ muss `2.11.0+cu128 True` und `torchao ≥ 0.16` ergeben. Abweichungen werden **protokolliert**, nicht stillschweigend akzeptiert.
3. **Zelle C (Shell):** `!cd /kaggle/working && NUM_EPOCHS=15 LORA_R=64 LORA_ALPHA=256 LORA_USE_RSLORA=0 LEARNING_RATE=2e-4 SEED=42 BASE_MODEL=Qwen/Qwen2.5-3B-Instruct python Ata3lm/kaggle/train_slow_consolidation.py --source local --dataset /kaggle/working/ds15.jsonl --out /kaggle/working/ab_rsloRa0 --gpu 0`
   → erwartet 15 Trainingsschritte (15 Zeilen ÷ Batch 16 ⇒ 1 Schritt/Epoch × 15 Epochen) und
   `kaggle_output.json` mit `dataset_rows: 15`, `dataset_hash_sha256: 18caaae7…`, `lora_use_rslora: false`.
4. **Zelle D:** Adapter + `kaggle_output.json` sichern (HF-Upload **in derselben Session**), dann Probe
   mit `--expect-dataset-sha 18caaae7…`, `--expect-b2prime-sha <Arm-B-Gewicht-SHA>`,
   `--expect-b2-sha <Arm-A-Gewicht-SHA>`, `--repo-root /kaggle/working/Ata3lm`; Write-Back-Messung mit
   Basis vor dem Wrap; Canary 15/15.
5. **Auswertung** nach der prä-registrierten Regel (`P-131:162-169`) und Dokumentation als
   **Rekursion 132** (A/B-Ergebnis mit Rohartefakten) — Status `pending`, Gate-Neubewertung.

---

## 9. Self-Feedback t+1

- **Was ich gelernt:** Ein Vergleich ist nur dann attribuierbar, wenn **alle** Vorbedingungen vor dem
  Lauf geprüft sind. Die Datei-Identität war in `P-131:247-252` **schriftlich gefordert** und wurde im
  Startversuch nicht verifiziert; das war mein Fehler, kein Umgebungsproblem. Konsequenz: Die Prüfung
  der Vorbedingungen gehört **vor** den Lauf (Assertion in der ersten Zelle), nicht danach.
- **Was unverändert bleibt:** §6 (keine Erfindung), Guardrail 7 (echte Signale), §9.3 (zwei Personen),
  Guardrail 6 (Git nur mit Erlaubnis — hier erteilt).

---

## 10. Quellen

- `AGENTS.md:61-68` (§6), `:95-109` (Guardrails 1–8), `:116-124` (§9), `:178-182` (§9.1d), `:214-234` (§9.3), `:271-276` (§10.3), `:304-331` (§10.7)
- `ergebnisse/proposals/P-131-kontrollierter-rslora-ab.md` (approved, §9.3 Batnini + Taoufik 2026-10-21): `:38-43`, `:48-72`, `:126-142`, `:148-169`, `:180-197`, `:216-233`, `:237-264`
- `ergebnisse/rekursion/130-m1-m2-m3-lauf-b2-prime-messung.md` (Baseline-Messung, Gate deny), `ergebnisse/rekursion/129-b2-prime-annahmenpruefung.md` (A1–A4)
- Code: `kaggle/train_slow_consolidation.py:55-56`, `:192-212`, `:215-222`, `:321-334`, `:394`, `:448-449` · `kaggle/m1_m2_m3_probe.py:152-156`, `:192-199` · `kaggle/write_back_cycle.py:420-421`, `:442-445`, `:576-584`
- Gesetzestests: `tests/test_agents_law.py:46-55` (Freigabe-Status + Quelle), `:77-85` (Indexzeile Pflicht)
- Messartefakte (extern): HF `Batnini/knowledge-agent-write-back` — Baseline `probe/m1_m2_m3_2026-10-20/`
  (`status.json` `69c27db3…`, `manifest.json` `8c8697c0…`, `per_item.jsonl` `95ceabbc…`),
  Baseline-Adapter `adapter/` Revision `f704f4a12df53966095604cce824c0d7785b1446`, Kontrollarm `04ed1333…`
- Rohbelege dieser Iteration: Kaggle-Notebook-Log 2026-10-22 (in §2 wörtlich zitiert) + lokales
  Verifikationsprotokoll des M1-Artefakts (in §3 wörtlich zitiert)
