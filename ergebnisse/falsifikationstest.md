# Falsifikationstest: Behauptung zur Mapping-Tabelle

> Lab-Prinzip: Keine Erfindungen, keine Anpassung an die Behauptung – nur Fakten.

## Geprüfte Behauptung

> "Stufe 1 (Erfahrung) = nur Observe
> Stufe 4 (Kognition) = nur Observe
> Stufe 6 (Nicht-Kognition) = nur Revise
> Stufe 8 (Wissen+) = nur Konstrukt"

## Prüfung (Zeile für Zeile gegen `wissenszyklus-8-stufen.md` Zeilen 110–119)

### Stufe 1 (Erfahrung)

- **Behauptung:** "Stufe 1 (Erfahrung) = nur Observe"
- **Datei `wissenszyklus-8-stufen.md:112` sagt wörtlich:**
  `| 1 Erfahrung | **Observe, Akt-Obs** | Quellen/Umgebung | Working Memory (Rohdaten) |`
- **Ergebnis:** **FALSCH** ("Observe, Akt-Obs" ≠ "nur Observe")

### Stufe 4 (Kognition)

- **Behauptung:** "Stufe 4 (Kognition) = nur Observe"
- **Datei `wissenszyklus-8-stufen.md:115` sagt wörtlich:**
  `| 4 Kognition | **Observe, Akt-Relate** | Ontologie | neue Verknüpfungen (M) |`
- **Ergebnis:** **FALSCH** ("Observe, Akt-Relate" ≠ "nur Observe")

### Stufe 6 (Nicht-Kognition)

- **Behauptung:** "Stufe 6 (Nicht-Kognition) = nur Revise"
- **Datei `wissenszyklus-8-stufen.md:117` sagt wörtlich:**
  `| 6 Nicht-Kognition | **alle Phasen** (dämpft durch alle) | M + Kontext | Einflussfaktoren-Log (M) |`
- **Ergebnis:** **FALSCH** ("alle Phasen" ≠ "nur Revise")

### Stufe 8 (Wissen+)

- **Behauptung:** "Stufe 8 (Wissen+) = nur Konstrukt"
- **Datei `wissenszyklus-8-stufen.md:119` sagt wörtlich:**
  `| 8 Wissen+ | **Compare, Revise** | M + Referenz | revidiertes Modell (M, knowledge/) |`
- **Ergebnis:** **FALSCH** ("Compare, Revise" ≠ "nur Konstrukt")

## Beweis (komplette Tabellen-Abstecher)

Exakt wie in `wissenszyklus-8-stufen.md` Zeilen 110–119:

```
| Stufe | Phase(n) | Liest | Schreibt |
|---|---|---|---|
| 1 Erfahrung | Observe, Akt-Obs | Quellen/Umgebung | Working Memory (Rohdaten) |
| 2 Wissen | Konstrukt | Working Memory | `knowledge/`-Struktur |
| 3 Gedächtnis | Konstrukt | Wissen | Ontologie + Memory-Connector |
| 4 Kognition | Observe, Akt-Relate | Ontologie | neue Verknüpfungen (M) |
| 5 Denken | Revise-Reflect | (τ, r, mem) | Self-Feedback (mem/M) |
| 6 Nicht-Kognition | **alle Phasen** (dämpft durch alle) | M + Kontext | Einflussfaktoren-Log (M) |
| 7 Handeln | Akt | M (Wissen+Modell) | Aktion + Traces (M) |
| 8 Wissen+ | **Compare, Revise** | M + Referenz | revidiertes Modell (M, knowledge/) |
```

## Fazit (urteil)

**Die Behauptung ist FALSCH in allen vier Aussagen.**

| Aussage | Behauptet | Datei (`wissenszyklus-8-stufen.md:112-119`) | Urteil |
|---|---|---|---|
| Stufe 1 = nur Observe | Observe | Observe, Akt-Obs | **Falsch** |
| Stufe 4 = nur Observe | Observe | Observe, Akt-Relate | **Falsch** |
| Stufe 6 = nur Revise | Revise | alle Phasen (Dämpfung) | **Falsch** |
| Stufe 8 = nur Konstrukt | Konstrukt | Compare, Revise | **Falsch** |

**Keine Korrektur der Tabelle vorgenommen** – die Datei ist bereits korrekt.
Die Behauptung widerspricht den Quelldateien. Der Widerspruch steht dokumentiert.
