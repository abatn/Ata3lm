# Non-Cognitive — Ablage für Stufe 6 (Prinzip 8)

> Lab-Prinzip: MD-first. Gesetz: `AGENTS.md` Prinzip 8.
> Doku: `knowledge/lifecycle/nicht-kognition.md`.
> Skill: `skills/non-cognitive/SKILL.md`.
> Connector: `connectors/affective-signals.md`.
> Markierung: `(Auftrag)` = gesetzte Ordnung, keine Quellen-Aussage.

## Status

- Status: angelegt, wartet auf t=1 (Auftrag).

## Konvention (Auftrag)

- Jeder Lauf von Stufe 6 legt hier sein Einflussfaktoren-Log ab.
- Dateiformat pro Lauf: `t-NNN-log.md` (Auftrag).
- Jeder Lauf zusätzlich mit Provenienz in `ergebnisse/rekursion/NNN-*.md`
  (Auftrag).

## Log-Format (Auftrag)

Pro Eintrag genau eine Zeile / ein Tupel:

```text
[Faktor, Kontext, Auswirkung/Dämpfung, Beleg]
```

## Pflichtfelder (Auftrag)

1. `Faktor`: Valenz / Proclivity (belegt) oder Stress / Zeitdruck /
   implizite Bias / unbewusste Vorgänge (nur protokolliert).
2. `Kontext`: was lag vor, ohne Deutung.
3. `Auswirkung/Dämpfung`: was wurde vorsichtiger getan, ohne
   Wirkungsbehauptung.
4. `Beleg`: Quellen-Link (belegt) oder `Auftrag-Protokoll` (nur
   protokolliert). Ohne Beleg kein Eintrag.

## Regeln (Auftrag)

- Stress, Zeitdruck, implizite Bias, unbewusste Vorgänge NUR als
  protokollierte Kontextfaktoren; keine Wirkungsbehauptung, kein
  psychologisches Gesetz.
- Sentiment-Analyse / Stress-Erkennung nur als geforderte externe Signaltypen
  (Auftrag, keine System-Behauptung); Übernahme nur bei verifiziertem
  externem Signal.
- Dämpfung = Vorsicht für Handeln (Stufe 7), steuert Handeln nie allein;
  kein Veto ohne Beleg.

## Quellen

Nur diese Quellen, keine weiteren behauptet:

- JISEM 2025 (Emotions-Modul + Valenz als intrinsisches Feedback, Schema
  `<context,action,emotion>`):
  https://jisem-journal.com/index.php/journal/article/view/12473
- CCA 2024 (autotelische + interactionale Selbstmotivation,
  Proclivity/Gewichte):
  https://researchr.org/publication/XueLM24-0
