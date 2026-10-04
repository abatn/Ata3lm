"""Connector-Prozess-Lücken: jeder Connector nennt ≥1 Prozess (SHACL/W3C).

Quelle (Auftrag): `ergebnisse/verbindungen-diagramm.md` §5 (Connector→Prozess),
W3C SHACL `https://www.w3.org/TR/shacl/`. Offline, deterministisch.
"""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONN = ROOT / "connectors"
MEM = ROOT / "data/memory"


def _connectors():
    return sorted(CONN.glob("*.md"))


def test_17_connectoren():
    assert len(_connectors()) == 17


def test_jeder_connector_nennt_prozess():
    for f in _connectors():
        s = f.read_text(encoding="utf-8")
        assert "## Prozess" in s, f"kein Prozess-Abschnitt: {f.name}"
        block = s.split("## Prozess", 1)[1]
        assert re.search(r"`[a-z_]+\.py`", block), f"kein Prozess genannt: {f.name}"


def test_genannte_prozess_module_existieren():
    dirs = [MEM, MEM / "tier3-working", MEM / "shared"]
    for f in _connectors():
        block = f.read_text(encoding="utf-8").split("## Prozess", 1)[1]
        for mod in re.findall(r"`([a-z_]+\.py)`", block):
            assert any((d / mod).exists() for d in dirs), f"{mod} fehlt ({f.name})"
