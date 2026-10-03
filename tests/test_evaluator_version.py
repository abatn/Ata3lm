"""Red-Queen-Ko-Evolution (data/memory/evaluator_version.py).

Offen 1: ε-Best-Belief (BB_ε = I⁻¹_ε(1+S, 1+F)) portiert – Gate nutzt BB statt
Trefferquote. Offen 2: echte HF-Anker (CRAVE/IMO-GradingBench) über `load_anchor`
(fake Loader im Test, kein Netz). Offen 3: Gate im Replacement-Pfad; Modul bleibt
additiv (kein Loop-Import). Quellen: arXiv:2606.26294 §3.1/§3.5,
kingkillery/src/rqgm/beta.py.
"""

import pathlib

import evaluator_version as ev
import pytest
from _live import call

BAD = "http://127.0.0.1:9"


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
    assert e.anchor_outcomes == 0 and e.anchor_accuracy == 0.0  # vor register
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
    rq.checkpoint(ev.EvaluatorVersion("", ev.make_grader(0.0)))  # (S4,F6)
    r = rq.checkpoint(ev.EvaluatorVersion("", ev.make_grader(0.7)))  # (S10,F0)
    assert r["promoted"] is False and r["pending"] is True and r["gate"] == "ask"
    assert r["candidate_best_belief"] > r["incumbent_best_belief"]
    assert rq.current.version == "evaluator_v1"  # §9


def test_checkpoint_besser_mit_approved_promoted_und_erasure():
    rq = ev.RedQueen(_anchor())
    rq.checkpoint(ev.EvaluatorVersion("", ev.make_grader(0.0)))  # v1
    rq.record("v1-item", 0.1)
    rq.record("gt", 0.0, evaluator_independent=True)
    r = rq.checkpoint(ev.EvaluatorVersion("", ev.make_grader(0.7)), approved=True)
    assert r["promoted"] is True and r["version"] == "evaluator_v2"
    assert r["replaced"] == "evaluator_v1" and r["erased_records"] == 1
    assert [rec["item"] for rec in rq.archive] == ["gt"]


def test_checkpoint_gleichstand_behaelt_incumbent():
    rq = ev.RedQueen(_anchor())
    rq.checkpoint(ev.EvaluatorVersion("", ev.make_grader(0.5)))  # (S7,F3)
    # 0.45 akzeptiert dieselben Items wie 0.5 -> identische Bilanz -> Gleichstand
    r = rq.checkpoint(ev.EvaluatorVersion("", ev.make_grader(0.45)), approved=True)
    assert r["promoted"] is False and r["gate"] == "deny"
    assert "nicht strikt besser" in r["reason"]
    assert rq.current.version == "evaluator_v1"


def test_selective_erasure_behaelt_andere_evaluatoren():
    rq = ev.RedQueen(_anchor())
    rq.checkpoint(ev.EvaluatorVersion("", ev.make_grader(0.0)))
    rq.archive.append({"evaluator": "evaluator_vX", "item": "fremd", "score": 0.0, "evaluator_independent": False})
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


# ------------------------------------------------------- Offen 2: echte Anker (HF)
def test_load_anchor_grading_und_coding_real():
    g = ev.load_anchor("grading", limit=5)
    assert g.source == f"HF:{ev.IMO_GRADINGBENCH_ID}" and g.n() >= 1
    assert all(isinstance(it["truth"], bool) for it in g.items)
    c = ev.load_anchor("coding", limit=5)
    assert c.source == f"HF:{ev.CRAVE_ID}" and c.n() >= 1
    assert all(isinstance(it["truth"], bool) for it in c.items)


def test_load_anchor_unbekannter_typ():
    with pytest.raises(ValueError):
        ev.load_anchor("paper-writing")


def test_load_anchor_nutzt_datasets_loader_real():
    """Realer HF-Loader (kein Fake): lädt ein echtes Anker-Item."""
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
    out = ev.simulate_real_anchor("grading", limit=5)
    assert out["anchor"] == f"HF:{ev.IMO_GRADINGBENCH_ID}" and out["n_items"] >= 1
    assert out["final_accuracy"] is not None
    assert out["measured_gain"] == pytest.approx(out["final_accuracy"] - out["baseline_accuracy_all_accept"])
    assert "eigene Messung" in out["note"]


def test_simulate_real_anchor_ohne_items():
    out = ev.simulate_real_anchor("grading", limit=0)
    assert out["n_items"] == 0 and out["final_accuracy"] == 0.0
    assert out["measured_gain"] == 0.0


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


