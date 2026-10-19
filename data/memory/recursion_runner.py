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

from pathlib import Path

import evaluator_version
import gate_labels
import ingestion_hook
import pipeline
import reflective_agent
import runner_state
import world_state_oracle

PHASES = ("Konstrukt", "Akt", "Observe", "Compare", "Revise")

# A4/§9 (Auftrag): Compare-Score (Erfolge/Beobachtungen) → Gate-Band.
# ≥ 95 % ⇒ allow (automatisch) · 70–94 % ⇒ ask (Mensch) · < 70 % ⇒ deny (blockiert).
REVISE_MIN_SCORE = 0.70  # ask-/deny-Grenze (Evidenz-Untergrenze)
ALLOW_MIN_SCORE = 0.95  # allow-Grenze (automatische Revision)


def _compare_gate(score: float) -> str:
    """A4/§9: Score-Band → einheitlicher Gate-Labelraum ``allow|ask|deny``.

    ≥ 0.95 ⇒ allow · ≥ 0.70 ⇒ ask (Human-Gate) · sonst ⇒ deny.
    """
    if score >= ALLOW_MIN_SCORE:
        return gate_labels.ALLOW
    if score >= REVISE_MIN_SCORE:
        return gate_labels.ASK
    return gate_labels.DENY


def _phase_konstrukt(ctx: dict) -> dict:
    """Konstrukt: π0 aus Ziel + Wissen — initialisiert die HMM-Trägheit (SEAA).

    K1: ein fortgesetzter Runner-Zustand (Restart) wird NICHT neu initialisiert.
    """
    if ctx.get("hmm") is not None:
        return {"phase": "Konstrukt", "K": ctx["hmm"].K, "pi0": "fortgesetzt (K1 Runner-State)"}
    ctx["hmm"] = reflective_agent.HMMInertia()
    return {"phase": "Konstrukt", "K": ctx["hmm"].K, "pi0": "uniform (SEAA Listing 1)"}


