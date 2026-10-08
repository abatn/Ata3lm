# Rekursion 086: Eskalationsgate `g*` im Fast Write Router

> Datum: 2026-10-08 · Phasen: Konstrukt → Akt → Observe → Compare → Revise.
> Ziel `g` (§9.1c): Eskalationsgate **forschungstreu** auf `g* = V_large − V_small`
> umstellen (statt allein String-Match).
> Quelle: **arXiv:2608.22215 §3.3.1/§3.3.2 + Tabelle 1** (in `AGENTS.md` §10.2
> referenziert ⇒ **keine neue Quelle**; HTML v2 real gelesen, 2026-10-08).
> Status: **`approved`** (Batnini + Taoufik, 2026-10-08; §9 Interface-Änderung).

## 1. Soll (wörtlich aus der Quelle, Belegt)

Kernformeln (Paper §3.3.1/§3.3.2):

```text
r(W) = EM(W) − EM(D) − λ_s          (Routing-Reward, §3.3.1)
r(D) = 0
a    = argmax(r(W), r(D))
V_small = r(a_small)
V_large = r(a_large) − λ_e
g*   = V_large − V_small            (Eskalationsgate, §3.3.2)
eskalieren ⟺ g_pred > 0
```

Paper-λ (Tabelle 1, Belegt): Configs `(λ_s=0.08, λ_e=0.005)` und
`(λ_s=0.2, λ_e=0.008)`.

**Auftrag (ehrlich):** `EM(W)`/`EM(D)` werden hier über **Modellverhalten**
approximiert (`_matches`: Antwort korrekt ja/nein) — das Paper nutzt gelernte
MLP-Heads (§3.3.3). Die Formeln/λ sind Belegt, die Verhaltens-Approximation ist
Projekt-Auftrag.

## 2. Ist (vorher → nachher)

**Vorher:** `classify()` eskalierte Stufe 1→2 allein über den String-Match
(`_matches(a_small, correct)`); ein `g_pred`-Vergleich existierte nicht
(vgl. `AGENTS.md:260`).

**Nachher** (`data/memory/fast_write_router.py`):

| Ort | Inhalt |
|---|---|
| `reward(...)` | `r(W)=EM(W)-EM(D)-λ_s`, `r(D)=0` (§3.3.1, Belegt) |
| `_argmax_reward(...)` | `a = argmax(r(W), r(D))`; Gleichstand ⇒ `D` |
| `escalation_gain(...)` | `V_small`, `V_large=r(a_large)-λ_e`, `g=V_large-V_small`, `escalate = g>0` (§3.3.2) |
| `_env_float(...)` | λ per ENV `FWR_LAMBDA_S`/`FWR_LAMBDA_E` (Default 0.08/0.005) |
| `_router_class(...)` | Klasse aus Verhalten EINES Routers (zero-shot korrekt ⇒ non-write) |
| `_classify_reward_gate(...)` | Eskalationspfad über `g*`; Ergebnisfeld `gate_info` |

**Rückwärtskompatibel:** `reward_gate=False` (Default) ⇒ **exakter alter Pfad**
(String-Match-Fallback bleibt); bestehende Aufrufer/Tests unverändert.
`classify(..., reward_gate=True)` nutzt die vier LLM-Antworten (small zero/mem,
large zero/mem), berechnet `g*` und eskaliert nur bei `g > 0`.

**Interface-Änderung (§9-pflichtig, kenntlich gemacht, `approved`):** neue
optionale Parameter `reward_gate=False`, `lambda_s=None`, `lambda_e=None` +
neue reine Funktionen. `AGENTS.md` und `data/memory/tier1-base/` wurden **nicht**
geändert.

## 3. Diff

```
data/memory/fast_write_router.py | 166 ++++++++++++++++++++++++++++++++++++++-
1 file changed, 163 insertions(+), 3 deletions(-)
```

- `+` 163 Zeilen: Docstring (§3.3.1/§3.3.2 Belegt + Auftrag-Hinweis), `reward`,
  `_argmax_reward`, `escalation_gain`, `_env_float`, `_router_class`,
  `_classify_reward_gate`, `classify`-Erweiterung.
- `-` 3 Zeilen: `classify`-Docstring/Signatur (ohne Semantikverlust ersetzt).
- Neu (untracked): `tests/test_fwr_gate.py`.

## 4. Compare / Tests (echtes externes Signal)

`tests/test_fwr_gate.py` (offline, Stubs) + bestehende FWR-Tests:

| Testblock | Aussage |
|---|---|
| `reward` | EM(W)=1,EM(D)=0,λ_s=0.08 ⇒ rW=0.92; identisch ⇒ −0.08 |
| `escalation_gain` (a) | groß besser ⇒ `g>0`, `escalate` |
| `escalation_gain` (b) | klein genügt ⇒ `g≤0`, kein `escalate` |
| `escalation_gain` (c) | `λ_e` kippt Vorzeichen (0.005 → 1.0) |
| Grenzfall | `g==0` ⇒ kein `escalate` |
| `classify(reward_gate=True)` | Eskalation→write-new; klein genügt→non-write; small-mem→write-new; uncertain; explizite/ENV-λ |
| Legacy-Fallback | `classify()` ohne Option unverändert |

**Akzeptanz (ausgeführt):**

- `.venv/bin/python -m pytest tests/test_fwr_gate.py tests/test_fwr.py tests/test_fwr_write.py -q --no-cov` → **38 passed** (405,7 s; echter Endpoint).
- `.venv/bin/python -m pytest -m "not network and not live" -q --no-cov -p no:cacheprovider` → **670 passed, 27 deselected** (32,7 s).
- `ruff check` + `ruff format --check` → sauber.
- Coverage `fast_write_router.py`: **100 % (Line+Branch)** (176 Stmts / 46 Branches, 0 Miss; gemessen über `test_fwr_gate`, `test_fwr`, `test_fwr_write`, `test_lifecycle_discard`, `test_network_boundaries`).

## 5. §9-Gate

**`approved`** (Batnini + Taoufik, 2026-10-08). Keine neue Quelle
(arXiv:2608.22215 in `AGENTS.md` §10.2). Interface-Änderung ist freigegeben und
im Docstring kenntlich gemacht. `data/memory/`-Skript/Test ⇒ **kein**
`versions/vN`. **Kein** `git add/commit/push` (§G6).
