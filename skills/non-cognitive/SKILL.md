---
name: non-cognitive
description: Stufe-6-Skill für Nicht-Kognition (Prinzip 8): Kontextfaktoren erheben, Einflussfaktoren-Log schreiben, Dämpfungsempfehlung für Handeln geben.
---

# Skill: Non-Cognitive (Stufe 6, Prinzip 8)

> Lab-Prinzip: MD-first. Gesetz: `AGENTS.md` Prinzip 8.
> Projektdoku: `knowledge/lifecycle/nicht-kognition.md`.
> Markierung: `(Auftrag)` = gesetzte Ordnung, keine Quellen-Aussage.
> Keine Erfindungen, keine psychologischen Gesetze.

## Ablauf

### Schritt 1 — Kontextfaktoren erheben (ohne Deutung)

- Belegte Faktoren prüfen (mit Quellen-Link):
  - Valenz als intrinsisches Feedback (JISEM 2025).
  - Proclivity/Gewichte aus autotelischer + interactionaler
    Selbstmotivation (CCA 2024).
- Nur protokollierte Faktoren festhalten (mit `Beleg = Auftrag-Protokoll`,
  keine Wirkungsbehauptung) (Auftrag):
  - Stress, Zeitdruck, implizite Bias, unbewusste Vorgänge.
- Sentiment-Analyse / Stress-Erkennung nur als geforderte externe Signaltypen
  behandeln (Auftrag, keine System-Behauptung): nur übernehmen, wenn ein
  verifiziertes externes Signal vorliegt, sonst nicht behaupten.

### Schritt 2 — Einflussfaktoren-Log schreiben (Auftrag)

Format pro Eintrag (Auftrag):

```text
[Faktor, Kontext, Auswirkung/Dämpfung, Beleg]
```

- Alle 4 Felder sind Pflicht (Auftrag).
- `Beleg` ist entweder ein Quellen-Link (belegte Faktoren) oder
  `Auftrag-Protokoll` (nur protokollierte Faktoren).
- Ohne Beleg kein Eintrag (Auftrag).
- Schreibziel: Working Memory (Auftrag). Sonst nichts schreiben.

### Schritt 3 — Dämpfungsempfehlung für Handeln (Stufe 7) (Auftrag)

- Empfehlung = Vorsicht (z. B. kleinerer Schritt, zusätzliche Prüfung),
  kein Veto ohne Beleg (Auftrag).
- Handeln (Stufe 7) steuert Stufe 6 nie allein; Stufe 6 dämpft nur (Auftrag).
- Begründung jeder Empfehlung verweist auf Log-Eintrag + Beleg.

### Schritt 4 — In `knowledge/non-cognitive/` dokumentieren (Auftrag)

- Ablage der Log-Konvention und jedes Laufs unter
  `knowledge/non-cognitive/` (Auftrag).
- Jede Iteration zusätzlich mit Provenienz in
  `ergebnisse/rekursion/NNN-*.md` (Auftrag).
- Status-Updates (z. B. `angelegt`, `t=1`) in
  `knowledge/non-cognitive/README.md` festhalten.

## Guardrails (Auftrag, aus AGENTS.md)

1. Human-Gate: kein `self_update` ohne `approved`.
2. Externe Verifikation: kein Compare ohne verifizierbares Signal.
3. Provenienz: jede Iteration → `ergebnisse/rekursion/NNN-*.md`.
4. Interface-Stabilität: Log-Format nicht ohne Freigabe ändern.
5. Stufen-Disziplin: kein Handeln ohne Stufe-6-Prüfung; kein Revise ohne
   Compare-Beleg.
6. Nur-Protokoll-Regel: Stress/Zeitdruck/implizite Bias/unbewusste Vorgänge
   nur protokollieren, keine Wirkung behaupten, kein psychologisches Gesetz.

## Quellen

Nur diese Quellen, keine weiteren behauptet:

- JISEM 2025 (Emotions-Modul + Valenz als intrinsisches Feedback, Schema
  `<context,action,emotion>`):
  https://jisem-journal.com/index.php/journal/article/view/12473
- CCA 2024 (autotelische + interactionale Selbstmotivation,
  Proclivity/Gewichte):
  https://researchr.org/publication/XueLM24-0
