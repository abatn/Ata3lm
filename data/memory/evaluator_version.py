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
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Callable, Optional

# ---------------------------------------------------------------------------
# 1. Beta-Quantil (ε-Best-Belief) – portiert aus kingkillery/src/rqgm/beta.py
#    (pure stdlib). Paper §3.1/§4: BB_ε = I⁻¹_ε(1 + S, 1 + F).
# ---------------------------------------------------------------------------
_TINY = 1e-30


def _betacf(a: float, b: float, x: float, max_iter: int = 200, eps: float = 1e-12) -> float:
    """Kettenbruch der unvollständigen Beta-Funktion (Lentz-Verfahren)."""
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c = 1.0
    d = 1.0 - qab * x / qap
    if abs(d) < _TINY:  # numerischer Schutz (für a,b>=1, 0<x<1 unerreichbar)
        d = _TINY  # pragma: no cover
    d = 1.0 / d
    h = d
    for m in range(1, max_iter + 1):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        if abs(d) < _TINY:
            d = _TINY  # pragma: no cover
        c = 1.0 + aa / c
        if abs(c) < _TINY:
            c = _TINY  # pragma: no cover
        d = 1.0 / d
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        if abs(d) < _TINY:
            d = _TINY  # pragma: no cover
        c = 1.0 + aa / c
        if abs(c) < _TINY:
            c = _TINY  # pragma: no cover
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


def beta_ppf(q: float, a: float, b: float, tol: float = 1e-10, max_iter: int = 200) -> float:
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
CAMBRIDGE_GRADER_GAIN = 0.09  # Abstract: +9 % Ground-Truth-Genauigkeit
EPS_BEST_BELIEF = 0.05  # Tab. 3
MIN_ANCHOR = 5  # Tab. 3: "five-outcome anchor minimum"
CHECKPOINT_RHO = 2  # Tab. 3: power-of-two (ρ = 2)
UCB_AIR_ALPHA = 0.6  # Tab. 3 (inherited)
PAPER_TOTAL_EVALS = 12_288  # Tab. 3
PAPER_TRAIN_SAMPLES_PER_NODE = 3  # Tab. 3
PAPER_SPLITS = (10, 49, 166)  # Tab. 4 (Polyglot train/val/test)
PAPER_BUDGET_USD = {"expand": 25, "train": 8, "val": 25}  # Tab. 4
PAPER_BUDGET_TIME_S = {"expand": 1200, "train": 900, "val": 1200}  # Tab. 4

CRAVE_ID = "TuringEnterprises/CRAVE"  # HF (Paper-Ref [50])
IMO_GRADINGBENCH_ID = "Hwilner/imo-gradingbench"  # HF (Paper §C.4)
ANCHOR_CODING = "Polyglot-Exec-Tests"  # Paper §C.4 (Coder)
ANCHOR_CRAVE = "CRAVE"  # Paper §C.4 (Reviewer)
ANCHOR_GRADING = "IMO-GradingBench"  # Paper §C.4 (Grading)


def power_of_two_checkpoints(total: int, start: int = 16, rho: int = CHECKPOINT_RHO) -> list[int]:
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