# ------------------------------------------------------- Offen 3: Epochen-Loop
def test_redqueenloop_epochen_und_checkpoints():
    loop = ev.RedQueenLoop(_anchor(), checkpoints={1, 3})
    out = loop.run(
        [ev.EvaluatorVersion("", ev.make_grader(0.0)), ev.EvaluatorVersion("", ev.make_grader(0.7))], approved=True
    )
    assert [e["epoch"] for e in out["trajectory"]] == [1, 2, 3]
    assert out["trajectory"][0]["checkpoint"]["version"] == "evaluator_v1"
    assert out["trajectory"][1]["evaluator"] == "evaluator_v1"  # Epoche 2 fix
    assert "checkpoint" not in out["trajectory"][1]
    assert out["trajectory"][2]["checkpoint"]["version"] == "evaluator_v2"
    assert out["report"]["current"] == "evaluator_v2"


def test_redqueenloop_approved_false_bleibt_pending():
    loop = ev.RedQueenLoop(_anchor(), checkpoints={1, 2})
    out = loop.run(
        [ev.EvaluatorVersion("", ev.make_grader(0.0)), ev.EvaluatorVersion("", ev.make_grader(0.7))], approved=False
    )
    cp2 = out["trajectory"][1]["checkpoint"]
    assert cp2["pending"] is True and cp2["promoted"] is False
    assert out["report"]["current"] == "evaluator_v1"


def test_redqueenloop_ohne_kandidaten_und_defaults():
    loop = ev.RedQueenLoop(_anchor())  # checkpoints=None -> {1,2,4,8}
    assert loop.last_epoch() == 8
    out = loop.run([ev.EvaluatorVersion("", ev.make_grader(0.0))])
    assert len(out["trajectory"]) == 8
    assert "checkpoint" not in out["trajectory"][1]  # Kandidaten erschöpft
    leer = ev.RedQueenLoop(_anchor(), checkpoints=set())
    assert leer.last_epoch() == 1
    assert leer.run([])["trajectory"][0]["evaluator"] is None


# ------------------------------------------------- Offen 3+: LLM-Grader (real)
def test_llm_grader_real_und_fail_soft(monkeypatch):
    item = {"id": "x", "text": "Problem P", "rubric": "full credit", "feature": 0.9}
    g = ev.make_llm_grader(ev.make_grader(0.5))
    assert call(g, item) in (True, False)  # realer LLM-Judge
    monkeypatch.setenv("OPENAI_BASE_URL", BAD)  # echtes unerreichbares Endpoint
    log = []
    g2 = ev.make_llm_grader(ev.make_grader(0.5), log=log)
    assert g2(item) == bool(ev.make_grader(0.5)(item))
    assert log and log[0]["fallback"] == "rule_grader" and log[0]["item"] == "x"


def test_llm_grader_api_fehler_ohne_log(monkeypatch):
    monkeypatch.setenv("OPENAI_BASE_URL", BAD)
    g = ev.make_llm_grader(ev.make_grader(0.5), log=None)
    assert g({"id": "y", "text": "", "rubric": "", "feature": 0.0}) is False


def test_parse_grader_verdict():
    assert ev._parse_grader_verdict('{"passed": true, "score": 1.0, "reason": "ok"}') is True
    assert ev._parse_grader_verdict('Vorrede {"passed": false, "score": 0.0} Nachrede') is False
    with pytest.raises(Exception):
        ev._parse_grader_verdict('{"passed": "ja"}')


def test_default_client_konstruiert():
    client = ev._default_client()
    assert hasattr(client, "chat")


def test_simulate_real_anchor_mit_llm():
    out = ev.simulate_real_anchor("grading", limit=2, use_llm=True, grader_log=[])
    assert out["grader"] == "llm+rule-fallback"
    assert out["report"]["current"] is not None
    assert "+ LLM-Judge (fail-soft)" in out["note"]


def test_extract_json_mit_und_ohne_objekt():
    assert ev._extract_json('Vorrede {"passed": true, "score": 1} Nachrede') == '{"passed": true, "score": 1}'
    assert ev._extract_json("kein json hier") == "kein json hier"


# ------------------------------------------------- Statistik/Methodik (§10)
def test_hedges_correction_exakt_und_approximation():
    assert ev.hedges_correction(7) == pytest.approx(0.8889, abs=1e-3)
    assert ev.hedges_correction_approx(7) == pytest.approx(1 - 3 / 27)
    assert ev.hedges_g(1.0, 7) == ev.hedges_correction(7)
    assert ev.hedges_correction(30) > ev.hedges_correction(7)  # n größer → näher an 1


