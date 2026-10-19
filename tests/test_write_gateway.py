"""K2: Einheitliches Write-Gateway – feste Reihenfolge, EIN Schreibpfad (Auftrag K2).

Abnahme (Bericht §4, Prio 2): jeder Schreibpfad hat Provenienz + Trust geprüft;
genau ein Gateway. STOPP: kein Aufrufer schreibt direkt; Freigabe + Drift VOR Mutation.
"""

import json

import bias_monitor
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


def test_store_file_echter_drift_ueber_tau_ask(tmp_path):
    """§9.1c: ECHTER Drift-Index (JSD, bias_monitor.BiasDriftMonitor) über τ → ask VOR der Mutation."""
    drift = bias_monitor.BiasDriftMonitor(baseline={"write-update": 1.0}, tau=0.10)
    r = wg.store_file(
        target=tmp_path / "drift.md",
        content="x",
        now=1.0,
        origin="user",
        verified=True,
        drift=drift,
        drift_label="write-new",
    )
    assert r["ok"] is False and r["gate"] == "ask"
    assert "Drift-Gate ask" in r["reason"] and not (tmp_path / "drift.md").exists()
    assert drift.history[-1]["DI"] > drift.tau


def test_store_file_freigabe_zwei_personen(tmp_path):
    ok = wg.store_file(
        target=tmp_path / "ok.md",
        content="neu",
        now=1.0,
        require_approval=True,
        approvers=["Batnini", "Verifier2"],
        activity="self-update",
        verified=True,
    )
    assert ok["ok"] is True and ok["provenance"]["approval"]["state"] == "approved"
    assert provenance.verify_record(ok["provenance"])["ok"] is True  # Freigabe gebunden (K3)
    bad = wg.store_file(
        target=tmp_path / "bad.md", content="neu", now=1.0, require_approval=True, approvers=["Solo"], verified=True
    )
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
        verified=True,
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
        verified=True,
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
        verified=True,
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
        verified=True,
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
        verified=True,
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
        verified=True,
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
        verified=True,
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
        verified=True,
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
        target=target,
        content="NEU",
        now=1.0,
        require_approval=True,
        approval_obj=obj,
        activity="self-update",
        verified=True,
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
        verified=True,
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
        verified=True,
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
            verified=True,
        )
    hist = list((tmp_path / "hist").glob("*.non-write.jsonl"))
    assert len(hist) == 1
    lines = hist[0].read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 2  # beide Events erhalten
    assert [json.loads(line)["at"] for line in lines] == [100.0, 101.0]


# ------------------------------------------------- A1: Freigabe an gesamte Zielmenge
def test_a1_freigabe_nur_primziel_deckt_also_write_nicht(tmp_path):
    """A1 (P1): eine nur für das Primärziel erteilte Freigabe deckt ein `also_write`-Ziel NICHT ab."""
    import approval

    prim, extra = tmp_path / "prim.md", tmp_path / "extra.md"
    sha_primary_only = wg._approval_sha("NEU", prim)  # ohne also_write gebunden
    obj = approval.TwoPersonApproval(subject="s")
    obj.approve("Batnini", diff_sha=sha_primary_only)
    obj.approve("Verifier2", diff_sha=sha_primary_only)
    obj.finalize()
    r = wg.store_file(
        target=prim,
        content="NEU",
        now=1.0,
        require_approval=True,
        approval_obj=obj,
        activity="self-update",
        also_write=[extra],
        verified=True,
    )
    assert r["ok"] is False and r["gate"] == "deny" and "Replay" in r["reason"]
    assert not prim.exists() and not extra.exists()  # kein nicht-genehmigtes Ziel geschrieben


def test_a1_freigabe_ueber_alle_ziele_wird_akzeptiert(tmp_path):
    """A1 (P1): die Freigabe über die gesamte Zielmenge (Primär + `also_write`) wird akzeptiert."""
    import approval

    prim, extra = tmp_path / "prim.md", tmp_path / "extra.md"
    sha = wg._approval_sha("NEU", [prim, extra])
    obj = approval.TwoPersonApproval(subject="s")
    obj.approve("Batnini", diff_sha=sha)
    obj.approve("Verifier2", diff_sha=sha)
    obj.finalize()
    r = wg.store_file(
        target=prim,
        content="NEU",
        now=1.0,
        require_approval=True,
        approval_obj=obj,
        activity="self-update",
        also_write=[extra],
        verified=True,
    )
    assert r["ok"] is True and len(r["written"]) == 2
    assert r["provenance"]["approval"]["diff_sha"] == sha


