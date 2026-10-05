"""Connector-Binding (data/memory/connector_binding.py) — echte Bindung (Guardrail 7)."""

from pathlib import Path

import connector_binding as cb
import mandate
import mcp_memory_server

ROOT = Path(__file__).resolve().parents[1]


def _ctx(tmp_path):
    return {
        "question": "Wo?",
        "fact": "Kontakt: max@example.com, Version 2.",
        "correct": "Version 2.",
        "classify_fn": lambda q, f, c: {"class": "write-new"},
        "mandate_obj": mandate.Mandate(
            mandate_id="t",
            principal="Batnini",
            agent="knowledge-agent",
            actions=frozenset({"write:memory"}),
            resources=frozenset({"data/memory"}),
            amount_limit=1.0,
            max_uses=100,
            valid_from=0.0,
            valid_until=1e12,
            approval_threshold=0.5,
        ),
        "now": 100.0,
        "structured_dir": tmp_path / "structured",
        "tier3_dir": tmp_path / "tier3",
    }


def test_parse_connector_real():
    spec = cb.parse_connector(ROOT / "connectors/htac-agentdice.md")
    assert spec["name"] == "htac-agentdice"
    assert spec["process"] == "pipeline.py"
    assert spec["phase"]


def test_parse_connector_ohne_prozess(tmp_path):
    p = tmp_path / "x.md"
    p.write_text("# x\nkein Prozess hier.\n", encoding="utf-8")
    spec = cb.parse_connector(p)
    assert spec["process"] is None and spec["phase"] == ""


def test_validate_connector_shacl():
    assert cb.validate_connector({"name": "a", "process": "pipeline.py"})["conforms"] is True
    assert cb.validate_connector({"name": "b", "process": None})["conforms"] is False


def test_bind_pipeline_mit_mcp_record(tmp_path, monkeypatch):
    monkeypatch.setattr(mcp_memory_server, "SCOPES", {"tier2": tmp_path / "mcp"})
    out = cb.bind(ROOT / "connectors/react.md", _ctx(tmp_path))
    assert out["process"] == "pipeline.py" and out["executed"] is True
    assert out["result"]["ok"] is True
    assert out["recorded"]["via"] == "mcp" and (tmp_path / "mcp" / "binding-react.md").exists()


def test_bind_unbekannter_prozess(tmp_path):
    out = cb.bind(ROOT / "connectors/react.md", _ctx(tmp_path), registry={}, mcp_record=False)
    assert out["executed"] is False and out["recorded"] is None


def test_bind_all_17(tmp_path, monkeypatch):
    monkeypatch.setattr(mcp_memory_server, "SCOPES", {"tier2": tmp_path / "mcp"})
    outs = cb.bind_all(_ctx(tmp_path))
    assert len(outs) == 17
    assert all(o["executed"] for o in outs)
    assert {o["process"] for o in outs} == set(cb.PROCESS_REGISTRY)


def test_record_binding_fallback(tmp_path, monkeypatch):
    def _boom():
        raise RuntimeError("MCP down")

    monkeypatch.setattr(mcp_memory_server, "build_server", _boom)
    r = cb._record_binding({"name": "x", "process": "trust.py", "phase": "p"}, {"fallback_dir": str(tmp_path)})
    assert r["via"] == "local-fallback" and (tmp_path / "binding-x.md").exists()


def test_bind_liefert_integrations_modus(tmp_path, monkeypatch):
    """S3: ehrlicher Integrationsgrad (integriert vs. beispiel)."""
    monkeypatch.setattr(mcp_memory_server, "SCOPES", {"tier2": tmp_path / "m"})
    assert cb.bind(ROOT / "connectors/react.md", _ctx(tmp_path))["mode"] == "integriert"
    assert cb.bind(ROOT / "connectors/mars-seaa.md", _ctx(tmp_path))["mode"] == "beispiel"
