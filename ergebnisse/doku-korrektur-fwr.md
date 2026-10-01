# Doku-Korrektur FWR: „write-update ungeübt" → „geübt – siehe Beweis"

> Datum: 2026-10-01 · Anlass: Nutzer-Prüfung · Lab-Prinzip §6 (keine Erfindungen –
> nur nachstehende Rohtexte, wörtlich aus den Dateien/Logs.)

## 0. Was korrigiert wurde

| Behauptung (vorher) | Prüfung | Behauptung (nachher) |
|---|---|---|
| „`write-update`-Klasse ungeübt – die Modelle verweigern immer" (`systemtest-gesamt.md`, `systemtest-8-stufen.md`, `rekursion/031-fwr-modell.md`) | Fall C „Größte Wüste der Welt?" mit den aktuellen Defaults **frisch ausgeführt**: `class=write-update stage=2` | **geübt – siehe Beweis** (§2 unten) |
| „Doku sagt ‚zero-shot falsch + mit Memory korrekt', Code prüft nur `is_refusal(a_large)`" | Codezeilen gelesen (`fast_write_router.py:67`, `:75-78`, `a_mem` nur `:73`/`:82`) | **bleibt bestehen** (§5 unten) |

Nicht geändert (bewusst): `ergebnisse/fwr-test.md` §5 – dort steht „wurde **in
diesem Lauf** nicht erreicht", was für genau diesen Lauf korrekt ist (dort lief
dieselbe Frage mit `correct="Antarctic Desert"` → `non-write`). Die
Verallgemeinerung stand in den drei oben genannten Dateien.

---

## 1. Rohtexte aus `ergebnisse/fast-write-router.md:70-78` (wörtlich)

```text
| A | „Hauptstadt von Frankreich?" | „Paris" (korrekt) | **non-write** | nur Historie (keine Eskalation) |
| B | „Hauptstadt von Xylophonia?" | „I don't know" → eskaliert | **write-new** | `structured/` + `tier3-working/` |
| C | „Größte Wüste der Welt?" | „Antarctic Desert" (konfident) → eskaliert | **write-update** | `structured/` überschreiben + `tier1-base` supersedieren |

**Rohe Modell-Ausgaben:**
A: small="The capital of France is Paris."            -> non-write (Stufe 1)
B: small="I don't know" | large0="I don't know." | largeM="…Xylophonia is Zentaria."  -> write-new
C: small="…Antarctic Desert…" | large0="…Antarctic Desert." | largeM="…the Sahara."     -> write-update
```

