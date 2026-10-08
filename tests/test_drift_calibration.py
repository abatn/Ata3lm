"""Kalibrier-Harness für den Drift-Schwellwert – Gl. 14–16 (arXiv:2603.06333).

Rein lokal/deterministisch: `embed_fn`/`grader_fn` sind **Stubs** (Guardrail 7);
der echte Kalibrierlauf ist separat. Die Mathematik stammt unverändert aus
`bias_monitor` (Gl. 8–16).
"""

import drift_calibration as dc
import pytest


# --------------------------------------------------------------------------- #
# Deterministische Stubs (kein Netz, kein LLM)
# --------------------------------------------------------------------------- #
def _embed(text):
    """Deterministisches Pseudo-Embedding (feste Dimension)."""
    return [float(text.count(ch)) for ch in "abcxyz"]


def _verdict_grader(drift_pairs):
    """Externes Stub-Signal: False (Drift) für Paare in `drift_pairs`, sonst True."""
    pairs = set(drift_pairs)
    return lambda prev, cur, reference: (prev, cur) not in pairs


# --------------------------------------------------------------------------- #
# signal_vector (Gl. 8–11)
# --------------------------------------------------------------------------- #
def test_signal_vector_wertebereich_0_1():
    prev = "alpha beta gamma\n\n- punkt eins\n- punkt zwei\n```code```"
    cur = "alpha delta\n- punkt\n\n```x```"
    sig = dc.signal_vector(prev, cur, embed_fn=_embed)
    assert set(sig) == {"semantic", "lexical", "structural", "distributional"}
    for name, value in sig.items():
        assert 0.0 <= value <= 1.0, f"{name} außerhalb [0,1]: {value}"


def test_signal_vector_identisch_ist_null():
    text = "alpha beta\n- eins\n- zwei\n```block```"
    sig = dc.signal_vector(text, text, embed_fn=_embed)
    assert sig["semantic"] == pytest.approx(0.0, abs=1e-9)
    assert sig["lexical"] == pytest.approx(0.0)
    assert sig["structural"] == pytest.approx(0.0)
    assert sig["distributional"] == pytest.approx(0.0)


def test_signal_vector_leer():
    # Nullvektoren ⇒ s_cos = 0 ⇒ Δ_sem = 0.5 (Gl. 5–8); lex/struct/dist = 0.
    sig = dc.signal_vector("", "", embed_fn=_embed)
    assert sig == {"semantic": 0.5, "lexical": 0.0, "structural": 0.0, "distributional": 0.0}


def test_structural_features_zaehlt_alle_vier():
    text = "a b c\nd e\n\n- x\n* y\n1. z\n```\ncode\n```"
    f = dc.structural_features(text)
    assert set(f) == set(dc.STRUCT_KEYS)
    assert f["length"] == float(len(text))
    assert f["lines"] == float(len(text.splitlines()))
    assert f["code_blocks"] == 1.0
    assert f["list_items"] == 3.0


def test_structural_features_ohne_listen():
    f = dc.structural_features("nur eine zeile")
    assert f["list_items"] == 0.0


# --------------------------------------------------------------------------- #
# gdi_of (Gl. 12–13)
# --------------------------------------------------------------------------- #
def test_gdi_of_mit_default_gewichten():
    pairs = (("sem", "semantic"), ("lex", "lexical"), ("struct", "structural"), ("dist", "distributional"))
    sig = dc.signal_vector("aaa", "zzz", embed_fn=_embed)
    expected = sum(dc.bm.DEFAULT_WEIGHTS[k] * sig[v] for k, v in pairs)
    assert dc.gdi_of("aaa", "zzz", embed_fn=_embed) == pytest.approx(expected)


