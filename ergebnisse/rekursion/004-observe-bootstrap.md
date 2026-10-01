# 004 – Observe-Unterphase eingebaut (Docs, keine Code-Änderung)

- Datum: 2026-09-30
- Rekursionstiefe: `t=0.O` (Strukturerweiterung, noch kein `self_update`)
- Phasen: Observe (Experten-Traces → hierarchische Skills, Skill vs. Concept
  Chaining; keine Policy-Änderung)
- Zustand `(π, I, M)`: unverändert; `M` erweitert um
  `knowledge/lifecycle/rekursion/observe.md`,
  `skills/recursive-improve/observe/SKILL.md`,
  `connectors/observer-agent.md`
- Observe: AAAI-2005-Seite (Abstract: Traces → Higher-Level-Skills) +
  Exa-Überblick + verwandte Papers (ILP05, ICML06, LHSO) gelesen.
- Compare: Quellen per HTTP verifiziert (AAAI-Seite, Exa-Seite 200 OK).
  „Observer Agent" als Auftrags-Mapping gekennzeichnet (Paper spricht vom
  lernenden System, nicht von diesem Namen).
- Revise: keine Code-Revision (nur Docs).
- Quelle:
  - https://aaai.org/papers/0021-fs05-07-021-learning-teleoreactive-logic-programs-by-observation/
  - https://exa.ai/library/publication/34qxkfcww51
  - http://www.isle.org/~langley/papers/icarus.trlp.ilp05.pdf
  - http://www.isle.org/~langley/papers/icarus.lbo.icml06.pdf
  - http://www.isle.org/~dgs/papers/lhso.DS02.pdf
- Freigabe: `approved: Batnini, 2026-09-30, Grund: Alle Connectoren sind in den 3 Kern-Dateien integriert; Cross-Referenz-Test bestanden.`
- **Korrigierte Verankerung (keine 1:1):** Aus `wissenszyklus-8-stufen.md:110-119`:
  Stufe 1 Erfahrung = Observe + Akt-Obs; Stufe 4 Kognition = Observe + Akt-Relate; Stufe 2 Wissen = Konstrukt; Stufe 3 Gedächtnis = Konstrukt; Stufe 5 Denken = Revise-Reflect; Stufe 6 Nicht-Kognition = ALLE Phasen (Dämpfung); Stufe 7 Handeln = Akt; Stufe 8 Wissen+ = Compare + Revise.
- Self-Feedback für `t+1`: erste echte Observe-Anwendung (Trace-Erklärung)
  erst nach Freigabe + primitiven Skill-Definitionen starten.
