# data/memory – lokaler Speicher (MD-Abbild)

> Lab-Prinzip, MD-first. Hinweis: Dieses Verzeichnis ist das MD-Abbild
> des lokalen Speichers (Auftrag: lokal, kostenlos, keine Cloud).
> Kein Cloud-Dienst, keine Zusatzdienste.

## 3-Schicht-Gedächtnis-Pipeline (Auftrag + Quellen)

Das Gedächtnis ist als **dreischichtige Pipeline** aufgebaut:

| Schicht | Inhalt | Ordner | Quelle |
|---|---|---|---|
| **Tier 1 – Base Knowledge** | Identität, Ontologie (8 Stufen, 5 Phasen), Kernbeziehungen | `tier1-base/` | SHIMI (arXiv:2504.06135), ARIADNE (arXiv:2105.09864), Graphiti (arXiv:2501.13956) |
| **Tier 2 – Concept Index** | Konzept-zu-Ort-Mapping (selektives Laden) | `tier2-index/` | SHIMI (arXiv:2504.06135), SwiftMem (arXiv:2601.08160), A-MEM (arXiv:2502.12110) |
| **Tier 3 – Working Memory** | begrenzter LRU-Cache (max. 15 aktive Items) | `tier3-working/` | MemGPT (arXiv:2310.08560), Cortex (arXiv:2509.17360) |

**Ablauf:** Anfrage → Tier 2 (Concept Index) → passende Orte → Tier 3 (Working Memory, max 15, LRU).

## Status (Auftrag)

- **Tier 1:** angelegt (Identität, Ontologie, Kernbeziehungen befüllt).
- **Tier 2:** angelegt (Concept Index befüllt).
- **Tier 3:** angelegt (Working Memory, 0 aktive Items, max 15).
- **Fakten:** Noch keine Fakten abgelegt; erster Schreibvorgang via Skill `skills/store-memory/SKILL.md`.

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
