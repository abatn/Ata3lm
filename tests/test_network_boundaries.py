"""Repro-Datei des Audit b09a0a9 — verbindliche Abnahme-Fälle (N1–N8).

QUELLE DER BEFUNDE (verbindlich): Audit b09a0a9, Datei `tests/test_network_boundaries.py`.
N-Nummerierung = Audit (NICHT Rekursion 062–063). Repro-Fälle:

| N  | Repro-Fall | Phase/Status |
|----|------------|--------------|
| N1 | `test_gateway_provenance_io_failure_cannot_leave_unrecorded_write` | Phase 1 (diese Datei) |
| N2 | `test_consolidated_old_key_does_not_hide_updated_fact` · `test_router_does_not_discard_changed_answer_for_old_key` | Phase 2 (§9 `ask`) |
| N3 | `test_flush_requires_success_evidence` · `test_flush_preserves_archive_when_called_with_filename` | Phase 2 (§9 `ask`) |
| N4 | `test_k8_changed_source_and_ontology_need_bound_approval` | Phase 2 (§9 `ask`) |
| N5 | `test_k8_all_structured_entrypoints_have_required_fields` | Phase 2 (§9 `ask`) |
| N6 | `test_k8_revision_links_to_preceding_entity` | Phase 2 (§9 `ask`) |
| N7 | `test_oracle_success_drives_revision_without_self_report` | Phase 2 (§9 `ask`) |
| N8 | statisch/source-belegt: `tests/test_e2e_theta_probe.py::test_n8_basismessung_vor_peftmodel_vor_em_adapter` | Phase 1 |

Phase-2-Repros wandern mit den jeweiligen Fixes hierher (Auftrag Phase 2:
„wie Phase 1, je Rekursion"). Guardrail 7: echte Fehlerquellen (Dateisystem),
keine Mocks, keine Fake-/skripteten Antworten.
"""

import fast_write_router as fwr
import mandate
import numpy as np
import provenance
import recursion_runner as rr
import slow_consolidation as sc
import write_gateway as wg


def _mandate():
    r = mandate.MandateRegistry()
    return r.issue(
        principal="Batnini",
        agent="knowledge-agent",
        actions={"write:memory"},
        resources={"data/memory"},
        amount_limit=100.0,
        max_uses=1000,
        valid_from=0.0,
        valid_until=10**12,
        approval_threshold=50.0,
    )


def _cls(kind):
    return lambda q, f, c: {"class": kind}


def test_gateway_provenance_io_failure_cannot_leave_unrecorded_write(tmp_path):
    """N1 (Audit b09a0a9, verbindlicher Repro-Fall): Ein Provenienz-I/O-Fehler darf
    KEINEN unprotokollierten Write hinterlassen — Write verweigern ODER Rollback.

    Beide Fehlerquellen sind REAL (Verzeichnis als Log-Ziel; Elternpfad ist Datei),
    beide Gateway-Pfade (`store_file` + `store`) werden geprüft.
    """
    # Fall 1: `store_file`, Log = Verzeichnis -> Verweigern VOR jeder Mutation.
    ziel1 = tmp_path / "a" / "fakt.md"
    log1 = tmp_path / "a" / "prov"
    log1.mkdir(parents=True)
    r1 = wg.store_file(target=ziel1, content="X", now=1.0, origin="user", verified=True, provenance_log=log1)
    assert r1["ok"] is False and not ziel1.exists()

    # Fall 2: `store`, Log = Verzeichnis -> Verweigern vor jeder Mutation (structured + tier3).
    log2 = tmp_path / "b" / "prov"
    log2.mkdir(parents=True)
    r2 = wg.store(
        question="Fakt N1",
        fact="N1-Fakt",
        classify_fn=_cls("write-new"),
        now=1.0,
        structured_dir=tmp_path / "b" / "s",
        tier3_dir=tmp_path / "b" / "t3",
        mandate_obj=_mandate(),
        provenance_log=log2,
    )
    assert r2["ok"] is False and not (tmp_path / "b" / "s").exists() and not (tmp_path / "b" / "t3").exists()

    # Fall 3: `store_file`, Log-Append scheitert NACH dem Datenwrite (Elternpfad = Datei)
    #         -> A3-Rollback auf den Vorzustand.
    blocker = tmp_path / "blocker"
    blocker.write_text("datei", encoding="utf-8")
    prim = tmp_path / "c" / "prim.md"
    prim.parent.mkdir()
    prim.write_text("ALT", encoding="utf-8")
    r3 = wg.store_file(
        target=prim,
        content="NEU",
        now=1.0,
        origin="user",
        verified=True,
        provenance_log=blocker / "sub" / "provenance.jsonl",
    )
    assert r3["ok"] is False and "Rollback" in r3["reason"]
    assert prim.read_text(encoding="utf-8") == "ALT"  # Vorzustand wiederhergestellt

    # Fall 4: `store`, Log-Append scheitert nach dem Datenwrite -> Rollback, keine Datei bleibt.
    r4 = wg.store(
        question="Fakt N1b",
        fact="N1-Fakt-b",
        classify_fn=_cls("write-new"),
        now=1.0,
        structured_dir=tmp_path / "d" / "s",
        tier3_dir=tmp_path / "d" / "t3",
        mandate_obj=_mandate(),
        provenance_log=blocker / "sub2" / "provenance.jsonl",
    )
    assert r4["ok"] is False and "Rollback" in r4["reason"]
    assert not list((tmp_path / "d" / "s").glob("*.md"))  # kein unprotokollierter Write
    assert not list((tmp_path / "d" / "t3").glob("*.md"))

    # Invariante über alle Fälle: kein Write-Record ohne Datei und keine Datei ohne Record.
    assert not (tmp_path / "a" / "provenance.jsonl").exists()
    logs = list(tmp_path.rglob("provenance.jsonl"))
    assert logs == [] or all(p.stat().st_size > 0 for p in logs)


