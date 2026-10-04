"""MCP-Kontext: TTC-Konverter, Token-Messung, Lazy-Gating (TTC/Tool Attention/Strayspark).

Quellen: Zenodo 10.5281/zenodo.19869008 (TTC), arXiv:2604.21816 (Tool Attention),
Strayspark (char/4). Offline + deterministisch; echte Tools via mcp-SDK (skip sonst).
"""

import mcp_catalog as mc
import pytest


def test_count_tokens_leer_und_text():
    assert mc.count_tokens("") == 1
    assert mc.count_tokens("a" * 40) == 10


def test_type_of_liste_leer_und_none():
    assert mc._type_of({"type": ["string", "null"]}) == "string"
    assert mc._type_of({"type": []}) == "any"
    assert mc._type_of({}) == "any"


def test_mcp_schema_to_ttc_varianten():
    t = {
        "name": "gmail_send_email",
        "description": "send email",
        "parameters": {"properties": {"to": {"type": "string"}, "cc": {"type": "string"}}, "required": ["to"]},
        "outputSchema": "message_id",
        "err": "auth_failed",
        "when": "user wants to send email",
        "tags": ["gmail", "email"],
    }
    s = mc.mcp_schema_to_ttc(t)
    assert "TOOL gmail_send_email" in s
    assert "IN: to:string, cc:string?" in s
    assert "OUT: message_id" in s and "WHEN: user wants to send email" in s and "TAGS: gmail, email" in s
    # inputSchema-Variante + Defaults (keine Annotationen) + Nicht-String-Output
    t2 = {"name": "x", "inputSchema": {"properties": {}}, "outputSchema": {"type": "object"}}
    s2 = mc.mcp_schema_to_ttc(t2)
    assert "IN: -" in s2 and "ERR: unknown" in s2 and "TAGS: x" in s2 and "OUT: any" in s2


def test_build_measure_reduction():
    # Realistisch: param-reiche Schemas -> JSON-Schaffold > kompakter TTC-Block.
    props = {f"p{j}": {"type": "string", "description": "a parameter"} for j in range(8)}
    tools = [
        {"name": f"tool_{i}", "description": "does something", "parameters": {"properties": props, "required": ["p0"]}}
        for i in range(3)
    ]
    m = mc.measure(tools)
    assert m["tools"] == 3 and m["tokens_after"] < m["tokens_before"] and m["reduction_pct"] > 0
    assert mc.measure([])["reduction_pct"] == 0.0


def test_iso_score_leer():
    assert mc.iso_score("", "x") == 0.0
    assert mc.iso_score("a", "") == 0.0


def test_lazy_gate_und_top_k_per_stage():
    tools = [
        {"name": "memory.read", "description": "read a resource"},
        {"name": "memory.write", "description": "write with gate"},
        {"name": "slack.send", "description": "send a message"},
    ]
    g = mc.lazy_gate("read memory resource", tools, top_k=2)
    assert g[0]["name"] == "memory.read" and len(g) == 2
    out = mc.top_k_per_stage(tools, {"Erfahrung": "collect experience", "Handeln": "act"}, top_k=2)
    assert set(out) == {"Erfahrung", "Handeln"} and all(len(v) == 2 for v in out.values())


def test_real_tools_ttc_reduktion():
    """Echte 5 Tools unseres MCP-Servers -> TTC-Reduktion (real, mcp-SDK)."""
    pytest.importorskip("mcp")
    import mcp_memory_server as m

    srv = m.build_server()
    tools = [
        {"name": name, "description": t.description or "", "parameters": t.parameters or {}}
        for name, t in srv._tool_manager._tools.items()
    ]
    assert len(tools) == 5
    m2 = mc.measure(tools)
    assert m2["tokens_after"] < m2["tokens_before"] and m2["reduction_pct"] > 0
    assert len(mc.lazy_gate("Ressource lesen", tools, top_k=5)) == 5
