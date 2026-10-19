#!/usr/bin/env python3
"""
Zwei-Personen-Verifikation für den approved-Flow.

Quelle (verifiziert 2026-10-01, HTTP 200):
  - EU-KI-VO (VO (EU) 2024/1689) **Art. 14(5)**: Für High-Risk-Systeme nach
    **Annex III Punkt 1(a)** (Remote-Biometrie-Identifikation) darf keine
    Aktion/Entscheidung auf der Identifikation beruhen, „unless that
    identification has been **separately verified and confirmed by at least two
    natural persons** with the necessary competence, training and authority."
    (Ausnahme: Law Enforcement, Migration, Grenzkontrolle, Asyl.)
  - Art. 14(1)–(4): menschliche Aufsicht (Human Oversight) allgemein.

Lab-Prinzip: Mechanik = aus der Quelle; die Anwendung auf ALLE Rekursionen ist
Projekt-Vorgabe (Auftrag) – die Quelle verlangt sie nur für Annex-III-1(a).

Flow: pending → first_approved → second_approved → approved

Zusatz (2026-10-02): Freigaben können an einen **Diff** gebunden werden
(`approve(person, diff_sha=...)`); beide Verifizierer müssen denselben Diff
bestätigen („separately verified and confirmed").
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class TwoPersonApproval:
    """Mindestens ZWEI distinkte natürliche Personen müssen bestätigen."""

    subject: str = ""
    approvers: list = field(default_factory=list)
    state: str = "pending"
    history: list = field(default_factory=list)
    diff_sha: Optional[str] = None  # an die Freigabe gebundener Diff (Evidence)

    def approve(self, person: str, diff_sha: Optional[str] = None) -> dict:
        """Freigabe einer natürlichen Person; optional an einen Diff gebunden.

        Beide Verifizierer müssen denselben Diff bestätigen (Quelle: „separately
        verified and confirmed"). Abweichender/fehlender Diff → abgelehnt.
        """
        if not person or not person.strip():
            return {"ok": False, "state": self.state, "reason": "keine natürliche Person angegeben"}
        if self.state == "approved":
            return {"ok": False, "state": self.state, "reason": "bereits approved"}
        if person.strip().lower() in [a.strip().lower() for a in self.approvers]:
            return {
                "ok": False,
                "state": self.state,
                "reason": f"'{person}' hat bereits bestätigt – zwei DISTINKTE Personen nötig",
            }
        if self.diff_sha is not None and diff_sha != self.diff_sha:
            return {
                "ok": False,
                "state": self.state,
                "reason": "Diff stimmt nicht mit der ersten Freigabe überein",
                "expected": self.diff_sha,
                "got": diff_sha,
            }
        if self.diff_sha is None and diff_sha is not None:
            self.diff_sha = diff_sha
        self.approvers.append(person.strip().lower())
        self.state = "first_approved" if len(self.approvers) == 1 else "second_approved"
        self.history.append({"person": person, "state": self.state, "ts": _now(), "diff_sha": diff_sha})
        return {"ok": True, "state": self.state, "approvers": list(self.approvers), "diff_sha": self.diff_sha}

    def finalize(self) -> dict:
        if len(self.approvers) < 2:
            return {
                "ok": False,
                "state": self.state,
                "reason": f"mind. 2 natürliche Personen erforderlich (aktuell {len(self.approvers)})",
            }
        self.state = "approved"
        self.history.append({"person": "(finalize)", "state": "approved", "ts": _now()})
        return {"ok": True, "state": self.state, "approvers": list(self.approvers)}

    def status(self) -> dict:
        return {
            "subject": self.subject,
            "state": self.state,
            "approvers": list(self.approvers),
            "count": len(self.approvers),
            "diff_sha": self.diff_sha,
        }


def _demo() -> None:
    print("=== Zwei-Personen-Verifikation (EU-KI-VO Art. 14(5)) ===")
    a = TwoPersonApproval(subject="Rekursion 023")
    print("  Start          :", a.status())
    print("  approve(Batnini)     ->", a.approve("Batnini"))
    print("  approve(Batnini) x2  ->", a.approve("Batnini"))  # distinkt verletzt
    print("  finalize (nur 1)     ->", a.finalize())  # < 2 Personen
    print("  approve(Verifier2)   ->", a.approve("Verifier2"))
    print("  finalize (2 Personen)->", a.finalize())
    print("  Endstatus      :", a.status())
    print("  Verlauf        :", [(h["person"], h["state"]) for h in a.history])


if __name__ == "__main__":
    _demo()
