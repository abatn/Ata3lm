"""Gesetzes-Konformität (AGENTS.md §1–§11) – CI-absicherbar.

Prüft die Struktur des Gesetzes und die im Gesetz geforderten Invarianten
(Provenienz, Versionierung, Tiers, Connectors, Gate-Schwellen). Kein Netz.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AGENTS = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
MEM = ROOT / "data" / "memory"
REK = ROOT / "ergebnisse" / "rekursion"


def test_acht_prinzipien_und_abschnitte():
    for i in range(1, 9):
        assert f"### {i}." in AGENTS, f"Prinzip {i} fehlt"
    assert "## 9. Automatisches Gate" in AGENTS
    for s in ("9.1", "9.2", "9.3"):
        assert f"### {s} " in AGENTS, f"§{s} fehlt"
    for s in (f"10.{i}" for i in range(1, 8)):
        assert f"### {s} " in AGENTS, f"§{s} fehlt"
    for s in ("11.1", "11.2", "11.3", "11.4"):
        assert f"### {s} " in AGENTS, f"§{s} fehlt"


def test_guardrails_1_bis_5():
    for g in (
        "1. Human-Gate",
        "2. Externe Verifikation",
        "3. Provenienz",
        "4. Interface-Stabilität",
        "5. Stufen-Disziplin",
    ):
        assert g in AGENTS, f"Guardrail fehlt: {g}"


def test_gate_schwellen_drift_und_zwei_personen():
    assert "Score ≥ 95%" in AGENTS
    assert "Score 70–94%" in AGENTS
    assert "Score < 70%" in AGENTS
    assert "10 %" in AGENTS  # Drift-Bound §9.1c
    assert "pending → first_approved → second_approved → approved" in AGENTS


def test_provenienz_jeder_rekursion():
    """§6/Guardrail 3: jede Iteration hat Freigabe-Status und Quelle."""
    files = sorted(REK.glob("0[0-9][0-9]-*.md"))
    assert len(files) >= 30, f"zu wenige Rekursions-Dateien: {len(files)}"
    for f in files:
        if f.name.startswith("000-"):
            continue  # Template
        low = f.read_text(encoding="utf-8").lower()
        assert "approved" in low or "rejected" in low or "pending" in low, f"Freigabe fehlt: {f.name}"
        assert "quelle" in low or "http" in low or "arxiv" in low, f"Quelle fehlt: {f.name}"


def test_versionierung_v1_bis_v4():
    for v in ("v1", "v2", "v3", "v4"):
        assert (MEM / "tier1-base" / "versions" / v).is_dir(), f"Version {v} fehlt"


def test_tiers_connectors_und_mcp_basis():
    for p in ("tier1-base", "tier2-index", "tier3-working", "shared"):
        assert (MEM / p).is_dir(), f"Tier fehlt: {p}"
    assert (MEM / "README.md").exists()  # §11: lokale Memory = Pflicht-Basis
    assert len(list((ROOT / "connectors").glob("*.md"))) >= 16


def test_rqgm_loop_im_agenten_verdrahtet():
    """§9.3-freigegebener Loop-Einbau: reflective_agent nutzt evaluator_version."""
    src = (MEM / "reflective_agent.py").read_text(encoding="utf-8")
    assert 'os.environ.get("RQGM_LOOP", "1")' in src
    assert "RedQueenLoop" in src


def test_ci_workflow_deckt_lint_und_tests():
    wf = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    assert "ruff check" in wf and "ruff format --check" in wf
    assert "make test" in wf
    assert "requirements-dev.txt" in wf
