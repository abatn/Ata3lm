"""Skill-Prozess-Lücken: jeder aktive SKILL.md nennt ≥1 Prozess (Atomic-MCP-Interface).

Quelle (Auftrag): `skills/README.md` (Skill→Prozess), Atomic `https://atomicapp.ai/guides/mcp-server/`.
Offline, deterministisch.
"""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"
MEM = ROOT / "data/memory"


def _active_skills():
    return sorted(p for p in SKILLS.rglob("SKILL.md") if "versions" not in p.parts)


def test_14_aktive_skills():
    assert len(_active_skills()) == 14


def test_jeder_skill_nennt_prozess():
    for f in _active_skills():
        s = f.read_text(encoding="utf-8")
        assert "## Prozesse" in s, f"kein Prozess-Abschnitt: {f.relative_to(ROOT)}"
        assert "`memory." in s, f"kein MCP-Tool genannt: {f.relative_to(ROOT)}"


def test_genannte_prozess_module_existieren():
    search_dirs = [MEM, MEM / "tier3-working", MEM / "shared"]
    for f in _active_skills():
        text = f.read_text(encoding="utf-8")
        block = text.split("## Prozesse", 1)[1] if "## Prozesse" in text else ""
        for mod in re.findall(r"`([a-z_]+\.py)`", block):
            assert any((d / mod).exists() for d in search_dirs), f"{mod} fehlt ({f.relative_to(ROOT)})"