# ------------------------------------------------- A3: atomarer Write + Rollback
def test_a3_io_fehler_zweites_ziel_prim_bleibt_altstand(tmp_path):
    """A3 (P1): I/O-Fehler am 2. Ziel -> Primärdatei wird auf den Vorzustand zurückgerollt."""
    prim = tmp_path / "prim.md"
    prim.write_text("ALT", encoding="utf-8")
    blocker = tmp_path / "blocker"
    blocker.write_text("datei", encoding="utf-8")  # Elternpfad ist Datei -> mkdir scheitert
    prov = tmp_path / "prov.jsonl"
    r = wg.store_file(
        target=prim,
        content="NEU",
        now=1.0,
        origin="user",
        verified=True,
        also_write=[blocker / "sub.md"],
        provenance_log=prov,
    )
    assert r["ok"] is False and r["gate"] == "ask" and "Rollback" in r["reason"]
    assert prim.read_text(encoding="utf-8") == "ALT"  # Vorzustand wiederhergestellt
    assert not prov.exists()  # keine Provenienz ohne Write (konsistent)


def test_a3_io_fehler_zweites_ziel_neue_primdatei_wird_entfernt(tmp_path):
    """A3 (P1): war die Primärdatei neu, entfernt der Rollback sie wieder (kein Teilzustand)."""
    prim = tmp_path / "neu.md"
    blocker = tmp_path / "blocker"
    blocker.write_text("datei", encoding="utf-8")
    r = wg.store_file(
        target=prim,
        content="NEU",
        now=1.0,
        origin="user",
        verified=True,
        also_write=[blocker / "sub.md"],
    )
    assert r["ok"] is False and "Rollback" in r["reason"]
    assert not prim.exists()


def test_a3_supersede_archiv_wird_zurueckgerollt(tmp_path):
    """A3 (P1): scheitert das Schreiben, wird auch das zuvor angelegte Archiv zurückgerollt."""
    prim = tmp_path / "prim.md"
    prim.write_text("ALT", encoding="utf-8")
    blocker = tmp_path / "blocker"
    blocker.write_text("datei", encoding="utf-8")
    r = wg.store_file(
        target=prim,
        content="NEU",
        now=2.0,
        origin="user",
        verified=True,
        supersede=True,
        also_write=[blocker / "sub.md"],
    )
    assert r["ok"] is False
    assert prim.read_text(encoding="utf-8") == "ALT"
    assert list(tmp_path.glob("prim.superseded-*")) == []  # Archiv zurückgerollt


def test_a3_supersede_entry_rollback_mit_altstand(tmp_path):
    """A3 (P1): supersede_entry rollt bei Schreibfehler den alten tier1-Eintrag zurück."""
    t1 = tmp_path / "t1"
    t1.mkdir()
    (t1 / "k.md").write_text("ALT", encoding="utf-8")
    (t1 / "supersede.jsonl").mkdir()  # Log-Ziel ist ein Verzeichnis -> open() scheitert
    r = wg.supersede_entry(t1, "k", "NEU", 7.0)
    assert r["ok"] is False and "Rollback" in r["reason"]
    assert (t1 / "k.md").read_text(encoding="utf-8") == "ALT"
    assert list(t1.glob("k.superseded-*")) == []


def test_a3_supersede_entry_rollback_ohne_altstand(tmp_path):
    """A3 (P1): ohne Altstand entfernt der Rollback den halb geschriebenen tier1-Eintrag."""
    t1 = tmp_path / "t1"
    t1.mkdir()
    (t1 / "supersede.jsonl").mkdir()
    r = wg.supersede_entry(t1, "neu", "NEU", 7.0)
    assert r["ok"] is False and "Rollback" in r["reason"]
    assert not (t1 / "neu.md").exists()


def test_archive_file_kollision_gleicher_inhalt(tmp_path):
    """N3/K5: gleicher Inhalt in derselben Sekunde -> Kollisions-Recheck (kein Überschreiben)."""
    p = tmp_path / "same.md"
    p.write_text("GLEICH", encoding="utf-8")
    a1 = wg._archive_file(p, 5.0)
    a2 = wg._archive_file(p, 5.0)  # identischer Inhalt/Zeitstempel -> Namenskollision
    assert a1 != a2 and a1.exists() and a2.exists()
    assert {a1.read_text(encoding="utf-8"), a2.read_text(encoding="utf-8")} == {"GLEICH"}


