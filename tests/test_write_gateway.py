"""K2: Einheitliches Write-Gateway – feste Reihenfolge, EIN Schreibpfad (Auftrag K2).

Abnahme (Bericht §4, Prio 2): jeder Schreibpfad hat Provenienz + Trust geprüft;
genau ein Gateway. STOPP: kein Aufrufer schreibt direkt; Freigabe + Drift VOR Mutation.
"""

import json

import mandate
import provenance
import write_gateway as wg


class _Drift:
    def __init__(self, gate):
        self.gate = gate
        self.seen = []

    def observe(self, distribution, step=None):
        self.seen.append(distribution)
        return {"DI": 0.5, "gate": self.gate, "flagged": self.gate != "allow"}


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


def _cls(kind, gate=None):
    d = {"class": kind}
    if gate is not None:
        d["gate"] = gate
    return lambda q, f, c: d


# --------------------------------------------------------------- store_file (Basis)
def test_store_file_schreibt_mit_provenienz(tmp_path):
    t = tmp_path / "s" / "fakt.md"
    r = wg.store_file(target=t, content="Version 2.", now=1.0, activity="write-new", origin="user", verified=True)
    assert r["ok"] is True and t.read_text(encoding="utf-8") == "Version 2."
    log = tmp_path / "s" / "provenance.jsonl"
    rec = json.loads(log.read_text(encoding="utf-8").splitlines()[0])
    assert rec["entity"]["sha256"] == provenance.content_hash("Version 2.")  # K3: Inhalt gebunden
    assert provenance.verify_record(rec, fact="Version 2.")["ok"] is True
    names = [s[0] for s in r["steps"]]
    assert names.index("mandate") < names.index("trust") < names.index("poisoning") < names.index("write")
    assert names.index("write") < names.index("provenance")


def test_store_file_mandat_deny_kein_write(tmp_path):
    r = wg.store_file(
        target=tmp_path / "f.md", content="x", now=1.0, mandate_obj=_mandate(allow=False), activity="write"
    )
    assert r["ok"] is False and r["gate"] == "deny"
    assert not (tmp_path / "f.md").exists()


def test_store_file_poisoning_untrusted_und_unverified(tmp_path):
    r = wg.store_file(target=tmp_path / "a.md", content="x", now=1.0, origin="web:untrusted", verified=True)
    assert r["ok"] is False and "Poisoning-Guard" in r["reason"] and not (tmp_path / "a.md").exists()
    r2 = wg.store_file(target=tmp_path / "b.md", content="x", now=1.0, origin="user", verified=False)
    assert r2["ok"] is False and not (tmp_path / "b.md").exists()


def test_store_file_pii_entfernt(tmp_path):
    t = tmp_path / "pii.md"
    r = wg.store_file(target=t, content="Mail max@example.com bitte", now=1.0, origin="user", verified=True)
    assert r["ok"] is True and "max@example.com" not in t.read_text(encoding="utf-8")
    assert ("trust", "PII entfernt") in r["steps"]


def test_store_file_drift_deny_kein_write(tmp_path):
    r = wg.store_file(target=tmp_path / "d.md", content="x", now=1.0, drift=_Drift("deny"), drift_label="write-new")
    assert r["ok"] is False and r["gate"] == "deny" and not (tmp_path / "d.md").exists()


def test_store_file_freigabe_zwei_personen(tmp_path):
    ok = wg.store_file(
        target=tmp_path / "ok.md",
        content="neu",
        now=1.0,
        require_approval=True,
        approvers=["Batnini", "Verifier2"],
        activity="self-update",
    )
    assert ok["ok"] is True and ok["provenance"]["approval"]["state"] == "approved"
    assert provenance.verify_record(ok["provenance"])["ok"] is True  # Freigabe gebunden (K3)
    bad = wg.store_file(target=tmp_path / "bad.md", content="neu", now=1.0, require_approval=True, approvers=["Solo"])
    assert bad["ok"] is False and bad["approval"] == "first_approved"
    assert not (tmp_path / "bad.md").exists()


def test_store_file_leerer_inhalt_stoppt_k3(tmp_path):
    r = wg.store_file(target=tmp_path / "e.md", content="   ", now=1.0, origin="user", verified=True)
    assert r["ok"] is False and "Provenienz (K3)" in r["reason"] and not (tmp_path / "e.md").exists()


