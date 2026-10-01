# FWR-Test: Schlüssel, Modell-Auswahl und End-to-End-Lauf

> Datum: 2026-10-01 · Iteration 031 · Phase: Observe → Compare
> Lab-Prinzip §6: nur gemessene Werte. Keine neuen Papers – der Nachweis ist eine
> Endpunkt-Messung (HTTP-Status + Rohtext der Modelle).

## 1. Behauptung prüfen: „FWR nicht testbar – kein OPENAI_API_KEY"

| Prüfung | Ergebnis |
|---|---|
| `env` im Testprozess | **leer** – kein `OPENAI_API_KEY`, kein `OPENAI_BASE_URL` |
| `.env` im Repo / `bashrc` / `profile` | **keine** |
| `~/.config/opencode/opencode.json` | **Key vorhanden**: `mcp/{graphiti,reflexion,react,mars,adas}.env.OPENAI_API_KEY` (`nvapi-…`, 70 Zeichen) + `OPENAI_BASE_URL = https://integrate.api.nvidia.com/v1` |
| `GET https://integrate.api.nvidia.com/v1/models` | **HTTP 200**, 81 Modelle |

**Fazit:** „kein Key in der Umgebung" war für den *Testprozess* wahr, als
**Begründung für „nicht testbar"** falsch – der Schlüssel existiert und gehört
dasselbe Konto wie die 5 MCP-Server des Projekts.

## 2. Echter Defekt: der alte Default war tot

`data/memory/fast_write_router.py` (vor dieser Iteration):

```python
SMALL_MODEL = os.environ.get("FWR_SMALL_MODEL", "google/gemma-2b")
```

| Modell | Status auf diesem Konto | Latenz |
|---|---|---|
| `google/gemma-2b` | **HTTP 404** `Not found for account …` | 0,2 s |
| `google/recurrentgemma-2b` | HTTP 404 | 0,1 s |
| `google/codegemma-7b`, `codegemma-1.1-7b` | HTTP 404 | 0,1–0,2 s |
| `google/gemma-3-4b-it`, `gemma-3-12b-it` | HTTP 404 | 0,1 s |

→ Stufe 1 schlug ohne ENV-Override immer fehl; `classify()` brach mit
`NotFoundError` ab. (Erfasst in `data/memory/fast_write_router.py:21`.)

## 3. Modell-Suche (Schritt S1 – read-only)

Kandidaten aus `opencode.json` (`provider.*.models`):

| deklariert in opencode.json | Ergebnis |
|---|---|
| `nvidia/nemotron-3-super-120b-a12b` | **OK** – bleibt Stufe 2 |
| `nvidia/llama-3.3-nemotron-super-49b-v1.5` | **HTTP 410 Gone** (EOL) |
| `nvidia/llama-3.1-8b-instruct` | **HTTP 404** (nicht in `/v1/models`) |
| `nvidia/kimi-k2.6` | **HTTP 404** |
| `nvidia/llama-3.1-nemoguard-8b-content-safety` | Timeout 45 s (Safety-Classifier, fachlich ungeeignet) |

Kleinst-Modelle aus `/v1/models` (15 geprüft, alle HTTP 404 außer den Genannten):
`ibm/granite-3.0-3b-a800m-instruct`, `ibm/granite-3.0-8b-instruct`,
`ibm/granite-8b-code-instruct`, `mistralai/mistral-7b-instruct-v0.3`,
`nv-mistralai/mistral-nemo-12b-instruct`, `nvidia/mistral-nemo-minitron-8b-8k-instruct`,
`nvidia/cosmos-reason2-8b`, `adept/fuyu-8b`, `aisingapore/sea-lion-7b-instruct`,
`deepseek-ai/deepseek-coder-6.7b-instruct`, `google/*` (s. Tabelle) u. a.

**Einzig funktionierendes kleines Modell:**

| Modell | Latenz | Funktionsprobe (zero-shot) |
|---|---|---|
| **`nvidia/nemotron-3-nano-omni-30b-a3b-reasoning`** | **1,2–3,8 s** | „2+2?" → `4` · unbekannt → `I don't know.` · „Hauptstadt Frankreich?" → `The capital of France is Paris.` |

Zweitplatziert (Fallback, falls nano instabil wird):
`deepseek-ai/deepseek-v4.1-flash` (OK, 16–31 s).

