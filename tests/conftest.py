"""Gemeinsame Infrastruktur der pytest-Läufe (Quelle: pytest-Doku).

1) Importierbarkeit: `data/memory/` ist KEIN Python-Package (kein `__init__.py`);
   das Verzeichnis wird deshalb vor dem Import in `sys.path` gesetzt.

2) Netzwerk-Sperre: `fast_write_router.py` legt BEIM IMPORT den OpenAI-Client an
   und wirft ohne Key einen Fehler (`openai.OpenAIError: Missing credentials`).
   Der Test-Run setzt deshalb eine Platzhalter-Key und eine nicht erreichbare
   Base-URL: ein versehentlicher Live-Aufruf schlägt sofort fehl, statt das echte
   Endpoint zu treffen. Zusätzlich werden `FWR_*_MODEL` entfernt, damit die
   Code-Defaults (AGENTS.md:252) getestet werden, nicht die Shell-Umgebung.

3) Alle LLM-Antworten in den Tests sind skriptet (pytest `monkeypatch`-Fixture,
   docs.pytest.org/en/stable/how-to/monkeypatch.html) – es wird nie das Netz
   benutzt.
"""

import os
import sys
from pathlib import Path

os.environ["OPENAI_API_KEY"] = "ci-platzhalter-kein-netzwerk"
os.environ["OPENAI_BASE_URL"] = "http://127.0.0.1:9"
os.environ.pop("FWR_SMALL_MODEL", None)
os.environ.pop("FWR_LARGE_MODEL", None)

ROOT = Path(__file__).resolve().parents[1]
for _p in ["data/memory", "data/memory/shared", "data/memory/tier3-working", "skills"]:
    sys.path.insert(0, str(ROOT / _p))