def test_store_file_supersede_archiviert_alten_stand(tmp_path):
    t = tmp_path / "k.md"
    wg.store_file(target=t, content="ALT", now=5.0, origin="user", verified=True)
    r = wg.store_file(target=t, content="NEU", now=5.0, origin="user", verified=True)
    assert r["superseded"]["old_found"] is True
    archived = list(tmp_path.glob("k.superseded-5-*.md"))
    assert len(archived) == 1 and archived[0].read_text(encoding="utf-8") == "ALT"  # §10.7: nicht löschen
    assert t.read_text(encoding="utf-8") == "NEU"
    rec = r["provenance"]["entity"]
    assert rec["prov:wasRevisionOf"].startswith("entity:") and rec["prov:invalidatedAtTime"]


def test_store_file_also_write_und_shared(tmp_path):
    import shared_memory

    tier = shared_memory.SharedTier({"agentA": {"read": {"*"}, "write": {"*"}}}, {"agentA": 0.5})
    t = tmp_path / "x.md"
    r = wg.store_file(
        target=t,
        content="Fakt",
        now=1.0,
        origin="user",
        verified=True,
        also_write=[tmp_path / "kopie.md"],
        shared_tier=tier,
        shared_key="x",
        agent="agentA",
    )
    assert r["ok"] is True
    assert t.read_text(encoding="utf-8") == (tmp_path / "kopie.md").read_text(encoding="utf-8") == "Fakt"
    assert len(r["written"]) == 2
    assert r["shared"]["ok"] is True and ("shared", True) in r["steps"]


# ---------------------------------------------------------------- store (Wissens-Kette)
def test_store_non_write_ohne_und_mit_historie(tmp_path):
    s, t3 = tmp_path / "s", tmp_path / "t3"
    r = wg.store(
        question="Q",
        fact="F",
        correct="C",
        classify_fn=_cls("non-write"),
        now=1.0,
        structured_dir=s,
        tier3_dir=t3,
        mandate_obj=_mandate(),
    )
    assert r["ok"] is True and r["action"] == "non-write" and r["gate"] == "allow"
    assert not s.exists() and not t3.exists()  # non-write schreibt kein Memory
    wg.store(
        question="Q",
        fact="F",
        correct="C",
        classify_fn=_cls("non-write"),
        now=1.0,
        structured_dir=s,
        tier3_dir=t3,
        history_dir=tmp_path / "hist",
        mandate_obj=_mandate(),
    )
    hist = list((tmp_path / "hist").glob("*.non-write.jsonl"))
    assert len(hist) == 1 and json.loads(hist[0].read_text(encoding="utf-8"))["class"] == "non-write"
    assert not s.exists() and not t3.exists()


def test_store_write_new_layout(tmp_path):
    r = wg.store(
        question="Was ist 2+2",
        fact="2+2 ergibt 4",
        correct="4",
        classify_fn=_cls("write-new"),
        now=1.0,
        structured_dir=tmp_path / "s",
        tier3_dir=tmp_path / "t3",
        mandate_obj=_mandate(),
    )
    assert r["ok"] and r["action"] == "write-new" and r["gate"] == "allow"
    assert (tmp_path / "s" / "was-ist-2-2.md").exists() and (tmp_path / "t3" / "was-ist-2-2.md").exists()
    assert r["superseded"] is None and r["superseded_tier1"] is None
    assert (tmp_path / "t3" / "provenance.jsonl").exists()


def test_store_write_update_layout_mit_tier1_supersede(tmp_path):
    t1 = tmp_path / "tier1"
    t1.mkdir()
    (t1 / "hauptstadt-frankreich.md").write_text("Paris (alt)", encoding="utf-8")
    (tmp_path / "t3").mkdir()
    (tmp_path / "t3" / "hauptstadt-frankreich.md").write_text("alt-kopie", encoding="utf-8")
    r = wg.store(
        question="Hauptstadt Frankreich",
        fact="Paris (neu)",
        correct="Paris",
        classify_fn=_cls("write-update"),
        now=3.0,
        structured_dir=tmp_path / "s",
        tier3_dir=tmp_path / "t3",
        tier1_dir=t1,
        mandate_obj=_mandate(),
    )
    assert r["ok"] and r["action"] == "write-update"
    # structured: alter Stand archiviert (Supersede), tier3-Arbeitskopie aktualisiert (N4)
    assert r["superseded_structured"]["old_found"] is False  # structured war neu
    assert (tmp_path / "t3" / "hauptstadt-frankreich.md").read_text(encoding="utf-8") == "Paris (neu)"
    # tier1: Eintrag supersediert (§10.7: archiviert, nicht gelöscht)
    assert r["superseded_tier1"]["old_found"] is True
    archived = list(t1.glob("*.superseded-*.md"))
    assert len(archived) == 1 and archived[0].read_text(encoding="utf-8") == "Paris (alt)"
    assert (t1 / "hauptstadt-frankreich.md").read_text(encoding="utf-8") == "Paris (neu)"


