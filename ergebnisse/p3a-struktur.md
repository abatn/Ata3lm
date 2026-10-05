# P3a — Struktur-Korrekturen (S1a/S1b/S3/S4/S5/S6, S2=A)

> Datum: 2026-10-05 · Status: **Auftrag** (Fixes) + **Belegt** (Regeln). Freigabe: `approved` (Batnini).
> Guardrail 7: echte Tests, 100 % Coverage. **Kein Commit** (Guardrail 6).

## 1. Umsetzungen

| ID | Befund | Fix | Regel | Datei |
|---|---|---|---|---|
| **S1a** | Revise lief trotz `Akt.ok=False` | Guard: bei abgelehnter `Akt`-Aktion `skipped=True`, kein HMM-Update | §3/§9 | `recursion_runner._phase_revise` |
| **S1b** | „Ground-Truth"-Label ohne Beobachtung | `observed=(ok+false)>0`; ohne Beobachtung „kein externes Signal … kein Claim" + Feld `observed` | §1/§6 | `recursion_runner._phase_compare` |
| **S2** | kein geteilter HMM/Gate-Zustand | **A (Doku-only):** Lücke dokumentiert (5-Phasen-HMM lauf-lokal; 8-Stufen-Runner ohne HMM; Gate/Mandat nicht geteilt). B = getrennt freizugeben. | §3 | dieses Dokument |
| **S3** | Bindings täuschten Integration vor | `PROCESS_MODE`-Map (`integriert`/`beispiel`); `bind()` liefert `mode` | §6/§11 | `connector_binding.py` |
| **S4** | niederer Trust senkte gespeicherten Trust | Equal-Value-Zweig ersetzt nur bei `new_trust > cur.trust` (Trust sinkt nie) | §10.7 | `shared_memory.py` |
| **S5** | Iterationsgrenze nicht ausgewiesen | `inference_status` (vollständig/unvollständig), `inference_complete`, `conforms_reliable`, `hint` | §6 | `shacl_inferenz.pipeline` |
| **S6** | harte `/home/opc/...`-Pfade | `ROOT = Path(__file__).resolve().parents[2|3]` (6 Module), MCP-Default repo-relativ | §6 | `ingestion_hook`, `reflective_agent`, `gaama_extract`, `shared_memory`, `lru_cache`, `mcp_memory_server` |

## 2. S2=A — dokumentierte Lücke (Auftrag)

- Der **5-Phasen-Runner** (`recursion_runner`) hält seine HMM-Trägheit (`HMMInertia`) **lauf-lokal**.
- Der **8-Stufen-Runner** (`lifecycle_runner`) führt **kein** HMM; Gate-/Mandat-Status wird **nicht** zwischen den Runnern geteilt.
- **Konsequenz:** keine durchgängige, laufübergreifende Selbst-Evolution. **Option B** (geteilter Zustand, neues Modul `runner_state.py`) = Interface-Neuzugang → **separater Human-Gate (§9)**. **Nicht umgesetzt.**

## 3. S6 — Persistenz-/Rekonstruktions-Lücke (dokumentiert)

- **In-Memory** (`WorkingMemory`, HMM-Trägheit, Drift) wird **nicht persistiert**; nach Neustart nur **teilweise** aus `knowledge/structured/` + `tier1-base/` rekonstruierbar.
- Harte Repo-Pfade sind entfernt (repo-relativ), sodass Pfade portabel sind — die **Zustands-Rekonstruktion** bleibt eine offene Struktur-Aufgabe (Auftrag).

## 4. Tests (echt, Guardrail 7)

- `test_recursion_runner.py`: `test_deny_keine_revision` (S1a), `test_compare_ohne_beobachtung_kein_ground_truth` (S1b).
- `test_connector_binding.py`: `test_bind_liefert_integrations_modus` (S3).
- `test_shared_memory.py`: `test_gleicher_wert_senkt_trust_nicht`, `test_gleicher_wert_hoeherer_trust_ersetzt` (S4).
- `test_shacl_inferenz.py`: `test_iterationsgrenze_als_unvollstaendig` (S5).
- `test_invariants.py`: `test_root_repo_relativ` (S6).
- **Volle Suite: 359 passed · 100 % (2757/670).**

## 5. Gate (§9)

- Verhaltens-/Interface-Änderungen → **approved** (Batnini). §9.1b: `AGENTS.md`/`tier1-base` unverändert.
- Guardrail 3: Provenienz `ergebnisse/rekursion/064-p3a-s1-s6.md`. Guardrail 6: **kein Commit**.
- **Offen:** S2=B (geteilter Zustand), S6-Rekonstruktion, P3b (CI) + P3c (Live).
