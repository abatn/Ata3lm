"""MCP-Memory-Server (data/memory/mcp_memory_server.py) – 5 Tools + Tri-Color Trust.

Echte Verifikation (Guardrail 7): ROOT/Scopes auf tmp_path; `build_server` mit dem
**echten** mcp-SDK (skip, falls nicht installiert) – kein Fake.
"""

import json
import os

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


def test_build_server_mit_echtem_mcp_sdk():
    """Reales offizielles mcp-SDK (Python >=3.10); sonst skip (Guardrail 7: kein Fake)."""
    pytest.importorskip("mcp")
    server = m.build_server()
    tools = set(server._tool_manager._tools.keys())
    assert {"memory.read", "memory.write", "memory.search", "memory.consolidate", "memory.link"} <= tools


def test_write_minimiert_pii_vor_store(tmp_path, monkeypatch):
    """§9.2a: PII wird VOR dem Store entfernt (F2)."""
    scopes = _setup(tmp_path, monkeypatch)
    r = m.write("structured", "pii.md", "Contact audit-person@example.test bitte melden", trust="green")
    assert r["ok"] is True
    text = (scopes["structured"] / "pii.md").read_text(encoding="utf-8")
    assert "audit-person@example.test" not in text and "Contact" in text


def test_green_ueberschreibt_blue_nicht(tmp_path, monkeypatch):
    """§9.2c/§10.7: green (Vorschlag) darf bestätigtes blue NICHT überschreiben (F1)."""
    scopes = _setup(tmp_path, monkeypatch)
    assert m.write("structured", "cur.md", "Bestätigt", trust="blue")["ok"] is True
    r = m.write("structured", "cur.md", "Vorschlag", trust="green")
    assert r["ok"] is False and r["status"] == "rejected"
    assert (scopes["structured"] / "cur.md").read_text(encoding="utf-8") == "Bestätigt"


def test_tier1_nur_blue(tmp_path, monkeypatch):
    """§9.2c/§9.3: kuratiertes tier1 nur mit trust=blue."""
    scopes = _setup(tmp_path, monkeypatch)
    r = m.write("tier1", "curated.md", "Vorschlag", trust="green")
    assert r["ok"] is False and r["status"] == "rejected"
    assert not (scopes["tier1"] / "curated.md").exists()
    assert m.write("tier1", "curated.md", "Kuratiert", trust="blue")["ok"] is True


def test_trust_db_kaputt_wird_ignoriert(tmp_path, monkeypatch):
    scopes = _setup(tmp_path, monkeypatch)
    (scopes["tier2"] / "mcp-trust.json").write_text("{kein json", encoding="utf-8")
    assert m.write("structured", "x.md", "y", trust="green")["ok"] is True


def test_write_fail_closed_ohne_tier2(tmp_path, monkeypatch):
    """§9.2c/§9.3: ohne Trust-Metadaten KEIN Write (fail-closed, nie fail-open)."""
    monkeypatch.setattr(m, "SCOPES", {"structured": tmp_path / "structured"})
    r = m.write("structured", "x.md", "y", trust="green")
    assert r["ok"] is False and r["status"] == "rejected"
    assert not (tmp_path / "structured" / "x.md").exists()


def test_n1_alias_key_teilt_trust_key(tmp_path, monkeypatch):
    """N1 §9.2c: Alias-Key (`./`) muss denselben Trust-Key treffen wie kanonisch."""
    scopes = _setup(tmp_path, monkeypatch)
    assert m.write("structured", "cur.md", "Bestätigt", trust="blue")["ok"] is True
    r = m.write("structured", "./cur.md", "Vorschlag", trust="green")
    assert r["ok"] is False and r["status"] == "rejected"  # Blue-Schutz greift über Alias
    assert (scopes["structured"] / "cur.md").read_text(encoding="utf-8") == "Bestätigt"
    assert list(m._load_trust_db(m._trust_db_path())) == ["structured/cur.md"]  # Scope+kanonischer Key


def test_n1_green_auf_green_erlaubt(tmp_path, monkeypatch):
    """N1/N2: bekannter green-Key (Datei existiert) darf erneut geschrieben werden."""
    scopes = _setup(tmp_path, monkeypatch)
    assert m.write("structured", "x.md", "v1", trust="green")["ok"] is True
    r = m.write("structured", "x.md", "v2", trust="green")
    assert r["ok"] is True and (scopes["structured"] / "x.md").read_text(encoding="utf-8") == "v2"


def test_n2_fail_closed_existierende_datei_unbekannter_trust(tmp_path, monkeypatch):
    """N2 §9.2c/§9.3: existierende Zieldatei + unbekannter Trust -> fail-closed."""
    scopes = _setup(tmp_path, monkeypatch)
    assert m.write("structured", "keep.md", "Bestätigt", trust="blue")["ok"] is True
    db = scopes["tier2"] / "mcp-trust.json"
    db.write_text("{kaputt", encoding="utf-8")  # beschädigte Trust-DB
    r = m.write("structured", "keep.md", "Clobber", trust="green")
    assert r["ok"] is False and r["status"] == "rejected"
    assert (scopes["structured"] / "keep.md").read_text(encoding="utf-8") == "Bestätigt"
    db.unlink()  # fehlende Trust-DB ebenso fail-closed
    r2 = m.write("structured", "keep.md", "Clobber2", trust="green")
    assert r2["ok"] is False and r2["status"] == "rejected"
    assert (scopes["structured"] / "keep.md").read_text(encoding="utf-8") == "Bestätigt"


