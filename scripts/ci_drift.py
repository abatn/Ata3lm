#!/usr/bin/env python3
"""
CI-Drift: prüft den Änderungsanteil an AGENTS.md und data/memory/tier1-base/.

Vergleicht HEAD mit dem Arbeitsbaum (git diff --numstat), berechnet je Datei
Δ = geänderte Zeilen / Gesamtzeilen und vergleicht mit dem Bound (10 %).

Exit-Code: 0 = innerhalb des Bounds, 1 = Bound überschritten.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

TARGETS = ["AGENTS.md", "data/memory/tier1-base"]
DRIFT_BOUND = 0.10


def git(*args: str) -> subprocess.CompletedProcess:
    """Führt einen Git-Befehl aus und liefert das Ergebnis zurück."""
    return subprocess.run(["git", *args], capture_output=True, text=True, check=False)


def repo_root() -> Path:
    """Ermittelt die Wurzel des Git-Repos (Fallback: aktuelles Verzeichnis)."""
    result = git("rev-parse", "--show-toplevel")
    if result.returncode != 0:
        return Path.cwd()
    return Path(result.stdout.strip())


def count_lines(path: Path) -> int:
    """Zählt die Zeilen einer Datei (0, wenn sie fehlt oder unlesbar ist)."""
    try:
        with path.open(encoding="utf-8") as handle:
            return sum(1 for _ in handle)
    except (OSError, UnicodeDecodeError):
        return 0


def numstat(root: Path) -> list:
    """Liefert (Pfad, added, deleted) je geänderter Datei oder None bei Fehler."""
    result = git("diff", "--numstat", "HEAD", "--", *TARGETS)
    if result.returncode != 0:
        print(f"FAIL: git diff fehlgeschlagen: {result.stderr.strip()}")
        return None
    entries = []
    for line in result.stdout.splitlines():
        parts = line.split("\t")
        if len(parts) != 3:
            continue
        added, deleted, path = parts
        if added == "-" or deleted == "-":
            continue
        entries.append((path, int(added), int(deleted)))
    return entries


def main() -> int:
    """Berechnet den Drift je Datei und prüft ihn gegen den Bound."""
    root = repo_root()
    entries = numstat(root)
    if entries is None:
        return 1
    if not entries:
        print("OK: Keine Änderungen an AGENTS.md / tier1-base.")
        return 0

    failed = False
    total_changed = 0
    total_lines = 0
    for path, added, deleted in entries:
        changed = added + deleted
        current = root / path
        lines = count_lines(current) if current.is_file() else 0
        ratio = changed / lines if lines else (1.0 if changed else 0.0)
        total_changed += changed
        total_lines += lines
        status = "FAIL" if ratio > DRIFT_BOUND else "OK"
        print(f"{status}: {path} geändert={changed} (added={added}, deleted={deleted}) gesamt={lines} Δ={ratio:.2%}")
        if ratio > DRIFT_BOUND:
            failed = True

    overall = total_changed / total_lines if total_lines else 0.0
    print(f"Gesamt: geändert={total_changed} gesamt={total_lines} Δ={overall:.2%} Bound={DRIFT_BOUND:.0%}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
