# Rekursion 035: Experience-Route (echter Router) + dokumentierte Hub-Abweichung

> Datum: 2026-10-03 · Tiefe: `t=34 → t=35` · Phase: **Observe → Compare → Revise**
> Freigabe: `approved: Batnini, 2026-10-03` (Plan + Punkt 3 **A und D**).
> Ziel `g`: Router am echten Experience-Eintritt (A) + Hub-Abweichung dokumentieren (D);
> **kein Löschen/Ändern** am Hub-Pfad.

## 1. Quellen (geprüft)

- **AGENTS.md** §10.1 (Router beim Eintreffen eines Facts), §10.7 (Klassen-Verhaltenstest),
  §10.4 (Unsicherheit/neue Quelle → ask), §6 (keine Erfindungen).
- **Primärquelle** arXiv:2608.22215 (Dual-Layer): §3.1 Taxonomie (non-write/write-new/
  write-update) · §3.3 „the write router bypasses explicit three-way classification and
  directly optimizes … a **binary admission decision: write or discard**".
- **Stand der Technik** (GitHub): Mem0 (ADD/UPDATE/DELETE/NOOP), Letta/MemGPT
  (Self-Editing), LangMem, `kaiqiangh/memory-attention-router` („route, not dump"),
  `gjxwxt/agent-memory-router` (rules-router). → Klasse stets ENTSCHEIDUNG, nie fix.

## 2. Änderung (A, additiv)

| Datei | Änderung |
|---|---|
| `data/memory/ingestion_hook.py` | + `IngestionHook.route_experience(...)` → `pipeline.route_and_store(classify_fn=None)` = **echter** `fast_write_router` |
| Hub-Pfad `reflective_agent` | **unverändert** (feste Klasse bleibt, nur dokumentiert) |
| `AGENTS.md` | unverändert → kein vN-Snapshot |

## 3. Bekannte Abweichung (D)

Der Hub-Pfad setzt fest `write-new`. Auslegung: Hub = interne Konsolidierung (§3), keine
Experience (§10.1); `question`/`correct` fehlen für §10.7. Das Paper routet ohnehin
**binär** — ein fixer 3-Klassen-Wert ist weder belegt noch verboten. Deshalb: **nur
dokumentiert**, nicht gelöscht/geändert (Freigabe-Vorbehalt).

## 4. Compare-Beleg (extern)

```text
make test → 228 passed · Coverage 100,00 % (Line+Branch)
test_ingestion.py::test_route_experience_nutzt_echten_router  → action=write-new via echtem Router
test_mappings.py::test_hub_abweichung_dokumentiert             → Abweichung im Diagramm belegt
```

**Drift:** siehe `git diff --numstat` (nur additive Zeilen in `ingestion_hook.py`).

## 5. Gate (§9)

- Verhaltensänderung (neue Route) + Doku → **approved** (Batnini, 2026-10-03, A+D).
- §10.4: Router-Unsicherheit/neue Quelle → ask bleibt aktiv.
- §9.3-Zwei-Personen: Record `ergebnisse/fwr-code-korrektur.md` §0 (offen: 2. Person).

## 6. Nächstes Self-Feedback (t+1)

- Optionale Entscheidung des Auftraggebers: Hub-Route entweder behalten (Konsolidierung)
  oder entfernen — Entfernen nur mit separater Freigabe.
