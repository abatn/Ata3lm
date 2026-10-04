# Fast Write Routing – Connector

## Titel
Fast Write Routing (Dual-Layer Agentic Memory)

## Quelle
arXiv:2608.22215 – "Dual-Layer Agentic Memory with Fast Write Routing and Slow Consolidation"

## Kernfunktion
Ein billiger Klassifikator (kleine-zu-große Kaskade) entscheidet, ob ein Fact in das externe Gedächtnis geschrieben wird (non-write, write-new, write-update). Der Router minimiert Routing-Overhead und reduziert redundante Speicher.

## Integration in den Knowledge-Agenten

### 1. Stufe 1 (Erfahrung) – Input-Fact
- Der neue Fact wird vom Fast Write Router klassifiziert.
- **non-write** → Direkt in parametrisches Gedächtnis (Θ) schreiben.
- **write-new / write-update** → An den großen Router (qwen3-8B) eskalieren.

### 2. Stufe 2 (Gedächtnis) – Speicherung
- **non-write** Fakten bleiben im parametrischen Gedächtnis.
- **write-new / write-update** Fakten werden in das externe Gedächtnis (EE) verschoben.
- Das externe Gedächtnis dient als temporärer Puffer gegen katastrophales Vergessen.

### 3. Stufe 3 (Kognition) – Write-Back (langsame Konsolidierung)
- Periodisches SFT der externen Fakten in das parametrische Gedächtnis (Θ′).
- Dies reduziert den Bedarf an externem Speicher und verbessert die QA-Leistung.

### 4. Stufe 4 (Handeln) – Antwort
- Das Modell nutzt sowohl parametrisches als auch externes Gedächtnis für Antworten.
- Die externe Speicherklasse wird dynamisch angepasst, je nachdem, welche Fakten internisiert wurden.

## Write-Aktion (Implementierung, AGENTS.md §10.7)

`data/memory/fast_write_router.py::apply_write_action(cls, ...)` schreibt die Ziele real:

| Klasse | Ziel | Gate |
|---|---|---|
| **non-write** | nur `ergebnisse/` (Historie), **kein** Memory-Write | none |
| **write-new** | `knowledge/structured/` + `data/memory/tier3-working/` | ask (neue Quelle) |
| **write-update** | `knowledge/structured/` + tier1 **Supersede** (alt archiviert `<key>.superseded-<ts>.md`, **nicht gelöscht**) | ask (`self_update`) |

**Caveat (ehrlich):** Das Paper routet operational **binär** „write or discard"
(§3.3); die 3 Klassen sind Trainings-**Labels**. Die 3-Klassen-**Aktionen** sind
Projekt-**Auftrag** (AGENTS.md §10.7), kein Paper-Claim.
Test: `tests/test_fwr_write.py` · Doku: `ergebnisse/fwr-write.md`.

## Verbindungen zu anderen Komponenten

- **AGENTS.md §9 (Automatisches Gate):** Fast Write Routing arbeitet unterhalb des automatischen Gates (Score ≥ 95 % → erlaubt). Es entscheidet innerhalb der Entscheidung, ob ein Fact gespeichert wird.
- **AGENTS.md §10 (neu):** Fast Write Routing ist Teil des Wissenslebenszyklus (Dual-Layer Agentic Memory).
- **Index.md:** Verweis auf §10 Fast Write Routing.
- **Wissenszyklus-8-stufen.md:** Integration in Stufe 1 (Erfahrung) und Stufe 2 (Gedächtnis).

## Parameter (empfohlen)
- **Router-Konfiguration:**
  - Kleiner Router: qwen3-1.7B (oder ähnliches kleines LLM)
  - Großer Router: qwen3-8B
  - Eskalationsschwelle (ρ): 0.4–0.6 (abhängig von Datensatz)
- **Write-Back-Intervalle:** Alle N Schritte oder basierend auf Speicherdruck
- **Speicherdruck:** Maximale externe Speicherquote (z.B. 32 % wie im Paper)

## Vorteile
- Reduziert redundante Speicher um bis zu 68 %
- Erhält >98 % der QA-Leistung (Full Store)
- Geringer Routing-Overhead dank kleinschrittiger Kaskade
- Paradoxerweise erhöht die externe Speicherung die QA-Leistung (durch bessere Abdeckung von seltenen Fakten)

## Herausforderungen
- **Parametrischer Interferenz:** Kontinuierliches Update kann alte Fakten beschädigen (siehe Paper: 1.752 Fakten verlieren Stabilität). Dies rechtfertigt den externen Puffer.
- **Latenz:** Write-Back erfordert periodisches SFT – kann durch asynchrone Prozesse oder kontinuierliches Lernen (z.B. Online LoRA) gemildert werden.
- **Epistemische Verschiebung:** Nach Write-Back müssen Fakten, die internisiert wurden, erneut überprüft werden (adaptives Discarding).

## Referenzen
- Li, W., Nie, D., Lan, R., Lyu, T., Wang, P., Hong, L., Pan, W., & Pan, B. (2026). *Dual-Layer Agentic Memory with Fast Write Routing and Slow Consolidation*. arXiv:2608.22215.


## Prozess (Aufruf) [Auftrag]

Dieser Connector bedient: `fast_write_router.py` — Klassifikation/Write.

MCP-Interface / Ontologie-Validierung (SHACL, W3C): https://www.w3.org/TR/shacl/ · `ergebnisse/connector-prozess.md`.
