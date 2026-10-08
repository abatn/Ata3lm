"""GDI (Goal Drift Index) – Gl. 5–16 der Quelle arXiv:2603.06333.

Rein lokal, echte handgerechnete Fälle (kein Fake): `data/memory/bias_monitor.py`.

Quelle (Belegt): arXiv:2603.06333 (SAHOO, ICLR-2026-Workshop), Appendix B
Gl. 5–16; in `AGENTS.md` §9.1c zitiert. Default-Gewichte = Auftrag (Haupttext).
"""

import math

import bias_monitor as bm
import pytest

# ------------------------------------------------------------------ Gl. 5–8


def test_semantic_drift_cos_eins_ist_null():
    # cos = 1 ⇒ Δ_sem = 0; ε=1e-12 lässt den Wert ~1e-12 statt exakt 0.
    assert bm.semantic_drift([1.0, 0.0], [1.0, 0.0]) == pytest.approx(0.0, abs=1e-9)


def test_semantic_drift_orthogonal_ist_halb():
    assert bm.semantic_drift([1.0, 0.0], [0.0, 1.0]) == pytest.approx(0.5)


def test_semantic_drift_gegenpol_ist_eins():
    assert bm.semantic_drift([1.0, 0.0], [-1.0, 0.0]) == pytest.approx(1.0)


def test_semantic_drift_nullvektor_ist_halb():
    # ||0|| = 0 ⇒ ê = 0 ⇒ s_cos = 0 ⇒ Δ_sem = 0.5 (Gl. 5/6 mit ε).
    assert bm.semantic_drift([0.0, 0.0], [1.0, 0.0]) == pytest.approx(0.5)


# -------------------------------------------------------------------- Gl. 9


def test_lexical_drift_identisch_ist_null():
    p = {"a": 1.0, "b": 3.0}
    assert bm.lexical_drift(p, p) == pytest.approx(0.0)
    assert bm.lexical_drift(["a", "b", "a"], ["a", "b", "a"]) == pytest.approx(0.0)


def test_lexical_drift_disjunkt_ist_eins():
    assert bm.lexical_drift({"a": 1.0}, {"b": 1.0}) == pytest.approx(1.0)
    assert bm.lexical_drift(["a"], ["b"]) == pytest.approx(1.0)


# ------------------------------------------------------------------- Gl. 10


def test_structural_drift_identisch_ist_null():
    s = {"a": 1.0, "b": 2.0}
    assert bm.structural_drift(s, s) == pytest.approx(0.0)


def test_structural_drift_betrag_groesser_gleich_ist_gecappt():
    # |1 − 3| / (1 + ε) > 1 ⇒ min(1, ·) = 1.
    assert bm.structural_drift({"a": 1.0}, {"a": 3.0}) == pytest.approx(1.0)


def test_structural_drift_fehlendes_feature():
    # b fehlt in s0 ⇒ s0_b = 0 ⇒ Beitrag = min(1, 1/ε) = 1; K = 2 ⇒ 0.5.
    assert bm.structural_drift({"a": 1.0}, {"a": 1.0, "b": 1.0}) == pytest.approx(0.5)


def test_structural_drift_leer_ist_null():
    assert bm.structural_drift({}, {}) == 0.0


# ------------------------------------------------------------------- Gl. 11


def test_distributional_drift_identisch_ist_null():
    assert bm.distributional_drift([1.0, 2.0, 3.0], [1.0, 2.0, 3.0]) == pytest.approx(0.0)


def test_distributional_drift_verschoben():
    # sortiert: (0,1,2) vs (1,2,3) ⇒ mean(|1|,|1|,|1|) = 1.
    assert bm.distributional_drift([0.0, 1.0, 2.0], [1.0, 2.0, 3.0]) == pytest.approx(1.0)


def test_distributional_drift_leer_ist_null():
    assert bm.distributional_drift([], []) == 0.0
    assert bm.distributional_drift([], [1.0]) == 0.0


# -------------------------------------------------------------- Gl. 12/13


def test_gdi_default_gewichte_summe_eins():
    assert abs(sum(bm.DEFAULT_WEIGHTS.values()) - 1.0) < 1e-12


def test_gdi_default_gewichte_erwartungswert():
    # 0.38*1 + 0.12*2 + 0.21*3 + 0.29*4 = 0.38+0.24+0.63+1.16 = 2.41
    assert bm.gdi(1.0, 2.0, 3.0, 4.0) == pytest.approx(2.41)


def test_gdi_bekannte_gewichte():
    w = {"sem": 0.5, "lex": 0.5, "struct": 0.0, "dist": 0.0}
    assert bm.gdi(1.0, 3.0, 9.0, 9.0, weights=w) == pytest.approx(2.0)


def test_gdi_fehlende_gewichte_wirft():
    with pytest.raises(ValueError, match="fehlen"):
        bm.gdi(0.0, 0.0, 0.0, 0.0, weights={"sem": 0.5, "lex": 0.5})


def test_gdi_gewicht_ausserhalb_bereich_wirft():
    with pytest.raises(ValueError, match=r"\[0, 1\]"):
        bm.gdi(0.0, 0.0, 0.0, 0.0, weights={"sem": 1.5, "lex": 0.0, "struct": 0.0, "dist": -0.5})


