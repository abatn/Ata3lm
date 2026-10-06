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
    assert out["action"] == "write-update" and out["superseded"]["old_found"] is False  # kein Vorgänger
    assert (s / "hauptstadt-x.md").exists() and not (t3 / "hauptstadt-x.md").exists()


def test_write_update_archiviert_alten_stand(tmp_path):
    """§10.7: bestehender Stand wird archiviert (nicht gelöscht) (S2)."""
    s, t3 = _dirs(tmp_path)
    s.mkdir(parents=True)
    (s / "hauptstadt-x.md").write_text("ALT", encoding="utf-8")
    out = pipeline.route_and_store(
        question="Hauptstadt X",
        fact="NEU",
        correct="NEU",
        classify_fn=_cls("write-update"),
        mandate_obj=_mandate(),
        now=5.0,
        structured_dir=s,
        tier3_dir=t3,
    )
    assert out["superseded"]["old_found"] is True
    archived = list(s.glob("hauptstadt-x.superseded-5-*.md"))
    assert len(archived) == 1 and archived[0].read_text(encoding="utf-8") == "ALT"
    assert (s / "hauptstadt-x.md").read_text(encoding="utf-8") == "NEU"


def test_n3_update_archiv_kollision_same_second(tmp_path):
    """N3 §10.7: zwei Updates in derselben Sekunde -> zwei Archive, kein Verlust."""
    s, t3 = _dirs(tmp_path)
    s.mkdir(parents=True)
    (s / "alpha.md").write_text("ORIGINAL", encoding="utf-8")
    common = dict(question="Alpha", correct="x", mandate_obj=_mandate(), now=100.0, structured_dir=s, tier3_dir=t3)
    pipeline.route_and_store(fact="UPDATE-ONE", classify_fn=_cls("write-update"), **common)
    pipeline.route_and_store(fact="UPDATE-TWO", classify_fn=_cls("write-update"), **common)
    archives = list(s.glob("alpha.superseded-*.md"))
    assert len(archives) == 2  # kein Überschreiben des ersten Archivs
    assert {p.read_text(encoding="utf-8") for p in archives} == {"ORIGINAL", "UPDATE-ONE"}
    assert (s / "alpha.md").read_text(encoding="utf-8") == "UPDATE-TWO"


def test_n4_write_update_aktualisiert_tier3(tmp_path):
    """N4 §10.7: write-update darf die Tier3-Arbeitskopie nicht auf dem alten Fakt belassen."""
    s, t3 = _dirs(tmp_path)
    pipeline.route_and_store(
        question="Hauptstadt X",
        fact="ALT",
        correct="ALT",
        classify_fn=_cls("write-new"),
        mandate_obj=_mandate(),
        now=1.0,
        structured_dir=s,
        tier3_dir=t3,
    )
    assert (t3 / "hauptstadt-x.md").read_text(encoding="utf-8") == "ALT"
    out = pipeline.route_and_store(
        question="Hauptstadt X",
        fact="NEU",
        correct="NEU",
        classify_fn=_cls("write-update"),
        mandate_obj=_mandate(),
        now=2.0,
        structured_dir=s,
        tier3_dir=t3,
    )
    assert (s / "hauptstadt-x.md").read_text(encoding="utf-8") == "NEU"
    assert (t3 / "hauptstadt-x.md").read_text(encoding="utf-8") == "NEU"  # nicht mehr veraltet
    assert str(t3 / "hauptstadt-x.md") in out["written"]


def test_n3_update_archiv_identischer_inhalt_kollision(tmp_path):
    """N3: identischer Altinhalt -> Hash-Kollision -> Suffix-Recheck, kein Verlust."""
    s, t3 = _dirs(tmp_path)
    s.mkdir(parents=True)
    (s / "alpha.md").write_text("SAME", encoding="utf-8")
    common = dict(question="Alpha", correct="x", mandate_obj=_mandate(), now=100.0, structured_dir=s, tier3_dir=t3)
    pipeline.route_and_store(fact="SAME", classify_fn=_cls("write-update"), **common)
    pipeline.route_and_store(fact="SAME", classify_fn=_cls("write-update"), **common)
    assert len(list(s.glob("alpha.superseded-*.md"))) == 2


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


