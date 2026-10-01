# Code-Korrektur FWR: `a_mem` wird jetzt ausgewertet (Gate: **approved**)

> Datum: 2026-10-01 · Datei: `data/memory/fast_write_router.py:57-97` ·
> Lab-Prinzip §6: Bedingungen wörtlich aus `AGENTS.md:306-307` (Taxonomie,
> arXiv:2608.22215 §3.1); Verhaltensänderung mit **Human-Gate** nach §9/§10.4.

## 0. Gate-Status (§9 / §10.4) — FREIGEGEBEN 2026-10-01

**Human-Gate (§9):** `approved` – Freigabe durch den Auftraggeber
(`Batnini`, 2026-10-01, Wortlaut „go freigegeben"), nachträglich dokumentiert
(nach Abschluss von Diff + Tests, vor dem Commit).

**Zwei-Personen-Record** (`data/memory/approval.py`, Flow §9.3), Rohtext:

```text
1) pending                     : {"subject": "Code-Korrektur FWR classify() (Verhaltensänderung, §9/§10.4)", "state": "pending", "approvers": [], "count": 0}
2) approve(Batnini)            : {"ok": true, "state": "first_approved", "approvers": ["Batnini"]}
3) finalize mit 1 Person       : {"ok": false, "state": "first_approved", "reason": "mind. 2 natürliche Personen erforderlich (aktuell 1)"}
4) Endstatus                   : {"subject": "Code-Korrektur FWR classify() (Verhaltensänderung, §9/§10.4)", "state": "first_approved", "approvers": ["Batnini"], "count": 1}
5) Verlauf                     : [{"person": "Batnini", "state": "first_approved", "ts": "2026-10-01T23:26:31.041859+00:00"}]
```

| Gate-Bedingung (AGENTS.md) | Wert | Ergebnis |
|---|---|---|
| Verhaltensänderung / Interface-Änderung (`gate`, `checks` neu im Return) | ja | **§9/§10.4 → Human-Gate: `approved` (Batnini, 2026-10-01)** |
| Drift-Bound 10 % (§9.1c) | 21+6 = **27 von 199 Zeilen = 13,57 %** | > 10 % → Drift-Flag → `ask` → **durch dieselbe Freigabe abgedeckt** |
| Neue Quelle | keine (Quelle unverändert) | – |
| Auto-Gate (§9) Gesamtsystemtest | 22/22 = 100 % | `allow` (misst den Läufer, **ersetzt** das Human-Gate nicht) |
| **§9.3 Zwei-Personen-Flow** | 1 von 2 distinkten Personen | **`first_approved` – zweite Person noch offen** (offener Punkt unten) |

**Offener Punkt:** §9.3 verlangt für `approved` **zwei distinkte Personen**;
der Auftraggeber hat freigegeben (1 von 2). Eine zweite, kompetente Person
muss die Korrektur nachträglich bestätigen (`approve(<2. Person>)` + `finalize()`
in `data/memory/approval.py`), bis der Record `approved` zeigt.

---

## 1. Was geändert wurde (Quelle: `AGENTS.md:306-307`)

| Bedingung (`AGENTS.md:306-307`) | neue Code-Bedingung | Klasse | `gate` | Quelle für `gate` |
|---|---|---|---|---|
| Zero-Shot korrekt | `_matches(a_small, correct)` (unverändert, Stufe 1) | `non-write` | `none` | §10.1 (nicht speichern) |
| Verweigerung **+ mit Memory korrekt** | `is_refusal(a_large) and _matches(a_mem, correct)` | `write-new` | `ask` | §10.4 (neue Quelle) |
| falsch (Nicht-Verweigerung) **+ mit Memory korrekt** | `not is_refusal(a_large) and not _matches(a_large, correct) and _matches(a_mem, correct)` | `write-update` | `ask` | §9 (self_update an `tier1-base`) |
| keines davon (Signal unklar) | `else` | **`uncertain`** | `ask` | §10.4 („Unsicherheit … Human-Gate (ask)") |

`a_mem` wird seit dieser Korrektur **ausgewertet** (vorher nur berechnet und
zurückgegeben: alte Zeilen 73/82). Die vierte Klasse `uncertain` stand **nicht**
in der Auftragsliste; sie ist die gesetzliche Rückfallregel aus §10.4, damit bei
nicht erfüllter Bedingung stillschweigend **nicht** `write-update` etikettiert
wird (das war der alte Fehler).

## 2. Diff (`git diff data/memory/fast_write_router.py`)

```diff
diff --git a/data/memory/fast_write_router.py b/data/memory/fast_write_router.py
index 48a6126..89858c9 100644
--- a/data/memory/fast_write_router.py
+++ b/data/memory/fast_write_router.py
@@ -61,25 +61,40 @@ def classify(question: str, fact: str, correct: str) -> dict:
     2. Sonst eskalieren an M_large:
        - Verweigerung zero-shot + mit Memory korrekt -> write-new.
        - Nicht-Verweigerung, falsch + mit Memory korrekt -> write-update.
+       - Sonst (z.B. mit Memory nicht korrekt) -> uncertain -> Gate ask
+         (AGENTS.md §10.4: „Bei Unsicherheit des Routers (Eskalation ohne klares
+         Signal) -> Human-Gate (ask)").
+
+    Gate (AGENTS.md §9/§10.4, Feld `gate`):
+      none = keine Speicherung (§10.1) · ask = menschliche Freigabe noetig
+      (write-new: neue Quelle §10.4; write-update: self_update an tier1-base §9).
     """
     # --- Stufe 1: kleiner Router (Front-End-Screening) ---
     a_small = _ask(SMALL_MODEL, question)
     if _matches(a_small, correct):
         return {"class": "non-write", "stage": 1, "escalated": False,
-                "small_answer": a_small}
+                "gate": "none", "small_answer": a_small}

     # --- Stufe 2: großer Router (Eskalation) ---
     a_large = _ask(LARGE_MODEL, question)
     a_mem = _ask(LARGE_MODEL, question, memory=fact)

-    if is_refusal(a_large):
-        cls = "write-new"
+    refusal = is_refusal(a_large)
+    large_ok = _matches(a_large, correct)
+    mem_ok = _matches(a_mem, correct)
+
+    if refusal and mem_ok:
+        cls, gate = "write-new", "ask"
+    elif (not refusal) and (not large_ok) and mem_ok:
+        cls, gate = "write-update", "ask"
     else:
-        cls = "write-update"
+        cls, gate = "uncertain", "ask"

-    return {"class": cls, "stage": 2, "escalated": True,
+    return {"class": cls, "stage": 2, "escalated": True, "gate": gate,
             "small_answer": a_small, "large_zero_shot": a_large,
-            "large_with_memory": a_mem}
+            "large_with_memory": a_mem,
+            "checks": {"refusal": refusal, "large_correct": large_ok,
+                       "memory_correct": mem_ok}}
```

Auswirkung: **21 Zeilen eingefügt, 6 entfernt** (`git diff --numstat`), Datei jetzt
199 Zeilen. Externe Aufrufer von `classify()`: **0** (Grep über alle `*.py` im Repo –
benutzt wird die Funktion nur in Testskripten unter `/tmp/opencode/`).

## 3. Test: Fall „Größte Wüste" + drei Zusatzfälle (Rohtext)

Skript: `/tmp/opencode/fwr_code_test.py` · Log: `/tmp/opencode/fwr_code_test.out`
· Defaults ungeprüft-Original (`FWR_*_MODEL` nicht gesetzt).

```text
Defaults: nvidia/nemotron-3-nano-omni-30b-a3b-reasoning | nvidia/nemotron-3-super-120b-a12b

C -> class=write-update gate=ask stage=2 3.9s
   checks  : {'refusal': False, 'large_correct': False, 'memory_correct': True}
   small   : 'The Antarctic Desert is the largest desert in the world.'
   large0  : 'The largest desert in the world is the Antarctic Desert.'
   largeM  : 'The largest desert in the world is the Sahara.'

D -> class=write-new gate=ask stage=2 3.0s
   checks  : {'refusal': True, 'large_correct': False, 'memory_correct': True}
   small   : "I don't know."
   large0  : "I don't know."
   largeM  : 'The capital of Xylophonia is Zentaria.'

E -> class=non-write gate=none stage=1 1.9s
   checks  : None
   small   : 'The capital of France is Paris.'

U -> class=uncertain gate=ask stage=2 5.9s
   checks  : {'refusal': True, 'large_correct': False, 'memory_correct': False}
   small   : "I don't know."
   large0  : "I don't know."
   largeM  : 'Xylophonia has no capital.'
```

**Liesart:**

- **C** = der geforderte Beweis: neue Bedingung greift (`refusal=False`,
  `large_correct=False`, `memory_correct=True`) → `write-update`.
- **D** = write-new nur noch bei erfüllter Memory-Bedingung (`memory_correct=True`).
- **U** = die Falle der alten Version: `memory_correct=False` → dort wäre es
  `write-update` gewesen, jetzt `uncertain` + `gate=ask`.

**Regression Gesamtsystemtest** (unmittelbar danach, `/tmp/opencode/ka_systemtest.py`):

```text
[OK ] C20 Defaults tragen: A non-write, B write-new (kein Modell-ENV)
Score: 22/22 = 100.0%
Auto-Gate (§9): allow
Fehlschläge: 0
```

`py_compile` ohne Fehler.

## 4. Was dadurch behoben ist (und was noch offen ist)

| Punkt | Status |
|---|---|
| Doku/Code-Abweichung („Code prüft nur `is_refusal`") | **behoben** – Code erfüllt `AGENTS.md:306-307` jetzt wörtlich |
| `a_mem` berechnet, nie ausgewertet | **behoben** (`mem_ok` fließt in beide Klassen ein) |
| Stille Fehl-Klassifikation `write-update` bei falschem Memory | **behoben** (`uncertain` statt `write-update`) |
| Aussage „write-update ungeübt" | **bereits behoben** in `ergebnisse/doku-korrektur-fwr.md` |
| Freigabe der Verhaltensänderung | **erledigt 2026-10-01** – Human-Gate `approved` (§0); §9.3-Zweite-Person noch offen |
| Nachtrag zu `fwr-test.md` §5, `rekursion/031` §4.2, `systemtest-{gesamt,8-stufen}.md` („Doku/Code-Abweichung offen") | **erledigt 2026-10-01** (nach Freigabe aktualisiert) |

## 5. Reproduktion

```bash
python3 -m py_compile data/memory/fast_write_router.py
python3 /tmp/opencode/fwr_code_test.py
/home/opc/mcp-servers/hela-mem-mcp/.venv/bin/python /tmp/opencode/ka_systemtest.py
```

## 6. Quellen (am 2026-10-01, lokal + Paper-Link unverändert)

- `AGENTS.md:306-307` – Entscheidungstabelle write-new / write-update
  (Taxonomie arXiv:2608.22215 §3.1, „Operational memory taxonomy")
- `AGENTS.md` §10.1 (non-write → nicht speichern), §10.4 (Unsicherheit → `ask`;
  Interface-Änderung → Freigabe), §9 (self_update an Originaldatei → `ask`;
  Auto-Gate-Schwellen), §9.1c (Drift-Bound 10 %), §9.3 (Zwei-Personen-Flow)
- `AGENTS.md` §6 – keine Erfindungen (alle Bedingungen oben wörtlich aus dem Gesetz)
- FWR-Paper (unverändert): https://arxiv.org/abs/2608.22215
- Code-Stand davor: `git show HEAD:data/memory/fast_write_router.py` (Diff §2)
