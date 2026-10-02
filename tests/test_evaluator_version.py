"""Red-Queen-Ko-Evolution (data/memory/evaluator_version.py).

Offen 1: ε-Best-Belief (BB_ε = I⁻¹_ε(1+S, 1+F)) portiert – Gate nutzt BB statt
Trefferquote. Offen 2: echte HF-Anker (CRAVE/IMO-GradingBench) über `load_anchor`
(fake Loader im Test, kein Netz). Offen 3: Gate im Replacement-Pfad; Modul bleibt
additiv (kein Loop-Import). Quellen: arXiv:2606.26294 §3.1/§3.5,
kingkillery/src/rqgm/beta.py.
"""
import math

import pytest

import evaluator_version as ev


def _anchor():
    """10 Items, truth = feature >= 0.7 (>= min_anchor 5)."""
    return ev.GroundTruthAnchor(items=list(ev.ANCHOR_ITEMS), source="test")


# ------------------------------------------------------- Offen 1: Beta / BB_ε
def test_beta_funktionen_grenzfaelle():
    assert ev.regularized_incomplete_beta(0.0, 2, 3) == 0.0
    assert ev.regularized_incomplete_beta(1.0, 2, 3) == 1.0
    assert ev.beta_ppf(0.0, 2, 3) == 0.0
    assert ev.beta_ppf(1.0, 2, 3) == 1.0


def test_beta_regulisiert_beide_regionen_und_monotonie():
    # x < (a+1)/(a+b+2) -> erste Region; sonst zweite
    lo = ev.regularized_incomplete_beta(0.1, 2, 3)
    hi = ev.regularized_incomplete_beta(0.9, 2, 3)
    assert 0.0 < lo < hi < 1.0
    assert ev.beta_ppf(0.5, 2, 3) == pytest.approx(0.3857, abs=2e-3)


def test_best_belief_semantik_und_gegenprobe_scipy():
    assert ev.best_belief(0, 0, 0.05) == pytest.approx(0.05, abs=1e-9)
    assert ev.best_belief(10, 0) > ev.best_belief(5, 5) > ev.best_belief(0, 10)
    assert ev.posterior_mean(0, 0) == 0.5
    from scipy.special import betaincinv
    for s, f in [(0, 0), (4, 6), (10, 0), (3, 9)]:
        assert ev.best_belief(s, f) == pytest.approx(float(betaincinv(1 + s, 1 + f, 0.05)), abs=1e-6)


# ------------------------------------------------------- Anker + Evaluatoren
def test_anker_outcomes_accuracy_und_leer():
    a = _anchor()
    assert a.n() == 10
    s, f = a.outcomes(ev.make_grader(0.0))
    assert (s, f) == (4, 6)
    assert a.accuracy(ev.make_grader(0.7)) == 1.0
    leer = ev.GroundTruthAnchor()
    assert leer.n() == 0 and leer.accuracy(ev.make_grader(0.0)) == 0.0


def test_evaluator_version_kennzahlen():
    e = ev.EvaluatorVersion("", ev.make_grader(0.5), threshold=0.5)
    assert e.anchor_outcomes == 0 and e.anchor_accuracy == 0.0   # vor register
    ev.RedQueen(_anchor()).register(e)
    assert e.anchor_outcomes == 10 and e.anchor_accuracy == 0.7
    assert 0.0 < e.best_belief() < 1.0


def test_feature_quantiles_und_leerer_anker():
    assert ev.feature_quantiles(_anchor()) == [0.4, 0.6, 0.7]
    assert ev.feature_quantiles(ev.GroundTruthAnchor()) == [0.0, 0.0, 0.0]


# ------------------------------------------------------- ε-BB-Gate (Checkpoint)
def test_checkpoint_initial_setzt_evaluator_v1():
    rq = ev.RedQueen(_anchor())
    r = rq.checkpoint(ev.EvaluatorVersion("", ev.make_grader(0.0)))
    assert r["promoted"] is True and r["version"] == "evaluator_v1"
    assert r["gate"] == "allow" and "best_belief" in r


def test_checkpoint_verweigert_zu_kleinen_anker():
    klein = ev.GroundTruthAnchor(items=[{"id": "a", "feature": 0.2, "truth": False}])
    rq = ev.RedQueen(klein)
    rq.checkpoint(ev.EvaluatorVersion("", ev.make_grader(0.0)))
    r = rq.checkpoint(ev.EvaluatorVersion("", ev.make_grader(0.5)), approved=True)
    assert r["promoted"] is False and r["gate"] == "ask"
    assert "Anker zu klein" in r["reason"]


