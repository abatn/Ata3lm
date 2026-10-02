#!/usr/bin/env python3
"""
Mandats-Formalisierung – EU Fidacy (Futurium) + AGENTS.md §9.

Quellen (HTTP 200, geprüft 2026-10-02):
  - Futurium (EU-Kommission), „Verifiable Authority Boundaries for AI Agents and
    Autonomous Systems" und „Europe's Next AI Infrastructure: Authority Before
    Action":
    https://futurium.ec.europa.eu/en/apply-ai-alliance/community-content/verifiable-authority-boundaries-ai-agents-and-autonomous-systems
    https://futurium.ec.europa.eu/en/apply-ai-alliance/community-content/europes-next-ai-infrastructure-authority-action
  - Fidacy-Docs (Mandat, Action Authority, Concepts):
    https://fidacy.com/docs/mandate · https://fidacy.com/docs/action-authority ·
    https://fidacy.com/docs/concepts

Wörtlich aus der Quelle:
  - „A bounded mandate … the agent cannot create for itself."
  - „a child agent can only attenuate, never expand" / „A child mandate may only
    reduce its parent's authority."
  - „A mandate can specify the permitted action, protected resource, recipient,
    amount or value ceiling, time window, use count and delegation depth."
  - „The outcome is ALLOW, REVIEW or DENY. An allowed consequential action can
    receive a short-lived, signed, single-use grant."
Flow: Mandate → Independent Decision → Execution Grant → Evidence.

Lab-Prinzip §6: Mechanik = Quelle; konkrete Werte = Auftrag (mandate.md).
"""

from __future__ import annotations

import hashlib
import json
import secrets
from dataclasses import dataclass, replace
from typing import Optional


class MandateError(Exception):
    """Verstoß gegen die Mandats-Grenze (z. B. unzulässige Erweiterung)."""


