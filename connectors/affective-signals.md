# Connector: Affective Signals (Nicht-Kognition, Stufe 6)

> Lab-Prinzip: MD-first. Gesetz: `AGENTS.md` Prinzip 8.
> Markierung: `(Auftrag)` = gesetzte Ordnung, keine Quellen-Aussage.
> Keine Erfindungen, keine psychologischen Gesetze.

## Identität (Auftrag)

- Name: Affective Signals — Signal-Connector für Stufe 6 Nicht-Kognition.
- Rolle (Auftrag): liefert belegte intrinsische Signale (Valenz,
  Proclivity) und nimmt geforderte externe Signaltypen (Sentiment,
  Stress) nur bei verifiziertem externem Signal entgegen.
- Dieser Connector entscheidet nichts selbst; er schreibt nur das
  Einflussfaktoren-Log nach Working Memory als Signal für Handeln
  (Auftrag).

## Belegte Mechanismen (aus Quellen abgeschrieben, ohne Zusatz)

- JISEM 2025: Emotions-Modul + Valenz als intrinsisches Feedback, Schema
  `<context,action,emotion>` —
  https://jisem-journal.com/index.php/journal/article/view/12473
- CCA 2024: autotelische + interactionale Selbstmotivation,
  Proclivity/Gewichte —
  https://researchr.org/publication/XueLM24-0

Keine weiteren Mechanismen werden als belegt behauptet.

## Signaltypen

### Belegt (mit Quellen-Link)

- Valenz (JISEM 2025): intrinsisches Feedback aus dem Emotions-Modul.
- Proclivity/Gewichte (CCA 2024): aus autotelischer + interactionaler
  Selbstmotivation.

### Gefordert, nicht als System behauptet (Auftrag)

- Sentiment-Analyse und Stress-Erkennung sind geforderte externe Signaltypen
  (Auftrag). Sie werden NICHT als existierende, verifizierte Systeme
  behauptet.
- Übernahme nur bei verifizierbarem externem Signal
  (Grader/Code-Run/DB bzw. belegte Quelle); sonst kein Eintrag, kein Compare
  (Auftrag).

### Nur protokolliert, nie als Wirkung behauptet (Auftrag)

- Stress, Zeitdruck, implizite Bias, unbewusste Vorgänge: NUR als
  protokollierte Kontextfaktoren im Format
  `[Faktor, Kontext, Auswirkung/Dämpfung, Beleg]` mit
  `Beleg = Auftrag-Protokoll` (Auftrag).
- Keine Wirkungsbehauptung, kein psychologisches Gesetz (Auftrag).

## Grenzen (Auftrag + Quellen-Schranke)

- Keine Behauptung über Wirkung von Stress/Zeitdruck/Bias/unbewussten
  Vorgängen (Auftrag).
- Keine Behauptung, dass Sentiment-/Stress-Erkennung als Systeme existieren
  oder funktionieren (Auftrag).
- Keine neuen Schemata, Aktionen oder Interfaces ohne Beleg-Trace +
  Quellen-Link + menschliche Freigabe (Auftrag, vgl. Prinzip 4).
- Dieser Connector schreibt niemals selbstständig Produktivcode; jede
  Anwendung → `ergebnisse/rekursion/NNN-*.md` (Auftrag).

## Quellen

Nur diese Quellen werden zitiert, keine weiteren behauptet:

- JISEM 2025 (Emotions-Modul + Valenz als intrinsisches Feedback, Schema
  `<context,action,emotion>`):
  https://jisem-journal.com/index.php/journal/article/view/12473
- CCA 2024 (autotelische + interactionale Selbstmotivation,
  Proclivity/Gewichte):
  https://researchr.org/publication/XueLM24-0


## Prozess (Aufruf) [Auftrag]

Dieser Connector bedient: `trust.py` — Nicht-Kognition/Guards.

MCP-Interface / Ontologie-Validierung (SHACL, W3C): https://www.w3.org/TR/shacl/ · `ergebnisse/connector-prozess.md`.
