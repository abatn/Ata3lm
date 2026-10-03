"""D) Mapping-Enforcement: Skill→Prozess und Connector→Prozess müssen dokumentiert sein."""

import re
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


def test_hub_abweichung_dokumentiert():
    """D) Die bekannte Hub-Abweichung (fester write-new) ist dokumentiert."""
    s = (ROOT / "ergebnisse/verbindungen-diagramm.md").read_text(encoding="utf-8")
    assert "Abweichung" in s or "Auslegung" in s


def test_connectors_konsistenz():
    """D) AGENTS.md-Connector-Tabelle und reale connectors/*.md sind konsistent."""
    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    on_disk = {p.name for p in (ROOT / "connectors").glob("*.md")}

    referenziert = set(re.findall(r"connectors/[a-z0-9\-]+\.md", agents))
    assert referenziert, "keine Connector-Referenzen in AGENTS.md gefunden"
    for ref in sorted(referenziert):
        name = ref.split("/", 1)[1]
        assert name in on_disk, f"referenzierte Connector-Datei fehlt: {ref}"

    m = re.search(r"(\d+)\s+Dateien insgesamt in `connectors/`", agents)
    assert m, "Gesamtzahl der Connector-Dateien im AGENTS.md-Header nicht gefunden"
    assert int(m.group(1)) == len(on_disk), f"Header nennt {m.group(1)} Dateien, real sind es {len(on_disk)}"
