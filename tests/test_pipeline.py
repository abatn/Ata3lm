"""Element-Pipeline (data/memory/pipeline.py) – verbindet die Prozesse.

Offline: Scopes auf tmp_path, FWR-Klassifikation injiziert.
"""

import mandate
import pipeline


def _mandate(allow=True):
    r = mandate.MandateRegistry()
    return r.issue(
        principal="Batnini",
        agent="knowledge-agent",
        actions={"write:memory"} if allow else {"read:repo"},
        resources={"data/memory"},
        amount_limit=100.0,
        max_uses=1000,
        valid_from=0.0,
        valid_until=10**12,
        approval_threshold=50.0,
    )


def _cls(kind):
    return lambda q, f, c: {"class": kind}


def _dirs(tmp_path):
    return tmp_path / "structured", tmp_path / "tier3"


def test_mandat_deny_blockiert(tmp_path):
    s, t3 = _dirs(tmp_path)
    out = pipeline.route_and_store(
        question="Q",
        fact="F",
        correct="C",
        classify_fn=_cls("write-new"),
        mandate_obj=_mandate(allow=False),
        now=1.0,
        structured_dir=s,
        tier3_dir=t3,
    )
    assert out["ok"] is False and out["gate"] == "deny"
    assert not s.exists()  # kein Write


def test_non_write_speichert_nichts(tmp_path):
    s, t3 = _dirs(tmp_path)
    out = pipeline.route_and_store(
        question="Q",
        fact="F",
        correct="C",
        classify_fn=_cls("non-write"),
        mandate_obj=_mandate(),
        now=1.0,
        structured_dir=s,
        tier3_dir=t3,
    )
    assert out["action"] == "none" and out["gate"] == "allow"
    assert ("trust", "keine PII") not in out["steps"]  # non-write bricht vorher ab


def test_write_new_schreibt_structured_und_tier3(tmp_path):
    s, t3 = _dirs(tmp_path)
    out = pipeline.route_and_store(
        question="Was ist 2+2",
        fact="2+2 ergibt 4",
        correct="4",
        classify_fn=_cls("write-new"),
        mandate_obj=_mandate(),
        now=1.0,
        structured_dir=s,
        tier3_dir=t3,
    )
    assert out["ok"] and out["action"] == "write-new"
    assert (s / "was-ist-2-2.md").exists() and (t3 / "was-ist-2-2.md").exists()
    assert out["superseded"] is None


def test_write_update_supersediert_bitemporal(tmp_path):
    s, t3 = _dirs(tmp_path)
    out = pipeline.route_and_store(
        question="Hauptstadt X",
        fact="Y ist Hauptstadt",
        correct="Y",
        classify_fn=_cls("write-update"),
        mandate_obj=_mandate(),
        now=1.0,
        structured_dir=s,
        tier3_dir=t3,
    )
    assert out["action"] == "write-update" and out["superseded"] == 0
    assert (s / "hauptstadt-x.md").exists() and not (t3 / "hauptstadt-x.md").exists()


def test_trust_entfernt_pii_vor_store(tmp_path):
    s, t3 = _dirs(tmp_path)
    out = pipeline.route_and_store(
        question="Kontakt",
        fact="Mail max@example.com anrufen",
        correct="x",
        classify_fn=_cls("write-new"),
        mandate_obj=_mandate(),
        now=1.0,
        structured_dir=s,
        tier3_dir=t3,
    )
    assert ("trust", "PII entfernt") in out["steps"]
    assert "max@example.com" not in (s / "kontakt.md").read_text(encoding="utf-8")


def test_self_update_ohne_approval_ist_ask(tmp_path):
    s, t3 = _dirs(tmp_path)
    out = pipeline.route_and_store(
        question="Gesetz §X",
        fact="neu",
        correct="c",
        classify_fn=_cls("write-update"),
        mandate_obj=_mandate(),
        now=1.0,
        structured_dir=s,
        tier3_dir=t3,
        self_update=True,
        approvers=["Batnini"],
    )
    assert out["ok"] is False and out["gate"] == "ask" and out["approval"] == "first_approved"


def test_self_update_mit_zwei_personen_approved(tmp_path):
    s, t3 = _dirs(tmp_path)
    out = pipeline.route_and_store(
        question="Gesetz §X",
        fact="neu",
        correct="c",
        classify_fn=_cls("write-update"),
        mandate_obj=_mandate(),
        now=1.0,
        structured_dir=s,
        tier3_dir=t3,
        self_update=True,
        approvers=["Batnini", "Verifier2"],
    )
    assert out["ok"] is True and ("approval", "approved") in out["steps"]


def test_drift_gate_ask_bei_abweichung(tmp_path):
    s, t3 = _dirs(tmp_path)
    import bias_monitor

    drift = bias_monitor.BiasDriftMonitor(baseline={"a": 1.0}, tau=0.01)
    out = pipeline.route_and_store(
        question="Q",
        fact="F",
        correct="C",
        classify_fn=_cls("write-new"),
        mandate_obj=_mandate(),
        now=1.0,
        structured_dir=s,
        tier3_dir=t3,
        drift=drift,
    )
    assert out["gate"] == "ask" and any(s0[0] == "drift" for s0 in out["steps"])


def test_drift_gate_ok_bei_stabilitaet(tmp_path):
    s, t3 = _dirs(tmp_path)
    import bias_monitor

    drift = bias_monitor.BiasDriftMonitor(baseline={"non-write": 0.5, "write": 0.5}, tau=0.5)
    out = pipeline.route_and_store(
        question="Q",
        fact="F",
        correct="C",
        classify_fn=_cls("write-new"),
        mandate_obj=_mandate(),
        now=1.0,
        structured_dir=s,
        tier3_dir=t3,
        drift=drift,
    )
    assert out["gate"] == "ok"


def test_load_from_tier2(tmp_path):
    t2 = tmp_path / "tier2"
    t2.mkdir()
    (t2 / "hub-index.md").write_text("Hub A", encoding="utf-8")
    (t2 / "concept-index.md").write_text("Konzept B", encoding="utf-8")
    out = pipeline.load_from_tier2(t2, tmp_path / "tier3")
    assert out["n"] == 2 and (tmp_path / "tier3" / "hub-index.md").exists()


def test_drift_gate_funktion():
    """bias_monitor → alle: Drift-Gate als Pipeline-Funktion."""
    ok = pipeline.drift_gate({"a": 0.5, "b": 0.5}, {"a": 0.5, "b": 0.5}, tau=0.5)
    assert ok["gate"] == "ok"
    bad = pipeline.drift_gate({"a": 1.0, "b": 0.0}, {"a": 0.5, "b": 0.5}, tau=0.01)
    assert bad["gate"] == "ask" and bad["DI"] > 0.01
