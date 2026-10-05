"""Echte Live-Calls mit Retry für transiente Endpoint-Fehler (AGENTS.md Guardrail 7).

Kein Fake: `call(...)` ruft die **echte** Funktion (LLM/Endpoint). Nur transiente
Netz-/Überlastfehler (503/429/…) werden mit Backoff wiederholt — das ist echte
Verifikation, keine skriptete Antwort.
"""

import random
import time

_RETRYABLE = (
    "503",
    "429",
    "overloaded",
    "resourceexhausted",
    "service unavailable",
    "timed out",
    "timeout",
    "temporarily",
    "rate limit",
    "rate_limit",
    "too many requests",
    "capacity",
)


def call(fn, *args, attempts: int = 18, base_delay: float = 4.0, max_delay: float = 20.0, **kwargs):
    """Echte Funktion aufrufen; nur transiente Fehler wiederholen."""
    last = None
    for i in range(attempts):
        try:
            return fn(*args, **kwargs)
        except Exception as exc:  # noqa: BLE001 - echte Fehler prüfen
            last = exc
            if not any(m in str(exc).lower() for m in _RETRYABLE):
                raise
            time.sleep(min(max_delay, base_delay * (i + 1)) + random.uniform(0, 1))
    raise last
