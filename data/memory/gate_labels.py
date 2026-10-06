#!/usr/bin/env python3
"""
Einheitlicher Gate-Labelraum (K6/B5): ``allow`` | ``ask`` | ``deny``.

Befund (K6, `ergebnisse/kopplung-komponenten-bericht.md` §2 K6): die Gate-Labels
waren pro Modul verschieden (``ok``/``ask``, ``none``/``ask``,
``ALLOW``/``REVIEW``/``DENY``, ``allow``/``ask``/``deny``). Ein Labelraum
verhindert, dass ``deny`` durch eine ``gate != ask``-Prüfung „mit durchrutscht"
(Review-Korrektur 4: **nie** ``!= ask``, immer ``== "allow"``).

Status (§6): Der **Labelraum** ist **Auftrag** (Betriebsregel, K6). Die
Zuordnung der Mandats-Entscheidungen folgt AGENTS.md §9 (``ALLOW`` →
automatisch, ``REVIEW`` → Human-Gate (ask), ``DENY`` → blockiert) — ebenfalls
**Auftrag**, kein Paper-Claim.

Regeln:
- ``normalize()`` bildet Alt-Labels auf den Labelraum ab; **unbekannte Labels
  werden zu ``ask``** (fail-safe: nie still erlauben).
- ``is_allow()`` ist die einzige Erlaubnis-Prüfung. ``gate != "ask"`` ist
  verboten, weil es ``deny`` passieren ließe.
"""

from __future__ import annotations

ALLOW = "allow"
ASK = "ask"
DENY = "deny"

GATE_LABELS = (ALLOW, ASK, DENY)

# Alt-Labelräume (K6-Befund) -> kanonisch.
_CANONICAL = {
    "allow": ALLOW,
    "ask": ASK,
    "deny": DENY,
    "ok": ALLOW,  # bias_monitor / lyapunov_check (Alt)
    "none": ALLOW,  # fast_write_router (Alt: „kein Gate nötig")
    "ALLOW": ALLOW,  # mandate.assess (AGENTS.md §9)
    "REVIEW": ASK,
    "DENY": DENY,
}


def normalize(value) -> str:
    """Bekanntes Label auf ``allow|ask|deny`` abbilden; unbekannt ⇒ ``ask`` (fail-safe)."""
    return _CANONICAL.get(str(value).strip(), ASK)


def is_allow(gate) -> bool:
    """Erlaubt nur ``allow`` — ``!= ask`` wäre ein Fehler (ließe ``deny`` durch)."""
    return normalize(gate) == ALLOW


def is_deny(gate) -> bool:
    """True nur bei ``deny`` (blockiert)."""
    return normalize(gate) == DENY