def test_store_write_update_ohne_tier1_dir(tmp_path):
    r = wg.store(
        question="Q",
        fact="F",
        correct="C",
        classify_fn=_cls("write-update"),
        now=1.0,
        structured_dir=tmp_path / "s",
        tier3_dir=tmp_path / "t3",
        mandate_obj=_mandate(),
    )
    assert r["ok"] and r["superseded_tier1"] is None and r["superseded"]["old_found"] is False


def test_store_reihenfolge_der_gates_fix(tmp_path):
    """K2-Abnahme: Reihenfolge Mandat→FWR→Trust→Poisoning→Freigabe→Drift→Write→Shared→Provenienz."""
    import shared_memory

    tier = shared_memory.SharedTier({"knowledge-agent": {"read": {"*"}, "write": {"*"}}}, {"knowledge-agent": 0.5})
    drift = _Drift("allow")
    r = wg.store(
        question="Gesetz X",
        fact="neu",
        correct="c",
        classify_fn=_cls("write-update", gate="ask"),
        now=1.0,
        structured_dir=tmp_path / "s",
        tier3_dir=tmp_path / "t3",
        mandate_obj=_mandate(),
        self_update=True,
        approvers=["Batnini", "Verifier2"],
        drift=drift,
        shared_tier=tier,
    )
    assert r["ok"] is True
    names = [s[0] for s in r["steps"]]
    expected = ["mandate", "fwr", "trust", "poisoning", "approval", "drift", "write", "shared", "provenance"]
    assert names == expected
    assert drift.seen == [{"write-update": 1.0}]  # Drift sieht die echte Klasse


def test_store_router_deny_wird_nicht_durch_self_update_umgangen(tmp_path):
    r = wg.store(
        question="Q",
        fact="F",
        correct="C",
        classify_fn=_cls("write-update", gate="deny"),
        now=1.0,
        structured_dir=tmp_path / "s",
        tier3_dir=tmp_path / "t3",
        mandate_obj=_mandate(),
        self_update=True,
        approvers=["Batnini", "Verifier2"],
    )
    assert r["ok"] is False and r["gate"] == "deny" and not (tmp_path / "s").exists()


def test_store_poisoning_und_leerer_fakt_sperren(tmp_path):
    r = wg.store(
        question="Q",
        fact="F",
        correct="C",
        classify_fn=_cls("write-new"),
        now=1.0,
        structured_dir=tmp_path / "s",
        tier3_dir=tmp_path / "t3",
        mandate_obj=_mandate(),
        origin="web:untrusted",
    )
    assert r["ok"] is False and "Poisoning-Guard" in r["reason"]
    r2 = wg.store(
        question="Q",
        fact="  ",
        correct="C",
        classify_fn=_cls("write-new"),
        now=1.0,
        structured_dir=tmp_path / "s",
        tier3_dir=tmp_path / "t3",
        mandate_obj=_mandate(),
    )
    assert r2["ok"] is False and "Provenienz (K3)" in r2["reason"] and not (tmp_path / "s").exists()


def test_store_mandat_deny_keine_mutation(tmp_path):
    r = wg.store(
        question="Q",
        fact="F",
        correct="C",
        classify_fn=_cls("write-new"),
        now=1.0,
        structured_dir=tmp_path / "s",
        tier3_dir=tmp_path / "t3",
        mandate_obj=_mandate(allow=False),
    )
    assert r["ok"] is False and r["gate"] == "deny" and not (tmp_path / "s").exists()


def test_supersede_entry_direkt(tmp_path):
    t1 = tmp_path / "t1"
    r1 = wg.supersede_entry(t1, "k", "neu", 7.0)
    assert r1["old_found"] is False and r1["archived"] is None
    r2 = wg.supersede_entry(t1, "k", "neuer", 7.0)  # gleiche Sekunde -> Hash-Namen (K5)
    assert r2["old_found"] is True and r2["archived"].endswith(".md")
    log = [json.loads(line) for line in (t1 / "supersede.jsonl").read_text(encoding="utf-8").splitlines()]
    assert [rec["new"] for rec in log] == ["neu", "neuer"]