def feature_quantiles(anchor: GroundTruthAnchor, qs: tuple = (0.25, 0.5, 0.75)) -> list[float]:
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

    def record(self, item_id: str, score: float, evaluator_independent: bool = False) -> dict:
        if self.current is None:
            return {"ok": False, "reason": "kein aktiver Evaluator"}
        rec = {
            "evaluator": self.current.version,
            "item": item_id,
            "score": score,
            "evaluator_independent": evaluator_independent,
            "ts": _now(),
        }
        self.archive.append(rec)
        return {"ok": True, "record": rec}

    def selective_erasure(self, old_version: str) -> int:
        """Löscht Records des alten Evaluators; Anker-Records bleiben."""
        keep = [r for r in self.archive if r["evaluator"] != old_version or r.get("evaluator_independent")]
        erased = len(self.archive) - len(keep)
        self.archive = keep
        return erased

    def checkpoint(self, candidate: EvaluatorVersion, approved: bool = False) -> dict:
        """ε-Best-Belief-Ersatzgate (Paper §3.5; Algorithm 1 Z. 22–31)."""
        self.register(candidate)
        if self.current is None:  # erste Epoche
            candidate.version = candidate.version or "evaluator_v1"
            self.current = candidate
            self.versions.append(candidate)
            return {
                "promoted": True,
                "version": candidate.version,
                "accuracy": candidate.anchor_accuracy,
                "best_belief": round(candidate.best_belief(), 4),
                "reason": "initialer Evaluator (Ground-Truth-Anker)",
                "gate": "allow",
            }
        if self.anchor.n() < self.min_anchor:  # Tab. 3: min_anchor
            return {
                "promoted": False,
                "version": self.current.version,
                "reason": f"Anker zu klein ({self.anchor.n()} < {self.min_anchor}) – nicht verifizierbar",
                "gate": "ask",
            }
        cand_bb = candidate.best_belief()
        inc_bb = self.current.best_belief()
        if cand_bb > inc_bb:  # STRICT (ties → incumbent)
            if not approved:  # §9: kein self_update
                return {
                    "promoted": False,
                    "pending": True,
                    "version": self.current.version,
                    "candidate_best_belief": round(cand_bb, 4),
                    "incumbent_best_belief": round(inc_bb, 4),
                    "reason": "BB_ε strikt besser, aber ohne approved (§9)",
                    "gate": "ask",
                }
            old = self.current
            candidate.version = f"evaluator_v{len(self.versions) + 1}"
            erased = self.selective_erasure(old.version)
            self.current = candidate
            self.versions.append(candidate)
            return {
                "promoted": True,
                "version": candidate.version,
                "replaced": old.version,
                "accuracy": candidate.anchor_accuracy,
                "best_belief": round(cand_bb, 4),
                "erased_records": erased,
                "reason": "BB_ε strikt besser + approved",
                "gate": "ask",
            }
        return {
            "promoted": False,
            "version": self.current.version,
            "candidate_best_belief": round(cand_bb, 4),
            "incumbent_best_belief": round(inc_bb, 4),
            "reason": "BB_ε nicht strikt besser (Gleichstand → Incumbent)",
            "gate": "deny",
        }

    def report(self) -> dict:
        return {
            "current": self.current.version if self.current else None,
            "current_best_belief": (round(self.current.best_belief(), 4) if self.current else None),
            "versions": [
                {
                    "version": v.version,
                    "accuracy": round(v.anchor_accuracy, 4),
                    "best_belief": round(v.best_belief(), 4),
                }
                for v in self.versions
            ],
            "archive_size": len(self.archive),
            "evaluator_ceiling_avoided": len(self.versions) > 1,
        }


# ---------------------------------------------------------------------------
# 5. Echte Anker laden (HuggingFace) – fail-soft
# ---------------------------------------------------------------------------
def load_anchor(
    kind: str = "grading", *, load_dataset_fn: Optional[Callable] = None, limit: int = 200
) -> GroundTruthAnchor:
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
        items = [
            {
                "id": str(r["Grading ID"]),
                "truth": int(r["Points"]) == 7,
                "feature": float(len(r["Response"] or "")),
                "text": f"{r['Problem']}\n\n{r['Response']}",
                "problem": r["Problem"],
                "response": r["Response"],
                "rubric": r["Grading guidelines"],
                "label": str(r["Reward"]),
            }
            for r in list(ds)[:limit]
        ]
        return GroundTruthAnchor(items, source=f"HF:{IMO_GRADINGBENCH_ID}")
    ds = load_dataset_fn(CRAVE_ID, split="test")
    items = [
        {
            "id": str(r["pr_number"]),
            "truth": r["label"] == "APPROVE",
            "feature": float(len(r["patch"] or "")),
            "text": f"{r.get('description', '')}\n\n{r.get('patch', '')}",
            "rubric": "",
            "label": str(r["label"]),
        }
        for r in list(ds)[:limit]
    ]
    return GroundTruthAnchor(items, source=f"HF:{CRAVE_ID}")


