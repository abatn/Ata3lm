# P3d / S1-korrekt — Drift-Referenz §-konform (§9.1c/§9.2b)

> Datum: 2026-10-05 · Status: **Auftrag** (Fix) + **Belegt** (Regeln).
> Freigabe: `approved` (Batnini, „go mit Bedingung 1–3", Lesart A = Cold-Start-Bootstrap).
> Guardrail 6: **kein Git**. Guardrail 7: echte Tests, echte Endpoint-Calls.

## 1. Warum (der zurückgesetzte S1-Fehler)
Die erste „S1"-Lösung setzte die Drift-Referenz = **die eigene Beobachtung**
(`reference = observed`) ⇒ `DI = JSD(observed, observed) = 0` ⇒ Gate **immer `ok`**
⇒ die Bremse war standardmäßig **AUS**. Verstoß gegen §9:116/122, §9.1c, §9.2b, §5.
Wurde per `git checkout`/`git clean` vollständig zurückgesetzt.

## 2. Fix (Referenz-Priorität, §9.1c/§9.2b)
`data/memory/lifecycle_runner.py`:
1. Referenz = **explizit** (`drift_baseline`) → **Env-Erwartung** (`LIFECYCLE_DRIFT_BASELINE`, JSON) → **persistierter Checkpoint** (`LIFECYCLE_DRIFT_REFERENCE`, Default `data/memory/tier2-index/drift-reference.json`) → **keine**.
2. **Cold-Start** (keine Referenz) ⇒ `gate="ask"` (Grund „keine Referenz §10.4") — **nie still `ok`**; einmaliger **Bootstrap** der Referenz (Initialisierung, Lesart A).
3. Checkpoint wird **nur bei freigegebenem Akt** (`Gedächtnis.ok`) fortgeschrieben `M(t)→M(t+1)` (§9-Analogie „keine Revision nach Ablehnung").
4. `run_cycle`-**Signatur unverändert** (G4); τ=10 % bleibt **Auftrag** (§9.1c). Pfad in `tier2-index/` ⇒ **kein §9.1b**-Snapshot (nicht `AGENTS.md`/`tier1-base`).

**Bedingung 1:** `.gitignore` + `tests/conftest.py` zwingen `LIFECYCLE_DRIFT_REFERENCE` global auf tmp ⇒ kein Repo-Write.
**Bedingung 3:** `test_n7_wissen_plus_echte_verteilung` inhaltlich erhalten, Erwartung per **injizierter Baseline**.

## 3. Evidenz (§9.1d, real gemessen)
| Fall | Referenz | Beobachtung | DI | Gate |
|---|---|---|---|---|
| alt (zurückgesetzt) | `{non-write:0.5, write:0.5}` | `{write:1.0}` | 0.3113 | ask (immer) |
| **kaputter S1** | `= observed` | `{write:1.0}` | 0.0 | **ok (immer)** ❌ |
| **korrekt: Cold-Start** | keine ⇒ `ask` (+ Bootstrap) | `{non-write:1.0}` | None | ask |
| **korrekt: unverändert** | `{non-write:1.0}` | `{non-write:1.0}` | 0.0 | ok |
| **korrekt: verschoben** | `{write:1.0}` | `{non-write:1.0}` | 1.0 | ask |

- **Tests:** `test_lifecycle_runner.py` **9 → 16** (7 neue: Cold-Start, unverändert, verschoben, Fortschreiben nur bei ok, Helfer, Env-Parsing, Env-im-Lauf).
- **Modul-Coverage** `lifecycle_runner.py`: **100 %** (104/104).
- **Volle Suite:** **368 passed · 100 % (2793/678)** (echt).
- **Kein Repo-Write:** nach den Tests kein `drift-reference.json` im Repo (verifiziert).

## 4. Gate (§9) + Provenienz
- S1 = Verhaltensänderung, `approved` (Mensch); keine neue Quelle, keine Signaturänderung (G4).
- §9.1b: `AGENTS.md`/`tier1-base` unverändert ⇒ kein `versions/vN`.
- Rekursion: `ergebnisse/rekursion/066-p3d-s1-korrekt.md`.