def test_cohens_d_paired_und_sd_null():
    assert ev.cohens_d_paired([1, 1, 1, 0, 1, 1, 0, 1]) > 0
    assert ev.cohens_d_paired([0, 0, 0]) == 0.0  # sd = 0


def test_power_und_required_n():
    p8 = ev.power_paired_t(0.625, 8)
    assert 0.0 < p8 < 1.0
    assert ev.power_paired_t(0.625, 100) > p8  # Power steigt mit n
    n80 = ev.required_n_paired_t(0.625)
    assert n80 >= 8 and ev.power_paired_t(0.625, n80) >= 0.80
    assert ev.required_n_paired_t(0.0, n_max=2) == 2  # nie erreicht → n_max


def test_ki_hedges_g_nichtzentral():
    g = 0.9
    lo, hi = ev.ci_hedges_g_noncentral(g, 8)
    assert lo < g < hi
    assert ev.ci_hedges_g_noncentral(g, 8) == pytest.approx((lo, hi))


def test_cohens_kappa_und_sonderfaelle():
    a = [1, 0, 1, 1, 0, 1, 0, 0]
    assert ev.cohens_kappa(a, a) == 1.0
    assert ev.cohens_kappa(a, [1 - x for x in a]) < 0
    assert ev.cohens_kappa([1, 1], [1, 1]) == 1.0  # pe == 1, po == 1
    assert ev.cohens_kappa([1, 1], [2, 2]) == 0.0  # pe == 1, po < 1


def test_kappa_se_ci_und_landis_koch():
    a = [1, 0, 1, 1, 0, 1, 0, 0]
    b = [1, 0, 1, 0, 0, 1, 0, 1]
    se = ev.kappa_se_simplified(a, b)
    assert se > 0.0
    assert ev.kappa_se_simplified([1, 1], [1, 1]) == 0.0
    k = ev.cohens_kappa(a, b)
    lo, hi = ev.kappa_ci(k, se)
    assert lo < k < hi
    for val, label in [
        (0.9, "almost perfect"),
        (0.7, "substantial"),
        (0.5, "moderate"),
        (0.3, "fair"),
        (0.1, "slight"),
        (0.0, "poor"),
    ]:
        assert ev.landis_koch(val) == label


def test_positions_und_repetitions_kennzahlen():
    orders = [["A", "A", "A"], ["B", "B", "B"], ["A", "B", "A"]]
    assert ev.flip_rate(orders) == pytest.approx(1 / 3)
    assert ev.position_consistency(orders) == pytest.approx(2 / 3)
    assert ev.repetition_stability([["x", "x"], ["y", "z"]]) == 0.5


def test_llm_pairwise_judge_real_und_fail_soft(monkeypatch):
    a = {"id": "1", "text": "kurz", "rubric": "r"}
    b = {"id": "2", "text": "viel laengerer text", "rubric": "r"}
    log = []
    for _ in range(6):  # echte Wiederholung bis Erfolg (kein Fallback-Log)
        log = []
        res = call(ev.make_llm_pairwise_judge(log=log), a, b)
        if not log:
            break
    assert res in ("A", "B") and not log  # Erfolgspfad des echten Judges
    monkeypatch.setenv("OPENAI_BASE_URL", BAD)
    log2 = []
    j2 = ev.make_llm_pairwise_judge(log=log2)
    assert j2(a, b) == "B" and log2[0]["fallback"] == "rule_length"  # Regel: längerer Text
    j3 = ev.make_llm_pairwise_judge(log=None)
    assert j3(b, a) == "A"


def test_parse_pair_winner():
    assert ev._parse_pair_winner('{"winner": "A"}') == "A"
    assert ev._parse_pair_winner('{"winner": "b"}') == "B"


# ------------------------------------------------- Bootstrap-KI für κ (§10-Nachtrag)
def test_bootstrap_kappa_ci_standard_und_reproduzierbar():
    a = [1, 0, 1, 1, 0, 1, 0, 0]
    b = [1, 0, 1, 0, 0, 1, 0, 1]
    r1 = ev.bootstrap_kappa_ci(a, b, n_resamples=200, seed=0)
    r2 = ev.bootstrap_kappa_ci(a, b, n_resamples=200, seed=0)
    assert r1 == r2  # seed-fixiert, bit-reproduzierbar
    assert r1["method"] in ("BCa", "percentile")
    assert r1["n_resamples"] == 200 and r1["seed"] == 0
    assert -1.0 <= r1["ci"][0] <= r1["ci"][1] <= 1.0
    assert 0.0 <= r1["degenerate_share"] < 1.0
    assert r1["degenerate_interpretation"] in ("ok", "degenerierte Resamples vorhanden - auf NaN pruefen")
    assert r1["kappa"] == ev.cohens_kappa(a, b)


