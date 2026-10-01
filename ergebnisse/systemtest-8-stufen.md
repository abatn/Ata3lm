# Systemtest 8 Stufen – realer End-to-End-Lauf

> **Datum:** 2026-10-01 · **Score: 22/22 = 100.0 %** · **Auto-Gate (§9): allow** · **Fehlschläge: 0**

Der Lauf benutzt **die realen Dateien des Repos** (kein Mock): `ingestion_hook.py`, `bias_monitor.py`, `trust.py`, `approval.py`, `shared/shared_memory.py`, `reflective_agent.py`, `bi_temporal.py` plus `governance-mcp` (stdio) und `fast_write_router.py` (echte NVIDIA-API).

- Skript: `/tmp/opencode/ka_systemtest.py` (Aufruf: venv-Python, s. Reproduktion unten)
- Ausgabe-Log: `/tmp/opencode/systemtest-8stufen.log`
- Repo-Schreibzugriffe: **keine** (`git status` vor und nach dem Lauf leer)

## Ergebnis je Stufe

| Stufe | Checks |
|---|---|
| 1 Erfahrung | 4/4 |
| 2 Wissen | 2/2 |
| 3 Gedaechtnis | 3/3 |
| 4 Kognition | 1/1 |
| 5 Denken | 3/3 |
| 6 Nicht-Kognition | 3/3 |
| 7 Handeln | 2/2 |
| 8 Wissen+ | 2/2 |
| 9 MCP-Layer | 1/1 |
| 10 FWR | 1/1 |
| **Gesamt** | **22/22 = 100.0 %** |

## Alle Checks mit echter Ausgabe

### C1 – Secret im Text wird abgelehnt (Encoding-Gate)

**OK**

```
Privacy: Secret-Muster: Bearer\s+[A-Za-z0-9._\-+/=]{20,}
```

### C2 – sauberer Text wird angenommen

**OK**

```
ok
```

### C3 – 1. Aufnahme ok, identische Wiederholung -> Duplikat

**OK**

```
1.=accepted / 2.=rejected (Duplikat (SHA-256, 5-min-Fenster))
```

### C1b – PII landet NICHT auf der Platte (Datenminimierung §9.2a)

**OK**

```
Datensatz sess-pii=accepted, E-Mail im Logfile=False (Zeilen=88)
```

### C4 – GLiNER aktiv und liefert >=1 Entitaet

**OK**

```
backend={'gliner'} entities=[('Concept', 'Fast Write Routing')]
```

### C5 – 2. Lauf identisch (deterministisch)

**OK**

```
lauf1=[('Concept', 'Fast Write Routing')] lauf2=[('Concept', 'Fast Write Routing')]
```

### C6 – Knoten/Kanten eingetragen

**OK**

```
nodes=['Fast Write Routing'] edges=[('Knowledge-Agent', 'supersedes', 'alter Agent')]
```

### C7 – Gegenrichtungs-Konflikt abgelehnt

**OK**

```
rejected=[(('alter Agent', 'supersedes', 'Knowledge-Agent'), 'Konflikt: Gegenrichtung Knowledge-Agent supersedes alter Agent existiert')]
```

### C8 – Hub-Detection (Gewicht >= delta_hub)

**OK**

```
report={'hubs': [{'node': 'Fast Write Routing', 'weight': 3.0, 'action': 'hebbian-distillation'}, {'node': 'Knowledge-Agent', 'weight': 4.0, 'action': 'hebbian-distillation'}], 'forgotten': [], 'kept': [{'node': 'alter Agent', 'weight': 1.0}]}
```

### C9 – Tier1 episodic_graph.json analysebar (Hub-Erkennung)

**OK**

```
graph_keys=['edges', 'nodes'] hubs=['n2']
```

### C10 – Drift ueber tau -> Flag/Human-Gate

**OK**

```
report={'steps': 10, 'tau': 0.02, 'w_max': 0.6, 'flagged_steps': [6, 7, 8, 9, 10], 'max_DI': 0.0731, 'max_jsd': 0.0731} max_w<=0.6 OK
```

### C11 – Lyapunov fallend -> E[dV]<=0 -> gate=ok