# ---------------------------------------------------------------------------
# 6. Epochen-Loop (RQGM §3.3): fixer Evaluator je Epoche, Ersatz an Checkpoints
# ---------------------------------------------------------------------------
class RedQueenLoop:
    """Treibt Epochen; der Evaluator ist je Epoche fix und wird nur an
    Checkpoints durch einen Challenger ersetzt (Paper §3.3, Algorithm 1)."""

    def __init__(self, anchor: GroundTruthAnchor, checkpoints: Optional[set] = None, min_anchor: int = MIN_ANCHOR):
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
# 8. Echter LLM-Grader (zweiter Call als Judge) – deterministisch + fail-soft
#    Quellen: arXiv:2606.26294 §5 (Grader-Evolution) ·
#    OpenAI Structured Outputs (https://platform.openai.com/docs/guides/structured-outputs)
# ---------------------------------------------------------------------------
GRADER_MODEL = os.environ.get("RQGM_GRADER_MODEL", "nvidia/nemotron-3-super-120b-a12b")
GRADER_MAX_TOKENS = int(os.environ.get("RQGM_GRADER_MAX_TOKENS", "1024"))  # fest (Auftrag)
GRADER_TEMPERATURE = 0.0  # deterministisch (Auftrag)


def _default_client():
    """OpenAI-kompatibler Client aus der Umgebung (Key/Base-URL)."""
    from openai import OpenAI

    return OpenAI(
        api_key=os.environ.get("OPENAI_API_KEY", ""),
        base_url=os.environ.get("OPENAI_BASE_URL", "https://integrate.api.nvidia.com/v1"),
    )


def _extract_json(raw: str) -> str:
    """Erstes JSON-Objekt aus einer Antwort ziehen (robust gegen Fließtext)."""
    import re

    m = re.search(r"\{.*\}", raw or "", re.DOTALL)
    return m.group(0) if m else (raw or "")


def _grader_prompt(item: dict) -> str:
    return (
        "You are a strict grader. Decide whether the RESPONSE earns FULL credit "
        "for the PROBLEM according to the GUIDELINES. "
        "Output ONLY the JSON object - no prose, no markdown, no code fences - "
        'with keys {"passed": true|false, "score": 0..1, "reason": "short"}.\n'
        f"PROBLEM:\n{item.get('text', '')}\nGUIDELINES:\n{item.get('rubric', '')}"
    )


def make_llm_grader(
    rule_grader: Callable,
    *,
    client=None,
    model: str = GRADER_MODEL,
    max_tokens: int = GRADER_MAX_TOKENS,
    log: Optional[list] = None,
) -> Callable:
    """Zweiter LLM-Call als Judge; JSON-Verdict per Pydantic validiert.

    temperature=0, feste max_tokens. **Fail-soft:** bei API-Fehler oder
    ungültigem Schema → Regel-Grader + Log-Eintrag (kein Crash).
    """
    from pydantic import BaseModel, Field

    class GraderVerdict(BaseModel):
        passed: bool
        score: float = Field(ge=0.0, le=1.0)
        reason: str = ""

    def verdict(item: dict) -> bool:
        try:
            c = client or _default_client()
            resp = c.chat.completions.create(
                model=model,
                temperature=GRADER_TEMPERATURE,
                max_tokens=max_tokens,
                response_format={"type": "json_object"},
                messages=[{"role": "user", "content": _grader_prompt(item)}],
            )
            raw = resp.choices[0].message
            raw = raw.content or getattr(raw, "reasoning_content", None) or ""
            return bool(GraderVerdict.model_validate_json(_extract_json(raw)).passed)
        except Exception as e:  # fail-soft
            if log is not None:
                log.append({"fallback": "rule_grader", "item": item.get("id"), "error": str(e)[:160]})
            return bool(rule_grader(item))

    return verdict


def _pair_prompt(item_a: dict, item_b: dict) -> str:
    return (
        "You are a strict grader. Two responses (A and B) answer the same problem. "
        "Decide which one better earns FULL credit per the guidelines. "
        'Output ONLY the JSON object {"winner": "A"|"B"} - no prose.\n'
        f"PROBLEM:\n{item_a.get('problem', item_a.get('text', ''))}\n"
        f"GUIDELINES:\n{item_a.get('rubric', '')}\n"
        f"A:\n{item_a.get('text', '')}\nB:\n{item_b.get('text', '')}"
    )


