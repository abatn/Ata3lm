#!/usr/bin/env python3
"""
Geteilter, persistenter Runner-Zustand (K1) — für 8-Stufen- und 5-Phasen-Runner.

Befund (Bericht §2 K1): beide Runner erzeugen eigenen Zustand; WM/Graph/HMM sind
in-memory. Lösung: **ein** Snapshot-Format + `reconstruct()`; der Snapshot enthält
**Inhalte, Metadaten, Schema-/Revisionsstand und offene Freigaben** — NIE nur
Schlüssel (K1-STOPP, `validate()`). Nebenläufigkeit (Lock) und Wiederherstellung
nach Schreibabbrüchen (atomares Schreiben + tmp-Recovery) sind geregelt.

Quellen (Belegt, verifiziert über AGENTS.md-Tabelle/Bericht §5): MemGPT
(arXiv:2310.08560) — hierarchische Memory-Tiers + Interrupts; Dual-Layer Θ+E
(arXiv:2608.22215). **Abgrenzung:** MemGPT stützt das *Muster*; dieses
`runner_state`-Interface ist **Auftrag** (K1), kein Paper-Claim.
"""

from __future__ import annotations

import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import ingestion_hook
import lru_cache
import reflective_agent

SCHEMA_VERSION = 1
LOCK_STALE_S = 60.0  # Auftrag: Locks älter als 60s gelten als abgebrochen


class StateError(Exception):
    """Snapshot ungültig (K1-STOPP) oder nicht wiederherstellbar."""


def _iso(ts: Optional[float] = None) -> str:
    return datetime.fromtimestamp(ts if ts is not None else time.time(), tz=timezone.utc).isoformat()


# ---------------------------------------------------------------- Snapshot
def _wm_state(wm) -> Optional[dict]:
    if wm is None:
        return None
    return {
        "capacity": wm.capacity,
        "tick": wm.tick,
        "evicted": list(wm.evicted),
        "log": list(wm.log),
        # K1: INHALTE + Metadaten, nicht nur Schlüssel
        "items": {key: dict(meta) for key, meta in wm.items.items()},
    }


def _graph_state(graph) -> Optional[dict]:
    if graph is None:
        return None
    return {
        "nodes": {name: dict(meta) for name, meta in graph.nodes.items()},
        "edges": [[s, p, o, float(w)] for (s, p, o), w in graph.edges.items()],
    }


def _hmm_state(hmm) -> Optional[dict]:
    if hmm is None:
        return None
    return {"states": hmm.K, "lr": hmm.lr, "beta": hmm.beta, "P": hmm.P.tolist()}


def snapshot(
    *,
    wm=None,
    graph=None,
    hmm=None,
    drift_reference=None,
    schema: Optional[dict] = None,
    open_approvals=None,
    runner: str = "",
    now: Optional[float] = None,
) -> dict:
    """Vollständiger Snapshot: WM-Inhalte+Metadaten, Graph, HMM, Drift-Checkpoint,
    Schema-/Revisionsstand (`schema`) und offene Freigaben (`open_approvals`)."""
    state = {
        "schema_version": SCHEMA_VERSION,
        "runner": runner,
        "created": _iso(now),
        "wm": _wm_state(wm),
        "graph": _graph_state(graph),
        "hmm": _hmm_state(hmm),
        "drift": {"reference": drift_reference},
        "schema": dict(schema or {}),
        "open_approvals": list(open_approvals or []),
    }
    validate(state)
    return state


def validate(state: dict) -> None:
    """K1-STOPP: Snapshot mit nur Schlüsseln ohne Inhalte/Metadaten wird abgelehnt."""
    if not isinstance(state, dict) or not isinstance(state.get("schema_version"), int):
        raise StateError("Snapshot ohne schema_version")
    if not isinstance(state.get("schema"), dict):
        raise StateError("Snapshot ohne Schema-/Revisionsstand")
    if not isinstance(state.get("open_approvals"), list):
        raise StateError("Snapshot ohne offene Freigaben")
    wm = state.get("wm")
    if wm is not None:
        items = wm.get("items")
        if not isinstance(items, dict):
            raise StateError("Snapshot speichert nur Schlüssel ohne Inhalt/Metadaten (K1-STOPP)")
        for key, meta in items.items():
            if not isinstance(meta, dict) or "value" not in meta or "last_used" not in meta:
                raise StateError(f"WM-Eintrag '{key}' ohne Inhalt/Metadaten (K1-STOPP)")
    graph = state.get("graph")
    if graph is not None and not isinstance(graph.get("nodes"), dict):
        raise StateError("Graph-Snapshot ohne Knoten/Metadaten")
    hmm = state.get("hmm")
    if hmm is not None and hmm.get("P") is None:
        raise StateError("HMM-Snapshot ohne Übergangsmatrix")


