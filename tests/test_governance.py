"""Governance-Tests: Zwei-Personen-Flow (§9.3) + Gesetzestext §9/§9.1/§10.4.

Rein lokal: `data/memory/approval.py` + `AGENTS.md` werden gelesen/ausgeführt.
"""

from pathlib import Path

import approval

ROOT = Path(__file__).resolve().parents[1]
AGENTS = (ROOT / "AGENTS.md").read_text(encoding="utf-8")


# ------------------------------------------------- Zwei-Personen-Flow §9.3
def test_flow_pending_first_second_approved():
    a = approval.TwoPersonApproval(subject="CI-Test")
    assert a.status() == {
        "subject": "CI-Test",
        "state": "pending",
        "approvers": [],
        "count": 0,
        "diff_sha": None,
    }
    assert a.approve("Batnini")["state"] == "first_approved"
    assert a.approve("Pruefer2")["state"] == "second_approved"
    assert a.finalize()["ok"] is True
    assert a.status()["state"] == "approved"


def test_eine_person_reicht_nicht():
    a = approval.TwoPersonApproval(subject="CI-Test")
    a.approve("Batnini")
    r = a.finalize()
    assert r["ok"] is False
    assert "2" in r["reason"]
    assert a.status()["state"] == "first_approved"


def test_gleiche_person_zweimal_wird_abgelehnt():
    a = approval.TwoPersonApproval(subject="CI-Test")
    a.approve("Batnini")
    r = a.approve("Batnini")
    assert r["ok"] is False
    assert a.status()["count"] == 1


def test_ohne_natuerliche_person_keine_freigabe():
    a = approval.TwoPersonApproval(subject="CI-Test")
    assert a.approve("")["ok"] is False
    assert a.approve("   ")["ok"] is False


# ------------------------------------------------------------ Gesetz §9
def test_gate_schwellen_laut_gesetz():
    assert "Score ≥ 95%" in AGENTS
    assert "Score 70–94%" in AGENTS
    assert "Score < 70%" in AGENTS


def test_zusaetzliche_ask_pflichten_laut_gesetz():
    assert "Neue Quelle" in AGENTS and "Immer menschliches Gate (ask)" in AGENTS
    assert "Interface-Änderung" in AGENTS
    assert "Drift > Drift-Bound" in AGENTS


def test_drift_bound_und_versionierung_vorhanden():
    assert "Drift-Bound" in AGENTS and "10 %" in AGENTS
    assert (ROOT / "data/memory/tier1-base/versions/v4").is_dir()
    readme = (ROOT / "data/memory/README.md").read_text(encoding="utf-8")
    assert "`versions/v1`,`v2`,`v3`,`v4`" in readme


def test_router_unsicherheit_fuehrt_zu_human_gate():
    """§10.4: Unsicherheit des Routers -> Human-Gate (ask)."""
    assert "Bei Unsicherheit des Routers" in AGENTS
    assert "Human-Gate (ask)" in AGENTS


def test_approve_nach_approved_wird_abgelehnt():
    a = approval.TwoPersonApproval(subject="CI-Test")
    a.approve("Batnini")
    a.approve("Pruefer2")
    a.finalize()
    r = a.approve("Dritte")
    assert r["ok"] is False and "bereits approved" in r["reason"]


def test_approval_demo_laeuft(capsys):
    approval._demo()
    out = capsys.readouterr().out
    assert "Zwei-Personen-Verifikation" in out
    assert "approved" in out


def test_flow_zwei_verifizierer_mit_diff():
    """Auftrag: Verifier2 prüft denselben Diff (Batnini + Verifier2)."""
    a = approval.TwoPersonApproval(subject="Hochrisiko-Änderung")
    assert a.approve("Batnini", diff_sha="abc123")["state"] == "first_approved"
    assert a.approve("Verifier2", diff_sha="abc123")["state"] == "second_approved"
    assert a.finalize()["ok"] is True
    assert a.status()["diff_sha"] == "abc123"
    assert [h.get("diff_sha") for h in a.history] == ["abc123", "abc123", None]


def test_diff_konflikt_wird_abgelehnt():
    a = approval.TwoPersonApproval(subject="Hochrisiko-Änderung")
    a.approve("Batnini", diff_sha="abc123")
    r = a.approve("Verifier2", diff_sha="xyz999")
    assert r["ok"] is False and "Diff stimmt nicht" in r["reason"]
    assert a.status()["count"] == 1 and a.status()["state"] == "first_approved"


def test_diff_fehlt_beim_zweiten_verifizierer():
    a = approval.TwoPersonApproval(subject="Hochrisiko-Änderung")
    a.approve("Batnini", diff_sha="abc123")
    r = a.approve("Verifier2")  # kein Diff -> Ablehnung
    assert r["ok"] is False and r["got"] is None
    assert a.status()["count"] == 1
