"""MCP-Memory-Server (data/memory/mcp_memory_server.py) – 5 Tools + Tri-Color Trust.

Offline: ROOT/Scopes auf tmp_path; MCP-SDK per Fake (lazy import).
"""

import sys
from types import SimpleNamespace

import mcp_memory_server as m
import pytest


def _setup(tmp_path, monkeypatch):
    scopes = {s: tmp_path / s for s in ["tier1", "tier2", "tier3", "structured", "connectors", "skills"]}
    for d in scopes.values():
        d.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(m, "SCOPES", scopes)
    monkeypatch.setattr(m, "ROOT", tmp_path)
    monkeypatch.setattr(m, "_LINKS", tmp_path / "tier2" / "mcp-links.jsonl")
    return scopes


def test_read_vorhanden_und_fehlend(tmp_path, monkeypatch):
    scopes = _setup(tmp_path, monkeypatch)
    (scopes["tier1"] / "identity.md").write_text("Ich bin der Agent.", encoding="utf-8")
    r = m.read("tier1", "identity.md")
    assert r["ok"] is True and r["content"] == "Ich bin der Agent."
    assert m.read("tier1", "fehlt.md")["ok"] is False


def test_scope_und_key_validierung(tmp_path, monkeypatch):
    _setup(tmp_path, monkeypatch)
    with pytest.raises(ValueError):
        m.read("unbekannt", "x.md")
    for bad in ["", "  ", "../etc/passwd", "/abs/pfad"]:
        with pytest.raises(ValueError):
            m.read("tier1", bad)


def test_write_tricolor(tmp_path, monkeypatch):
    scopes = _setup(tmp_path, monkeypatch)
    green = m.write("structured", "neu.md", "KI-Vorschlag", trust="green")
    assert green["ok"] and green["status"] == "proposed"
    blue = m.write("structured", "best.md", "Mensch", trust="blue")
    assert blue["ok"] and blue["status"] == "confirmed"
    red = m.write("structured", "boese.md", "Verstoß", trust="red")
    assert red["ok"] is False and red["status"] == "rejected"
    assert not (scopes["structured"] / "boese.md").exists()  # Red wird NICHT geschrieben
    assert m.write("structured", "x.md", "y", trust="gelb")["ok"] is False
    assert (scopes["structured"] / "neu.md").read_text(encoding="utf-8") == "KI-Vorschlag"


def test_search_alle_scopes_und_gezielt(tmp_path, monkeypatch):
    scopes = _setup(tmp_path, monkeypatch)
    (scopes["tier1"] / "a.md").write_text("Hub Detection\nanderes", encoding="utf-8")
    (scopes["skills"] / "b.md").write_text("hub detection in Skills", encoding="utf-8")
    assert m.search("")["ok"] is False
    alle = m.search("hub detection")
    assert alle["n_hits"] == 2 and {h["scope"] for h in alle["hits"]} == {"tier1", "skills"}
    nur = m.search("hub detection", scope="tier1")
    assert nur["n_hits"] == 1 and nur["hits"][0]["line"] == 1


def test_search_ueberspringt_nicht_utf8(tmp_path, monkeypatch):
    scopes = _setup(tmp_path, monkeypatch)
    (scopes["tier3"] / "bin.dat").write_bytes(b"\xff\xfe\x00\x01")
    (scopes["tier3"] / "ok.md").write_text("treffer", encoding="utf-8")
    (scopes["tier3"] / "unterordner").mkdir()  # Verzeichnis -> uebersprungen
    r = m.search("treffer")
    assert r["n_hits"] == 1 and r["hits"][0]["file"] == "ok.md"


def test_link_tricolor(tmp_path, monkeypatch):
    _setup(tmp_path, monkeypatch)
    g = m.link("tier1:ontology", "connectors:cognee", trust="green")
    assert g["ok"] and g["edge"]["status"] == "proposed"
    b = m.link("a", "b", trust="blue")
    assert b["edge"]["status"] == "confirmed"
    assert m.link("a", "b", trust="red")["status"] == "rejected"
    assert m.link("a", "b", trust="pink")["ok"] is False
    assert m.link("", "b")["ok"] is False


def test_consolidate_zaehlt_und_schreibt(tmp_path, monkeypatch):
    scopes = _setup(tmp_path, monkeypatch)
    (scopes["tier1"] / "a.md").write_text("x", encoding="utf-8")
    (scopes["tier1"] / "b.md").write_text("y", encoding="utf-8")
    out = m.consolidate()
    assert out["ok"] and out["scopes"]["tier1"]["files"] == 2
    written = (tmp_path / "tier2" / "mcp-consolidation.md").read_text(encoding="utf-8")
    assert "| tier1 | 2 |" in written


def test_build_server_registriert_5_tools(monkeypatch):
    calls = {}

    class FakeMCP:
        def __init__(self, name):
            calls["name"] = name

        def add_tool(self, fn, name=None, description=None):
            calls.setdefault("tools", []).append(name)

    fake = SimpleNamespace(FastMCP=FakeMCP)
    monkeypatch.setitem(sys.modules, "mcp", SimpleNamespace(server=SimpleNamespace(fastmcp=fake)))
    monkeypatch.setitem(sys.modules, "mcp.server", SimpleNamespace(fastmcp=fake))
    monkeypatch.setitem(sys.modules, "mcp.server.fastmcp", fake)
    server = m.build_server()
    assert isinstance(server, FakeMCP)
    assert calls["tools"] == ["memory.read", "memory.write", "memory.search", "memory.consolidate", "memory.link"]
