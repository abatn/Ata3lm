"""MCP-Live-Binding (data/memory/mcp_live_binding.py) — echter Live-Aufruf (Guardrail 7)."""

import socket
import sys
import threading
import time
from pathlib import Path

import mcp_live_binding as mlb
import mcp_memory_server
import pytest

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


def test_call_tool_live_rejected_write(tmp_path):
    """F5: fachliche Ablehnung (inner ok=false) → outer ok=false (Transport bleibt ok)."""
    out = mlb.call_tool_live(
        "memory",
        "memory.write",
        {"scope": "tier3", "key": "r.md", "content": "x", "trust": "red"},
        servers=_own(tmp_path),
    )
    assert out["ok"] is False and out["transport_ok"] is True


def test_inner_ok_zweige():
    assert mlb._inner_ok(['{"ok": false}']) is False
    assert mlb._inner_ok(['{"ok": true}']) is True
    assert mlb._inner_ok(["nicht json"]) is True
    assert mlb._inner_ok(['{"x": 1}']) is True
    assert mlb._inner_ok([]) is True


# --- K7: Streamable HTTP (MCP-Spec 2025-06-18) — echter lokaler Server ---


def test_is_http_transportwahl():
    assert mlb._is_http({"url": "http://127.0.0.1:1/mcp"}) is True
    assert mlb._is_http({"command": ["x"]}) is False


@pytest.fixture
def http_memory_server(tmp_path, monkeypatch):
    """Startet den Memory-Server REAL über Streamable HTTP (uvicorn, lokaler Port)."""
    t2, t3 = tmp_path / "t2", tmp_path / "t3"
    t2.mkdir()
    t3.mkdir()
    (t3 / "note.md").write_text("MARKER-HTTP", encoding="utf-8")
    monkeypatch.setattr(mcp_memory_server, "SCOPES", {"tier2": t2, "tier3": t3})

    sock = socket.socket()
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    sock.close()

    import uvicorn

    server = mcp_memory_server.build_server()
    config = uvicorn.Config(server.streamable_http_app(), host="127.0.0.1", port=port, log_level="error")
    uv = uvicorn.Server(config)
    thread = threading.Thread(target=uv.run, daemon=True)
    thread.start()
    for _ in range(200):
        if uv.started:
            break
        time.sleep(0.05)
    assert uv.started, "HTTP-MCP-Server nicht gestartet"
    yield {"url": f"http://127.0.0.1:{port}/mcp"}
    uv.should_exit = True
    thread.join(timeout=10)


def test_call_tool_live_streamable_http(http_memory_server):
    out = mlb.call_tool_live(
        "memory", "memory.search", {"query": "MARKER-HTTP"}, servers={"memory": http_memory_server}, timeout=30.0
    )
    assert out["ok"] is True and out["transport_ok"] is True
    assert any("MARKER-HTTP" in c for c in out["content"])


def test_catalog_server_streamable_http(http_memory_server):
    out = mlb.catalog_server("memory", servers={"memory": http_memory_server}, timeout=30.0)
    assert out["ok"] is True and out["n_tools"] >= 5 and "TOOL memory." in out["catalog"]


def test_call_tool_live_http_fehler():
    servers = {"bad": {"url": "http://127.0.0.1:9/mcp"}}  # discard-Port -> Transportfehler
    out = mlb.call_tool_live("bad", "x", servers=servers, timeout=5.0)
    assert out["ok"] is False and "error" in out


def test_catalog_server_http_probe_fehler():
    servers = {"bad": {"url": "http://127.0.0.1:9/mcp"}}
    out = mlb.catalog_server("bad", servers=servers, timeout=5.0)
    assert out["ok"] is False and "error" in out