def make_llm_pairwise_judge(
    *, client=None, model: str = GRADER_MODEL, max_tokens: int = GRADER_MAX_TOKENS, log: Optional[list] = None
) -> Callable:
    """Paarweiser LLM-Judge (A/B) für Positions-Bias-Tests (Quelle: lechmazur/position_bias).

    Fail-soft: bei API-Fehler/ungültigem Schema gewinnt der **längere** Text
    (Regel) + Log-Eintrag.
    """
    from pydantic import BaseModel

    class PairVerdict(BaseModel):
        winner: str

    def judge(item_a: dict, item_b: dict) -> str:
        try:
            c = client or _default_client()
            resp = c.chat.completions.create(
                model=model,
                temperature=GRADER_TEMPERATURE,
                max_tokens=max_tokens,
                response_format={"type": "json_object"},
                messages=[{"role": "user", "content": _pair_prompt(item_a, item_b)}],
            )
            msg = resp.choices[0].message
            raw = msg.content or getattr(msg, "reasoning_content", None) or ""
            winner = PairVerdict.model_validate_json(_extract_json(raw)).winner.strip().upper()
            return "A" if winner.startswith("A") else "B"
        except Exception as e:  # fail-soft
            if log is not None:
                log.append({"fallback": "rule_length", "error": str(e)[:160]})
            return "A" if len(item_a.get("text", "")) >= len(item_b.get("text", "")) else "B"

    return judge


# ---------------------------------------------------------------------------
# 9. Statistik/Methodik: Hedges' g · Power · KI · Cohen's κ · Positions-Bias
#    Quellen (HTTP 200, 2026-10-02): Faul et al. 2007 (G*Power 3,
#    https://link.springer.com/article/10.3758/BF03193146) · NIST Hedges g
#    (https://www.itl.nist.gov/div898/software/dataplot/refman2/auxillar/hedgeg.htm)
#    · metafor::cmicalc (https://wviechtb.github.io/metafor/reference/cmicalc.html)
#    · Landis & Koch 1977 (https://doi.org/10.2307/2529310) · Steiger & Fouladi 1997
#    (Buchkapitel) · Fleiss, Cohen & Everitt 1969 (Psychol. Bull. 72(5):323–327;
#    DOI 10.1037/h0028106 blockt Bots → bibliografisch zitiert).
# ---------------------------------------------------------------------------
def hedges_correction(nu: float) -> float:
    """Exakter Korrekturfaktor J(ν) = Γ(ν/2) / (√(ν/2)·Γ((ν−1)/2))."""
    return math.exp(math.lgamma(nu / 2.0) - math.lgamma((nu - 1.0) / 2.0)) / math.sqrt(nu / 2.0)


def hedges_correction_approx(nu: float) -> float:
    """Näherung J(ν) ≈ 1 − 3/(4ν−1) (akzeptiert für n>4; metafor::cmicalc)."""
    return 1.0 - 3.0 / (4.0 * nu - 1.0)


def hedges_g(d: float, nu: float) -> float:
    """g = J(ν)·d (NIST: Hedges' g)."""
    return hedges_correction(nu) * d


def cohens_d_paired(diffs: list) -> float:
    """d = mean(diff)/sd(diff) für gepaarte Stichproben (sd=0 → 0.0)."""
    n = len(diffs)
    m = sum(diffs) / n
    sd = math.sqrt(sum((x - m) ** 2 for x in diffs) / (n - 1))
    return m / sd if sd > 0 else 0.0


def power_paired_t(effect_size: float, n: int, alpha: float = 0.05) -> float:
    """Power des zweiseitigen gepaarten t-Tests (nichtzentrales t, G*Power-konform)."""
    import numpy as np
    from scipy import stats

    df = n - 1
    ncp = effect_size * math.sqrt(n)
    tcrit = stats.t.ppf(1.0 - alpha / 2.0, df)
    with np.errstate(divide="ignore", invalid="ignore"):
        return float(1.0 - stats.nct.cdf(tcrit, df, ncp))


def required_n_paired_t(effect_size: float, power: float = 0.80, alpha: float = 0.05, n_max: int = 100_000) -> int:
    """Kleinste n mit Power ≥ Ziel (G*Power-Analog); n_max, wenn nie erreicht."""
    for n in range(2, n_max + 1):
        if power_paired_t(effect_size, n, alpha) >= power:
            return n
    return n_max


def _solve_nct(t: float, df: int, target: float) -> float:
    """δ mit nct.cdf(t; df, δ) = target (Bisektion; cdf sinkt monoton in δ)."""
    import numpy as np
    from scipy import stats

    lo, hi = -50.0, 50.0
    with np.errstate(divide="ignore", invalid="ignore"):
        for _ in range(200):
            mid = 0.5 * (lo + hi)
            if stats.nct.cdf(t, df, mid) > target:
                lo = mid
            else:
                hi = mid
    return 0.5 * (lo + hi)


