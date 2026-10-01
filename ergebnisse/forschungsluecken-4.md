# Vier Forschungslücken – konsolidierter Stand (Code + Doku + Selbsttest)

> Datum: 2026-10-01
> Prinzip: Keine Erfindungen (§6). Jede Aussage **Belegt** (Quelle, HTTP 200) oder **Auftrag**.
> Diese Datei bündelt die vier Punkte (Details je Punkt in den verlinkten Einzeldokumenten).

## Übersicht

| # | Lücke | Code | Quelle | Status |
|---|---|---|---|---|
| 1 | L4-Operationalisierung | `skills/procedural_memory.py` | Memory Survey, TEA, Mem^p | Belegt + Auftrag |
| 2 | Shared-Konfliktauflösung (Trust-Supersession) | `data/memory/shared/shared_memory.py` | LatticeMind, Governed Collaborative Memory | Belegt + Auftrag |
| 3 | Drift-Index (JSD) | `data/memory/bias_monitor.py` | Causal Audit Framework (WhyLab), Agent Drift | Belegt + Auftrag |
| 4 | GLiNER-Prinzip (ehrlich) | `data/memory/ingestion_hook.py` | GraphRAG-SDK, GLiNER-Relex | Belegt (Prinzip) / Auftrag (Regeln) |

---

## 1. L4-Operationalisierung — versioniert, auditierbar, rückrollbar

- **Code:** `skills/procedural_memory.py` — `snapshot()`, `propose_update(approved)`,
  `rollback()`, `audit()`; Ablage `skills/<name>/versions/vN/` + `skills/AUDIT.md`.
- **Quellen (HTTP 200):** Memory Survey (arXiv:2603.07670, „first-class system component";
  temporal versioning) · TEA (arXiv:2506.12508, „first-class, versioned resources" + Rollback) ·
  Mem^p (arXiv:2508.06433, „first-class optimization object").
- **Selbsttest:**
  ```text
  ohne approved -> applied=False status=pending (kein Write)
  mit approved  -> applied=True  version=v9
  rollback      -> {'ok': True, 'restored': 'v1', 'saved_current_as': 'v10'}
  ```
- **Status:** First-Class/Versioning/Rollback/Gate = **Belegt**; `versions/vN`-Mechanik = **Auftrag**.
- **Detail:** `skills/README.md`, `ergebnisse/l4-operational.md`.

## 2. Shared-Memory-Konfliktauflösung — Trust-Supersession + `superseded_by`

- **Code:** `data/memory/shared/shared_memory.py` — Write-Time-Konfliktlösung, Status
  `confirmed | superseded | contested`, `superseded_by`, `validate_write` (Kollisionsvalidierung).
- **Quellen (HTTP 200):** LatticeMind (arXiv:2608.08236, write-time, Status, Checker, Supersession) ·
  Governed Collaborative Memory (arXiv:2605.04264, „supersede-not-erase", version lineage).
- **Selbsttest:**
  ```text
  v1 berechne_durchschnitt | agentA(0.5) | superseded | superseded_by v2
  v2 berechne_median        | agentB(0.9) | confirmed  | supersedes v1
  v3 berechne_summe         | agentC(0.3) | superseded | superseded_by v2
  ```
- **Status:** Mechanik = **Belegt**; Trust-Grenze = **Auftrag**.
- **Detail:** `ergebnisse/shared-supersession.md`, `data/memory/shared/README.md`.

## 3. Drift-Index-Formalisierung — JSD + Signalgewichtung + Lyapunov-Damping

- **Code:** `data/memory/bias_monitor.py` — `jsd()`, `entropy()`, `capped_simplex(w_max=0.6)`,
  `BiasDriftMonitor` (DI = JSD), `damping = max(0, 1 − 10·DI)`.
- **Quellen (HTTP 200):** Causal Audit Framework / WhyLab (C1 information-theoretic Drift Index,
  C3 Lyapunov-bounded adaptive damping; `github.com/neogenesislab/WhyLab-NeurIPS2026`) ·
  Agent Drift (arXiv:2601.04170, JSD).
- **Selbsttest (10 self_updates):**
  ```text
  self_update  1: DI(JSD)=0.0006 damping=0.994 -> ok
  self_update  6: DI(JSD)=0.0243 damping=0.757 -> ask   (τ=0.02 überschritten)
  ```
- **Status:** JSD-Drift + Lyapunov-Damping = **Belegt**; Entropie-Gewichtung/`w_max`/τ = **Auftrag**.
- **Detail:** `ergebnisse/drift-index.md`.
- **Hinweis (Lyapunov `E[ΔV] ≤ 0`):** WhyLab C3 = „Lyapunov-bounded adaptive damping"; unsere
  Damping-Funktion ist monoton fallend mit dem Drift (Auftrag-Implementierung der Schranke).

## 4. GLiNER-Prinzip — ehrlich eingeordnet (pluggable)

- **Code:** `data/memory/ingestion_hook.py` — `resolve_entities(text, backend="auto"|"gliner"|"rules")`.
  - `gliner_available()` prüft, ob **echtes GLiNER** importierbar ist; wenn ja → `GLiNER.from_pretrained(...)`
    (GraphRAG-SDK Step 1).
  - sonst → **regelbasiert** (`backend="rules"`, als **Auftrag** markiert).
- **Quellen (HTTP 200):** GraphRAG-SDK (FalkorDB, Step 1 `GLiNERExtractor`, lokal, keine API-Calls) ·
  GLiNER-Relex (arXiv:2605.10108, deterministische lokale NER+RE).
- **Selbsttest:**
  ```text
  gliner_available: False
  backend=auto  : [('Concept','Knowledge-Agent','rules'), ('Concept','Fast Write Routing','rules'), ('Phase','Konstrukt','rules')]
  backend=gliner: []      # explizit angefordert, aber GLiNER nicht installiert
  ```
- **Status:** GLiNER-**Prinzip** (lokal, deterministisch, reproduzierbar) = **Belegt**;
  die regelbasierte Umsetzung in dieser Umgebung = **Auftrag** (echtes GLiNER nicht installiert →
  Backend ist vorbereitet, greift automatisch, sobald `pip install gliner`).
- **Detail:** `ergebnisse/ingestion-hook.md`.

---

## Quellen (alle HTTP 200, 2026-10-01)

- Memory Survey: https://arxiv.org/abs/2603.07670
- TEA-Protokoll: https://arxiv.org/abs/2506.12508
- Mem^p: https://arxiv.org/abs/2508.06433
- LatticeMind: https://arxiv.org/abs/2608.08236
- Governed Collaborative Memory: https://arxiv.org/abs/2605.04264
- Causal Audit Framework (WhyLab): https://github.com/neogenesislab/WhyLab-NeurIPS2026
- Agent Drift: https://arxiv.org/abs/2601.04170
- GraphRAG-SDK: https://github.com/FalkorDB/GraphRAG-SDK
- GLiNER-Relex: https://arxiv.org/abs/2605.10108
