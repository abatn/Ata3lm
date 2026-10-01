# Connector: CCA-Framework (Constructivist Cognitive Architecture)

> Lab-Prinzip, MD-first. Alles Behauptete steht in den verlinkten Quellen.
> Hinweis zur Jahreszahl: Das CCA-Paper ist IEEE CogMI **2024** (Background:
> Dissertation 2020); die MAS-Konstruktivismus-Evaluation mit behavioralen
> Schemata ist JISEM **2025**. Beide werden hier getrennt belegt –
> kein „CCA-2025-Paper" erfunden.

## Identität

- Name: CCA – Constructivist Cognitive Architecture (hierarchischer Aufbau
  von Interaktions-Schemata).
- CCA-Paper: Xue, Lallement, Morelli (2024): Sense-making and knowledge
  construction via constructivist learning paradigm, 6th IEEE Int. Conf. on
  Cognitive Machine Intelligence (CogMI 2024), S. 137–143 –
  https://researchr.org/publication/XueLM24-0
- DOI: https://doi.org/10.1109/cogmi62246.2024.00027
- HAL-Volltext: https://cea.hal.science/cea-04761173/document
- IEEE-Eintrag: https://ieeexplore.ieee.org/document/7846786
- Dissertation (Background): J. Xue (2020): Architecture cognitive
  constructiviste – Modell für selbstmotivierte Agenten mit Sense-Making
  und Wissensaufbau (in der Recherche verifiziert, hier nur als Herkunft
  genannt, keine Detailbehauptung).
- MAS-Anwendung (Paper 2025): Mokhtari et al. (2025): Multi-Agent System
  Cooperation Via Constructivist Learning Approach, JISEM 10(57s) –
  https://jisem-journal.com/index.php/journal/article/view/12473
- PDF: https://jisem-journal.com/index.php/journal/article/download/12473/5791/20977

## Mechanismus CCA (aus Quelle abgeschrieben)

Komponenten (vgl. Paper Fig. 1):

1. **Stream of enacted interactions (Timeline)** – enacted Interactions als
   Folge farbcodierter Symbole über die Zeit.
2. **Container of sensorimotor interactions** – enthält **primitive
   interactions** (elementare sensomotorische Schemata) und **composite
   interactions** (hierarchisch-sequenzielle Schemata).
3. **Episodic Memory** – hierarchisch strukturierte enacted Interactions.
4. **Hierarchical Sequential Construction Module / Hierarchical Sequential
   System** – lernt hierarchische Interaktions-Regularitäten:
   rudimentäres Lernen (vorherige + aktuelle enacted Interaction) plus
   rekursives Bottom-up-Lernen kompositer Interaktionen aus
   untergeordneten Mustern.
5. **Anticipation Proposition Process** – schlägt nächste Interaktionen vor
   (Proclivity + Gewicht, Threshold `d` für Enactment kompositer
   Interaktionen als Ganzes).
6. **Behavior Selection Mechanism** – balanciert Propositionen aus
   Sequential System und Episodic Memory, wählt nächste zu enactende
   Sequenz (z. B. „moving forward with success" aus Episodic Memory).

Selbstmotivation (2 Formen, aus Paper):

- **Autotelisch:** Sequenzen erfolgreich enacten.
- **Interactional:** Interaktionen mit vorab positivem Wert bevorzugen.

Lernregel (aus Paper): enacted Interaction mit intended Interaction
abgleichen; bei kompositen Interaktionen flache enacted Folge gemäß
Enactment-Sequenz + intended Struktur hierarchisch aufbauen; neue
komposite Interactions konstruieren/verstärken (pre-interaction = Kontext,
post-interaction = Ergebnis) und in `C(t+1)` übernehmen.

**GAIT** – Toolkit zum Generieren/Analysieren von Interaction Traces zur
Laufzeit (Feinlernprozess + entstandene strukturierte Verhaltensweisen
pro Entscheidungsschritt sichtbar machen).

Evaluation (aus Paper, Small Loop Problem): CCA lernt erfolgreiches
Interagieren + Vermeiden ungünstiger Interaktionen; im Vergleich früheres
Konvergieren als Q-Learning-Baseline (Bumping-Stopp CCA ab Schritt 357
vs. Q-Learning ab Schritt 1246 – Zahlen nur aus Paper zitiert, nicht
selbst gemessen).

## Mechanismus JISEM 2025 (MAS-Anwendung, aus Quelle abgeschrieben)

- Schema `<context,action,emotion>` + numerische `valence`.
- Module: perception, learning, enaction, emotion (intrinsisches Feedback).
- Selektion: Kontext → Kandidaten → Valenz-Auswahl → Enaction → Update.
- Experiment: kollaborative Ressourcen-Extraktion in Grid-Simulation;
  emergente Navigations- + Kollaborations-Schemata
  (`wait` an Ressource, kollektives `extract`, Sequenz
  `[move toward resource, wait for help, extract]`).
- Limitation (aus Paper, ehrlich übernommen): Agenten interagieren sozial,
  aber ohne aktive Kommunikation/direkte Imitation; Simulation bleibt 2D.

## Mapping auf unsere Konstrukt-Phase

| Konstrukt-Bedarf | CCA / JISEM-Äquivalent |
|---|---|
| Verhaltene Schemata aufbauen | JISEM `<context,action,emotion>` + Valenz |
| Hierarchie aufbauen | CCA primitiv → komposit (bottom-up, rekursiv) |
| Aus Erfahrung + intrinsischer Motivation | CCA autotelisch/interactional; JISEM Emotions-Feedback |
| Working Memory lesen/schreiben | CCA Episodic Memory + Enactment-Timeline; bei uns `M(t) → M(t+1)` |
| Nachvollziehbarkeit | GAIT-Traces; bei uns `ergebnisse/rekursion/NNN-*.md` |

## Nutzung im Knowledge-Agenten

- Skill `skills/recursive-improve/konstrukt/SKILL.md` ruft diesen Connector
  für Schritt 2 (Konstruieren): JISEM-Selektion + CCA-Hierarchisierung.
- Materialisierung von `M` weiter via `connectors/goedel-agent.md`
  (Runtime-Memory / `logic.py`-Analogon).
- Neue Domänen: Perzeption als Kontextvektor definieren, Valenz-/Proclivity-
  Initialisierung offenlegen (Paper nennt manuelle Thresholds als offene
  Baustelle – hier dokumentieren, nicht verschweigen).

## Grenzen (aus Quellen übernommen)

- CCA-Thresholds/Valenz-Init teils manuell (Paper nennt das als
  weiter zu erforschende Lücke) – keine Autonomie-Behauptung darüber hinaus.
- JISEM-Simulation 2D, keine aktive Agenten-Kommunikation – Übertrag auf
  unseren Agenten nur mit externer Verifikation (`Compare`) + Freigabe.
- Dieser Connector schreibt NIEMALS selbstständig Produktivcode; er liefert
  nur das dokumentierte Verfahren. Jede Anwendung → `ergebnisse/rekursion/`.

## Quellen

- https://researchr.org/publication/XueLM24-0
- https://doi.org/10.1109/cogmi62246.2024.00027
- https://cea.hal.science/cea-04761173/document
- https://ieeexplore.ieee.org/document/7846786
- https://jisem-journal.com/index.php/journal/article/view/12473
- https://jisem-journal.com/index.php/journal/article/download/12473/5791/20977
