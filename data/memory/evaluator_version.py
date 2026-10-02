#!/usr/bin/env python3
"""
Red-Queen-Ko-Evolution: versionierte Evaluatoren, ε-Best-Belief-Gate,
Ground-Truth-Anker (echte HuggingFace-Daten).

Quellen (alle HTTP 200, geprüft 2026-10-02):
  - The Red Queen Gödel Machine: Co-Evolving Agents and Their Evaluators,
    arXiv:2606.26294 (Cambridge/NVIDIA/Flower Labs/MBZUAI/Inria, 24.06.2026).
    Aus dem offiziellen PDF wörtlich:
      * Tab. 3: "Total budget per run 12,288 evaluations · Train samples per node
        3 · Best-belief quantile ε = 0.05, five-outcome anchor minimum ·
        Checkpoint schedule power-of-two (ρ = 2) · UCB-Air expansion exponent α = 0.6"
      * Tab. 4: "Polyglot train split 10 items · validation split 49 items ·
        test split 166 items · Expand cap $25, 1,200 s · Train cap $8, 900 s ·
        Validation cap $25, 1,200 s"
      * §3.1/§4: BB_ε = I⁻¹_ε(1 + S_gt, 1 + F_gt); §3.4–3.5: Ersatz nur am
        Checkpoint, strikt besser auf dem Ground-Truth-Anker, ties keep incumbent,
        Selective Erasure der abhängigen Records.
      * §C.4: Anker = Polyglot-Exec-Tests (Coder), CRAVE (Reviewer),
        IMO-GradingBench (Grading); „a proof is accepted only when the epoch's
        frozen grader awards full credit (7 of 7)".
    https://arxiv.org/abs/2606.26294
  - best_belief-Portierung: kingkillery/red-queen-godel-machine
    src/rqgm/beta.py (BB_ε = beta_ppf(ε, 1+S, 1+F)) und src/rqgm/search.py
    (strict ">", ties keep incumbent, min_anchor_outcomes).
    https://github.com/kingkillery/red-queen-godel-machine
  - Echte Anker: https://huggingface.co/datasets/TuringEnterprises/CRAVE
    und https://huggingface.co/datasets/Hwilner/imo-gradingbench
  - Projekt-Gesetz: AGENTS.md §9 (kein self_update ohne `approved`), §9.3.

Lab-Prinzip: Mechanik = Quelle; die Demo-Anker sind Auftrag. Die 9 % des Papers
werden NICHT behauptet – `simulate_real_anchor()` misst eine EIGENE Zahl.

Hinweis: Dieses Modul ist additiv; kein bestehender Prozess importiert es.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Callable, Optional

# ---------------------------------------------------------------------------
# 1. Beta-Quantil (ε-Best-Belief) – portiert aus kingkillery/src/rqgm/beta.py
#    (pure stdlib). Paper §3.1/§4: BB_ε = I⁻¹_ε(1 + S, 1 + F).
# ---------------------------------------------------------------------------
_TINY = 1e-30


def _betacf(a: float, b: float, x: float, max_iter: int = 200,
            eps: float = 1e-12) -> float:
    """Kettenbruch der unvollständigen Beta-Funktion (Lentz-Verfahren)."""
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c = 1.0
    d = 1.0 - qab * x / qap
    if abs(d) < _TINY:                 # numerischer Schutz (für a,b>=1, 0<x<1 unerreichbar)
        d = _TINY                      # pragma: no cover
    d = 1.0 / d
    h = d
    for m in range(1, max_iter + 1):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        if abs(d) < _TINY:
            d = _TINY                  # pragma: no cover
        c = 1.0 + aa / c
        if abs(c) < _TINY:
            c = _TINY                  # pragma: no cover
        d = 1.0 / d
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        if abs(d) < _TINY:
            d = _TINY                  # pragma: no cover
        c = 1.0 + aa / c
        if abs(c) < _TINY:
            c = _TINY                  # pragma: no cover
        d = 1.0 / d
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < eps:
            break
    return h


def regularized_incomplete_beta(x: float, a: float, b: float) -> float:
    """I_x(a, b): CDF der Beta(a, b)-Verteilung an der Stelle x."""
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0
    ln_beta = math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b)
    front = math.exp(ln_beta + a * math.log(x) + b * math.log1p(-x))
    if x < (a + 1.0) / (a + b + 2.0):
        return front * _betacf(a, b, x) / a
    return 1.0 - front * _betacf(b, a, 1.0 - x) / b


def beta_ppf(q: float, a: float, b: float, tol: float = 1e-10,
             max_iter: int = 200) -> float:
    """Inverse CDF (Quantil) der Beta(a, b) per Bisektion (monoton in x)."""
    if q <= 0.0:
        return 0.0
    if q >= 1.0:
        return 1.0
    lo, hi = 0.0, 1.0
    for _ in range(max_iter):
        mid = 0.5 * (lo + hi)
        if regularized_incomplete_beta(mid, a, b) < q:
            lo = mid
        else:
            hi = mid
        if hi - lo < tol:
            break
    return 0.5 * (lo + hi)


def best_belief(successes: int, failures: int, epsilon: float = 0.05) -> float:
    """Paper BB_ε: ε-Quantil von Beta(1 + S, 1 + F) (konservative Untergrenze)."""
    return beta_ppf(epsilon, 1.0 + successes, 1.0 + failures)


def posterior_mean(successes: int, failures: int) -> float:
    """Posterior-Mittel von Beta(1 + S, 1 + F) (Laplace-geglättete Rate)."""
    return (1.0 + successes) / (2.0 + successes + failures)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# 2. Paper-Parameter (Tab. 3 + 4, PDF-geprüft) und Anker-IDs
# ---------------------------------------------------------------------------
CAMBRIDGE_GRADER_GAIN = 0.09        # Abstract: +9 % Ground-Truth-Genauigkeit
EPS_BEST_BELIEF = 0.05             # Tab. 3
MIN_ANCHOR = 5                     # Tab. 3: "five-outcome anchor minimum"
CHECKPOINT_RHO = 2                 # Tab. 3: power-of-two (ρ = 2)
UCB_AIR_ALPHA = 0.6                # Tab. 3 (inherited)
PAPER_TOTAL_EVALS = 12_288         # Tab. 3
PAPER_TRAIN_SAMPLES_PER_NODE = 3   # Tab. 3
PAPER_SPLITS = (10, 49, 166)       # Tab. 4 (Polyglot train/val/test)
PAPER_BUDGET_USD = {"expand": 25, "train": 8, "val": 25}          # Tab. 4
PAPER_BUDGET_TIME_S = {"expand": 1200, "train": 900, "val": 1200}  # Tab. 4

CRAVE_ID = "TuringEnterprises/CRAVE"          # HF (Paper-Ref [50])
IMO_GRADINGBENCH_ID = "Hwilner/imo-gradingbench"   # HF (Paper §C.4)
ANCHOR_CODING = "Polyglot-Exec-Tests"          # Paper §C.4 (Coder)
ANCHOR_CRAVE = "CRAVE"                         # Paper §C.4 (Reviewer)
ANCHOR_GRADING = "IMO-GradingBench"            # Paper §C.4 (Grading)


def power_of_two_checkpoints(total: int, start: int = 16,
                             rho: int = CHECKPOINT_RHO) -> list[int]:
    """Checkpoint-Zeitpunkte mit exponentiell wachsendem Abstand (Tab. 3, ρ=2)."""
    out: list[int] = []
    t = start
    while t <= total:
        out.append(t)
        t *= rho
    return out


# ---------------------------------------------------------------------------
# 3. Ground-Truth-Anker (echt oder Demo) + Evaluatoren
# ---------------------------------------------------------------------------
@dataclass
class GroundTruthAnchor:
    """Held-out Ground-Truth-Checkpoints (Paper §3.4 „ground-truth anchor").

    Item-Form: {"id": str, "truth": bool, "feature": float}.
    `feature` ist ein echtes, numerisches Merkmal des Datensatzes; unsere
    Demo-Grader sind Schwellwert-Regeln darauf (NICHT die LLM-Grader des Papers).
    """

    items: list = field(default_factory=list)
    source: str = "synthetic-demo"

    def n(self) -> int:
        return len(self.items)

    def outcomes(self, verdict_fn: Callable) -> tuple[int, int]:
        """(Erfolge, Fehlschläge) = Übereinstimmungen mit der Ground Truth."""
        successes = failures = 0
        for it in self.items:
            if bool(verdict_fn(it)) == bool(it["truth"]):
                successes += 1
            else:
                failures += 1
        return successes, failures

    def accuracy(self, verdict_fn: Callable) -> float:
        if not self.items:
            return 0.0
        s, f = self.outcomes(verdict_fn)
        return s / (s + f)


@dataclass
class EvaluatorVersion:
    """Ein Evaluator mit Versionsname (evaluator_v1, v2, …) und Anker-Bilanz."""

    version: str
    verdict_fn: Callable
    threshold: Optional[float] = None
    anchor_successes: int = 0
    anchor_failures: int = 0

    @property
    def anchor_outcomes(self) -> int:
        return self.anchor_successes + self.anchor_failures

    @property
    def anchor_accuracy(self) -> float:
        n = self.anchor_outcomes
        return self.anchor_successes / n if n else 0.0

    def best_belief(self, eps: float = EPS_BEST_BELIEF) -> float:
        return best_belief(self.anchor_successes, self.anchor_failures, eps)


def make_grader(threshold: float) -> Callable:
    """Deterministischer Demo-Grader: akzeptiert, wenn `feature >= threshold`."""
    return lambda it: it["feature"] >= threshold


def feature_quantiles(anchor: GroundTruthAnchor,
                      qs: tuple = (0.25, 0.5, 0.75)) -> list[float]:
    """Feature-Schwellen an festen Quantilen (a priori, kein Cherry-Picking)."""
    feats = sorted(float(it["feature"]) for it in anchor.items)
    if not feats:
        return [0.0 for _ in qs]
    out = []
    for q in qs:
        idx = min(len(feats) - 1, max(0, int(q * (len(feats) - 1))))
        out.append(feats[idx])
    return out


# ---------------------------------------------------------------------------
# 4. Red Queen: Checkpoint-Gate mit ε-Best-Belief + Selective Erasure
# ---------------------------------------------------------------------------
class RedQueen:
    """Ko-Evolution von Agent und Evaluator (Paper §3.2–3.5).

    - Evaluator ist **innerhalb** einer Epoche fix.
    - Am Checkpoint ersetzt ein Challenger den Incumbent nur, wenn seine
      **ε-Best-Belief** auf dem Ground-Truth-Anker **strikt größer** ist
      (Gleichstand → Incumbent bleibt, Paper §3.5).
    - Ersatz nur mit `approved` (Projekt §9); danach Selective Erasure.
    """

    def __init__(self, anchor: GroundTruthAnchor, min_anchor: int = MIN_ANCHOR):
        self.anchor = anchor
        self.min_anchor = min_anchor
        self.current: Optional[EvaluatorVersion] = None
        self.versions: list[EvaluatorVersion] = []
        self.archive: list[dict] = []

    def register(self, evaluator: EvaluatorVersion) -> EvaluatorVersion:
        """Misst den Kandidaten auf dem Anker (S/F für BB_ε)."""
        s, f = self.anchor.outcomes(evaluator.verdict_fn)
        evaluator.anchor_successes, evaluator.anchor_failures = s, f
        return evaluator

    def record(self, item_id: str, score: float,
               evaluator_independent: bool = False) -> dict:
        if self.current is None:
            return {"ok": False, "reason": "kein aktiver Evaluator"}
        rec = {"evaluator": self.current.version, "item": item_id, "score": score,
               "evaluator_independent": evaluator_independent, "ts": _now()}
        self.archive.append(rec)
        return {"ok": True, "record": rec}

    def selective_erasure(self, old_version: str) -> int:
        """Löscht Records des alten Evaluators; Anker-Records bleiben."""
        keep = [r for r in self.archive
                if r["evaluator"] != old_version or r.get("evaluator_independent")]
        erased = len(self.archive) - len(keep)
        self.archive = keep
        return erased

    def checkpoint(self, candidate: EvaluatorVersion, approved: bool = False) -> dict:
        """ε-Best-Belief-Ersatzgate (Paper §3.5; Algorithm 1 Z. 22–31)."""
        self.register(candidate)
        if self.current is None:                          # erste Epoche
            candidate.version = candidate.version or "evaluator_v1"
            self.current = candidate
            self.versions.append(candidate)
            return {"promoted": True, "version": candidate.version,
                    "accuracy": candidate.anchor_accuracy,
                    "best_belief": round(candidate.best_belief(), 4),
                    "reason": "initialer Evaluator (Ground-Truth-Anker)",
                    "gate": "allow"}
        if self.anchor.n() < self.min_anchor:             # Tab. 3: min_anchor
            return {"promoted": False, "version": self.current.version,
                    "reason": f"Anker zu klein ({self.anchor.n()} < "
                              f"{self.min_anchor}) – nicht verifizierbar",
                    "gate": "ask"}
        cand_bb = candidate.best_belief()
        inc_bb = self.current.best_belief()
        if cand_bb > inc_bb:                              # STRICT (ties → incumbent)
            if not approved:                              # §9: kein self_update
                return {"promoted": False, "pending": True,
                        "version": self.current.version,
                        "candidate_best_belief": round(cand_bb, 4),
                        "incumbent_best_belief": round(inc_bb, 4),
                        "reason": "BB_ε strikt besser, aber ohne approved (§9)",
                        "gate": "ask"}
            old = self.current
            candidate.version = f"evaluator_v{len(self.versions) + 1}"
            erased = self.selective_erasure(old.version)
            self.current = candidate
            self.versions.append(candidate)
            return {"promoted": True, "version": candidate.version,
                    "replaced": old.version, "accuracy": candidate.anchor_accuracy,
                    "best_belief": round(cand_bb, 4), "erased_records": erased,
                    "reason": "BB_ε strikt besser + approved", "gate": "ask"}
        return {"promoted": False, "version": self.current.version,
                "candidate_best_belief": round(cand_bb, 4),
                "incumbent_best_belief": round(inc_bb, 4),
                "reason": "BB_ε nicht strikt besser (Gleichstand → Incumbent)",
                "gate": "deny"}

    def report(self) -> dict:
        return {"current": self.current.version if self.current else None,
                "current_best_belief": (round(self.current.best_belief(), 4)
                                        if self.current else None),
                "versions": [{"version": v.version,
                              "accuracy": round(v.anchor_accuracy, 4),
                              "best_belief": round(v.best_belief(), 4)}
                             for v in self.versions],
                "archive_size": len(self.archive),
                "evaluator_ceiling_avoided": len(self.versions) > 1}


# ---------------------------------------------------------------------------
# 5. Echte Anker laden (HuggingFace) – fail-soft
# ---------------------------------------------------------------------------
def load_anchor(kind: str = "grading", *, load_dataset_fn: Optional[Callable] = None,
                limit: int = 200) -> GroundTruthAnchor:
    """Lädt einen echten Ground-Truth-Anker von HuggingFace.

    - kind="grading": IMO-GradingBench, truth = (Points == 7)  (Paper §C.4:
      „full credit (7 of 7)"), feature = Länge der Antwort.
    - kind="coding":  CRAVE (Reviewer), truth = (label == "APPROVE"),
      feature = Patch-Länge.
    """
    if kind not in ("grading", "coding"):
        raise ValueError(f"unbekannter Anker: {kind!r} (erwartet grading|coding)")
    if load_dataset_fn is None:
        from datasets import load_dataset as load_dataset_fn
    if kind == "grading":
        ds = load_dataset_fn(IMO_GRADINGBENCH_ID, split="train")
        items = [{"id": str(r["Grading ID"]), "truth": int(r["Points"]) == 7,
                  "feature": float(len(r["Response"] or ""))}
                 for r in list(ds)[:limit]]
        return GroundTruthAnchor(items, source=f"HF:{IMO_GRADINGBENCH_ID}")
    ds = load_dataset_fn(CRAVE_ID, split="test")
    items = [{"id": str(r["pr_number"]), "truth": r["label"] == "APPROVE",
              "feature": float(len(r["patch"] or ""))}
             for r in list(ds)[:limit]]
    return GroundTruthAnchor(items, source=f"HF:{CRAVE_ID}")


# ---------------------------------------------------------------------------
# 6. Epochen-Loop (RQGM §3.3): fixer Evaluator je Epoche, Ersatz an Checkpoints
# ---------------------------------------------------------------------------
class RedQueenLoop:
    """Treibt Epochen; der Evaluator ist je Epoche fix und wird nur an
    Checkpoints durch einen Challenger ersetzt (Paper §3.3, Algorithm 1)."""

    def __init__(self, anchor: GroundTruthAnchor,
                 checkpoints: Optional[set] = None,
                 min_anchor: int = MIN_ANCHOR):
        self.rq = RedQueen(anchor, min_anchor=min_anchor)
        self.checkpoints = set(checkpoints) if checkpoints is not None else {1, 2, 4, 8}
        self.trajectory: list[dict] = []

    def last_epoch(self) -> int:
        return max(self.checkpoints) if self.checkpoints else 1

    def run(self, candidates: list, approved: bool = True) -> dict:
        """candidates = Challenger in Checkpoint-Reihenfolge."""
        pending = list(candidates)
        for epoch in range(1, self.last_epoch() + 1):
            entry: dict = {"epoch": epoch}
            if (epoch == 1 or epoch in self.checkpoints) and pending:
                entry["checkpoint"] = self.rq.checkpoint(pending.pop(0), approved=approved)
            entry["evaluator"] = self.rq.current.version if self.rq.current else None
            self.trajectory.append(entry)
        return {"trajectory": self.trajectory, "report": self.rq.report()}


# ---------------------------------------------------------------------------
# 7. Simulationen
# ---------------------------------------------------------------------------
ANCHOR_ITEMS = [
    {"id": f"proof-{i:02d}", "feature": q, "truth": q >= 0.7}
    for i, q in enumerate([0.20, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90, 0.95, 0.30, 0.65], 1)
]


def simulate_3_evaluators() -> dict:
    """Offline-Demo: 3 Evaluatoren steigender Schwierigkeit am Demo-Anker."""
    rq = RedQueen(GroundTruthAnchor(items=ANCHOR_ITEMS, source="synthetic-demo"))
    e1 = rq.checkpoint(EvaluatorVersion("", make_grader(0.0), threshold=0.0))
    rq.record("proof-01", 0.9)
    rq.record("gt-unit-1", 0.0, evaluator_independent=True)
    e2_pending = rq.checkpoint(EvaluatorVersion("", make_grader(0.5), threshold=0.5))
    e2 = rq.checkpoint(EvaluatorVersion("", make_grader(0.5), threshold=0.5),
                       approved=True)
    rq.record("proof-02", 0.6)
    rq.record("gt-unit-2", 0.0, evaluator_independent=True)
    e3 = rq.checkpoint(EvaluatorVersion("", make_grader(0.7), threshold=0.7),
                       approved=True)
    return {
        "epoch_1": e1, "epoch_2_pending": e2_pending, "epoch_2": e2, "epoch_3": e3,
        "report": rq.report(), "archive": rq.archive,
        "paper_gain_ground_truth": CAMBRIDGE_GRADER_GAIN,
        "checkpoints": power_of_two_checkpoints(PAPER_TOTAL_EVALS),
        "paper_params": {"eps_best_belief": EPS_BEST_BELIEF,
                         "min_anchor": MIN_ANCHOR, "checkpoint_rho": CHECKPOINT_RHO,
                         "ucb_air_alpha": UCB_AIR_ALPHA,
                         "total_evals": PAPER_TOTAL_EVALS,
                         "train_samples_per_node": PAPER_TRAIN_SAMPLES_PER_NODE,
                         "splits": list(PAPER_SPLITS),
                         "budget_usd": dict(PAPER_BUDGET_USD),
                         "budget_time_s": dict(PAPER_BUDGET_TIME_S),
                         "anchors": [ANCHOR_CODING, ANCHOR_CRAVE, ANCHOR_GRADING]},
    }


def simulate_real_anchor(kind: str = "grading", limit: int = 200,
                         *, load_dataset_fn: Optional[Callable] = None) -> dict:
    """Echte Messung: ε-BB-Ko-Evolution auf einem realen HF-Anker.

    Die Grader sind deterministische Schwellwert-Regeln auf einem echten Feature
    (Auftrag), NICHT die LLM-Grader des Papers. Die gemessene Zahl ist daher
    unsere – nicht die +9 % des Papers.
    """
    anchor = load_anchor(kind, load_dataset_fn=load_dataset_fn, limit=limit)
    rq = RedQueen(anchor)
    before = anchor.accuracy(make_grader(0.0))          # trivialer Baseline-Grader
    results = []
    for i, thr in enumerate(feature_quantiles(anchor), 1):
        r = rq.checkpoint(EvaluatorVersion("", make_grader(thr), threshold=thr),
                          approved=True)
        r["threshold"] = thr
        results.append(r)
    final = rq.current
    return {"anchor": anchor.source, "n_items": anchor.n(),
            "baseline_accuracy_all_accept": round(before, 4),
            "epochs": results, "report": rq.report(),
            "final_accuracy": round(final.anchor_accuracy, 4),
            "measured_gain": round(final.anchor_accuracy - before, 4),
            "paper_gain_ground_truth": CAMBRIDGE_GRADER_GAIN,
            "note": "eigene Messung auf echtem Anker; Grader = Schwellwert-Regeln"}


if __name__ == "__main__":
    import json
    print(json.dumps(simulate_real_anchor("grading"), ensure_ascii=False, indent=2))