def test_gdi_of_mit_eigenen_gewichten():
    weights = {"sem": 1.0, "lex": 0.0, "struct": 0.0, "dist": 0.0}
    sig = dc.signal_vector("aaa", "zzz", embed_fn=_embed)
    assert sig["semantic"] == pytest.approx(0.5)
    assert dc.gdi_of("aaa", "zzz", embed_fn=_embed, weights=weights) == pytest.approx(sig["semantic"])


# --------------------------------------------------------------------------- #
# Grader-Auflösung (lazy Default ohne echten Aufruf)
# --------------------------------------------------------------------------- #
def test_resolve_grader_injiziert_bleibt_gleich():
    stub = _verdict_grader([])
    assert dc._resolve_grader_fn(stub) is stub


def test_resolve_grader_default_ist_lazy_callable():
    grade = dc._resolve_grader_fn(None)
    assert callable(grade)


# --------------------------------------------------------------------------- #
# collect_samples (Gl. 12–14)
# --------------------------------------------------------------------------- #
def test_collect_samples_laenge_und_labels():
    samples = [
        {"prev": "gleich", "cur": "gleich"},
        {"prev": "aaa", "cur": "zzz", "reference": "ref"},
    ]
    grade = _verdict_grader([("aaa", "zzz")])
    values, labels = dc.collect_samples(samples, embed_fn=_embed, grader_fn=grade)
    assert len(values) == len(samples) == 2
    assert labels == [dc.LABEL_NO_DRIFT, dc.LABEL_DRIFT]
    assert values[0] == pytest.approx(0.0)


def test_collect_samples_grader_bekommt_referenz():
    seen = {}

    def grade(prev, cur, reference):
        seen["ref"] = reference
        return True

    dc.collect_samples([{"prev": "a", "cur": "b", "reference": "R"}], embed_fn=_embed, grader_fn=grade)
    assert seen["ref"] == "R"


# --------------------------------------------------------------------------- #
# calibrate (Gl. 14–16)
# --------------------------------------------------------------------------- #
def _separation_samples():
    quiet = [("alpha beta", "alpha beta"), ("gamma delta", "gamma delta"), ("epsilon zeta", "epsilon zeta")]
    loud = [("alpha alpha\nbeta", "omega omega\nsigma"), ("beta beta\nbeta", "sigma sigma\ntau")]
    samples = [{"prev": p, "cur": c} for p, c in (quiet + loud)]
    return samples, set(loud)


def test_calibrate_gewichte_tau_ci():
    samples, loud = _separation_samples()
    out = dc.calibrate(samples, embed_fn=_embed, grader_fn=_verdict_grader(loud), bootstrap_B=200)
    assert out["n"] == len(samples)
    assert abs(sum(out["weights"].values()) - 1.0) < 1e-9
    assert 0.0 <= out["tau"] <= 1.0
    assert out["ci"]["lo"] <= out["ci"]["hi"]
    assert isinstance(out["note"], str) and out["note"]


def test_calibrate_tau_trennt_konstruiertes_beispiel_sauber():
    samples, loud = _separation_samples()
    out = dc.calibrate(samples, embed_fn=_embed, grader_fn=_verdict_grader(loud), bootstrap_B=200)
    weights = out["weights"]
    values = [dc.gdi_of(s["prev"], s["cur"], embed_fn=_embed, weights=weights) for s in samples]
    positives = [v for s, v in zip(samples, values) if (s["prev"], s["cur"]) in loud]
    negatives = [v for s, v in zip(samples, values) if (s["prev"], s["cur"]) not in loud]
    assert min(positives) > max(negatives)
    assert out["f1"] == pytest.approx(1.0)
    assert all(v > out["tau"] for v in positives)
    assert all(v <= out["tau"] for v in negatives)


def test_calibrate_ohne_samples():
    out = dc.calibrate([], embed_fn=_embed, grader_fn=_verdict_grader([]))
    assert out["n"] == 0
    assert out["tau"] == 0.0
    assert out["ci"] == {"lo": 0.0, "hi": 0.0}
    assert out["weights"] == dc.bm.DEFAULT_WEIGHTS
