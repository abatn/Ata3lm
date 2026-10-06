# K7 — MCP-Integration + Beobachtbarkeit (Spans ≠ Audit)

> Datum: 2026-10-06 · Status: **implementiert** · §9-Freigabe **`approved`** (Batnini, 2026-10-06).
> Ziel `g`: Transportausfall nutzt den **geschützten** lokalen Fallback, eine
> **fachliche Ablehnung** wird dadurch NIE umgangen; Execution-Trace (OTel-Spans)
> und ein **dauerhaftes Auditprotokoll** entstehen real.

## 1. Quellen (verifiziert, HTTP 200, 2026-10-06)

- **MCP-Spec 2025-06-18** (Transporte: stdio UND Streamable HTTP):
  <https://modelcontextprotocol.io/specification/2025-06-18> → 200;
  Transporte: <https://modelcontextprotocol.io/specification/2025-06-18/basic/transports> → 200.
- **OpenTelemetry-Spec**: <https://opentelemetry.io/docs/specs/otel/> → 200.
- SDK lokal verifiziert: `mcp==1.30.0` (`mcp.client.streamable_http.streamable_http_client`),
  `opentelemetry-api==1.45.0`, `opentelemetry-sdk==1.45.0`.

Die Quellen rechtfertigen **Muster** (Transport/Spans); die Durchsetzung (Gates,
Audit-Format) ist Projekt-**Auftrag** (vgl. Bericht §6 Review-Korrektur 1).

## 2. Änderung (Diff)

| Datei | Änderung | §9 |
|---|---|---|
| `data/memory/skill_interpreter.py` | `_run_memory_write`: fachliches `rejected` (MCP-Ergebnis **und** `DomainRejection`/`__cause__`) → `via=mcp`, **kein** Fallback; `_fallback_domain_violation` (blue-Schutz + existing/unknown fail-closed); `run_skill_agent(..., recorder=None)` mit Spans + Audit | **ja** (optionaler Parameter) |
| `data/memory/write_gateway.py` | `DomainRejection`, `is_domain_rejection()`, Backstop-Parameter `store_file(..., domain_rejected=False)` | **ja** (optionaler Parameter) |
| `data/memory/mcp_live_binding.py` | Streamable-HTTP-Adapter (`_is_http`, `_call_http`, `_probe_http`); `call_tool_live`/`catalog_server` wählen stdio **oder** HTTP anhand `url` | **ja** (Transport) |
| `data/memory/trace_audit.py` | **neu**: `Recorder` (OTel-Spans → JSONL, lokaler FileExporter, kein Collector) + Audit-Log (append-only JSONL) | neues Modul |
| `requirements-dev.txt` | `opentelemetry-api==1.45.0`, `opentelemetry-sdk==1.45.0` (gepinnt) | Abhängigkeit |
| `tests/…` | neue Tests (K7) | – |

**Fail-closed-Regel (B3):** Nur ein **echter Transport-/SDK-Ausfall** erreicht
`_local_fallback`. Ein fachliches `rejected` (red, blue-geschützt, unbekannter
Trust, Poisoning) wird als MCP-Ergebnis zurückgegeben — nie in einen Write
übersetzt. Der Fallback selbst prüft zusätzlich blue-Schutz und ist bei
fehlenden Trust-Metadaten für **existierende** Ziele fail-closed.

**Spans ≠ Audit:** OTel-Spans (`spans.jsonl`, trace_id/span_id/parent) sind
Telemetrie; das Audit (`audit.jsonl`) ist dauerhaft, append-only und hält das
Ergebnis je Aktion. `KNOWLEDGE_TRACE_DIR` aktiviert beides; ungesetzt = NOOP.

## 3. Compare (extern, echt)

```text
Pflichtlauf: pytest tests/test_skill_interpreter.py tests/test_write_gateway.py -q --no-cov
  -> 48 passed
Alle K7-Tests: + test_trace_audit, test_mcp_live_binding, test_skill_binding
  -> 93 passed
Coverage (isoliert, addopts=""):
  trace_audit.py       100 % (82 stmts · 22 branches)
  skill_interpreter.py 100 % (214 stmts · 52 branches)
  mcp_live_binding.py  100 % (110 stmts · 18 branches)
  write_gateway.py     neue Zeilen (DomainRejection/Guard) abgedeckt
HTTP: echter lokaler FastMCP-Server über uvicorn + streamable_http_client (kein Fake)
```

**Abnahmen (§4):**
- (a) Domain-Reject → kein Fallback-Write ✅ (`test_k7_domain_reject_kein_fallback`,
  `…_domain_rejection_exception…`, `…_domain_rejection_cause…`,
  `test_is_domain_rejection_und_domain_rejected_guard`).
- (b) Transportfehler → geschützter Fallback ✅ (bestehende N5-Tests + neu
  `test_k7_fallback_blue_geschuetzt`, `…_existing_unknown_trust_fail_closed`,
  `…_ohne_trust_db_existing_fail_closed`).
- (c) Audit-Eintrag entsteht ✅ (`test_run_skill_agent_mit_recorder`,
  `test_spans_graph_und_audit_trace_bezug`).

## 4. Offene / blockierte Punkte

- **§9-Freigabe erteilt** (Batnini, 2026-10-06): der `recorder`-Parameter und `domain_rejected`
  sowie der Streamable-HTTP-Transport sind freigegeben (Guardrail 4 gewahrt).
- **Voll-Suite-100 %:** hier nicht erneut gefahren (Live-LLM-Kosten, Guardrail 7);
  die geänderten Module sind je isoliert 100 %. Unverändert durch K7.
- **Kein OTel-Collector:** bewusst lokal (Spec-konform, kein Netz).

## 5. Regelkonformität

- G6 (kein Git) eingehalten · G7 (echte Tests: OTel-SDK, realer HTTP-Server, echte MCP-Calls).
- Keine erfundenen Quellen/Scores; alle Links HTTP 200.
