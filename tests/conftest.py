"""Gemeinsame Infrastruktur der pytest-Läufe.

1) Importierbarkeit: `data/memory/` ist kein Package → `sys.path` erweitern.

2) ECHTE Verifikation (AGENTS.md Guardrail 7, Auftrag 2026-10-03):
   Tests/Compare laufen gegen das **echte** NVIDIA-Endpoint. Key/BaseURL werden –
   falls nicht in der Umgebung – aus `~/.config/opencode/opencode.json`
   (Provider `nvidia-llama-nemotron`) gelesen. **Keine** Platzhalter, **keine**
   Netz-Sperre, **keine** skripteten Antworten.
"""

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_CFG = Path.home() / ".config/opencode/opencode.json"
if not os.environ.get("OPENAI_API_KEY") and _CFG.exists():
    _opt = (
        json.loads(_CFG.read_text(encoding="utf-8"))
        .get("provider", {})
        .get("nvidia-llama-nemotron", {})
        .get("options", {})
    )
    if _opt.get("apiKey"):
        os.environ["OPENAI_API_KEY"] = _opt["apiKey"]
    if _opt.get("baseURL"):
        os.environ["OPENAI_BASE_URL"] = _opt["baseURL"]

for _p in ["data/memory", "data/memory/shared", "data/memory/tier3-working", "skills"]:
    sys.path.insert(0, str(ROOT / _p))