# ===================================================================== N2 (P1)
# Konsolidierung an Inhalt/Modell binden: ein als konsolidiert markierter Fakt
# darf eine NEUE Antwort/Fassung (neuer Hash, gleicher Key) NICHT ausblenden.
KEY = "hauptstadt-frankreich"
OLD_FACT = "Paris ist die Hauptstadt Frankreichs."
NEW_FACT = "Lyon ist die neue Hauptstadt Frankreichs."
QUESTION = "Hauptstadt Frankreich?"


def test_consolidated_old_key_does_not_hide_updated_fact(tmp_path):
    """N2 (Audit b09a0a9, verbindlicher Repro-Fall): gleicher Key, geänderter Fakt
    (neuer Hash) ⇒ wieder `pending` (echte tmp-Dateien, kein Mock)."""
    tier3 = tmp_path / "tier3"
    tier3.mkdir()
    log = tier3 / "provenance.jsonl"
    (tier3 / f"{KEY}.md").write_text(OLD_FACT, encoding="utf-8")
    provenance.append_record(
        log,
        provenance.build_record(fact=OLD_FACT, activity="write-new", agent="t", source="tool:verified", now=1.0),
    )
    state = tmp_path / "state.json"
    sc.mark_consolidated([KEY], state, facts={KEY: OLD_FACT})

    # Der unveränderte Fakt ist konsolidiert ⇒ nicht mehr pending.
    assert sc.collect_pending(tier3, log, state_path=state) == []

    # Gleicher Key, NEUER Inhalt (write-update) ⇒ wieder konsolidierbar.
    (tier3 / f"{KEY}.md").write_text(NEW_FACT, encoding="utf-8")
    provenance.append_record(
        log,
        provenance.build_record(fact=NEW_FACT, activity="write-update", agent="t", source="tool:verified", now=2.0),
    )
    pend = sc.collect_pending(tier3, log, state_path=state)
    assert [p["key"] for p in pend] == [KEY]
    assert pend[0]["fact"] == NEW_FACT


def test_router_does_not_discard_changed_answer_for_old_key(tmp_path):
    """N2 (Audit b09a0a9, verbindlicher Repro-Fall): der Router darf eine GEÄNDERTE
    Antwort zum alten (konsolidierten) Key NICHT als `non-write` verwerfen."""
    state = tmp_path / "state.json"
    sc.mark_consolidated([KEY], state, facts={KEY: OLD_FACT})

    # Unveränderte Antwort ⇒ konsolidiert ⇒ non-write.
    d = fwr.discard_if_consolidated(OLD_FACT, question=QUESTION, state_path=state)
    assert d is not None and d["class"] == "non-write" and d["consolidated_key"] == KEY

    # Geänderte Antwort zum selben Key ⇒ NICHT verworfen (kein `non-write`).
    assert fwr.discard_if_consolidated(NEW_FACT, question=QUESTION, state_path=state) is None


