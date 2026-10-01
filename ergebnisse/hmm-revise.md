# HMM-Revision – Metakognition strukturell in Revise

> Datum: 2026-10-01
> Zweck: HMM-Trägheit strukturell in die Revise-Phase einbauen.
> Lab-Prinzip: Keine Erfindungen – Mechanismus + Werte aus Quelle (SEAA, Table 2).
> Geltung: `AGENTS.md` §6, §7 (Kognition & Metakognition).

---

## 1. Bestand (zuerst geprüft)

| Ort | HMM-Trägheit vorhanden? |
|---|---|
| `knowledge/lifecycle/denken.md` §3 (SEAA-Mapping) | ✅ ja (Stufe 5) |
| `connectors/mars-seaa.md` (SEAA) | ✅ ja |
| `skills/recursive-improve/revise/SKILL.md` | ❌ **nein** → ergänzt (§2b) |

**Ergebnis:** Der HMM-Mechanismus war in Stufe 5 belegt, fehlte in Revise. → ergänzt.

---

## 2. Mechanismus (Quelle: SEAA, exakte Werte)

**Quelle:** SEAA (Self-Emergence Agent Architecture), https://arxiv.org/abs/2609.17331.

**Gleichung (Eq. 2):**
```text
P_{t+1} = Normalize( P_t + η · Δ(R_t) )
```
- `Δ(R_t)` = Richtungsmatrix, geparst aus dem Reflexionstext (LLM).
- `η` = Reflexions-Lernrate.
- Row-Normalisierung erhält die Stochasticität.

**Alternative Form (Eq. 3):** `P_t = softmax(log P_base + β·V_t)`, `P_base` diagonal-dominant.

**SEAA-Hyperparameter (Table 2, identisch für alle Agenten):**

| Symbol | Bedeutung | Wert |
|---|---|---|
| K | latente Zustände | **4** |
| D | Verhaltens-Dimensionen | 3 |
| N | Agenten | 5 |
| T | Zeitschritte/Run | 600 |
| **η** | Reflexions-Lernrate | **0.05** |
| **β** | Präferenz→Übergangs-Stärke | **4.0** |
| — | Random-Walk-Schritt | 0.03 |
| **P_base** | initiale Trägheitsmatrix | **diag-dominant, row-stochastic** |

**Implementierung (SEAA):** Python 3.10+, **hmmlearn**, numpy/matplotlib.

**Abgrenzung (Auftrag):** HMM gehört zu SEAA, **nicht** zu MARS
(`knowledge/lifecycle/denken.md:40-41`).

---

## 3. Struktur in Revise

```text
Beobachtung r ─▶ VALIDATE ─▶ REFLECT (sr) ─▶ HMM-Matrix anpassen (Eq. 2) ─▶ PIVOT
```

- **Zustände (HMM):** K = 4 (SEAA Table 2).
- **Trägheit:** diag-dominante P_base (hohe Selbst-Übergangswahrscheinlichkeit).
- **Reflexion:** `P_{t+1} = Normalize(P_t + η·Δ(R_t))` mit η = 0.05.

---

## 4. Test: neue Beobachtung → Übergangswahrscheinlichkeiten (mit SEAA-Formel)

> **Quelle der Werte:** P_base diag-dominant, η = 0.05 (SEAA Table 2).
> Die konkrete Δ(R)-Matrix ist eine Beispiel-Reflexion (Auftrag), da `Δ(R_t)`
> im Paper LLM-geparst wird.

### Ausgangsmatrix P_base (diag-dominant, K=4)

| | S1 | S2 | S3 | S4 |
|---|---|---|---|---|
| **S1** | 0.70 | 0.10 | 0.10 | 0.10 |
| **S2** | 0.10 | 0.70 | 0.10 | 0.10 |
| **S3** | 0.10 | 0.10 | 0.70 | 0.10 |
| **S4** | 0.10 | 0.10 | 0.10 | 0.70 |

### Neue Beobachtung → Reflexion
- `r` = negativ (Solver-Test fehlgeschlagen).
- `sr`: „Verhalten war falsch → stärker abweichen."
- Δ(R): Diagonale −0.4, Off-Diagonale +0.4/3.

### Anwendung Eq. (2): `P_{t+1} = Normalize(P + 0.05·Δ(R))`

| | S1 | S2 | S3 | S4 |
|---|---|---|---|---|
| **S1** | **0.6800** | 0.1067 | 0.1067 | 0.1067 |
| **S2** | 0.1067 | 0.6800 | 0.1067 | 0.1067 |
| **S3** | 0.1067 | 0.1067 | 0.6800 | 0.1067 |
| **S4** | 0.1067 | 0.1067 | 0.1067 | 0.6800 |

**Effekt:** Selbst-Übergang **P[0,0]: 0.7000 → 0.6800** (Trägheit gesenkt,
weil η·Δ = 0.05·(−0.4) = −0.02). Der Agent weicht bei der nächsten Beobachtung
stärker ab.

### Umgekehrt (positive Beobachtung)
- Δ(R) mit Diagonale **+**0.4 → P[0,0] steigt (mehr Trägheit, weniger Abweichung).

---

## 5. Quellen (HTTP 200, verifiziert 2026-10-01)

- SEAA (HMM-Trägheit, Eq. 2/3/4, Table 2): https://arxiv.org/abs/2609.17331
- SEAA HTML (Formeln + Hyperparameter): https://arxiv.org/html/2609.17331v1
- Reflexion (verbale Selbstreflexion): https://arxiv.org/abs/2303.11366
- Projekt-Belege: `knowledge/lifecycle/denken.md` §3, `connectors/mars-seaa.md`

---

## 6. Status

| Punkt | Status |
|---|---|
| Bestand geprüft | ✅ (in denken.md vorhanden, in revise fehlend) |
| HMM strukturell in Revise | ✅ ergänzt (`revise/SKILL.md` §2b) |
| Werte aus Quelle | ✅ SEAA Table 2 (K=4, η=0.05, β=4.0, P_base diag-dominant) |
| Simulation mit Eq. (2) | ✅ P[0,0] 0.70 → 0.68 |

**Ehrlich:** Mechanismus, Formel und Hyperparameter stammen aus SEAA
(arXiv:2609.17331, Table 2). Nur die **konkrete Δ(R)-Beispielmatrix** ist eine
Illustration (Auftrag), weil `Δ(R_t)` im Paper LLM-geparst wird.
