---
name: expand-knowledge
description: Erweitert die Wissensbasis in Stufe 8 (WISSEN+): prueft Kandidaten-Erweiterungen gegen Compare-Beleg, erkennt veraltete Regeln via Veraltet-Test und Reversal-Logik, invalidiert statt zu loeschen, dokumentiert alles in knowledge/expansion/ — nur mit Quelle und Freigabe.
---

# Skill: expand-knowledge (Stufe 8: WISSEN+)

> Lab-Prinzip MD-first: keine Erfindungen. Aussagen mit dem Zusatz
> `(Status: Auftrag)` sind gesetzte Betriebsregeln, keine Quellen-Claims.
> Erlaubte Quellen stehen nur im Abschnitt `Quellen`.

## Ablauf (Status: Auftrag)

1. **Compare-Bericht + Memory laden**
   - Compare-Bericht mit Beleg laden.
   - Aktuellen Stand aus Working Memory / Ontologie laden.
   - Ohne Compare-Beleg: Abbruch (`rejected`).

2. **Kandidaten-Erweiterungen prüfen**
   - Jede Kandidaten-Erweiterung braucht eine Quelle aus `Quellen`.
   - Kandidat ohne Quelle: `rejected`.

3. **Veraltet-Test (Status: Auftrag)**
   - Gegen-Evidenz vorhanden?
   - Gültigkeitsfenster abgelaufen?
   - Bei Reversal-Hinweis (Gegen-Evidenz): Regel als Invalidierungs-Kandidat
     markieren (Reversal-Logik als Projekt-Anwendung von EvoPathBench,
     das hier nur Evaluations-Benchmark ist, kein Revisions-Algorithmus).

4. **Alte Regeln invalidieren (nicht löschen, mit Historie) (Status: Auftrag)**
   - Invalidierung statt Löschung (Bi-Temporal-Prinzip aus Graphiti).
   - Gültigkeitsfenster schließen, Historie behalten.
   - Episoden + Provenienz mitführen.
   - Point-in-Time-Abfragen müssen möglich bleiben.

5. **Neue Regeln mit Quelle schreiben (Status: Auftrag)**
   - Nur mit Compare-Beleg + menschlicher Freigabe.
   - Verdichtung nach HeLa-Referenz (Hebbian Distillation: Hubs zu stabilem
     semantischem Wissen verdichten) nur als dokumentierte Referenz;
     keine automatische Verdichtung ohne Freigabe.
   - Adaptive Forgetting nur als Quellen-Mechanismus für Skalierbarkeit
     referenziert; kein Vergessen ohne Freigabe.

6. **In `knowledge/expansion/` dokumentieren (Status: Auftrag)**
   - Format und Pflichtfelder nach `knowledge/expansion/README.md`.
   - Jede Erweiterung mit Quelle; jede Invalidierung mit Historie.

## Guardrails (Status: Auftrag, wie `knowledge/lifecycle/wissen-plus.md`)

1. Human-Gate: kein Zurückschreiben ohne `approved`.
2. Externe Verifikation: kein WISSEN+ ohne Compare-Beleg.
3. Provenienz: jede Erweiterung mit Quelle aus `Quellen`.
4. Invalidierung statt Löschung: alte Fakten/Regeln behalten Gültigkeitsfenster + Historie.
5. Interface-Stabilität: keine Format- / Schnittstellenänderung ohne Freigabe.
6. Stufen-Disziplin: keine Stufe überspringen.

## Input / Output (Status: Auftrag)

Input: Compare-Bericht mit Beleg, Memory-Stand, Kandidaten mit Quelle, Freigabe-Status.

Output: Revidiertes Modell + Dokumentation in `knowledge/expansion/` +
Rückschrieb nach Working Memory / Ontologie.

## Quellen

- https://aclanthology.org/2026.acl-long.625/
- https://github.com/ReinerBRO/HeLa-Mem
- https://github.com/getzep/graphiti
- https://arxiv.org/abs/2609.24663