# ------------------------------------------------- K8: §6-Pflichtfelder im structured-Doc
def _structured_store(tmp_path, **kw):
    return wg.store(
        question="Was ist X",
        fact="X ist Y",
        correct="Y",
        classify_fn=_cls("write-new"),
        now=1.0,
        structured_dir=tmp_path / "s",
        tier3_dir=tmp_path / "t3",
        mandate_obj=_mandate(),
        **kw,
    )


def test_k8_structured_traegt_pflichtfelder_und_body(tmp_path):
    """K8: `structured` trägt §6-Kopf; `tier3` bleibt Body-only (K3-Hash/§10.3 intakt)."""
    r = _structured_store(tmp_path, verified=True)
    assert r["ok"] is True
    doc = (tmp_path / "s" / "was-ist-x.md").read_text(encoding="utf-8")
    for feld in ("ontologie-bezug", "quelle", "evidence"):
        assert feld in doc.lower()
    assert doc.rstrip().endswith("X ist Y")  # Body unverändert
    assert "sha256:" in doc  # Evidence bindet den K3-Hash
    t3 = (tmp_path / "t3" / "was-ist-x.md").read_text(encoding="utf-8")
    assert t3 == "X ist Y" and provenance.content_hash(t3) == r["provenance"]["entity"]["sha256"]


def test_k8_ontology_ref_und_source_ref_im_kopf(tmp_path):
    r = _structured_store(tmp_path, ontology_ref="Denken (5)", source_ref="AGENTS.md §9.1c", verified=True)
    assert r["ok"] is True
    doc = (tmp_path / "s" / "was-ist-x.md").read_text(encoding="utf-8")
    assert "Denken (5)" in doc and "AGENTS.md §9.1c" in doc


def test_k8_ohne_refs_ehrlich_offen_kein_fake(tmp_path):
    """K8/A5: ohne Ontologie-Ref wird „offen" markiert; die Quelle ist der reale Record-Ort (§6)."""
    _structured_store(tmp_path, origin="tool:verified", verified=True)
    doc = (tmp_path / "s" / "was-ist-x.md").read_text(encoding="utf-8")
    assert "offen (§4" in doc  # Ontologie-Bezug offen (A5)
    assert "tool:verified" in doc  # Quelle = realer PROV-O-Ort (kein Fake)


def test_k8_fail_closed_untrusted_und_unverified(tmp_path):
    """K8/§9.2c: untrusted/unverified -> KEINE structured-Datei, kein Write."""
    r = _structured_store(tmp_path, origin="web:untrusted")
    assert r["ok"] is False and not (tmp_path / "s").exists()
    r2 = _structured_store(tmp_path, verified=False)
    assert r2["ok"] is False and not (tmp_path / "s").exists()


def test_n6_legacy_body_only_structured_file_bleibt_body(tmp_path):
    """N6: ein structured-Dokument OHNE K8-Kopf (Write vor K8) wird als Body gehasht."""
    s = tmp_path / "s"
    s.mkdir()
    (s / "was-ist-x.md").write_text("X ist ALT", encoding="utf-8")  # Body-only, kein §6-Kopf
    r = wg.store(
        question="Was ist X",
        fact="X ist NEU",
        correct="NEU",
        classify_fn=_cls("write-update"),
        now=1.0,
        structured_dir=s,
        tier3_dir=tmp_path / "t3",
        mandate_obj=_mandate(),
        verified=True,
    )
    assert r["ok"] is True
    expected = f"entity:{provenance.content_hash('X ist ALT')[:16]}"
    assert r["provenance"]["entity"]["prov:wasRevisionOf"] == expected


def test_n4_freigabe_mit_gebundenen_refs_wird_akzeptiert(tmp_path):
    """N4: eine an Body + §6-Kopf gebundene Freigabe wird akzeptiert (positiver Zweig)."""
    import approval

    s, t3 = tmp_path / "s", tmp_path / "t3"
    structured = s / "was-ist-x.md"
    sha = wg._approval_sha(
        "X ist Y", [structured, t3 / "was-ist-x.md"], source_ref="AGENTS.md", ontology_ref="Denken (5)"
    )
    obj = approval.TwoPersonApproval(subject="Was ist X")
    obj.approve("Batnini", diff_sha=sha)
    obj.approve("Taoufik", diff_sha=sha)
    obj.finalize()
    r = wg.store(
        question="Was ist X",
        fact="X ist Y",
        correct="Y",
        classify_fn=_cls("write-new"),
        now=1.0,
        structured_dir=s,
        tier3_dir=t3,
        mandate_obj=_mandate(),
        self_update=True,
        approval_obj=obj,
        source_ref="AGENTS.md",
        ontology_ref="Denken (5)",
        verified=True,
    )
    assert r["ok"] is True and r["provenance"]["approval"]["diff_sha"] == sha
    assert "Denken (5)" in structured.read_text(encoding="utf-8")


