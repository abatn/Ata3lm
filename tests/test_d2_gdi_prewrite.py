"""D2 (Audit d25486c, P1): kalibriertes **GDI-Pre-Write-Gate VOR der Mutation**.

Quelle (**Belegt**): arXiv:2603.06333 (SAHOO) Gl. 12–16 – GDI ist Schutzmechanismus
**vor** der Änderung; in `AGENTS.md` §9.1c zitiert ⇒ keine neue Quelle. Offline mit
**injizierter** `embed_fn` + Kalibrierung (Guardrail 7: kein Netz/Endpoint).

Nachweis: der kalibrierte GDI wirkt in **Stufe 3 (`_stage_gedaechtnis`)** und hält die
Store-Kette (`pipeline.route_and_store` → `write_gateway.store`) **vor** der Mutation an
(`gdi > τ ⇒ ask ⇒ KEIN Write`). Default (GDI aus) ⇒ exakt altes Verhalten.

**Interface-Änderung §9 approved** (Batnini + Taoufik): neuer Parameter `gdi_drift`
in `route_and_store`/`store` (additiv, Default None).
"""

import bias_monitor as bm
import lifecycle_runner as lr

#: Kalibrierte Gewichte/τ wie in `ergebnisse/drift-calibration-sahoo.json`.
CAL = {"weights": {"sem": 0.0, "lex": 0.85, "struct": 0.0, "dist": 0.15}, "tau": 0.24}


def _emb_same(_text):
    """Stub-Embedder: konstanter Vektor ⇒ Δ_sem = 0; lexikalischer Drift dominiert."""
    return [1.0, 0.0]


def _classify(cls):
    return lambda q, f, c: {"class": cls}


def _run(tmp_path, name, **extra):
    """Ein Write-Lauf (`write-new`) mit/ohne gebundenes GDI-Pre-Write-Gate."""
    return lr.run_cycle(
        name,
        extra.pop("fact"),
        "c",
        classify_fn=_classify("write-new"),
        structured_dir=tmp_path / "s",
        tier3_dir=tmp_path / "t",
        **extra,
    )


def test_gdi_over_tau_blocks_write_before_mutation(tmp_path, monkeypatch):
    """GDI > τ ⇒ `ask` ⇒ die Mutation (Structured-File) entsteht NIE (Stufe 3)."""
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    stem = "gdihoch"
    out = _run(
        tmp_path,
        stem,
        fact="beta beta",  # lexikalischer Drift gegen "alpha alpha" > τ (0.24)
        gdi=True,
        embed_fn=_emb_same,
        gdi_prev_text="alpha alpha",
        gdi_calibration=CAL,
    )
    ged = out["results"]["Gedächtnis"]
    assert ged["ok"] is False  # Gate hielt VOR der Mutation an
    assert ("gdi_drift", 0.85) in ged["steps"]
    assert not (tmp_path / "s" / f"{stem}.md").exists()  # KEIN Structured-File
    assert not (tmp_path / "t" / f"{stem}.md").exists()  # KEIN tier3-File
    assert not (tmp_path / "t" / "provenance.jsonl").exists()  # KEINE Provenienz-Zeile
    # Stufe 8 (Revisionsfilter) sieht ok=False ⇒ nie revised.
    assert out["results"]["Wissen+"]["revised"] is False


def test_gdi_under_tau_allows_write(tmp_path, monkeypatch):
    """GDI ≤ τ ⇒ `allow` ⇒ der Write erfolgt (Pre-Write-Gate blockiert nicht)."""
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    stem = "gdition"
    out = _run(
        tmp_path,
        stem,
        fact="a b c",  # kein Drift gegen "a b c" ≤ τ
        gdi=True,
        embed_fn=_emb_same,
        gdi_prev_text="a b c",
        gdi_calibration=CAL,
    )
    ged = out["results"]["Gedächtnis"]
    assert ged["ok"] is True
    assert ("gdi_drift", 0.0) in ged["steps"]
    assert (tmp_path / "s" / f"{stem}.md").exists()  # Structured-File entstanden
    assert (tmp_path / "t" / f"{stem}.md").exists()  # tier3-File entstanden


def test_default_gdi_off_unchanged(tmp_path, monkeypatch):
    """Default (GDI aus) ⇒ `gdi_drift=None` ⇒ exakt altes Verhalten (Write erfolgt)."""
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    stem = "default"
    out = _run(tmp_path, stem, fact="Fakt")
    ged = out["results"]["Gedächtnis"]
    assert ged["ok"] is True
    assert (tmp_path / "s" / f"{stem}.md").exists()
    assert all(step[0] != "gdi_drift" for step in ged["steps"])  # kein GDI-Schritt


def test_observe_gdi_grenze_tau_genau_allow():
    """Randfall: GDI == τ ist NICHT > τ ⇒ allow (Gl. 15: `GDI > τ` flaggt)."""
    m = bm.BiasDriftMonitor(baseline={}, gdi_weights=CAL["weights"], gdi_tau=CAL["tau"])
    # gleicher Text ⇒ GDI 0.0 ≤ τ ⇒ allow (Grenze bleibt beim strikten `>`).
    r = m.observe_gdi("a", "a", embed_fn=_emb_same)
    assert r["gdi"] <= CAL["tau"] and r["gate"] == "allow"
