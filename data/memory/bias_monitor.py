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
  - **Goal Drift Index (GDI) / SAHOO** (arXiv:2603.06333, ICLR-2026-Workshop;
    in `AGENTS.md` §9.1c zitiert): Appendix B, Gl. 5–16 – Semantic/Lexical/
    Structural/Distributional Drift → GDI, Gewichts-/τ-Kalibrierung, Bootstrap-CI.

Lab-Prinzip: JSD + Drift-Index + Lyapunov-Damping = **belegt** (WhyLab/Agent-Drift);
die konkrete Entropie-Gewichtung, `w_max` und τ sind **Auftrag**.

GDI-Ergänzung (Rekursion 082): `semantic_drift`, `lexical_drift`,
`structural_drift`, `distributional_drift` sowie `gdi`, `calibrate_weights`,
`calibrate_tau`, `bootstrap_ci` setzen **Gl. 5–16** der Quelle arXiv:2603.06333
um. **Belegt** sind ausschließlich die Formeln/Verfahren der Quelle (Gl. 5–16);
die **Default-Gewichte** `0.38/0.12/0.21/0.29` stammen aus der Tabelle des
Haupttexts und sind im Code als **Auftrag**-Default verdrahtet. Die bestehende
JSD-`BiasDriftMonitor` (WhyLab/Agent-Drift) bleibt unverändert erhalten.

Paper-Inkonsistenz (ehrlich, nicht aufgelöst): Gl. 14 definiert die
Gewichts-Kalibrierung als `w* = argmax_w Σ_i AUC(GDI_i(w), y_i^drift)`
(AUC-Maximierung), während der begleitende Haupttext zusätzlich „logistic
regression" nennt. Beide Angaben sind **nicht** deckungsgleich; implementiert
ist die explizite Gleichung (AUC über Rang-/Paar-Statistik, kein sklearn).
Wo die Quelle nichts sagt (numerischer τ-Wert, Bootstrap-**Statistik** je
Replikat), wird das im Code als „nicht gefunden" kenntlich gemacht.

Gate (K6/B5): `gate` nutzt den einheitlichen Labelraum `allow|ask|deny`
(`gate_labels`) – Flag ⇒ `ask` (Human-Gate, §9.1c), sonst `allow`.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import Optional

import gate_labels


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


# --------------------------------------------------------------------------- #
# GDI – Goal Drift Index (Quelle: arXiv:2603.06333, Gl. 5–16)
# --------------------------------------------------------------------------- #
# Belegt: die Gleichungen Gl. 5–16 (Semantic/Lexical/Structural/Distributional
#         Drift, GDI-Aggregation, AUC-Gewichts- und F1-τ-Kalibrierung, CI).
# Auftrag: Default-Gewichte aus dem Haupttext (sem .38 · lex .12 · struct .21 ·
#          dist .29) sowie die defensive Behandlung leerer Eingaben.

_WEIGHT_KEYS = ("sem", "lex", "struct", "dist")

# Referenz-Gewichte (Haupttext, Tabelle): sem .38 · lex .12 · struct .21 · dist .29
DEFAULT_WEIGHTS = {"sem": 0.38, "lex": 0.12, "struct": 0.21, "dist": 0.29}


def semantic_drift(e0, et, eps=1e-12):
    """Gl. 5–8: Semantic Drift `Δ_sem = (1 − s_cos) / 2` ∈ [0, 1].

    Normierung `ê = e / (||e|| + ε)` (Gl. 5/6), `s_cos = ê_0 · ê_t` (Gl. 7).
    """
    n0 = math.sqrt(sum(x * x for x in e0))
    nt = math.sqrt(sum(x * x for x in et))
    e0h = [x / (n0 + eps) for x in e0]
    eth = [x / (nt + eps) for x in et]
    s_cos = sum(a * b for a, b in zip(e0h, eth))
    return (1.0 - s_cos) / 2.0


def _to_dist(x):
    """Wandelt ein Dict oder eine Tokenliste in eine normierte Verteilung (Gl. 9)."""
    if isinstance(x, dict):
        return _norm(x)
    counts: dict = {}
    for tok in x:
        counts[tok] = counts.get(tok, 0.0) + 1.0
    return _norm(counts)


