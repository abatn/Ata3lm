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

import json
import os
import re
from pathlib import Path

import bias_monitor
import gate_labels
import ingestion_hook
import lru_cache
import mandate
import pipeline
import reflective_agent
import runner_state
import trust

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


# S1 §9.1c/§9.2b: persistierte Drift-Referenz = Ground-Truth-Checkpoint (M(t)→M(t+1)).
# Pfad via `LIFECYCLE_DRIFT_REFERENCE` überschreibbar (Test-Isolation); Default tier2-index
# (nicht AGENTS.md/tier1-base ⇒ kein §9.1b-Snapshot).
DEFAULT_DRIFT_REFERENCE = "data/memory/tier2-index/drift-reference.json"


def _drift_reference_path() -> Path:
    """Pfad der persistierten Drift-Referenz (Umgebungsvariable oder Default)."""
    return Path(os.environ.get("LIFECYCLE_DRIFT_REFERENCE", DEFAULT_DRIFT_REFERENCE))


def _load_drift_reference():
    """Persistierten Checkpoint lesen; fehlend/ungültig ⇒ None (Cold-Start)."""
    try:
        data = json.loads(_drift_reference_path().read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return data if isinstance(data, dict) and data else None


def _save_drift_reference(distribution: dict) -> None:
    """Checkpoint schreiben (M(t+1), §9.2b Ground-Truth-Checkpoint)."""
    path = _drift_reference_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(distribution, ensure_ascii=False, sort_keys=True), encoding="utf-8")


def _configured_drift_baseline():
    """Konfigurierte Erwartung (§9.1c) aus `LIFECYCLE_DRIFT_BASELINE` (JSON-Dict) oder None."""
    raw = os.environ.get("LIFECYCLE_DRIFT_BASELINE", "").strip()
    if not raw:
        return None
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return None
    return parsed if isinstance(parsed, dict) and parsed else None


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", (text or "").lower()).strip("-")[:60] or "eintrag"


def _drift_label(value) -> str:
    """EIN Drift-Labelraum vor UND nach dem Write (R16): ``write`` | ``non-write``."""
    v = str(value or "").strip().lower()
    if v in ("write-new", "write-update", "write"):
        return "write"
    if v in ("non-write", "none", "non_write"):
        return "non-write"
    return v


def _canonicalize_distribution(distribution: dict) -> dict:
    """R16/A5 (Auftrag): Verteilung auf EINEN Labelraum abbilden und Kategorien aggregieren.

    ``{write-new: 0.3, write-update: 0.7}`` → ``{write: 1.0}``. Sowohl die **Baseline**
    (Env/Checkpoint/Param) als auch die **Beobachtung** laufen hierdurch, damit beide
    denselben Kategorienraum haben (sonst ``{write-update:1}`` vs ``write`` ⇒ falsches ``ask``).
    """
    agg: dict = {}
    for k, v in (distribution or {}).items():
        key = _drift_label(k)
        agg[key] = agg.get(key, 0.0) + float(v)
    return agg


class _CanonicalDriftMonitor:
    """Reicht Write-Label kanonisiert an den Monitor (R16/A5: ein Labelraum).

    Der Write-Gateway ruft `observe({cls: 1.0})` mit `write-new`/`write-update`; Stufe 8
    nutzt `write`/`non-write`. Ohne Kanonisierung sähe der Monitor zwei Klassenräume und
    würde fälschlich `ask` melden. **Baseline UND Beobachtung** werden kanonisiert (A5).
    """

    def __init__(self, monitor):
        self._monitor = monitor
        if hasattr(monitor, "baseline"):  # A5: Baseline mit-kanonisieren (Altformat-Migration)
            monitor.baseline = _canonicalize_distribution(monitor.baseline)

    def observe(self, distribution, step=None):
        return self._monitor.observe(_canonicalize_distribution(distribution), step=step)


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
    ctx["entities"] = [e.get("span", str(e)) if isinstance(e, dict) else str(e) for e in entities]
    # N6 §9.1: KEINE Mutation vor dem Mandat-Gate – der `raw:`-Write erfolgt erst,
    # wenn das Mandat `write:memory` erlaubt (Vorab-Prüfung in `run_cycle`).
    if not ctx.get("mandate_allow", False):
        return {
            "stage": "Erfahrung",
            "entities": ctx["entities"],
            "stored": None,
            "reason": "Mandat nicht ALLOW – kein WM-Write (§9.1)",
        }
    key = "raw:" + _slug(ctx["question"])
    ctx["wm"].store(key, trust.PIIFilter().minimize(ctx["fact"]))  # §9.2a: PII vor M
    return {"stage": "Erfahrung", "entities": ctx["entities"], "stored": key}


