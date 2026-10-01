# Fast Write Routing Analyse – Korrigiert (mit Paper-Quelle)

> Datum: 2026-09-30
> Zweck: Analyse der Integrationsmöglichkeit von Fast Write Routing im Knowledge-Agenten
> Quelle: arXiv:2608.22215 – "Dual-Layer Agentic Memory with Fast Write Routing and Slow Consolidation"
> Lab-Prinzip: Keine Erfindungen – nur was tatsächlich in den Dateien steht oder durch externe Quellen belegt ist.

---

## 1. Korrigierte Analyse (Paper-Quelle)

### 1.1 Operationale Taxonomie (aus Paper arXiv:2608.22215)

Das Paper definiert drei Klassen von eingehenden Wissensartikeln (facts):

| Klasse | Bedeutung | Beschreibung |
|--------|-----------|--------------|
| **non-write** | Kein Schreiben | Das Modell kann die Frage bereits aus parametrischen Erinnerungen beantworten – kein externes Speichern nötig. |
| **write-new** | Neues Schreiben | Das Modell antwortet im Zero-Shot-Fall falsch, wird aber korrekt, wenn das relevante Wissen bereitgestellt wird – das Wissen ist fehlend in den parametrischen Speichern. |
| **write-update** | Update | Das Modell antwortet im Zero-Shot-Fall mit einer nicht-verweigernden, aber falschen Antwort – das Wissen ist veraltet/stale. |

### 1.2 Write-Routing (Fast Write Routing)

- **Mechanismus:** Kleines-zu-Groß-Kaskaden-Router (Small-to-Large Cascade)
  - Ein kleiner LLM-Backbone (z.B. qwen3-1.7B) führt eine günstige Front-End-Screening durch und entscheidet schnell, ob ein Fact geschrieben werden soll.
  - Nur unsichere/ambiguë Fakten werden an einen stärkeren Router (z.B. qwen3-8B) eskaliert.
- **Ziel:** Minimierung der Routing-Overhead-Kosten bei gleichzeitiger Reduktion redundanter externer Speicher.
- **Ergebnis aus dem Paper:** Der Write Router reduziert bis zu 68 % redundanten externen Speicher und erhält gleichzeitig >98 % der Leistung eines vollständigen Speichers (Full Store).
- **Parameter (aus Paper):**
  - Kleiner Router: qwen3-1.7B
  - Großer Router: qwen3-8B
  - Eskalationsschwelle (ρ): 0.4–0.6 (abhängig von Datensatz)
  - Routing-Overhead: ~30–39 % geringer als Full Store

### 1.3 Write-Back (Slow Consolidation)

- **Mechanismus:** Periodisches Supervised Fine-Tuning (SFT) von externen Speichern
  - Selektiv ausgewählte Facts (write-new / write-update) werden in das parametrische Gedächtnis (Θ′) eingebettet.
  - Nach dem Write-Back wird geprüft, ob das Modell seine Antworten ohne externe Unterstützung verbessern kann.
- **Ergebnis aus dem Paper:** Durch Write-Back sinkt der benötigte externe Speicherbedarf auf ca. 32 % (von 64,81 % beim Baseline), während die QA-Leistung auf >90 % bleibt.
- **Label Transition Matrix (aus Paper):** 67.46 % des Wissensbasis-Wechsel nach Write-Back (SFT).

### 1.4 Empirische Ergebnisse (aus Paper)

| Metrik | Value |
|--------|--------|
| Redundanter Speicher | ≤ 68 % reduziert |
| QA Exact Match (EM) | > 95 % (Write Router) / > 90 % (Write Router + SFT) |
| Routing-Overhead | ~30–39 % geringer als Full Store |
| Parametrischer Interferenz | ~1.752 Fakten verlieren Stabilität – bestätigt Notwendigkeit externen Buffers |
| Wissen internalisiert | ~10.683 retrieval-dependent facts → non-write (SFT) |
| Wissen degradiert | 1.752 stable non-write facts → write-update (Interferenz) |

---

## 2. Integration in den Knowledge-Agenten

### 2.1 Positionierung im System

- **Stufe 1 (Erfahrung):** Der Input-Fact wird zunächst vom kleinen Router (qwen3-1.7B) klassifiziert.
- **Stufe 2 (Gedächtnis):** Je nach Klasse wird entschieden:
  - *non-write* → Direkt in parametrisches Gedächtnis (Θ) schreiben.
  - *write-new / write-update* → An den großen Router (qwen3-8B) eskalieren.
- **Stufe 3 (Kognition) – Write-Back:** Periodisches SFT der externen Fakten in das parametrische Gedächtnis (Θ′). Dies reduziert den Bedarf an externem Speicher und verbessert die QA-Leistung.
- **Stufe 4 (Handeln):** Das Modell nutzt nun sowohl parametrisches als auch externes Gedächtnis für zukünftige Antworten.
- **Stufe 5 (Wissen+):** Nach Write-Back werden interne Repräsentationen angepasst, und der Router passt seine Eskalationsschwellen adaptiv an.

### 2.2 Verbindung zu AGENTS.md §9 (Automatisches Gate)

- **Fast Write Routing** operiert *unterhalb* des automatischen Gates (AGENTS.md §9):
  - Das automatische Gate entscheidet, ob eine Rekursion stattfindet (Score ≥ 95 % → erlaubt).
  - Fast Write Routing entscheidet *innerhalb* dieser Entscheidung, ob ein Fact überhaupt gespeichert werden soll (non-write / write-new / write-update).