def ci_hedges_g_noncentral(g: float, n: int, conf: float = 0.95) -> tuple:
    """KI für g über nichtzentrales t (Steiger & Fouladi 1997)."""
    df = n - 1
    j = hedges_correction(df)
    t = (g / j) * math.sqrt(n)
    alpha = 1.0 - conf
    lo = _solve_nct(t, df, 1.0 - alpha / 2.0) / math.sqrt(n) * j
    hi = _solve_nct(t, df, alpha / 2.0) / math.sqrt(n) * j
    return (lo, hi)


def cohens_kappa(a: list, b: list) -> float:
    """Cohen's κ für zwei Rater (pe=1 → 1.0 bei perfekter Übereinstimmung, sonst 0.0)."""
    n = len(a)
    labels = sorted({*a, *b}, key=str)
    po = sum(1 for x, y in zip(a, b) if x == y) / n
    pe = sum((a.count(lab) / n) * (b.count(lab) / n) for lab in labels)
    if pe == 1.0:
        return 1.0 if po == 1.0 else 0.0
    return (po - pe) / (1.0 - pe)


def kappa_se_simplified(a: list, b: list) -> float:
    """Vereinfachte asymptotische SE (Fleiss); volle FCE-Kovarianzterme NICHT modelliert."""
    n = len(a)
    labels = sorted({*a, *b}, key=str)
    po = sum(1 for x, y in zip(a, b) if x == y) / n
    pe = sum((a.count(lab) / n) * (b.count(lab) / n) for lab in labels)
    return math.sqrt(po * (1.0 - po) / (n * (1.0 - pe) ** 2)) if pe != 1.0 else 0.0


def kappa_ci(kappa: float, se: float, z: float = 1.96) -> tuple:
    """Asymptotisches KI (veraltet für n=8) – ersetzt durch `bootstrap_kappa_ci`."""
    return (kappa - z * se, kappa + z * se)


BOOTSTRAP_RESAMPLES = 10_000  # Efron & Tibshirani: B≥1000 für KI (Auftrag: 10.000)
BOOTSTRAP_SEED = 0  # reproduzierbar (Auftrag)


def bootstrap_kappa_ci(
    a: list,
    b: list,
    n_resamples: int = BOOTSTRAP_RESAMPLES,
    seed: int = BOOTSTRAP_SEED,
    confidence_level: float = 0.95,
    method: str = "BCa",
) -> dict:
    """Case-level **Bootstrap**-KI für Cohen's κ (KEIN Wilson – κ ist keine Proportion).

    - B = 10.000 Resamples mit Zurücklegen, seed-fixiert → bit-reproduzierbar.
    - BCa (Default), Percentile als Fallback bei degenerierter Verteilung (NaN).
    - `degenerate_share` = Anteil Resamples, in denen ein Stream konstant war
      (κ undefiniert → 0.0). KEINE willkürliche Schwelle: die Interpretation ist
      datenabgeleitet (`degenerate_interpretation`): 0 → ok; >0 → auf NaN prüfen;
      1.0 → Stream konstant, κ nicht interpretierbar.
    Quellen: scipy.stats.bootstrap (method='BCa') ·
    Efron & Tibshirani 1993 (An Introduction to the Bootstrap, S. 184–188).
    """

    import warnings

    import numpy as np
    from scipy import stats as _st

    a, b, n = list(a), list(b), len(a)
    kappa = cohens_kappa(a, b)

    # Degenerate-Share: eigener seed-fixierter Resample-Durchlauf
    rng = np.random.default_rng(seed)
    degenerate = 0
    for _ in range(n_resamples):
        idx = rng.integers(0, n, n)
        if len({a[i] for i in idx}) == 1 or len({b[i] for i in idx}) == 1:
            degenerate += 1
    degenerate_share = degenerate / n_resamples

    def stat(x, y):
        return cohens_kappa(list(x), list(y))

    with warnings.catch_warnings():  # degenerierte BCa-Akzeleration -> NaN, kein Lärm
        warnings.simplefilter("ignore")
        res = _st.bootstrap(
            (a, b),
            stat,
            paired=True,
            n_resamples=n_resamples,
            confidence_level=confidence_level,
            method=method,
            random_state=seed,
        )
    lo, hi = res.confidence_interval
    used = method
    if np.isnan(lo) or np.isnan(hi):  # degenerierte Bootstrap-Verteilung
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            res = _st.bootstrap(
                (a, b),
                stat,
                paired=True,
                n_resamples=n_resamples,
                confidence_level=confidence_level,
                method="percentile",
                random_state=seed,
            )
        lo, hi = res.confidence_interval
        used = "percentile"
    return {
        "kappa": kappa,
        "ci": (float(lo), float(hi)),
        "method": used,
        "n_resamples": n_resamples,
        "seed": seed,
        "degenerate_share": degenerate_share,
        "degenerate_interpretation": (
            "Stream konstant - kappa nicht interpretierbar"
            if degenerate_share == 1.0
            else "degenerierte Resamples vorhanden - auf NaN pruefen"
            if degenerate_share > 0.0
            else "ok"
        ),
    }


