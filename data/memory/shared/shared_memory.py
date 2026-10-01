#!/usr/bin/env python3
"""
Multi-Agent Shared Memory Tier – gemeinsame Schicht mit Sync & Konflikt-Erkennung.

Quelle (verifiziert 2026-10-01, HTTP 200):
  - Memory Survey (arXiv:2603.07670) §6.5 „Multi-agent collaboration": „shared vs.
    private memory boundaries"; „consistency under concurrent writes". §9.6
    „Multi-agent memory governance": „access control over shared stores, consensus
    protocols for concurrent writes … distributed memory with merge semantics …
    remain wide open."
  - Collaborative Memory (arXiv:2505.18279): zwei Tiers (private / shared),
    asymmetrische Zugriffskontrolle, unveränderliche Provenienz.

Lab-Prinzip: Mechanik = aus den Quellen; die konkrete Tier-/ACL-Mechanik ist
Projekt-Vorgabe (Auftrag). Kein Löschen bei Konflikt — alter Eintrag wird
superseded (bi-temporal), vgl. Graphiti.
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
    status: str = "valid"        # valid | superseded
    supersedes: int = 0
    invalid_at: str = ""


class SharedTier:
    """Gemeinsame Schicht: mehrere Agenten lesen/schreiben; versioniert + konfliktgeprüft.

    ACL: agent -> {"read": set, "write": set}  ("*" = alle Keys).
    """

    def __init__(self, acl: Optional[dict] = None):
        self.entries: dict[str, Entry] = {}       # key -> aktuell gültiger Eintrag
        self.history: list[Entry] = []
        self.versions: dict[str, int] = {}        # key -> letzte Version
        self.acl: dict = acl or {}

    # --- Zugriffskontrolle (Memory Survey §6.5/§9.6; Collaborative Memory) ---
    def _can(self, agent: str, key: str, mode: str) -> bool:
        rule = self.acl.get(agent, {})
        allowed = rule.get(mode, set())
        return "*" in allowed or key in allowed

    # --- Schreiben (versioniert + Konflikt-Erkennung) ---
    def write(self, agent: str, key: str, value: str) -> dict:
        if not self._can(agent, key, "write"):
            return {"ok": False, "reason": f"{agent}: kein Schreibrecht auf '{key}'"}
        v = self.versions.get(key, 0) + 1
        self.versions[key] = v
        e = Entry(key=key, value=value, version=v, writer=agent, ts=_now())
        cur = self.entries.get(key)
        superseded = None
        if cur is not None and cur.value != value:
            # cur ist bereits in self.history (mutieren genügt – kein Doppel-Eintrag)
            cur.status = "superseded"
            cur.invalid_at = e.ts
            e.supersedes = cur.version
            superseded = cur.version
        conflict = (cur is not None and cur.value != value and cur.writer != agent)
        self.entries[key] = e
        self.history.append(e)
        return {"ok": True, "version": v, "conflict": conflict, "superseded": superseded}

    # --- Lesen ---
    def read(self, agent: str, key: str) -> dict:
        if not self._can(agent, key, "read"):
            return {"ok": False, "reason": f"{agent}: kein Leserecht auf '{key}'"}
        e = self.entries.get(key)
        return {"ok": True, "value": e.value if e else None,
                "version": e.version if e else None, "writer": e.writer if e else None}

    # --- Sync: Konflikte über die Historie erkennen (gleicher Key, versch. Werte) ---
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
                                  "rule": "prefer newest (Memory Survey)"})
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
        "agentC": {"read": {"public.*"}, "write": set()},   # nur Lesen, eingeschränkt
    }
    tier = SharedTier(acl)

    print("=== [1] Zwei Agenten schreiben denselben Key (konkurrierend) ===")
    r1 = tier.write("agentA", "solver.current_version", "berechne_durchschnitt")
    print("  agentA write ->", r1)
    r2 = tier.write("agentB", "solver.current_version", "berechne_median")
    print("  agentB write ->", r2)

    print("\n=== [2] Sync: Konflikt-Erkennung ===")
    print(" ", tier.sync())

    print("\n=== [3] Lesen (Sicht je Agent) ===")
    print("  agentA read:", tier.read("agentA", "solver.current_version"))
    print("  agentC read (kein Recht):", tier.read("agentC", "solver.current_version"))
    print("  agentC write (kein Recht):", tier.write("agentC", "solver.current_version", "x"))

    print("\n=== [4] Versionierte Historie ===")
    for e in tier.history:
        print(f"  v{e.version} {e.key} = {e.value} | {e.writer} | {e.status}"
              + (f" | supersedes v{e.supersedes}" if e.supersedes else ""))

    tier.dump(Path("/tmp/opencode/shared_store.jsonl"))
    print("\n  Store (Demo): /tmp/opencode/shared_store.jsonl")


if __name__ == "__main__":
    _demo()
