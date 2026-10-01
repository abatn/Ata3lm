# Reflective Agent – laufender Prozess (HeLa-Mem)

> Datum: 2026-10-01
> Zweck: Reflective Agent als laufender Prozess (Hub-Erkennung + Destillation).
> Quelle: **HeLa-Mem, ACL 2026, arXiv:2604.16839** (§3.3 + §4.4).
> Lab-Prinzip: Keine Erfindungen – Mechanismus wörtlich aus der Quelle.

---

## 0. Quellen-Korrektur (ehrlich)

| Angabe | Korrekt? |
|---|---|
| Aufgabe: „HeLa-Mem (ACL 2026), arXiv:2609.24663" | ❌ **falsch** |
| **HeLa-Mem** = arXiv:**2604.16839** + ACL 2026 | ✅ korrekt |
| arXiv:2609.24663 = **EvoPathBench** (nicht HeLa-Mem) | ℹ️ anderes Paper |

→ Verwendet wurde die **korrekte** HeLa-Mem-Quelle: **arXiv:2604.16839**.

---

## 1. Mechanismus (HeLa-Mem §3.3, wörtlich)

**Hub Detection (Eq. 2):**
```text
D(v_i) = Σ_{j∈N(i)} w_ij  >  δ_hub
```

**Hebbian Distillation (wörtlich):** „Upon detecting that a node's accumulative
weight exceeds the threshold δ_hub, the agent triggers Hebbian Distillation. To
capture the full context, the agent retrieves the hub node along with its strongly
connected neighbors. **The LLM synthesizes this cluster of related memories** to
identify common themes and causal relationships, **abstracting them into declarative
semantic entries.** These distilled records are stored in the **Semantic Memory Store**."

**Adaptive Forgetting (wörtlich):** „triggered when a node's status falls below
critical retention thresholds."

---

## 2. Laufender Prozess

**Datei:** `data/memory/reflective_agent.py`

```text
Loop:
  1. load_graph(data/memory/tier1-base/episodic_graph.json)
  2. Hub Detection:   D(v_i) = Σ w_ij > delta_hub
  3. Adaptive Forgetting: D(v_i) < retain_min
  4. Distillation: hub + neighbors -> LLM -> semantischer Eintrag
  5. Write: knowledge/structured/distilled-hub-<id>.md
  6. Update Index: data/memory/tier2-index/hub-index.md
```

**Parameter (Auftrag):** `HELA_DELTA_HUB` (default 1.0), `HELA_RETAIN_MIN` (default 0.05).

---

## 3. Test: Memory-Hub simuliert

**Eingabe-Graph** (`episodic_graph.json`): 6 Knoten, Hub `n2` mit 4 Kanten
(n0=0.5, n1=0.5, n3=0.4, n4=0.4), isolierter Knoten `n5`.

**Ausgabe (real):**
```json
{
  "hubs": ["n2"],
  "forgotten": ["n5"],
  "distilled": [{"hub": "n2", "score": 1.8, ...}]
}
```

| Schritt | Ergebnis |
|---|---|
| Hub Detection | **n2** (D=1.80 > δ_hub=1.0) |
| Adaptive Forgetting | **n5** (D=0 < retain_min) |
| Distillation (LLM) | semantischer Eintrag erzeugt |
| Write | `knowledge/structured/distilled-hub-n2.md` |
| Index-Update | `data/memory/tier2-index/hub-index.md` |

**LLM-destillierter Text (real):**
> „The recursion cycle (Observe→Compare→Revise) exhibits solver-specific bugs at t=4
> (integer division) and t=5 (first-element error) due to HMM-induced inertia in the
> Revise step (SEAA), which corrupts state propagation … and ultimately determines
> faulty output decisions in Fast Write Routing."

---

## 4. Ergebnis-Dateien

| Datei | Inhalt |
|---|---|
| `data/memory/reflective_agent.py` | laufender Prozess |
| `data/memory/tier1-base/episodic_graph.json` | Test-Graph (Hub n2) |
| `knowledge/structured/distilled-hub-n2.md` | destilliertes semantisches Wissen |
| `data/memory/tier2-index/hub-index.md` | aktualisierter Konzept-Index |

---

## 5. Quellen (HTTP 200, verifiziert 2026-10-01)

- **HeLa-Mem (korrekt):** https://arxiv.org/abs/2604.16839
- HeLa-Mem ACL 2026: https://aclanthology.org/2026.acl-long.625/
- HeLa-Mem Code: https://github.com/ReinerBRO/HeLa-Mem

---

## 6. Status

| Punkt | Status |
|---|---|
| Reflective Agent (laufender Prozess) | ✅ `data/memory/reflective_agent.py` |
| Hub-Erkennung (Eq. 2) | ✅ (n2, D=1.80) |
| Distillation (LLM) | ✅ (semantischer Eintrag) |
| Index-Update (tier2-index) | ✅ |
| Adaptive Forgetting | ✅ (n5) |

**Ehrlich:** Mechanismus (Hub Detection Eq. 2, Hebbian Distillation, Adaptive
Forgetting) wörtlich aus HeLa-Mem **arXiv:2604.16839**. Die Dateipfade sind die
Projekt-Bindung (Auftrag). Die Quellen-Angabe der Aufgabe (2609.24663) war falsch
und wurde korrigiert.
