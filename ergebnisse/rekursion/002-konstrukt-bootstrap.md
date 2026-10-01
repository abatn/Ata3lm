# 002 – Konstrukt-Unterphase eingebaut (Docs, keine Code-Änderung)

- Datum: 2026-09-30
- Rekursionstiefe: `t=0 → t=0.K` (Strukturerweiterung, noch kein `self_update`)
- Phasen: Konstrukt (diese Unterphase einrichten) – liest `M(t)` (Eltern-Dok
  + Gödel-Connector), schreibt Schemata-Definition zurück für nächsten Zyklus
- Zustand vorher `(π, I, M)`:
  - `π`: unverändert (kein Solver angefasst)
  - `I`: unverändert (kein `SELF_IMPROVE` angefasst)
  - `M`: erweitert um `knowledge/lifecycle/rekursion/konstrukt.md`,
    `skills/recursive-improve/konstrukt/SKILL.md`,
    `connectors/cca-framework.md`; Eltern-Refaktor
    `rekursion.md → rekursion/index.md` (Pfadkonflikt Datei vs. Verzeichnis
    aufgelöst, Inhalt unverändert + §2.1/§7-Verweise)
- Observe (`self_inspect` + `interact`):
  - Repo-Inspektion: 7 Files Bestand bestätigt, Pfadkonflikt festgestellt.
  - Paper-Recherche: JISEM 2025 (Abstract + Volltext-PDF) und CCA
    (researchr + DOI + HAL-Volltext) gelesen.
- Compare (externes Signal):
  - Referenz: Erreichbarkeit + Inhaltsprüfung der Quellen (HTTP 200).
  - JISEM-Abstract enthält wörtlich: internes Wissen durch Erfahrung +
    intrinsische Motivation, behaviorale Schemata ohne externe Supervision.
  - CCA-Quelle enthält: primitive/composite interactions, hierarchical
    sequential system (rudimentär + rekursiv bottom-up), episodic memory,
    behavior selection, autotelisch/interactional, GAIT.
  - Kein Scoring erfunden; keine Code-Änderung zu verifizieren.
- Revise: keine Code-Revision (nur Docs). Restrukturierung ist reversibel
  (`git mv`-äquivalent, ein `mv`-Befehl).
- Quelle (Paper, Code – mit Link):
  - JISEM 2025: https://jisem-journal.com/index.php/journal/article/view/12473
  - PDF: https://jisem-journal.com/index.php/journal/article/download/12473/5791/20977
  - CCA: https://researchr.org/publication/XueLM24-0
  - DOI: https://doi.org/10.1109/cogmi62246.2024.00027
  - HAL: https://cea.hal.science/cea-04761173/document
  - IEEE: https://ieeexplore.ieee.org/document/7846786
- Freigabe: `approved: Batnini, 2026-09-30, Grund: Alle Connectoren sind in den 3 Kern-Dateien integriert; Cross-Referenz-Test bestanden.`
- **Korrigierte Verankerung (keine 1:1):** Aus `wissenszyklus-8-stufen.md:110-119`:
  Stufe 2 Wissen = Konstrukt; Stufe 3 Gedächtnis = Konstrukt (beide lesen/schreiben Konstrukt-Phase).
  Stufe 1 Erfahrung = Observe + Akt-Obs; Stufe 4 Kognition = Observe + Akt-Relate; Stufe 5 Denken = Revise-Reflect; Stufe 6 Nicht-Kognition = ALLE Phasen (Dämpfung); Stufe 7 Handeln = Akt; Stufe 8 Wissen+ = Compare + Revise.
- Self-Feedback für `t+1`:
  - Nach Freigabe: erste echte Konstrukt-Anwendung (Schemata aus Traces
    bauen) erst mit definiertem Validierungsset + `Compare`-Beleg starten.
  - Transparenz-Hinweis: CCA-Paper ist 2024 (nicht 2025); JISEM-Paper ist
    2025 – im Connector getrennt belegt, kein „CCA-2025-Paper" behauptet.