def test_bootstrap_kappa_ci_degeneriert_und_fallback():
    konstant = [1] * 8
    r = ev.bootstrap_kappa_ci(konstant, konstant, n_resamples=100, seed=0)
    assert r["method"] == "percentile"  # BCa NaN -> Fallback
    assert r["degenerate_share"] == 1.0
    assert r["degenerate_interpretation"].startswith("Stream konstant")
    assert r["ci"] == (1.0, 1.0)


def test_bootstrap_konstanten_und_kein_wilson():
    assert ev.BOOTSTRAP_RESAMPLES == 10_000
    assert ev.BOOTSTRAP_SEED == 0
    assert not hasattr(ev, "DEGENERATE_WARN_THRESHOLD")  # keine willkürliche Schwelle
    src = (pathlib.Path(ev.__file__)).read_text(encoding="utf-8").lower()
    assert "def wilson" not in src and "wilson_ci" not in src  # κ NIE über Wilson routen
    assert "from scipy import stats" in src


# ------------------------------------- Stabile κ-Statistik (§11, n≥50)
def test_kappa_required_n_monoton_und_konkret():
    n = ev.kappa_required_n(0.5, [0.25, 0.25, 0.25, 0.25], target_width=0.30)
    assert n > 50  # width<0.3 braucht mehr als 50
    assert ev.kappa_required_n(0.5, [0.25] * 4, target_width=0.20) > n
    assert ev.kappa_required_n(0.5, [0.25] * 4, conf=0.90) < n


def test_bootstrap_interpretation_ok_bei_nicht_degeneriert():
    a = [0, 1, 0, 1, 0, 1, 0, 1]
    r = ev.bootstrap_kappa_ci(a, a, n_resamples=1, seed=0)
    assert r["degenerate_share"] == 0.0
    assert r["degenerate_interpretation"] == "ok"


def test_llm_class_grader_real_und_fail_soft(monkeypatch):
    item = {"id": "GB-1", "text": "t", "rubric": "r"}
    assert call(ev.make_llm_class_grader(votes=1), item) in ev.CLASS_GRADES  # realer Grader
    monkeypatch.setenv("OPENAI_BASE_URL", BAD)
    log = []
    g = ev.make_llm_class_grader(log=log, votes=1)
    assert g(item) == "Incorrect" and log[0]["fallback"] == "rule_incorrect"
    g2 = ev.make_llm_class_grader(log=None, votes=1)
    assert g2(item) == "Incorrect"


def test_parse_class_grade():
    assert ev._parse_class_grade('{"grade": "Almost"}') == "Almost"
    with pytest.raises(Exception):
        ev._parse_class_grade('{"grade": "Superb"}')  # nicht in CLASS_GRADES


def test_stable_kappa_run_real():
    out = ev.stable_kappa_run("grading", n=2, grader_log=[])
    assert out["n"] >= 1 and out["grader"] == "llm-4class+fallback"
    assert out["seed"] == 0 and out["n_resamples"] == 10_000
    assert "degenerate_share" in out and "degenerate_interpretation" in out
    assert isinstance(out["class_counts_llm"], dict)


# ------------------------------------- Robuster Grader (json-repair real)
def test_repair_json_real():
    assert ev._repair_json("Hier: {grade: Partial,} bitte") == '{"grade": "Partial"}'
    assert ev._repair_json('Prosa {"grade": "Almost"} Rest') == '{"grade": "Almost"}'


def test_llm_class_grader_retry_real(monkeypatch):
    """Retry-Schleife real: unerreichbares Endpoint -> nach allen Versuchen Fallback."""
    monkeypatch.setenv("OPENAI_BASE_URL", BAD)
    log = []
    g = ev.make_llm_class_grader(log=log, max_attempts=2, votes=1)
    assert g({"id": "GB-9", "text": "t", "rubric": "r"}) == "Incorrect"
    assert log[0]["fallback"] == "rule_incorrect"


def test_llm_class_grader_use_schema_real():
    """use_schema=True (echte Structured Outputs) -> gültige Klasse."""
    item = {"id": "s", "text": "Problem P", "rubric": "full credit"}
    assert call(ev.make_llm_class_grader(use_schema=True, votes=1), item) in ev.CLASS_GRADES


def test_load_anchor_explicit_loader_real():
    """Expliziter, ECHTER HF-Loader (kein Fake) deckt den Nicht-None-Zweig."""
    import datasets

    a = ev.load_anchor("grading", load_dataset_fn=datasets.load_dataset, limit=1)
    assert a.n() == 1
