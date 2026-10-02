"""Red-Queen-Ko-Evolution (data/memory/evaluator_version.py).

Quelle: arXiv:2606.26294 (Cambridge/NVIDIA) – Epochen mit fixem Evaluator,
Checkpoint-Ersatz nur bei besserer Ground-Truth-Anker-Genauigkeit, Selective
Erasure; AGENTS.md §9: Wechsel = self_update → nur mit `approved`.
"""
import evaluator_version as ev


def _anchor():
    return ev.GroundTruthAnchor(items=[
        {"id": "a", "quality": 0.2, "truth": False},
        {"id": "b", "quality": 0.8, "truth": True},
    ])


def test_accuracy_und_leerer_anker():
    a = _anchor()
    assert a.accuracy(lambda it: it["quality"] >= 0.5) == 1.0
    assert a.accuracy(lambda it: False) == 0.5          # "b" wird falsch beurteilt
    assert ev.GroundTruthAnchor().accuracy(lambda it: True) == 0.0


def test_checkpoint_initial_setzt_evaluator_v1():
    rq = ev.RedQueen(_anchor())
    r = rq.checkpoint(ev.EvaluatorVersion("", lambda it: True))
    assert r["promoted"] is True and r["version"] == "evaluator_v1"
    assert r["gate"] == "allow" and rq.current.version == "evaluator_v1"


def test_checkpoint_schwaecheren_kandidat_ablehnen():
    rq = ev.RedQueen(_anchor())
    rq.checkpoint(ev.EvaluatorVersion("", lambda it: it["quality"] >= 0.5))      # 1.0
    r = rq.checkpoint(ev.EvaluatorVersion("", lambda it: True), approved=True)   # 0.5
    assert r["promoted"] is False and r["gate"] == "deny"
    assert r["candidate_accuracy"] < r["incumbent_accuracy"]
    assert rq.current.version == "evaluator_v1" and len(rq.versions) == 1


def test_checkpoint_besser_ohne_approved_ist_pending():
    rq = ev.RedQueen(_anchor())
    rq.checkpoint(ev.EvaluatorVersion("", lambda it: False))                     # 0.5
    r = rq.checkpoint(ev.EvaluatorVersion("", lambda it: it["quality"] >= 0.5))  # 1.0
    assert r["promoted"] is False and r["pending"] is True and r["gate"] == "ask"
    assert rq.current.version == "evaluator_v1"          # §9: kein self_update


def test_checkpoint_besser_mit_approved_promoted_und_erasure():
    rq = ev.RedQueen(_anchor())
    rq.checkpoint(ev.EvaluatorVersion("", lambda it: False))     # v1 (0.5)
    rq.record("v1-item", 0.1)                                    # v1-abhängig
    rq.record("gt", 0.0, evaluator_independent=True)             # bleibt
    r = rq.checkpoint(ev.EvaluatorVersion("", lambda it: it["quality"] >= 0.5),
                      approved=True)
    assert r["promoted"] is True and r["version"] == "evaluator_v2"
    assert r["replaced"] == "evaluator_v1" and r["erased_records"] == 1
    assert [rec["item"] for rec in rq.archive] == ["gt"]         # Selective Erasure
    assert rq.current.version == "evaluator_v2"


def test_selective_erasure_behaelt_andere_evaluatoren():
    rq = ev.RedQueen(_anchor())
    rq.checkpoint(ev.EvaluatorVersion("", lambda it: True))      # v1
    rq.archive.append({"evaluator": "evaluator_vX", "item": "fremd",
                       "score": 0.0, "evaluator_independent": False})
    rq.record("v1-item", 0.5)
    rq.record("gt", 0.0, evaluator_independent=True)
    assert rq.selective_erasure("evaluator_v1") == 1
    assert {r["item"] for r in rq.archive} == {"fremd", "gt"}


def test_record_ohne_und_mit_evaluator():
    rq = ev.RedQueen(_anchor())
    assert rq.record("x", 0.5) == {"ok": False, "reason": "kein aktiver Evaluator"}
    rq.checkpoint(ev.EvaluatorVersion("", lambda it: True))
    r = rq.record("x", 0.5)
    assert r["ok"] is True and r["record"]["evaluator"] == "evaluator_v1"


def test_simulate_3_evaluatoren_steigende_schwierigkeit():
    out = ev.simulate_3_evaluators()
    assert out["epoch_1"]["version"] == "evaluator_v1"
    assert out["epoch_2_pending"]["pending"] is True
    assert out["epoch_2"]["version"] == "evaluator_v2"
    assert out["epoch_3"]["version"] == "evaluator_v3"
    accs = [v["accuracy"] for v in out["report"]["versions"]]
    assert accs == sorted(accs) and accs[0] < accs[-1]        # v1 < v2 < v3
    assert out["report"]["evaluator_ceiling_avoided"] is True
    assert {r["item"] for r in out["archive"]} == {"gt-unit-1", "gt-unit-2"}
    assert out["paper_gain_ground_truth"] == 0.09


def test_report_ohne_evaluator():
    rep = ev.RedQueen(_anchor()).report()
    assert rep["current"] is None and rep["versions"] == []
    assert rep["evaluator_ceiling_avoided"] is False
