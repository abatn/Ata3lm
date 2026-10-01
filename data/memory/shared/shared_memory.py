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
    status: str = "valid"        # valid | superseded
    supersedes: int = 0
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

        cur = self.entries.get(key)
        new_trust = float(self.trust.get(agent, 0.0))
        # Trigger: zwei Agenten, gleicher Key, verschiedene Werte
        conflict = cur is not None and cur.value != value

        # Auflösung: Trust-Score – niedrigerer Trust überschreibt NICHT
        if conflict and new_trust < cur.trust:
            return {"ok": False, "phase": "resolution", "conflict": True,
                    "reason": f"niedrigerer Trust {new_trust} < {cur.trust}; aktueller Wert bleibt",
                    "current": cur.value, "current_writer": cur.writer}

        v = self.versions.get(key, 0) + 1
        self.versions[key] = v
        e = Entry(key=key, value=value, version=v, writer=agent, ts=_now(), trust=new_trust)
        superseded = None
        if conflict:
            cur.status = "superseded"                          # Supersede-Marker (kein Löschen)
            cur.invalid_at = e.ts
            e.supersedes = cur.version
            superseded = cur.version
        self.entries[key] = e
        self.history.append(e)
        return {"ok": True, "phase": "commit", "version": v, "conflict": conflict,
                "superseded": superseded, "trust": new_trust}

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
                                  "rule": "versioning + supersede + trust (Memory Survey)"})
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
        "agentC": {"read": {"public.*"}, "write": set()},
    }
    trust = {"agentA": 0.9, "agentB": 0.5, "agentC": 0.0}
    schema = {"config.mode": {"fast", "safe"}}
    tier = SharedTier(acl, trust, schema)

    print("=== [1] Trigger: zwei Agenten, gleicher Key, verschiedene Werte ===")
    print("  agentA (trust 0.9) write ->", tier.write("agentA", "solver.current_version", "berechne_durchschnitt"))

    print("\n=== [2] Auflösung: Trust-Score (niedrigerer Trust verliert) ===")
    print("  agentB (trust 0.5) write ->", tier.write("agentB", "solver.current_version", "berechne_median"))
    print("  agentA (trust 0.9) write ->", tier.write("agentA", "solver.current_version", "berechne_median"))

    print("\n=== [3] Kollisionsvalidierung VOR dem Write ===")
    print("  Schema-Verstoß (config.mode=turbo) ->", tier.write("agentA", "config.mode", "turbo"))
    print("  leerer Wert ->", tier.write("agentA", "solver.current_version", "  "))

    print("\n=== [4] Sync + Historie ===")
    print(" ", tier.sync())
    for e in tier.history:
        print(f"  v{e.version} {e.key} = {e.value} | {e.writer} (trust {e.trust}) | {e.status}"
              + (f" | supersedes v{e.supersedes}" if e.supersedes else ""))

    tier.dump(Path("/tmp/opencode/shared_store.jsonl"))
    print("\n  Store (Demo): /tmp/opencode/shared_store.jsonl")


if __name__ == "__main__":
    _demo()
