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

import mandate
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