@dataclass(frozen=True)
class Mandate:
    """Begrenztes Mandat (Quelle: „bounded mandate")."""

    mandate_id: str
    principal: str  # verantwortliche Person/Organisation
    agent: str  # Workload-Identität
    actions: frozenset  # erlaubte Aktionen (allowlist)
    resources: frozenset  # erlaubte Ressourcen (allowlist)
    amount_limit: float  # Wert-/Änderungs-Obergrenze
    max_uses: int
    valid_from: float  # epoch-Sekunden
    valid_until: float
    approval_threshold: float
    delegation_depth: int = 0
    parent_id: Optional[str] = None
    revoked: bool = False

    def digest(self) -> str:
        """SHA-256 über die kanonischen Felder (Identität des Mandats)."""
        payload = json.dumps(
            {
                "mandate_id": self.mandate_id,
                "principal": self.principal,
                "agent": self.agent,
                "actions": sorted(self.actions),
                "resources": sorted(self.resources),
                "amount_limit": self.amount_limit,
                "max_uses": self.max_uses,
                "valid_from": self.valid_from,
                "valid_until": self.valid_until,
                "approval_threshold": self.approval_threshold,
                "delegation_depth": self.delegation_depth,
                "parent_id": self.parent_id,
            },
            sort_keys=True,
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


class MandateRegistry:
    """Hält Mandate, Entscheidungen und Grants (Evidence)."""

    def __init__(self) -> None:
        self._mandates: dict[str, Mandate] = {}
        self.decisions: list[dict] = []
        self.grants: dict[str, dict] = {}

    def issue(
        self,
        *,
        principal: str,
        agent: str,
        actions,
        resources,
        amount_limit: float,
        max_uses: int,
        valid_from: float,
        valid_until: float,
        approval_threshold: float,
        delegation_depth: int = 0,
        parent_id: Optional[str] = None,
        mandate_id: Optional[str] = None,
    ) -> Mandate:
        """Mandat ausstellen — nur der Principal (Mensch/Organisation)."""
        m = Mandate(
            mandate_id=mandate_id or f"mandate-{secrets.token_hex(4)}",
            principal=principal,
            agent=agent,
            actions=frozenset(actions),
            resources=frozenset(resources),
            amount_limit=amount_limit,
            max_uses=max_uses,
            valid_from=valid_from,
            valid_until=valid_until,
            approval_threshold=approval_threshold,
            delegation_depth=delegation_depth,
            parent_id=parent_id,
        )
        self._mandates[m.mandate_id] = m
        return m

    def get(self, mandate_id: str) -> Mandate:
        return self._mandates[mandate_id]

    def revoke(self, mandate_id: str) -> Mandate:
        m = replace(self.get(mandate_id), revoked=True)
        self._mandates[mandate_id] = m
        return m

    def attenuate(
        self,
        parent: Mandate,
        *,
        agent: str,
        actions=None,
        resources=None,
        amount_limit: Optional[float] = None,
        max_uses: Optional[int] = None,
        valid_until: Optional[float] = None,
        approval_threshold: Optional[float] = None,
    ) -> Mandate:
        """Kind-Mandat: darf die Autorität NUR verkleinern (attenuate, nie expand)."""
        new_actions = frozenset(actions) if actions is not None else parent.actions
        new_resources = frozenset(resources) if resources is not None else parent.resources
        new_amount = parent.amount_limit if amount_limit is None else amount_limit
        new_uses = parent.max_uses if max_uses is None else max_uses
        new_until = parent.valid_until if valid_until is None else valid_until
        new_threshold = parent.approval_threshold if approval_threshold is None else approval_threshold
        if parent.delegation_depth <= 0:
            raise MandateError("keine Delegation erlaubt (delegation_depth=0)")
        if not new_actions <= parent.actions:
            raise MandateError("Aktionen sind keine Teilmenge des Eltern-Mandats")
        if not new_resources <= parent.resources:
            raise MandateError("Ressourcen sind keine Teilmenge des Eltern-Mandats")
        if new_amount > parent.amount_limit:
            raise MandateError("amount_limit erweitert das Eltern-Mandat")
        if new_uses > parent.max_uses:
            raise MandateError("max_uses erweitert das Eltern-Mandat")
        if new_until > parent.valid_until:
            raise MandateError("valid_until erweitert das Eltern-Mandat")
        if new_threshold > parent.approval_threshold:
            raise MandateError("approval_threshold erweitert das Eltern-Mandat")
        return self.issue(
            principal=parent.principal,
            agent=agent,
            actions=new_actions,
            resources=new_resources,
            amount_limit=new_amount,
            max_uses=new_uses,
            valid_from=parent.valid_from,
            valid_until=new_until,
            approval_threshold=new_threshold,
            delegation_depth=parent.delegation_depth - 1,
            parent_id=parent.mandate_id,
        )

    def expand(self, mandate: Mandate, *, agent: str, **changes) -> dict:
        """Erweiterung durch den Agenten → NIE erlaubt, immer Human-Gate (ask)."""
        return {
            "allowed": False,
            "gate": "ask",
            "agent": agent,
            "mandate_id": mandate.mandate_id,
            "reason": "Agent kann sein Mandat nicht erweitern – nur der Principal (Mensch) (§9)",
        }


def is_active(mandate: Mandate, now: float) -> bool:
    """Gültig, wenn nicht widerrufen und im Zeitfenster."""
    return (not mandate.revoked) and mandate.valid_from <= now <= mandate.valid_until


def assess(mandate: Mandate, *, action: str, resource: str, amount: float, now: float) -> dict:
    """Unabhängige Entscheidung AUSSERHALB des Modells: ALLOW | REVIEW | DENY."""
    if mandate.revoked:
        decision, reason = "DENY", "Mandat widerrufen"
    elif not (mandate.valid_from <= now <= mandate.valid_until):
        decision, reason = "DENY", "außerhalb des Gültigkeitsfensters"
    elif action not in mandate.actions:
        decision, reason = "DENY", f"Aktion '{action}' nicht erlaubt"
    elif resource not in mandate.resources:
        decision, reason = "DENY", f"Ressource '{resource}' nicht erlaubt"
    elif amount > mandate.amount_limit:
        decision, reason = "DENY", "amount_limit überschritten"
    elif amount >= mandate.approval_threshold:
        decision, reason = "REVIEW", "menschliche Freigabe nötig (§9)"
    else:
        decision, reason = "ALLOW", "im Mandat"
    return {
        "decision": decision,
        "reason": reason,
        "mandate_id": mandate.mandate_id,
        "action": action,
        "resource": resource,
        "amount": amount,
    }


def issue_grant(decision: dict, *, now: float, ttl_seconds: float = 60.0) -> Optional[dict]:
    """Nur ein ALLOW erhält einen kurzlebigen, einmaligen Grant."""
    if decision["decision"] != "ALLOW":
        return None
    return {
        "grant_id": secrets.token_hex(8),
        "mandate_id": decision["mandate_id"],
        "expires_at": now + ttl_seconds,
        "used": False,
    }


def redeem(grant: dict, *, now: float) -> dict:
    """Executor-Seite: Grant prüfen und EINMALIG verbrauchen (Replay/Expiry abweisen)."""
    if grant["used"]:
        return {"ok": False, "reason": "grant_replayed"}
    if now > grant["expires_at"]:
        return {"ok": False, "reason": "grant_expired"}
    grant["used"] = True
    return {"ok": True, "reason": "consumed", "grant_id": grant["grant_id"]}


def evidence(record: dict, *, prev_hash: Optional[str] = None) -> dict:
    """Hash-verketteter Evidence-Eintrag (Tamper-evident)."""
    canonical = json.dumps(record, sort_keys=True, default=str)
    h = hashlib.sha256(f"{prev_hash or ''}{canonical}".encode("utf-8")).hexdigest()
    return {"record": record, "prev": prev_hash, "hash": h}
