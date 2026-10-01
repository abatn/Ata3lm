# Rekursion-Plan (Lab-Prinzip: Projekt + Skills + Connectors + Knowledge)

> Ausgabe-Datei per Aufgabe. MD-first, keine Erfindungen.
> Jede Quelle mit Link (Paper, GitHub).

## 1. Struktur (angelegt)

```text
knowledge-agent/
├── knowledge/lifecycle/rekursion.md      # Projekt: Rekursion als Kommunikationsstruktur (5 Phasen)
├── skills/recursive-improve/SKILL.md     # Skill: geschlossener Wahrnehmungs-Handlungs-Lern-Loop
├── connectors/goedel-agent.md            # Connector: Gödel Agent (ACL 2025) via Monkey Patching
└── ergebnisse/
    ├── rekursion-plan.md                 # diese Datei (Ausgabe)
    └── rekursion/
        ├── README.md                     # Wissens-Index + Konvention
        ├── 000-template.md               # Template je Iteration
        └── 001-bootstrap-rekursion-phase.md  # t=0, Quellen-Verifikation
```

## 2. Skill

- Pfad: `skills/recursive-improve/SKILL.md`
- Loop:
  - **Kreis A (Selbstbeobachtung):** Observe → Compare → Revise
  - **Kreis B (schließt den Kreis):** Revise → Konstrukt → Akt → Observe
- Geteilte Sprache: Ontologie + Working Memory (`M`); im Connector:
  Runtime-Memory + `logic.py`.
- Self-Feedback: `r` + Error-Traces als rekursives Signal für `t+1`;
  Abbruch ohne belegte Verbesserung.
- Details + Pseudocode (aus Paper Algorithmus 1): siehe Skill-File.

## 3. Connector

- **Gödel Agent (ACL 2025), selbstreferenziell via Python Monkey Patching.**
- Paper: https://arxiv.org/abs/2410.04444
- ACL: https://aclanthology.org/2025.acl-long.1354/
- PDF: https://aclanthology.org/2025.acl-long.1354.pdf
- Code: https://github.com/Arvid-pku/Godel_Agent
- Mechanismus (verifiziert): `SELF_INSPECT` lesen → `U(E, π)` Feedback →
  `self_update` per Monkey Patching schreiben → `continue_improve`
  rekursiv; Hauptfunktion rekursiv statt Loop; Thinking Before Acting +
  Error Handling + Python/Bash/LLM-Tools (§4.2).
- Datei-Mapping: `src/main.py` (Einstieg), `src/agent_module.py` (Kern mit
  `solver`/`evolve`/`action_*`), `src/logic.py` (generierter Code),
  `src/goal_prompt.md` (Ziel), `src/task_*.py` (Eval, adaptiert aus
  https://github.com/ShengranHu/ADAS), `src/wrap.py` (Debug).
- Volldoku: `connectors/goedel-agent.md`.

## 4. Kommunikationsstruktur

```text
Konstrukt → Akt → Observe → Compare → Revise → (Konstrukt → Akt …)
```

- Rekursives Lesen, Modifizieren, Zurückschreiben desselben Zustands
  `S = (π, I, M)`.
- 5 Unterphasen dokumentiert in `knowledge/lifecycle/rekursion.md`
  (§2.1–2.5) mit Gödel-Mapping je Phase.
- Kanonische Aktionen: `self_inspect`, `interact`,
  `action_evaluate_on_task`, `self_update`/`action_adjust_logic`,
  `continue_improve`, `action_run_code`, `thinking_before_acting`.

## 5. Guardrails (verbindlich)

1. **Menschliche Freigabe:** Kein `self_update` ohne Human-Gate; jede
   Revision → Diff + `ergebnisse/rekursion/NNN-*.md`, Status `pending`
   bis `approved`.
2. **Externe Verifikation:** `Compare` nur mit verifizierbarem Signal
   (Validierungsset, Tests, Ground Truth via `action_evaluate_on_task`);
   rein internes Scoring verboten → verhindert „konfidente Fehlanpassung".
3. **Schnittstellen-Stabilität:** keine Interface-Änderungen ohne Freigabe.
4. **Fehler-Rückfall:** Sequenz stoppen, Fehlerinfo mittragen,
   Original wiederherstellbar.
5. **Provenienz:** jede Iteration mit Quelle (Paper-/Code-Link).

## 6. Wissen (Provenienz)

- `ergebnisse/rekursion/README.md` – Index + Pflichtfelder.
- `000-template.md` – Template.
- `001-bootstrap-rekursion-phase.md` – `t=0`: 3/3 Quellen per HTTP verifiziert,
  keine Code-Änderung, `approved: bootstrap`.
- Nächster Schritt (`t=1`, erst nach Freigabe + Validierungsset):
  `solver`-Stub + `task_*.py`-Eval nach README Development Tips.

## 7. Quellen (vollständig)

- https://arxiv.org/abs/2410.04444
- https://aclanthology.org/2025.acl-long.1354/
- https://aclanthology.org/2025.acl-long.1354.pdf
- https://github.com/Arvid-pku/Godel_Agent
- https://github.com/ShengranHu/ADAS
- https://web.archive.org/web/20120822051047/http://www.mindfiresolutions.com/Monkey-Patching-in-Python-1238.php