# ===================================================================== N3 (P1)
# Flush nur mit nachgewiesenem Erfolg; Archiv (`.superseded-`) = Historie bleibt.
def test_flush_requires_success_evidence(tmp_path):
    """N3 (Audit b09a0a9, verbindlicher Repro-Fall): ohne Beleg kein Löschen –
    `state_path` fehlt ODER der Key ist dort nicht verbucht."""
    tier3 = tmp_path / "tier3"
    tier3.mkdir()
    f = tier3 / "fakt-a.md"
    f.write_text("Fakt A.", encoding="utf-8")

    # Fall 1: kein `state_path` ⇒ verweigern, nichts löschen.
    r1 = sc.flush(["fakt-a"], tier3)
    assert r1["ok"] is False and r1["removed"] == [] and r1["blocked"] == ["fakt-a"]
    assert f.exists()

    # Fall 2: Beleg vorhanden, aber ohne diesen Key ⇒ blockiert, nichts löschen.
    state = tmp_path / "state.json"
    sc.mark_consolidated(["anderer-key"], state)
    r2 = sc.flush(["fakt-a"], tier3, state_path=state)
    assert r2["ok"] and r2["removed"] == [] and r2["blocked"] == ["fakt-a"]
    assert f.exists()

    # Fall 3: verbuchter Key, aber Datei fehlt ⇒ `missing` (kein Fake-Erfolg).
    sc.mark_consolidated(["gibt-es-nicht"], state)
    r3 = sc.flush(["gibt-es-nicht"], tier3, state_path=state)
    assert r3["missing"] == ["gibt-es-nicht"] and r3["removed"] == []

    # Fall 4: Erfolg belegt ⇒ löschen.
    sc.mark_consolidated(["fakt-a"], state)
    r4 = sc.flush(["fakt-a"], tier3, state_path=state)
    assert r4["removed"] == ["fakt-a"] and not f.exists()


def test_flush_preserves_archive_when_called_with_filename(tmp_path):
    """N3 (Audit b09a0a9, verbindlicher Repro-Fall): ein als Key übergebener
    Archiv-Dateiname (`*.superseded-*`) darf die Historie NIE löschen – und auch
    nicht den aktiven Eintrag (Stem-Trunkierung)."""
    tier3 = tmp_path / "tier3"
    tier3.mkdir()
    active = tier3 / f"{KEY}.md"
    active.write_text(NEW_FACT, encoding="utf-8")
    archive_key = f"{KEY}.superseded-9-abcd1234"
    archive = tier3 / f"{archive_key}.md"
    archive.write_text(OLD_FACT, encoding="utf-8")

    state = tmp_path / "state.json"
    # Beleg deckt den Archiv-Key ab – trotzdem darf nichts gelöscht werden.
    sc.mark_consolidated([archive_key], state)
    res = sc.flush([archive_key], tier3, state_path=state)
    assert res["removed"] == [] and res["blocked"] == [archive_key]
    assert archive.exists() and archive.read_text(encoding="utf-8") == OLD_FACT
    assert active.exists() and active.read_text(encoding="utf-8") == NEW_FACT


# ===================================================================== N4 (P1)
# K8-Metadaten (source_ref/ontology_ref) sind Teil der Zwei-Personen-Freigabebindung:
# eine für den Body erteilte Freigabe deckt einen abweichenden §6-Kopf NICHT ab.
def test_k8_changed_source_and_ontology_need_bound_approval(tmp_path):
    """N4 (Audit b09a0a9, verbindlicher Repro-Fall): Freigabe bindet Body **und**
    §6-Kopf; ein abweichender `source_ref`/`ontology_ref` ⇒ Replay/deny, kein Write."""
    import approval

    s, t3 = tmp_path / "s", tmp_path / "t3"
    structured, tier3 = s / "was-ist-x.md", t3 / "was-ist-x.md"
    # Freigabe exakt für Body „X ist Y" + Zielmenge, OHNE/andere §6-Kopffelder.
    bound = wg._approval_sha("X ist Y", [structured, tier3])  # leere Refs ⇒ alter Hash
    obj = approval.TwoPersonApproval(subject="Was ist X")
    obj.approve("Batnini", diff_sha=bound)
    obj.approve("Taoufik", diff_sha=bound)
    assert obj.finalize()["state"] == "approved"

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
        source_ref="NEUE-QUELLE",  # Kopffeld nach der Freigabe geändert
        ontology_ref="NEUER-BEZUG",
    )
    assert r["ok"] is False and r["gate"] == "deny" and "Replay" in r["reason"]
    assert not structured.exists() and not tier3.exists()  # kein Write bei Replay


# ===================================================================== N6 (P2)
# `prov:wasRevisionOf` verweist auf die reale VORGÄNGER-Entity-ID (Body-Hash),
# nicht auf den Hash der gesamten (K8-Kopf + Body) Datei.
def test_k8_revision_links_to_preceding_entity(tmp_path):
    """N6 (Audit b09a0a9, verbindlicher Repro-Fall): Revisions-ID == vorige Entity-ID
    (der Vorgänger-Hash wird über den Body ohne K8-Kopf gebildet)."""
    s, t3 = tmp_path / "s", tmp_path / "t3"
    r1 = wg.store(
        question="Was ist X",
        fact="X ist ALT",
        correct="ALT",
        classify_fn=_cls("write-new"),
        now=1.0,
        structured_dir=s,
        tier3_dir=t3,
        mandate_obj=_mandate(),
    )
    assert r1["ok"] is True
    r2 = wg.store(
        question="Was ist X",
        fact="X ist NEU",
        correct="NEU",
        classify_fn=_cls("write-update"),
        now=2.0,
        structured_dir=s,
        tier3_dir=t3,
        mandate_obj=_mandate(),
    )
    assert r2["ok"] is True
    prior_id = r1["provenance"]["entity"]["@id"]  # entity:<sha256(body ALT)>
    assert r2["provenance"]["entity"]["prov:wasRevisionOf"] == prior_id


