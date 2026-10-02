#!/usr/bin/env python3
"""
Red-Queen-Ko-Evolution: versionierte Evaluatoren mit Ground-Truth-Anker.

Quelle (verifiziert 2026-10-01, HTTP 200):
  - The Red Queen Gödel Machine: Co-Evolving Agents and Their Evaluators,
    arXiv:2606.26294 (Univ. Cambridge + NVIDIA + Flower Labs + MBZUAI + Inria,
    Preprint 24.06.2026). Wörtlich aus dem Paper/der Cambridge-Meldung:
      * "search is organized into epochs with a fixed within-epoch evaluation
        criterion, while the utility can be updated at epoch boundaries"
      * "At checkpoints, a stronger evaluator can replace the old one if it
        performs better on trusted ground-truth examples."
      * "Selective Erasure … all utility records in the archive that were
        produced by the old evaluator are deleted. However, data from
        'evaluator-independent' sources—such as ground-truth unit tests or fixed
        historical benchmarks—is retained."
      * "co-evolved graders reach 9% higher ground-truth accuracy."
    https://arxiv.org/abs/2606.26294
    https://www.cst.cam.ac.uk/news/red-queen-hypothesis-new-way-forward-self-improving-ai
    (Cambridge, 21.07.2026)
  - Projekt-Gesetz: AGENTS.md §9 (kein self_update ohne `approved`).

Lab-Prinzip: Mechanik = wörtlich aus der Quelle; die konkreten Anker-Werte der
Simulation sind Auftrag (KEINE Paper-Behauptung). Die 9 % stehen nur als
dokumentierte Kennzahl (`CAMBRIDGE_GRADER_GAIN`) – hier wird keine 9 %
simuliert oder behauptet.

Hinweis (ehrlich): Dieses Modul ist **additiv** und wird von keinem bestehenden
Prozess aufgerufen. Es ändert kein Verhalten (§9) und ist nicht in
`reflective_agent`/`ingestion_hook` verdrahtet – das wäre eine eigene
Verhaltensänderung und bräuchte ein Human-Gate.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Callable, Optional

# Quelle: "co-evolved graders reach 9% higher ground-truth accuracy"
# (arXiv:2606.26294). Kennzahl des Papers – NICHT hier gemessen.
CAMBRIDGE_GRADER_GAIN = 0.09

# --- Konkrete Paper-Parameter (Paper Tab. 3) -------------------------------
# ACHTUNG (ehrlich): Cambridge hat NOCH KEIN Code-Release ("The underlying
# method will be open sourced"). Die folgenden Werte stammen aus unabhängigen
# Reproduktionen, die sich ausdrücklich auf Paper Tab. 3 berufen – NICHT
# offiziell bestätigt:
#   ianyac/red-queen-godel-machine  (config.yaml: "paper Tab. 3")
#   DreamFallenFlowers/OpenRQGM     (12.288 Validation-Outcomes, 166er Holdout)
EPS_BEST_BELIEF = 0.05        # ε-Best-Belief-Quantil (paper Tab. 3)
MIN_ANCHOR = 5                # "five-outcome anchor minimum" (paper Tab. 3)
CHECKPOINT_RHO = 2            # exponentielles Checkpoint-Spacing ρ=2 (paper Tab. 3)
PAPER_TOTAL_EVALS = 12_288    # paper: 12.288 (Demo-Repro: 64)
PAPER_SPLITS = (10, 49, 166)  # paper: 10/49/166 (Demo-Repro: 2/3/5)
PAPER_BUDGET_USD = {"expand": 25, "train": 8, "val": 25}   # paper Tab. 3
ANCHOR_CODING = "CRAVE"                 # Coding-Anker (Polyglot-Repro)
ANCHOR_GRADING = "IMO-GradingBench"     # Proof-Grading (HF: Hwilner/imo-gradingbench)


def power_of_two_checkpoints(total: int, start: int = 16,
                             rho: int = CHECKPOINT_RHO) -> list[int]:
    """Checkpoint-Zeitpunkte mit exponentiell wachsendem Abstand (paper Tab. 3).

    Reproduktionen: erster Checkpoint bei 16, danach ×ρ (=2) → 16, 32, 64, …
    Innerhalb einer Epoche bleibt der Evaluator fix.
    """
    out: list[int] = []
    t = start
    while t <= total:
        out.append(t)
        t *= rho
    return out


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class GroundTruthAnchor:
    """Vertrauenswürdige Ground-Truth-Checkpoints (menschlich geprüft).

    Quelle: „trusted ground-truth examples" / „Ground-Truth Anchor" (RQGM).
    Item-Form: {"id": str, "quality": float, "truth": bool}.
    """

    items: list = field(default_factory=list)

    def accuracy(self, verdict_fn: Callable) -> float:
        """Anteil der Items, bei denen das Urteil der Ground-Truth entspricht."""
        if not self.items:
            return 0.0
        ok = sum(1 for it in self.items if bool(verdict_fn(it)) == bool(it["truth"]))
        return ok / len(self.items)


@dataclass
class EvaluatorVersion:
    """Ein Evaluator mit Versionsname (evaluator_v1, v2, …) und Anker-Genauigkeit."""

    version: str
    verdict_fn: Callable
    anchor_accuracy: float = 0.0


class RedQueen:
    """Epoch-basierte Ko-Evolution von Agent und Evaluator (RQGM).

    - Innerhalb einer Epoche ist der Evaluator **fix** (Vergleichbarkeit).
    - An Checkpoints ersetzt ein **stärkerer** Evaluator den alten – nur wenn er
      auf dem Ground-Truth-Anker besser ist.
    - **Selective Erasure:** Beim Wechsel werden die Utility-Records des alten
      Evaluators gelöscht; evaluator-unabhängige Daten bleiben.
    - Projekt-Gesetz §9: Der Wechsel ist ein `self_update` → nur mit `approved`.
    """

    def __init__(self, anchor: GroundTruthAnchor, min_anchor: int = MIN_ANCHOR):
        self.anchor = anchor
        self.min_anchor = min_anchor
        self.current: Optional[EvaluatorVersion] = None
        self.versions: list[EvaluatorVersion] = []
        self.archive: list[dict] = []

    def register(self, evaluator: EvaluatorVersion) -> EvaluatorVersion:
        """Misst den Kandidaten auf dem Ground-Truth-Anker (Voraussetzung)."""
        evaluator.anchor_accuracy = self.anchor.accuracy(evaluator.verdict_fn)
        return evaluator

    def record(self, item_id: str, score: float,
               evaluator_independent: bool = False) -> dict:
        """Utility-Record unter dem AKTUELLEN Evaluator ablegen."""
        if self.current is None:
            return {"ok": False, "reason": "kein aktiver Evaluator"}
        rec = {"evaluator": self.current.version, "item": item_id, "score": score,
               "evaluator_independent": evaluator_independent, "ts": _now()}
        self.archive.append(rec)
        return {"ok": True, "record": rec}

    def selective_erasure(self, old_version: str) -> int:
        """Löscht Records des alten Evaluators; behält evaluator-unabhängige."""
        keep = [r for r in self.archive
                if r["evaluator"] != old_version or r.get("evaluator_independent")]
        erased = len(self.archive) - len(keep)
        self.archive = keep
        return erased

    def checkpoint(self, candidate: EvaluatorVersion, approved: bool = False) -> dict:
        """Checkpoint: Kandidat ersetzt den aktuellen Evaluator nur, wenn er auf
        dem Ground-Truth-Anker besser ist UND (§9) `approved` vorliegt."""
        self.register(candidate)
        if self.current is None:                     # erste Epoche
            candidate.version = candidate.version or "evaluator_v1"
            self.current = candidate
            self.versions.append(candidate)
            return {"promoted": True, "version": candidate.version,
                    "accuracy": candidate.anchor_accuracy,
                    "reason": "initialer Evaluator (Ground-Truth-Anker)",
                    "gate": "allow"}
        if len(self.anchor.items) < self.min_anchor:   # paper Tab. 3: min_anchor
            return {"promoted": False, "version": self.current.version,
                    "reason": f"Anker zu klein ({len(self.anchor.items)} < "
                              f"{self.min_anchor}) – nicht verifizierbar",
                    "gate": "ask"}
        if candidate.anchor_accuracy <= self.current.anchor_accuracy:
            return {"promoted": False, "version": self.current.version,
                    "candidate_accuracy": candidate.anchor_accuracy,
                    "incumbent_accuracy": self.current.anchor_accuracy,
                    "reason": "nicht besser auf Ground-Truth-Anker", "gate": "deny"}
        if not approved:                             # §9: self_update ohne approved
            return {"promoted": False, "pending": True,
                    "version": self.current.version,
                    "candidate_accuracy": candidate.anchor_accuracy,
                    "incumbent_accuracy": self.current.anchor_accuracy,
                    "reason": "besser auf Anker, aber ohne approved (§9)",
                    "gate": "ask"}
        old = self.current
        candidate.version = f"evaluator_v{len(self.versions) + 1}"
        erased = self.selective_erasure(old.version)
        self.current = candidate
        self.versions.append(candidate)
        return {"promoted": True, "version": candidate.version,
                "replaced": old.version, "accuracy": candidate.anchor_accuracy,
                "erased_records": erased,
                "reason": "besser auf Ground-Truth-Anker + approved",
                "gate": "ask"}

    def report(self) -> dict:
        return {"current": self.current.version if self.current else None,
                "versions": [{"version": v.version, "accuracy": round(v.anchor_accuracy, 4)}
                             for v in self.versions],
                "archive_size": len(self.archive),
                "evaluator_ceiling_avoided": len(self.versions) > 1}


# ---------------------------------------------------------------------------
# Simulation: 3 Evaluator-Versionen mit steigender Schwierigkeit (Auftrag).
# Der Anker ist Auftrag (keine Paper-Zahl).
# ---------------------------------------------------------------------------
ANCHOR_ITEMS = [
    {"id": f"proof-{i:02d}", "quality": q, "truth": q >= 0.7}
    for i, q in enumerate([0.20, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90, 0.95, 0.30, 0.65], 1)
]


def _accept_all(_item) -> bool:                       # v1: schwach
    return True


def _accept_from_50(item) -> bool:                    # v2: mittel
    return item["quality"] >= 0.5


def _accept_from_70(item) -> bool:                    # v3: streng
    return item["quality"] >= 0.7


def simulate_3_evaluators() -> dict:
    """3 Evaluator-Versionen mit steigender Schwierigkeit an einem Checkpoint-Lauf."""
    rq = RedQueen(GroundTruthAnchor(items=ANCHOR_ITEMS))

    e1 = rq.checkpoint(EvaluatorVersion("", _accept_all))            # initial
    rq.record("proof-01", 0.9)                                       # v1-abhängig
    rq.record("gt-unit-1", 0.0, evaluator_independent=True)          # bleibt

    e2_pending = rq.checkpoint(EvaluatorVersion("", _accept_from_50))          # ohne approved
    e2 = rq.checkpoint(EvaluatorVersion("", _accept_from_50), approved=True)   # mit approved
    rq.record("proof-02", 0.6)
    rq.record("gt-unit-2", 0.0, evaluator_independent=True)

    e3 = rq.checkpoint(EvaluatorVersion("", _accept_from_70), approved=True)

    return {
        "epoch_1": e1,
        "epoch_2_pending": e2_pending,
        "epoch_2": e2,
        "epoch_3": e3,
        "report": rq.report(),
        "archive": rq.archive,
        "paper_gain_ground_truth": CAMBRIDGE_GRADER_GAIN,
        "checkpoints": power_of_two_checkpoints(PAPER_TOTAL_EVALS),
        "paper_params": {"eps_best_belief": EPS_BEST_BELIEF,
                         "min_anchor": MIN_ANCHOR, "checkpoint_rho": CHECKPOINT_RHO,
                         "splits": list(PAPER_SPLITS),
                         "budget_usd": dict(PAPER_BUDGET_USD),
                         "anchors": [ANCHOR_CODING, ANCHOR_GRADING]},
    }


if __name__ == "__main__":
    import json
    print(json.dumps(simulate_3_evaluators(), ensure_ascii=False, indent=2))