def test_checkpoint_besser_ohne_approved_ist_pending():
    rq = ev.RedQueen(_anchor())
    rq.checkpoint(ev.EvaluatorVersion("", ev.make_grader(0.0)))          # (S4,F6)
    r = rq.checkpoint(ev.EvaluatorVersion("", ev.make_grader(0.7)))      # (S10,F0)
    assert r["promoted"] is False and r["pending"] is True and r["gate"] == "ask"
    assert r["candidate_best_belief"] > r["incumbent_best_belief"]
    assert rq.current.version == "evaluator_v1"                          # §9


def test_checkpoint_besser_mit_approved_promoted_und_erasure():
    rq = ev.RedQueen(_anchor())
    rq.checkpoint(ev.EvaluatorVersion("", ev.make_grader(0.0)))          # v1
    rq.record("v1-item", 0.1)
    rq.record("gt", 0.0, evaluator_independent=True)
    r = rq.checkpoint(ev.EvaluatorVersion("", ev.make_grader(0.7)), approved=True)
    assert r["promoted"] is True and r["version"] == "evaluator_v2"
    assert r["replaced"] == "evaluator_v1" and r["erased_records"] == 1
    assert [rec["item"] for rec in rq.archive] == ["gt"]


def test_checkpoint_gleichstand_behaelt_incumbent():
    rq = ev.RedQueen(_anchor())
    rq.checkpoint(ev.EvaluatorVersion("", ev.make_grader(0.5)))          # (S7,F3)
    # 0.45 akzeptiert dieselben Items wie 0.5 -> identische Bilanz -> Gleichstand
    r = rq.checkpoint(ev.EvaluatorVersion("", ev.make_grader(0.45)), approved=True)
    assert r["promoted"] is False and r["gate"] == "deny"
    assert "nicht strikt besser" in r["reason"]
    assert rq.current.version == "evaluator_v1"


def test_selective_erasure_behaelt_andere_evaluatoren():
    rq = ev.RedQueen(_anchor())
    rq.checkpoint(ev.EvaluatorVersion("", ev.make_grader(0.0)))
    rq.archive.append({"evaluator": "evaluator_vX", "item": "fremd",
                       "score": 0.0, "evaluator_independent": False})
    rq.record("v1-item", 0.5)
    rq.record("gt", 0.0, evaluator_independent=True)
    assert rq.selective_erasure("evaluator_v1") == 1
    assert {r["item"] for r in rq.archive} == {"fremd", "gt"}


def test_record_ohne_und_mit_evaluator():
    rq = ev.RedQueen(_anchor())
    assert rq.record("x", 0.5) == {"ok": False, "reason": "kein aktiver Evaluator"}
    rq.checkpoint(ev.EvaluatorVersion("", ev.make_grader(0.0)))
    r = rq.record("x", 0.5)
    assert r["ok"] is True and r["record"]["evaluator"] == "evaluator_v1"


def test_report_mit_und_ohne_evaluator():
    leer = ev.RedQueen(_anchor()).report()
    assert leer["current"] is None and leer["current_best_belief"] is None
    assert leer["evaluator_ceiling_avoided"] is False
    rq = ev.RedQueen(_anchor())
    rq.checkpoint(ev.EvaluatorVersion("", ev.make_grader(0.0)))
    rq.checkpoint(ev.EvaluatorVersion("", ev.make_grader(0.7)), approved=True)
    rep = rq.report()
    assert rep["current"] == "evaluator_v2" and rep["evaluator_ceiling_avoided"] is True
    assert [v["version"] for v in rep["versions"]] == ["evaluator_v1", "evaluator_v2"]


# ------------------------------------------------------- Offen 2: echte Anker
class _FakeDS(list):
    pass


def _fake_loader_grading(ds_id, split):
    assert ds_id == ev.IMO_GRADINGBENCH_ID and split == "train"
    return _FakeDS([{"Grading ID": "GB-1", "Points": 7, "Response": "x" * 100},
                    {"Grading ID": "GB-2", "Points": 0, "Response": "x" * 10}])


def _fake_loader_coding(ds_id, split):
    assert ds_id == ev.CRAVE_ID and split == "test"
    return _FakeDS([{"pr_number": 1, "label": "APPROVE", "patch": "x" * 50},
                    {"pr_number": 2, "label": "REQUEST_CHANGES", "patch": "x"}])


