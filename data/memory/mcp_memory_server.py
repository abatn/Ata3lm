#!/usr/bin/env python3
"""
MCP-Memory-Server – 5 Kern-Tools + Tri-Color Trust.

Quellen (HTTP 200, geprüft 2026-10-03):
  - Atomic (MCP-Interface, kenforthewin/atomic): MCP-Server exponiert die
    Knowledge-Base über Tools; Leitlinien wörtlich: „Search Atomic before
    answering", „Store durable preferences … Update stale atoms instead of
    creating duplicates." → Such-vor-Schreiben, Update statt Duplikat.
    https://atomicapp.ai/guides/mcp-server/ · https://github.com/kenforthewin/atomic
  - ATHENA / Tri-Color Trust Model (Leu, 2026, „A Provenance-Typed Edge Taxonomy"):
    jede Verbindung trägt eine Farbe nach epistemischer Herkunft:
      Blue  = explizit, vom Menschen verfasst
      Green = neuronal, KI-vorgeschlagen (pending validation)
      Red   = supervised, von formaler Constraint-Validierung geflaggt (Verstoß)
    „AI can only propose; it cannot auto-commit to curated knowledge."
    https://exa.ai/library/publication/ydhtt93r884

Lab-Prinzip §6: Mechanik = Quelle; die 5 Tool-Namen sind Auftrag.
Hinweis: `mcp` wird LAZY importiert (nur im Serverbetrieb); die Kernfunktionen
sind ohne SDK testbar.
"""

from __future__ import annotations

import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import trust as trust_mod
import write_gateway

ROOT = Path(os.environ.get("MCP_MEMORY_ROOT", str(Path(__file__).resolve().parents[2])))

# Tri-Color Trust (ATHENA): Blue = Mensch, Green = KI-Vorschlag, Red = Verstoß
TRUST_COLORS = ("blue", "green", "red")

SCOPES: dict[str, Path] = {
    "tier1": ROOT / "data/memory/tier1-base",
    "tier2": ROOT / "data/memory/tier2-index",
    "tier3": ROOT / "data/memory/tier3-working",
    "structured": ROOT / "knowledge/structured",
    "connectors": ROOT / "connectors",
    "skills": ROOT / "skills",
}

_LINKS = ROOT / "data/memory/tier2-index/mcp-links.jsonl"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _scope_dir(scope: str) -> Path:
    if scope not in SCOPES:
        raise ValueError(f"unbekannter Scope: {scope!r} (erlaubt: {sorted(SCOPES)})")
    return SCOPES[scope]


def _within(base: Path, target: Path) -> bool:
    """True, wenn `target` innerhalb von `base` liegt (beide aufgelöst/absolut)."""
    return target.is_relative_to(base)


def _path(scope: str, key: str) -> Path:
    base = _scope_dir(scope)
    key = (key or "").strip()
    if not key or ".." in key or key.startswith("/"):
        raise ValueError(f"ungültiger key: {key!r}")
    path = base / key
    # R12 §9.2c/§9.3: das AUFGELÖSTE Ziel muss im Scope liegen. Ein dangling/externer
    # Symlink würde den Schreibpfad aus dem Scope herausführen → reject (fail-closed).
    if not _within(base.resolve(), path.resolve()):
        raise ValueError(f"key verlässt den Scope (Symlink/Auflösung): {key!r}")
    return path


def _trust_key(scope: str, key_path: Path) -> str:
    """R11/R13/R14 §9.2c: Trust-Identität = **Scope + kanonischer key**.

    Der Scope ist Teil des Schlüssels, damit gleiche Dateinamen in verschiedenen
    Scopes unabhängig sind (keine Cross-Scope-Kollision/Umgehung). Das Format
    `"{scope}/{relpfad}"` entspricht dem Altschema und liest bestehende Trust-DBs.
    """
    rel = key_path.relative_to(_scope_dir(scope)).as_posix()
    return f"{scope}/{rel}"


def _trust_db_path() -> Optional[Path]:
    """Pfad der Tri-Color-Trust-DB (None, wenn kein `tier2`-Scope konfiguriert)."""
    base = SCOPES.get("tier2")
    return (base / "mcp-trust.json") if base else None


def _load_trust_db(p: Path) -> dict:
    """Tri-Color-Trust je `scope/key` (blue = bestätigt, green = Vorschlag).

    Robust (R15): fehltypisierte/undekodierbare Metadaten liefern `{}` statt zu
    crashen (der strenge Reject erfolgt in `write` über `_trust_db_malformed`).
    """
    if not p.exists():
        return {}
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}
    return data if isinstance(data, dict) else {}


