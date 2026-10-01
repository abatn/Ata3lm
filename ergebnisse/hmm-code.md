# HMM-Übergangsmatrix – ausführbarer Code

> Datum: 2026-10-01
> Zweck: HMM-Übergangsmatrix als ausführbaren Code in `reflective_agent.py`.
> Quelle: SEAA, **arXiv:2609.17331** (September 2026), §5.7.1 + Eq. 2.
> Lab-Prinzip: Keine Erfindungen – Formel + Werte aus der Quelle.

---

## 1. Formel (SEAA Eq. 2, wörtlich)

```text
P_{t+1} = Normalize( P_t + η · Δ(R_t) )
```
- `Δ(R_t)` = Richtungsmatrix, **geparst aus dem Reflexionstext**.
- `η` = Lernrate (SEAA Table 2: **0.05**).
- Row-Normalisierung erhält die Stochasticität.

**Wörtlich (SEAA):** „a Reflexion-style verbal metacognition loop whose output
updates the HMM parameters themselves, **rather than merely being stored as text**."

---

## 2. Ausführbarer Code (`data/memory/reflective_agent.py`)

**Klasse `HMMInertia`:**
```python
class HMMInertia:
    def __init__(self, states=4, lr=0.05, beta=4.0):
        self.P = uniform_stochastic_matrix(states)   # SEAA Listing 1
        self.P_base = diag_dominant(states)          # SEAA Table 2
        self.V = zeros(states)                       # Präferenzvektor
    def update_from_reflection(self, text):
        delta = parse_transition_delta(text, self.K)  # Δ(R_t) aus Text
        self.P = row_normalize(self.P + self.lr * delta)   # Eq. 2
    def step_free_prototype(self, n_t):              # Eq. 3/4 (LLM-frei)
        r = cos(b_z, n_t) - 0.80 + eps
        self.V[z] = clip(self.V[z] + lr*tanh(2*r))
        self.P = softmax(log(P_base) + beta*V)
```

**`parse_transition_delta(text, k)`:** parst `Δ(R_t)` per LLM (SEAA §4.2, 4 Fragen);
Fallback = deterministische Heuristik (Vorzeichen).

**Ausführen:** `SEAA_SIM=3 python3 data/memory/reflective_agent.py`

---

## 3. Test: 3 Reflexionen → P_t ändert sich

**Ausgeführt** (`SEAA_SIM=3`, lr=0.05):

| Reflexion | Text | P vorher (Zeile 0) | P nachher (Zeile 0) |
|---|---|---|---|
| 1 | „action was wrong… deviate more" | [0.25, 0.25, 0.25, 0.25] | **[0.2424**, 0.2525, 0.2525, 0.2525] |
| 2 | „matched my inertia… keep" | [0.2424, 0.2525, 0.2525, 0.2525] | [0.2424, 0.2525, 0.2525, 0.2525] |
| 3 | „biased… adjustment" | [0.2424, 0.2525, 0.2525, 0.2525] | **[0.2342**, 0.2570, 0.2544, 0.2544] |

**Effekt:**
- **Reflexion 1 (negativ):** P[0,0] 0.2500 → 0.2424 (Trägheit gesenkt).
- **Reflexion 2 (positiv/„keep"):** keine Änderung (Δ=0 → Tendenz beibehalten).
- **Reflexion 3 (negativ):** P[0,0] 0.2424 → 0.2342 (Trägheit weiter gesenkt).

→ Jede verbale Reflexion **parst Δ(R_t) und aktualisiert P_t** – nicht nur Text. ✅

---

## 4. Parameter-editierend vs. text-only (SEAA)

| Modus | Wirkung |
|---|---|
| **text-only (Kontrolle)** | Reflexion wird nur als Text gespeichert; P bleibt bei P_base |
| **SEAA (parameter-editierend)** | Reflexion **editiert P_t** (Eq. 2) |

> Wörtlich (SEAA): Kontrolle „never applies Eq. (4), so its matrix stays at P_base".

---

## 5. Quellen (HTTP 200, verifiziert 2026-10-01)

- SEAA (Eq. 2, §5.7.1, Table 2): https://arxiv.org/abs/2609.17331
- SEAA HTML: https://arxiv.org/html/2609.17331v1

---

## 6. Status

| Punkt | Status |
|---|---|
| HMM-Matrix als ausführbarer Code | ✅ `HMMInertia` in `reflective_agent.py` |
| Eq. 2 (`P_{t+1}=Normalize(P_t+η·Δ)`) | ✅ |
| Δ(R_t) aus Reflexionstext | ✅ (LLM + Fallback) |
| Test (3 Reflexionen, vorher/nachher) | ✅ (P[0,0] 0.25 → 0.2424 → 0.2342) |

**Ehrlich:** Formel (Eq. 2) + Werte (η=0.05, K=4) wörtlich aus SEAA (arXiv:2609.17331).
`Δ(R_t)` wird per LLM geparst (wie im Paper); die 3 Beispiel-Reflexionen sind Auftrag.