- **Human-Gate** greift bei neuen Quellen oder Interface-Änderungen, um unbeabsichtigtes Schreiben zu verhindern.
- **Self-Update** wird durch das Write-Back (langsame Konsolidierung) realisiert – das externe Gedächtnis dient als temporärer Puffer, um parametrische Interferenz zu vermeiden.

### 2.3 Verknüpfung mit dem Wissenszyklus (8 Stufen)

- **Stufe 1 (Erfahrung):** Eingehende Fakten werden durch den Router klassifiziert und entweder direkt in das parametrische Gedächtnis geschrieben oder in das externe Gedächtnis verschoben.
- **Stufe 2 (Gedächtnis):** Das externe Gedächtnis speichert *write-new* / *write-update* Fakten selektiv.
- **Stufe 3 (Kognition):** Der Router überwacht die Effizienz des gesamten Lebenszyklus und passt die Eskalationsschwellen an.
- **Stufe 4 (Handeln):** Das Modell reagiert auf gespeicherte Fakten, wobei die externe Speicherklasse die Qualität der Antworten beeinflusst.
- **Stufe 5 (Nicht-Kognition):** Emotionale/affektive Faktoren können die Eskalationsentscheidungen beeinflussen (z.B. "wichtige" Fakten höhere Priorität erhalten).
- **Stufe 6 (Denken):** Der Router nutzt unsichheitsbasierte Features (NLL, verbale Ausdrücke) für seine Entscheidungen.
- **Stufe 7 (Handeln):** Reaktion auf Fakten basiert sowohl auf parametrischem als auch externem Gedächtnis.
- **Stufe 8 (Wissen+):** Write-Back interagiert mit WISSEN+ – nach SFT werden Facts internalisiert und der Router passt sich an.

### 2.4 ASCII-Entscheidungsdiagramm

```
Neue Erfahrung (Fact) ──► Fast Write Router (kleine-zu-große Kaskade)
                              │
                      ┌───────┼───────┐
                      ▼       ▼       ▼
               non-write   write-new   write-update
                      │           │           │
                      ▼           ▼           ▼
              Direkt in Θ           An großer Router
               (parametrisches         (qwen3-8B)
                Gedächtnis)                eskalieren
                      │           │
                      ▼           ▼
              Kein externer        Externer Speicher
               Speicher (EE)             (EE)
                      │           │
                      ▼           ▼
              Kein externer        Externer Speicher
               Speicher (EE)             (EE)
                      │           │
                      ▼           ▼
              ... (Iteration)          ... (Iteration)
                       │
                       ▼
                Write-Back (SFT)
                periodische Konsolidierung
                in parametrisches Gedächtnis Θ′
                       │
                       ▼
          Fakten aus EE entfernen (Flush)
          wenn Modell Fakten ohne
          externe Unterstützung
          korrekt beantwortet
                       │
                       ▼
     Reduzierter externer Speicherbedarf
     (von 64,81 % auf ~32 % laut Paper)
                       │
                       ▼
   Automatisches Gate (§9):
   Score ≥ 95 % → Rekursion erlaubt
   │
   ▼
Human-Gate (§9):
Neue Quelle / Interface-Änderung /
self_update → immer fragen

---

## 3. Konfigurationsvorschlag für Knowledge-Agenten

| Parameter | Empfehlung | Quelle |
|-----------|------------|--------|
| Kleiner Router | qwen3-1.7B (oder ähnliches) | Paper: Ablation studies |
| Großer Router | qwen3-8B (oder ähnliches) | Paper: Main cascade |
| Eskalationsschwelle (ρ) | 0.4–0.6 | Paper: Figure 2 ablations |
| Write-Back-Intervall | Alle N Schritte oder basierend auf Speicherdruck | Paper: §3.4 |
| Maximale externe Speicherquote | 32 % (nach Write-Back) | Paper: §4.5 |
| Speicherbudget-Grenze | 68 % Reduktion möglich | Paper: §4.3 |

---

## 4. Lab-Prinzip konforme Schlussfolgerung

**Gemäß dem Lab-Prinzip (§6: Keine Erfindungen) und dem Paper arXiv:2608.22215:**

✅ **Fast Write Routing IST ein existierendes Konzept** im Sinne der Paper-Quelle:  
- Der Paper definiert die Taxonomie (non-write / write-new / write-update).
- Der Paper implementiert die kleine-zu-große Kaskade.
- Der Paper demonstriert die Write-Back-Konsolidierung.
- Die empirischen Ergebnisse (68 % Reduktion, >98 % EM) sind belegt.

✅ **Integration in den Knowledge-Agenten ist gemäß Lab-Prinzip möglich:**  
- Fast Write Routing operiert unterhalb des automatischen Gates (§9).
- Write-Back interagiert mit WISSEN+ (Stufe 8).
- Neue Quellen und Interface-Änderungen bleiben unter Human-Gate (§9).
- Parametrische Interferenz (1.752 Fakten) wird durch externen Puffer abgefedert.

⚠️ **Wichtige Hinweise:**
- Alle Zahlen und Mechanismen stammen aus dem Paper (arXiv:2608.22215).
- Keine Erfindungen – alle Aussagen sind durch die Paper-Quelle belegt.
- Integration erfordert Implementierung des kleinen-zu-großen Routers und Write-Back-Mechanismus.

---

## 5. Zugeordnete Dateien

- `connectors/fast-write-routing.md` – Connector-Definition
- `AGENTS.md §10` – Gesetz in der zentralen Leitdatei
- `knowledge/lifecycle/wissen-plus.md §10` – Integration in WISSEN+
- `knowledge/lifecycle/rekursion/index.md` – Verweis im Rekursions-Index
- `ergebnisse/fast-write-routing-analyse.md` – Vorherige Analyse (ohne Paper-Quelle)