def test_gdi_summe_ungleich_eins_wirft():
    with pytest.raises(ValueError, match="summieren"):
        bm.gdi(0.0, 0.0, 0.0, 0.0, weights={"sem": 0.5, "lex": 0.0, "struct": 0.0, "dist": 0.0})


# ------------------------------------------------------------------- AUC


def test_auc_ohne_positive_klasse_ist_halb():
    assert bm._auc([0.1, 0.2, 0.3], [0, 0, 0]) == 0.5


def test_auc_perfekt_und_invertiert():
    assert bm._auc([0.9, 0.1], [1, 0]) == pytest.approx(1.0)
    assert bm._auc([0.1, 0.9], [1, 0]) == pytest.approx(0.0)


def test_auc_tie_zaehlt_halb():
    assert bm._auc([1.0, 1.0], [1, 0]) == pytest.approx(0.5)


def test_auc_tie_bei_mehreren():
    # 2 positive, 1 negativer, alle gleich ⇒ jeder Paar-Vergleich Tie ⇒ 0.5.
    assert bm._auc([0.5, 0.5, 0.5], [1, 0, 1]) == pytest.approx(0.5)


# -------------------------------------------------------------- Gl. 14


def test_calibrate_weights_langenfehler():
    with pytest.raises(ValueError, match="gleich lang"):
        bm.calibrate_weights([{"sem": 1.0, "lex": 0.0, "struct": 0.0, "dist": 0.0}], [])


def test_calibrate_weights_gegebenes_gitter_waehlt_sem():
    scores = [
        {"sem": 0.9, "lex": 0.0, "struct": 0.0, "dist": 0.0},
        {"sem": 0.8, "lex": 0.0, "struct": 0.0, "dist": 0.0},
        {"sem": 0.2, "lex": 0.0, "struct": 0.0, "dist": 0.0},
        {"sem": 0.1, "lex": 0.0, "struct": 0.0, "dist": 0.0},
    ]
    labels = [1, 1, 0, 0]
    grid = [
        {"sem": 0.0, "lex": 0.0, "struct": 0.0, "dist": 1.0},  # AUC 0.5 (alle 0)
        {"sem": 1.0, "lex": 0.0, "struct": 0.0, "dist": 0.0},  # AUC 1.0
    ]
    out = bm.calibrate_weights(scores, labels, grid=grid)
    assert out["auc"] == pytest.approx(1.0)
    assert out["weights"] == {"sem": 1.0, "lex": 0.0, "struct": 0.0, "dist": 0.0}


def test_calibrate_weights_default_gitter_trennt_sem():
    scores = [
        {"sem": 0.9, "lex": 0.5, "struct": 0.5, "dist": 0.5},
        {"sem": 0.8, "lex": 0.5, "struct": 0.5, "dist": 0.5},
        {"sem": 0.2, "lex": 0.5, "struct": 0.5, "dist": 0.5},
        {"sem": 0.1, "lex": 0.5, "struct": 0.5, "dist": 0.5},
    ]
    out = bm.calibrate_weights(scores, [1, 1, 0, 0])
    assert out["auc"] == pytest.approx(1.0)
    assert sum(out["weights"].values()) == pytest.approx(1.0)


def test_simplex_grid_summe_eins():
    grid = bm._simplex_grid(step=0.25)
    assert grid
    assert all(abs(sum(w.values()) - 1.0) < 1e-9 for w in grid)


# -------------------------------------------------------------- Gl. 15


def test_calibrate_tau_langenfehler():
    with pytest.raises(ValueError, match="gleich lang"):
        bm.calibrate_tau([1.0], [])


def test_calibrate_tau_leer():
    assert bm.calibrate_tau([], []) == {"tau": 0.0, "f1": 0.0}


def test_calibrate_tau_f1_maximum():
    out = bm.calibrate_tau([0.1, 0.4, 0.6, 0.9], [0, 0, 1, 1])
    assert out["tau"] == pytest.approx(0.4)
    assert out["f1"] == pytest.approx(1.0)


def test_calibrate_tau_leerer_nenner():
    # Keine positiven Vorhersagen/Labels ⇒ F1 = 0.0.
    assert bm.calibrate_tau([0.0, 0.0], [0, 0]) == {"tau": 0.0, "f1": 0.0}


# -------------------------------------------------------------- Gl. 16


def test_bootstrap_ci_konstant():
    out = bm.bootstrap_ci([3.0] * 10, B=200)
    assert out["lo"] == pytest.approx(3.0)
    assert out["hi"] == pytest.approx(3.0)


def test_bootstrap_ci_b_eins_deckt_quantil_singularitaet():
    # B=1 ⇒ 1 Replikat ⇒ _quantile n==1.
    out = bm.bootstrap_ci([1.0, 2.0, 3.0], B=1)
    assert out["lo"] == out["hi"]


def test_bootstrap_ci_bereich():
    out = bm.bootstrap_ci(list(range(10)), B=500)
    assert math.isfinite(out["lo"]) and math.isfinite(out["hi"])
    assert 0.0 <= out["lo"] <= out["hi"] <= 9.0


def test_bootstrap_ci_leer_wirft():
    with pytest.raises(ValueError, match="leer"):
        bm.bootstrap_ci([])
