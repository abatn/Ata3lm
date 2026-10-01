#!/usr/bin/env python3
"""
Multi-Agent Shared Memory Tier – Konfliktauflösung (Versionierung · Supersede · Trust).

Quelle (verifiziert 2026-10-01, HTTP 200):
  - Memory Survey (arXiv:2603.07670) §6.5 „Multi-agent collaboration": „shared vs.
    private memory boundaries"; „**consistency under concurrent writes**". §9.6
    „Multi-agent memory governance": „access control over shared stores, **consensus
    protocols for concurrent writes** … distributed memory with **merge semantics** …
    remain **wide open**." (→ Frontier-Direktion; konkrete Mechanik = Auftrag.)
  - Memory Survey (Write-Path): „source attribution (user statement > agent inference)"
    → Grundlage für Trust-Ordnung. Collaborative Memory (arXiv:2505.18279):
    private/shared-Tiers, asymmetrische Zugriffskontrolle, Provenienz.
  - Graphiti (arXiv:2501.13956): bi-temporal – invalidieren statt löschen.

Lab-Prinzip: Mechanik = aus den Quellen; die konkrete Auflösungsstrategie
(Trust-Grenze, Supersede-Marker, Schema) ist Projekt-Vorgabe (Auftrag).

Hinweis: Der Auftrag nennt `data/memory/shared_memory.py`; die Datei liegt unter
`data/memory/shared/shared_memory.py`.
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

ROOT = Path("/home/opc/knowledge-agent")
SHARED = ROOT / "data/memory/shared"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class Entry:
    key: str
    value: str
    version: int
    writer: str
    ts: str
    trust: float = 0.0
    status: str = "confirmed"    # confirmed | superseded | contested  (LatticeMind-Status)
    supersedes: int = 0          # Version, die dieser Eintrag ablöst
    superseded_by: int = 0       # Version, die DIESEN Eintrag ablöst (unterlegen; nicht gelöscht)
    invalid_at: str = ""


class SharedTier:
    """Gemeinsame Schicht: mehrere Agenten lesen/schreiben.

    - ACL:        agent -> {"read": set, "write": set}   ("*" = alle Keys)
    - Trust:      agent -> float (0..1)  (Memory Survey: „source attribution")
    - Schema:     key   -> set(erlaubte Werte)           (Konsistenz-Check)
    """

    def __init__(self, acl: Optional[dict] = None, trust: Optional[dict] = None,
                 schema: Optional[dict] = None):
        self.entries: dict[str, Entry] = {}
        self.history: list[Entry] = []
        self.versions: dict[str, int] = {}
        self.acl: dict = acl or {}
        self.trust: dict = trust or {}
        self.schema: dict = schema or {}

    # --- Zugriffskontrolle (Memory Survey §6.5/§9.6; Collaborative Memory) ---
    def _can(self, agent: str, key: str, mode: str) -> bool:
        rule = self.acl.get(agent, {})
        allowed = rule.get(mode, set())
        return "*" in allowed or key in allowed

    # --- Kollisionsvalidierung: VOR jedem Write (Konsistenzprüfung) ---
    def validate_write(self, agent: str, key: str, value: str) -> dict:
        if not self._can(agent, key, "write"):
            return {"ok": False, "reason": f"{agent}: kein Schreibrecht auf '{key}'"}
        if not (value or "").strip():
            return {"ok": False, "reason": "leerer Wert"}
        allowed = self.schema.get(key)
        if allowed is not None and value not in allowed:
            return {"ok": False, "reason": f"Wert '{value}' nicht erlaubt (Schema: {sorted(allowed)})"}
        return {"ok": True, "reason": "konsistent"}

    # --- Schreiben: Trigger → Validierung → Auflösung (Trust) → Commit ---
    def write(self, agent: str, key: str, value: str) -> dict:
        chk = self.validate_write(agent, key, value)          # Konsistenzprüfung
        if not chk["ok"]:
            return {"ok": False, "phase": "validation", "reason": chk["reason"]}

        cur = self.entries.get(key)                 # aktuell CONFIRMED (LatticeMind)
        new_trust = float(self.trust.get(agent, 0.0))
        v = self.versions.get(key, 0) + 1
        self.versions[key] = v
        e = Entry(key=key, value=value, version=v, writer=agent, ts=_now(), trust=new_trust)

        # Write-Time-Konfliktlösung (LatticeMind): Trust-Score entscheidet.
        if cur is None or cur.value == value:
            e.status = "confirmed"                  # neu oder Evidence-Accumulation
            self.entries[key] = e
            outcome, conflict = "confirmed", False
        else:
            conflict = True
            if new_trust > cur.trust:               # stärkerer Trust gewinnt
                cur.status = "superseded"
                cur.invalid_at = e.ts
                cur.superseded_by = v               # unterlegen: superseded_by (nicht gelöscht)
                e.supersedes = cur.version
                e.status = "confirmed"
                self.entries[key] = e
                outcome = "superseded_old"
            elif new_trust < cur.trust:             # schwächerer Trust → unterlegen, behalten
                e.status = "superseded"
                e.superseded_by = cur.version
                outcome = "superseded_new"
            else:                                   # Gleichstand → contested (LatticeMind)
                e.status = "contested"
                outcome = "contested"
        self.history.append(e)
        return {"ok": True, "phase": "commit", "version": v, "conflict": conflict,
                "outcome": outcome, "status": e.status,
                "current": self.entries[key].value, "current_version": self.entries[key].version}

    # --- Lesen ---
    def read(self, agent: str, key: str) -> dict:
        if not self._can(agent, key, "read"):
            return {"ok": False, "reason": f"{agent}: kein Leserecht auf '{key}'"}
        e = self.entries.get(key)
        return {"ok": True, "value": e.value if e else None,
                "version": e.version if e else None, "writer": e.writer if e else None,
                "trust": e.trust if e else None}

    # --- Sync: Konflikte über die Historie (gleicher Key, versch. Werte) ---
    def sync(self) -> dict:
        by_key: dict[str, list[Entry]] = {}
        for e in self.history:
            by_key.setdefault(e.key, []).append(e)
        conflicts = []
        for k, es in by_key.items():
            vals = sorted({e.value for e in es})
            if len(vals) > 1:
                conflicts.append({"key": k, "values": vals,
                                  "resolved_to": self.entries[k].value,
                                  "rule": "versioning + trust-supersession (LatticeMind; Memory Survey)"})
        return {"conflicts": conflicts, "keys": len(self.entries)}

    def dump(self, path: Path) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            for e in self.history:
                f.write(json.dumps(asdict(e), ensure_ascii=False) + "\n")
        return path


def _demo() -> None:
    acl = {
        "agentA": {"read": {"*"}, "write": {"*"}},
        "agentB": {"read": {"*"}, "write": {"*"}},
        "agentC": {"read": {"*"}, "write": {"*"}},
    }
    trust = {"agentA": 0.5, "agentB": 0.9, "agentC": 0.3}
    schema = {"config.mode": {"fast", "safe"}}
    tier = SharedTier(acl, trust, schema)

    print("=== [1] Write-Time-Konfliktlösung (Trust-Score entscheidet) ===")
    print("  agentA(0.5) ->", tier.write("agentA", "solver.current_version", "berechne_durchschnitt"))
    print("  agentB(0.9) ->", tier.write("agentB", "solver.current_version", "berechne_median"))
    print("  agentC(0.3) ->", tier.write("agentC", "solver.current_version", "berechne_summe"))

    print("\n=== [2] Kollisionsvalidierung VOR dem Write ===")
    print("  Schema-Verstoß (config.mode=turbo) ->", tier.write("agentA", "config.mode", "turbo"))
    print("  leerer Wert                        ->", tier.write("agentA", "solver.current_version", "  "))

    print("\n=== [3] Historie: Supersession (kein Löschen) ===")
    for e in tier.history:
        sb = f" | superseded_by v{e.superseded_by}" if e.superseded_by else ""
        ss = f" | supersedes v{e.supersedes}" if e.supersedes else ""
        print(f"  v{e.version} {e.value} | {e.writer}(trust {e.trust}) | {e.status}{sb}{ss}")

    print("\n=== [4] Sync (aktueller CONFIRMED-Wert) ===")
    print(" ", tier.sync())

    tier.dump(Path("/tmp/opencode/shared_store.jsonl"))
    print("\n  Store (Demo): /tmp/opencode/shared_store.jsonl")


if __name__ == "__main__":
    _demo()
