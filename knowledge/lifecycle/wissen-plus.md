# WISSEN+ — Stufe 8 des 8-Stufen-Zyklus

> Lab-Prinzip MD-first: keine Erfindungen. Alles in dieser Datei stammt aus
> dem Auftrag oder aus den Quellen im Abschnitt `Quellen`. Begriffe mit dem
> Zusatz `(Status: Auftrag)` sind gesetzte Betriebsregeln, keine
> Quellen-belegten wissenschaftlichen Claims.

## 1. Definition (Status: Auftrag)

WISSEN+ erweitert die Wissensbasis und erkennt veraltete Regeln.

- Die Stufe schreibt das revidierte Modell zurück.
- Das Zurückschreiben schließt den Kreis zu neuen Konstruktionen:
  Das revidierte Modell ist Ausgangspunkt des nächsten Durchlaufs.
- Es wird nichts stillschweigend gelöscht oder überschrieben;
  jede Änderung braucht Beleg und Freigabe (siehe `Revisions-Regel`).

## 2. HeLa-Mapping (aus Quellen abgeschrieben)

Quelle: HeLa-Mem.

- **Hebbian Distillation:** Hubs zu stabilem semantischem Wissen verdichten.
- **Adaptive Forgetting:** dient der Skalierbarkeit.
- **Reflective Agent:** Mechanismus-Name aus der Quelle, ohne eigene
  Zusatzbehauptung über seine interne Wirkweise.
- Mapping auf WISSEN+ (Status: Auftrag): Verdichtung und Vergessen sind
  nur als dokumentierte Quellen-Mechanismen referenziert; ob und was im
  Projekt verdichtet oder vergessen wird, entscheidet allein die
  `Revisions-Regel` (Compare-Beleg + Freigabe).

## 3. Bi-Temporal-Mapping (aus Quellen abgeschrieben)

Quelle: Graphiti bi-temporal.

- Fakten werden mit Validitätsfenstern geführt.
- Alte Fakten werden invalidiert statt gelöscht.
- Episoden + Provenienz werden mitgeführt.
- Point-in-Time-Abfragen werden ermöglicht.
- Mapping auf WISSEN+ (Status: Auftrag): Jede Invalidierung behält die
  Historie; Löschung ist verboten.

## 4. EvoPathBench-Mapping (Evaluations-Benchmark, kein Revisions-Algorithmus)

Quelle: EvoPathBench (arXiv 21. Sep 2026).

- EvoPathBench ist ein Evaluations-Benchmark für selbst-evolvierende
  Agenten (Status: Auftrag: diese Einordnung ist gesetzt; EvoPathBench wird
  hier NICHT als Revisions-Algorithmus verwendet).
- Prozess-Eval-Dimensionen aus der Quelle:
  Generalisierung auf Ungesehenes, Retention nach unbezogenem Lernen,
  Regel-Adaption bei Gegen-Evidenz.
- Streams aus der Quelle: Accumulation- / Interference- / Reversal-Streams.
- Reversal-Logik (Status: Auftrag der Projekt-Anwendung): Veraltete Regeln
  werden via Reversal-Logik erkannt, d. h. bei Gegen-Evidenz wird die
  betroffene Regel als Kandidat für Invalidierung markiert und nur mit
  Compare-Beleg + Freigabe invalidiert.
- Befunde (nur falls in der Quelle erwähnt, ohne eigene Zahlen/Details):
  keine Methode mit verlässlicher Regel-Adaption;
  Kandidaten-Selektion als Kernproblem.

## 5. Revisions-Regel (Status: Auftrag)

1. Keine Erweiterung und keine Invalidierung ohne Compare-Beleg.
2. Keine Erweiterung und keine Invalidierung ohne menschliche Freigabe.
3. Jede Erweiterung trägt ihre Quelle (eine der Quellen aus `Quellen`).
4. Verstoß: `rejected`.

## 6. Rekursionsschnittstelle (Status: Auftrag)

- Das revidierte Modell wird nach Working Memory / Ontologie geschrieben.
- Working Memory / Ontologie ist der Input neuer Konstruktionen.
- Damit schließt Stufe 8 den 8-Stufen-Zyklus und öffnet den nächsten Durchlauf.

## 7. Input / Output (Status: Auftrag)

Input:

- Compare-Bericht mit Beleg.
- Aktueller Stand aus Memory (Working Memory / Ontologie).
- Kandidaten-Erweiterungen mit Quellenangabe.
- Freigabe-Status.

Output:

- Revidiertes Modell (erweiterte Wissensbasis, invalidierte Regeln mit Historie).
- Dokumentation in `knowledge/expansion/`.
- Rückschrieb nach Working Memory / Ontologie als Input neuer Konstruktionen.

## 8. Guardrails (Status: Auftrag)

1. Human-Gate: kein Zurückschreiben ohne `approved`.
2. Externe Verifikation: kein WISSEN+ ohne Compare-Beleg.
3. Provenienz: jede Erweiterung mit Quelle aus `Quellen`.
4. Invalidierung statt Löschung: alte Fakten/Regeln behalten Gültigkeitsfenster + Historie.
5. Interface-Stabilität: keine Format- / Schnittstellenänderung ohne Freigabe.
6. Stufen-Disziplin: keine Stufe überspringen (kein WISSEN+ ohne Beobachten und Compare-Beleg).

## 9. Quellen

- https://aclanthology.org/2026.acl-long.625/
- https://github.com/ReinerBRO/HeLa-Mem
- https://github.com/getzep/graphiti
- https://arxiv.org/abs/2609.24663

## 10. Fast Write Routing (Status: Quelle)

Diese Stufe ist mit Fast Write Routing aus AGENTS.md §10 und dem
Connector `connectors/fast-write-routing.md` verknüpft.

- **Quelle:** arXiv:2608.22215 – Dual-Layer Agentic Memory with Fast Write Routing and Slow Consolidation
- **Einbindung in WISSEN+:** Das Write-Back (langsame Konsolidierung) interagiert
  mit Stufe 8 (Wissen+): Extern gespeicherte Facts (aus Stufe 3 Gedächtnis)
  werden durch periodisches SFT in das parametrische Gedächtnis (Θ′) internalisiert.
- **Validierung:** Nach Konsolidierung wird geprüft, ob das Model Fakten ohne
  externe Unterstützung beantworten kann (Flush aus externem Speicher).
- **Guardrail:** Bei parametrischer Interferenz (1.752 Fakten verlieren Stabilität)
  bleibt der Fact im externen Puffer. Siehe `connectors/fast-write-routing.md`.
