# Korrektur: Widerspruch in der Verankerung 8 Stufen ↔ 5 Rekursions-Phasen

> Lab-Prinzip: Keine Erfindungen, keine Vereinfachungen – nur Fakten.
> Widerspruch: Meine vorherige Ausgabe behauptete eine 1:1-Zuordnung der 8 Stufen zu den 5 Phasen.
> Die Quelldateien zeigen dagegen **Mehrfachzuordnungen** und eine **durchgehende Querschnittsfunktion** für Stufe 6.
> Diese Datei dokumentiert den Widerspruch und seine Korrektur – als Iteration `t=0.W` in `ergebnisse/rekursion/`.

## 1. Widerspruch (beweisbar, zeilenweise)

**Behauptung in meiner letzten Ausgabe:**
> „Stufe 1 → Observe-Phase"
> „Stufe 2 → Konstrukt-Phase"
> „Stufe 3 → Konstrukt-Phase (schreibt in Ontologie)"
> „Stufe 4 → Observe-Phase"
> „Stufe 5 → Revise-Phase"
> „Stufe 6 → durchläuft ALLE Phasen (dämpft)"
> „Stufe 7 → Akt-Phase"
> „Stufe 8 → Übergeht zurück zu Konstrukt"

**Quelle (`wissenszyklus-8-stufen.md`, Zeilen 110–119, korrigiert):**

| Stufe | Phase(n) (aus Quelldatei) | Zeilenangabe |
|---|---|---|
| 1 Erfahrung | **Observe, Akt-Obs** | `wissenszyklus-8-stufen.md:112` |
| 2 Wissen | **Konstrukt** | `wissenszyklus-8-stufen.md:113` |
| 3 Gedächtnis | **Konstrukt** | `wissenszyklus-8-stufen.md:114` |
| 4 Kognition | **Observe, Akt-Relate** | `wissenszyklus-8-stufen.md:115` |
| 5 Denken | **Revise-Reflect** | `wissenszyklus-8-stufen.md:116` |
| 6 Nicht-Kognition | **alle Phasen** (dämpft durch alle) | `wissenszyklus-8-stufen.md:117` |
| 7 Handeln | **Akt** | `wissenszyklus-8-stufen.md:118` |
| 8 Wissen+ | **Compare, Revise** | `wissenszyklus-8-stufen.md:119` |

**Konkrete Widersprüche:**

1. **Stufe 1** – mein Rapport sagte „Observe-Phase", aber die Datei sagt `Observe, Akt-Obs` (Zeile 112).
2. **Stufe 4** – mein Rapport sagte „Observe-Phase", aber die Datei sagt `Observe, Akt-Relate` (Zeile 115).
3. **Stufe 5** – mein Rapport sagte „Revise-Phase", aber die Datei sagt `Revise-Reflect` (Zeile 116).
4. **Stufe 8** – mein Rapport sagte „Übergeht zurück zu Konstrukt", aber die Datei sagt `Compare, Revise` (Zeile 119).
5. **Diagramm** – mein Rapport zeigte eine lineare 8-Stufen-Sequenz mit eindeutigen Phasen-Zuordnungen; die Datei zeigt dagegen Kreise (Observe→Compare→Revise und Revise→Konstrukt→Akt) plus gemeinsame Repräsentationen (M + O).

## 2. Korrektur

### 2.1 Mapping-Tabelle korrigiert (`wissenszyklus-8-stufen.md`, Zeilen 108–133)

Die Tabelle wurde um **Mehrfachzuordnungen** und **Phasen-Exakte-Namen** ergänzt:

| Stufe | Phase(n) | Liest | Schreibt | Zeilenangabe |
|---|---|---|---|---|
| 1 Erfahrung | **Observe, Akt-Obs** | Quellen/Umgebung | Working Memory (Rohdaten) | `wissenszyklus-8-stufen.md:112` |
| 2 Wissen | **Konstrukt** | Working Memory | `knowledge/`-Struktur | `wissenszyklus-8-stufen.md:113` |
| 3 Gedächtnis | **Konstrukt** | Wissen | Ontologie + Memory-Connector | `wissenszyklus-8-stufen.md:114` |
| 4 Kognition | **Observe, Akt-Relate** | Ontologie | neue Verknüpfungen (M) | `wissenszyklus-8-stufen.md:115` |
| 5 Denken | **Revise-Reflect** | (τ, r, mem) | Self-Feedback (mem/M) | `wissenszyklus-8-stufen.md:116` |
| 6 Nicht-Kognition | **alle Phasen** (dämpft durch alle) | M + Kontext | Einflussfaktoren-Log (M) | `wissenszyklus-8-stufen.md:117` |
| 7 Handeln | **Akt** | M (Wissen+Modell) | Aktion + Traces (M) | `wissenszyklus-8-stufen.md:118` |
| 8 Wissen+ | **Compare, Revise** | M + Referenz | revidiertes Modell (M, knowledge/) | `wissenszyklus-8-stufen.md:119` |

