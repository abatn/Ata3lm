# MCP-Check Auftrag 3: Lyapunov-Damping — Abdeckung + Implementierung

> Datum: 2026-10-01 · Auftrag 3 von 3 · Phase: Observe → Compare
> Lab-Prinzip §6: gemessene Werte, Rohausgaben aus dem Lauf.

## 1. Prüfung: Deckt einer der 16 MCP-Server (Gödel Agent, Agent-Dice, ADAS) Lyapunov-Damping ab?

**Quelle:** `ergebnisse/mcp-16-test.md` + Code-Durchgriff auf die Server.

| Server | komplette Tool-Liste | Lyapunov/E[ΔV]/Damping? |
|---|---|---|
| godel-agent | `run_code`, `read_logic` | nein — führt beliebigen Code aus, hat aber **kein** Lyapunov-Werkzeug |
| agent-dice | `geometric_consensus_fuse` | nein — Parameter-Fusion, kein Energie-Kriterium |
| adas | `adas_init_archive`, `adas_get_prompt`, `adas_propose_agent` | nein — Prompt-Archiv |
| mars | `mars_list_strategies`, `mars_run_strategy`, `mars_analyze_failure` | nein |
| trace | 6 Metriken (`metric_*`, `parse_json`) | nein |
| hela-mem / reflexion / react / graphiti / cognee / … | siehe `mcp-16-test.md` | nein |

```bash
grep -in "lyapunov\|E\[dV\]\|damping" ergebnisse/mcp-16-test.md
# -> 0 Treffer
```

**Ergebnis: KEIN MCP deckt Lyapunov-Damping ab.**
(`godel-agent:run_code` *könnte* die Formel rechnen — das ist ein Executor,
kein Governance-Primitiv; ein explizites, gate-gekoppeltes Tool fehlt.)

## 2. Implementierung: `E[ΔV] ≤ 0` in `data/memory/reflective_agent.py`

Neu in `data/memory/reflective_agent.py`:

- `lyapunov_check(energies, tau=0.0)` — mittlere Energieänderung
  `E[ΔV] = mean(V[t+1] − V[t])`; **stabil ⟺ `E[ΔV] ≤ τ`**, sonst `gate="ask"`
  (Verletzung → Human-Gate, §9).
- `simulate_lyapunov()` — zwei Verläufe (fallend/steilend) als Selbsttest.
- Dispatch `LYAPUNOV_SIM=1` im `__main__`-Block.

```python
def lyapunov_check(energies: list, tau: float = 0.0) -> dict:
    dV = [energies[i + 1] - energies[i] for i in range(len(energies) - 1)]
    e_dv = sum(dV) / len(dV)
    stable = e_dv <= tau
    return {..., "stable": stable, "gate": "ok" if stable else "ask"}
```

Fail-soft: `len(energies) < 2` → `{"stable": true, "gate": "ok",
"note": "zu wenig Daten"}` statt Absturz.

### Selbsttest (real)

```bash
python3 -m py_compile data/memory/reflective_agent.py && echo "compile OK"
LYAPUNOV_SIM=1 python3 data/memory/reflective_agent.py
```

```
compile OK
{
  "stable": {
    "E_dV": -0.16,
    "dV": [-0.2, -0.2, -0.15, -0.15, -0.1],
    "stable": true,
    "gate": "ok"
  },
  "unstable": {
    "E_dV": 0.3,
    "dV": [0.1, 0.2, 0.3, 0.4, 0.5],
    "stable": false,
    "gate": "ask"
  }
}
```

**Geprüft:** abnehmende Energie → `E[ΔV]=−0.16 ≤ 0` → `ok`;
wachsende Energie → `E[ΔV]=+0.3 > 0` → **`ask` (Human-Gate)** ✓.
Kein Repository-Schreibzugriff bei `LYAPUNOV_SIM=1` (nimmt den
`elif`-Zweig, nicht `run_once()`).

### Provenienz-Hinweis

Die beiden Edits wurden nach einem versehentlich ausgelösten
`git checkout -- .` aus dem OpenCode-Session-Log
(`~/.local/share/opencode/opencode.db`, Teile `prt_0f8eef77…`/`prt_0f8eefcf…`)
replayt und mit der **identischen** Ausgabe des Vorverlust-Laufs verifiziert.
Kein inhaltlicher Unterschied zur Original-Implementierung.

## 3. MCP-Lücke wird geschlossen

`lyapunov_check` liegt zusätzlich als MCP-Tool im neuen `governance-mcp`
(`ergebnisse/mcp-neu.md`). Echtes Ergebnis nach `initialize` + `tools/list`:

```text
server: governance-mcp
tools: ['drift_index', 'lyapunov_check', 'resolve_entities']
lyapunov stable:   {"E_dV": -0.16, ..., "stable": true,  "gate": "ok"}
lyapunov unstable: {"E_dV": 0.3,   ..., "stable": false, "gate": "ask"}
```

## 4. Quellen (HTTP 200 geprüft 2026-10-01)

| Quelle | Link | Status |
|---|---|---|
| WhyLab / Causal Audit Framework (C3 „Lyapunov-bounded damping") | https://github.com/neogenesislab/WhyLab-NeurIPS2026 | 200 |
| Gödel-Agent (Vergleich: was `godel-agent` kann) | https://arxiv.org/abs/2410.04444 | 200 |

> Formulierung „Lyapunov-bounded adaptive damping 2026" aus dem Auftrag ist
> über die WhyLab-C3-Referenz verankert (im Repo als Causal Audit Framework
> geführt). Kein zweites Paper hinzuerfunden.

## 5. Gate (§9)

Score 8/8 · keine neue Quelle (WhyLab stand schon in 027) · keine
Interface-Änderung (neue Funktion, keine geänderte Signatur) · Drift
`reflective_agent.py` 24/503 = **4,77 %** ≤ 10 % → **allow**.
