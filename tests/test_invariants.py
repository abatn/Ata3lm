"""Offline-Invarianten: Versionierung, Snapshots, Skills, Pflichtfelder.

Deterministisch, kein Netz. Regelquellen: AGENTS.md §9.1b (Versionierung) und
`ergebnisse/versionierung.md` (Inhalt je Snapshot). Guardrail 7-konform rein lesend.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSIONS = ROOT / "data" / "memory" / "tier1-base" / "versions"
STRUCTURED = ROOT / "knowledge" / "structured"

# Basisdateien, die JEDER Tier-1-Snapshot enthält (ergebnisse/versionierung.md §2).
BASIS_DATEIEN = ("core-relations.md", "episodic_graph.json", "identity.md", "ontology.md")
# `AGENTS.md` wird erst ab v5 mit-versioniert (ergebnisse/versionierung.md §4:
# v1–v4 ohne, v5+ „(+ AGENTS.md)"). Dokumentierte, legitime Ausnahme.
AGENTS_AB = 5

# Pflichtfelder je `knowledge/structured/*.md` (case-insensitiv), vgl. AGENTS.md §6.
PFLICHTFELDER = ("ontologie-bezug", "quelle", "evidence")


def _versionsnummern(directory: Path):
    """Alle `vN`-Unterordner als sortierte Ganzzahlen (N ≥ 1)."""
    nummern = []
    for p in directory.glob("v[0-9]*"):
        if p.is_dir() and p.name[1:].isdigit():
            nummern.append(int(p.name[1:]))
    return sorted(nummern)


def _assert_lueckenlos(nummern, kontext: str):
    assert nummern, f"keine Versionsverzeichnisse in {kontext}"
    assert nummern[0] == 1, f"{kontext} beginnt nicht bei v1: {nummern}"
    assert nummern == list(range(1, max(nummern) + 1)), f"Lücke in {kontext}: {nummern}"


def test_versions_lueckenlos():
    """v1..vN lückenlos; jeder Snapshot hat die Pflichtdateien."""
    nummern = _versionsnummern(VERSIONS)
    _assert_lueckenlos(nummern, "tier1-base/versions")
    for n in nummern:
        snap = VERSIONS / f"v{n}"
        for name in BASIS_DATEIEN:
            assert (snap / name).is_file(), f"v{n} fehlt {name}"
        if n >= AGENTS_AB:
            assert (snap / "AGENTS.md").is_file(), f"v{n} fehlt AGENTS.md"


def test_neuester_snapshot_gleich_aktuell():
    """Der jüngste Snapshot des Gesetzes ist byte-identisch mit AGENTS.md."""
    nummern = _versionsnummern(VERSIONS)
    assert nummern, "keine Versionen gefunden"
    neuester = VERSIONS / f"v{max(nummern)}" / "AGENTS.md"
    assert neuester.is_file(), f"{neuester} fehlt"
    assert neuester.read_text(encoding="utf-8") == (ROOT / "AGENTS.md").read_text(encoding="utf-8")


def test_skills_versions_lueckenlos():
    """Für jeden Skill-Ordner mit `versions/` sind die vN lückenlos ab v1."""
    skill_versions = sorted(p for p in (ROOT / "skills").rglob("versions") if p.is_dir())
    assert skill_versions, "keine Skill-versions/ gefunden"
    for directory in skill_versions:
        _assert_lueckenlos(_versionsnummern(directory), str(directory.relative_to(ROOT)))


def test_structured_pflichtfelder():
    """Jede `knowledge/structured/*.md` (außer README.md) trägt die Pflichtfelder.

    Geprüft am 2026-10-03: alle 7 Dateien enthalten „ontologie-bezug", „quelle"
    und „evidence" (case-insensitiv) – keine weiteren legitimen Ausnahmen.
    """
    dateien = [p for p in sorted(STRUCTURED.glob("*.md")) if p.name != "README.md"]
    assert dateien, "keine strukturierten Dateien gefunden"
    for datei in dateien:
        text = datei.read_text(encoding="utf-8").lower()
        for feld in PFLICHTFELDER:
            assert feld in text, f"{datei.name} ohne Pflichtfeld '{feld}'"


def test_root_repo_relativ():
    """S6: keine harten /home/opc-Pfade – ROOT == Repo-Wurzel."""
    from pathlib import Path

    import gaama_extract
    import ingestion_hook
    import lru_cache
    import mcp_memory_server
    import reflective_agent
    import shared_memory

    repo = Path(__file__).resolve().parents[1]
    for m in (ingestion_hook, reflective_agent, gaama_extract, shared_memory, lru_cache, mcp_memory_server):
        assert Path(m.ROOT).resolve() == repo