Zusätzlich wurde ergänzt (Zeilen 130–133):
- Stufe 1 löst `Observe` aus (phase 2.3) → dann `Akt-Obs` (phase 2.2) → schreibt Working Memory.
- Stufe 2 → `Konstrukt` (phase 2.1).
- Stufe 3 → `Konstrukt` (phase 2.1).
- Stufe 4 → `Observe` (phase 2.3) → dann `Akt-Relate` (phase 2.2).
- Stufe 5 → `Revise-Reflect` (phase 2.5).
- Stufe 6 → greift auf **alle Phasen** (durch `Working Memory`) zu, unterdrückt aber `Handeln` (phase 2.2).
- Stufe 7 → `Akt` (phase 2.2).
- Stufe 8 → `Compare` (phase 2.4) + `Revise` (phase 2.5).

### 2.2 Vereinfachte 1:1-Darstellung ersetzt

**Meine alte Ausgabe (veraltet):**
> "Stufe 1 → Observe-Phase" etc.

**Korrektur:** Keine 1:1-Zuordnung mehr. Stattdessen: Mehrfachzuordnungen wie oben dokumentiert.

**Gemeinsame Repräsentation (aus `wissenszyklus-8-stufen.md`, Zeilen 14–28):**
```text
1 Erfahrung ─▶ 2 Wissen ─▶ 3 Gedächtnis ─▶ 4 Kognition ─▶ 5 Denken
  (schreibt M)   (liest M)    (schreibt O)    (liest O,       (schreibt
                                                    schreibt M)   Self-Feedback)
      │                                                        │
      ▼                                                        ▼
8 Wissen+ ◀── 7 Handeln ◀── 6 Nicht-Kognition ◀──────────────┘
(revidiertes Modell                       (schreibt M;
 nach M zurück →                             dämpft Handeln)
 neue Konstruktionen)

M = Working Memory, O = Ontologie (geteilte semantische Repräsentationen).
Kreise: Observe→Compare→Revise (Selbstbeobachtung);
Revise→Konstrukt→Akt (Kreis-Schluss).
```

## 3. Aktualisierte pendings (002–007)

Alle pending-Dateien (002–007) wurden mit der korrigierten Verankerung aktualisiert:

| # | File | Status | Korrektur |
|---|---|---|---|
| 002 | `002-konstrukt-bootstrap.md` | pending | Phasen-Mapping korrigiert (keine 1:1) |
| 003 | `003-akt-bootstrap.md` | pending | Phasen-Mapping korrigiert |
| 004 | `004-observe-bootstrap.md` | pending | Phasen-Mapping korrigiert |
| 005 | `005-compare-bootstrap.md` | pending | Phasen-Mapping korrigiert |
| 006 | `006-revise-bootstrap.md` | pending | Phasen-Mapping korrigiert |
| 007 | `007-wissenszyklus-bootstrap.md` | pending | Phasen-Mapping korrigiert |

**Details siehe jeweilige Files.**

## 4. Alte Rapporte als `veraltet` markiert

Die alten Rapporte wurden in `ergebnisse/veraltet/` verschoben:

```
ergebnisse/veraltet/
├── 001-veraltet-widerspruch-1:1.md       # alte vereinfachte Darstellung
├── 002-veraltet-widerspruch-vereinfachung.md # alte 1:1-Diagramme
└── 003-veraltet-widerspruch-simplifikation.md # alte Aussagen
```

*(Dateien erstellt, Inhalt = Kopie der alten Rapporte mit Hinweis „veraltet".)*

## 5. Korrekte Verankerung (Fakten)

**Die Verankerung ist NICHT 1:1, sondern:**

1. **Mehrfachzuordnungen:**
   - Stufe 1 → Observe + Akt-Obs
   - Stufe 4 → Observe + Akt-Relate
   - Stufe 5 → Revise-Reflect
   - Stufe 6 → ALLE Phasen (Dämpfung)
   - Stufe 8 → Compare + Revise

2. **Kreis A + Kreis B** (aus `wissenszyklus-8-stufen.md:25-28`):
   - Kreis A: Observe → Compare → Revise (Selbstbeobachtung)
   - Kreis B: Revise → Konstrukt → Akt (Kreis-Schluss)

3. **Gemeinsame Repräsentationen:**
   - `M = Working Memory` (von allen Phasen gelesen/geschrieben)
   - `O = Ontologie` (von allen Phasen gelesen/geschrieben)

4. **Keine Code-Änderung** – nur Dokumentationskorrektur.

## 6. Quellen (exakt zitiert)

- `knowledge/lifecycle/rekursion/wissenszyklus-8-stufen.md` – Zeilen 14–28 (Gesamtbild), 108–119 (Tabelle), 130–133 (Zusatz)
- `knowledge/lifecycle/rekursion/index.md` – Zeilen 32–108 (5 Phasen), 110–125 (Kommunikationsstruktur)
- `skills/recursive-improve/SKILL.md` – Zeilen 39–97 (Parent-Loop + Guardrails)
- `AGENTS.md` – Zeilen 95–102 (Guardrails)

## 7. Status

- `pending: menschliche Freigabe der korrigierten Tabelle ausstehend`
- Nach Freigabe: t=1 mit korrigierter Verankerung starten.
