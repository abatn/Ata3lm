# Konstrukt – Unterphase der Rekursions-Kommunikation

> Lab-Prinzip: Projekt + Skills + Connectors + Knowledge. MD-first.
> Eltern-Dok: `knowledge/lifecycle/rekursion/index.md` (§2.1).
> Das Konstrukt ist die kommunikative Schnittstelle, die den Zyklus
> schließt: Es liest den aktuellen Zustand (Working Memory) und schreibt
> neue Schemata zurück – Input für den nächsten Zyklus (Revise → Konstrukt → Akt).

## 1. Definition (aus Quelle, kein Eigenbau)

„Constructivist approaches consider agents as active entities capable of
constructing their internal knowledge through experience and intrinsic
motivation, without relying on predefined behaviors or external rewards."

- Quelle: Mokhtari et al. (2025), Abstract –
  https://jisem-journal.com/index.php/journal/article/view/12473

„We propose a model that integrates constructivist learning concepts like
schema and intrinsic motivation in cooperative multi-agent systems to enable
agents to progressively build, refine behavioral schemas and to learn
collaboration behaviors without external supervision."

- Quelle: ebd., Abstract.

Konstrukt = Aufbau internen Wissens durch Erfahrung + intrinsische
Motivation in Form behavioraler Schemata – ohne vordefinierte
Verhaltensweisen, ohne externe Belohnung.

## 2. Schema-Format (JISEM 2025, §4)

Schema = `<context, action, emotion>`:

- `context` – Kontextvektor aus Perzeption (in welcher Lage befindet sich der Agent)
- `action` – in diesem Kontext auszuführende Aktion
- `emotion` – neuer emotionaler Zustand nach Ausführung der Aktion
- `valence` (numerisch) – Zufriedenheitswert des Schemas in der Lernphase

Agenten-Architektur (4 Module, vgl. Paper Fig. 1):

- `perception` → `learning` → `enaction` → `emotion` → zurück in `learning`
  (intrinsisches Feedback aus dem Emotions-Modul aktualisiert die Schemata)

Schema-Selektion (Algorithmus 1, aus Paper abgeschrieben):

1. Kontextvektor aus Perzeptionen konstruieren.
2. Kontextbasierte Selektion → Kandidaten-Schemata.
3. Valenzbasierte Selektion → zu enactendes Schema wählen.
4. Gewähltes Schema ans Enaction-Modul senden, Aktionsteil ausführen.
5. Schemata per intrinsischem Feedback aus dem Emotions-Modul updaten.

Belegte emergente Schemata (Grid-Experiment, Ressourcen-Extraktion):

- Navigation: Hindernissen/Wänden ausweichen (Pain-Kurve konvergiert).
- Kollaboration: `[<no_obstacle,resource_close,no_agent>, wait, exciting]`
  (an Ressource auf Hilfe warten) + `[<no_obstacle,resource_close,agent>,
  extract, very_exciting]` (kollektives Extrahieren).
- Sequenz: `[move toward resource, wait for help, extract]` –
  Interpretation im Paper: emergentes Planungsverhalten.

Quelle Volltext/PDF: https://jisem-journal.com/index.php/journal/article/download/12473/5791/20977

## 3. Hierarchischer Aufbau (CCA-Framework, Connector)

Der hierarchische Aufbau von Interaktions-Schemata folgt dem
Constructivist Cognitive Architecture (CCA):

- **Primitive Interaction** – elementares sensomotorisches Schema.
- **Composite Interaction** – hierarchisch-sequenzielles Schema aus
  untergeordneten (primitiven oder rudimentären) Interaktionen.
- **Hierarchical Sequential System** – lernt Interaktions-Regularitäten:
  rudimentäres Lernen (vorherige + aktuelle enacted Interaction) plus
  rekursives Bottom-up-Lernen kompositer Interaktionen.
- **Episodic Memory** – hierarchisch strukturierte enacted Interactions.
- **Behavior Selection** – balanciert Propositionen aus Sequential System
  und Episodic Memory, wählt nächste zu enactende Sequenz.
- **Selbstmotivation (2 Formen):** autotelisch (Sequenzen erfolgreich
  enacten) + interactional (Interaktionen mit positivem Vorab-Wert bevorzugen).
