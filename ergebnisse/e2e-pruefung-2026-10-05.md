# E2E-Prüfung (Lab-1) – 2026-10-05

> Basis: Rapport `fix-nachpruefung-e1a61b9.md` + `AGENTS.md` §1–§11. **Keine Produktänderungen, kein Commit.**
> Methode: Code-Lesen (read-only) + volle Suite (mit Key aus `opencode.json`). Erfindung verboten (§6).

## 1. Ausgangslage (Lab-1)

- **Revision:** `git rev-parse HEAD` = **`e1a61b92793d9d01a6132f5094fffbb14a3adf81`** — **identisch** mit der vom Rapport geprüften Revision (`e1a61b9`). Kein Diff.
- Gelesen: `AGENTS.md` (§1–§11), `README.md`, `CONTRIBUTING.md`, `ergebnisse/fixes-p1/p2/p3.md`, Rekursion 058–060.
- **Keine Erfolgsaussage** aus Commit-Nachrichten übernommen; alles unten belegt.

## 2. Tests (mit Key: `apiKey` aus `opencode.json`, conftest)

| Prüfung | Ergebnis |
|---|---|
| `make test` (inkl. network/live) | **337 passed · 0 failed · 100 % (2707/648)** |
| Ruff Lint / Format | bestanden / 70 Dateien |
| MD-Links / Artefakte / Secrets | 0 fehlend / 0 Fehler / 0 Treffer |
| **ci_preflight** | **FAIL** (liest `opencode.json` **nicht**; braucht `export OPENAI_*`) |
| `ci_drift.py` | läuft lokal (OK) |
| `ci.yml` | **`ci_drift` + `gitleaks` nicht verdrahtet** |
| pymarkdown (advisory) | rot (MD034 bare URL in `AGENTS.md`) — CI toleriert |

