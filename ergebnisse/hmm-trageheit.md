# HMM-Trägheit – Update-Logik (SEAA)

> Datum: 2026-10-01
> Zweck: HMM-Übergangsmatrix-Update-Logik in `data/memory/reflective_agent.py`.
> Quelle: SEAA, **arXiv:2609.17331** (September 2026), §5.7.1 + Eq. 2.
> Lab-Prinzip: Keine Erfindungen – Formel + Werte wörtlich aus der Quelle.

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
**§5.7.1:** K=4, S = {calm, alert, impulsive, pessimistic}.

---

## 2. Implementierung (`data/memory/reflective_agent.py`)

| Funktion | Aufgabe |
|---|---|
| `parse_transition_delta(text, k)` | parst `Δ(R_t)` aus dem Reflexionstext (LLM §4.2, 4 Fragen; Fallback-Heuristik) |
| `HMMInertia.update_from_reflection(text)` | `P = Normalize(P + η·Δ(R_t))` (Eq. 2) |
| `simulate_3_reflections()` | 3 Reflexionen → P vorher/nachher |

**SEAA-Reflexionsprompt (§4.2, 4 Fragen):** (1) match inertia? (2) which tendency?
(3) how adjust? (4) **structured edit to P_t** (language-to-parameter mapping).

**Ausführen:** `SEAA_SIM=3 python3 data/memory/reflective_agent.py`

---

## 3. Test: 3 Reflexionen → P_t ändert sich

**Ausgeführt** (lr=0.05):

| Reflexion | Text | P vorher (Zeile 0) | P nachher (Zeile 0) |
|---|---|---|---|
| 1 | „action was wrong… deviate more" | [0.2500, 0.25, 0.25, 0.25] | **[0.2308**, 0.2564, 0.2564, 0.2564] |
| 2 | „matched my inertia… keep" | [0.2308, 0.2564, …] | [0.2308, 0.2564, …] |
| 3 | „biased… adjustment" | [0.2308, 0.2564, …] | **[0.2158**, 0.2614, 0.2614, 0.2614] |

**Effekt:**
- **Reflexion 1 (negativ):** P[0,0] 0.2500 → 0.2308 (Trägheit gesenkt).
- **Reflexion 2 (positiv/„keep"):** Δ=0 → Tendenz beibehalten.
- **Reflexion 3 (negativ):** P[0,0] 0.2308 → 0.2158 (weiter gesenkt).

→ Jede verbale Reflexion **parst Δ(R_t) und aktualisiert P_t** – nicht nur Text. ✅

---

## 4. Parameter-editierend vs. text-only (SEAA)

| Modus | Wirkung |
|---|---|
| **text-only (Kontrolle)** | Reflexion nur als Text; P bleibt bei P_base |
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
| HMM-Update-Logik | ✅ `HMMInertia.update_from_reflection` |
| Eq. 2 (`P_{t+1}=Normalize(P_t+η·Δ)`) | ✅ |
| Δ(R_t) aus Reflexionstext | ✅ (LLM + Fallback) |
| Test (3 Reflexionen) | ✅ (P[0,0] 0.25 → 0.2308 → 0.2158) |

**Ehrlich:** Formel (Eq. 2) + Werte (η=0.05, K=4) wörtlich aus SEAA (arXiv:2609.17331).
`Δ(R_t)` per LLM geparst (wie im Paper); die 3 Beispiel-Reflexionen sind Auftrag.