def test_default_mandate_erlaubt_write_memory():
    m = wg.default_mandate("tester")
    assert m.agent == "tester" and "write:memory" in m.actions and "data/memory" in m.resources


# ------------------------------------------------- K7/B3: Domain-Rejection fail-closed
def test_is_domain_rejection_und_domain_rejected_guard(tmp_path):
    """K7/B3: fachliches `rejected` ist kein Transportfehler und wird nie geschrieben."""
    assert wg.is_domain_rejection({"status": "rejected"}) is True
    assert wg.is_domain_rejection({"ok": False}) is False
    assert wg.is_domain_rejection("kein-dict") is False
    assert issubclass(wg.DomainRejection, Exception)
    r = wg.store_file(target=tmp_path / "d.md", content="x", now=1.0, domain_rejected=True)
    assert r["ok"] is False and r["gate"] == "deny" and not (tmp_path / "d.md").exists()


# ------------------------------------------------- K5: Lock/Concurrency-Pfade
def test_acquire_lock_stale_wird_ersetzt(tmp_path):
    import os
    import time

    lock = tmp_path / "x.lock"
    lock.write_text("", encoding="utf-8")
    alt = time.time() - (wg.LOCK_STALE_S + 10)
    os.utime(lock, (alt, alt))  # abgebrochener Schreiber -> stale
    fd = wg._acquire_lock(lock)
    assert isinstance(fd, int)  # Lock ersetzt und neu gehalten
    os.close(fd)
    lock.unlink(missing_ok=True)


def test_acquire_lock_frisch_ist_gehalten(tmp_path):
    lock = tmp_path / "y.lock"
    lock.write_text("", encoding="utf-8")  # frischer Lock -> gehalten
    assert wg._acquire_lock(lock) is None


def test_store_file_lock_konflikt_kein_write(tmp_path):
    t = tmp_path / "s" / "fakt.md"
    t.parent.mkdir(parents=True, exist_ok=True)
    (tmp_path / "s" / "fakt.md.lock").write_text("", encoding="utf-8")  # paralleler Schreiber
    r = wg.store_file(target=t, content="neu", now=1.0, origin="user", verified=True)
    assert r["ok"] is False and r["gate"] == "ask" and "lock" in r["reason"]
    assert not t.exists()  # Konflikt -> KEIN Write


def test_store_lock_konflikt_kein_write(tmp_path):
    s = tmp_path / "s"
    s.mkdir()
    (s / "gesetz-x.md.lock").write_text("", encoding="utf-8")
    r = wg.store(
        question="Gesetz X",
        fact="neu",
        correct="c",
        classify_fn=_cls("write-new"),
        now=1.0,
        structured_dir=s,
        tier3_dir=tmp_path / "t3",
        mandate_obj=_mandate(),
    )
    assert r["ok"] is False and r["gate"] == "ask" and "lock" in r["reason"]
    assert not (s / "gesetz-x.md").exists()


def test_supersede_entry_lock_konflikt(tmp_path):
    t1 = tmp_path / "t1"
    t1.mkdir()
    (t1 / "k.md.lock").write_text("", encoding="utf-8")
    r = wg.supersede_entry(t1, "k", "neu", 7.0)
    assert r["ok"] is False and "lock" in r["reason"]


# ------------------------------------------------- R01: Freigabe-Replay-Schutz
def test_store_file_freigabe_replay_anderer_inhalt_wird_abgelehnt(tmp_path):
    """R01: alte, für anderen Inhalt/Ziel erteilte Freigabe darf NICHT wiederverwendet werden."""
    import approval

    target = tmp_path / "f.md"
    old = approval.TwoPersonApproval(subject=str(target))
    old.approve("Batnini", diff_sha=wg._approval_sha("ALT", target))
    old.approve("Verifier2", diff_sha=wg._approval_sha("ALT", target))
    assert old.finalize()["state"] == "approved"
    r = wg.store_file(
        target=target,
        content="NEU",  # anderer Inhalt -> anderer diff_sha
        now=1.0,
        require_approval=True,
        approval_obj=old,
        activity="self-update",
    )
    assert r["ok"] is False and r["gate"] == "deny" and "Replay" in r["reason"]
    assert not target.exists()  # kein Write bei Replay


