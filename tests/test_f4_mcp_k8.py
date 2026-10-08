"""F4 (Audit 75095d5): MCP-`structured`-Write darf den K8-Kopf nicht beschädigen.

SOLL (Quelle): MCP-Spec + TMA-NM (arXiv:2606.24322 „write-time origin binding"):
`Evidence: sha256:…` muss dem **Body-Hash** entsprechen; Kopf und Body getrennt.
Ursache war: der **gesamte** Inhalt (Body + Kopf) lief durch `PIIFilter.minimize`,
wodurch die Ziffern aus `sha256`/Datum im Kopf verschwanden (F4). Fix: der K8-Kopf
wird erst **nach** der PII-Sanitisierung aus dem realen PROV-O-Record erzeugt.

Echte Verifikation (Guardrail 7): realer Store-Pfad (`m.write`) **und** REALER
stdio-MCP-Server (kein Fake).
"""

import re
import sys
from pathlib import Path

import mcp_live_binding as mlb
import mcp_memory_server as m
import provenance
import pytest
import write_gateway

REPO = Path(__file__).resolve().parents[1]


def _setup(tmp_path, monkeypatch):
    scopes = {s: tmp_path / s for s in ["tier1", "tier2", "tier3", "structured", "connectors", "skills"]}
    for d in scopes.values():
        d.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(m, "SCOPES", scopes)
    monkeypatch.setattr(m, "ROOT", tmp_path)
    monkeypatch.setattr(m, "_LINKS", tmp_path / "tier2" / "mcp-links.jsonl")
    return scopes


def _split_k8(doc: str):
    """K8-Kopf und Body müssen durch genau eine Leerzeile (`\\n\\n`) getrennt sein."""
    head, sep, body = doc.partition("\n\n")
    assert sep == "\n\n", "K8-Kopf und Body sind nicht durch eine Leerzeile getrennt (F4)"
    return head, body


def test_mcp_k8_evidence_hash_matches_stored_body(tmp_path, monkeypatch):
    """Repro F4 (realer Store-Pfad): `Evidence: sha256:` == `content_hash(body)`."""
    scopes = _setup(tmp_path, monkeypatch)
    body = "Fakt leak@example.test und Nummer 123456789012345"
    r = m.write("structured", "k8.md", body, trust="green")
    assert r["ok"] is True
    doc = (scopes["structured"] / "k8.md").read_text(encoding="utf-8")
    head, stored_body = _split_k8(doc)
    m_head = re.search(r"sha256:([0-9a-f]{64})", head)
    assert m_head, "Evidence-sha256 fehlt/ist beschädigt (F4)"
    assert m_head.group(1) == provenance.content_hash(stored_body)
    # PII bleibt entfernt (§9.2a) – der Body ist Teil des gespeicherten Inhalts.
    assert "leak@example.test" not in stored_body and "123456789012345" not in stored_body
    # `_strip_k8_header` greift weiterhin und liefert exakt den Body (K8/N6).
    assert write_gateway._strip_k8_header(doc) == stored_body


def test_mcp_k8_datum_im_kopf_unangetastet(tmp_path, monkeypatch):
    """F4-Ursache: der PII-Filter darf die Ziffern des Datums im Kopf NICHT entfernen."""
    scopes = _setup(tmp_path, monkeypatch)
    assert m.write("structured", "zeit.md", "harmloser Fakt", trust="green")["ok"] is True
    head, _body = _split_k8((scopes["structured"] / "zeit.md").read_text(encoding="utf-8"))
    assert re.search(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}", head), "Datum im Kopf beschädigt (F4)"
    assert "approval:none" in head


def test_mcp_k8_non_structured_bleibt_body_only(tmp_path, monkeypatch):
    """Nicht-`structured`-Scopes bleiben unverändert Body-only (kein K8-Kopf)."""
    scopes = _setup(tmp_path, monkeypatch)
    assert m.write("tier3", "plain.md", "Nur Body", trust="green")["ok"] is True
    assert (scopes["tier3"] / "plain.md").read_text(encoding="utf-8") == "Nur Body"


def test_store_file_structured_mit_refs(tmp_path):
    """`store_file(structured=True, …)` erzeugt den Kopf aus den übergebenen Refs."""
    target = tmp_path / "structured" / "refs.md"
    body = "Fakt mit Nummer 123456789012345"
    res = write_gateway.store_file(
        target=target,
        content=body,
        now=1.0,
        origin="user",
        verified=True,
        structured=True,
        ontology_ref="ontologie:ref",
        source_ref="https://example.test/quelle",
    )
    assert res["ok"] is True
    doc = target.read_text(encoding="utf-8")
    head, stored_body = _split_k8(doc)
    assert "ontologie:ref" in head and "https://example.test/quelle" in head
    m_head = re.search(r"sha256:([0-9a-f]{64})", head)
    assert m_head and m_head.group(1) == provenance.content_hash(stored_body)
    assert "123456789012345" not in stored_body


def test_mcp_k8_stdio_evidence_hash_matches(tmp_path):
    """Echter stdio-MCP-Server (MCP-Spec, Guardrail 7): Kopf-Hash == Body-Hash."""
    pytest.importorskip("mcp")
    root = tmp_path / "root"
    for rel in ("knowledge/structured", "data/memory/tier2-index", "data/memory/tier3-working"):
        (root / rel).mkdir(parents=True, exist_ok=True)
    servers = {
        "memory": {
            "command": [sys.executable, str(REPO / "data/memory/mcp_memory_server.py")],
            "env": {"MCP_MEMORY_ROOT": str(root)},
        }
    }
    out = mlb.call_tool_live(
        "memory",
        "memory.write",
        {"scope": "structured", "key": "stdio.md", "content": "Fakt 123456789012345", "trust": "green"},
        servers=servers,
        timeout=60.0,
    )
    assert out["ok"] is True and out.get("transport_ok") is True
    doc = (root / "knowledge/structured/stdio.md").read_text(encoding="utf-8")
    head, stored_body = _split_k8(doc)
    m_head = re.search(r"sha256:([0-9a-f]{64})", head)
    assert m_head and m_head.group(1) == provenance.content_hash(stored_body)
