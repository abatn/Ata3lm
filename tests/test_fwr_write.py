"""FWR-Write-Aktion: 3 Klassen -> echte Writes (AGENTS.md §10.7, offenbar).

Simuliert die 3 Klassen und prüft die echten Datei-Writes:
  non-write -> nur Historie · write-new -> structured + tier3 · write-update -> structured + tier1-Supersede.
Kein Netz: `apply_write_action` ist reine Dateisystem-Logik.
"""

import json

import fast_write_router as fwr


def test_non_write_schreibt_nur_historie(tmp_path):
    r = fwr.apply_write_action(
        "non-write",
        question="Hauptstadt Frankreich?",
        fact="Paris",
        structured_dir=tmp_path / "s",
        tier3_dir=tmp_path / "t3",
        results_dir=tmp_path / "ergebnisse",
        now=1.0,
    )
    assert r["ok"] and r["action"] == "non-write" and r["gate"] == "allow"  # K6/B5: Labelraum
    assert not (tmp_path / "s").exists() and not (tmp_path / "t3").exists()
    hist = list((tmp_path / "ergebnisse").glob("*.non-write.jsonl"))
    assert len(hist) == 1 and json.loads(hist[0].read_text(encoding="utf-8"))["class"] == "non-write"


def test_write_new_schreibt_structured_und_tier3(tmp_path):
    r = fwr.apply_write_action(
        "write-new",
        question="Hauptstadt Xylophonia?",
        fact="Zentaria",
        structured_dir=tmp_path / "s",
        tier3_dir=tmp_path / "t3",
        now=2.0,
    )
    assert r["ok"] and r["action"] == "write-new" and r["gate"] == "ask"
    name = "hauptstadt-xylophonia.md"
    assert (tmp_path / "s" / name).read_text(encoding="utf-8") == "Zentaria"
    assert (tmp_path / "t3" / name).read_text(encoding="utf-8") == "Zentaria"
    assert r["superseded"] is None


def test_write_update_supersediert_tier1_nicht_loeschen(tmp_path):
    t1 = tmp_path / "tier1"
    t1.mkdir()
    (t1 / "hauptstadt-frankreich.md").write_text("Paris (alt)", encoding="utf-8")
    r = fwr.apply_write_action(
        "write-update",
        question="Hauptstadt Frankreich?",
        fact="Paris (neu)",
        structured_dir=tmp_path / "s",
        tier3_dir=tmp_path / "t3",
        tier1_dir=t1,
        now=3.0,
    )
    assert r["ok"] and r["action"] == "write-update" and r["gate"] == "ask"
    assert r["superseded"]["old_found"] is True
    # alter Inhalt archiviert (nicht gelöscht), neuer aktiv
    archived = list(t1.glob("*.superseded-*.md"))
    assert len(archived) == 1 and archived[0].read_text(encoding="utf-8") == "Paris (alt)"
    assert (t1 / "hauptstadt-frankreich.md").read_text(encoding="utf-8") == "Paris (neu)"
    log = json.loads((t1 / "supersede.jsonl").read_text(encoding="utf-8").strip())
    assert log["new"] == "Paris (neu)"


def test_write_update_ohne_alten_eintrag(tmp_path):
    r = fwr.apply_write_action(
        "write-update",
        question="Neu",
        fact="F",
        structured_dir=tmp_path / "s",
        tier3_dir=tmp_path / "t3",
        tier1_dir=tmp_path / "tier1",
        now=4.0,
    )
    assert r["superseded"]["old_found"] is False and r["superseded"]["archived"] is None


def test_write_update_supersede_fn_injizierbar(tmp_path):
    called = {}

    def fake(tier1_dir, key, fact, now):
        called.update({"key": key, "fact": fact})
        return {"key": key, "old_found": True}

    r = fwr.apply_write_action(
        "write-update",
        question="Q",
        fact="F",
        structured_dir=tmp_path / "s",
        tier3_dir=tmp_path / "t3",
        tier1_dir=tmp_path / "tier1",
        now=5.0,
        supersede_fn=fake,
    )
    assert called == {"key": "q", "fact": "F"} and r["superseded"]["old_found"] is True


def test_unbekannte_klasse_kein_write(tmp_path):
    r = fwr.apply_write_action(
        "uncertain", question="Q", fact="F", structured_dir=tmp_path / "s", tier3_dir=tmp_path / "t3", now=6.0
    )
    assert r["ok"] is False and r["gate"] == "ask" and r["written"] == []
