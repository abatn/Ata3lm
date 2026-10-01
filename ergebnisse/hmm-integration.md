# SEAA-HMM-Integration in den Reflective Agent

> Datum: 2026-10-01
> Zweck: SEAA-HMM-Übergangsmatrix in `data/memory/reflective_agent.py` integrieren.
> Quelle: SEAA, **arXiv:2609.17331** (September 2026).
> Lab-Prinzip: Keine Erfindungen – Mechanismus + Werte aus der Quelle.

---

## 1. Mechanismus (SEAA, wörtlich)

**Gleichung (Eq. 2):**
```text
P_{t+1} = Normalize( P_t + η · Δ(R_t) )
```
- `Δ(R_t)` = Richtungsmatrix, geparst aus dem Reflexionstext.
- `η` = Lernrate (SEAA Table 2: **η = 0.05**).
- Row-Normalisierung erhält die Stochasticität.

**Wörtlich (SEAA):** „a Reflexion-style verbal metacognition loop whose output
updates the HMM parameters themselves, **rather than merely being stored as text**."

**Parameter (SEAA Table 2):** K = 4 latente Zustände, η = 0.05, `P_base` diag-dominant;
Bibliothek **hmmlearn**.

---

## 2. Integration in `reflective_agent.py`

**Neue Komponenten:**
- `HMMInertia` (Klasse): P-Matrix (K×K), `update_from_reflection(text)`.
- `parse_transition_delta(text, k)`: parst Δ(R_t) aus dem Reflexionstext
  (LLM wenn verfügbar, sonst deterministische Heuristik).
- `run_once()`: ruft nach der Destillation `hmm.update_from_reflection(summary)` auf.

```text
Hub-Destillation ─▶ Reflexionstext ─▶ parse Δ(R_t) ─▶ P_{t+1}=Normalize(P_t+η·Δ)
                                                         (nicht nur Text!)
```

**Parameter:** `SEAA_STATES=4`, `SEAA_LR=0.05` (ENV, Default = SEAA Table 2).

---

## 3. Test: neue Beobachtung → P_t ändert sich

**Ausgeführt:** `python3 data/memory/reflective_agent.py` (Hub n2, Destillation).

| | S1 | S2 | S3 | S4 |
|---|---|---|---|---|
| **P vorher (Zeile 0)** | 0.2500 | 0.2500 | 0.2500 | 0.2500 |
| **P nachher (Zeile 0)** | **0.2350** | 0.2550 | 0.2550 | 0.2550 |

**Effekt:** Selbst-Übergang **P[0,0]: 0.2500 → 0.2350** (Trägheit gesenkt,
Δ[0,0] negativ aus der Reflexion). Die Reflexion hat die **Übergangswahrscheinlichkeiten**
geändert – nicht nur Text gespeichert.

**Verifikation:** K=4, η=0.05 (SEAA Table 2) bestätigt.

---

## 3b. LLM-freier Kern (Eq. 3/4) — verbessert

**Ergänzung (nach Prüfung einer externen Analyse):** Das Paper hat **zwei** Wege:
- **Eq. 2** (LLM parst Δ(R_t)) → `update_from_reflection`
- **Eq. 3/4** (LLM-frei, „direct numerical realization of Eq. 2") → `step_free_prototype`

**Eq. 3/4 (Paper §5.7.1, Listing 2):**
```text
P_t       = softmax( log P_base + β·V_t )          (Eq. 3)
r_t       = cos(b_{z_t}, n_t) − 0.80 + ε_t          (Eq. 4)
V_{t+1}[z]= clip( V_t[z] + η·tanh(2·r_t) )          (Eq. 4)
```

**Zustandsraum (Paper §5.7.1):** K=4, S = **{calm, alert, impulsive, pessimistic}**.

**Test (LLM-frei, T=600):**
```text
P_base (diag-dominant): [0.7, 0.1, 0.1, 0.1]
Nach T=600:  V = [7.184, 1.202, -0.060, 0.071]
             P Zeile 0 = [1.0, 0.0, 0.0, 0.0]
=> Symmetriebrechung: P konzentriert sich auf den dominanten Zustand
   (SEAA §5.7.2: „a positive feedback loop that concentrates P_t onto a dominant state").
```

**Bugfix:** `V` muss **per Spalte** addiert werden (`V[None,:]`), nicht per Zeile —
sonst ist die Softmax invariant (konstante Verschiebung). Behoben.

---

## 4. Parameter-editierende vs. text-only Reflexion (SEAA)

| Ansatz | Wirkung |
|---|---|
| **text-only Reflexion** | Reflexion wird nur als Text gespeichert (Baseline) |
| **SEAA (parameter-editierend)** | Reflexion **editiert die HMM-Parameter** (`P_{t+1}`) |

> Wörtlich (SEAA): „updates the HMM parameters themselves, rather than merely being
> stored as text"; die Kontrollgruppe „never applies Eq. (4), so its matrix stays at P_base".

---

## 5. Quellen (HTTP 200, verifiziert 2026-10-01)

- SEAA (Behavior-Inertia HMM, Eq. 2, Table 2): https://arxiv.org/abs/2609.17331
- SEAA HTML (Formeln + Pseudocode): https://arxiv.org/html/2609.17331v1

---

## 5b. Suche nach offizieller Code-Lösung (GitHub/HuggingFace)

**Auftrag:** „suche in github und huggingface nach offizieller Lösung".

| Ort | Suche | Ergebnis |
|---|---|---|
| GitHub | `self-emergence agent SEAA` | **0 Treffer** |
| GitHub | `behavior inertia HMM agent` | **0 Treffer** |
| HuggingFace | `self-emergence agent` | **0 Modelle** |
| HuggingFace | `SEAA inertia` | **0 Modelle** |
| Paper | Code-URL? | **keine** (nur arXiv-eigener „Report GitHub Issue"-Link) |

**Befund:** Es gibt **kein offizielles Code-Repository** für SEAA (Stand 2026-10-01).
Das Paper behauptet „fully open-source and reproducible", liefert aber **keinen Link**.
Die **offizielle Spezifikation ist der Pseudocode** (Listing 1 + Listing 2) + Eq. 2/3/4 + Table 2.

**SEAA-Reflexionsprompt (Paper §4.2, 4 Fragen):**
1. Did the action match my usual inertia?
2. Which inertial tendency drove the decision, and was it biased?
3. How should that tendency be adjusted?
4. **What is the corresponding structured edit to P_t?** (= language-to-parameter mapping)

**Konsequenz:** Die Implementierung folgt dem **Paper-Pseudocode** (`LLM.parse_transition_delta`
mit den 4 Fragen). Da kein Referenz-Code existiert, ist der Pseudocode die höchste
verfügbare Quelle – keine Erfindung.

---

## 6. Status

| Punkt | Status |
|---|---|
| HMM-Übergangsmatrix (Eq. 2) | ✅ in `reflective_agent.py` |
| Reflexion editiert P (nicht nur Text) | ✅ |
| Test (P vorher/nachher) | ✅ (P[0,0] 0.25 → 0.235) |
| Werte (K=4, η=0.05) | ✅ SEAA Table 2 |

**Ehrlich:** Mechanismus (Eq. 2), Werte (K=4, η=0.05) und die parameter-editierende
Reflexion stammen aus SEAA (arXiv:2609.17331). Δ(R_t) wird im Paper per LLM geparst;
hier per LLM (mit deterministischer Heuristik als Fallback) – klar markiert.
