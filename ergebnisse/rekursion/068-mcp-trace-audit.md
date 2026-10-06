# Rekursion 068: K7 — MCP-Integration + Beobachtbarkeit (Spans ≠ Audit)

> Datum: 2026-10-06 · Tiefe: `t=67 → t=68` · Phasen: Observe → Compare → Revise.
> Freigabe: **`approved`** (Batnini, 2026-10-06) — optionale Parameter (`recorder`, `domain_rejected`) und der
> Streamable-HTTP-Transport sind **Interface-/Transport-Änderungen** (§9/Guardrail 4).
> Ziel `g`: Transportausfall ≠ Umgehung fachlicher Ablehnung; Trace + dauerhaftes Audit.

## 1. Quellen (verifiziert, §6)

- MCP-Spec 2025-06-18 (stdio + **Streamable HTTP**):
  <https://modelcontextprotocol.io/specification/2025-06-18> (HTTP 200, 2026-10-06);
  Transporte: <https://modelcontextprotocol.io/specification/2025-06-18/basic/transports> (200).
- OpenTelemetry-Spec: <https://opentelemetry.io/docs/specs/otel/> (HTTP 200, 2026-10-06).
- Vorlage: `ergebnisse/kopplung-komponenten-bericht.md` §K7; `AGENTS.md` §11.

## 2. Observe (`self_inspect` + `interact`)

- `skill_interpreter._run_memory_write` fing **jede** Exception und fiel in
  `_local_fallback`; der Fallback prüfte kein blue-Schutz / unbekannten Trust
  (Audit B3: fachliches `rejected` konnte umgangen werden).
- Nur stdio-Transport (`mcp_live_binding._server_params`); keine Spans/kein Audit.

## 3. Änderung (Diff)

| Datei | Änderung |
|---|---|
| `data/memory/write_gateway.py` | `DomainRejection`, `is_domain_rejection()`, `store_file(..., domain_rejected=False)` (Backstop) |
| `data/memory/skill_interpreter.py` | fachliches `rejected` → `via=mcp`, **kein** Fallback; `_fallback_domain_violation`; `run_skill_agent(..., recorder=None)` |
| `data/memory/mcp_live_binding.py` | Streamable HTTP (`_is_http`/`_call_http`/`_probe_http`) |
| `data/memory/trace_audit.py` | **neu**: OTel-Spans → JSONL + Audit (append-only JSONL) |
| `requirements-dev.txt` | `opentelemetry-api/sdk==1.45.0` |
| `tests/…` | K7-Tests (a/b/c) + `tests/test_trace_audit.py` |

## 4. Compare (externes Signal, Pflicht)

```text
Pflicht: tests/test_skill_interpreter.py + tests/test_write_gateway.py  -> 48 passed
K7-Set:  + test_trace_audit + test_mcp_live_binding + test_skill_binding  -> 93 passed
Coverage: trace_audit 100 % · skill_interpreter 100 % · mcp_live_binding 100 %
HTTP-Beleg: realer lokaler FastMCP-Server (uvicorn) + streamable_http_client
```

- (a) Domain-Reject → kein Fallback-Write ✅
- (b) Transportfehler → geschützter Fallback (blue/fail-closed) ✅
- (c) Audit-Eintrag + Span-Graph entstehen ✅

## 5. Gate (§9) + Provenienz

- Interface-/Transport-Änderungen → **§9 `approved`** (Batnini, 2026-10-06).
- G4 markiert (kein self-update an Originaldateien ohne `approved`), G6 (kein Git) eingehalten.
- Peer-Doku: `ergebnisse/mcp-trace-audit.md`.
- Nächstes Self-Feedback: nach `approved` Voll-Suite-100 % mit Live-Key nachziehen.
