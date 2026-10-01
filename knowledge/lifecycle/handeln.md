# Handeln — Stufe 7 des 8-Stufen-Zyklus

> Lab-Prinzip: MD-first. Keine Erfindungen. Alles stammt aus dem Auftrag
> oder aus den unten genannten Quellen. Auftrag-Begriffe sind mit
> `[Auftrag]` markiert, Übertragungen auf diese Stufe mit `[Mapping/Auftrag]`.

## 1. Definition

**[Auftrag]** Handeln bedeutet: Wissen anwenden und auf neue Aufgaben transferieren.

**[Auftrag]** Handeln schreibt die Aktion in das Working Memory. Dieser
Eintrag ist das Signal für Wissen+ (Stufe 8).

Abgrenzung **[Auftrag]**:

- Beobachten (Stufe 1) hält fest, Handeln greift ein.
- Vergleichen (Stufe 6) bewertet, Handeln setzt um.
- Wissen+ (Stufe 8) übernimmt erst, was Handeln als Aktion + Ergebnis
  im Working Memory hinterlassen hat.

## 2. HTAC-Mapping

Quelle: HTAC (ICML 2026 Poster).

Belegte Mechanismen (nur diese werden übernommen, nichts hinzuerfunden):

- Duale Task-Kodierung auf Domain- und Task-Ebene.
- Dual-Level-Experten, bereitgestellt on demand.
- Adaptive Knowledge Composition historischen Wissens per Attention.
- Task-Adapter.

**[Mapping/Auftrag]** Übertragung auf Handeln:

- Duale Aufgabenkapselung (Domain-/Task-Ebene) strukturiert, worauf
  Wissen angewendet wird.
- Passende Expertise wird on demand komponiert statt starr angewendet.
- Historisches Wissen wird adaptiv per Attention komponiert.
- Task-Adapter dienen dem Transfer ohne Vergessen.

Zum Benchmark Offline Continual World werden hier keine Ergebnisse
behauptet (nur zitieren, falls erwähnt — hier nicht erwähnt).

## 3. Agent-Dice-Mapping

Quellen: Agent-Dice Paper (ACL 2026 Findings), Agent-Dice Code.

Belegte Mechanismen (nur diese werden übernommen, nichts hinzuerfunden):

- Parameter-Fusion via Directional Consensus.
- Zweistufig: Geometric-Consensus-Filtering + Curvature-based Importance Weighting.
- Evaluierte Domänen laut Paper: Tool-Use- und GUI-Agenten.

**[Mapping/Auftrag]** Übertragung auf Handeln:

- Geometric-Consensus-Filtering beschneidet widersprüchliche Updates.
- Krümmungs-Gewichtung (Curvature-based Importance Weighting) verstärkt
  geteilte Semantik.
- Dies adressiert das Stabilitäts-Plastizitäts-Dilemma für Transfer
  ohne katastrophales Vergessen.

Hinweis **[Mapping/Auftrag]**: Die Auftrags-Formulierung
„filtert widersprüchliche Updates" ist ein Mapping auf
Geometric-Consensus-Filtering, kein wörtliches Quellen-Zitat.

Zu Domänen-Ergebnissen werden hier keine Zahlen oder Details behauptet.

## 4. Transfer-Regel **[Auftrag]**

1. Nur belegtes Wissen anwenden.
2. Neue Aufgaben ausschließlich via Komposition belegter Experten lösen.
3. Jede Anwendung braucht Beleg-Trace + Quellen-Link.
4. Ohne diese Belege: kein Transfer, Status `rejected`.

## 5. Rekursionsschnittstelle **[Auftrag]**

Handeln schreibt nach Working Memory:

- Aktion (was wurde mit welchem Wissen auf welche Aufgabe angewendet).
- Ergebnis (Beobachtung des Ausgangs, keine Deutung).

Dieser Working-Memory-Eintrag ist das Eingangssignal für Stufe 8 (Wissen+).
Provenienz erfolgt in `ergebnisse/rekursion/NNN-*.md` gemäß `AGENTS.md`.

## 6. Input / Output **[Auftrag]**

Input:

- Belegtes Wissen (aus Stufe 2–6).
- Ziel `g` + Task-Input.
- Vorgabe, welche Expertise komponiert werden darf.

Output:

- Aktion + Ergebnis im Working Memory.
- Dokumentation in `knowledge/action/` mit Quelle.

## 7. Guardrails **[Auftrag]**

1. Kein Handeln ohne Stufen 1 und 6 (kein Handeln ohne Beobachten,
   kein Handeln ohne Compare-Beleg).
2. Keine unbelegten Anwendungen.
3. Widersprüchliche Updates filtern (Konsens-Prinzip, siehe Mapping oben).
4. Keine Format- oder Schnittstellenänderung ohne Freigabe.
5. Kein `self_update` ohne `approved` (Human-Gate).

## 8. Quellen

Nur diese Quellen sind für diese Datei zulässig; keine weiteren behauptet:

- HTAC (ICML 2026 Poster): https://icml.cc/virtual/2026/poster/63033
- Agent-Dice Paper (ACL 2026 Findings): https://aclanthology.org/2026.findings-acl.908/
- Agent-Dice Code: https://github.com/Wuzheng02/Agent-Dice
