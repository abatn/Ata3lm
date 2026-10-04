#!/usr/bin/env python3
"""MCP-Live-Binding: ruft MCP-Server **live** über stdio auf (MCP-Spec) + Governance.

Quellen (verifiziert, §6):
  - **Intent Leakage by Design: Governance Gaps in MCP, Tool Use, and A2A**
    (Yuchia Chang, 2026) nennt wörtlich **Tool-Path Fingerprinting** („the sequence and
    combination of tool invocations leaks strategic intent") und **Cross-Endpoint
    Correlation** („behavioral patterns across independent MCP servers can be linked").
    (Der Auftrag nennt „Zenodo, 2026" — die verifizierte Primärquelle ist die Chang-Arbeit.)
  - **MCP-Spec** (stdio transport): Client ruft `tools/call` über stdin/stdout.
    https://modelcontextprotocol.io/specification
Integration: `mcp_catalog.py` (TTC-Katalog) + `scripts/mcp_probe.py` (load_servers/probe, stdio).
Guardrail 7: echte Aufrufe (keine Simulation). §11: MCP optional über lokaler Memory.
"""

from __future__ import annotations

import asyncio
import hashlib
import importlib.util
import os
from pathlib import Path

import mcp_catalog

# CI-Stabilität: Kinder-Prozesse (stdio-MCP-Server) dürfen die pytest-cov-Umgebung NICHT
# erben — sonst schreiben sie in dieselbe Coverage-Datei (flakige 99,x %). Explizite Pops
# (immer ausgeführt → deterministische Coverage).
os.environ.pop("COV_CORE_SOURCE", None)
os.environ.pop("COV_CORE_CONFIG", None)
os.environ.pop("COV_CORE_DATAFILE", None)
os.environ.pop("COVERAGE_PROCESS_START", None)

ROOT = Path(__file__).resolve().parents[2]  # repo-relativ (CI-tauglich)


def _load_probe():
    """Importiert `scripts/mcp_probe.py` (stdio-Helfer) ohne Package-Zwang."""
    spec = importlib.util.spec_from_file_location("mcp_probe", ROOT / "scripts/mcp_probe.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_servers() -> dict:
    """Aktive lokale MCP-Server aus `opencode.json` (leer, wenn Config fehlt → CI-tauglich)."""
    try:
        return _load_probe().load_servers()
    except FileNotFoundError:
        return {}


def _server_params(srv: dict):
    from mcp import StdioServerParameters

    cmd = srv["command"]
    env = {**os.environ, **(srv.get("env") or srv.get("environment") or {})}
    return StdioServerParameters(command=cmd[0], args=cmd[1:], env=env)


async def _call(srv: dict, tool: str, arguments: dict, timeout: float) -> dict:
    from mcp import ClientSession
    from mcp.client.stdio import stdio_client

    async def _run() -> dict:
        async with stdio_client(_server_params(srv)) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                res = await session.call_tool(tool, arguments=arguments or {})
                texts = [getattr(b, "text", None) for b in (res.content or [])]
                return {"ok": not getattr(res, "isError", False), "content": [t for t in texts if t]}

    return await asyncio.wait_for(_run(), timeout=timeout)


def tool_path_fingerprint(tool_calls: list) -> str:
    """Tool-Path Fingerprinting (Chang 2026): stabile ID der Aufruf-Sequenz `[(server, tool)]`."""
    norm = "|".join(f"{s}::{t}" for s, t in tool_calls)
    return hashlib.sha256(norm.encode("utf-8")).hexdigest()[:16]


def cross_endpoint_correlation(records: list) -> dict:
    """Cross-Endpoint Correlation (Chang 2026): gleiche Tool-Pfade über Server gruppieren."""
    groups: dict[str, set] = {}
    for r in records:
        fp = r.get("fingerprint")
        if fp:
            groups.setdefault(fp, set()).add(r.get("server"))
    return {fp: sorted(s) for fp, s in groups.items()}


def call_tool_live(
    server_name: str, tool: str, arguments: dict | None = None, *, servers: dict | None = None, timeout: float = 60.0
) -> dict:
    """Ruft ein MCP-Tool **live** über stdio auf (echte Ausführung)."""
    servers = servers if servers is not None else load_servers()
    srv = servers.get(server_name)
    if srv is None:
        return {"server": server_name, "tool": tool, "ok": False, "error": "Server nicht (aktiv/lokal) konfiguriert"}
    try:
        out = asyncio.run(_call(srv, tool, arguments or {}, timeout))
        return {
            "server": server_name,
            "tool": tool,
            "ok": out["ok"],
            "content": out["content"],
            "fingerprint": tool_path_fingerprint([(server_name, tool)]),
        }
    except Exception as exc:  # noqa: BLE001 - echte Fehler melden
        return {"server": server_name, "tool": tool, "ok": False, "error": f"{type(exc).__name__}: {str(exc)[:120]}"}


def catalog_server(server_name: str, *, servers: dict | None = None, timeout: float = 90.0) -> dict:
    """Live-Probe eines Servers + TTC-Katalog (`mcp_catalog`) — Integration mcp_probe + mcp_catalog."""
    servers = servers if servers is not None else load_servers()
    srv = servers.get(server_name)
    if srv is None:
        return {"server": server_name, "ok": False, "error": "Server nicht (aktiv/lokal) konfiguriert"}
    res = asyncio.run(_load_probe().probe(server_name, srv, timeout=timeout))
    if not res.get("ok"):
        return {"server": server_name, "ok": False, "error": res.get("error")}
    return {
        "server": server_name,
        "ok": True,
        "n_tools": res["n_tools"],
        "measure": mcp_catalog.measure(res["tools"]),
        "catalog": mcp_catalog.build_catalog(res["tools"]),
    }


if __name__ == "__main__":  # pragma: no cover - CLI
    import json
    import sys

    # Eigener Memory-Server live über stdio (MCP_MEMORY_ROOT → /tmp, Repo bleibt sauber).
    own = {
        "memory": {
            "command": [sys.executable, str(ROOT / "data/memory/mcp_memory_server.py")],
            "env": {"MCP_MEMORY_ROOT": "/tmp/mcp-live-root"},
        }
    }
    out = call_tool_live("memory", "memory.search", {"query": "SHACL"}, servers=own)
    print(json.dumps(out, ensure_ascii=False, indent=2))
