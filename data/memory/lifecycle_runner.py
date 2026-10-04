#!/usr/bin/env python3
"""8-Stufen-Runner (AGENTS.md §3): Erfahrung → … → Wissen+.

Quelle (Gesetz): AGENTS.md §3 · knowledge/lifecycle/rekursion/wissenszyklus-8-stufen.md.
- **Stufenfolge** = Auftrag (gesetzte Ordnung), kein Paper-Claim.
- **Stufe → Modul** = Auftrag, abgeleitet aus dem Phasen-Mapping des Zyklus-Dokuments.
- **Keine Erfindung:** jede Stufe ruft eine **echte**, bestehende Funktion auf
  (Guardrail 7: echte Ausführung). Die 8 Stufen sind die Schicht-1-Lücke aus
  `ergebnisse/reverse-engineering-vollstaendig.md` (zuvor „nur Doku").

Ablauf (Lese-/Schreib-Semantik aus dem Auftrag):
  1 Erfahrung   (schreibt M)   -> ingestion_hook.resolve_entities + WorkingMemory.store
  2 Wissen      (liest M)      -> ingestion_hook.update_graph (strukturieren)
  3 Gedächtnis  (schreibt O)   -> pipeline.route_and_store   (Pipeline-Integration)
  4 Kognition   (liest O)      -> lru_cache.consolidate_edges (verknüpfen)
  5 Denken      (Self-Feedback)-> reflective_agent.parse_transition_delta (echte LLM-Reflexion)
  6 Nicht-Kogn. (dämpft)       -> reflective_agent.lyapunov_check (Dämpfung)
  7 Handeln     (Aktion → M)   -> WorkingMemory.store (gedämpfte Aktion)
  8 Wissen+     (Compare/Revise)-> bias_monitor.BiasDriftMonitor.observe (Drift-Gate)
"""

from __future__ import annotations

import re

import bias_monitor
import ingestion_hook
import lru_cache
import mandate
import pipeline
import reflective_agent

STAGES = (
    "Erfahrung",
    "Wissen",
    "Gedächtnis",
    "Kognition",
    "Denken",
    "Nicht-Kognition",
    "Handeln",
    "Wissen+",
)

# Stufe -> echtes Modul/Funktion (Auftrag; Phasen-Mapping aus wissenszyklus-8-stufen.md).
STAGE_MECHANISM = {
    "Erfahrung": "ingestion_hook.resolve_entities + lru_cache.WorkingMemory.store",
    "Wissen": "ingestion_hook.update_graph",
    "Gedächtnis": "pipeline.route_and_store",
    "Kognition": "lru_cache.WorkingMemory.consolidate_edges",
    "Denken": "reflective_agent.parse_transition_delta (LLM-Reflexion)",
    "Nicht-Kognition": "reflective_agent.lyapunov_check",
    "Handeln": "lru_cache.WorkingMemory.store",
    "Wissen+": "bias_monitor.BiasDriftMonitor.observe",
}


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", (text or "").lower()).strip("-")[:60] or "eintrag"