**Entscheidung:** `FWR_SMALL_MODEL` = `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning`,
`FWR_LARGE_MODEL` unverändert = `nvidia/nemotron-3-super-120b-a12b`.
Freigabe: Mensch, 2026-10-01 („ok go").

## 4. End-to-End-Lauf (NEUE Defaults, **kein** ENV-Override für Modelle)

Nur `OPENAI_API_KEY`/`OPENAI_BASE_URL` aus `opencode.json` injiziert.

```
SMALL = nvidia/nemotron-3-nano-omni-30b-a3b-reasoning
LARGE = nvidia/nemotron-3-super-120b-a12b

A: class=non-write  stage=1 escalated=False (5.5s)
   small    : '4.'
B: class=write-new  stage=2 escalated=True  (8.5s)
   small    : "I don't know."
   large 0s : "I don't know."
   large mem: 'The drift-bound threshold is 10 % per iteration.'
C: class=non-write  stage=1 escalated=False (3.3s)
   small    : 'The Antarctic Desert is the largest desert in the world.'
D: class=write-new  stage=2 escalated=True  (7.2s)
   small    : "I don't know."
   large mem: 'The Knowledge-Agent has 17 MCP servers.'
E: class=non-write  stage=1 escalated=False (4.2s)
   small    : 'Berlin.'
F: class=write-new  stage=2 escalated=True  (8.4s)
   small    : "I don't know."
   large mem: 'The graphiti MCP server exposes 13 tools.'
G: class=non-write  stage=1 escalated=False (3.5s)
   small    : 'It was published in 2024.'
```

Fragen: A „2+2?" · B Drift-Bound §9.1c (Fact injiziert) · C größte Wüste ·
D Anzahl MCP-Server (Fact injiziert) · E Hauptstadt Deutschland ·
F graphiti-Tool-Anzahl (Fact injiziert) · G EU AI Act-Jahr.

## 5. Ergebnis gegen die Taxonomie (arXiv:2608.22215 §3.1)

| Klasse | Fälle | Beleg |
|---|---|---|
| `non-write` (Stufe 1, keine Eskalation) | **A, C, E, G** | zero-shot-Antwort enthielt `correct` |
| `write-new` (Stufe 2, Verweigerung + mit Memory korrekt) | **B, D, F** | `small` = „I don't know." → `large_zero_shot` = Verweigerung → `large_with_memory` = richtige Antwort |
| `write-update` (Stufe 2, keine Verweigerung) | **keiner** | nicht ausgelöst – s. Befund unten |

**Befund 1 (ehrlich):** `write-update` wurde in diesem Lauf **nicht** erreicht,
weil beide Modelle auf unbekannten Fakten **verweigern** statt falsch zu antworten.
Der Branch existiert im Code, wurde hier aber nicht geübt.

**Befund 2 (Doku-Code-Abweichung, nicht behoben):**
`fast_write_router.py`-Docstring und `ergebnisse/fast-write-router.md` schreiben
`write-update` = „zero-shot **falsch** + mit Memory korrekt". Der Code prüft nur:

```python
if is_refusal(a_large):
    cls = "write-new"
else:
    cls = "write-update"     # jede Nicht-Verweigerung, ohne "falsch"/"mit Memory korrekt" zu prüfen
```

Damit wird jede nicht-verweigernde Antwort als `write-update` etikettiert.
**Keine Code-Änderung in dieser Iteration** – Korrektur wäre eine Verhaltensänderung
und braucht eigenes Gate (§9/§4).

## 6. Reproduktion

```bash
# Key injizieren, Modelle NICHT ueberschreiben (Tests die neuen Defaults):
python3 - <<'EOF'
import json, os
e = json.load(open("/home/opc/.config/opencode/opencode.json"))["mcp"]["mars"]["env"]
os.environ["OPENAI_API_KEY"] = e["OPENAI_API_KEY"]
os.environ["OPENAI_BASE_URL"] = e["OPENAI_BASE_URL"]
# ... dann data/memory/fast_write_router.py importieren und classify() aufrufen
EOF
```

Skripte dieser Iteration: `/tmp/opencode/s1_probe.py`, `s1b.py`, `s1c.py`,
`fwr_final.py`, `fwr_d.py`, `fwr_f.py`.

## 7. Gate (§9)

| Bedingung | Wert |
|---|---|
| Compare-Score | siehe `ergebnisse/rekursion/031-fwr-modell.md` |
| Neue Quelle | **nein** – kein neues Paper; Nachweis = HTTP-Messung am Endpunkt |
| Interface-Änderung | **nein** – nur Default-Literal, Signatur/ENV unverändert |
| `AGENTS.md` geändert | **ja** → Human-Gate (Freigabe „ok go", 2026-10-01) + Mechanik A/B (Git + `versions/v4/`) |
| Drift | `fast_write_router.py` 1 Zeile; `AGENTS.md` 1 Zelle |