def lexical_drift(p0, pt):
    """Gl. 9: Lexical Drift `Δ_lex = JSD(P_0 || P_t)` (Basis 2, [0, 1])."""
    return jsd(_to_dist(p0), _to_dist(pt))


def structural_drift(s0, st, eps=1e-12):
    """Gl. 10: `Δ_struct = (1/K) · Σ_k min(1, |s0_k − st_k| / (s0_k + ε))`.

    `s0`/`st` = Dicts Feature→Wert; K = Anzahl der Features (Union). Fehlende
    Features zählen als 0. Leere Feature-Menge ⇒ 0.0 (defensiv, Auftrag).
    """
    keys = set(s0) | set(st)
    if not keys:
        return 0.0
    total = 0.0
    for k in keys:
        base = s0.get(k, 0.0)
        total += min(1.0, abs(base - st.get(k, 0.0)) / (base + eps))
    return total / len(keys)


def distributional_drift(sample0, samplet):
    """Gl. 11: `Δ_dist = W(P_baseline, P_current)` – 1-D-Wasserstein, closed form.

    Beide Stichproben werden sortiert und paarweise verglichen:
    `mean(|a_i − b_i|)` (kein scipy). Ungleich lange Stichproben werden auf die
    kürzere Länge beschnitten (closed form).
    """
    a, b = sorted(sample0), sorted(samplet)
    n = min(len(a), len(b))
    if n == 0:
        return 0.0
    return sum(abs(a[i] - b[i]) for i in range(n)) / n


def _resolve_weights(weights):
    """Prüft Gl. 13 (`Σw = 1`, `w_i ∈ [0, 1]`) und liefert die Gewichte."""
    w = dict(DEFAULT_WEIGHTS) if weights is None else dict(weights)
    missing = [k for k in _WEIGHT_KEYS if k not in w]
    if missing:
        raise ValueError(f"Gewichte fehlen für: {missing} (Gl. 12/13)")
    if any(w[k] < 0.0 or w[k] > 1.0 for k in _WEIGHT_KEYS):
        raise ValueError("Gewichte müssen in [0, 1] liegen (Gl. 13)")
    if abs(sum(w[k] for k in _WEIGHT_KEYS) - 1.0) > 1e-9:
        raise ValueError("Gewichte müssen zu 1 summieren (Gl. 13)")
    return {k: w[k] for k in _WEIGHT_KEYS}


def gdi(sem, lex, stru, dist, weights=None):
    """Gl. 12–13: `GDI = w_s·Δ_sem + w_l·Δ_lex + w_st·Δ_struct + w_d·Δ_dist`.

    Default-Gewichte = Referenz-Gewichte des Haupttexts (Auftrag).
    """
    w = _resolve_weights(weights)
    return w["sem"] * sem + w["lex"] * lex + w["struct"] * stru + w["dist"] * dist


def _auc(scores, labels):
    """AUC über Rang-/Paar-Statistik (Mann-Whitney; kein sklearn).

    `AUC = P(score_pos > score_neg) + ½·P(score_pos = score_neg)`. Ohne beide
    Klassen ist die AUC nicht definiert ⇒ 0.5.
    """
    pos = [s for s, y in zip(scores, labels) if y == 1]
    neg = [s for s, y in zip(scores, labels) if y == 0]
    if not pos or not neg:
        return 0.5
    wins = 0.0
    for p in pos:
        for n in neg:
            if p > n:
                wins += 1.0
            elif p == n:
                wins += 0.5
    return wins / (len(pos) * len(neg))


def _simplex_grid(step=0.05):
    """Gitter über den Simplex `{Σw = 1, w_i ≥ 0}` für Gl. 14 (Default w-Schritt)."""
    n = max(1, int(round(1.0 / step)))
    grid = []
    for i in range(n + 1):
        for j in range(n + 1 - i):
            for k in range(n + 1 - i - j):
                m = n - i - j - k
                grid.append({"sem": i / n, "lex": j / n, "struct": k / n, "dist": m / n})
    return grid


