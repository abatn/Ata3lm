# data/memory – lokaler Speicher (MD-Abbild)

> Lab-Prinzip, MD-first. Hinweis: Dieses Verzeichnis ist das MD-Abbild
> des lokalen Speichers (Auftrag: lokal, kostenlos, keine Cloud).
> Kein Cloud-Dienst, keine Zusatzdienste.

## 3-Schicht-Gedächtnis-Pipeline (Auftrag + Quellen)

Das Gedächtnis ist als **dreischichtige Pipeline** aufgebaut — ergänzt um
**L4 Procedural Memory** (`skills/`) und einen **Shared Tier** (`shared/`):

| Schicht | Inhalt | Ordner | Quelle |
|---|---|---|---|
| **Tier 1 – Base Knowledge** | Identität, Ontologie (8 Stufen, 5 Phasen), Kernbeziehungen | `tier1-base/` | SHIMI (arXiv:2504.06135), ARIADNE (arXiv:2105.09864), Graphiti (arXiv:2501.13956) |
| **Tier 2 – Concept Index** | Konzept-zu-Ort-Mapping (selektives Laden) | `tier2-index/` | SHIMI (arXiv:2504.06135), SwiftMem (arXiv:2601.08160), A-MEM (arXiv:2502.12110) |
| **Tier 3 – Working Memory** | bounded Cache, **Default wertbewusste Eviction** (`policy="value"`), max. 15; reine LRU = Vergleichsbaseline | `tier3-working/` | MemGPT (arXiv:2310.08560), Cortex (arXiv:2509.17360) |
| **L4 – Procedural Memory** | Skills (versioniert, auditierbar, rückrollbar) | `skills/` (+ `versions/`) | Memory Survey (arXiv:2603.07670), TEA (arXiv:2506.12508), Mem^p (arXiv:2508.06433) |
| **Shared Tier** | gemeinsamer Store mehrerer Agenten (ACL + Sync) | `shared/` | Memory Survey §6.5/§9.6 (arXiv:2603.07670), Collaborative Memory (arXiv:2505.18279) |

**Ablauf:** Anfrage → Tier 2 (Concept Index) → passende Orte → Tier 3 (Working Memory, max 15, wertbewusste Eviction (Default)).
**L4:** Prozeduren (Skills) sind First-Class + versioniert. **Shared:** mehrere Agenten lesen/schreiben konfliktgeprüft (supersede statt löschen).

## Prozesse (`data/memory/*.py`)

| Datei | Aufgabe |
|---|---|
| `fast_write_router.py` | 3-Klassen-Kaskade (non-write/write-new/write-update) + MemRouter |
| `reflective_agent.py` | Konsolidierung (Hub-Distillation), Adaptive Forgetting (3 Bed.), Konfliktlösung, HMM-Trägheit, Spreading Activation |
| `ingestion_hook.py` | Lifecycle-Events, Encoding-Gate, asynchrone Enrichment-Queue |
| `trust.py` | Privacy (PII-Löschung), Poisoning-Guard, Bias-Check |
| `approval.py` | Zwei-Personen-Verifikation (EU-KI-VO Art. 14(5)); Flow pending → first_approved → second_approved → approved |
| `bias_monitor.py` | JSD-basierter Bias-Drift-Index (DI) + Capped-Simplex + Lyapunov-Damping |
| `bi_temporal.py` | Bi-temporaler Faktenspeicher (valid time × transaction time; supersede statt löschen) |
| `shared/shared_memory.py` | SharedTier (ACL, Trust, Versionierung, Supersession, Sync) |
| `tier3-working/lru_cache.py` | Working Memory (Default wertbewusste Eviction; reine LRU = Baseline) |

## Status (Auftrag)

- **Tier 1:** angelegt (Identität, Ontologie, Kernbeziehungen, episodischer Graph; `versions/v1`,`v2`,`v3`,`v4`).
- **Tier 2:** angelegt (Concept Index, Hub-Index, Evicted-Index).
- **Tier 3:** angelegt (Working Memory, max 15).
- **L4 Procedural:** `skills/` (14 aktive + `versions/vN/`, `AUDIT.md`).
- **Shared Tier:** `shared/` (ACL + Sync, Konflikt-Erkennung).
- **Fakten:** vorhanden — strukturiertes Wissen in `knowledge/structured/`
  (Entities/Relations, bi-temporal) + Inferenzen in `knowledge/cognition/`;
  Rohdaten/Provenienz in `ergebnisse/`.

## Ablageformat (Auftrag)

- Ein Fakt = ein MD-File (oder MD-Sektion) unter `data/memory/`.
- Dateiname (Auftrag): `YYYY-MM-DD-kurztitel.md`.
- Dualer Speicher als MD-Abbild:
  - **Graph-Anteil:** Knoten (Entitäten) + Kanten (Beziehungen) als
    Listen mit `[[Wiki-Links]]`.
  - **Vektor-Anteil:** als Platzhalter `embeddings: vorgesehen (lokal)`
    vermerken – keine Cloud-Embeddings.

## Pflichtfelder pro Fakt (Auftrag)

Jeder Fakt braucht alle drei Felder, sonst kein Schreibvorgang:

1. **Gültigkeit:** Validitätsfenster (`gueltig_von`, `gueltig_bis`;
   `gueltig_bis: offen` falls aktuell). Bei Widerspruch: alter Fakt wird
   invalidiert (`status: invalidiert`), NICHT gelöscht.
2. **Provenienz:** Episode (Quelleingabe) + Ablagezeitpunkt + Iteration
   (z. B. `t=1`).
3. **Quelle:** Link aus Auftrag oder den zugelassenen Quellen
   (Cognee-Repo, Cognee-Doku/Deployment, Graphiti-Repo, Zep-Paper);
   keine weiteren Quellen behaupten.

## Vorlage

```markdown
# Fakt: <Kurztitel>

- status: gueltig | invalidiert
- gueltig_von: YYYY-MM-DD
- gueltig_bis: YYYY-MM-DD | offen
- episode: <Kurzbeschreibung der Quelleingabe>
- quelle: <Link>
- iteration: t=<N>

## Knoten

- [[Entität A]]
- [[Entität B]]

## Kanten

- [[Entität A]] --<Beziehung>--> [[Entität B]]

## Embeddings

- embeddings: vorgesehen (lokal)
```

## Quellen (ausschließlich diese)

- https://github.com/topoteretes/cognee
- https://docs.cognee.ai/how-to-guides/cognee-sdk/deployment
- https://github.com/getzep/graphiti
- https://arxiv.org/html/2501.13956v1