def test_write_lock_konflikt_wird_rejected(tmp_path, monkeypatch):
    """K5/K2: hält ein paralleler Schreiber den Lock, wird der Write abgelehnt (kein Clobber)."""
    scopes = _setup(tmp_path, monkeypatch)
    (scopes["structured"] / "neu.md.lock").write_text("", encoding="utf-8")  # paralleler Schreiber
    r = m.write("structured", "neu.md", "x", trust="green")
    assert r["ok"] is False and r["status"] == "rejected"
    assert not (scopes["structured"] / "neu.md").exists()


# --- R11/R12/R13/R14/R15: Scope + kanonischer Trust-Key, Symlink-Schranke, Typ-Guard ---


def test_r13_scope_trennung_gleicher_key(tmp_path, monkeypatch):
    """R13: Blue `structured/cur.md` blockiert Green `tier3/cur.md` NICHT (Scope im Key)."""
    scopes = _setup(tmp_path, monkeypatch)
    assert m.write("structured", "cur.md", "Bestätigt", trust="blue")["ok"] is True
    r = m.write("tier3", "cur.md", "Vorschlag", trust="green")
    assert r["ok"] is True and r["status"] == "proposed"
    assert (scopes["structured"] / "cur.md").read_text(encoding="utf-8") == "Bestätigt"
    assert (scopes["tier3"] / "cur.md").read_text(encoding="utf-8") == "Vorschlag"
    db = m._load_trust_db(m._trust_db_path())
    assert db["structured/cur.md"] == "blue" and db["tier3/cur.md"] == "green"


def test_r11_db_verlust_kein_cross_scope_repair(tmp_path, monkeypatch):
    """R11: nach Metadatenverlust „repariert" Green in Tier3 NICHT das Blue in Structured."""
    scopes = _setup(tmp_path, monkeypatch)
    assert m.write("structured", "cur.md", "BLUE", trust="blue")["ok"] is True
    (scopes["tier2"] / "mcp-trust.json").write_text("{}", encoding="utf-8")  # DB-Verlust
    assert m.write("tier3", "cur.md", "GREEN", trust="green")["ok"] is True
    r = m.write("structured", "cur.md", "CLOBBER", trust="green")
    assert r["ok"] is False and r["status"] == "rejected"
    assert (scopes["structured"] / "cur.md").read_text(encoding="utf-8") == "BLUE"


def test_r14_altformat_scope_qualified_akzeptiert(tmp_path, monkeypatch):
    """R14: alte Trust-DB (`structured/cur.md`) wird gelesen (kein Migrationszwang)."""
    scopes = _setup(tmp_path, monkeypatch)
    (scopes["structured"] / "cur.md").write_text("Bestätigt", encoding="utf-8")
    (scopes["tier2"] / "mcp-trust.json").write_text(json.dumps({"structured/cur.md": "blue"}), encoding="utf-8")
    green = m.write("structured", "cur.md", "Vorschlag", trust="green")
    assert green["ok"] is False and green["status"] == "rejected"  # Blue-Schutz aus Altformat
    blue = m.write("structured", "cur.md", "Neu bestätigt", trust="blue")
    assert blue["ok"] is True and (scopes["structured"] / "cur.md").read_text(encoding="utf-8") == "Neu bestätigt"


def test_r12_symlink_ausserhalb_scope_rejected(tmp_path, monkeypatch):
    """R12 §9.2c: dangling/externer Symlink darf den Scope nicht verlassen."""
    scopes = _setup(tmp_path, monkeypatch)
    outside = tmp_path / "OUTSIDE.md"
    os.symlink(outside, scopes["structured"] / "link.md")
    with pytest.raises(ValueError):
        m.write("structured", "link.md", "EXTERN", trust="green")
    assert not outside.exists()  # kein externer Write


def test_r12_symlink_im_scope_erlaubt(tmp_path, monkeypatch):
    """R12: Symlink, dessen Ziel IM Scope liegt, ist zulässig."""
    scopes = _setup(tmp_path, monkeypatch)
    inside = scopes["structured"] / "ziel.md"
    inside.write_text("Ziel", encoding="utf-8")
    os.symlink(inside, scopes["structured"] / "kurz.md")
    (scopes["tier2"] / "mcp-trust.json").write_text(json.dumps({"structured/kurz.md": "green"}), encoding="utf-8")
    r = m.write("structured", "kurz.md", "Neu", trust="green")
    assert r["ok"] is True and inside.read_text(encoding="utf-8") == "Neu"


def test_r15_metadaten_falscher_typ_rejected(tmp_path, monkeypatch):
    """R15 §9.2c: JSON `[]` als Trust-DB → kontrolliert rejected, kein AttributeError."""
    scopes = _setup(tmp_path, monkeypatch)
    (scopes["structured"] / "cur.md").write_text("Bestätigt", encoding="utf-8")
    (scopes["tier2"] / "mcp-trust.json").write_text("[]", encoding="utf-8")
    r = m.write("structured", "cur.md", "Clobber", trust="green")
    assert r["ok"] is False and r["status"] == "rejected"
    assert (scopes["structured"] / "cur.md").read_text(encoding="utf-8") == "Bestätigt"
