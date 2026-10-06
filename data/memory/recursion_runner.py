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
import gate_labels
import ingestion_hook
import pipeline
import reflective_agent
import runner_state

PHASES = ("Konstrukt", "Akt", "Observe", "Compare", "Revise")

# R10/§9: Revision nur bei Score ≥ 70 % (automatisches Gate §9: < 70 % = blockiert).
REVISE_MIN_SCORE = 0.70


def _phase_konstrukt(ctx: dict) -> dict:
    """Konstrukt: π0 aus Ziel + Wissen — initialisiert die HMM-Trägheit (SEAA).

    K1: ein fortgesetzter Runner-Zustand (Restart) wird NICHT neu initialisiert.
    """
    if ctx.get("hmm") is not None:
        return {"phase": "Konstrukt", "K": ctx["hmm"].K, "pi0": "fortgesetzt (K1 Runner-State)"}
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
    # K6/B5: `gate` im einheitlichen Labelraum (allow|ask|deny) mitführen.
    return {
        "phase": "Akt",
        "ok": res.get("ok"),
        "action": res.get("action") or res.get("gate"),
        "gate": gate_labels.normalize(res.get("gate")),
    }


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
    B6 (K6): Revision braucht eine **ausdrücklich zulässige Entscheidung**
    (`ok` AND `gate == "allow"`) **und** passende, zur Änderung gehörende
    Evidenz (§9.1d). `Compare.observed=True` genügt **nicht** – Beobachtungen
    können negativ/unzureichend sein (Review-Korrektur 4).
    """
    akt = ctx["results"]["Akt"]
    gate = gate_labels.normalize(akt.get("gate"))
    if not (akt.get("ok") and gate_labels.is_allow(gate)):
        return {
            "phase": "Revise",
            "skipped": True,
            "reason": f"Akt nicht ausdrücklich zulässig (ok={akt.get('ok')}, gate={gate}) – keine Revision (§9)",
        }
    vergleich = ctx["results"]["Compare"]
    # §9.1d: passende Evidenz = externes Signal mit ≥ 1 positivem Beleg.
    n = ctx["successes"] + ctx["failures"]
    score = (ctx["successes"] / n) if n else 0.0
    # R10/§9: Score < 70 % ⇒ keine Revision (1 Erfolg / 99 Fehler lernt nicht).
    evidence_ok = bool(vergleich.get("observed")) and ctx["successes"] >= 1 and score >= REVISE_MIN_SCORE
    if not evidence_ok:
        return {
            "phase": "Revise",
            "skipped": True,
            "reason": (
                f"keine passende Evidenz (§9.1d/R10): Score {score:.2f} < {REVISE_MIN_SCORE:.2f} "
                "oder Signal negativ/unzureichend – keine Revision"
            ),
        }
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
    state_path=None,
) -> dict:
    """Führt die 5 Phasen in gesetzter Reihenfolge aus und liefert die echte Spur.

    K1: `state_path` setzt den geteilten Runner-Zustand (inkl. HMM) fort und
    persistiert ihn danach – gemeinsamer Zustand mit dem 8-Stufen-Runner.
    """
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
    # K1: geteilter persistenter Runner-Zustand – vor dem Lauf fortsetzen (Restart)
    resumed, rec_wm, rec_graph = None, None, None
    if state_path is not None:
        resumed = runner_state.load(state_path)
        if resumed is not None:
            rec = runner_state.reconstruct(resumed)
            ctx["hmm"], rec_wm, rec_graph = rec["hmm"], rec["wm"], rec["graph"]
    trace = []
    for phase in PHASES:
        result = _PHASE_FN[phase](ctx)
        ctx["results"][phase] = result
        trace.append(result)
    state_save = None
    if state_path is not None:
        # R18: ein abgelehnter Akt persistiert KEINEN neuen Wissenszustand (§9).
        akt_ok = bool(ctx["results"].get("Akt", {}).get("ok"))
        if not akt_ok:
            state_save = {
                "ok": False,
                "path": str(state_path),
                "reason": "Akt abgelehnt (ok=False) – kein neuer Wissenszustand persistiert (R18/§9)",
            }
        else:
            # R06: CAS über den geladenen Revisionsstand; R07: Rückgabe wird berichtet.
            state_save = runner_state.save(
                runner_state.snapshot(
                    wm=rec_wm,
                    graph=rec_graph,
                    hmm=ctx["hmm"],
                    drift_reference=(resumed or {}).get("drift", {}).get("reference"),
                    schema=(resumed or {}).get("schema", {}),
                    open_approvals=(resumed or {}).get("open_approvals", []),
                    runner="recursion-runner",
                ),
                state_path,
                expected_rev=(resumed or {}).get("rev", 0),
            )
    return {
        "phases": list(PHASES),
        "results": ctx["results"],
        "trace": trace,
        "hmm": ctx["hmm"],
        "state_save": state_save,
    }


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
