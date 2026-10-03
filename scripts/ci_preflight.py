#!/usr/bin/env python3
"""
CI-Preflight: prüft, ob der konfigurierte LLM-Endpoint erreichbar ist.

Liest OPENAI_API_KEY und OPENAI_BASE_URL aus der Umgebung, führt einen echten
Chat-Completion-Call aus (bis zu 8 Versuche mit Backoff bei transienten
Fehlern) und gibt Statusmeldungen nach stdout aus.

Exit-Code: 0 = Endpoint erreichbar, 1 = nicht erreichbar.
"""

from __future__ import annotations

import os
import sys
import time

DEFAULT_MODEL = "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning"
MAX_ATTEMPTS = 8
TRANSIENT_MARKERS = ("overloaded", "rate limit", "429", "503", "temporarily")


def is_transient(exc: Exception) -> bool:
    """Erkennt transiente Fehler anhand von Status-Code oder Meldung."""
    status = getattr(exc, "status_code", None)
    if status in (429, 503):
        return True
    text = str(exc).lower()
    return any(marker in text for marker in TRANSIENT_MARKERS)


def main() -> int:
    """Führt den Preflight-Call aus und liefert den Exit-Code."""
    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    base_url = os.environ.get("OPENAI_BASE_URL", "").strip()
    model = os.environ.get("FWR_SMALL_MODEL", "").strip() or DEFAULT_MODEL

    if not api_key:
        print("FAIL: OPENAI_API_KEY ist nicht gesetzt.")
        return 1

    try:
        from openai import OpenAI
    except ImportError:
        print("FAIL: openai-Paket ist nicht installiert.")
        return 1

    options = {"api_key": api_key}
    if base_url:
        options["base_url"] = base_url
    client = OpenAI(**options)
    print(f"Preflight: Modell={model} Endpoint={base_url or 'default'}")

    last_error = ""
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": "ping"}],
                max_tokens=8,
            )
            content = response.choices[0].message.content if response.choices else ""
            print(f"OK: Versuch {attempt} erfolgreich (Antwort: {content!r}).")
            return 0
        except Exception as exc:
            last_error = f"{type(exc).__name__}: {exc}"
            if is_transient(exc) and attempt < MAX_ATTEMPTS:
                delay = min(2**attempt, 30)
                print(f"Transienter Fehler (Versuch {attempt}/{MAX_ATTEMPTS}): {last_error} – warte {delay}s.")
                time.sleep(delay)
                continue
            break

    print(f"FAIL: Endpoint nicht erreichbar. Letzter Fehler: {last_error}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