def test_store_file_freigabe_gleicher_inhalt_wird_akzeptiert(tmp_path):
    """R01: Freigabe, die an DENSELBEN Inhalt/Ziel gebunden ist, wird akzeptiert."""
    import approval

    target = tmp_path / "f.md"
    sha = wg._approval_sha("NEU", target)
    obj = approval.TwoPersonApproval(subject=str(target))
    obj.approve("Batnini", diff_sha=sha)
    obj.approve("Verifier2", diff_sha=sha)
    obj.finalize()
    r = wg.store_file(
        target=target, content="NEU", now=1.0, require_approval=True, approval_obj=obj, activity="self-update"
    )
    assert r["ok"] is True and r["provenance"]["approval"]["diff_sha"] == sha


def test_store_freigabe_replay_anderer_inhalt_wird_abgelehnt(tmp_path):
    """R01 im store()-Pfad (write-update/self_update)."""
    import approval

    structured = tmp_path / "s" / "gesetz-x.md"
    old = approval.TwoPersonApproval(subject="alt")
    old.approve("Batnini", diff_sha=wg._approval_sha("ALT", structured))
    old.approve("Verifier2", diff_sha=wg._approval_sha("ALT", structured))
    old.finalize()
    r = wg.store(
        question="Gesetz X",
        fact="neu",  # anderer Inhalt/Target als freigegeben
        correct="c",
        classify_fn=_cls("write-update", gate="ask"),
        now=1.0,
        structured_dir=tmp_path / "s",
        tier3_dir=tmp_path / "t3",
        mandate_obj=_mandate(),
        self_update=True,
        approval_obj=old,
    )
    assert r["ok"] is False and r["gate"] == "deny" and "Replay" in r["reason"]
    assert not structured.exists()


# ------------------------------------------------- R08: atomarer Mehrziel-Write
def test_store_file_mehrziel_verzeichnis_kein_halb_write(tmp_path):
    """R08: ungültiges zweites Ziel (Verzeichnis) -> KEIN Write, keine Provenienz."""
    t = tmp_path / "prim.md"
    d = tmp_path / "ziel"
    d.mkdir()
    prov = tmp_path / "prov.jsonl"
    r = wg.store_file(target=t, content="X", now=1.0, origin="user", verified=True, also_write=[d], provenance_log=prov)
    assert r["ok"] is False and r["gate"] == "ask" and "Verzeichnis" in r["reason"]
    assert not t.exists()  # Primärdatei NICHT geschrieben (kein halb-geschrieben)
    assert not d.is_file()
    assert not prov.exists()  # keine Provenienz ohne Write (konsistent)


# ------------------------------------------------- R09: tier1-Konflikt = Teilfehler
def test_store_write_update_tier1_konflikt_ist_teilfehler(tmp_path):
    """R09: tier1-Lock gehalten -> Gesamt-Update NICHT ok=True (Teilfehler gemeldet)."""
    t1 = tmp_path / "tier1"
    t1.mkdir()
    (t1 / "gesetz-x.md.lock").write_text("", encoding="utf-8")  # tier1-Konflikt
    s = tmp_path / "s"
    r = wg.store(
        question="Gesetz X",
        fact="neu",
        correct="c",
        classify_fn=_cls("write-update"),
        now=1.0,
        structured_dir=s,
        tier3_dir=tmp_path / "t3",
        tier1_dir=t1,
        mandate_obj=_mandate(),
    )
    assert r["ok"] is False and r["gate"] == "ask" and r.get("partial") is True
    assert (s / "gesetz-x.md").exists()  # strukturierter Teil wurde geschrieben ...
    assert (tmp_path / "t3" / "provenance.jsonl").exists()  # ... und ist belegt (K3)


# ------------------------------------------------- R20: non-write-Historie append
def test_store_non_write_historie_haengt_an(tmp_path):
    """R20: zwei Aufrufe derselben Frage -> BEIDE Events bleiben (JSONL append)."""
    s, t3 = tmp_path / "s", tmp_path / "t3"
    for at in (100.0, 101.0):
        wg.store(
            question="Q",
            fact="F",
            correct="C",
            classify_fn=_cls("non-write"),
            now=at,
            structured_dir=s,
            tier3_dir=t3,
            history_dir=tmp_path / "hist",
            mandate_obj=_mandate(),
        )
    hist = list((tmp_path / "hist").glob("*.non-write.jsonl"))
    assert len(hist) == 1
    lines = hist[0].read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 2  # beide Events erhalten
    assert [json.loads(line)["at"] for line in lines] == [100.0, 101.0]