**OK**

```
E_dV=-0.175 gate=ok
```

### C12 – Lyapunov steigend -> E[dV]>0 -> gate=ask

**OK**

```
E_dV=0.35 gate=ask
```

### C13 – PII wird VOR dem Store entfernt (minimiert)

**OK**

```
erkannt=['email', 'phone'] -> 'Kontakt oder hier.'
```

### C14 – Poisoning-Guard: untrusted+unverifiziert abgelehnt

**OK**

```
untrusted=untrusted source 'anon:web' (origin-bound) | trusted=verified + trusted origin
```

### C15 – Bias-Check: unter tau ok, ueber tau flag

**OK**

```
0.09->ok | 0.20->flag (drift 0.15)
```

### C16 – 2 distinkte Personen noetig: 1 -> verweigert, 2 -> approved

**OK**

```
1 Person: mind. 2 natürliche Personen erforderlich (aktuell 1) | 2 Personen: state=approved ['Batnini', 'Verifier2']
```

### C17 – Auto-Gate §9 korrekt (>=95 allow / 70-94 ask / <70 deny)

**OK**

```
100->allow, 94->ask, 69->deny
```

### C18 – alter Eintrag superseded (nicht geloescht), neuer confirmed

**OK**

```
v1 status=superseded superseded_by=2 wert='Konstrukt' | v2 outcome=superseded_old wert='Revise' history=2
```

### C21 – bi-temporale Semantik: as-of (valid x transaction), kein Hard-Delete

**OK**

```
facts=2 superseded=0 alt valid_to=2026-06-01 superseded_at=2026-06-01 | world 03/01=['Konstrukt'] 09/01=['Revise'] | wissen 03/01=['Konstrukt'] 09/01=['Revise']
```

### C19 – governance-mcp erreichbar, 3 Tools, Gate-Regel greift

**OK**

```
tools=['drift_index', 'lyapunov_check', 'resolve_entities'] drift_index gate=ask DI=0.0316
```

### C20 – Defaults tragen: A non-write, B write-new (kein Modell-ENV)

**OK**

```
small=nvidia/nemotron-3-nano-omni-30b-a3b-reasoning large=nvidia/nemotron-3-super-120b-a12b | A=non-write(stage 1) B=write-new(stage 2)
```

## Szenario

```
SYSTEMTEST KNOWLEDGE-AGENT  -  Szenario: 'Fehlermeldung mit PII + neues Konzept'
  Zeit: 2026-10-01 22:29:22   Repo: /home/opc/knowledge-agent
```

## Reproduktion

```bash
/home/opc/mcp-servers/hela-mem-mcp/.venv/bin/python /tmp/opencode/ka_systemtest.py
```

Erwartet: 22/22 = 100.0 % → Gate **allow** (§9: ≥ 95 % allow, 70–94 % ask, < 70 % deny).

## Offene Punkte (bewusst nicht gefixt)

- **`write-update`-Klasse des Fast Write Routers: geübt – siehe Beweis.** Fall C „Größte Wüste der Welt?“ (`correct="Sahara"`) → `write-update`; Rohtexte in `ergebnisse/fast-write-router.md:70-78`, Nachlauf 2026-10-01 in `ergebnisse/doku-korrektur-fwr.md`. In diesem Systemtest-Lauf kam C nicht vor (Szenarien A/B); in `fwr-test.md` §4 lief dieselbe Frage mit `correct="Antarctic Desert"` → `non-write`.
- ~~**Doku/Code-Abweichung** in `fast_write_router.py`: Doku sagt „zero-shot falsch + mit Memory korrekt“, der Code prüft nur `is_refusal(a_large)`.~~
  **Erledigt 2026-10-01 nach Gate-Freigabe:** `a_mem` wird ausgewertet, sonst
  `uncertain` + `gate=ask` (`ergebnisse/fwr-code-korrektur.md`); Tests in
  `tests/test_fwr.py`.
- `faulthandler.dump_traceback_later(300)` beendet den Lauf nach 5 Minuten – FWS-Modell-Ladezeiten liegen deutlich darunter, aber ein sehr langsamer Endpoint würde den Lauf abbrechen.

