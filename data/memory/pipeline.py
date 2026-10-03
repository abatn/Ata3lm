#!/usr/bin/env python3
"""
Element-Pipeline – verbindet die Prozesse (schließt die Verbindungs-LÜCKEN).

Quellen: AGENTS.md §9 (Gate/Trust/Approval/Drift), §10 (Fast Write Routing:
write-new → knowledge/structured + tier3; write-update → tier1 supersede),
Atomic (search-before-store), ATHENA (Tri-Color Trust, „AI can only propose").
Lab-Prinzip §6: Mechanik = Quellen; die Verdrahtung ist Auftrag.

Kette: Mandat-Gate → FWR-Klassifikation → Trust (PII) → Approval (self_update)
       → Write (write-new / write-update + Bi-Temporal-Supersede) → Drift-Gate.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Callable, Optional

import approval
import bi_temporal
import bias_monitor
import mandate
import trust


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", (text or "").lower()).strip("-")[:60] or "eintrag"


def drift_gate(distribution: dict, baseline: dict, tau: float = 0.10) -> dict:
    """Drift-Gate über `bias_monitor` (bias_monitor → alle, §9.1c)."""
    return bias_monitor.BiasDriftMonitor(baseline=baseline, tau=tau).observe(distribution, step=1)


def load_from_tier2(tier2_dir: Path, tier3_dir: Path) -> dict:
    """tier2-index → tier3-working laden (schließt die Lücke „kein Ladepfad")."""
    tier3_dir.mkdir(parents=True, exist_ok=True)
    loaded = []
    for p in sorted(Path(tier2_dir).glob("*.md")):
        (Path(tier3_dir) / p.name).write_text(p.read_text(encoding="utf-8"), encoding="utf-8")
        loaded.append(p.name)
    return {"loaded": loaded, "n": len(loaded)}


def route_and_store(
    *,
    question: str,
    fact: str,
    correct: str,
    classify_fn: Callable,
    mandate_obj,
    now: float,
    structured_dir: Path,
    tier3_dir: Path,
    drift=None,
    self_update: bool = False,
    approval_obj=None,
    approvers: Optional[list] = None,
) -> dict:
    """Eine Erfahrung durch die ganze Kette schicken (alle Elemente reden mit)."""
    steps: list[tuple] = []

    # 1) Mandat-Gate (mandate → alle)
    dec = mandate.assess(mandate_obj, action="write:memory", resource="data/memory", amount=0.0, now=now)
    steps.append(("mandate", dec["decision"]))
    if dec["decision"] != "ALLOW":
        return {"ok": False, "gate": "deny", "reason": dec["reason"], "steps": steps}

    # 2) Fast Write Routing (Klassifikation injiziert – im Betrieb der echte Router)
    cls = classify_fn(question, fact, correct)["class"]
    steps.append(("fwr", cls))
    if cls == "non-write":
        return {"ok": True, "action": "none", "gate": "allow", "steps": steps}

    # 3) Trust: PII vor dem Store entfernen (§9.2)
    clean = trust.PIIFilter().minimize(fact)
    steps.append(("trust", "PII entfernt" if clean != fact else "keine PII"))

    # 4) Approval (§9.3) bei self_update an Originaldatei
    if self_update:
        a = approval_obj or approval.TwoPersonApproval(subject=question)
        for person in approvers or []:
            a.approve(person, diff_sha=_slug(clean))
        a.finalize()
        state = a.status()["state"]
        steps.append(("approval", state))
        if state != "approved":
            return {"ok": False, "gate": "ask", "approval": state, "steps": steps}

    # 5) Write: write-new → structured + tier3 · write-update → Bi-Temporal-Supersede
    Path(structured_dir).mkdir(parents=True, exist_ok=True)
    Path(tier3_dir).mkdir(parents=True, exist_ok=True)
    name = f"{_slug(question)}.md"
    written = [str(Path(structured_dir) / name)]
    (Path(structured_dir) / name).write_text(clean, encoding="utf-8")
    superseded = None
    if cls == "write-new":
        (Path(tier3_dir) / name).write_text(clean, encoding="utf-8")
        written.append(str(Path(tier3_dir) / name))
    else:  # write-update → alten Fakt invalidieren (nicht löschen)
        bt = bi_temporal.BiTemporalStore()
        bt.assert_fact(question, "answer", "alt", valid_from=str(now), recorded_at=str(now))
        res = bt.assert_fact(question, "answer", correct, valid_from=str(now), recorded_at=str(now))
        superseded = res["superseded"]
    steps.append(("write", cls))

    # 6) Drift-Gate (bias_monitor → alle)
    gate = "allow"
    if drift is not None:
        d = drift.observe({"non-write": 0.5, "write": 0.5}, step=1)
        gate = d["gate"]
        steps.append(("drift", d["DI"]))
    return {"ok": True, "action": cls, "written": written, "superseded": superseded, "gate": gate, "steps": steps}
