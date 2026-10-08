#!/usr/bin/env python3
"""
Element-Pipeline – verbindet die Prozesse (schließt die Verbindungs-LÜCKEN).

Quellen: AGENTS.md §9 (Gate/Trust/Approval/Drift), §10 (Fast Write Routing:
write-new → knowledge/structured + tier3; write-update → tier1 supersede),
Atomic (search-before-store), ATHENA (Tri-Color Trust, „AI can only propose").
Lab-Prinzip §6: Mechanik = Quellen; die Verdrahtung ist Auftrag.

**K2 (Auftrag):** die Schreib-Kette läuft IM EINEN `write_gateway.store`
(feste Reihenfolge: Mandat → FWR → Trust/PII → Poisoning → Freigabe (§9.3) →
Drift (§9.1c) → Supersede → Write → Shared → Provenienz). Diese Datei behält
den Vertrag `route_and_store` (Kompatibilität aller Aufrufer) und die
technischen Helfer – KEIN eigener Schreibpfad mehr (K2-STOPP).
"""

from __future__ import annotations

from pathlib import Path
from typing import Callable, Optional

import bias_monitor
import write_gateway


def export_shared(tier, tier1_dir: Path) -> str:
    """SharedTier → tier1-base persistieren (schließt shared_memory → tier1)."""
    Path(tier1_dir).mkdir(parents=True, exist_ok=True)
    return str(tier.dump(Path(tier1_dir) / "shared_store.jsonl"))


def drift_gate(distribution: dict, baseline: dict, tau: float = 0.10) -> dict:
    """Drift-Gate über `bias_monitor` (bias_monitor → alle, §9.1c)."""
    return bias_monitor.BiasDriftMonitor(baseline=baseline, tau=tau).observe(distribution, step=1)


def load_from_tier2(tier2_dir: Path, tier3_dir: Path) -> dict:
    """tier2-index → tier3-working laden (schließt die Lücke „kein Ladepfad“)."""
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
    ontology_ref: str = "",
    source_ref: str = "",
) -> dict:
    """Eine Erfahrung durch die ganze Kette schicken (alle Elemente reden mit).

    K2: DELEGATION an `write_gateway.store` (EIN Schreibpfad, feste Reihenfolge).
    """
    res = write_gateway.store(
        question=question,
        fact=fact,
        correct=correct,
        classify_fn=classify_fn,
        mandate_obj=mandate_obj,
        now=now,
        structured_dir=structured_dir,
        tier3_dir=tier3_dir,
        drift=drift,
        self_update=self_update,
        approval_obj=approval_obj,
        approvers=approvers,
        agent="pipeline",
        ontology_ref=ontology_ref,
        source_ref=source_ref,
    )
    if res.get("action") == "non-write":
        res["action"] = "none"  # Vertrag der Pipeline: non-write meldet action "none"
    return res
