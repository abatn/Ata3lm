"""D) Mapping-Enforcement: Skill→Prozess und Connector→Prozess müssen dokumentiert sein."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_skills_mapping_vorhanden():
    s = (ROOT / "skills/README.md").read_text(encoding="utf-8")
    assert "Skill → Prozess" in s
    for skill in [
        "collect-experience",
        "structure-knowledge",
        "store-memory",
        "cognize",
        "reflect",
        "non-cognitive",
        "act",
        "expand-knowledge",
    ]:
        assert skill in s


def test_connector_mapping_vorhanden():
    s = (ROOT / "ergebnisse/verbindungen-diagramm.md").read_text(encoding="utf-8")
    assert "Connector → Prozess" in s
    for c in ["fast-write-routing", "cognee-memory", "mars-seaa", "governance-mcp"]:
        assert c in s
