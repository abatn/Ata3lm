#!/usr/bin/env python3
"""5-Phasen-Runner (AGENTS.md §2): Konstrukt → Akt → Observe → Compare → Revise.

Quellen (verifiziert, §6):
  - **SEAA** (arXiv:2609.17331): „a Hidden Markov Model (HMM) that encodes long-term
    behavioral and cognitive inertia as an **editable state-transition matrix**"; die
    Reflexion „updates the HMM parameters themselves". → `reflective_agent.HMMInertia`.
  - **AGENTS.md §2** (5 Phasen: Konstrukt, Akt, Observe, Compare, Revise) — Auftrag.

Integration: `reflective_agent.py` (HMM/Revise), `evaluator_version.py` (Compare/externes
Signal), `pipeline.py` (Akt). Guardrail 7: echte Funktionen; offline → NOOP.
Phasenfolge = **Auftrag** (gesetzte Ordnung, kein Paper-Claim).
"""

from __future__ import annotations

import evaluator_version
import ingestion_hook
import pipeline
import reflective_agent

PHASES = ("Konstrukt", "Akt", "Observe", "Compare", "Revise")


def _phase_konstrukt(ctx: dict) -> dict:
    """Konstrukt: π0 aus Ziel + Wissen — initialisiert die HMM-Trägheit (SEAA)."""
    ctx["hmm"] = reflective_agent.HMMInertia()
    return {"phase": "Konstrukt", "K": ctx["hmm"].K, "pi0": "uniform (SEAA Listing 1)"}


def _phase_akt(ctx: dict) -> dict:
    """Akt: π ausführen → Pipeline-Kette (Mandat→FWR→Trust→Write)."""
    res = pipeline.route_and_store(
        question=ctx["question"],
        fact=ctx["fact"],
        correct=ctx["correct"],
        classify_fn=ctx["classify_fn"],
        mandate_obj=ctx["mandate_obj"],
        now=ctx["now"],
        structured_dir=ctx["structured_dir"],
        tier3_dir=ctx["tier3_dir"],
    )
    return {"phase": "Akt", "ok": res.get("ok"), "action": res.get("action") or res.get("gate")}


def _phase_observe(ctx: dict) -> dict:
    """Observe: Traces/States festhalten (Entitäten) — ohne Wertung (Prinzip 1)."""
    ents = ingestion_hook.resolve_entities(ctx["fact"])
    return {"phase": "Observe", "entities": [e.get("span", str(e)) if isinstance(e, dict) else str(e) for e in ents]}


def _phase_compare(ctx: dict) -> dict:
    """Compare: externes Signal — Belief aus Erfolgen/Fehlern (`evaluator_version`)."""
    observed = (ctx["successes"] + ctx["failures"]) > 0
    belief = evaluator_version.best_belief(ctx["successes"], ctx["failures"])
    signal = (
        "externes Ground-Truth-Signal"
        if observed
        else "kein externes Signal (unbeobachtet) – kein Ground-Truth-Claim (§1/§6)"
    )
    return {"phase": "Compare", "belief": round(float(belief), 4), "signal": signal, "observed": observed}


def _phase_revise(ctx: dict) -> dict:
    """Revise: Reflexion aktualisiert die HMM-Übergangsmatrix (SEAA Eq. 2).

    §9: Nach einer abgelehnten `Akt`-Aktion (`deny`/`ask`) KEINE Revision.
    """
    if not ctx["results"]["Akt"].get("ok"):
        return {"phase": "Revise", "skipped": True, "reason": "Akt abgelehnt (deny/ask) – keine Revision (§9)"}
    out = ctx["hmm"].update_from_reflection(ctx["reflection_text"], delta=ctx["delta"])
    return {"phase": "Revise", "skipped": out["skipped"], "lr": out["lr"]}


_PHASE_FN = {
    "Konstrukt": _phase_konstrukt,
    "Akt": _phase_akt,
    "Observe": _phase_observe,
    "Compare": _phase_compare,
    "Revise": _phase_revise,
}


def run_recursion(
    question: str,
    fact: str,
    correct: str,
    *,
    classify_fn,
    mandate_obj,
    structured_dir,
    tier3_dir,
    now: float = 100.0,
    reflection_text: str = "",
    delta=None,
    successes: int = 0,
    failures: int = 0,
) -> dict:
    """Führt die 5 Phasen in gesetzter Reihenfolge aus und liefert die echte Spur."""
    ctx = {
        "question": question,
        "fact": fact,
        "correct": correct,
        "classify_fn": classify_fn,
        "mandate_obj": mandate_obj,
        "structured_dir": structured_dir,
        "tier3_dir": tier3_dir,
        "now": now,
        "reflection_text": reflection_text,
        "delta": delta,
        "successes": successes,
        "failures": failures,
        "hmm": None,
        "results": {},
    }
    trace = []
    for phase in PHASES:
        result = _PHASE_FN[phase](ctx)
        ctx["results"][phase] = result
        trace.append(result)
    return {"phases": list(PHASES), "results": ctx["results"], "trace": trace, "hmm": ctx["hmm"]}


if __name__ == "__main__":  # pragma: no cover - CLI
    import json

    import mandate
    import numpy as np

    mandate_obj = mandate.Mandate(
        mandate_id="recursion-runner",
        principal="Batnini",
        agent="knowledge-agent",
        actions=frozenset({"write:memory"}),
        resources=frozenset({"data/memory"}),
        amount_limit=1.0,
        max_uses=10_000,
        valid_from=0.0,
        valid_until=1e12,
        approval_threshold=0.5,
    )
    out = run_recursion(
        "Beispiel?",
        "Kontakt: max@example.com, Version 2.",
        "Version 2.",
        classify_fn=lambda q, f, c: {"class": "write-new"},
        mandate_obj=mandate_obj,
        structured_dir="/tmp/recursion-runner/structured",
        tier3_dir="/tmp/recursion-runner/tier3",
        delta=np.full((4, 4), 0.05),  # echte SEAA-Δ-Matrix (offline, ohne LLM)
        successes=3,
        failures=1,
    )
    print(json.dumps({"phases": out["phases"], "trace": out["trace"]}, ensure_ascii=False, indent=2))
