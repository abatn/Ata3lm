#!/usr/bin/env python3
"""MCP-Probe: startet die aktivierten Projekt-MCP-Server und listet ihre Tools (echt).

Quelle: MCP Python SDK (stdio_client) · opencode.json (Server-Konfiguration).
Guardrail 7: echte Aktivierung + tools/list, keine Simulation. §11: MCP optional.
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

CFG = Path.home() / ".config/opencode/opencode.json"


def load_servers() -> dict:
    d = json.loads(CFG.read_text(encoding="utf-8"))
    out = {}
    for name, srv in d.get("mcp", {}).items():
        if not srv.get("enabled", True) or srv.get("type") == "remote" or not srv.get("command"):
            continue
        out[name] = srv
    return out


async def probe(name: str, srv: dict, timeout: float = 90.0) -> dict:
    cmd = srv["command"]
    env = {**os.environ, **(srv.get("env") or srv.get("environment") or {})}
    params = StdioServerParameters(command=cmd[0], args=cmd[1:], env=env)

    async def _run() -> dict:
        async with stdio_client(params) as (read, write):
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
                return {"server": name, "ok": True, "n_tools": len(tools), "tools": tools}

    try:
        return await asyncio.wait_for(_run(), timeout=timeout)
    except Exception as exc:  # noqa: BLE001 - echte Fehler melden
        return {"server": name, "ok": False, "error": f"{type(exc).__name__}: {str(exc)[:160]}"}


async def main() -> int:
    servers = load_servers()
    names = sys.argv[1:] or list(servers)
    results = []
    for name in names:
        if name not in servers:
            print(f"SKIP {name}: nicht (aktiv/lokal) konfiguriert")
            continue
        r = await probe(name, servers[name])
        results.append(r)
        print(f"OK   {name}: {r['n_tools']} Tools" if r["ok"] else f"FAIL {name}: {r['error']}")
    total = sum(r.get("n_tools", 0) for r in results)
    print(f"\nServer ok: {sum(1 for r in results if r['ok'])}/{len(results)} · Tools gesamt: {total}")
    out = Path("ergebnisse/mcp-probe.json")
    out.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print("geschrieben:", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
