"""MCP-Live-Binding (data/memory/mcp_live_binding.py) — echter Live-Aufruf (Guardrail 7)."""

import sys
from pathlib import Path

import mcp_live_binding as mlb

ROOT = Path(__file__).resolve().parents[1]


def _own(extra_root: Path):
    return {
        "memory": {
            "command": [sys.executable, str(ROOT / "data/memory/mcp_memory_server.py")],
            "env": {"MCP_MEMORY_ROOT": str(extra_root)},
        }
    }


def test_tool_path_fingerprint():
    fp = mlb.tool_path_fingerprint([("memory", "memory.read"), ("graphiti", "search")])
    assert len(fp) == 16 and fp == mlb.tool_path_fingerprint([("memory", "memory.read"), ("graphiti", "search")])


def test_cross_endpoint_correlation():
    recs = [
        {"server": "a", "fingerprint": "x"},
        {"server": "b", "fingerprint": "x"},
        {"server": "c", "fingerprint": "y"},
        {"server": "d"},  # ohne Fingerprint -> ignoriert
    ]
    corr = mlb.cross_endpoint_correlation(recs)
    assert corr == {"x": ["a", "b"], "y": ["c"]}


def test_call_tool_live_eigener_server(tmp_path):
    out = mlb.call_tool_live("memory", "memory.search", {"query": "SHACL"}, servers=_own(tmp_path))
    assert out["ok"] is True
    assert out["server"] == "memory" and out["fingerprint"]
    assert any("SHACL" in c for c in out["content"])


def test_call_tool_live_unbekannter_server():
    out = mlb.call_tool_live("gibt-es-nicht", "x", servers={})
    assert out["ok"] is False and "konfiguriert" in out["error"]


def test_call_tool_live_fehler():
    servers = {"bad": {"command": ["/nonexistent-binary-xyz-123"]}}
    out = mlb.call_tool_live("bad", "x", servers=servers, timeout=20.0)
    assert out["ok"] is False and "error" in out


def test_catalog_server_live(tmp_path):
    out = mlb.catalog_server("memory", servers=_own(tmp_path))
    assert out["ok"] is True and out["n_tools"] >= 5
    assert "TOOL memory." in out["catalog"] and out["measure"]["tools"] >= 5


def test_catalog_server_unbekannt():
    out = mlb.catalog_server("gibt-es-nicht", servers={})
    assert out["ok"] is False


def test_catalog_server_probe_fehler():
    servers = {"bad": {"command": ["/nonexistent-binary-xyz-123"]}}
    out = mlb.catalog_server("bad", servers=servers, timeout=20.0)
    assert out["ok"] is False


def test_load_servers_ohne_config(monkeypatch):
    def _boom():
        raise FileNotFoundError("kein opencode.json")

    monkeypatch.setattr(mlb, "_load_probe", _boom)
    assert mlb.load_servers() == {}