def _phase_akt(ctx: dict) -> dict:
    """Akt: π ausführen → Pipeline-Kette (Mandat→FWR→Trust→Freigabe→Write)."""
    res = pipeline.route_and_store(
        question=ctx["question"],
        fact=ctx["fact"],
        correct=ctx["correct"],
        classify_fn=ctx["classify_fn"],
        mandate_obj=ctx["mandate_obj"],
        now=ctx["now"],
        structured_dir=ctx["structured_dir"],
        tier3_dir=ctx["tier3_dir"],
        # R094/§9.3: Zwei-Personen-Freigabe an die Pipeline durchreichen – nur so kann
        # ein `write-new`/`write-update` (Router-Gate `ask`) tatsächlich geschrieben werden.
        self_update=ctx["self_update"],
        approvers=ctx["approvers"],
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
    """Compare: **externes** Signal (World-State-Oracle) hat Vorrang (§6).

    A4/§9: der Compare-Score wird in das Gate-Band überführt (≥ 95 % allow ·
    70–94 % ask · < 70 % deny). Ohne Beobachtung kein Ground-Truth-Signal ⇒ ``ask``.

    M3/§6: Ist ein echtes ``world_state_probe`` gesetzt, entscheidet allein das
    **Out-of-Band-Ergebnis** (`world_state_oracle.evaluate`) über ``observed``;
    der Selbstreport des Agenten (`successes`/`failures`) ist dann nur noch
    Annotation. Liefert das Probe kein Signal, gilt ``observed=False`` und es wird
    **kein** Ground-Truth-Claim erhoben (§1/§6). Ohne Probe bleibt der bisherige
    Pfad unverändert (Rückwärtskompatibilität bestehender Aufrufer/Tests).
    """
    self_report = {
        "successes": ctx["successes"],
        "failures": ctx["failures"],
        "belief": round(float(evaluator_version.best_belief(ctx["successes"], ctx["failures"])), 4),
        "annotation": "Selbstreport – kein ausreichendes Signal (§6)",
    }
    probe = ctx.get("world_state_probe")
    if probe is not None:
        oracle = world_state_oracle.evaluate(ctx.get("world_state_claim") or ctx.get("fact", ""), probe)
        observed = bool(oracle["ok"])
        if observed:
            on = oracle["successes"] + oracle["failures"]
            score = (oracle["successes"] / on) if on else 1.0
            gate = _compare_gate(score)
            signal = oracle["signal"]
        else:
            score = 0.0
            gate = gate_labels.ASK
            signal = "kein externes Signal (Oracle) – Selbstreport nur Annotation, kein Ground-Truth-Claim (§1/§6)"
        return {
            "phase": "Compare",
            "belief": round(float(evaluator_version.best_belief(oracle["successes"], oracle["failures"])), 4),
            "score": round(score, 4),
            "gate": gate,
            "signal": signal,
            "observed": observed,
            "oracle": oracle,
            "self_report": self_report,
        }
    n = ctx["successes"] + ctx["failures"]
    observed = n > 0
    belief = evaluator_version.best_belief(ctx["successes"], ctx["failures"])
    score = (ctx["successes"] / n) if n else 0.0
    gate = _compare_gate(score) if observed else gate_labels.ASK
    signal = (
        "Aufrufer-Report (kein externes Probe)"
        if observed
        else "kein externes Signal (unbeobachtet) – kein Ground-Truth-Claim (§1/§6)"
    )
    return {
        "phase": "Compare",
        "belief": round(float(belief), 4),
        "score": round(score, 4),
        "gate": gate,
        "signal": signal,
        "observed": observed,
        "self_report": self_report,
    }


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
    # N7/§6: Liegt ein Oracle-Signal vor (Compare mit `world_state_probe`), entscheidet
    # die **Oracle-Evidenz** – Compare und Revise nutzen damit DIESELBE Quelle; der
    # Selbstreport (`successes`/`failures`) ist nur Annotation. Ohne Probe bleibt der
    # bisherige Selbstreport-Pfad unverändert (Rückwärtskompatibilität).
    oracle = vergleich.get("oracle")
    if oracle is not None:
        score = float(vergleich.get("score", 0.0))
        positive = int(oracle.get("successes", 0)) >= 1
    else:
        n = ctx["successes"] + ctx["failures"]
        score = (ctx["successes"] / n) if n else 0.0
        positive = ctx["successes"] >= 1
    # §9.1d/R10/A4: passende Evidenz = externes Signal mit ≥ 1 positivem Beleg und
    # Score ≥ 70 % (1 Erfolg / 99 Fehler lernt nicht).
    evidence_ok = bool(vergleich.get("observed")) and positive and score >= REVISE_MIN_SCORE
    if not evidence_ok:
        return {
            "phase": "Revise",
            "skipped": True,
            "reason": (
                f"keine passende Evidenz (§9.1d/R10): Score {score:.2f} < {REVISE_MIN_SCORE:.2f} "
                "oder Signal negativ/unzureichend – keine Revision"
            ),
        }
    # A4/§9: Compare-Band in allow/ask/deny. Im ask-Band (70–94 %) NUR mit
    # menschlicher Freigabe (`revise_approved`) revisieren; `deny` (< 70 %) nie.
    compare_gate = gate_labels.normalize(vergleich.get("gate", _compare_gate(score)))
    if compare_gate == gate_labels.DENY:
        return {
            "phase": "Revise",
            "skipped": True,
            "reason": f"Compare-Gate deny: Score {score:.2f} < {REVISE_MIN_SCORE:.2f} – keine Revision (§9)",
        }
    if compare_gate == gate_labels.ASK and not ctx.get("revise_approved"):
        return {
            "phase": "Revise",
            "skipped": True,
            "reason": (
                f"Compare-Gate ask: Score {score:.2f} im Band 70–94 % – Revision nur mit "
                "menschlicher Freigabe (`approved`, §9)"
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
    revise_approved: bool = False,
    self_update: bool = False,
    approvers=None,
    state_path=None,
    consolidation_state_path=None,
    world_state_probe=None,
    world_state_claim=None,
) -> dict:
    """Führt die 5 Phasen in gesetzter Reihenfolge aus und liefert die echte Spur.

    K1: `state_path` setzt den geteilten Runner-Zustand (inkl. HMM) fort und
    persistiert ihn danach – gemeinsamer Zustand mit dem 8-Stufen-Runner.

    **Interface-Änderung (§9-pflichtig, kenntlich gemacht):** `revise_approved`
    (A4) schaltet die HMM-Revision im **ask-Band** (Compare-Score 70–94 %) frei; ohne
    Freigabe bleibt sie dort aus (§9, 70–94 % ⇒ Human-Gate). `Compare` meldet nun
    `score` + `gate` (allow/ask/deny).

    **Interface-Änderung (§9-pflichtig, kenntlich gemacht, R094):** neue optionale
    Parameter `self_update` (Default `False`) und `approvers` (Default `None`). Sie
    werden in der Akt-Phase an `pipeline.route_and_store(self_update=..., approvers=...)`
    durchgereicht; nur mit `self_update=True` **und** einer §9.3-Zwei-Personen-Freigabe
    (`approvers` mit ≥ 2 distinkten Personen) wird ein `write-new`/`write-update`
    (Router-Gate `ask`) geschrieben. Default `False`/`None` ⇒ **exakt altes Verhalten**
    (kein Write ohne Freigabe, Gate bleibt `ask`).

    **Interface-Änderung (§9-pflichtig, kenntlich gemacht):** neuer optionaler
    Parameter `consolidation_state_path` (Auftrag §10.3) – ist er gesetzt, sammelt der
    Lauf am Ende **lesend** konsolidierbare Fakten (`slow_consolidation.collect_pending`)
    und hängt sie als `pending_consolidation` an das Ergebnis. Kein Write/Flush im
    Lauf (§9 Human-Gate); Default `None` ⇒ unverändertes Verhalten.

    **Interface-Änderung (§9-pflichtig, kenntlich gemacht, M3):** neue optionale
    Parameter `world_state_probe` (echtes externes Callable, World-State-Oracle)
    und `world_state_claim` (zu prüfende Behauptung; Default: `fact`). Ist
    `world_state_probe` gesetzt, entscheidet das **externe** Ergebnis über
    `Compare.observed`; der Selbstreport (`successes`/`failures`) ist nur noch
    Annotation (§6). Default `None` ⇒ unverändertes Verhalten (Rückwärtskompatibilität).
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
        "revise_approved": revise_approved,
        "self_update": self_update,
        "approvers": approvers,
        "world_state_probe": world_state_probe,
        "world_state_claim": world_state_claim,
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
    out = {
        "phases": list(PHASES),
        "results": ctx["results"],
        "trace": trace,
        "hmm": ctx["hmm"],
        "state_save": state_save,
    }
    if consolidation_state_path is not None:  # §10.3 Optional-Hook (lesend, kein Write)
        import slow_consolidation

        out["pending_consolidation"] = slow_consolidation.collect_pending(
            tier3_dir, Path(tier3_dir) / "provenance.jsonl", state_path=consolidation_state_path
        )
    return out


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
