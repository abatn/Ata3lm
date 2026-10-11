"""Per-Item Acceptance-Gate auf Basis des SAGE-Paarvergleichs.

Quelle: SAGE arXiv:2609.36043; AGENTS.md §9.1d/§6.

Ersetzt den naiven Aggregat-Vergleich (§9.1d, Rekursion 103): Statt Mittelwerte
über alle Items zu vergleichen, zählt das Gate **pro Item** Sieg/Niederlage/
Gleichstand (per-item paired comparison) und prüft mit einem einseitigen
Vorzeichentest (sign_test_p), ob der Kandidat systematisch gewinnt oder
verliert. Ein Bootstrap liefert das Konfidenzintervall der Delta-Rate. Ist der
Test nicht signifikant, **enthält sich** das Gate ("abstains otherwise").

Nur Python-Standardbibliothek (``math``, ``random``), deterministisch über
``seed``. Kein Netzwerk, kein Fake.
"""

from __future__ import annotations

import math
import random


def per_item_compare(base: list[bool], cand: list[bool]) -> dict:
    """Paarvergleich zweier gleich langer boolescher Item-Listen.

    Zählt je Item einen Sieg (``cand=True``, ``base=False``), eine Niederlage
    (``base=True``, ``cand=False``) oder einen Gleichstand. Gibt neben den
    Zählern auch die Roh-Paare ``pairs`` (Index, base, cand) zurück.

    Quelle: SAGE arXiv:2609.36043; AGENTS.md §9.1d/§6.
    """
    if len(base) != len(cand):
        raise ValueError("base and cand must have equal length")
    wins = losses = ties = 0
    pairs = []
    for i, (b, c) in enumerate(zip(base, cand)):
        b = bool(b)
        c = bool(c)
        if c and not b:
            wins += 1
        elif b and not c:
            losses += 1
        else:
            ties += 1
        pairs.append((i, b, c))
    return {"n": len(base), "wins": wins, "losses": losses, "ties": ties, "pairs": pairs}


def sign_test_p(wins: int, losses: int) -> float:
    """Einseitiger exakter Vorzeichentest (one-sided paired test).

    P(X >= wins) mit X ~ Binomial(wins + losses, 0.5). Bindungen (ties) fließen
    nicht ein. Ohne entschiedene Paare ist ``p = 1.0`` (kein Signal).

    Quelle: SAGE arXiv:2609.36043; AGENTS.md §9.1d/§6.
    """
    n = wins + losses
    if n == 0:
        return 1.0
    tail = sum(math.comb(n, k) for k in range(wins, n + 1))
    return tail / (2**n)


def bootstrap_delta_ci(
    base: list[bool],
    cand: list[bool],
    *,
    n_resamples: int = 10000,
    alpha: float = 0.05,
    seed: int = 0,
) -> dict:
    """Bootstrap-Konfidenzintervall der Delta-Rate (cand - base).

    ``delta`` ist die beobachtete Differenz der Trefferraten; ``lo``/``hi``
    stammen aus der perzentilen Bootstrap-Verteilung (``n_resamples``), gezogen
    mit deterministischem ``random.Random(seed)``.

    Quelle: SAGE arXiv:2609.36043; AGENTS.md §9.1d/§6.
    """
    if len(base) != len(cand) or not base:
        raise ValueError("base and cand must be non-empty and equal length")
    rng = random.Random(seed)
    n = len(base)
    deltas = []
    for _ in range(n_resamples):
        idx = [rng.randrange(n) for _ in range(n)]
        d = sum(1 for i in idx if cand[i]) / n - sum(1 for i in idx if base[i]) / n
        deltas.append(d)
    deltas.sort()
    delta = sum(1 for c in cand if c) / n - sum(1 for b in base if b) / n
    lo = deltas[int((alpha / 2) * n_resamples)]
    hi = deltas[min(n_resamples - 1, int((1 - alpha / 2) * n_resamples))]
    return {"delta": delta, "lo": lo, "hi": hi, "n_resamples": n_resamples, "seed": seed}


def evaluate(
    base: list[bool],
    cand: list[bool],
    *,
    alpha: float = 0.05,
    n_resamples: int = 10000,
    seed: int = 0,
) -> dict:
    """Entscheidet ``accept`` / ``reject`` / ``abstain`` aus Paartest + Bootstrap.

    Zwei **einseitige** Vorzeichentests (SAGE: per-item paired, one-sided):
    ``p_win = sign_test_p(wins, losses)`` (Vorteil) und
    ``p_loss = sign_test_p(losses, wins)`` (Nachteil). ``accept`` nur bei
    signifikantem Vorteil (``p_win <= alpha``), ``reject`` bei signifikantem
    Nachteil (``p_loss <= alpha``), sonst ``abstain`` (SAGE: "abstains
    otherwise"). Beide Richtungen sind damit bei Default-``alpha`` erreichbar.

    Quelle: SAGE arXiv:2609.36043; AGENTS.md §9.1d/§6.
    """
    cmp = per_item_compare(base, cand)
    p_win = sign_test_p(cmp["wins"], cmp["losses"])
    p_loss = sign_test_p(cmp["losses"], cmp["wins"])
    ci = bootstrap_delta_ci(base, cand, n_resamples=n_resamples, alpha=alpha, seed=seed)
    if p_win <= alpha:
        decision = "accept"
    elif p_loss <= alpha:
        decision = "reject"
    else:
        decision = "abstain"
    return {
        "decision": decision,
        "p": p_win,
        "p_win": p_win,
        "p_loss": p_loss,
        "delta": ci["delta"],
        "ci": [ci["lo"], ci["hi"]],
        "compare": cmp,
        "alpha": alpha,
    }
