# Connector: Gödel Agent (ACL 2025)

> Lab-Prinzip, MD-first. Dieser Connector bindet genau EINE externe Quelle
> ein – ohne Erfindungen. Alles hier Behauptete steht im Paper oder README.

## Identität

- Name: Gödel Agent – selbstreferenzieller Agent via Python Monkey Patching
- Paper (arXiv): https://arxiv.org/abs/2410.04444
- ACL 2025 Long Paper 1354: https://aclanthology.org/2025.acl-long.1354/
- PDF: https://aclanthology.org/2025.acl-long.1354.pdf
- Code: https://github.com/Arvid-pku/Godel_Agent
- Lizenz lt. Repo: MIT (siehe Repo-Root `LICENSE`)
- Theoretischer Ursprung (nur via Paper referenziert): Gödel Machine
  (Schmidhuber) – keine eigenen Behauptungen hier.

## Mechanismus (aus Paper §4 + README verifiziert)

1. **Self-Awareness via Runtime Memory Inspection:** Liest lokale/globale
   Variablen, Funktionen, Klassen aus Python Runtime-Memory.
2. **Self-Improvement via Dynamic Code Modification:** Generiert neuen Code,
   schreibt ihn per Monkey Patching ins Runtime-Memory
   (Klassen/Module dynamisch modifizieren – im Paper zitiert als Bimal 2012:
   https://web.archive.org/web/20120822051047/http://www.mindfiresolutions.com/Monkey-Patching-in-Python-1238.php).
3. **Recursive Improvement Mechanism:** Hauptfunktion ist rekursiv
   (kein Loop), damit modifizierte Optimierungslogik in der nächsten Tiefe
   wirksam wird.
4. **Environmental Interaction:** Feedback via Utility `U(E, π)` /
   Validierungsset; Task-Interfaces pro Task maßgeschneidert.
5. **Zusatz-Designs (§4.2):** Thinking Before Acting, Error Handling
   (Sequenz stoppen, Fehlerinfo mittragen), Additional Tools
   (Python/Bash ausführen, LLM-API rufen).

## Datei-Mapping (aus README „Project Structure" verifiziert)

| Repo-Pfad | Rolle im Rekursions-Loop |
|---|---|
| `src/main.py` | Einstiegspunkt (`python src/main.py`) |
| `src/agent_module.py` | Kern: Self-Awareness, Self-Modification, Action Execution; enthält `solver`, `evolve`, `execute_action`, `action_adjust_logic`, `action_run_code`, `action_evaluate_on_task` |
| `src/logic.py` | Ablage des generierten Agenten-Codes (= materialisiertes `M`) |
| `src/goal_prompt.md` | Goal Prompt (High-Level-Ziel, Werkzeug-Einführung) |
| `src/task_*.py` | Evaluation pro Task/Umgebung (adaptiert aus ADAS: https://github.com/ShengranHu/ADAS) |
| `src/wrap.py` | Debugging-Hilfe |
| `datasets/` | Experiment-Daten |
| `results/` | Selbst-optimierter Code + Test-Outputs pro Task |

Install (nur aus README abgeschrieben):

```bash
git clone https://github.com/Arvid-pku/Godel_Agent.git
cd Godel_Agent
pip install -r requirements.txt
# OpenAI API key in key.env konfigurieren, dann:
python src/main.py
```

## Mapping auf unsere 5 Phasen

| Unsere Phase | Gödel-Äquivalent |
|---|---|
| Konstrukt | Initial Policy + `goal_prompt.md` |
| Akt | `solver` + `execute_action` + `action_run_code` |
| Observe | `self_inspect` + `interact` (`U(E, π)`) |
| Compare | `action_evaluate_on_task` + Validierungsset |
| Revise | `self_update` / `action_adjust_logic` + `continue_improve` (Rekursion) |

## Nutzung im Knowledge-Agenten

- Der Skill `skills/recursive-improve/SKILL.md` ruft diesen Connector
  für `Observe` (lesen), `Revise` (patchen) und `Compare` (evaluieren).
- Neue Umgebungen nach README Development Tips einbinden:
  Reward-Funktion definieren → `action_evaluate_on_task` implementieren →
  initialen `solver` bereitstellen.
- Neue Aktionen: in `agent.action_functions` eintragen → Funktion
  implementieren → ggf. im Goal Prompt betonen.

## Grenzen (aus Paper ehrlich übernommen)

- Konvergenz hängt von LLM-Fähigkeiten ab; Zusatzmechanismen (§4.2)
  sind Stützen, kein Garant.
- Ohne externes Validierungsset droht Selbsttäuschung – daher Guardrail:
  `Compare` nur mit verifizierbarem Signal + menschlicher Freigabe.
- Dieser Connector modifiziert NIEMALS selbstständig Produktivcode;
  er liefert nur das dokumentierte Verfahren. Jede Anwendung wird in
  `ergebnisse/rekursion/` protokolliert.

## Quellen

- https://arxiv.org/abs/2410.04444
- https://aclanthology.org/2025.acl-long.1354/
- https://aclanthology.org/2025.acl-long.1354.pdf
- https://github.com/Arvid-pku/Godel_Agent
- https://github.com/ShengranHu/ADAS
