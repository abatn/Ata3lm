# Heuristik entfernt: NOOP statt Faustregel (Rekursion 032, Nachtrag)

> Datum: 2026-10-01 · Auftrag: „Entferne die Heuristik aus
> `data/memory/reflective_agent.py` und ersetze sie durch NOOP – nach SEAA
> (arXiv:2609.17331) und Mem0-Pattern. … Keine Heuristik, kein Default – die
> Matrix muss vom LLM kommen." · Lab-Prinzip §6: nur was in den Dateien steht
> oder durch die Quelle belegt ist.

## 1. Was entfernt wurde (wörtlich, vorher)

`parse_transition_delta` endete mit einer Faustregel, die eine Matrix **erfand**,
wenn das LLM nichts Gültiges lieferte:

```text
101:     # Heuristik (Auftrag): negative Reflexion -> Diagonale senken (weniger Trägheit)
102:     neg = any(w in text.lower() for w in ["falsch", "wrong", "fehler", "error", "failed", "bug"])
103:     sign = -1.0 if neg else 1.0
104:     np.fill_diagonal(delta, sign * 0.4)
105:     for i in range(k):
106:         for j in range(k):
107:             if i != j:
108:                 delta[i, j] = -sign * 0.4 / (k - 1)
109:     return delta
```

Diese Zeilen sind **ersatzlos gestrichen** – es gibt keine Regel, keinen
Default-Wert und keine Ersatz-Matrix mehr.

## 2. Was jetzt passiert (NOOP)

`parse_transition_delta(text, k)` liefert die Matrix **nur noch vom LLM** und
sonst `None`:

| Fall | vorher | jetzt |
|---|---|---|
| kein `OPENAI_API_KEY` | Heuristik-Matrix | `None` (NOOP) |
| LLM-Antwort ohne JSON | Heuristik-Matrix | `None` (NOOP) |
| Matrix-Form ≠ K×K | IndexError / Heuristik | `None` (NOOP) |
| LLM-Fehler/Exception | Heuristik-Matrix | `None` (NOOP) |
| gültige K×K-Matrix | übernommen | übernommen |

`HMMInertia.update_from_reflection` überspringt bei `None` das Update:

```python
delta = parse_transition_delta(text, self.K)
if delta is None:
    return {"before": self.P.tolist(), "after": self.P.tolist(),
            "delta": None, "lr": self.lr,
            "skipped": True, "note": HMM_NOOP_NOTE}
```

**Log-Meldung (wörtlich, wie beauftragt):**

```text
HMM-Update übersprungen (keine LLM-Matrix)
```

Sie steht als Modulkonstante `HMM_NOOP_NOTE` im Code
(`data/memory/reflective_agent.py`) und erscheint im Rückgabe-Dict als `note`
sowie in `simulate_3_reflections()` pro Reflexion.

## 3. Rohtext-Beweis (kein LLM-Key)

```text
$ python3 - (OPENAI_API_KEY entfernt)
NOOP-Beweis (kein LLM-Key):
  skipped : True
  delta   : None
  note    : HMM-Update übersprungen (keine LLM-Matrix)
  P unveraendert: True
  parse_transition_delta -> None
```

Kein Update, kein Crash, keine erfundene Matrix.

## 4. Diff (Kern)

```diff
-    import numpy as np
-    delta = np.zeros((k, k))
-    key = os.environ.get("OPENAI_API_KEY")
-    if key:
-        try:
+    import numpy as np
+    key = os.environ.get("OPENAI_API_KEY")
+    if not key:
+        return None                                  # NOOP: ohne LLM keine Matrix
+    try:
             ...
-            m = re.search(r"\[[\s\S]*\]", raw)
-            if m:
-                candidate = np.array(json.loads(m.group(0)), dtype=float)
-                if candidate.shape == (k, k):
-                    return candidate
-        except Exception:
-            pass
-    # Heuristik (Auftrag): ...
-    ...
-    return delta
+        m = re.search(r"\[[\s\S]*\]", raw)
+        if not m:
+            return None                              # NOOP: kein JSON im Text
+        candidate = np.array(json.loads(m.group(0)), dtype=float)
+        if candidate.shape != (k, k):
+            return None                              # NOOP: falsche Form (SEAA: K×K)
+        return candidate
+    except Exception:
+        return None                                  # NOOP: Fehler -> überspringen
```