# --------------------------- N1: Provenienz + Datenwrite = EINE Transaktion (K3)
def test_n1_store_provenance_log_ist_verzeichnis_kein_write(tmp_path):
    """N1 (Auftrag): `provenance_log` = Verzeichnis -> Write VERWEIGERT (R08), keine Mutation."""
    log = tmp_path / "prov"
    log.mkdir()  # Log-Ziel ist ein Verzeichnis -> Mit-Append in _commit wuerde scheitern
    r = wg.store(
        question="Fakt N1",
        fact="N1-Fakt",
        classify_fn=_cls("write-new"),
        now=1.0,
        structured_dir=tmp_path / "s",
        tier3_dir=tmp_path / "t3",
        mandate_obj=_mandate(),
        provenance_log=log,
        verified=True,
    )
    assert r["ok"] is False and "Verzeichnis" in r["reason"]
    assert not (tmp_path / "s").exists()  # Akzeptanz: provenance_log=Verzeichnis => KEIN Write
    assert not (tmp_path / "t3").exists()


def test_n1_store_file_provenance_log_ist_verzeichnis_kein_write(tmp_path):
    """N1 (Auftrag): dieselbe Verweigerung im `store_file`-Pfad (gleiche Transaktionsregel)."""
    t = tmp_path / "fakt.md"
    log = tmp_path / "prov"
    log.mkdir()
    r = wg.store_file(target=t, content="X", now=1.0, origin="user", verified=True, provenance_log=log)
    assert r["ok"] is False and "Verzeichnis" in r["reason"]
    assert not t.exists()  # kein Write ohne Provenienz (K3)


def test_n1_log_schreibfehler_rollt_datenwrite_zurueck(tmp_path):
    """N1 (Auftrag): Log-Fehler -> A3-Rollback, kein unprotokollierter Write (kein Teilzustand)."""
    prim = tmp_path / "prim.md"
    prim.write_text("ALT", encoding="utf-8")
    blocker = tmp_path / "blocker"
    blocker.write_text("datei", encoding="utf-8")
    log = blocker / "sub" / "provenance.jsonl"  # Elternpfad ist Datei -> Log-Append scheitert REAL
    r = wg.store_file(target=prim, content="NEU", now=1.0, origin="user", verified=True, provenance_log=log)
    assert r["ok"] is False and "Rollback" in r["reason"]
    assert prim.read_text(encoding="utf-8") == "ALT"  # Vorzustand wiederhergestellt
    assert list(tmp_path.glob("prim.superseded-*")) == []  # Archiv mitgerollt


def test_n1_teilpfad_tier1_konflikt_protokolliert_exakt_einmal(tmp_path):
    """N1: R09-Teilpfad (tier1-Konflikt) -> Record steht GENAU einmal im Provenienz-Log."""
    t1 = tmp_path / "t1"
    t1.mkdir()
    (t1 / "supersede.jsonl").mkdir()  # supersede_entry: Log-Ziel ist Verzeichnis -> echter Fehler
    r = wg.store(
        question="Fakt N1 R09",
        fact="NEU",
        classify_fn=_cls("write-update"),
        now=1.0,
        structured_dir=tmp_path / "s",
        tier3_dir=tmp_path / "t3",
        tier1_dir=t1,
        mandate_obj=_mandate(),
        verified=True,
    )
    assert r["ok"] is False and r.get("partial") is True
    lines = (tmp_path / "t3" / "provenance.jsonl").read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1  # kein Doppel-Eintrag (Teilpfad + Transaktion)


def test_n1_record_line_ist_format_zwilling_zu_append_record(tmp_path):
    """N1: `_record_line` serialisiert byte-gleich zu `provenance.append_record` (kein Format-Drift)."""
    rec = provenance.build_record(fact="F", activity="write", agent="a", source="user", now=1.0)
    p = tmp_path / "log.jsonl"
    provenance.append_record(p, rec)
    assert p.read_text(encoding="utf-8") == wg._record_line(rec)