def calibrate_weights(scores, labels, grid=None):
    """Gl. 14: `w* = argmax_w Σ_i AUC(GDI_i(w), y_i^drift)`.

    `scores` = Liste von Dicts mit den vier Drift-Signalen je Instanz,
    `labels` = `y_i^drift ∈ {0,1}`; `grid` = Liste von Gewichts-Dicts
    (Default = 0.05-Simplex-Gitter). Ties ⇒ erster Treffer der Gitterreihenfolge.
    Rückgabe: `{"weights": w*, "auc": AUC(w*)}`.

    Paper-Inkonsistenz (siehe Modul-Docstring): Gl. 14 schreibt AUC-Optimierung
    vor, der Haupttext nennt daneben „logistic regression" – implementiert ist
    die explizite Gleichung (AUC), das Zitat wird nicht erfunden.
    """
    if len(scores) != len(labels):
        raise ValueError("scores und labels müssen gleich lang sein")
    if grid is None:
        grid = _simplex_grid()
    best_w = None
    best_auc = -1.0
    for w in grid:
        wc = _resolve_weights(w)
        values = [
            wc["sem"] * sc["sem"] + wc["lex"] * sc["lex"] + wc["struct"] * sc["struct"] + wc["dist"] * sc["dist"]
            for sc in scores
        ]
        a = _auc(values, labels)
        if a > best_auc:
            best_auc = a
            best_w = dict(wc)
    return {"weights": best_w, "auc": best_auc}


def _f1(preds, labels):
    """F1-Score aus binären Vorhersagen und Labels (0 bei leerem Nenner)."""
    tp = sum(1 for p, y in zip(preds, labels) if p == 1 and y == 1)
    fp = sum(1 for p, y in zip(preds, labels) if p == 1 and y == 0)
    fn = sum(1 for p, y in zip(preds, labels) if p == 0 and y == 1)
    denom = 2 * tp + fp + fn
    if denom == 0:
        return 0.0
    return 2.0 * tp / denom


def calibrate_tau(gdi_values, labels):
    """Gl. 15: `τ* = argmax_τ F1(GDI > τ, y^drift)`.

    Kandidaten = eindeutige GDI-Werte (aufsteigend); bei gleichem F1 gewinnt der
    kleinere τ (erster Treffer). Rückgabe: `{"tau": τ*, "f1": F1_max}`.
    """
    if len(gdi_values) != len(labels):
        raise ValueError("gdi_values und labels müssen gleich lang sein")
    if not gdi_values:
        return {"tau": 0.0, "f1": 0.0}
    best_tau = gdi_values[0]
    best_f1 = -1.0
    for tau in sorted(set(gdi_values)):
        preds = [1 if v > tau else 0 for v in gdi_values]
        f1 = _f1(preds, labels)
        if f1 > best_f1:
            best_f1 = f1
            best_tau = tau
    return {"tau": best_tau, "f1": best_f1}


def _quantile(sorted_vals, q):
    """Empirisches Quantil (lineare Interpolation zwischen Order-Statistiken)."""
    n = len(sorted_vals)
    if n == 1:
        return sorted_vals[0]
    pos = q * (n - 1)
    lo = int(math.floor(pos))
    hi = int(math.ceil(pos))
    frac = pos - lo
    return sorted_vals[lo] * (1.0 - frac) + sorted_vals[hi] * frac


def bootstrap_ci(values, B=2000, alpha=0.05):
    """Gl. 16: `95%-CI` = 0.025-/0.975-Quantile von `B` Bootstrap-Replikaten.

    Nichtparametrisch (Resampling mit Zurücklegen). Rückgabe `{"lo", "hi"}`.

    Anmerkung (ehrlich): Gl. 16 legt nur Quantile und `B≈2000` fest; die
    **Statistik je Replikat** wird in der zitierten Gleichung nicht benannt
    („nicht gefunden") – hier der Mittelwert.
    """
    vals = list(values)
    if not vals:
        raise ValueError("values darf nicht leer sein")
    n = len(vals)
    reps = sorted(sum(vals[random.randrange(n)] for _ in range(n)) / n for _ in range(B))
    return {"lo": _quantile(reps, alpha / 2.0), "hi": _quantile(reps, 1.0 - alpha / 2.0)}


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
            # K6/B5: einheitlicher Labelraum `allow|ask|deny` (gate_labels).
            "gate": gate_labels.ASK if flagged else gate_labels.ALLOW,
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
