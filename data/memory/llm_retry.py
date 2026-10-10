#!/usr/bin/env python3
"""Bounded Retry/Backoff fuer echte LLM-Endpoint-Aufrufe (AGENTS.md Guardrail 7).

Kein Fake: Nur transiente Ueberlast-/Gateway-Fehler (429/5xx, "page not found",
"rate limit", "overloaded", Timeouts) werden mit Backoff wiederholt; alles andere
fliegt sofort. Muster: `tests/_live.py::call`, `scripts/ci_preflight.py`.

Quelle (Projekt-Auftrag, kein Paper): Ueberlast des geteilten NVIDIA-Endpoints
(Log: `Worker local total request limit reached (16/16)` → 503).
"""

from __future__ import annotations

import os
import time

RETRY_ATTEMPTS = int(os.environ.get("LLM_RETRY_ATTEMPTS", "10"))
RETRY_BASE_DELAY = float(os.environ.get("LLM_RETRY_BASE_DELAY", "1.0"))
RETRY_MAX_DELAY = float(os.environ.get("LLM_RETRY_MAX_DELAY", "30.0"))
TRANSIENT_STATUS = {429, 500, 502, 503, 504}
TRANSIENT_MARKERS = (
    "429",
    "500",
    "502",
    "503",
    "504",
    "overloaded",
    "resourceexhausted",
    "service unavailable",
    "internal server error",
    "timed out",
    "timeout",
    "temporarily",
    "rate limit",
    "rate_limit",
    "too many requests",
    "capacity",
    "page not found",
)


def is_transient(exc) -> bool:
    """True, wenn der Fehler ein Retry rechtfertigt (Ueberlast/Gateway)."""
    if getattr(exc, "status_code", None) in TRANSIENT_STATUS:
        return True
    text = str(exc).lower()
    return any(marker in text for marker in TRANSIENT_MARKERS)


def create_with_retry(client, *, models=None, **kwargs):
    """Chat-Completion mit begrenztem Retry/Backoff bei transienten Fehlern.

    `models`: optionale Modell-Kette. Ist sie gesetzt, wird pro Versuch das
    naechste Modell probiert (Fallback, falls ein Modell am Endpoint nicht
    verfuegbar ist -> 404 "page not found"). Echt: Antworten kommen immer vom
    echten Endpoint; es wird nur geduldig/ausweichend wiederholt (kein Fake).
    """
    chain = list(models) if models else None
    last = None
    for attempt in range(1, RETRY_ATTEMPTS + 1):
        call_kwargs = dict(kwargs)
        if chain:
            call_kwargs["model"] = chain[(attempt - 1) % len(chain)]
        try:
            return client.chat.completions.create(**call_kwargs)
        except Exception as exc:  # echte Fehler klassifizieren
            last = exc
            if not is_transient(exc) or attempt >= RETRY_ATTEMPTS:
                raise
            time.sleep(min(RETRY_MAX_DELAY, RETRY_BASE_DELAY * attempt))
    raise last  # pragma: no cover - Schleife endet nur via return/raise