def landis_koch(kappa: float) -> str:
    """Interpretation nach Landis & Koch (1977)."""
    a = abs(kappa)
    if a > 0.81:
        return "almost perfect"
    if a >= 0.61:
        return "substantial"
    if a >= 0.41:
        return "moderate"
    if a >= 0.21:
        return "fair"
    if a >= 0.01:
        return "slight"
    return "poor"


def flip_rate(orders: list) -> float:
    """Anteil Items mit wechselndem Gewinner zwischen Ordnungen."""
    return sum(1 for item in orders if len(set(item)) > 1) / len(orders)


def position_consistency(orders: list) -> float:
    """Anteil Items mit demselben Gewinner in ALLEN Ordnungen."""
    return sum(1 for item in orders if len(set(item)) == 1) / len(orders)


def repetition_stability(runs: list) -> float:
    """Anteil Items mit identischem Output über Wiederholungen."""
    return sum(1 for item in runs if len(set(item)) == 1) / len(runs)


# ---------------------------------------------------------------------------
# 10. Simulationen
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
    e2 = rq.checkpoint(EvaluatorVersion("", make_grader(0.5), threshold=0.5), approved=True)
    rq.record("proof-02", 0.6)
    rq.record("gt-unit-2", 0.0, evaluator_independent=True)
    e3 = rq.checkpoint(EvaluatorVersion("", make_grader(0.7), threshold=0.7), approved=True)
    return {
        "epoch_1": e1,
        "epoch_2_pending": e2_pending,
        "epoch_2": e2,
        "epoch_3": e3,
        "report": rq.report(),
        "archive": rq.archive,
        "paper_gain_ground_truth": CAMBRIDGE_GRADER_GAIN,
        "checkpoints": power_of_two_checkpoints(PAPER_TOTAL_EVALS),
        "paper_params": {
            "eps_best_belief": EPS_BEST_BELIEF,
            "min_anchor": MIN_ANCHOR,
            "checkpoint_rho": CHECKPOINT_RHO,
            "ucb_air_alpha": UCB_AIR_ALPHA,
            "total_evals": PAPER_TOTAL_EVALS,
            "train_samples_per_node": PAPER_TRAIN_SAMPLES_PER_NODE,
            "splits": list(PAPER_SPLITS),
            "budget_usd": dict(PAPER_BUDGET_USD),
            "budget_time_s": dict(PAPER_BUDGET_TIME_S),
            "anchors": [ANCHOR_CODING, ANCHOR_CRAVE, ANCHOR_GRADING],
        },
    }


def simulate_real_anchor(
    kind: str = "grading",
    limit: int = 200,
    *,
    load_dataset_fn: Optional[Callable] = None,
    use_llm: bool = False,
    client=None,
    grader_log: Optional[list] = None,
) -> dict:
    """Echte Messung: ε-BB-Ko-Evolution auf einem realen HF-Anker.

    use_llm=False: deterministische Schwellwert-Regeln (offline).
    use_llm=True : zweiter LLM-Call als Judge (fail-soft → Regel-Grader).
    Die gemessene Zahl ist unsere – nicht die +9 % des Papers.
    """
    anchor = load_anchor(kind, load_dataset_fn=load_dataset_fn, limit=limit)
    rq = RedQueen(anchor)
    before = anchor.accuracy(make_grader(0.0))  # trivialer Baseline-Grader
    thresholds = feature_quantiles(anchor)
    graders = [make_grader(thr) for thr in thresholds]
    if use_llm:
        graders = [make_llm_grader(g, client=client, log=grader_log) for g in graders]
    results = []
    for i, g in enumerate(graders, 1):
        r = rq.checkpoint(EvaluatorVersion("", g), approved=True)
        r["threshold"] = thresholds[i - 1]
        results.append(r)
    final = rq.current
    return {
        "anchor": anchor.source,
        "n_items": anchor.n(),
        "grader": "llm+rule-fallback" if use_llm else "rule",
        "baseline_accuracy_all_accept": round(before, 4),
        "epochs": results,
        "report": rq.report(),
        "final_accuracy": round(final.anchor_accuracy, 4),
        "measured_gain": round(final.anchor_accuracy - before, 4),
        "paper_gain_ground_truth": CAMBRIDGE_GRADER_GAIN,
        "note": "eigene Messung auf echtem Anker; Grader = Schwellwert-Regeln"
        + (" + LLM-Judge (fail-soft)" if use_llm else ""),
    }


