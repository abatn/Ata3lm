#!/usr/bin/env python3
"""MCP-Live-Binding: ruft MCP-Server **live** über stdio auf (MCP-Spec) + Governance.

Quellen (verifiziert, §6):
  - **Intent Leakage by Design: Governance Gaps in MCP, Tool Use, and A2A**
    (Yuchia Chang, 2026) nennt wörtlich **Tool-Path Fingerprinting** („the sequence and
    combination of tool invocations leaks strategic intent") und **Cross-Endpoint
    Correlation** („behavioral patterns across independent MCP servers can be linked").
    (Der Auftrag nennt „Zenodo, 2026" — die verifizierte Primärquelle ist die Chang-Arbeit.)
  - **MCP-Spec** (Transporte): **stdio** (stdin/stdout) UND **Streamable HTTP**
    (ein HTTP-Endpunkt, POST/GET, `MCP-Protocol-Version`/`Mcp-Session-Id`).
    https://modelcontextprotocol.io/specification/2025-06-18/basic/transports
    (HTTP 200, geprüft 2026-10-06). SDK: `mcp.client.streamable_http`.
Integration: `mcp_catalog.py` (TTC-Katalog) + `scripts/mcp_probe.py` (load_servers/probe, stdio).
Guardrail 7: echte Aufrufe (keine Simulation). §11: MCP optional über lokaler Memory.
K7/B3: Konfigurations-Eintrag mit `url` → Streamable HTTP, sonst stdio (`command`).
"""

from __future__ import annotations

import asyncio
import hashlib
import importlib.util
import json
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


def _is_http(srv: dict) -> bool:
    """K7: Streamable-HTTP-Transport, wenn der Server eine `url` konfiguriert hat."""
    return bool(srv.get("url"))


async def _call_http(srv: dict, tool: str, arguments: dict, timeout: float) -> dict:
    """`tools/call` über Streamable HTTP (MCP-Spec 2025-06-18)."""
    from mcp import ClientSession
    from mcp.client.streamable_http import streamable_http_client

    async def _run() -> dict:
        async with streamable_http_client(srv["url"]) as (read, write, _cb):
            async with ClientSession(read, write) as session:
                await session.initialize()
                res = await session.call_tool(tool, arguments=arguments or {})
                texts = [getattr(b, "text", None) for b in (res.content or [])]
                return {"ok": not getattr(res, "isError", False), "content": [t for t in texts if t]}

    return await asyncio.wait_for(_run(), timeout=timeout)


async def _call(srv: dict, tool: str, arguments: dict, timeout: float) -> dict:
    if _is_http(srv):
        return await _call_http(srv, tool, arguments, timeout)
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


async def _probe_http(server_name: str, srv: dict, timeout: float) -> dict:
    """`tools/list` über Streamable HTTP → dieselbe Tool-Form wie `mcp_probe`."""
    from mcp import ClientSession
    from mcp.client.streamable_http import streamable_http_client

    async def _run() -> dict:
        async with streamable_http_client(srv["url"]) as (read, write, _cb):
            async with ClientSession(read, write) as session:
                await session.initialize()
                res = await session.list_tools()
                tools = [
                    {
                        "name": t.name,
                        "description": t.description or "",
                        "parameters": getattr(t, "inputSchema", None) or {},
                    }
                    for t in res.tools
                ]
                return {"server": server_name, "ok": True, "n_tools": len(tools), "tools": tools}

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


def _inner_ok(content: list) -> bool:
    """Fachlicher Erfolg aus dem inneren JSON (`ok`); fehlt/kein JSON → True."""
    for c in content:
        try:
            j = json.loads(c)
        except (json.JSONDecodeError, TypeError):
            continue
        if isinstance(j, dict) and "ok" in j:
            return bool(j["ok"])
    return True


def call_tool_live(
    server_name: str, tool: str, arguments: dict | None = None, *, servers: dict | None = None, timeout: float = 60.0
) -> dict:
    """Ruft ein MCP-Tool **live** auf (echte Ausführung): stdio oder Streamable HTTP."""
    servers = servers if servers is not None else load_servers()
    srv = servers.get(server_name)
    if srv is None:
        return {"server": server_name, "tool": tool, "ok": False, "error": "Server nicht (aktiv/lokal) konfiguriert"}
    try:
        out = asyncio.run(_call(srv, tool, arguments or {}, timeout))
        transport_ok = out["ok"]
        inner_ok = _inner_ok(out["content"])  # F5: fachlicher Erfolg (inneres JSON `ok`)
        return {
            "server": server_name,
            "tool": tool,
            "ok": transport_ok and inner_ok,  # Transport UND fachlich
            "transport_ok": transport_ok,
            "content": out["content"],
            "fingerprint": tool_path_fingerprint([(server_name, tool)]),
        }
    except Exception as exc:  # noqa: BLE001 - echte Fehler melden
        return {"server": server_name, "tool": tool, "ok": False, "error": f"{type(exc).__name__}: {str(exc)[:120]}"}


def catalog_server(server_name: str, *, servers: dict | None = None, timeout: float = 90.0) -> dict:
    """Live-Probe eines Servers + TTC-Katalog (`mcp_catalog`) — stdio oder Streamable HTTP."""
    servers = servers if servers is not None else load_servers()
    srv = servers.get(server_name)
    if srv is None:
        return {"server": server_name, "ok": False, "error": "Server nicht (aktiv/lokal) konfiguriert"}
    if _is_http(srv):  # K7: Streamable HTTP (MCP-Spec)
        try:
            res = asyncio.run(_probe_http(server_name, srv, timeout))
        except Exception as exc:  # noqa: BLE001 - echte Fehler melden
            return {"server": server_name, "ok": False, "error": f"{type(exc).__name__}: {str(exc)[:120]}"}
    else:
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
