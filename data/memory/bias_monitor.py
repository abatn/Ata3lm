#!/usr/bin/env python3
"""
Bias-Drift-Monitor – JSD-basierter Drift-Index (DI) für self_update-Feedback-Schleifen.

Quellen (verifiziert 2026-10-01, HTTP 200):
  - **WhyLab – A Causal Audit Framework for Stable Agent Self-Improvement** (2026):
    C1 **information-theoretic drift detection** (Drift Index), C2 E-value ×
    Sensitivitätsfilter, C3 **Lyapunov-bounded adaptive damping**.
    Code: https://github.com/neogenesislab/WhyLab-NeurIPS2026
  - EU-KI-VO (VO (EU) 2024/1689) **Art. 15(4)**: biased outputs → feedback loops →
    mitigieren; EC-Guidance: fairness metrics + thresholds + human oversight.
  - Agent Drift (arXiv:2601.04170): Jensen-Shannon-Divergenz zur Drift-Messung.

Lab-Prinzip: JSD + Drift-Index + Lyapunov-Damping = **belegt** (WhyLab/Agent-Drift);
die konkrete Entropie-Gewichtung, `w_max` und τ sind **Auftrag**.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Optional


def _norm(d: dict) -> dict:
    s = sum(max(0.0, v) for v in d.values()) or 1.0
    return {k: max(0.0, v) / s for k, v in d.items()}


def entropy(p: dict) -> float:
    """Shannon-Entropie (Basis 2) einer Verteilung."""
    return -sum(v * math.log2(v) for v in p.values() if v > 0)


def jsd(p: dict, q: dict) -> float:
    """Jensen-Shannon-Divergenz (Basis 2), symmetrisch, Wertebereich [0, 1]."""
    keys = set(p) | set(q)
    m = {k: 0.5 * (p.get(k, 0.0) + q.get(k, 0.0)) for k in keys}

    def _kl(a: dict, b: dict) -> float:
        s = 0.0
        for k in keys:
            ak, bk = a.get(k, 0.0), b.get(k, 0.0)
            if ak > 0 and bk > 0:
                s += ak * math.log2(ak / bk)
        return s

    return 0.5 * _kl(p, m) + 0.5 * _kl(q, m)


def capped_simplex(w: dict, w_max: float = 0.6, iters: int = 100) -> dict:
    """Projiziert Gewichte auf das „capped simplex" {Σw=1, 0≤w_i≤w_max}.

    Begrenzt den Einfluss einzelner Signale (w_max = 0.6 → Auftrag).
    """
    keys = list(w)
    if not keys:
        return {}
    total = sum(max(0.0, w[k]) for k in keys) or 1.0
    v = {k: max(0.0, w[k]) / total for k in keys}
    # iteratives Cappen + Umverteilen
    for _ in range(iters):
        over = [k for k in keys if v[k] > w_max]
        if not over:
            break
        excess = sum(v[k] - w_max for k in over)
        for k in over:
            v[k] = w_max
        free = [k for k in keys if v[k] < w_max]
        if not free:
            break
        add = excess / len(free)
        for k in free:
            v[k] += add
    return v


@dataclass
class BiasDriftMonitor:
    """Trigger: Drift-Index > τ → Flag + Human-Gate."""

    baseline: dict
    tau: float = 0.10  # Auftrag
    w_max: float = 0.6  # Auftrag (Capped Simplex)
    history: list = field(default_factory=list)
    _prev: Optional[dict] = None

    def __post_init__(self):
        self.baseline = _norm(self.baseline)

    def drift_index(self, current: dict, reference: dict) -> dict:
        """JSD-basierter Drift-Index (DI = JSD) + entropie-gewichtete, capped-simplex-
        aggregierte Kategorie-Signale (|Δp_k|)."""
        cur, ref = _norm(current), _norm(reference)
        keys = set(cur) | set(ref)
        # Signal pro Kategorie: |Δp_k|
        signals = {k: abs(cur.get(k, 0.0) - ref.get(k, 0.0)) for k in keys}
        # Entropie-Gewichte: w_k ∝ Entropie-Beitrag von k in der Referenz
        contrib = {k: (-ref[k] * math.log2(ref[k]) if ref.get(k, 0.0) > 0 else 0.0) for k in keys}
        w = capped_simplex(contrib, self.w_max)  # w_max = 0.6
        weighted_shift = sum(w[k] * signals[k] for k in keys)
        DI = jsd(cur, ref)  # JSD-basiert (ersetzt TV)
        return {
            "DI": round(DI, 4),
            "jsd": round(DI, 4),
            "weighted_shift": round(weighted_shift, 4),
            "signals": {k: round(v, 4) for k, v in signals.items()},
            "weights": {k: round(v, 4) for k, v in w.items()},
        }

    def observe(self, distribution: dict, step: Optional[int] = None) -> dict:
        d = _norm(distribution)
        di_base = self.drift_index(d, self.baseline)
        di_step = self.drift_index(d, self._prev) if self._prev else {"DI": 0.0}
        metric = di_base["DI"]  # DI = JSD
        flagged = metric > self.tau
        damping = max(0.0, 1.0 - metric * 10)  # Lyapunov-bounded adaptive damping (Auftrag)
        rec = {
            "step": step,
            "distribution": {k: round(v, 3) for k, v in d.items()},
            "DI": di_base["DI"],
            "jsd": di_base["jsd"],
            "weighted_shift": di_base["weighted_shift"],
            "step_DI": di_step["DI"],
            "damping": round(damping, 4),
            "flagged": flagged,
            "gate": "ask" if flagged else "ok",
        }
        self.history.append(rec)
        self._prev = d
        return rec

    def report(self) -> dict:
        flagged = [h for h in self.history if h["flagged"]]
        return {
            "steps": len(self.history),
            "tau": self.tau,
            "w_max": self.w_max,
            "flagged_steps": [h["step"] for h in flagged],
            "max_DI": max((h["DI"] for h in self.history), default=0.0),
            "max_jsd": max((h["jsd"] for h in self.history), default=0.0),
        }


def _demo() -> None:
    baseline = {"approve": 0.5, "revise": 0.3, "reject": 0.2}
    mon = BiasDriftMonitor(baseline, tau=0.02, w_max=0.6)  # tau für JSD-Bereich (Auftrag)

    print("=== JSD-basierter Drift-Index: 10 self_update-Aufrufe ===")
    print(f"  Baseline: {baseline} | tau={mon.tau} | w_max={mon.w_max}")
    for i in range(1, 11):
        shift = 0.03 * i
        dist = {"approve": 0.5 + shift, "revise": 0.3 - shift * 0.6, "reject": 0.2 - shift * 0.4}
        r = mon.observe(dist, step=i)
        print(
            f"  self_update {i:2}: DI(JSD)={r['DI']:.4f} weighted={r['weighted_shift']:.4f} "
            f"damping={r['damping']:.3f} -> {r['gate']}"
        )
    print("\n  Report:", mon.report())
    print(
        "\n  Beispiel Signale/Gewichte (capped simplex w_max=0.6):",
        mon.drift_index({"approve": 0.8, "revise": 0.1, "reject": 0.1}, baseline),
    )


if __name__ == "__main__":
    _demo()
