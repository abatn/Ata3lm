# Nicht-Kognition — Stufe 6 des 8-Stufen-Zyklus (Prinzip 8)

> Lab-Prinzip: MD-first. Gesetz: `AGENTS.md` Prinzip 8.
> Eltern-Dok: `knowledge/lifecycle/rekursion/wissenszyklus-8-stufen.md`.
> Markierungskonvention dieser Datei: Alles, was nur per Auftrag gesetzt ist
> (gesetzte Ordnung, keine Quellen-Aussage), ist mit `(Auftrag)` markiert.
> Alles Belegte steht unter „Belegtes" mit Quellen-Link. Keine weiteren
> Behauptungen, keine psychologischen Gesetze.

## Definition

Nicht-Kognition ist eine eigene Stufe mit Schreibrecht nach Working Memory
(Auftrag). Sie dämpft Handeln (Vorsicht), steuert es nie allein (Auftrag).

Das heißt (Auftrag):

- Stufe 6 wird nach Denken (Stufe 5) und vor Handeln (Stufe 7) geprüft.
- Ihr einziges Schreibrecht ist das Einflussfaktoren-Log nach Working Memory
  (Auftrag).
- Sie gibt eine Dämpfungsempfehlung (z. B. vorsichtigerer nächster Schritt),
  kein Veto und keine Handlungsentscheidung (Auftrag).

## Belegtes

Nur diese Mechanismen werden als belegt übernommen, aus den Quellen
abgeschrieben, ohne Zusatzbehauptung:

- JISEM 2025: Emotions-Modul + Valenz als intrinsisches Feedback, Schema
  `<context,action,emotion>` —
  https://jisem-journal.com/index.php/journal/article/view/12473
- CCA 2024: autotelische + interactionale Selbstmotivation,
  Proclivity/Gewichte —
  https://researchr.org/publication/XueLM24-0

Keine anderen Mechanismen werden hier als belegt behauptet.

## Einflussfaktoren-Log-Format (Auftrag)

Jeder Eintrag ist eine Zeile/Tupel mit genau diesen 4 Feldern (Auftrag):

```text
[Faktor, Kontext, Auswirkung/Dämpfung, Beleg]
```

- `Faktor`: z. B. Valenz, Proclivity (belegt) oder Stress, Zeitdruck,
  implizite Bias, unbewusste Vorgänge (nur protokolliert, siehe Regel).
- `Kontext`: was lag vor (Working-Memory-Stand, Task-Situation), ohne Deutung.
- `Auswirkung/Dämpfung`: was wurde vorsichtiger getan (z. B. kleinerer
  Schritt, zusätzliche Prüfung vor Handeln), ohne Wirkungsbehauptung.
- `Beleg`: Quellen-Link (für belegte Faktoren) oder `Auftrag-Protokoll`
  (für nur protokollierte Faktoren). Ohne Beleg kein Eintrag (Auftrag).

Pflichtfelder: alle 4 Felder müssen ausgefüllt sein (Auftrag).

## Regel für nicht-belegte Faktoren

Stress, Zeitdruck, implizite Bias und unbewusste Vorgänge werden NUR als
protokollierte Kontextfaktoren behandelt (Auftrag):

- Erlaubt: protokollieren als `[Faktor, Kontext, Auswirkung/Dämpfung, Beleg]`
  mit `Beleg = Auftrag-Protokoll`.
- Verboten: keine Wirkungsbehauptung („X verursacht Y"), kein
  psychologisches Gesetz zitieren oder behaupten, keine Deutung über deren
  Wirkung.

## Signaltypen: Sentiment-/Stress-Erkennung (Auftrag, keine System-Behauptung)

Sentiment-Analyse und Stress-Erkennung werden hier NICHT als existierende,
verifizierte Systeme behauptet. Sie sind geforderte externe Signaltypen
(Auftrag):

- Sie beschreiben, welche Art externen Signals Stufe 6 entgegennehmen darf,
  falls ein verifiziertes externes Signal vorliegt (Auftrag).
- Ohne verifizierbares externes Signal (Grader/Code-Run/DB bzw. belegte
  Quelle) gibt es keinen Compare und keine Behauptung über deren Funktion
  (Auftrag, vgl. Prinzip 6).
- Belegte intrinsische Signale bleiben ausschließlich: Valenz (JISEM) und
  Proclivity/Gewichte (CCA).

## Rekursionsschnittstelle (Auftrag)

- Stufe 6 schreibt das Einflussfaktoren-Log nach Working Memory (Auftrag).
- Dieses Log ist ein Signal für Handeln (Stufe 7): Handeln liest es und
  wendet die Dämpfungsempfehlung an oder dokumentiert begründet, warum nicht
  (Auftrag).
- Stufe 6 schreibt sonst nichts: kein Modell-Update, keine Ontologie-Änderung,
  keinen Produktivcode (Auftrag).

## Input / Output (Auftrag)

- Input: Working-Memory-Stand (inkl. Self-Feedback aus Stufe 5) + vorliegender
  Kontext (Task, externe Signale falls verifiziert).
- Output: Einflussfaktoren-Log im obigen Format nach Working Memory +
  Dämpfungsempfehlung für Stufe 7.

## Guardrails (aus AGENTS.md, als Auftrag übernommen)

1. Human-Gate: kein `self_update` ohne `approved`.
2. Externe Verifikation: kein Compare ohne verifizierbares Signal; ohne Beleg
   kein Log-Eintrag.
3. Provenienz: jede Anwendung dokumentiert in
   `ergebnisse/rekursion/NNN-*.md` mit Quelle bzw. `Auftrag-Protokoll`.
4. Interface-Stabilität: keine Format-/Schnittstellenänderung des Logs ohne
   Freigabe.
5. Stufen-Disziplin: keine Stufe überspringen — kein Handeln (Stufe 7) ohne
   Prüfung von Stufe 6; kein Revise ohne Compare-Beleg.

## Auftrag-markierte Aussagen dieser Datei

Als Auftrag (nicht quellenbelegt) sind markiert: eigene Stufe mit
Schreibrecht nach Working Memory; Dämpfung von Handeln ohne Alleinsteuerung;
Log-Format und Pflichtfelder; Nur-Protokoll-Regel für Stress/Zeitdruck/
implizite Bias/unbewusste Vorgänge; Sentiment-/Stress-Erkennung als geforderte
externe Signaltypen; Rekursionsschnittstelle; Input/Output; Guardrails.

## Quellen

Nur diese Quellen werden zitiert, keine weiteren behauptet:

- JISEM 2025 (Emotions-Modul + Valenz als intrinsisches Feedback, Schema
  `<context,action,emotion>`):
  https://jisem-journal.com/index.php/journal/article/view/12473
- CCA 2024 (autotelische + interactionale Selbstmotivation,
  Proclivity/Gewichte):
  https://researchr.org/publication/XueLM24-0
