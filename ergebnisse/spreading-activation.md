# Dual-Path Spreading Activation Retrieval (HeLa-Mem)

> Datum: 2026-10-01
> Zweck: Dual-Path Retrieval in `data/memory/reflective_agent.py` implementieren.
> Quelle: **HeLa-Mem, ACL 2026, arXiv:2604.16839** (§3.4 + Ablation §4.3).
> Lab-Prinzip: Keine Erfindungen – Formeln + Werte wörtlich aus der Quelle.

---

## 1. Base Activation (HeLa-Mem Eq. 3, wörtlich)

```text
S_base(v_i) = ( sim(q, e_i) + α · keyword_match ) · γ(v_i)
```
- `sim(q, e_i)` = Kosinus-Ähnlichkeit zwischen Query-Embedding q und Knoten-Embedding e_i.
- `γ(v_i) = exp(−Δt/τ)` = Zeitzerfall, **τ = 60 Tage**.
- `α` = Bonus für Keyword-Übereinstimmung.

## 2. Spreading Activation (HeLa-Mem, wörtlich)

```text
S(v_j) = S_base(v_j) + β · Σ_{i∈N(j)} S_base(v_i) · w_ij
```
- Aktivierung fließt über **Hebbian-Kanten** an Nachbarn.
- **β = 0.1** (spreading strength), **θ = 0.6** (spreading threshold).

**Ziel (HeLa-Mem):** „semantically distant but highly associated" Erinnerungen
abrufen → **Multi-Hop-Reasoning** (Aktivierung erreicht entfernte, aber verbundene Knoten).

---

## 3. Ablation (HeLa-Mem §4.3, wörtlich)

| Variante | Avg F1 |
|---|---|
| HeLa-Mem (Full) | **34.74** |
| **w/o Spreading Activation** | **32.19** |

→ **Deaktivieren von Spreading Activation kostet 2,55 Avg-F1-Punkte** (34.74 − 32.19). ✅

---

## 4. Implementierung (`data/memory/reflective_agent.py`)

**Klasse `DualPathRetrieval`:**
| Methode | Formel |
|---|---|
| `base_activation(graph, query, now)` | Eq. 3 |
| `spreading_activation(graph, s_base)` | Spreading |
| `retrieve(...)` | base → spread → θ-Schwelle → top_k |

**Parameter (HeLa-Mem):** τ=60, β=0.1, θ=0.6, α=1.0 (ENV-konfigurierbar).
**Ausführen:** `SPREAD_SIM=5 python3 data/memory/reflective_agent.py`

---

## 5. Test: 5 Multi-Hop-Abfragen

**Graph:** `data/memory/tier1-base/episodic_graph.json` (Hub n2 ↔ n0, n1, n3, n4; isoliert n5).

| Query | top_k | aktiviert (≥θ) | Spreading-Gewinn (Top) |
|---|---|---|---|
| „Rekursions-Zyklus Compare Revise" | n2, n4, n0, n1, n3 | n2, n4 | n0 +0.0692, n1 +0.0692, n3 +0.0554, n4 +0.0554 |
| „Solver Bug Integer-Division" | n0, n1, n2, n3, n4 | n0, n1 | **n2 +0.1280** |
| „HMM Traegheit Revise" | n4, n2, n5, n0, n1 | n2, n4 | (Nachbarn) |
| „Fast Write Routing entscheidet" | n3, n1, n2, n0, n4 | n3 | (Nachbarn) |
| „Minimum erstes Element" | n1, n2, n0, n3, n4 | n1 | (Nachbarn) |

**Beleg für Multi-Hop:** Query „Solver Bug" matcht **n0** (base hoch); **n2** (der Hub,
Nachbar von n0) erhält **+0.1280** Aktivierung **durch Spreading** – obwohl n2 dem
Query-Text semantisch fern ist. Das ist der „semantically distant but highly associated"-Effekt.

---

## 6. Quellen (HTTP 200, verifiziert 2026-10-01)

- HeLa-Mem (Base + Spreading Activation §3.4, Ablation §4.3): https://arxiv.org/abs/2604.16839
- HeLa-Mem ACL 2026: https://aclanthology.org/2026.acl-long.625/

---

## 7. Status

| Punkt | Status |
|---|---|
| Base Activation (Eq. 3) | ✅ `base_activation` |
| Spreading Activation | ✅ `spreading_activation` |
| Parameter (τ=60, β=0.1, θ=0.6) | ✅ wörtlich aus HeLa-Mem |
| 5 Multi-Hop-Abfragen | ✅ (Spreading-Gewinn nachgewiesen) |
| Ablation (2,55 F1) | ✅ dokumentiert |

**Ehrlich:** Formeln (Eq. 3 + Spreading) + Werte (τ=60, β=0.1, θ=0.6) + Ablation
(34.74→32.19 = 2,55) wörtlich aus HeLa-Mem (arXiv:2604.16839). Die Embedding-Ersatz-
funktion (`_embed`) ist eine Auftrags-Vereinfachung (kein Modell) – klar markiert.