def _trust_db_malformed(p: Path) -> bool:
    """R15 §9.2c/§9.3: True, wenn die DB parsebar, aber KEIN Objekt ist (`[]`, `"x"`).

    Ein reiner Parse-Fehler (`{kaputt`) gilt als „keine Metadaten" (bestehendes
    Verhalten); ein gültiges JSON des falschen Typs ist strukturell ungültig und
    wird kontrolliert abgelehnt (kein `AttributeError`).
    """
    if not p.exists():
        return False
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return False
    return not isinstance(data, dict)


def _save_trust_db(p: Path, db: dict) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(db, ensure_ascii=False), encoding="utf-8")


def read(scope: str, key: str) -> dict:
    """memory.read – Inhalt einer Ressource aus einem Scope lesen."""
    path = _path(scope, key)
    if not path.exists():
        return {"ok": False, "scope": scope, "key": key, "reason": "nicht gefunden"}
    return {"ok": True, "scope": scope, "key": key, "content": path.read_text(encoding="utf-8")}


def write(scope: str, key: str, content: str, trust: str = "green") -> dict:
    """memory.write – schreiben mit Tri-Color-Gate.

    Blue = menschlich bestätigt (confirmed) · Green = KI-Vorschlag (proposed,
    pending validation) · Red = Constraint-Verstoß (rejected, kein Write).
    Quelle: „AI can only propose; it cannot auto-commit."

    Gate (§9.2c/§9.3/§10.7): `green` darf ein **bestätigtes** `blue` **nicht**
    überschreiben; `tier1` (kuratiert) nur mit `blue`. **§9.2a:** PII wird VOR
    dem Store entfernt (`trust.PIIFilter.minimize`). **N5 (§6/K8):** ein
    `structured`-Write trägt den §6-Kopf (`Ontologie-Bezug`/`Quelle`/`Evidence`);
    alle übrigen Scopes bleiben body-only (unverändert). **F4:** Der Kopf wird
    **nach** der PII-Sanitisierung im Write-Gateway erzeugt, damit `sha256`/Datum
    unangetastet bleiben.
    """
    if trust not in TRUST_COLORS:
        return {"ok": False, "reason": f"ungültige Trust-Farbe {trust!r} (erlaubt: {TRUST_COLORS})"}
    path = _path(scope, key)
    if trust == "red":
        return {
            "ok": False,
            "status": "rejected",
            "scope": scope,
            "key": key,
            "reason": "Tri-Color Red: Constraint-Verstoß – nicht gespeichert",
        }
    db_path = _trust_db_path()
    if db_path is None:
        # §9.2c/§9.3: FAIL-CLOSED — ohne Trust-Metadaten KEIN Write (nie fail-open).
        return {
            "ok": False,
            "status": "rejected",
            "scope": scope,
            "key": key,
            "reason": "Trust-Metadaten (tier2) nicht verfügbar → fail-closed (§9.2c/§9.3)",
        }
    db = _load_trust_db(db_path)
    if _trust_db_malformed(db_path):
        # R15 §9.2c/§9.3: parsebar, aber kein Objekt (`[]`) → kontrolliert ablehnen.
        return {
            "ok": False,
            "status": "rejected",
            "scope": scope,
            "key": key,
            "reason": "Trust-Metadaten fehltypisiert (kein Objekt) → fail-closed (§9.2c/§9.3)",
        }
    db_key = _trust_key(scope, path)  # R11/R13/R14: Scope + kanonischer key
    if path.exists() and db.get(db_key) is None:
        # N2 §9.2c/§9.3: existierende Zieldatei + unbekannter Trust -> fail-closed.
        # Nur „keine Datei" darf grün sein (auch bei fehlender/kaputter Trust-DB).
        return {
            "ok": False,
            "status": "rejected",
            "scope": scope,
            "key": key,
            "reason": "existierende Zieldatei + unbekannter Trust → fail-closed (§9.2c/§9.3)",
        }
    if db.get(db_key) == "blue" and trust == "green":
        return {
            "ok": False,
            "status": "rejected",
            "scope": scope,
            "key": key,
            "reason": "green (Vorschlag) darf bestätigtes blue nicht überschreiben (§9.2c/§10.7)",
        }
    if scope == "tier1" and trust != "blue":
        return {
            "ok": False,
            "status": "rejected",
            "scope": scope,
            "key": key,
            "reason": "tier1 (kuratiert) nur mit trust=blue + Approval (§9.2c/§9.3)",
        }
    clean = trust_mod.PIIFilter().minimize(content)  # §9.2a: PII vor dem Store entfernen
    # N5 (Auftrag, §6/K8) + F4 (Audit 75095d5): Der §6-Kopf (`Ontologie-Bezug`/
    # `Quelle`/`Evidence`) wird **erst NACH** der PII-Sanitisierung erzeugt — im
    # Write-Gateway (`structured=True`), das nur den **Body** bereinigt. Andernfalls
    # entfernt der PII-Filter die Ziffern aus `sha256`/Datum im Kopf (F4).
    # Nicht-`structured`-Writes (JSONL/History/tier1/tier3) bleiben UNVERÄNDERT Body-only.
    res = write_gateway.store_file(
        target=path,
        content=clean,
        now=time.time(),
        activity=f"mcp-write:{scope}",
        agent="mcp-memory-server",
        origin="tool:verified",
        verified=True,  # Tri-Color-Gate + Trust-DB = Write-Time-Validation (§9.2c)
        structured=(scope == "structured"),
        provenance_log=(SCOPES.get("tier3") or path.parent) / "provenance.jsonl",
    )
    if not res["ok"]:
        return {"ok": False, "status": "rejected", "scope": scope, "key": key, "reason": res.get("reason", "")}
    db[db_key] = trust
    _save_trust_db(db_path, db)
    status = "confirmed" if trust == "blue" else "proposed"
    return {
        "ok": True,
        "status": status,
        "trust": trust,
        "scope": scope,
        "key": key,
        "bytes": len(path.read_text(encoding="utf-8").encode("utf-8")),
    }