if __name__ == "__main__":
    import json

    print(json.dumps(simulate_real_anchor("grading"), ensure_ascii=False, indent=2))


# ---------------------------------------------------------------------------
# 11. Stabile κ-Statistik (n≥50): Sample-Size, 4-Klassen-Grader, stabiler Lauf
#     Quellen (HTTP 200, 2026-10-02): presize::prec_kappa
#     (https://search.r-project.org/CRAN/refmans/presize/html/prec_kappa.html) ·
#     kappaSize (https://cran.r-project.org/web/packages/kappaSize/index.html,
#     Rotondi & Donner 2012) · scipy.stats.bootstrap · HF Hwilner/imo-gradingbench.
#     R war NICHT installiert -> prec-Methode algebraisch portiert (Abweichung
#     dokumentiert: simplified-SE statt voller kappaSize-Varianz).
# ---------------------------------------------------------------------------
CLASS_GRADES = ("Correct", "Almost", "Partial", "Incorrect")


def kappa_required_n(kappa: float, props: list, target_width: float = 0.30, conf: float = 0.95) -> int:
    """Benötigte n für eine 95%-KI-Breite < target_width (simplified-SE-basiert).

    Methode analog presize::prec_kappa / kappaSize (Large-Sample); R fehlte, daher
    algebraische Umstellung der vereinfachten Fleiss-SE (NICHT die volle
    kappaSize-Varianz). Unter N < 50 unsicher (presize/kappaSize-Warnung).
    """
    from scipy import stats as _st

    z = _st.norm.ppf(1.0 - (1.0 - conf) / 2.0)
    pe = sum(p * p for p in props)
    po = pe + kappa * (1.0 - pe)
    return int(math.ceil((2.0 * z) ** 2 * po * (1.0 - po) / (target_width**2 * (1.0 - pe) ** 2)))


GRADER_MAX_ATTEMPTS = int(os.environ.get("RQGM_GRADER_MAX_ATTEMPTS", "3"))
GRADER_VOTES = int(os.environ.get("RQGM_GRADER_VOTES", "1"))


def _repair_json(raw: str) -> str:
    """JSON reparieren (json-repair), sonst erstes {...} per Regex.

    Quelle: https://github.com/mangiucugna/json_repair (PyPI `json-repair`).
    """
    try:
        from json_repair import repair_json

        repaired = repair_json(raw or "")
        return repaired if repaired else _extract_json(raw)
    except Exception:
        return _extract_json(raw)


def _class_schema() -> dict:
    """OpenAI-Structured-Outputs-Schema (strict) für das Klassen-Verdict."""
    return {
        "type": "json_schema",
        "json_schema": {
            "name": "ClassVerdict",
            "strict": True,
            "schema": {
                "type": "object",
                "properties": {"grade": {"type": "string", "enum": list(CLASS_GRADES)}},
                "required": ["grade"],
                "additionalProperties": False,
            },
        },
    }


def _class_prompt(item: dict, strict: bool = False) -> str:
    suffix = " Return ONLY the JSON object, nothing else." if strict else ""
    problem = item.get("problem") or item.get("text", "")
    response = item.get("response") or ""
    return (
        "You are a STRICT IMO proof grader. Read PROBLEM, GRADING GUIDELINES and the "
        "candidate RESPONSE. Map the achieved credit to exactly one class:\n"
        "  Correct   = full credit (7/7): complete and valid proof.\n"
        "  Almost    = nearly complete (5-6/7): minor gaps.\n"
        "  Partial   = partial progress (1-4/7).\n"
        "  Incorrect = no valid progress (0/7).\n"
        "Be strict: a long, confident or well-written answer is NOT automatically "
        "correct - the key steps must actually be present and valid. If unsure, do NOT "
        'choose Correct. Output ONLY the JSON object {"grade": "<class>"} - no prose.' + suffix + "\n"
        f"PROBLEM:\n{problem}\nGRADING GUIDELINES:\n{item.get('rubric', '')}\n"
        f"CANDIDATE RESPONSE:\n{response}"
    )


