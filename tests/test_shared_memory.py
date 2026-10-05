"""Shared Memory Tier (data/memory/shared/shared_memory.py) – ACL · Trust · Supersede."""

import shared_memory as sm


def _tier():
    acl = {a: {"read": {"*"}, "write": {"*"}} for a in ("agentA", "agentB", "agentC")}
    return sm.SharedTier(acl, {"agentA": 0.5, "agentB": 0.9, "agentC": 0.3}, {"config.mode": {"fast", "safe"}})


def test_acl_blockiert_schreiben_und_lesen():
    t = sm.SharedTier({"agentA": {"read": {"x"}, "write": {"x"}}}, {"agentA": 0.5})
    assert t.write("agentB", "x", "v")["ok"] is False
    assert "kein Schreibrecht" in t.write("agentB", "x", "v")["reason"]
    assert t.read("agentB", "x")["ok"] is False
    assert "kein Leserecht" in t.read("agentB", "x")["reason"]


def test_leerer_wert_und_schema_verstoss():
    t = _tier()
    assert t.write("agentA", "solver.current_version", "  ")["reason"] == "leerer Wert"
    r = t.write("agentA", "config.mode", "turbo")
    assert r["ok"] is False and "nicht erlaubt" in r["reason"]
    assert t.write("agentA", "config.mode", "fast")["ok"] is True


def test_trust_entscheidet_konflikt():
    t = _tier()
    assert t.write("agentA", "k", "v1")["outcome"] == "confirmed"
    assert t.write("agentA", "k", "v1")["outcome"] == "confirmed"  # gleicher Wert
    r = t.write("agentB", "k", "v2")  # 0.9 > 0.5
    assert r["outcome"] == "superseded_old" and r["conflict"] is True
    assert t.entries["k"].value == "v2"
    r = t.write("agentC", "k", "v3")  # 0.3 < 0.9
    assert r["outcome"] == "superseded_new"
    assert t.entries["k"].value == "v2"  # unterlegen, behalten
    t.trust["agentA"] = 0.9
    assert t.write("agentA", "k", "v4")["outcome"] == "contested"  # Gleichstand
    assert t.history[-1].status == "contested"


def test_gleicher_wert_senkt_trust_nicht():
    """§10.7/S4: gleicher Wert + niederer Trust darf den gespeicherten Trust NICHT senken."""
    t = _tier()
    assert t.write("agentB", "k", "v")["outcome"] == "confirmed"  # trust 0.9
    r = t.write("agentC", "k", "v")  # gleicher Wert, trust 0.3
    assert r["outcome"] == "confirmed"
    assert t.entries["k"].trust == 0.9  # Incumbent-Trust bleibt


def test_gleicher_wert_hoeherer_trust_ersetzt():
    """§10.7/S4: gleicher Wert + höherer Trust ersetzt (Incumbent wird angehoben)."""
    t = _tier()
    assert t.write("agentA", "k", "v")["outcome"] == "confirmed"  # trust 0.5
    r = t.write("agentB", "k", "v")  # gleicher Wert, trust 0.9 > 0.5
    assert r["outcome"] == "confirmed"
    assert t.entries["k"].trust == 0.9


def test_read_ohne_eintrag_und_mit_eintrag():
    t = _tier()
    assert t.read("agentA", "nie-geschrieben") == {
        "ok": True,
        "value": None,
        "version": None,
        "writer": None,
        "trust": None,
    }
    t.write("agentA", "k", "v")
    assert t.read("agentA", "k")["value"] == "v"


def test_sync_erkennt_konflikte():
    t = _tier()
    t.write("agentA", "k", "v1")
    t.write("agentB", "k", "v2")
    s = t.sync()
    assert s["keys"] == 1 and s["conflicts"][0]["key"] == "k"
    assert s["conflicts"][0]["values"] == ["v1", "v2"]
    assert s["conflicts"][0]["resolved_to"] == "v2"


def test_dump_schreibt_jsonl(tmp_path):
    t = _tier()
    t.write("agentA", "k", "v")
    p = t.dump(tmp_path / "sub" / "store.jsonl")
    assert p.exists() and p.read_text(encoding="utf-8").count("\n") == 1


def test_demo_laeuft(capsys):
    sm._demo()
    out = capsys.readouterr().out
    assert "Trust-Score entscheidet" in out and "Sync" in out


def test_sync_ohne_konflikt_bei_gleichem_wert():
    """Branch 142->140: gleicher Wert -> nur eine Ausprägung, kein Konflikt."""
    t = _tier()
    t.write("agentA", "k", "v1")
    t.write("agentA", "k", "v1")  # Historie wächst, Werte bleiben gleich
    s = t.sync()
    assert s["conflicts"] == [] and s["keys"] == 1