# -------------------------------------------------- Persistenz (atomar + Lock)
def save(state: dict, path) -> dict:
    """Atomar speichern (tmp + `os.replace`) mit Lock gegen parallele Schreiber.

    - Schreibabbruch: tmp bleibt liegen, die alte Datei bleibt gültig (Atomicität).
    - Nebenläufigkeit: zweiter Schreiber bekommt `ok: False` (Lock) statt still
      zu überschreiben (Compare-and-swap-Ersatz; Auftrag K1).
    """
    validate(state)  # K1-STOPP vor jedem Schreiben
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    lock = Path(str(path) + ".lock")
    fd = _acquire_lock(lock)
    if fd is None:
        return {"ok": False, "path": str(path), "reason": "lock gehalten (Nebenläufigkeit)", "lock": str(lock)}
    try:
        tmp = Path(str(path) + ".tmp")
        tmp.write_text(json.dumps(state, ensure_ascii=False, sort_keys=True), encoding="utf-8")
        os.replace(tmp, path)  # atomar: nie halb geschriebener Zustand sichtbar
        return {"ok": True, "path": str(path), "bytes": path.stat().st_size}
    finally:
        os.close(fd)
        lock.unlink(missing_ok=True)


def _acquire_lock(lock: Path):
    """Lock-Datei anlegen (O_EXCL); stale Locks (abgebrochener Prozess) werden ersetzt."""
    for _ in range(2):
        try:
            return os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            try:
                if time.time() - lock.stat().st_mtime > LOCK_STALE_S:
                    lock.unlink(missing_ok=True)  # abgebrochener Schreiber -> freigeben
                    continue
            except OSError:  # pragma: no cover - Lock zwischenzeitlich gelöscht
                continue
            return None
    return None  # pragma: no cover - nur bei Dauerblockade


def load(path):
    """Snapshot lesen; bei Schreibabbruch (nur tmp vorhanden) wird wiederhergestellt.

    Rückgabe: State-Dict oder None (Cold-Start). StateError bei korruptem Zustand
    ohne Wiederherstellungsmöglichkeit.
    """
    path = Path(path)
    tmp = Path(str(path) + ".tmp")
    if not path.exists():
        if tmp.exists():
            return _parse(tmp, recover_to=path)  # Wiederherstellung nach Abbruch
        return None
    try:
        return _parse(path)
    except StateError:
        if tmp.exists():
            return _parse(tmp, recover_to=path)  # Abbruch-Recovery: tmp ist heil
        raise


def _parse(path: Path, recover_to: Optional[Path] = None) -> dict:
    try:
        state = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise StateError(f"State korrupt und keine Wiederherstellung möglich: {exc}") from exc
    validate(state)
    if recover_to is not None:
        save(state, recover_to)  # wiederhergestellten Zustand festhalten
    return state


# --------------------------------------------------------------- Rekonstruktion
def reconstruct(state: dict) -> dict:
    """Live-Objekte aus dem Snapshot fortsetzen (WM · Graph · HMM · Drift-Checkpoint)."""
    validate(state)
    wm = None
    if state.get("wm") is not None:
        w = state["wm"]
        wm = lru_cache.WorkingMemory(capacity=w.get("capacity", 15))
        wm.items.update({key: dict(meta) for key, meta in w.get("items", {}).items()})
        wm.tick = w.get("tick", 0)
        wm.evicted = list(w.get("evicted", []))
        wm.log = list(w.get("log", []))
    graph = None
    if state.get("graph") is not None:
        g = state["graph"]
        graph = ingestion_hook.MemoryGraph()
        graph.nodes = {name: dict(meta) for name, meta in g.get("nodes", {}).items()}
        graph.edges = {(s, p, o): float(w_) for s, p, o, w_ in g.get("edges", [])}
    hmm = None
    if state.get("hmm") is not None:
        import numpy as np

        h = state["hmm"]
        hmm = reflective_agent.HMMInertia(states=h.get("states", 4), lr=h.get("lr", 0.05), beta=h.get("beta", 4.0))
        hmm.P = np.array(h["P"], dtype=float)
    drift_reference = (state.get("drift") or {}).get("reference")
    return {"wm": wm, "graph": graph, "hmm": hmm, "drift_reference": drift_reference}