def _stage_wissen(ctx: dict) -> dict:
    # B4 (K6): Mandat vor JEDER Mutation – auch Graph (§9). Ohne Mandat kein Delta.
    if not ctx.get("mandate_allow", False):
        return {
            "stage": "Wissen",
            "added_nodes": [],
            "added_edges": 0,
            "skipped": True,
            "reason": "Mandat nicht ALLOW – keine Graph-Mutation (§9, B4)",
        }
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
        # N7 §9.1c/§10.4: Gate/Drift an die Pipeline durchreichen.
        self_update=ctx["self_update"],
        approvers=ctx["approvers"],
        drift=ctx["drift_write"],
    )
    action = res.get("action") or res.get("gate")
    return {"stage": "Gedächtnis", "ok": res.get("ok"), "action": action, "steps": res.get("steps")}


def _stage_kognition(ctx: dict) -> dict:
    # B4 (K6): WM-Edge-Konsolidierung ist eine Mutation ⇒ nur mit Mandat (§9).
    if not ctx.get("mandate_allow", False):
        return {
            "stage": "Kognition",
            "consolidated": False,
            "strengthened": [],
            "skipped": True,
            "reason": "Mandat nicht ALLOW – keine WM-Mutation (§9, B4)",
        }
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
    ged = ctx["results"]["Gedächtnis"]
    if not ged.get("ok"):
        # §9.1: Ablehnung (deny/ask) begrenzt nachfolgende Änderungen → KEIN Action-Write
        return {
            "stage": "Handeln",
            "action": None,
            "stored": None,
            "skipped": True,
            "reason": "Gedächtnis-Gate nicht ok",
        }
    action = ged.get("action")
    key = "action:" + _slug(ctx["question"])
    ctx["wm"].store(key, str(action))
    return {
        "stage": "Handeln",
        "action": action,
        "damped_by": ctx["results"]["Nicht-Kognition"]["damping"],
        "stored": key,
    }


