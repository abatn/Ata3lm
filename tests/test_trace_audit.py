"""K7/B3: Execution-Trace (OpenTelemetry-Spans) + dauerhaftes Auditprotokoll.

Quelle (HTTP 200, 2026-10-06): OpenTelemetry-Spec https://opentelemetry.io/docs/specs/otel/
Konzept: Spans ≠ Audit. Guardrail 7: echtes OTel-SDK, lokaler FileSpanExporter (kein Collector).
"""

import json

import trace_audit


def test_recorder_disabled_ist_noop():
    rec = trace_audit.Recorder()
    assert rec.spans_path is None and rec.audit_path is None and rec.tracer is None
    with rec.span("x", a=1) as sp:
        assert sp is None
    assert rec.audit("e", k=1) is None
    rec.flush()
    rec.shutdown()


def test_from_env_ohne_und_mit_dir(tmp_path):
    assert trace_audit.Recorder.from_env({}).spans_path is None
    rec = trace_audit.Recorder.from_env({"KNOWLEDGE_TRACE_DIR": str(tmp_path)})
    assert rec.spans_path == tmp_path / "spans.jsonl"
    assert rec.audit_path == tmp_path / "audit.jsonl"
    rec.shutdown()


def test_spans_graph_und_audit_trace_bezug(tmp_path):
    rec = trace_audit.Recorder(spans_path=tmp_path / "spans.jsonl", audit_path=tmp_path / "audit.jsonl")
    with rec.span("run", **{"skill.name": "act"}):
        rec.audit("a1", n=None)
        with rec.span("tool", tool=None):
            pass
        rec.audit("a2", ok=True, via="mcp")
    rec.audit("a3")  # außerhalb eines Spans -> keine gültige SpanContext
    rec.flush()

    spans = [json.loads(line) for line in (tmp_path / "spans.jsonl").read_text(encoding="utf-8").splitlines()]
    by_name = {s["name"]: s for s in spans}
    assert set(by_name) == {"run", "tool"}
    assert by_name["run"]["parent_span_id"] is None  # Wurzel
    assert by_name["run"]["attributes"] == {"skill.name": "act"}
    assert by_name["tool"]["parent_span_id"] == by_name["run"]["span_id"]  # Kind
    assert by_name["tool"]["attributes"] == {}  # None-Attribut wird ausgelassen
    assert by_name["run"]["trace_id"] == by_name["tool"]["trace_id"]

    audits = [json.loads(line) for line in (tmp_path / "audit.jsonl").read_text(encoding="utf-8").splitlines()]
    assert [a["event"] for a in audits] == ["a1", "a2", "a3"]
    assert audits[1]["trace_id"] and audits[1]["span_id"]  # im Span
    assert audits[2]["trace_id"] is None  # außerhalb -> kein gültiger Kontext
    rec.shutdown()


def test_audit_ohne_span_pfad_ist_noop(tmp_path):
    rec = trace_audit.Recorder(spans_path=tmp_path / "spans.jsonl")  # nur Spans
    assert rec.audit("e") is None
    rec.shutdown()


def test_audit_ohne_tracer_aber_mit_audit_pfad(tmp_path):
    """Audit ist eigenständig: funktioniert auch ohne Span-Tracer (Spans ≠ Audit)."""
    rec = trace_audit.Recorder(audit_path=tmp_path / "audit.jsonl")
    rec.audit("ohne-tracer", k=1)
    rec.flush()
    rec.shutdown()
    recs = [json.loads(line) for line in (tmp_path / "audit.jsonl").read_text(encoding="utf-8").splitlines()]
    assert recs == [{"ts": recs[0]["ts"], "event": "ohne-tracer", "trace_id": None, "span_id": None, "k": 1}]


def test_file_exporter_methoden(tmp_path):
    exporter = trace_audit.FileSpanExporter(tmp_path / "sub" / "spans.jsonl")
    assert exporter.shutdown() is None
    assert exporter.force_flush() is True