(Zeilen 70–72 = Tabelle §4, Zeilen 76–78 = Codeblock „Rohe Modell-Ausgaben".)

---

## 2. Nachlauf 2026-10-01 – Rohtext (aktuelle Defaults, kein ENV-Override)

Skript: `/tmp/opencode/fwr_writeupdate.py` · Ausgabe: `/tmp/opencode/writeupdate.out`
· Fall C identisch zu `data/memory/fast_write_router.py:176-177`
(`correct="Sahara"`).

```text
Defaults: nvidia/nemotron-3-nano-omni-30b-a3b-reasoning | nvidia/nemotron-3-super-120b-a12b

C -> class=write-update stage=2 11.8s
   small  : 'The Antarctic Desert is the largest desert in the world.'
   large0 : 'The largest desert in the world is the Antarctic Desert.'  is_refusal=False
   largeM : 'The largest desert in the world is the Sahara.'  match=True

D -> class=write-new stage=2 3.3s
   small  : "I don't know."
   large0 : "I don't know."  is_refusal=True
   largeM : 'The capital of Xylophonia is Zentaria.'  match=True

E -> class=non-write stage=1 2.9s
   small  : 'Paris.'
```

**Beweis:** `C → class=write-update stage=2` – die Klasse wird erreicht, weil
`large0` **nicht** verweigert (`is_refusal=False`).

**Warum dieselbe Frage in `fwr-test.md` §4 als `non-write` landete:** dort war
`correct="Antarctic Desert"` (Quelle: `/tmp/opencode/fwr_final.py:18`
`("C", B+"What is the largest desert in the world?", "-", "Antarctic Desert")`) –
die small-Antwort „The Antarctic Desert is the largest desert in the world."
enthielt diesen String und beendete den Lauf auf Stufe 1. Mit `correct="Sahara"`
(laut `fast_write_router.py:177`) eskaliert derselbe Fall und wird zu
`write-update`. Beide Messungen sind wahr, weil `correct` verschieden war.

---

## 3. Diff (unified, `diff -u`)

Vorher-Kopien: `/tmp/opencode/before/{systemtest-gesamt,systemtest-8-stufen,031-fwr-modell}.md`
(bzw. `fwr-test.md`, unverändert).

```diff
--- /tmp/opencode/before/systemtest-gesamt.md
+++ ergebnisse/systemtest-gesamt.md
@@ -406,7 +406,7 @@
 3. **Parallel-Limit des Endpoints:** bei 8 gleichzeitigen Anfragen 503/Timeout (Worker-Limit 16/16); sequenziell stabil.
-4. **`write-update`-Klasse des FWR** ist weiterhin ungeübt (Modelle verweigern statt falsch zu antworten).
+4. **`write-update`-Klasse des FWR: geübt – siehe Beweis.** Fall C „Größte Wüste der Welt?“ (`correct="Sahara"`) liefert `write-update`; Rohtexte in `ergebnisse/fast-write-router.md:70-78`, Nachlauf 2026-10-01 mit den aktuellen Defaults in `ergebnisse/doku-korrektur-fwr.md`. In `fwr-test.md` §4 stand derselbe Fragenwortlaut mit `correct="Antarctic Desert"` und wurde deshalb zu `non-write` – die Aussage „ungeübt“ war falsch.
 5. **Doku/Code-Abweichung** `fast_write_router.py` (Doku „zero-shot falsch“, Code prüft `is_refusal`).

--- /tmp/opencode/before/systemtest-8-stufen.md
+++ ergebnisse/systemtest-8-stufen.md
@@ -219,7 +219,7 @@
 ## Offene Punkte (bewusst nicht gefixt)

-- **`write-update`-Klasse des Fast Write Routers wurde nicht geübt** – die getesteten Modelle verweigern (→ `write-new`) statt falsch zu antworten (→ `write-update`); siehe `ergebnisse/fwr-test.md` §5.
+- **`write-update`-Klasse des Fast Write Routers: geübt – siehe Beweis.** Fall C „Größte Wüste der Welt?“ (`correct="Sahara"`) → `write-update`; Rohtexte in `ergebnisse/fast-write-router.md:70-78`, Nachlauf 2026-10-01 in `ergebnisse/doku-korrektur-fwr.md`. In diesem Systemtest-Lauf kam C nicht vor (Szenarien A/B); in `fwr-test.md` §4 lief dieselbe Frage mit `correct="Antarctic Desert"` → `non-write`.

--- /tmp/opencode/before/031-fwr-modell.md
+++ ergebnisse/rekursion/031-fwr-modell.md
@@ -53,8 +53,16 @@
 ## 4. Befunde ohne Code-Fix (bewusst offen)

-1. **`write-update` wurde nicht geübt** – beide Modelle verweigern statt falsch zu
-   antworten; der Branch blieb in diesem Lauf unbenutzt.
+1. ~~`write-update` wurde nicht geübt~~ → **korrigiert 2026-10-01: `write-update`
+   ist geübt – siehe Beweis.** Fall C „Größte Wüste der Welt?“ (`correct="Sahara"`,
+   `fast_write_router.py:176-177`) liefert mit den aktuellen Defaults
+   `class=write-update stage=2`. Rohtexte: `ergebnisse/fast-write-router.md:70-78`;
+   Nachlauf 2026-10-01 (small `The Antarctic Desert is the largest desert in the
+   world.` · large0 nicht-verweigernd falsch · largeM `The largest desert in the
+   world is the Sahara.`): `ergebnisse/doku-korrektur-fwr.md`.
+   In *dieser* Iteration kam C nicht vor (dort liefen A/B/D/E/F/G);
+   `fwr-test.md` §4 nutzte für dieselbe Frage `correct="Antarctic Desert"` →
+   `non-write`.
 2. **Doku-Code-Abweichung**: Docstring/`fast-write-router.md` verlangen für
    `write-update` „zero-shot falsch + mit Memory korrekt"; der Code prüft nur
    `is_refusal(a_large)`. Korrektur = Verhaltensänderung → eigenes Gate nötig.
@@ -85,10 +93,11 @@
 ## 8. Nächstes Self-Feedback (t+1)

-- `write-update`-Fall gezielt erzeugen (Fixture, bei der das große Modell
-  nicht-verweigernd falsch antwortet) – oder die Doku-Code-Abweichung (§4.2) per
-  Gate schließen.
-- `ergebnisse/versionierung.md` §4 um den Eintrag `versions/v4` ergänzen.
+- ~~`write-update`-Fall gezielt erzeugen~~ → **erledigt 2026-10-01** (natürlich
+  reproduzierbar, siehe §4.1) – übrig bleibt nur die Doku-Code-Abweichung (§4,
+  Punkt 2), die ein eigenes Gate (§9) braucht.
+- ~~`ergebnisse/versionierung.md` §4 um den Eintrag `versions/v4` ergänzen~~ →
+  **erledigt 2026-10-01** (Zeile in §4 vorhanden).
```

Außerdem: `data/memory/fast_write_router.py` unverändert (kein Code-Fix);
`ergebnisse/fwr-test.md` unverändert (laufbezogen korrekt).

---

## 4. Was weiterhin offen ist (unverändert, ehrlich)

**Doku-Code-Abweichung** – geprüft an den Zeilen:

| Stelle | Text / Code |
|---|---|
| `AGENTS.md:306` | `Verweigerung + mit Memory korrekt` → `write-new` |
| `AGENTS.md:307` | `falsch (Nicht-Verweigerung) + mit Memory korrekt` → `write-update` |
| `fast_write_router.py:62-63` (Docstring) | „Verweigerung zero-shot + mit Memory korrekt → write-new"; „Nicht-Verweigerung, falsch + mit Memory korrekt → write-update" |
| `fast_write_router.py:75-78` (Code) | `if is_refusal(a_large): cls = "write-new"` / `else: cls = "write-update"` |
| `fast_write_router.py:67` | `_matches(...)` wird **nur** für Stufe 1 benutzt |
| `fast_write_router.py:73, 82` | `a_mem` wird berechnet und zurückgegeben, **aber nie ausgewertet** |

Damit prüft der Code nur „verweigert ja/nein" und nicht „falsch" und nicht
„mit Memory korrekt". Eine Codekorrektur ist eine **Verhaltensänderung** →
§9 Human-Gate (`ask`) erforderlich; daher in dieser Iteration **kein Code-Fix**.

---

## 5. Reproduktion

```bash
python3 /tmp/opencode/fwr_writeupdate.py
# erwartet: C -> class=write-update stage=2
```

Rohtexte von §1 stammen aus `ergebnisse/fast-write-router.md` (Datei unverändert),
Rohtexte von §2 aus `/tmp/opencode/writeupdate.out`.

## 6. Quellen (am 2026-10-01)

- `ergebnisse/fast-write-router.md:70-78` (lokale Datei, unverändert)
- `data/memory/fast_write_router.py:67`, `:73`, `:75-78`, `:82`, `:176-177`
- `/tmp/opencode/fwr_final.py:18` (Skript des 031-Laufs)
- `/tmp/opencode/fwr_writeupdate.py` + `/tmp/opencode/writeupdate.out` (Nachlauf)
- `AGENTS.md:306-307` (§10.7 Taxonomie)
- Keine neuen Papers; Endpunkt-Messung derselbe wie in
  `ergebnisse/systemtest-gesamt.md` (`GET /v1/models` → HTTP 200,
  `POST /chat/completions` → HTTP 200, 2026-10-01 geprüft)