- **GAIT** – Toolkit zum Generieren/Analysieren von Interaction Traces
  zur Laufzeit (welches strukturierte Verhalten wurde wann gelernt).

Quellen:

- Xue, Lallement, Morelli (2024), IEEE CogMI 2024, S. 137–143:
  https://researchr.org/publication/XueLM24-0
- DOI: https://doi.org/10.1109/cogmi62246.2024.00027
- Volltext (HAL): https://cea.hal.science/cea-04761173/document
- IEEE-Eintrag: https://ieeexplore.ieee.org/document/7846786
- Details: `connectors/cca-framework.md`

## 4. Rekursionsschnittstelle (lesen → schreiben → nächster Zyklus)

```text
Working Memory M(t) ──lesen──▶ KONSTRUKT ──schreiben──▶ M(t+1)
                                  │                        │
                     Revise → (freigegebenes π,I)      (Akt liest M(t+1)
                      als Startmodell)                 und führt solver aus)
```

- **Lesen:** Konstrukt liest `M(t)` – aktuelles `(π, I)`, Ontologie,
  Episodic Memory, Compare-Bericht aus `ergebnisse/rekursion/`.
- **Schreiben:** Neue Schemata (primitiv/komposit, inkl. Valenz bzw.
  Proclivity/Gewicht) werden nach `M` zurückgeschrieben:
  im Gödel Agent materialisiert als Runtime-Memory + `logic.py`
  (vgl. `connectors/goedel-agent.md`).
- **Nächster Zyklus:** `Akt` konsumiert `M(t+1)` (`solver` ausführen),
  `Observe` liest die Traces, `Compare` verifiziert extern, `Revise`
  erzeugt `(πₜ₊₁, Iₜ₊₁)` – das nach Freigabe wieder in Konstrukt einfließt
  (`continue_improve`-Rekursion).
- **Self-Feedback:** Enaction-Ergebnis + Emotions-Feedback (JISEM) bzw.
  enacted-vs-intended-Abgleich (CCA) sind das rekursive Signal für `t+1`.

## 5. Input / Output

Input:

- `M(t)`: `(π, I)`, Ontologie, Working/Episodic Memory, Compare-Bericht,
  Ziel `g`.

Output:

- `M(t+1)`: neue/geänderte Schemata (mit Beleg: welches Feedback hat sie
  erzeugt), bereit für `Akt`. Jede Änderung → File in
  `ergebnisse/rekursion/NNN-*.md` (Pflichtfelder siehe dort `README.md`).

## 6. Guardrails (aus Eltern-Phase übernommen, hier konkretisiert)

1. Konstrukt schreibt nur Schemata, deren Feedback-Beleg in `M` liegt
   (keine erfundenen Schemata – MD-first).
2. Interface-Änderungen (z. B. Schema-Format verlassen) nur mit
   menschlicher Freigabe.
3. `Compare`-Pflicht bleibt: Auch intrinsische Valenz ersetzt NICHT das
   externe Verifikationssignal (Validierungsset/Test) – sonst
   „konfidente Fehlanpassung".
4. Jedes neue Schema → Provenienz (welcher Trace, welche Quelle mit Link).

## 7. Quellen (keine Erfindungen)

- Mokhtari et al. (2025): Multi-Agent System Cooperation Via Constructivist
  Learning Approach, J. Inf. Syst. Eng. Manag. 10(57s) –
  https://jisem-journal.com/index.php/journal/article/view/12473
- PDF: https://jisem-journal.com/index.php/journal/article/download/12473/5791/20977
- Xue, Lallement, Morelli (2024): Sense-making and knowledge construction
  via constructivist learning paradigm, IEEE CogMI 2024 –
  https://researchr.org/publication/XueLM24-0
- DOI: https://doi.org/10.1109/cogmi62246.2024.00027
- HAL-Volltext: https://cea.hal.science/cea-04761173/document
- Eltern-Dok: `knowledge/lifecycle/rekursion/index.md`
- Skill: `skills/recursive-improve/konstrukt/SKILL.md`
- Connector: `connectors/cca-framework.md`
