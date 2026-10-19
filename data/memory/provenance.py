#!/usr/bin/env python3
"""
PROV-O-Provenienz je Fakt (K3) – W3C PROV-O (Recommendation 2013).

Quelle (verifiziert 2026-10-06, HTTP 200): **W3C PROV-O: The PROV Ontology**,
W3C Recommendation 30 April 2013, <https://www.w3.org/TR/prov-o/> ·
Namespace ``http://www.w3.org/ns/prov#``. Genutzte Terme (normativ):
``prov:Entity``, ``prov:Activity``, ``prov:Agent``, ``prov:wasGeneratedBy``,
``prov:wasDerivedFrom``, ``prov:wasAttributedTo``, ``prov:wasRevisionOf``,
``prov:invalidatedAtTime``.

Status (§6): Datenmodell **Belegt** (PROV-O); die **Durchsetzung** (Inhalt per
sha256 binden, Freigabe binden, Schreibverweigerung ohne Bindung) ist
**Auftrag** (K3) — PROV-O garantiert weder geprüfte Quellen noch unveränderliche
Protokolle (Bericht §2 K3).

K3-STOPP-Regel: **kein Record ohne Inhalt-Hash und – wo gefordert – ohne
gebundene Freigabe.** ``build_record`` wirft ``ProvenanceError``, ``verify_record``
meldet ``ok: False``.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

PROV_NS = "http://www.w3.org/ns/prov#"

DEFAULT_LOG = Path(__file__).resolve().parents[2] / "data/memory/tier3-working/provenance.jsonl"


class ProvenanceError(Exception):
    """Record unvollständig: kein Inhalt-Hash oder keine gebundene Freigabe (K3-STOPP)."""


def content_hash(text: str) -> str:
    """SHA-256 (hex) über den Fakt-Inhalt – die Inhalt-Bindung des Records."""
    return hashlib.sha256((text or "").encode("utf-8")).hexdigest()


def _iso(now: float) -> str:
    return datetime.fromtimestamp(float(now), tz=timezone.utc).isoformat()


@dataclass(frozen=True)
class ApprovalBinding:
    """Gebundene Freigabe (§9.3 Zwei-Personen): state + Approver + diff_sha."""

    state: str
    approvers: tuple
    diff_sha: str

    def as_dict(self) -> dict:
        return {"state": self.state, "approvers": list(self.approvers), "diff_sha": self.diff_sha}


def _valid_approval(approval) -> bool:
    """Freigabe-Bindung gültig? (Auftrag K3: state=approved, ≥2 Approver, diff_sha)."""
    if isinstance(approval, ApprovalBinding):
        approval = approval.as_dict()
    if not isinstance(approval, dict):
        return False
    approvers = approval.get("approvers") or ()
    return (
        approval.get("state") == "approved"
        and len({a.strip().lower() for a in approvers if a}) >= 2
        and bool(approval.get("diff_sha"))
    )


def build_record(
    *,
    fact: str,
    activity: str,
    agent: str,
    source: str,
    now: float,
    derived_from: Optional[str] = None,
    revision_of: Optional[str] = None,
    invalidated_at: Optional[float] = None,
    approval=None,
    require_approval: bool = False,
) -> dict:
    """PROV-O-Record für einen Write (K3).

    - ``prov:Entity`` = der Fakt (gebunden über ``sha256``).
    - ``prov:Activity`` = die schreibende Aktivität (``kind`` = Pfadname).
    - ``prov:Agent`` = ausführender Agent.
    - ``prov:wasGeneratedBy`` / ``prov:wasAttributedTo`` (immer),
      ``prov:wasDerivedFrom`` / ``prov:wasRevisionOf`` / ``prov:invalidatedAtTime``
      (sofern zutreffend, z. B. Supersede §10.7).

    STOPP (``ProvenanceError``): leerer Inhalt (kein Hash), leere Quelle/Agent/
    Aktivität oder ``require_approval=True`` ohne gültige Freigabe-Bindung.
    """
    if not (fact or "").strip():
        raise ProvenanceError("kein Inhalt – kein Hash bindbar (K3-STOPP)")
    if not (activity or "").strip() or not (agent or "").strip() or not (source or "").strip():
        raise ProvenanceError("Record ohne Aktivität/Agent/Quelle – Provenienz unvollständig (§6)")
    if isinstance(approval, ApprovalBinding):
        approval = approval.as_dict()
    if require_approval and not _valid_approval(approval):
        raise ProvenanceError("Freigabe nicht gebunden (K3-STOPP): state=approved, ≥2 Approver, diff_sha nötig")
    if approval is not None and not isinstance(approval, dict):
        raise ProvenanceError("Freigabe-Bindung muss dict oder ApprovalBinding sein")

    h = content_hash(fact)
    ts = _iso(now)
    entity_id = f"entity:{h[:16]}"
    activity_id = f"activity:{activity}:{int(now)}"
    agent_id = f"agent:{agent}"

    entity = {
        "@id": entity_id,
        "@type": "prov:Entity",
        "sha256": h,
        "prov:wasGeneratedBy": activity_id,
        "prov:wasAttributedTo": agent_id,
    }
    if derived_from is not None:
        entity["prov:wasDerivedFrom"] = derived_from
    if revision_of is not None:
        entity["prov:wasRevisionOf"] = revision_of
    if invalidated_at is not None:
        entity["prov:invalidatedAtTime"] = _iso(invalidated_at)

    return {
        "@context": {"prov": PROV_NS},
        "entity": entity,
        "activity": {
            "@id": activity_id,
            "@type": "prov:Activity",
            "kind": activity,
            "prov:startedAtTime": ts,
            "prov:endedAtTime": ts,
        },
        "agent": {"@id": agent_id, "@type": "prov:Agent", "name": agent},
        "source": source,
        "approval": approval,
        "require_approval": bool(require_approval),
        "created": ts,
    }


def verify_record(record: dict, fact: Optional[str] = None) -> dict:
    """Record prüfen: Struktur, Inhalt-Hash-Bindung, Freigabe-Bindung (K3-STOPP)."""
    try:
        entity = record["entity"]
        activity = record["activity"]
        agent = record["agent"]
        assert entity["@type"] == "prov:Entity"
        assert activity["@type"] == "prov:Activity"
        assert agent["@type"] == "prov:Agent"
        assert entity["prov:wasGeneratedBy"] == activity["@id"]
        assert entity["prov:wasAttributedTo"] == agent["@id"]
        h = entity["sha256"]
        assert isinstance(h, str) and len(h) == 64
    except (KeyError, TypeError, AssertionError):
        return {"ok": False, "hash_ok": False, "approval_ok": False, "reason": "Record-Struktur unvollständig"}
    hash_ok = content_hash(fact) == h if fact is not None else True
    approval = record.get("approval")
    approval_ok = _valid_approval(approval) if approval is not None else not record.get("require_approval")
    if not hash_ok:
        return {"ok": False, "hash_ok": False, "approval_ok": approval_ok, "reason": "Inhalt-Hash stimmt nicht überein"}
    if not approval_ok:
        return {"ok": False, "hash_ok": True, "approval_ok": False, "reason": "Freigabe nicht gebunden (K3-STOPP)"}
    return {"ok": True, "hash_ok": True, "approval_ok": True, "reason": "ok"}


def append_record(path, record: dict) -> str:
    """Record dauerhaft protokollieren (JSONL, append). Rückgabe: Pfad."""
    p = Path(path) if path is not None else DEFAULT_LOG
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")
    return str(p)
