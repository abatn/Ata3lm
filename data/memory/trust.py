#!/usr/bin/env python3
"""
Trust & Governance – Privacy, Bias, Adversarial Robustness (Guards vor dem Store).

Quellen (verifiziert 2026-10-01, HTTP 200):
  - Privacy: SP-Mem (arXiv:2608.16551) – „identify and separate sensitive
    information … store sanitized content … isolated structures". agentmemory:
    „API keys, secrets, <private> tags stripped before storage".
  - Bias: DIB / Dynamic Memory Tagging (arXiv:2602.01558) – „Periodic Bias
    Evaluation" gegen Benchmark-Ground-Truth; Fairness-Tag beim Memory-Write.
    Memory Contagion (arXiv:2606.23195); MemAudit (arXiv:2606.24595, Ground-Truth-Audit).
  - Adversarial: MPBench (arXiv:2606.04329, V-S1 „No Write-Path Validation"),
    A-MemGuard (arXiv:2510.02373, Consensus-Validation), TMA-NM (arXiv:2606.24322,
    „write-time origin binding is necessary"), LTM-Security-Survey (arXiv:2604.16548,
    Verifiable Memory Governance), TrustAgent (arXiv:2503.09648).

Lab-Prinzip: Mechanik = aus den Quellen; Schwellen = Auftrag.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

# =====================================================================
# 1. Privacy – PII-Erkennung + Anonymisierung (SP-Mem; agentmemory)
# =====================================================================
# Reihenfolge = Priorität: spezifische Muster (IBAN/Karte) VOR dem greedy phone.
PII_PATTERNS = {
    "email": re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+"),
    "iban": re.compile(r"\b[A-Z]{2}\d{2}[A-Z0-9]{10,30}\b"),
    "credit_card": re.compile(r"\b(?:\d[ -]?){13,16}\b"),
    "phone": re.compile(r"\+?\d[\d\s().\-]{7,}\d"),
}


class PIIFilter:
    """Erkennt PII und LÖSCHT sie vor dem Speichern (Datenminimierung, kein LLM).

    Statt `[PII:<typ>]` (Markierung) wird der PII-Span **entfernt**:
    - DSGVO Art. 5(1)(c): Datenminimierung („limited to what is necessary").
    - EU-KI-VO Art. 10(5): personenbezogene Daten minimieren/löschen.
    „Sparse": nur die sensiblen Spans werden entfernt, der übrige Text bleibt.
    """

    def detect(self, text: str) -> list[str]:
        return [kind for kind, pat in PII_PATTERNS.items() if pat.search(text or "")]

    def minimize(self, text: str) -> str:
        out = text or ""
        for _kind, pat in PII_PATTERNS.items():
            out = pat.sub("", out)
        return re.sub(r"\s{2,}", " ", out).strip()

    # Abwärtskompatibler Alias – löscht ebenfalls (keine Markierung):
    anonymize = minimize


# =====================================================================
# 2. Adversarial Robustness – Poisoning-Guard (MPBench/A-MemGuard/TMA-NM)
# =====================================================================
@dataclass
class PoisoningGuard:
    """Nur verifizierte Items werden gespeichert.

    „Verifiziert" = Quelle in der Allowlist (origin-bound, TMA-NM) UND
    verifiziert-Flag (Consensus/Prüfung, A-MemGuard). Alles andere → rejected
    (MPBench: „no write-path validation" ist die Lücke).
    """

    trusted_sources: set = field(default_factory=lambda: {"user", "tool:verified", "system"})

    def admit(self, item: dict) -> dict:
        src = item.get("source")
        verified = bool(item.get("verified"))
        if src not in self.trusted_sources:
            return {"admitted": False, "reason": f"untrusted source '{src}' (origin-bound)"}
        if not verified:
            return {"admitted": False, "reason": "not verified (consensus/verification required)"}
        return {"admitted": True, "reason": "verified + trusted origin"}


# =====================================================================
# 3. Bias – periodischer Check gegen Ground-Truth-Checkpoint (DIB/DMT)
# =====================================================================
@dataclass
class BiasCheck:
    """Vergleicht einen aktuellen Bias-Score gegen einen Ground-Truth-Checkpoint.

    DIB/DMT (arXiv:2602.01558): „Periodic Bias Evaluation" gegen Benchmark-
    Ground-Truth; Schwellwert tau = Auftrag.
    """

    checkpoint: float  # Ground-Truth-Score (Referenz)
    tau: float = 0.10  # Auftrag: max. tolerierte Abweichung

    def check(self, current: float) -> dict:
        drift = current - self.checkpoint
        flagged = abs(drift) > self.tau
        return {
            "current": current,
            "checkpoint": self.checkpoint,
            "drift": round(drift, 4),
            "flagged": flagged,
            "status": "flag" if flagged else "ok",
        }


# =====================================================================
# Demo / Selbsttest
# =====================================================================
def _demo() -> None:
    print("=== [1] Privacy: PII-Minimierung – PII wird GELÖSCHT (DSGVO Art. 5(1)(c)) ===")
    pii = PIIFilter()
    cases = [
        "Kontakt: max.mustermann@example.com bitte melden",
        "Ruf mich an: +49 30 1234567",
        "IBAN DE89370400440532013000 überweisen",
    ]
    for c in cases:
        print(f"  vorher : {c}")
        print(f"  erkannt: {pii.detect(c)}  -> nachher: '{pii.minimize(c)}'")

    print("\n=== [2] Adversarial: Poisoning-Guard (MPBench/A-MemGuard/TMA-NM) ===")
    guard = PoisoningGuard()
    for item in [
        {"source": "user", "verified": True, "content": "Fakt A"},
        {"source": "web:untrusted", "verified": True, "content": "Fakt B"},
        {"source": "user", "verified": False, "content": "Fakt C"},
    ]:
        r = guard.admit(item)
        print(f"  {item['source']:14} verified={item['verified']!s:5} -> admitted={r['admitted']} | {r['reason']}")

    print("\n=== [3] Bias: periodischer Check gegen Ground-Truth (DIB/DMT) ===")
    bc = BiasCheck(checkpoint=0.05, tau=0.10)  # Referenz: niedriger Bias
    for cur in [0.06, 0.09, 0.20]:
        print(f"  current={cur} ->", bc.check(cur))


if __name__ == "__main__":
    _demo()
