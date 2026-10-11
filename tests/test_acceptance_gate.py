"""Tests für das SAGE-basierte per-Item Acceptance-Gate.

Quelle: SAGE arXiv:2609.36043; AGENTS.md §9.1d/§6. Kein Netz, kein Fake:
reine, deterministische Standardbibliothek-Logik (`math`, `random`).
"""

import acceptance_gate as ag
import pytest


# ------------------------------------------------------------- per_item_compare
def test_per_item_compare_zaehlt_siege_niederlagen_ties():
    base = [True, True, False, False, True]
    cand = [True, False, False, True, False]
    res = ag.per_item_compare(base, cand)
    # Index 0: T/T = tie, 1: T/F = loss, 2: F/F = tie, 3: F/T = win, 4: T/F = loss
    assert (res["wins"], res["losses"], res["ties"]) == (1, 2, 2)
    assert res["n"] == 5
    assert res["pairs"] == [
        (0, True, True),
        (1, True, False),
        (2, False, False),
        (3, False, True),
        (4, True, False),
    ]


def test_per_item_compare_koerziert_auf_bool():
    """Nicht-boolesche Wahrheitswerte werden wie bool behandelt (keine Logikänderung)."""
    res = ag.per_item_compare([0, 1], [1, 1])
    assert (res["wins"], res["losses"], res["ties"]) == (1, 0, 1)


def test_per_item_compare_ungleiche_laenge_wirft():
    with pytest.raises(ValueError, match="equal length"):
        ag.per_item_compare([True], [True, False])


# ---------------------------------------------------------------- sign_test_p
def test_sign_test_p_ohne_entschiedene_paare_ist_eins():
    assert ag.sign_test_p(0, 0) == 1.0


def test_sign_test_p_fuenf_siege_null_niederlagen():
    assert ag.sign_test_p(5, 0) == pytest.approx(1 / 32)


def test_sign_test_p_ein_sieg_eine_niederlage():
    # tail = C(2,1) + C(2,2) = 3; p = 3/4
    assert ag.sign_test_p(1, 1) == pytest.approx(0.75)


# ----------------------------------------------------------- bootstrap_delta_ci
def test_bootstrap_delta_deterministisch_und_delta_korrekt():
    base = [False] * 200
    cand = [True] * 40 + [False] * 160
    a = ag.bootstrap_delta_ci(base, cand, n_resamples=500, seed=7)
    b = ag.bootstrap_delta_ci(base, cand, n_resamples=500, seed=7)
    assert a == b  # gleicher Seed ⇒ identisches Ergebnis
    assert a["delta"] == pytest.approx(0.2)
    assert a["n_resamples"] == 500 and a["seed"] == 7
    assert a["lo"] <= a["delta"] <= a["hi"]


def test_bootstrap_delta_ci_unterschiedliche_seeds_duerfen_abweichen():
    """Anderer Seed zieht andere Resamples (Verteilung bleibt gültig)."""
    base = [False, True] * 50
    cand = [True, True] * 50
    a = ag.bootstrap_delta_ci(base, cand, n_resamples=200, seed=1)
    b = ag.bootstrap_delta_ci(base, cand, n_resamples=200, seed=2)
    assert a["lo"] <= a["delta"] <= a["hi"]
    assert b["lo"] <= b["delta"] <= b["hi"]


def test_bootstrap_delta_ci_leer_oder_ungleich_wirft():
    with pytest.raises(ValueError, match="non-empty and equal length"):
        ag.bootstrap_delta_ci([], [])
    with pytest.raises(ValueError, match="non-empty and equal length"):
        ag.bootstrap_delta_ci([True], [True, False])


# --------------------------------------------------------------------- evaluate
def _items(n, hits):
    return [i < hits for i in range(n)]


def test_evaluate_accept_klarer_gewinn():
    res = ag.evaluate(_items(200, 8), _items(200, 40), n_resamples=500, seed=0)
    assert res["decision"] == "accept"
    assert res["p"] <= 0.05
    assert res["compare"]["wins"] == 32 and res["compare"]["losses"] == 0
    assert res["delta"] == pytest.approx(0.16)
    assert res["ci"][0] <= res["delta"] <= res["ci"][1]
    assert res["alpha"] == 0.05


def test_evaluate_reject_klarer_verlust():
    """Reject-Zweig bei Default-alpha erreichbar (symmetrischer einseitiger Test):
    klarer Nachteil base 40/200 -> cand 8/200 (losses=32, wins=0)."""
    res = ag.evaluate(_items(200, 40), _items(200, 8), n_resamples=500, seed=0)
    assert res["decision"] == "reject"
    assert res["p_loss"] <= 0.05 and res["p_win"] > 0.05
    assert res["compare"]["losses"] == 32 and res["compare"]["wins"] == 0
    assert res["delta"] == pytest.approx(-0.16)
    assert res["ci"][0] <= res["delta"] <= res["ci"][1]


def test_evaluate_abstain_trotz_verlust_bei_strengem_alpha():
    """Gegenprobe zum reject-Zweig: bei Default-alpha ⇒ abstain (kein Fehlschluss)."""
    res = ag.evaluate([True], [False], n_resamples=100, seed=0)
    assert res["decision"] == "abstain"
    assert res["compare"]["losses"] == 1


def test_evaluate_abstain_bei_gleichstand():
    res = ag.evaluate(_items(50, 10), _items(50, 10), n_resamples=200, seed=0)
    assert res["decision"] == "abstain"
    assert res["p"] == 1.0
    assert res["delta"] == pytest.approx(0.0)
    assert res["ci"][0] <= res["delta"] <= res["ci"][1]


def test_evaluate_abstain_bei_ein_sieg_ein_verlust():
    res = ag.evaluate([True, False], [False, True], n_resamples=200, seed=0)
    assert res["decision"] == "abstain"
    assert res["p"] == pytest.approx(0.75)
    assert res["compare"]["wins"] == 1 and res["compare"]["losses"] == 1