def _stage_wissen_plus(ctx: dict) -> dict:
    # N7/S1 §9.1c: echte Klasse des Laufs (nicht 0.5/0.5). Referenz = **Checkpoint**
    # (§9.2b), NIE die eigene Beobachtung. Cold-Start (§10.4): unsicher ⇒ `ask`
    # (niemals still `ok`) + einmaliger Bootstrap der Referenz (Initialisierung,
    # KEIN Fortschreiben).
    # B5 (K6): `revised` = ok AND gate == "allow" (NIE `gate != ask` – das ließe
    # `deny` durch!). M(t)→M(t+1) nur bei `revised` ⇒ `deny`/`ask` ⇒ revised=False.
    # B4 (K6): jede Referenz-Schreibung ist eine Mutation ⇒ nur mit Mandat (§9).
    action = ctx["results"]["Gedächtnis"].get("action")
    label = "write" if action in ("write-new", "write-update") else "non-write"
    observed = {label: 1.0}
    ok = bool(ctx["results"]["Gedächtnis"].get("ok"))  # §9: keine Revision nach Ablehnung
    allow = ctx.get("mandate_allow", False)
    monitor = ctx["drift_monitor"]
    if monitor is not None:  # explizit übergebener Monitor (Test / Write-Schutz)
        d = monitor.observe(observed, step=1)
        gate = gate_labels.normalize(d["gate"])
        return {
            "stage": "Wissen+",
            "DI": d["DI"],
            "gate": gate,
            "revised": ok and gate_labels.is_allow(gate),
            "reference": "monitor",
        }
    # R093 (§9.1c, Interface-Änderung §9 approved): optionales GDI-Gate statt JSD.
    # Nutzt das **kalibrierte** τ+Gewichte (Gl. 14–16) auf dem Textpaar; kein
    # Checkpoint-Write im GDI-Modus (die Referenz ist Text, nicht die Label-Verteilung).
    if ctx.get("gdi_enabled"):
        d = ctx["gdi_monitor"].observe_gdi(ctx["gdi_prev_text"], ctx["fact"], embed_fn=ctx["embed_fn"], step=1)
        gate = gate_labels.normalize(d["gate"])
        return {
            "stage": "Wissen+",
            "gdi": d["gdi"],
            "tau": d["tau"],
            "gate": gate,
            "revised": ok and gate_labels.is_allow(gate),
            "reference": "gdi",
        }
    reference = ctx["drift_baseline"] if ctx["drift_baseline"] is not None else _load_drift_reference()
    # R16/A5: auch die Stufe-8-Referenz auf denselben Labelraum kanonisieren.
    reference = _canonicalize_distribution(reference) if reference is not None else None
    if reference is None:
        if allow:  # B4: Bootstrap ist Initialisierung – aber keine Mutation ohne Mandat
            _save_drift_reference(observed)  # Cold-Start-Bootstrap (Initialisierung, Lesart A)
        return {
            "stage": "Wissen+",
            "DI": None,
            "gate": gate_labels.ASK,
            "reason": (
                "keine Referenz (Cold-Start §10.4) – Bootstrap gesetzt"
                if allow
                else "keine Referenz (Cold-Start §10.4) – kein Bootstrap ohne Mandat (B4)"
            ),
            "revised": False,  # gate=ask ⇒ nie revised (B5)
            "reference": "bootstrap" if allow else "blocked",
        }
    d = bias_monitor.BiasDriftMonitor(baseline=reference, tau=ctx["tau"]).observe(observed, step=1)
    gate = gate_labels.normalize(d["gate"])
    revised = ok and gate_labels.is_allow(gate)  # B5: ok AND gate == "allow"
    if revised and allow:
        _save_drift_reference(observed)  # M(t)->M(t+1) nur bei revised (§9, B5)
    return {
        "stage": "Wissen+",
        "DI": d["DI"],
        "gate": gate,
        "revised": revised,
        "reference": "checkpoint" if revised else "checkpoint(kept)",
    }


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
    self_update: bool = False,
    approvers=None,
    drift=None,
    state_path=None,
    consolidation_state_path=None,
    gdi: bool = False,
    embed_fn=None,
    gdi_calibration=None,
    gdi_prev_text=None,
) -> dict:
    """Führt die 8 Stufen in gesetzter Reihenfolge aus und liefert die echte Spur.

    K1: `state_path` setzt den geteilten Runner-Zustand vor dem Lauf fort und
    persistiert ihn danach (atomar, mit Inhalten/Metadaten/offenen Freigaben).

    **Interface-Änderung (§9-pflichtig, kenntlich gemacht):** neuer optionaler
    Parameter `consolidation_state_path` (Auftrag §10.3) – ist er gesetzt, sammelt der
    Lauf am Ende **lesend** konsolidierbare Fakten (`slow_consolidation.collect_pending`)
    und hängt sie als `pending_consolidation` an das Ergebnis. Kein Write/Flush im Lauf
    (§9 Human-Gate); Default `None` ⇒ unverändertes Verhalten.

    **Interface-Änderung §9 approved (Rekursion 093; Batnini + Taoufik, 2026-10-08):**
    optionale Parameter `gdi`/`embed_fn`/`gdi_calibration`/`gdi_prev_text` binden das
    **kalibrierte GDI-Gate** (SAHOO Gl. 12–16, AGENTS.md §9.1c) additiv an Stufe 8.
    Nur wenn `gdi=True` **und** `embed_fn` **und** `gdi_prev_text` **und** eine
    Kalibrierung (`gdi_calibration` oder `bias_monitor.load_calibration()`) vorliegen,
    wird statt des JSD-`observe` das GDI-`observe_gdi` genutzt. Default `gdi=False`
    ⇒ **exakt altes Verhalten** (JSD).
    """
    mandate_obj = mandate_obj if mandate_obj is not None else _default_mandate()
    # S1 §9.1c: Referenz-Priorität (explizit > Env-Erwartung > persistierter Checkpoint > keine).
    baseline = drift_baseline if drift_baseline is not None else _configured_drift_baseline()
    # R16/A5: Baseline (und jeder Checkpoint) auf EINEN Labelraum kanonisieren.
    if baseline is not None:
        baseline = _canonicalize_distribution(baseline)
    # N6 §9.1: Mandat VOR jeder Mutation prüfen (Stufe 1 schreibt `raw:` in WM).
    dec0 = mandate.assess(mandate_obj, action="write:memory", resource="data/memory", amount=0.0, now=now)
    # N7/S1 §9.1c: ein explizit übergebener Drift schützt den Write in Stufe 3 und wird
    # in Stufe 8 genutzt; sonst löst Stufe 8 die Referenz auf (Checkpoint / Cold-Start).
    # R04: auch die Default-Erwartung (`LIFECYCLE_DRIFT_BASELINE`) gatet VOR der Mutation.
    # A2 (Auftrag): die **persistierte Drift-Referenz** (Checkpoint) wird ebenfalls VOR
    # jeder Mutation aufgelöst und gatet den Write – nicht erst nach dem Write (Stufe 8).
    # R16: vor (Write-Gateway) und nach (Stufe 8) gilt EIN kanonischer Labelraum.
    drift_monitor = drift
    if drift is not None:
        drift_write = _CanonicalDriftMonitor(drift)
    else:
        write_reference = baseline if baseline is not None else _load_drift_reference()
        if write_reference is not None:
            drift_write = _CanonicalDriftMonitor(bias_monitor.BiasDriftMonitor(baseline=write_reference, tau=tau))
        else:
            drift_write = None
    # R093 (§9.1c, Interface-Änderung §9 approved): GDI-Gate nur opt-in UND vollständig.
    # Kalibrierung: explizit übergeben oder aus `drift-calibration-sahoo.json` geladen.
    gdi_cal = gdi_calibration
    if gdi and gdi_cal is None:
        gdi_cal = bias_monitor.load_calibration()
    gdi_enabled = bool(gdi and embed_fn is not None and gdi_prev_text is not None and gdi_cal is not None)
    if gdi_enabled:
        gdi_monitor = bias_monitor.BiasDriftMonitor(baseline={}, gdi_weights=gdi_cal["weights"], gdi_tau=gdi_cal["tau"])
    else:
        gdi_monitor = None
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
        "drift_baseline": baseline,
        "tau": tau,
        "mandate_obj": mandate_obj,
        "mandate_allow": gate_labels.is_allow(dec0["decision"]),
        "self_update": self_update,
        "approvers": approvers,
        "drift_write": drift_write,
        "drift_monitor": drift_monitor,
        "gdi_enabled": gdi_enabled,
        "gdi_monitor": gdi_monitor,
        "embed_fn": embed_fn,
        "gdi_prev_text": gdi_prev_text,
        "entities": [],
        "results": {},
    }
    # K1: geteilter persistenter Runner-Zustand – vor dem Lauf fortsetzen (Restart)
    resumed, rec = None, {}
    if state_path is not None:
        resumed = runner_state.load(state_path)
        if resumed is not None:
            rec = runner_state.reconstruct(resumed)
            # R05: fehlende Teile (None) NICHT über gesetzte Defaults legen. Ein
            # 5-Phasen-Cold-Start persistiert wm/graph=None; der 8-Stufen-Resume darf
            # die bereits erzeugten Default-Objekte dann nicht durch None ersetzen.
            ctx["wm"] = ctx["wm"] if wm is not None else (rec["wm"] if rec["wm"] is not None else ctx["wm"])
            ctx["graph"] = (
                ctx["graph"] if graph is not None else (rec["graph"] if rec["graph"] is not None else ctx["graph"])
            )
    trace = []
    for stage in STAGES:
        result = _STAGE_FN[stage](ctx)
        ctx["results"][stage] = result
        trace.append(result)
    state_save = None
    if state_path is not None:
        # R18: ein abgelehnter Akt (Gedächtnis ok=False) persistiert KEINEN neuen
        # Wissenszustand – der Runner-State wird dann nicht fortgeschrieben (§9).
        akt_ok = bool(ctx["results"].get("Gedächtnis", {}).get("ok"))
        if not akt_ok:
            state_save = {
                "ok": False,
                "path": str(state_path),
                "reason": "Akt abgelehnt (Gedächtnis ok=False) – kein neuer Wissenszustand persistiert (R18/§9)",
            }
        else:
            # K1: Zustand nach dem Lauf persistieren (Inhalte + Metadaten + offene Freigaben).
            # R06: CAS über den geladenen Revisionsstand (Lost-Update verhindern).
            # R07: die Rückgabe wird NICHT verschwiegen (Feld `state_save` im Ergebnis).
            state_save = runner_state.save(
                runner_state.snapshot(
                    wm=ctx["wm"],
                    graph=ctx["graph"],
                    hmm=rec.get("hmm"),  # K1: fremdes HMM im Shared State erhalten
                    drift_reference=_load_drift_reference(),
                    schema=(resumed or {}).get("schema", {}),
                    open_approvals=(resumed or {}).get("open_approvals", []),
                    runner="lifecycle-runner",
                ),
                state_path,
                expected_rev=(resumed or {}).get("rev", 0),
            )
    out = {
        "stages": list(STAGES),
        "results": ctx["results"],
        "trace": trace,
        "wm": ctx["wm"],
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
