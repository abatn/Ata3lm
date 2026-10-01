# 031 – Fast Write Router: toten Default ersetzen (gemma-2b → nano-30b)

> Datum: 2026-10-01
> Rekursionstiefe: System-Iteration (Governance/FWR)
> Phase: Observe → Compare → Revise
> Auslöser: menschlicher Auftrag 2026-10-01 („prüfe die FWR-Blockade, ersetze
> gemma-2b durch ein verfügbares Modell"). Freigabe: `ok go`.

## 1. Zustand vorher / nachher

| Aspekt | vorher | nachher |
|---|---|---|
| `FWR_SMALL_MODEL` Default | `google/gemma-2b` → **HTTP 404** auf diesem Konto (Stufe 1 tot) | `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning` (1,2–3,8 s, geprüft) |
| `FWR_LARGE_MODEL` | `nvidia/nemotron-3-super-120b-a12b` | unverändert (geprüft OK) |
| Testbarkeit | nur mit Modell-ENV-Override | **mit den Defaults**, nur Key nötig |
| Behauptung „kein Key → nicht testbar" | in Chat so behauptet | korrigiert: Key lag in `opencode.json`, Probe war fehlerhaft |

**Diff `(π, I, M)`:**
- `π` (Code): `data/memory/fast_write_router.py` **1 Zeile** (Default-Literal).
  Signatur, Logik, ENV-Überschreibbarkeit unverändert → **keine Interface-Änderung**.
- `I` (Interface): unverändert. `AGENTS.md` §10.2-Tabelle: 1 Zelle (Default-Wert).
- `M` (Memory): `data/memory/tier1-base/` inhaltlich **nicht** geändert; Snapshot
  `versions/v4/` angelegt (Mechanik B, §9.1b). `ontology.md` weicht von `v3` ab →
  v4 ist ein echter Zwischenstand.

## 2. Änderungen

| Datei | Was |
|---|---|
| `data/memory/fast_write_router.py:21` | Default-Literal getauscht (1 Zeile) |
| `AGENTS.md:252` | Zelle „Default `google/gemma-2b`" → neuer Default (Gesetz, Human-Gate) |
| `data/memory/tier1-base/versions/v4/` | Snapshot (identity, ontology, core-relations, episodic_graph) |
| `ergebnisse/fast-write-router.md` §3 | „nur nemotron-3-super-120b verfügbar" → aktueller Prüfstand |
| `ergebnisse/fwr-test.md` | **neu** – Key-Prüfung, Modell-Suche (15 Modelle), E2E-Rohergebnisse |
| `ergebnisse/rekursion/031-fwr-modell.md`, `README.md` Index | diese Iteration |

## 3. Compare-Beleg (externes Signal, 8 Tests)

| # | Test | Ergebnis |
|---|---|---|
| T1 | `py_compile` + Default zeigt neues Modell | `SMALL=nvidia/nemotron-3-nano-omni-30b-a3b-reasoning` ✓ |
| T2 | FWR-Fall A „2+2?" | `non-write`, stage 1, `small='4.'` ✓ |
| T3 | FWR-Fall B Drift-Bound §9.1c | `write-new`, stage 2, `small="I don't know."`, `large+mem="…10 %…"` ✓ |
| T4 | zero-shot-Kontrollfragen C/E/G | `non-write` ✓ (Wüste, Berlin, EU AI Act) |
| T5 | **kein** `FWR_*_MODEL` im ENV gesetzt | Defaults greifen ✓ |
| T6 | `versions/v4/` == Live-Tier-1 (4/4 md5) | identisch ✓ |
| T7 | Gesamt-Systemtest (10 Stufen) | **21/21 = 100 %** ✓ |
| T8 | `git status` ohne Seiteneffekte | leer (Logdateien sind gitignored) ✓ |

**Score: 8/8 = 100 %** – Gesamtsystemtest 21/21 → Auto-Gate `allow` (§9).

Rohausgaben: `ergebnisse/fwr-test.md` §4, `/tmp/opencode/st2.out`.

## 4. Befunde ohne Code-Fix (bewusst offen)

1. ~~`write-update` wurde nicht geübt~~ → **korrigiert 2026-10-01: `write-update`
   ist geübt – siehe Beweis.** Fall C „Größte Wüste der Welt?“ (`correct="Sahara"`,
   `fast_write_router.py:176-177`) liefert mit den aktuellen Defaults
   `class=write-update stage=2`. Rohtexte: `ergebnisse/fast-write-router.md:70-78`;
   Nachlauf 2026-10-01 (small `The Antarctic Desert is the largest desert in the
   world.` · large0 nicht-verweigernd falsch · largeM `The largest desert in the
   world is the Sahara.`): `ergebnisse/doku-korrektur-fwr.md`.
   In *dieser* Iteration kam C nicht vor (dort liefen A/B/D/E/F/G);
   `fwr-test.md` §4 nutzte für dieselbe Frage `correct="Antarctic Desert"` →
   `non-write`.
2. **Doku-Code-Abweichung**: Docstring/`fast-write-router.md` verlangen für
   `write-update` „zero-shot falsch + mit Memory korrekt"; der Code prüft nur
   `is_refusal(a_large)`. Korrektur = Verhaltensänderung → eigenes Gate nötig.
   → **Erledigt 2026-10-01 nach Freigabe:** `classify()` wertet `a_mem` aus,
   sonst `uncertain` + `gate=ask`; Diff/Test/Freigabe: `ergebnisse/fwr-code-korrektur.md`.

## 5. Quellen

Keine neuen Papers. Nachweis = Endpunkt-Messung:
`GET https://integrate.api.nvidia.com/v1/models` → 200 (81 Modelle),
`POST …/chat/completions` → 404/410/200 je Modell.
Schlüssel/Basis-URL: `~/.config/opencode/opencode.json` (`mcp.mars.env`).
Bestehende FWR-Quelle unverändert: arXiv:2608.22215 (§3.1/§3.3),
https://arxiv.org/abs/2608.22215.

## 6. Gate-Entscheidung (§9)

| Bedingung | Wert | Gate |
|---|---|---|
| Compare-Score | 100 % | allow |
| Neue Quelle | keine | – |
| Interface-Änderung | keine | – |
| Drift | `fast_write_router.py` 2/184 = **1,09 %**; `AGENTS.md` 2/392 = 0,51 % | ≤ 10 % ✓ |
| **`AGENTS.md` geändert** | §10.2-Tabelle, 1 Zelle | **Human-Gate: `approved: Batnini, 2026-10-01` („ok go")** + Snapshot `versions/v4/` |

## 7. Freigabe

`approved: Batnini, 2026-10-01` – Entscheidung „ok go" des Auftraggebers,
vor der Umsetzung dokumentiert.

## 8. Nächstes Self-Feedback (t+1)

- ~~`write-update`-Fall gezielt erzeugen~~ → **erledigt 2026-10-01** (natürlich
  reproduzierbar, siehe §4.1) – übrig bleibt nur die Doku-Code-Abweichung (§4,
  Punkt 2), die ein eigenes Gate (§9) braucht → **auch erledigt 2026-10-01**
  (Gate freigegeben, `ergebnisse/fwr-code-korrektur.md` §0).
- ~~`ergebnisse/versionierung.md` §4 um den Eintrag `versions/v4` ergänzen~~ →
  **erledigt 2026-10-01** (Zeile in §4 vorhanden).
- Fallback-Modell `deepseek-ai/deepseek-v4.1-flash` beobachten (Ersatz bei
  nano-503/„worker exhausted").
- `/tmp/opencode/ka_systemtest.py` dauerhaft ins Repo übernehmen (offen seit 030).