def search(query: str, scope: Optional[str] = None) -> dict:
    """memory.search – Such-vor-Schreiben (Atomic): Textsuche über Scope(s)."""
    if not query:
        return {"ok": False, "reason": "leere query"}
    scopes = [scope] if scope is not None else sorted(SCOPES)
    hits: list[dict] = []
    for sc in scopes:
        base = _scope_dir(sc)
        for p in sorted(base.rglob("*")):
            if not p.is_file():
                continue
            try:
                for i, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
                    if query.lower() in line.lower():
                        hits.append(
                            {"scope": sc, "file": str(p.relative_to(base)), "line": i, "text": line.strip()[:200]}
                        )
            except (UnicodeDecodeError, OSError):
                continue
    return {"ok": True, "query": query, "n_hits": len(hits), "hits": hits[:50]}


def link(a: str, b: str, trust: str = "green") -> dict:
    """memory.link – typisierte Kante (Tri-Color) anlegen."""
    if trust not in TRUST_COLORS:
        return {"ok": False, "reason": f"ungültige Trust-Farbe {trust!r}"}
    if not a or not b:
        return {"ok": False, "reason": "a und b erforderlich"}
    if trust == "red":
        return {"ok": False, "status": "rejected", "reason": "Tri-Color Red: Verstoß"}
    _LINKS.parent.mkdir(parents=True, exist_ok=True)
    edge = {"from": a, "to": b, "trust": trust, "status": "confirmed" if trust == "blue" else "proposed", "ts": _now()}
    with open(_LINKS, "a", encoding="utf-8") as f:
        f.write(json.dumps(edge, ensure_ascii=False) + "\n")
    return {"ok": True, "edge": edge}


def consolidate() -> dict:
    """memory.consolidate – Bestand je Scope zählen und Index schreiben."""
    report = {}
    for sc, base in SCOPES.items():
        files = [p for p in base.rglob("*") if p.is_file()] if base.exists() else []
        report[sc] = {"files": len(files), "dir": str(base)}
    out = SCOPES["tier2"] / "mcp-consolidation.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    rows = "\n".join(f"| {sc} | {v['files']} | {v['dir']} |" for sc, v in report.items())
    out.write_text(
        f"# MCP-Konsolidierung ({_now()})\n\n| Scope | Dateien | Pfad |\n|---|---|---|\n{rows}\n", encoding="utf-8"
    )
    return {"ok": True, "scopes": report, "written": str(out)}


# ---------------------------------------------------------------------------
# MCP-Wiring (lazy – SDK nur im Serverbetrieb nötig)
# ---------------------------------------------------------------------------
def build_server():  # pragma: no cover - nur mit realem mcp-SDK (Python >=3.10)
    """FastMCP-Server mit den 5 Kern-Tools (Atomic-MCP-Interface)."""
    from mcp.server.fastmcp import FastMCP

    server = FastMCP("knowledge-agent-memory")
    server.add_tool(read, name="memory.read", description="Ressource aus einem Scope lesen")
    server.add_tool(write, name="memory.write", description="Schreiben mit Tri-Color-Gate (blue/green/red)")
    server.add_tool(search, name="memory.search", description="Volltextsuche (Such-vor-Schreiben)")
    server.add_tool(consolidate, name="memory.consolidate", description="Bestand zählen + Index schreiben")
    server.add_tool(link, name="memory.link", description="typisierte Kante mit Tri-Color-Trust")
    return server


def main() -> None:  # pragma: no cover - nur im Serverbetrieb
    build_server().run()


if __name__ == "__main__":  # pragma: no cover
    main()
