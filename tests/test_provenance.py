"""K3: PROV-O-Provenienz je Fakt – Inhalt-Hash + Freigabe-Bindung (STOPP-Regel).

Quelle (Belegt): W3C PROV-O, Recommendation 30 April 2013, https://www.w3.org/TR/prov-o/
(verifiziert 2026-10-06, HTTP 200). Durchsetzung = Auftrag K3.
"""

import json

import provenance as prov
import pytest


def _approval(state="approved", approvers=("Batnini", "Verifier2"), diff_sha="abc123"):
    return {"state": state, "approvers": list(approvers), "diff_sha": diff_sha}


def _record(**kw):
    base = dict(
        fact="Version 2.",
        activity="write-new",
        agent="knowledge-agent",
        source="pipeline",
        now=100.0,
    )
    base.update(kw)
    return prov.build_record(**base)


# ---------------------------------------------------------------- content_hash
def test_content_hash_sha256_stabil():
    h = prov.content_hash("Version 2.")
    assert len(h) == 64 and h == prov.content_hash("Version 2.")
    assert h != prov.content_hash("Version 3.")


# ------------------------------------------------------------- ApprovalBinding
def test_approval_binding_as_dict():
    a = prov.ApprovalBinding(state="approved", approvers=("A", "B"), diff_sha="d1")
    assert a.as_dict() == {"state": "approved", "approvers": ["A", "B"], "diff_sha": "d1"}
    assert prov._valid_approval(a) is True


def test_valid_approval_nur_mit_zwei_unterschiedlichen_und_diff():
    assert prov._valid_approval(_approval()) is True
    assert prov._valid_approval(_approval(approvers=("A", "A"))) is False  # keine 2 distinkten (§9.3)
    assert prov._valid_approval(_approval(approvers=("A",))) is False
    assert prov._valid_approval(_approval(state="first_approved")) is False
    assert prov._valid_approval(_approval(diff_sha="")) is False
    assert prov._valid_approval(None) is False
    assert prov._valid_approval("approved") is False


# ------------------------------------------------------------------ build_record
def test_build_record_prov_o_kernfelder():
    r = _record()
    assert r["@context"]["prov"] == prov.PROV_NS
    e, a, ag = r["entity"], r["activity"], r["agent"]
    assert e["@type"] == "prov:Entity" and a["@type"] == "prov:Activity" and ag["@type"] == "prov:Agent"
    assert e["sha256"] == prov.content_hash("Version 2.")  # Inhalt gebunden
    assert e["prov:wasGeneratedBy"] == a["@id"]
    assert e["prov:wasAttributedTo"] == ag["@id"]
    assert r["source"] == "pipeline" and r["approval"] is None and r["require_approval"] is False


def test_build_record_revision_und_invalidierung():
    r = _record(
        fact="Paris (neu)",
        activity="write-update",
        derived_from="quelle:alt",
        revision_of="entity:alt",
        invalidated_at=50.0,
    )
    e = r["entity"]
    assert e["prov:wasDerivedFrom"] == "quelle:alt"
    assert e["prov:wasRevisionOf"] == "entity:alt"
    assert e["prov:invalidatedAtTime"].startswith("1970-01-01T00:00:50")


def test_build_record_stoppt_ohne_inhalt_hash():
    with pytest.raises(prov.ProvenanceError, match="Inhalt"):
        _record(fact="   ")


def test_build_record_stoppt_ohne_quelle_oder_agent():
    for kw in ({"activity": ""}, {"agent": ""}, {"source": ""}):
        with pytest.raises(prov.ProvenanceError, match="unvollständig"):
            _record(**kw)


def test_build_record_stoppt_ohne_freigabe_wenn_gefordert():
    with pytest.raises(prov.ProvenanceError, match="Freigabe nicht gebunden"):
        _record(require_approval=True)
    with pytest.raises(prov.ProvenanceError, match="Freigabe nicht gebunden"):
        _record(require_approval=True, approval=_approval(approvers=("Solo",)))
    r = _record(require_approval=True, approval=_approval())
    assert r["require_approval"] is True and r["approval"]["diff_sha"] == "abc123"


def test_build_record_freigabe_als_binding_objekt():
    r = _record(approval=prov.ApprovalBinding("approved", ("A", "B"), "d1"))
    assert r["approval"] == {"state": "approved", "approvers": ["A", "B"], "diff_sha": "d1"}


def test_build_record_freigabe_falscher_typ():
    with pytest.raises(prov.ProvenanceError, match="dict oder ApprovalBinding"):
        _record(approval="approved")


# ----------------------------------------------------------------- verify_record
def test_verify_record_ok_mit_und_ohne_fakt():
    r = _record()
    assert prov.verify_record(r, fact="Version 2.")["ok"] is True
    assert prov.verify_record(r)["ok"] is True  # nur Hash vorhanden


def test_verify_record_enthalt_manipuliert():
    r = _record()
    v = prov.verify_record(r, fact="Version 3.")
    assert v["ok"] is False and v["hash_ok"] is False and "Hash" in v["reason"]


def test_verify_record_struktur_unvollstaendig():
    for broken in ({}, {"entity": {}}, {"entity": {"@type": "prov:Entity"}}):
        v = prov.verify_record(broken)
        assert v["ok"] is False and "Struktur" in v["reason"]


def test_verify_record_freigabe_gefordert_und_fehlt():
    r = _record(require_approval=True, approval=_approval())
    assert prov.verify_record(r)["approval_ok"] is True
    r2 = dict(r, approval=None)
    v = prov.verify_record(r2)
    assert v["ok"] is False and v["approval_ok"] is False and "Freigabe" in v["reason"]
    r3 = _record(approval=_approval(approvers=("Solo",)))  # ungültige Bindung
    assert prov.verify_record(r3)["ok"] is False


# ----------------------------------------------------------------- append_record
def test_append_record_jsonl(tmp_path):
    p = tmp_path / "sub" / "prov.jsonl"
    r1 = _record()
    r2 = _record(fact="Anderer Fakt", now=200.0)
    assert prov.append_record(p, r1) == str(p)
    prov.append_record(p, r2)
    lines = [json.loads(line) for line in p.read_text(encoding="utf-8").splitlines()]
    assert len(lines) == 2 and lines[0]["entity"]["sha256"] == r1["entity"]["sha256"]


def test_append_record_default_pfad(tmp_path, monkeypatch):
    monkeypatch.setattr(prov, "DEFAULT_LOG", tmp_path / "default.jsonl")
    assert prov.append_record(None, _record()) == str(tmp_path / "default.jsonl")
    assert (tmp_path / "default.jsonl").exists()
