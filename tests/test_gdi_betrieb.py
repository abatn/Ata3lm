"""GDI-Betriebspfad (Rekursion 093) – kalibriertes τ+Gewichte im Monitor/Runner.

Offline-Tests mit **injizierter** `embed_fn` und Kalibrierung (Guardrail 7: kein
Netz/Endpoint). Quelle (**Belegt**): arXiv:2603.06333 (SAHOO) Gl. 12–16, in
`AGENTS.md` §9.1c zitiert ⇒ keine neue Quelle. **Interface-Änderung §9 approved**
(Batnini + Taoufik, 2026-10-08): `load_calibration`, `observe_gdi`, GDI-Schalter
im `run_cycle`.

Der stabile `embed_fn`-Stub liefert für JEDEN Text denselben Vektor ⇒ Semantic-
Drift = 0; die kalibrierten Gewichte (lex 0.85) machen den **lexikalischen** Drift
zum bestimmenden Signal.
"""

import json

import bias_monitor as bm
import lifecycle_runner as lr

#: Kalibrierte Gewichte/τ wie in `ergebnisse/drift-calibration-sahoo.json`.
CAL = {"weights": {"sem": 0.0, "lex": 0.85, "struct": 0.0, "dist": 0.15}, "tau": 0.24}


def _emb_same(_text):
    """Stub-Embedder: konstanter Vektor ⇒ Δ_sem = 0 (kein Netz)."""
    return [1.0, 0.0]


def _classify(cls):
    return lambda q, f, c: {"class": cls}


# ---------------------------------------------------------- load_calibration


def test_load_calibration_liest_echte_json(tmp_path):
    p = tmp_path / "cal.json"
    p.write_text(json.dumps({"tau": CAL["tau"], "weights": CAL["weights"]}), encoding="utf-8")
    out = bm.load_calibration(p)
    assert out == CAL


def test_load_calibration_default_pfad_ist_echte_datei():
    out = bm.load_calibration()  # path=None ⇒ CALIBRATION_PATH (Repo-Datei)
    assert out is not None and out["tau"] > 0.0
    assert abs(sum(out["weights"].values()) - 1.0) < 1e-9


def test_load_calibration_fehlt_ist_none(tmp_path):
    assert bm.load_calibration(tmp_path / "fehlt.json") is None  # OSError ⇒ Fallback


def test_load_calibration_ungueltig_ist_none(tmp_path):
    p = tmp_path / "bad.json"
    p.write_text("{kaputt", encoding="utf-8")
    assert bm.load_calibration(p) is None  # ungültiges JSON
    p.write_text(json.dumps({"weights": CAL["weights"]}), encoding="utf-8")
    assert bm.load_calibration(p) is None  # tau fehlt (KeyError)
    p.write_text(json.dumps({"weights": {"sem": 1.0}, "tau": 0.2}), encoding="utf-8")
    assert bm.load_calibration(p) is None  # Gewichte unvollständig (ValueError)
    p.write_text(json.dumps([1, 2]), encoding="utf-8")
    assert bm.load_calibration(p) is None  # kein Dict (TypeError)


# -------------------------------------------------------------- observe_gdi


def test_observe_gdi_niedrig_allow_hoch_ask():
    m = bm.BiasDriftMonitor(baseline={}, gdi_weights=CAL["weights"], gdi_tau=CAL["tau"])
    low = m.observe_gdi("a b c", "a b c", embed_fn=_emb_same, step=1)
    assert low["gdi"] < CAL["tau"] and low["flagged"] is False and low["gate"] == "allow"
    assert low["weights"] == CAL["weights"] and low["tau"] == CAL["tau"]  # geladene Gewichte
    high = m.observe_gdi("alpha alpha", "beta beta", embed_fn=_emb_same, step=2)
    assert high["gdi"] > CAL["tau"] and high["flagged"] is True and high["gate"] == "ask"


