"""Procedural Memory L4 (skills/procedural_memory.py) – versionieren · auditieren · rollback.

Alle Schreibpfade werden auf `tmp_path` umgebogen; das Repo bleibt unberührt.
"""

import procedural_memory as pm


def _setup(tmp_path, monkeypatch):
    skills = tmp_path / "skills"
    (skills / "demo").mkdir(parents=True)
    (skills / "demo" / "SKILL.md").write_text("---\nname: demo\n---\n\nAlt.\n", encoding="utf-8")
    monkeypatch.setattr(pm, "ROOT", tmp_path)
    monkeypatch.setattr(pm, "SKILLS", skills)
    monkeypatch.setattr(pm, "AUDIT", skills / "AUDIT.md")
    monkeypatch.setattr(pm, "DIFF_DIR", skills / "audit-diffs")
    return skills / "demo" / "SKILL.md"


def test_active_skills_ohne_versions(tmp_path, monkeypatch):
    skill = _setup(tmp_path, monkeypatch)
    (skill.parent / "versions" / "v1").mkdir(parents=True)
    (skill.parent / "versions" / "v1" / "SKILL.md").write_text("alt", encoding="utf-8")
    assert pm.active_skills() == [skill]  # versions/ ist ausgeschlossen


def test_rel_faellt_auf_absoluten_pfad_zurueck(tmp_path, monkeypatch):
    _setup(tmp_path, monkeypatch)
    outside = tmp_path.parent / "ausserhalb.md"  # liegt außerhalb von ROOT
    assert pm._rel(outside) == str(outside)
    assert pm._rel(tmp_path / "innen.md") == "innen.md"


def test_snapshot_ist_unveraenderlich(tmp_path, monkeypatch):
    skill = _setup(tmp_path, monkeypatch)
    dst = pm.snapshot(skill, "v1", reason="Baseline")
    assert dst.read_text(encoding="utf-8").startswith("---")
    dst.write_text("MANIPULIERT", encoding="utf-8")
    again = pm.snapshot(skill, "v1", reason="nochmal")
    assert again == dst and again.read_text(encoding="utf-8") == "MANIPULIERT"  # kein Overwrite


def test_update_ohne_approved_bleibt_unveraendert(tmp_path, monkeypatch):
    skill = _setup(tmp_path, monkeypatch)
    r = pm.propose_update(skill, "NEU", "Grund", approved=False)
    assert r == {"applied": False, "status": "pending", "reason": "kein approved (Human-Gate)"}
    assert "Alt." in skill.read_text(encoding="utf-8")
    assert pm.AUDIT.exists()  # Audit-Eintrag wurde geschrieben


def test_update_mit_approved_versioniert(tmp_path, monkeypatch):
    skill = _setup(tmp_path, monkeypatch)
    pm.snapshot(skill, "v1", reason="Baseline")
    r = pm.propose_update(skill, "---\nneu\n---\n", "Grund", approved=True)
    assert r["applied"] is True and r["version"] == "v2"
    assert skill.read_text(encoding="utf-8") == "---\nneu\n---\n"
    assert (skill.parent / "versions" / "v2" / "SKILL.md").exists()


def test_rollback_und_fehlende_version(tmp_path, monkeypatch):
    skill = _setup(tmp_path, monkeypatch)
    pm.snapshot(skill, "v1", reason="Baseline")
    skill.write_text("KAPUTT", encoding="utf-8")
    assert pm.rollback(skill, "v9", reason="gibt es nicht")["ok"] is False
    r = pm.rollback(skill, "v1", reason="zurueck")
    assert r["ok"] is True and r["restored"] == "v1"
    assert "Alt." in skill.read_text(encoding="utf-8")
    assert (skill.parent / "versions" / r["saved_current_as"] / "SKILL.md").exists()


def test_demo_laeuft_im_tmp(tmp_path, monkeypatch, capsys):
    _setup(tmp_path, monkeypatch)
    pm._demo()
    out = capsys.readouterr().out
    assert "Versionierung" in out and "Rollback" in out
    assert "Inhalt wieder v1? True" in out