def make_llm_class_grader(
    *,
    client=None,
    model: str = GRADER_MODEL,
    max_tokens: int = GRADER_MAX_TOKENS,
    log: Optional[list] = None,
    max_attempts: int = GRADER_MAX_ATTEMPTS,
    votes: int = GRADER_VOTES,
    use_schema: bool = False,
) -> Callable:
    """Robuster 4-Klassen-LLM-Grader (Correct/Almost/Partial/Incorrect).

    - **json-repair** repariert Prosa/abgeschnittenes JSON.
    - **Retry** bis `max_attempts` (strengerer Prompt ab Versuch 2).
    - **Mehrheitsentscheid** über `votes` Samples (Gleichstand → Fallback).
    - optional `use_schema` (OpenAI Structured Outputs, `json_schema` strict).
    - **fail-soft**: nach Erschöpfung → `"Incorrect"` + Log-Eintrag.
    Quellen: json_repair · OpenAI Structured Outputs · NVIDIA NIM Structured Generation.
    """
    from collections import Counter

    from pydantic import BaseModel

    class ClassVerdict(BaseModel):
        grade: str

    def _one(item: dict) -> str:
        last: Optional[Exception] = None
        for attempt in range(1, max_attempts + 1):
            try:
                c = client or _default_client()
                resp = c.chat.completions.create(
                    model=model,
                    temperature=GRADER_TEMPERATURE,
                    max_tokens=max_tokens,
                    response_format=_class_schema() if use_schema else {"type": "json_object"},
                    messages=[{"role": "user", "content": _class_prompt(item, strict=attempt > 1)}],
                )
                msg = resp.choices[0].message
                raw = msg.content or getattr(msg, "reasoning_content", None) or ""
                grade_value = ClassVerdict.model_validate_json(_repair_json(raw)).grade.strip()
                if grade_value not in CLASS_GRADES:
                    raise ValueError(f"ungueltige Klasse: {grade_value}")
                return grade_value
            except Exception as e:
                last = e
        raise last

    def grade(item: dict) -> str:
        try:
            results = [_one(item) for _ in range(votes)]
            top, count = Counter(results).most_common(1)[0]
            if count * 2 <= votes:  # Gleichstand -> unsicher
                raise ValueError("keine Mehrheit")
            return top
        except Exception as e:  # fail-soft
            if log is not None:
                log.append({"fallback": "rule_incorrect", "item": item.get("id"), "error": str(e)[:160]})
            return "Incorrect"

    return grade


def stable_kappa_run(
    kind: str = "grading",
    n: int = 50,
    *,
    load_dataset_fn: Optional[Callable] = None,
    client=None,
    grader_log: Optional[list] = None,
) -> dict:
    """Stabiler κ-Lauf: n ≥ 50 Items, 4-Klassen-LLM-Grader vs. humanes Label,
    Bootstrap-KI (BCa, B=10.000, seed=0)."""
    from collections import Counter

    anchor = load_anchor(kind, load_dataset_fn=load_dataset_fn, limit=n)
    grader = make_llm_class_grader(client=client, log=grader_log)
    verdicts = [grader(it) for it in anchor.items]
    labels = [it["label"] for it in anchor.items]
    boot = bootstrap_kappa_ci(verdicts, labels)
    return {
        "anchor": anchor.source,
        "n": anchor.n(),
        "grader": "llm-4class+fallback",
        "kappa": boot["kappa"],
        "ci": boot["ci"],
        "method": boot["method"],
        "degenerate_share": boot["degenerate_share"],
        "degenerate_interpretation": boot["degenerate_interpretation"],
        "seed": boot["seed"],
        "n_resamples": boot["n_resamples"],
        "class_counts_llm": dict(Counter(verdicts)),
        "class_counts_human": dict(Counter(labels)),
        "fallbacks": len(grader_log) if grader_log is not None else None,
    }