**Ehrlich:** Ohne Key/Provider = Audit-Sandbox (323/337, **98,06 %**) — die 14 Fehler sind **umgebungsabhängig** (13× „Missing credentials", 1× Fehler-Reflexionstest), **kein** neuer Produktfehler.

## 3. Befunde N1–N7 (Code-verifiziert)

| ID | Status | Beleg (Code) | Kern |
|---|---|---|---|
| **N1** Pfad-Alias | **OFFEN** | `mcp_memory_server._path` normalisiert den Pfad, die Trust-DB nutzt aber den **rohen** Key `f"{scope}/{key}"` (ab `write` Z.130) | `structured/./cur.md`, `cur.md` umgehen den Blue-Schutz |
| **N2** Metadaten-Verlust/‑Beschädigung | **OFFEN** | `_load_trust_db` → `{}` bei fehlender/kaputter `mcp-trust.json` | Green überschreibt Blue (fail-open); die fail-closed-Prüfung greift nur bei **fehlendem `tier2`-Scope**, nicht bei kaputter DB |
| **N3** Sekunden-Archivkollision | **OFFEN** | `pipeline.py` → `<slug>.superseded-{int(now)}.md` | zwei Updates in derselben Sekunde überschreiben einander (Beta verliert Alpha) |
| **N4** Tier3 veraltet | **BEHOBEN (063)** | `pipeline.py` write-update schreibt nur `structured`, Tier3 unberührt | Arbeitskopie bleibt auf dem alten Fakt |
| **N5** Skill-Fallback umgeht Validierung | **OFFEN** | `skill_interpreter._run_memory_write` except-Zweig schreibt `content` **roh** nach `fallback_dir/key` | schreibt PII, persistiert `trust=red`, `../key` escaped |
| **N6** raw vor Mandat | **BEHOBEN (063)** | `lifecycle_runner._stage_erfahrung` (`:80`) `wm.store("raw:…")` **vor** Stufe 3 (Mandat) | In-Memory-Änderung ohne Schreibmandat (kein Datei-Write) |
| **N7** Gate/Drift nicht gekoppelt | **BEHOBEN (063)** | `lifecycle_runner.run_cycle` übergibt **kein** `self_update`/`approvers`/`drift` an `route_and_store`; Stufe 8 nutzt feste `{non-write:0.5, write:0.5}` | echtes Router-`gate=ask` erreicht über den Runner keine Freigabe; Drift im Gesamtlauf ungeschützt |

**Behoben (Audit bestätigt):** F2 (PII im MCP-Kanonpfad), F4 (`valid_to_known_at`), F5 (`ok = Transport ∧ fachlich`), A9 (lazy Client). **Teilweise:** F1 (nur kanonischer Schlüssel), F3 (raw), S1 (Pipeline ja, Runner nein), S2 (Archiv ja, Kollision/Tier3/Tier1 nein), S3 (Pipeline ja, Runner nein).

## 4. Komponenten-/Verbindungsmatrix (Auszug)

| Komponente | Einstieg | Aufrufer | Ausgabe | Speicher | Berechtigung | Fehlerverhalten | Test |
|---|---|---|---|---|---|---|---|
| `mcp_memory_server.write` | stdio/FastMCP | skill_interpreter, connector_binding, Tests | `{ok,status,trust}` | scope/key | Tri-Color + fail-closed (nur fehlender tier2) | rejected | test_mcp_memory |
| `pipeline.route_and_store` | Funktion | ingestion_hook, Runner, Tests | `{ok,action,written,superseded,gate}` | structured/tier3 | Mandat→Router-Gate→Trust→Approval→Drift | ask/deny | test_pipeline |
| `lifecycle_runner.run_cycle` | CLI | Tests | `{trace}` | wm (raw/action) | **kein** Gate/Drift-Durchreichen | folgt `Gedächtnis.ok` | test_lifecycle_runner |
| `skill_interpreter._run_memory_write` | ReAct-Tool | run_skill_agent | `{via,result}` | MCP **oder Fallback** | MCP validiert; **Fallback nicht** | Fallback roh | test_skill_interpreter |
| `bi_temporal.as_of` | Funktion | Tests, (kein Prod-Aufruf) | Faktenliste | in-memory | — | — | test_bi_temporal |

**Kennzeichnung:** ausgeführter Code (alle oben); **reine Doku** (lifecycle-Phasen, Skills NL); **Beispieladapter/feste Werte** (Drift-Verteilung im Runner, `_default_llm`); **nicht angebunden** (bi_temporal in Prod, Tier1-Supersede in `route_and_store`).

## 5. Gesamtläufe (Runner)

| Runner | Status | Beleg |
|---|---|---|
| **8-Stufen** (`lifecycle_runner.run_cycle`) | läuft (offline → Stufe 5 NOOP); **Gate/Drift nicht durchgereicht** (N6/N7) | Rekursion 048/059 |
| **5-Phasen** (`reflective_agent.run_once` + `evaluator_version`) | läuft; Compare=`best_belief` (kein voller Grader-Loop), HMM-Zustand **nicht** geteilt | Rekursion 057 |
| **Zusammenarbeit** beider Runner | **nicht belegt** (kein gemeinsamer HITL-/HMM-Zustand) | — |

## 6. Maßnahmenplan

| Prio | Befund | Maßnahme | Regel |
|---|---|---|---|
| **P1** | N1 | Trust-Key über **normalisierten** Pfad (`Path(scope/key).relative_to(base)`) statt roher String | §9.2c |
| **P1** | N2 | fehlende/kaputte Trust-DB bei **existierender** Zieldatei → **fail-closed** (reject); nur „keine Datei" darf grün sein | §9.2c/§9.3 |
| **P1** | N5 | Fallback: `_path`-Validierung + PII-Filter + **kein** `../`, `red` → reject; Fallback nur bei echtem MCP-Ausfall, nicht bei Validierungsfehler | §9.2a/§9.2c |
| **P1** | N3 | Archivname mit **Monotonie/Unikat** (`superseded-<ts>-<hash>` oder Kollisions-Recheck) | §10.7 |
| **P2** | N4 | Update aktualisiert/invalidiert die Tier3-Kopie | §10.7 |
| **P2** | N6 | `raw:`-Write erst **nach** Mandat (oder Working-Memory-Write explizit als erlaubte Operation definieren) | §9.1 |
| **P2** | N7 | Runner: `self_update`/`approvers`/`drift` an `route_and_store` durchreichen | §9.1c/§10.4 |
| **P3** | Struktur | 5-Phasen-Runner (Revision/Compare), Connector-Adapter, Shared-Trust-Absenkung, SHACL-Iterationsgrenze, Persistenz/Provenienz | §6/§9 |
| **P3** | CI | `ci_preflight` liest `opencode.json`; `ci_drift`+`gitleaks` verdrahten; pymarkdown MD034 | §9.1d |
| **P3** | Live | echter Key/`BASE_URL`; beide Router-Modelle; 8-Stufen mit echter Reflexion; externe MCP + Fallback | Guardrail 7 |

## 7. Fazit (ehrlich)

- **Behoben:** F2, F4, F5, A9 (P0/060) · N1/N2/N5/N3 (P1/062) · **N4/N6/N7 (P2/063)**. **Teilweise:** F1, F3. **Offen:** P3 (Struktur/CI/Live).
- **Mit Key:** 337/337, 100 %. **Ohne Key** (Audit-Sandbox): 98,06 % — umgebungsbedingt.
- **Priorität:** N1/N2/N5 (Schutzumgehungen) + N3 (Archivverlust); danach Zustands-/CI-Kopplung + Live-Nachweis.

> **Stand 064 (2026-10-05):** aktuell **359 Tests / 100 % (2757/670)**. Die oben genannten
> Zahlen fixieren den **damaligen** Iterationsstand (Provenienz, §3/§9.1d) und wurden bewusst NICHT ersetzt.