def test_observe_gdi_defaults_ohne_kalibrierung():
    m = bm.BiasDriftMonitor(baseline={}, tau=0.5)  # kein gdi_weights/gdi_tau
    r = m.observe_gdi("a", "b", embed_fn=_emb_same)
    assert r["weights"] == {k: bm.DEFAULT_WEIGHTS[k] for k in ("sem", "lex", "struct", "dist")}
    assert r["tau"] == 0.5  # Fallback auf self.tau


# --------------------------------------------------------- lifecycle_runner


def test_lifecycle_default_gdi_aus_identisch(tmp_path, monkeypatch):
    """Default (`gdi=False`) ⇒ exakt altes JSD-Verhalten (keine GDI-Keys)."""
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    common = dict(
        classify_fn=_classify("non-write"),
        tier3_dir=tmp_path / "t",
    )
    monkeypatch.setenv("LIFECYCLE_DRIFT_REFERENCE", str(tmp_path / "ref_a.json"))
    a = lr.run_cycle("Q", "F", "F", structured_dir=tmp_path / "sa", **common)
    monkeypatch.setenv("LIFECYCLE_DRIFT_REFERENCE", str(tmp_path / "ref_b.json"))
    b = lr.run_cycle("Q", "F", "F", gdi=False, structured_dir=tmp_path / "sb", **common)
    assert a["results"]["Wissen+"] == b["results"]["Wissen+"]
    assert "gdi" not in a["results"]["Wissen+"]


def test_lifecycle_gdi_an_nutzt_kalibriertes_tau(tmp_path, monkeypatch):
    """Mit GDI an greift das **kalibrierte** τ (hier 0.24) im Stufe-8-Gate."""
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setenv("LIFECYCLE_DRIFT_REFERENCE", str(tmp_path / "ref.json"))
    w = lr.run_cycle(
        "Q",
        "alpha alpha",
        "c",
        classify_fn=_classify("non-write"),
        structured_dir=tmp_path / "s",
        tier3_dir=tmp_path / "t",
        gdi=True,
        embed_fn=_emb_same,
        gdi_prev_text="beta beta",
        gdi_calibration=CAL,
    )["results"]["Wissen+"]
    assert w["reference"] == "gdi"
    assert w["tau"] == CAL["tau"]
    assert w["gdi"] > CAL["tau"] and w["gate"] == "ask" and w["revised"] is False


def test_lifecycle_gdi_fallbacks_jsd(tmp_path, monkeypatch):
    """Fehlt eine GDI-Voraussetzung ⇒ JSD-Fallback (kein GDI-Gate, kein Crash)."""
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    base = dict(classify_fn=_classify("non-write"))

    # (a) gdi=True, aber kein embed_fn
    monkeypatch.setenv("LIFECYCLE_DRIFT_REFERENCE", str(tmp_path / "ra.json"))
    a = lr.run_cycle("Q", "F", "F", structured_dir=tmp_path / "a", tier3_dir=tmp_path / "ta", gdi=True, **base)
    assert "gdi" not in a["results"]["Wissen+"]

    # (b) gdi=True + embed_fn, aber kein Referenztext
    monkeypatch.setenv("LIFECYCLE_DRIFT_REFERENCE", str(tmp_path / "rb.json"))
    b = lr.run_cycle(
        "Q",
        "F",
        "F",
        structured_dir=tmp_path / "b",
        tier3_dir=tmp_path / "tb",
        gdi=True,
        embed_fn=_emb_same,
        **base,
    )
    assert "gdi" not in b["results"]["Wissen+"]

    # (c) gdi=True + embed_fn + Referenztext, aber keine ladbare Kalibrierung
    monkeypatch.setattr(bm, "load_calibration", lambda path=None: None)
    monkeypatch.setenv("LIFECYCLE_DRIFT_REFERENCE", str(tmp_path / "rc.json"))
    c = lr.run_cycle(
        "Q",
        "F",
        "F",
        structured_dir=tmp_path / "c",
        tier3_dir=tmp_path / "tc",
        gdi=True,
        embed_fn=_emb_same,
        gdi_prev_text="x",
        **base,
    )
    assert "gdi" not in c["results"]["Wissen+"]
