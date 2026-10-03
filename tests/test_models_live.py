"""Live-Erreichbarkeit der FWR-Default-Modelle – ECHT (AGENTS.md Guardrail 7).

Kein Fake/skriptet: pro Modell ein echter POST /chat/completions gegen das echte
NVIDIA-Endpoint (Key/BaseURL via `conftest.py`). Transiente Fehler (503/429)
werden bis zu 6× mit Backoff wiederholt; dauerhafter Ausfall (z. B. 404/410)
lässt den Test **scheitern**. Marker `network` → nicht Teil von `make test`.
"""

import os
import time

import fast_write_router as fwr
import pytest
from openai import OpenAI

_MAX_VERSUCHE = 6
_TRANSIENT = (429, 503)


def _client() -> OpenAI:
    return OpenAI(
        api_key=os.environ.get("OPENAI_API_KEY", ""),
        base_url=os.environ.get("OPENAI_BASE_URL", "https://integrate.api.nvidia.com/v1"),
    )


@pytest.mark.network
@pytest.mark.parametrize("model", [fwr.SMALL_MODEL, fwr.LARGE_MODEL])
def test_modelle_live(model):
    """Default-Modell-IDs sind per echtem HTTP-200-Call erreichbar (kein 404/410)."""
    client = _client()
    letzter = None
    for versuch in range(_MAX_VERSUCHE):
        try:
            antwort = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": "ping"}],
                max_tokens=1,
            )
            assert antwort.id, f"keine Response-Id für {model}"
            return
        except Exception as exc:  # noqa: BLE001 – echte Fehler klassifizieren
            letzter = exc
            if getattr(exc, "status_code", None) in _TRANSIENT and versuch < _MAX_VERSUCHE - 1:
                time.sleep(2**versuch)
                continue
            raise
    raise AssertionError(f"Modell nach {_MAX_VERSUCHE} Versuchen nicht erreichbar: {model}: {letzter}")
