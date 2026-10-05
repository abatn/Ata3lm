# Korrekturen P1 (F2 · F1 · S1)

> Datum: 2026-10-05 · Status: **Auftrag** (Fixes) + **Belegt** (Regeln). Freigabe: `approved` (Batnini).
> Basis: E2E-Audit + Verifikation (9/9 bestätigt). Guardrail 7: echte Repro-Tests, 100 % Coverage.
> Nur **P1** umgesetzt (P2/P3 offen). Kein Commit ohne Erlaubnis (Guardrail 6).

## 1. Umgesetzte Befunde

| ID | Befund | Fix | Regel | Datei:Zeile |
|---|---|---|---|---|
| **F2** | MCP speicherte PII ungefiltert | `trust.PIIFilter().minimize(content)` **vor** `write_text` | §9.2a | `mcp_memory_server.py` (`write`) |
| **F1** | `green` überschrieb bestätigtes `blue` | Trust-DB (`tier2/mcp-trust.json`): `green` auf `blue` → `rejected`; `tier1` nur `blue` | §9.2c/§9.3/§10.7 | `mcp_memory_server.py` (`_load_trust_db`/`_save_trust_db`/`write`) |
| **S1** | Pipeline ignorierte Router-`gate`/`uncertain` | `router.get("gate")=="ask"` (o. `uncertain`) → **kein Write**, `gate=ask` | §10.4 | `pipeline.py` (`route_and_store`, Schritt 2) |

## 2. Diff (Kern)

- **F2:** `clean = trust_mod.PIIFilter().minimize(content)`; `path.write_text(clean)`; `bytes = len(clean…)`.
- **F1:** `db = _load_trust_db(db_path)`; **fail-closed** wenn `db_path is None` (kein `tier2`) → `rejected`;
  `if db.get(f"{scope}/{key}")=="blue" and trust=="green": rejected`;
  `if scope=="tier1" and trust!="blue": rejected`; sonst `db[...] = trust; _save_trust_db(db_path, db)`.
- **S1:** vorher nur `classify_fn(...)["class"]`; jetzt `router` gelesen, `uncertain` → ask,
  `gate=="ask" and not self_update` → ask. Injektion ohne `gate` (Tests/Offline) bleibt unverändert.

## 3. Tests (echt, Guardrail 7)

- `tests/test_mcp_memory.py`: `test_write_minimiert_pii_vor_store` (F2), `test_green_ueberschreibt_blue_nicht` (F1),
  `test_tier1_nur_blue` (F1), `test_trust_db_kaputt_wird_ignoriert`.
- `tests/test_pipeline.py`: `test_router_gate_ask_blockiert_write` (S1), `test_router_uncertain_blockiert_write` (S1).
- **Volle Suite: 330 passed · 100 % (2672/628).**

## 4. Gate (§9)

- Verhaltensänderungen (MCP-Write-Gate, Pipeline-Gate) → **approved** (Batnini).
- Guardrail 3: Provenienz `ergebnisse/rekursion/058-fixes-p1.md`. §9.1b: `AGENTS.md` unverändert.
- Guardrail 6: **kein Commit** ohne Erlaubnis.
- **Ehrliche Grenzen:** `tier1`-nur-`blue` ist die **Auftrags**-Umsetzung von §9.2c
  („nur verifizierte Items werden gespeichert"). **Kein fail-open:** Fehlen die
  Trust-Metadaten (`tier2`), wird der Write **fail-closed** abgelehnt (§9.2c/§9.3) —
  das Gate ist nie stillschweigend inaktiv.
  **Offen (P2/P3):** F3 (lifecycle deny), S2 (echtes Supersede), S3 (Drift vor Write),
  F4 (bi-temporal `as_of`), F5 (Transport-≠Fach-`ok`), A9 (lazy Client).