```diff
     def update_from_reflection(self, text: str):
         delta = parse_transition_delta(text, self.K)
+        if delta is None:
+            return {"before": self.P.tolist(), "after": self.P.tolist(),
+                    "delta": None, "lr": self.lr,
+                    "skipped": True, "note": HMM_NOOP_NOTE}
         before = self.P.copy()
```

## 5. Quellen (am 2026-10-01, HTTP 200 geprüft)

| Quelle | Beleg | Link |
|---|---|---|
| SEAA (arXiv:2609.17331) | Δ(R_t) ist K×K; K=4 (Paper §5.7.1, `HMM_STATES=4`) | https://arxiv.org/abs/2609.17331 |
| Mem0-Memory-Operationen | vier Aktionen `ADD` / `UPDATE` / `DELETE` / **`NONE`** („no change") – Vorlage für NOOP | https://github.com/mem0ai/mem0/blob/v1.0.10/docs/open-source/features/custom-update-memory-prompt.mdx · https://docs.mem0.ai/core-concepts/memory-operations/add |
| „Honest Lying" (ICML 2026, FAGEN-Workshop) | ungeprüfte Selbst-Diagnosen im Schreibpfad sind schädlich: „a memory system that stores confident, plausible-sounding but wrong beliefs is worse than no memory at all" → lieber NOOP als eine erfundene Matrix | https://arxiv.org/abs/2605.29463 |

**Ehrliche Einordnung:** Der Auftrag nennt „NOOP"; Mem0 dokumentiert die vierte
Aktion als **`NONE`** („no change") – inhaltlich identisch, hier so benannt.
Kein Papier verlangt wörtlich „NOOP"; die Begründung stützt sich auf das
Mem0-Aktionsschema und den Honest-Lying-Befund zum Schreibpfad.

## 6. Test + Compare-Beleg

```text
make test   → 119 passed · Coverage 1195/1195 Statements = 100,00 % · rc=0
Systemtest  → Score: 22/22 = 100.0% · Auto-Gate (§9): allow · 0 Fehlschläge
```

Neue/angepasste Tests (`tests/test_reflective.py`, 20 Tests):

- `test_row_normalize_und_noop_ohne_llm` – ohne Key → `None`
- `test_parse_transition_delta_noop_bei_kein_json_und_fehler` – kein JSON / Fehler → `None`
- `test_parse_transition_delta_falsche_form_ist_noop` – 2×2 → `None`
- `test_parse_transition_delta_4x4_wird_uebernommen` – gültige Matrix kommt durch
- `test_hmm_update_noop_ohne_matrix` – `skipped=True`, `note`, `P_t` unverändert
- `test_hmm_update_mit_llm_matrix` – `skipped=False`, `P_t` geändert
- `test_simulate_3_reflections_noop_ohne_llm` / `..._mit_llm` – beide Pfade
- `test_run_once` – `hmm_skipped=True` (LLM nicht erreichbar)

## 7. Gate / Drift (§9, §9.1c)

- **Verhaltensänderung** (Auftrag des Auftraggebers, 2026-10-01) → Human-Gate §9
  damit **freigegeben**; Interface-Erweiterung: Rückgabe von
  `update_from_reflection` trägt zusätzlich `skipped`/`note` (dokumentiert).
- **Drift:** 69 eingefügt / 55 entfernt = **124 von 526 Zeilen = 23,6 %** →
  über dem 10-%-Bound (§9.1c) → **Drift-Flag**, durch dieselbe Freigabe gedeckt.
- **Neue Quellen:** Mem0 + „Honest Lying" (beide HTTP 200) – im Code als
  Kommentar verlinkt, in `AGENTS.md` nicht als neues Gesetz geführt.
- **§9.3:** zweite Freigabe-Person weiterhin offen (wie 031/032).

## 8. Nächstes Self-Feedback (t+1)

- Ohne LLM-Key ändert die HMM-Trägheit nichts mehr (NOOP) – das ist gewollt,
  aber `simulate_3_reflections()` ist damit offline nur noch ein
  „übersprungen"-Nachweis. Für echte Läufe ist ein erreichbares Modell nötig.
- Offen: Branch-Coverage (CI misst Statements).