def test_drift_gate_allow_bei_stabilitaet(tmp_path):
    s, t3 = _dirs(tmp_path)
    import bias_monitor

    drift = bias_monitor.BiasDriftMonitor(baseline={"write-new": 1.0}, tau=0.5)
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
    assert out["gate"] == "allow"  # K6/B5: Labelraum allow|ask|deny


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
    assert ok["gate"] == "allow"  # K6/B5: Labelraum allow|ask|deny
    bad = pipeline.drift_gate({"a": 1.0, "b": 0.0}, {"a": 0.5, "b": 0.5}, tau=0.01)
    assert bad["gate"] == "ask" and bad["DI"] > 0.01


def test_default_classify_verdrahtet_fwr(tmp_path, monkeypatch):
    """B) pipeline → fast_write_router fest verdrahtet (lazy import)."""
    import sys
    from types import SimpleNamespace

    fake = SimpleNamespace(classify=lambda q, f, c: {"class": "non-write"})
    monkeypatch.setitem(sys.modules, "fast_write_router", fake)
    s, t3 = _dirs(tmp_path)
    out = pipeline.route_and_store(
        question="Q",
        fact="F",
        correct="C",
        classify_fn=None,
        mandate_obj=_mandate(),
        now=1.0,
        structured_dir=s,
        tier3_dir=t3,
    )
    assert out["action"] == "none"  # Default-FWR wurde benutzt


def test_export_shared_nach_tier1(tmp_path):
    """C) shared_memory → tier1-base (SharedTier.dump)."""
    import shared_memory

    tier = shared_memory.SharedTier({"agentA": {"read": {"*"}, "write": {"*"}}}, {"agentA": 0.5})
    tier.write("agentA", "k", "v")
    path = pipeline.export_shared(tier, tmp_path / "tier1")
    assert (tmp_path / "tier1" / "shared_store.jsonl").exists()
    assert path.endswith("shared_store.jsonl")


def test_router_gate_ask_blockiert_write(tmp_path):
    """§10.4: Router-Gate ask -> KEIN Write vor Freigabe (S1)."""
    s, t3 = _dirs(tmp_path)
    out = pipeline.route_and_store(
        question="Q",
        fact="F",
        correct="C",
        classify_fn=lambda q, f, c: {"class": "write-new", "gate": "ask"},
        mandate_obj=_mandate(),
        now=1.0,
        structured_dir=s,
        tier3_dir=t3,
    )
    assert out["ok"] is False and out["gate"] == "ask"
    assert not s.exists()  # kein Write


def test_router_uncertain_blockiert_write(tmp_path):
    """§10.4: Router uncertain -> Human-Gate, KEIN Write (S1)."""
    s, t3 = _dirs(tmp_path)
    out = pipeline.route_and_store(
        question="Q",
        fact="F",
        correct="C",
        classify_fn=_cls("uncertain"),
        mandate_obj=_mandate(),
        now=1.0,
        structured_dir=s,
        tier3_dir=t3,
    )
    assert out["ok"] is False and out["gate"] == "ask"
    assert not s.exists()


def test_mandat_review_ist_ask_nicht_deny(tmp_path):
    """K6/B5: REVIEW -> ask (Human-Gate), nicht pauschal deny (Labelraum allow|ask|deny)."""
    s, t3 = _dirs(tmp_path)
    r = mandate.MandateRegistry()
    m = r.issue(
        principal="Batnini",
        agent="knowledge-agent",
        actions={"write:memory"},
        resources={"data/memory"},
        amount_limit=100.0,
        max_uses=1000,
        valid_from=0.0,
        valid_until=10**12,
        approval_threshold=0.0,  # amount=0.0 >= threshold -> REVIEW
    )
    out = pipeline.route_and_store(
        question="Q",
        fact="F",
        correct="C",
        classify_fn=_cls("write-new"),
        mandate_obj=m,
        now=1.0,
        structured_dir=s,
        tier3_dir=t3,
    )
    assert out["ok"] is False and out["gate"] == "ask"
    assert not s.exists()


def test_router_deny_wird_nicht_durch_self_update_umgangen(tmp_path):
    """K6/B5: `deny` darf nie durch – self_update umgeht keine fachliche Ablehnung."""
    s, t3 = _dirs(tmp_path)
    out = pipeline.route_and_store(
        question="Q",
        fact="F",
        correct="C",
        classify_fn=lambda q, f, c: {"class": "write-update", "gate": "deny"},
        mandate_obj=_mandate(),
        now=1.0,
        structured_dir=s,
        tier3_dir=t3,
        self_update=True,
        approvers=["Batnini", "Verifier2"],
    )
    assert out["ok"] is False and out["gate"] == "deny"
    assert not s.exists()  # keine Mutation