def test_load_anchor_grading_und_coding():
    g = ev.load_anchor("grading", load_dataset_fn=_fake_loader_grading)
    assert g.source == f"HF:{ev.IMO_GRADINGBENCH_ID}" and g.n() == 2
    assert g.items[0]["truth"] is True and g.items[1]["truth"] is False
    c = ev.load_anchor("coding", load_dataset_fn=_fake_loader_coding)
    assert c.source == f"HF:{ev.CRAVE_ID}"
    assert c.items[0]["truth"] is True and c.items[1]["truth"] is False


def test_load_anchor_unbekannter_typ():
    with pytest.raises(ValueError):
        ev.load_anchor("paper-writing")


def test_load_anchor_nutzt_datasets_loader(monkeypatch):
    import datasets
    monkeypatch.setattr(datasets, "load_dataset", _fake_loader_grading)
    a = ev.load_anchor("grading", limit=1)
    assert a.n() == 1


# ------------------------------------------------------- Simulationen
def test_simulate_3_evaluatoren_steigende_schwierigkeit():
    out = ev.simulate_3_evaluators()
    assert out["epoch_1"]["version"] == "evaluator_v1"
    assert out["epoch_2_pending"]["pending"] is True
    assert out["epoch_2"]["version"] == "evaluator_v2"
    assert out["epoch_3"]["version"] == "evaluator_v3"
    bbs = [v["best_belief"] for v in out["report"]["versions"]]
    assert bbs == sorted(bbs) and bbs[0] < bbs[-1]
    assert out["report"]["evaluator_ceiling_avoided"] is True
    assert {r["item"] for r in out["archive"]} == {"gt-unit-1", "gt-unit-2"}
    assert out["paper_gain_ground_truth"] == 0.09
    assert out["checkpoints"][:3] == [16, 32, 64]
    assert out["paper_params"]["min_anchor"] == 5


def test_simulate_real_anchor_misst_eigene_zahl():
    out = ev.simulate_real_anchor("grading", load_dataset_fn=_fake_loader_grading)
    assert out["anchor"] == f"HF:{ev.IMO_GRADINGBENCH_ID}" and out["n_items"] == 2
    assert out["final_accuracy"] is not None
    assert out["measured_gain"] == pytest.approx(
        out["final_accuracy"] - out["baseline_accuracy_all_accept"])
    assert "eigene Messung" in out["note"]


def test_simulate_real_anchor_ohne_items():
    leer = _FakeDS([])
    out = ev.simulate_real_anchor("grading", load_dataset_fn=lambda i, split: leer)
    assert out["n_items"] == 0 and out["final_accuracy"] == 0.0
    assert out["measured_gain"] == 0.0          # leerer Anker: kein Gewinn


def test_power_of_two_checkpoints_rho2():
    assert ev.power_of_two_checkpoints(64) == [16, 32, 64]
    assert ev.power_of_two_checkpoints(8) == []
    assert ev.power_of_two_checkpoints(20, start=2, rho=3) == [2, 6, 18]


def test_paper_parameter_dokumentiert():
    """Primärquelle (PDF Tab. 3+4), geprüft 2026-10-02."""
    assert ev.EPS_BEST_BELIEF == 0.05 and ev.MIN_ANCHOR == 5
    assert ev.CHECKPOINT_RHO == 2 and ev.UCB_AIR_ALPHA == 0.6
    assert ev.PAPER_TOTAL_EVALS == 12288
    assert ev.PAPER_TRAIN_SAMPLES_PER_NODE == 3
    assert ev.PAPER_SPLITS == (10, 49, 166)
    assert ev.PAPER_BUDGET_USD == {"expand": 25, "train": 8, "val": 25}
    assert ev.PAPER_BUDGET_TIME_S == {"expand": 1200, "train": 900, "val": 1200}
    assert ev.CRAVE_ID == "TuringEnterprises/CRAVE"
    assert ev.IMO_GRADINGBENCH_ID == "Hwilner/imo-gradingbench"


def test_betacf_und_ppf_ohne_abbruch():
    """Deckt die Schleifen-Enden ohne break (max_iter=1, eps=0) ab."""
    assert ev._betacf(2.0, 3.0, 0.4, max_iter=1, eps=0.0) > 0.0
    assert ev.beta_ppf(0.5, 2.0, 3.0, tol=0.0, max_iter=1) > 0.0
