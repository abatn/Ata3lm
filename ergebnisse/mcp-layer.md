# MCP-Layer – optional über lokaler Memory (mit Fallback)

> Datum: 2026-10-01
> Zweck: MCP als Layer über der lokalen Memory – nicht als Ersatz.
> Lab-Prinzip: Keine Erfindungen – Konzept + Fallback mit Quellen-Link (HTTP 200).
> Geltung: `AGENTS.md` §11 (neu), §10 (Fast Write Routing).

---

## 1. Layer-Architektur

| Layer | Inhalt | Verfügbarkeit | Quelle |
|---|---|---|---|
| **Basis (Pflicht)** | lokale Memory (`data/memory/`, 3-Tier) | **immer** (lokal, keine Cloud) | `data/memory/README.md` |
| **Optional** | MCPs: Cognee, Graphiti, HeLa-Mem | optional (kann ausfallen) | arXiv:2608.22215 |

**Quelle (Dual-Layer):** arXiv:2608.22215 – „At the carrier layer, the agent
maintains **parametric memory** for stable, compressed, low-cost knowledge and
**external memory** for dynamic, editable, high-risk facts."

```text
Anfrage ─▶ MCP-Layer (Cognee/Graphiti/HeLa-Mem)
              │
     ┌────────┴────────┐
     ▼                 ▼
  antwortet        antwortet NICHT
     │                 │
     ▼                 ▼
  MCP-Ergebnis     lokale Memory (data/memory/) – Fallback
```

---

## 2. Fallback-Regel

**Quelle (MCP-Fallback):** arXiv:2504.21030 – „**Error handling and fallback
strategies:** Gracefully handling server unavailability, request failures, or
other exceptional conditions."; „**Graceful degradation** to maintain partial
functionality".

- Wenn ein MCP nicht antwortet → **lokale Memory übernimmt** (Basis-Layer).
- Kein Datenverlust: die lokale Memory ist die Pflicht-Basis.

---

## 3. Test: MCP-Ausfall simuliert

| Schritt | Aktion | Ergebnis (real) |
|---|---|---|
| 1 | MCP-Versuch (Graphiti, Port 6380) | ✅ erreichbar |
| 2 | Simulierter Ausfall (Port 9999) | ❌ Connection refused → **Fallback ausgelöst** |
| 3 | Fallback: lokale Memory (`data/memory/tier1-base/identity.md`) | ✅ antwortet (Basis-Layer) |

**Rohe Ausgabe Schritt 3:**
```text
# Tier 1 – Base Knowledge: Identität
> Schicht: Tier 1 (Base Knowledge) der 3-Schicht-Gedächtnis-Pipeline.
```

**Ergebnis:** Bei MCP-Ausfall übernimmt die lokale Memory → kein Ausfall des
Gesamtsystems (graceful degradation).

---

## 4. Guardrails (AGENTS.md §11.3)

- MCPs sind **optional**; die lokale Memory ist die **Pflicht-Basis**.
- Kein Schreibvorgang nur in einen MCP (lokale Memory muss den Fakt ebenfalls halten).
- MCP-Ausfall → Fallback auf lokale Memory (kein Datenverlust).

---

## 5. Quellen (HTTP 200, verifiziert 2026-10-01)

- Dual-Layer Agentic Memory (parametric + external): https://arxiv.org/abs/2608.22215
- MCP-Integration (Error handling & fallback, graceful degradation): https://arxiv.org/abs/2504.21030
- MCP-Spezifikation: https://modelcontextprotocol.io/
- Graphiti (temporaler Graph): https://arxiv.org/abs/2501.13956
- Cognee MCP: https://docs.cognee.ai/cognee-mcp/mcp-overview

---

## 6. Status

| Punkt | Status |
|---|---|
| Layer-Architektur | ✅ dokumentiert (AGENTS.md §11) |
| Fallback | ✅ dokumentiert + getestet |
| MCP-Ausfall simuliert | ✅ (Port 9999 → Connection refused → lokale Memory) |
| Quellen | ✅ (2608.22215, 2504.21030, MCP-Spec) |

**Ehrlich:** Das Dual-Layer-Konzept (parametric + external memory) stammt aus
arXiv:2608.22215; die Fallback-Strategie (graceful degradation) aus arXiv:2504.21030.
Die lokale Memory (`data/memory/`) ist die Pflicht-Basis; MCPs sind optional.
