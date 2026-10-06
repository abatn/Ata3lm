#!/usr/bin/env python3
"""Execution-Trace (OpenTelemetry-Spans) + dauerhaftes Auditprotokoll (K7/B3).

Quellen (HTTP 200, geprüft 2026-10-06):
  - **OpenTelemetry Specification** — Traces sind Spans mit Trace-/SpanContext,
    Attributen, Zeitstempeln und Status; ein externer Collector ist nicht nötig.
    https://opentelemetry.io/docs/specs/otel/
  - **OpenTelemetry Python SDK** (`TracerProvider` + `SpanProcessor` + `SpanExporter`),
    lokal, kein Netz: https://opentelemetry.io/docs/languages/python/

Konzept (§6/ K7): **Spans ≠ Audit.**
  - *Spans* = flüchtige Telemetrie des Execution-Graphs/Timeline (parent/child,
    trace_id/span_id); hier als JSONL über einen lokalen `SpanExporter`.
  - *Audit* = dauerhaftes, append-only Protokoll (JSONL) mit Ergebnis je Aktion.
Beide sind **opt-in**: ohne `KNOWLEDGE_TRACE_DIR` bleibt der `Recorder` ein NOOP
(kein Repo-Write, keine Seiteneffekte). Guardrail 7: echtes OTel-SDK, kein Fake.
"""

from __future__ import annotations

import json
import os
import time
from contextlib import contextmanager
from pathlib import Path

from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor, SpanExporter, SpanExportResult

DEFAULT_SPANS_NAME = "spans.jsonl"
DEFAULT_AUDIT_NAME = "audit.jsonl"
TRACE_DIR_ENV = "KNOWLEDGE_TRACE_DIR"
TRACER_NAME = "knowledge-agent"


def _hex16(value: int) -> str:
    """Span-ID als 16-stelliger Hex-String (OTel-Spec)."""
    return format(value, "016x")


def _hex32(value: int) -> str:
    """Trace-ID als 32-stelliger Hex-String (OTel-Spec)."""
    return format(value, "032x")


def span_to_dict(span) -> dict:
    """Serialisiert einen beendeten Span (Trace-Graph/Timeline) in ein Dict."""
    ctx = span.get_span_context()
    parent = span.parent
    return {
        "name": span.name,
        "trace_id": _hex32(ctx.trace_id),
        "span_id": _hex16(ctx.span_id),
        "parent_span_id": _hex16(parent.span_id) if parent is not None else None,
        "start_time_unix_nano": span.start_time,
        "end_time_unix_nano": span.end_time,
        "status": span.status.status_code.name,
        "attributes": dict(span.attributes or {}),
    }


class FileSpanExporter(SpanExporter):
    """Schreibt beendete Spans als JSONL — lokaler Ersatz für einen Collector."""

    def __init__(self, path) -> None:
        self.path = Path(path)

    def export(self, spans) -> "SpanExportResult":
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as fh:
            for span in spans:
                fh.write(json.dumps(span_to_dict(span), ensure_ascii=False, default=str) + "\n")
        return SpanExportResult.SUCCESS

    def shutdown(self) -> None:
        return None

    def force_flush(self, timeout_millis: int = 30000) -> bool:
        return True


class Recorder:
    """Execution-Trace + Audit. Ohne Pfade = NOOP (kein Write)."""

    def __init__(self, spans_path=None, audit_path=None) -> None:
        self.spans_path = Path(spans_path) if spans_path is not None else None
        self.audit_path = Path(audit_path) if audit_path is not None else None
        self._provider = None
        self.tracer = None
        if self.spans_path is not None:
            self._provider = TracerProvider()
            self._provider.add_span_processor(SimpleSpanProcessor(FileSpanExporter(self.spans_path)))
            self.tracer = self._provider.get_tracer(TRACER_NAME)

    @classmethod
    def from_env(cls, env=None) -> "Recorder":
        """Recorder aus `KNOWLEDGE_TRACE_DIR` (leer/ungesetzt → NOOP)."""
        env = os.environ if env is None else env
        directory = env.get(TRACE_DIR_ENV)
        if not directory:
            return cls()
        base = Path(directory)
        return cls(spans_path=base / DEFAULT_SPANS_NAME, audit_path=base / DEFAULT_AUDIT_NAME)

    @contextmanager
    def span(self, name: str, **attributes):
        """OTel-Span als Kontext (parent/child über den aktiven Kontext)."""
        if self.tracer is None:
            yield None
            return
        with self.tracer.start_as_current_span(name) as span:
            for key, value in attributes.items():
                if value is not None:
                    span.set_attribute(key, value)
            yield span

    def audit(self, event: str, **fields):
        """Dauerhafter Audit-Eintrag (append-only JSONL) mit Trace-/Span-Bezug."""
        if self.audit_path is None:
            return None
        trace_id = span_id = None
        if self.tracer is not None:
            from opentelemetry import trace as otel_trace

            ctx = otel_trace.get_current_span().get_span_context()
            if ctx.is_valid:
                trace_id = _hex32(ctx.trace_id)
                span_id = _hex16(ctx.span_id)
        record = {"ts": time.time(), "event": event, "trace_id": trace_id, "span_id": span_id, **fields}
        self.audit_path.parent.mkdir(parents=True, exist_ok=True)
        with self.audit_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")
        return record

    def flush(self) -> None:
        if self._provider is not None:
            self._provider.force_flush()

    def shutdown(self) -> None:
        if self._provider is not None:
            self._provider.shutdown()
