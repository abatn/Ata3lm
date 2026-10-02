"""Mandats-Formalisierung (data/memory/mandate.py) – EU Fidacy (Futurium) + AGENTS.md §9.

Flow: Mandate → Independent Decision → Execution Grant → Evidence.
Kernregel: Der Agent kann sein Mandat NIE erweitern (nur attenuieren) → Gate ask.
"""

import mandate


def _reg():
    r = mandate.MandateRegistry()
    m = r.issue(
        principal="Batnini",
        agent="knowledge-agent",
        actions={"read:repo", "write:ergebnisse"},
        resources={"data/memory", "ergebnisse"},
        amount_limit=10.0,
        max_uses=1000,
        valid_from=1000.0,
        valid_until=2000.0,
        approval_threshold=5.0,
        delegation_depth=1,
        mandate_id="m-root",
    )
    return r, m


def test_issue_get_revoke_und_digest():
    r, m = _reg()
    assert r.get("m-root") is m and m.principal == "Batnini"
    d0 = m.digest()
    revoked = r.revoke("m-root")
    assert revoked.revoked is True and r.get("m-root").revoked is True
    assert r.issue(
        principal="P",
        agent="a",
        actions={"x"},
        resources={"y"},
        amount_limit=1.0,
        max_uses=1,
        valid_from=0.0,
        valid_until=1.0,
        approval_threshold=1.0,
    ).mandate_id.startswith("mandate-")
    # digest reagiert auf Inhaltsänderung (nicht auf revoked, das ist nicht im Payload)
    assert d0 == m.digest()


def test_attenuate_verkleinert_erlaubt():
    r, m = _reg()
    child = r.attenuate(
        m,
        agent="child",
        actions={"read:repo"},
        amount_limit=5.0,
        max_uses=10,
        valid_until=1500.0,
        approval_threshold=2.0,
    )
    assert child.parent_id == "m-root" and child.delegation_depth == 0
    assert child.actions == {"read:repo"} and child.amount_limit == 5.0
    assert child.resources == m.resources  # unverändert = Teilmenge


def test_attenuate_erweiterung_wird_abgelehnt():
    r, m = _reg()
    for kwargs, msg in [
        ({"actions": {"read:repo", "admin:all"}}, "Aktionen"),
        ({"resources": {"secrets"}}, "Ressourcen"),
        ({"amount_limit": 99.0}, "amount_limit"),
        ({"max_uses": 9999}, "max_uses"),
        ({"valid_until": 9999.0}, "valid_until"),
        ({"approval_threshold": 99.0}, "approval_threshold"),
    ]:
        try:
            r.attenuate(m, agent="child", **kwargs)
            raise AssertionError("Erweiterung hätte fehlschlagen müssen")
        except mandate.MandateError as e:
            assert msg in str(e)


def test_attenuate_ohne_delegationsrecht():
    r, m = _reg()
    keine = r.issue(
        principal="P",
        agent="a",
        actions={"x"},
        resources={"y"},
        amount_limit=1.0,
        max_uses=1,
        valid_from=0.0,
        valid_until=1.0,
        approval_threshold=1.0,
        delegation_depth=0,
    )
    try:
        r.attenuate(keine, agent="child")
        raise AssertionError("muss fehlschlagen")
    except mandate.MandateError as e:
        assert "Delegation" in str(e)


def test_expand_des_agenten_ist_immer_ask():
    r, m = _reg()
    out = r.expand(m, agent="knowledge-agent", amount_limit=999.0)
    assert out["allowed"] is False and out["gate"] == "ask"
    assert "nicht erweitern" in out["reason"]


def test_is_active():
    r, m = _reg()
    assert mandate.is_active(m, 1500.0) is True
    assert mandate.is_active(m, 999.0) is False  # vor Gültigkeit
    assert mandate.is_active(m, 2001.0) is False  # nach Gültigkeit
    assert mandate.is_active(r.revoke("m-root"), 1500.0) is False


def test_assess_alle_entscheidungen():
    r, m = _reg()
    ok = mandate.assess(m, action="read:repo", resource="data/memory", amount=1.0, now=1500.0)
    assert ok["decision"] == "ALLOW"
    review = mandate.assess(m, action="read:repo", resource="data/memory", amount=5.0, now=1500.0)
    assert review["decision"] == "REVIEW"
    assert mandate.assess(m, action="read:repo", resource="data/memory", amount=11.0, now=1500.0)["decision"] == "DENY"
    assert mandate.assess(m, action="admin", resource="data/memory", amount=1.0, now=1500.0)["decision"] == "DENY"
    assert mandate.assess(m, action="read:repo", resource="secrets", amount=1.0, now=1500.0)["decision"] == "DENY"
    assert mandate.assess(m, action="read:repo", resource="data/memory", amount=1.0, now=500.0)["decision"] == "DENY"
    assert (
        mandate.assess(r.revoke("m-root"), action="read:repo", resource="data/memory", amount=1.0, now=1500.0)[
            "decision"
        ]
        == "DENY"
    )


def test_grant_und_redeem():
    r, m = _reg()
    allow = mandate.assess(m, action="read:repo", resource="data/memory", amount=1.0, now=1500.0)
    review = mandate.assess(m, action="read:repo", resource="data/memory", amount=5.0, now=1500.0)
    assert mandate.issue_grant(review, now=1500.0) is None  # nur ALLOW
    g = mandate.issue_grant(allow, now=1500.0, ttl_seconds=60.0)
    assert g["used"] is False
    assert mandate.redeem(g, now=1510.0)["ok"] is True
    assert mandate.redeem(g, now=1511.0)["reason"] == "grant_replayed"
    g2 = mandate.issue_grant(allow, now=1500.0, ttl_seconds=10.0)
    assert mandate.redeem(g2, now=1600.0)["reason"] == "grant_expired"


def test_evidence_hash_kette():
    e1 = mandate.evidence({"decision": "ALLOW"}, prev_hash=None)
    e2 = mandate.evidence({"decision": "DENY"}, prev_hash=e1["hash"])
    assert e1["prev"] is None and e2["prev"] == e1["hash"]
    assert e1["hash"] != e2["hash"] and len(e1["hash"]) == 64
