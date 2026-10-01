#!/usr/bin/env python3
"""
Bias-Drift-Monitor – überwacht wiederholte self_update-Aufrufe auf Entscheidungs-Drift.

Quelle (verifiziert 2026-10-01, HTTP 200):
  - EU-KI-VO (VO (EU) 2024/1689) **Art. 15(4)**: „High-risk AI systems that
    continue to learn after being placed on the market … shall be developed in
    such a way as to eliminate or reduce as far as possible the risk of possibly
    **biased outputs influencing input for future operations (‘feedback loops’)**,
    and … that any such feedback loops are duly addressed with appropriate
    mitigation measures."
  - EC-Implementation-Guidance (2026): Dokumentation soll „performance and
    fairness metrics that will be monitored, the **thresholds beyond which the
    system will be halted or rolled back**, and the human oversight measures"
    beschreiben.

Lab-Prinzip: Mechanik = aus der Quelle; τ-Wert = Auftrag (Default 0.10, vgl.
AGENTS.md §9.1 Drift-Bound).

Drift-Maß: Total-Variation-Distanz (0..1) zwischen Entscheidungsverteilungen.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


def _norm(d: dict) -> dict:
    s = sum(max(0.0, v) for v in d.values()) or 1.0
    return {k: max(0.0, v) / s for k, v in d.items()}


def total_variation(p: dict, q: dict) -> float:
    keys = set(p) | set(q)
    return 0.5 * sum(abs(p.get(k, 0.0) - q.get(k, 0.0)) for k in keys)


@dataclass
class BiasDriftMonitor:
    """Trigger: Drift > τ → Flag + Human-Gate."""
    baseline: dict
    tau: float = 0.10            # Auftrag (vgl. §9.1)
    history: list = field(default_factory=list)
    _prev: Optional[dict] = None

    def __post_init__(self):
        self.baseline = _norm(self.baseline)

    def observe(self, distribution: dict, step: Optional[int] = None) -> dict:
        d = _norm(distribution)
        drift_baseline = total_variation(d, self.baseline)
        drift_step = total_variation(d, self._prev) if self._prev else 0.0
        flagged = drift_baseline > self.tau
        rec = {"step": step, "distribution": {k: round(v, 3) for k, v in d.items()},
               "drift_baseline": round(drift_baseline, 4),
               "drift_step": round(drift_step, 4),
               "flagged": flagged, "gate": "ask" if flagged else "ok"}
        self.history.append(rec)
        self._prev = d
        return rec

    def report(self) -> dict:
        flagged = [h for h in self.history if h["flagged"]]
        return {"steps": len(self.history), "tau": self.tau,
                "flagged_steps": [h["step"] for h in flagged],
                "max_drift": max((h["drift_baseline"] for h in self.history), default=0.0)}


def _demo() -> None:
    # Entscheidungsverteilung: approve / revise / reject
    baseline = {"approve": 0.5, "revise": 0.3, "reject": 0.2}
    mon = BiasDriftMonitor(baseline, tau=0.10)

    print("=== Bias-Drift-Monitor: 10 self_update-Aufrufe ===")
    print(f"  Baseline: {baseline} | tau={mon.tau}")
    # Jeder self_update verschiebt die Verteilung (Feedback-Schleife) Richtung 'approve'
    for i in range(1, 11):
        shift = 0.03 * i                      # kumulative Verschiebung
        dist = {"approve": 0.5 + shift, "revise": 0.3 - shift * 0.6,
                "reject": 0.2 - shift * 0.4}
        r = mon.observe(dist, step=i)
        print(f"  self_update {i:2}: drift={r['drift_baseline']:.4f} "
              f"(schritt={r['drift_step']:.4f}) -> {r['gate']}")
    print("\n  Report:", mon.report())


if __name__ == "__main__":
    _demo()