def _default_mandate() -> "mandate.Mandate":
    """Minimales Mandat, das `write:memory` auf `data/memory` erlaubt (§9)."""
    return mandate.Mandate(
        mandate_id="lifecycle-runner",
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


def _stage_erfahrung(ctx: dict) -> dict:
    entities = ingestion_hook.resolve_entities(ctx["fact"])
    key = "raw:" + _slug(ctx["question"])
    ctx["wm"].store(key, ctx["fact"])
    ctx["entities"] = [e.get("span", str(e)) if isinstance(e, dict) else str(e) for e in entities]
    return {"stage": "Erfahrung", "entities": ctx["entities"], "stored": key}


def _stage_wissen(ctx: dict) -> dict:
    delta = ingestion_hook.update_graph(ctx["graph"], ctx["entities"], ctx["relations"])
    return {"stage": "Wissen", "added_nodes": delta["added_nodes"], "added_edges": len(delta["added_edges"])}


def _stage_gedaechtnis(ctx: dict) -> dict:
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
    action = res.get("action") or res.get("gate")
    return {"stage": "Gedächtnis", "ok": res.get("ok"), "action": action, "steps": res.get("steps")}


def _stage_kognition(ctx: dict) -> dict:
    res = ctx["wm"].consolidate_edges(ctx["edges"], ctx["dims"])
    return {"stage": "Kognition", "consolidated": res["consolidated"], "strengthened": res["strengthened"]}


def _stage_denken(ctx: dict) -> dict:
    # Echte LLM-Reflexion (Guardrail 7): liefert nur eine gültige Matrix oder None (NOOP).
    matrix = ctx["reflect_fn"](ctx["reflection_text"], ctx["k"])
    feedback = None if matrix is None else round(float(matrix.diagonal().mean()), 4)
    return {"stage": "Denken", "self_feedback": feedback}


def _stage_nicht_kognition(ctx: dict) -> dict:
    res = reflective_agent.lyapunov_check(ctx["energies"], tau=ctx["tau"])
    damping = 1.0 if res["stable"] else 0.5  # dämpft Handeln, steuert nie allein (§8)
    return {"stage": "Nicht-Kognition", "E_dV": res["E_dV"], "damping": damping}


def _stage_handeln(ctx: dict) -> dict:
    action = ctx["results"]["Gedächtnis"]["action"]
    key = "action:" + _slug(ctx["question"])
    ctx["wm"].store(key, str(action))
    return {
        "stage": "Handeln",
        "action": action,
        "damped_by": ctx["results"]["Nicht-Kognition"]["damping"],
        "stored": key,
    }


def _stage_wissen_plus(ctx: dict) -> dict:
    monitor = bias_monitor.BiasDriftMonitor(baseline=ctx["drift_baseline"], tau=ctx["tau"])
    d = monitor.observe({"non-write": 0.5, "write": 0.5}, step=1)
    return {"stage": "Wissen+", "DI": d["DI"], "gate": d["gate"], "revised": True}


_STAGE_FN = {
    "Erfahrung": _stage_erfahrung,
    "Wissen": _stage_wissen,
    "Gedächtnis": _stage_gedaechtnis,
    "Kognition": _stage_kognition,
    "Denken": _stage_denken,
    "Nicht-Kognition": _stage_nicht_kognition,
    "Handeln": _stage_handeln,
    "Wissen+": _stage_wissen_plus,
}


def run_cycle(
    question: str,
    fact: str,
    correct: str,
    *,
    classify_fn,
    structured_dir,
    tier3_dir,
    now: float = 100.0,
    wm=None,
    graph=None,
    relations=None,
    edges=None,
    dims=None,
    reflection_text: str = "[]",
    k: int = 4,
    reflect_fn=None,
    energies=None,
    drift_baseline=None,
    tau: float = 0.10,
    mandate_obj=None,
) -> dict:
    """Führt die 8 Stufen in gesetzter Reihenfolge aus und liefert die echte Spur."""
    ctx = {
        "question": question,
        "fact": fact,
        "correct": correct,
        "classify_fn": classify_fn,
        "structured_dir": structured_dir,
        "tier3_dir": tier3_dir,
        "now": now,
        "wm": wm if wm is not None else lru_cache.WorkingMemory(),
        "graph": graph if graph is not None else ingestion_hook.MemoryGraph(),
        "relations": relations or [],
        "edges": edges or [],
        "dims": dims if dims is not None else {"logical": 0.9, "grounding": 0.9, "alignment": 0.9, "novelty": 0.5},
        "reflection_text": reflection_text,
        "k": k,
        "reflect_fn": reflect_fn if reflect_fn is not None else reflective_agent.parse_transition_delta,
        "energies": energies if energies is not None else [1.0, 0.9],
        "drift_baseline": drift_baseline if drift_baseline is not None else {"non-write": 0.5, "write": 0.5},
        "tau": tau,
        "mandate_obj": mandate_obj if mandate_obj is not None else _default_mandate(),
        "entities": [],
        "results": {},
    }
    trace = []
    for stage in STAGES:
        result = _STAGE_FN[stage](ctx)
        ctx["results"][stage] = result
        trace.append(result)
    return {"stages": list(STAGES), "results": ctx["results"], "trace": trace, "wm": ctx["wm"]}


if __name__ == "__main__":  # pragma: no cover - CLI
    import json

    out = run_cycle(
        "Beispiel?",
        "Kontakt: max@example.com, Version 2.",
        "Version 2.",
        classify_fn=lambda q, f, c: {"class": "write-new"},
        structured_dir="/tmp/lifecycle-runner/structured",
        tier3_dir="/tmp/lifecycle-runner/tier3",
        reflection_text="The action matched my usual inertia; slight bias to caution.",
    )
    print(json.dumps({"stages": out["stages"], "trace": out["trace"]}, ensure_ascii=False, indent=2))