# ===================================================================== N5 (P2)
# JEDER `structured`-Einstieg trägt die §6-Pflichtfelder (K8) – kein Umgehungspfad;
# nicht-structured Scopes (tier3/JSONL/History) bleiben body-only (unverändert).
def test_k8_all_structured_entrypoints_have_required_fields(tmp_path, monkeypatch):
    """N5 (Audit b09a0a9, verbindlicher Repro-Fall): MCP-`write` UND Gateway-`store`
    schreiben in `structured` die 3 §6-Felder (`ontologie-bezug`/`quelle`/`evidence`);
    `tier3` (nicht-structured) bleibt unverändert."""
    import mcp_memory_server as mcp

    scopes = {s: tmp_path / s for s in ("tier1", "tier2", "tier3", "structured", "connectors", "skills")}
    for d in scopes.values():
        d.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(mcp, "SCOPES", scopes)
    monkeypatch.setattr(mcp, "_LINKS", scopes["tier2"] / "mcp-links.jsonl")

    # Einstieg 1: MCP-Tool `memory.write` (echter Codepfad, tmp-Scopes).
    r = mcp.write("structured", "mcp-fakt.md", "MCP-Fakt.", trust="green")
    assert r["ok"] is True
    mcp_doc = (scopes["structured"] / "mcp-fakt.md").read_text(encoding="utf-8")
    for feld in ("ontologie-bezug", "quelle", "evidence"):
        assert feld in mcp_doc.lower()

    # Einstieg 2: Gateway-Kette `store` (structured + tier3).
    g = wg.store(
        question="Was ist X",
        fact="X ist Y",
        correct="Y",
        classify_fn=_cls("write-new"),
        now=1.0,
        structured_dir=tmp_path / "s",
        tier3_dir=tmp_path / "t3",
        mandate_obj=_mandate(),
    )
    assert g["ok"] is True
    gateway_doc = (tmp_path / "s" / "was-ist-x.md").read_text(encoding="utf-8")
    for feld in ("ontologie-bezug", "quelle", "evidence"):
        assert feld in gateway_doc.lower()

    # Gegenprobe: nicht-structured bleibt Body-only (kein §6-Kopf).
    assert (tmp_path / "t3" / "was-ist-x.md").read_text(encoding="utf-8") == "X ist Y"
    r3 = mcp.write("tier3", "arb.md", "Arbeitskopie.", trust="green")
    assert r3["ok"] is True
    assert (scopes["tier3"] / "arb.md").read_text(encoding="utf-8") == "Arbeitskopie."


# ===================================================================== N7 (P2)
# Bei gesetztem `world_state_probe` entscheidet die ORACLE-Evidenz die Revision;
# der Selbstreport (`successes`/`failures`) ist dann nur Annotation (§6) — Compare
# und Revise dürfen NICHT auf verschiedene Evidenzquellen schauen.
def test_oracle_success_drives_revision_without_self_report(tmp_path):
    """N7 (Audit b09a0a9, verbindlicher Repro-Fall): ein **echter** Datei-Oracle-Check
    liefert Erfolg, während der Selbstreport `successes=failures=0` ist ⇒ die Revision
    findet statt (Revise bezieht die Evidenz aus dem Compare-Ergebnis, nicht aus dem
    Selbstreport)."""
    marker = tmp_path / "oracle.txt"
    marker.write_text("OK", encoding="utf-8")

    def probe():  # echtes externes Signal: Datei-Check (Guardrail 7)
        return {"ok": marker.read_text(encoding="utf-8") == "OK"}

    out = rr.run_recursion(
        "Wo?",
        "Kontakt: max@example.com, Version 2.",
        "Version 2.",
        classify_fn=_cls("write-new"),
        mandate_obj=_mandate(),
        structured_dir=tmp_path / "s",
        tier3_dir=tmp_path / "t3",
        now=1.0,
        delta=np.full((4, 4), 0.05),
        successes=0,
        failures=0,
        world_state_probe=probe,
    )
    cmp = out["results"]["Compare"]
    assert cmp["observed"] is True and cmp["score"] == 1.0 and cmp["gate"] == "allow"
    # Selbstreport ist 0/0 – trotzdem Revision, weil die Oracle-Evidenz entscheidet.
    assert out["results"]["Revise"]["skipped"] is False
