#!/usr/bin/env python3
"""
CI-Drift: prüft den Änderungsanteil an AGENTS.md und data/memory/tier1-base/.

Vergleicht BASE mit dem Arbeitsbaum (git diff --numstat), berechnet je Datei
Δ = geänderte Zeilen / Gesamtzeilen und vergleicht mit dem Bound (10 %).

K5 (Auftrag, B8): **Archiv-/Versionsdateien** (`versions/**`, `*.superseded-*`)
zählen NICHT als Drift – regelkonforme Versionierung (§9.1b) muss Exit 0 liefern.
Stattdessen gilt ein eigener **Integritäts-Check** (Bericht §6, Korrektur 3):
historische Archive dürfen nicht geändert, gelöscht oder umbenannt werden
(erkennbar an `git diff --name-status` != `A` ⇒ FAIL). Nur NEU-Anlagen sind ok.

Exit-Code: 0 = innerhalb des Bounds + Archiv-Integrität ok, 1 = sonst.
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

TARGETS = ["AGENTS.md", "data/memory/tier1-base"]
DRIFT_BOUND = 0.10
# Unveränderliches Archiv = Snapshot-Verzeichnis `versions/vN/` oder `*.superseded-*`.
# NICHT `versions/README.md` (das ist der Versionen-Index und wird pro vN ergänzt).
ARCHIVE_RE = re.compile(r"/versions/v\d+/")


def is_archive(path: str) -> bool:
    """Unveränderliches Archiv: `versions/vN/**` oder `*.superseded-*` (nicht README)."""
    normalized = "/" + (path or "").replace("\\", "/").lstrip("/")
    return ".superseded-" in normalized or bool(ARCHIVE_RE.search(normalized))


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


def numstat(root: Path):
    """Liefert (Pfad, added, deleted) je geänderter Datei oder None bei Fehler.

    Basis: `CI_DRIFT_BASE` (Default `HEAD`). In CI wird `HEAD~1` gesetzt, damit der
    **gepushte Commit** geprüft wird (Arbeitsbaum ↔ HEAD wäre in CI immer sauber).
    """
    base = os.environ.get("CI_DRIFT_BASE", "HEAD")
    result = git("diff", "--numstat", base, "--", *TARGETS)
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


def name_status(root: Path):
    """Liefert (Status-Buchstabe, Pfad) je geänderter Datei oder None bei Fehler.

    `A` = neu (auch Archive ok) · `M`/`D`/`R` = geändert/gelöscht/umbenannt
    (bei Renames: alter Pfad als `R`, neuer Pfad als `A`).
    """
    base = os.environ.get("CI_DRIFT_BASE", "HEAD")
    result = git("diff", "--name-status", base, "--", *TARGETS)
    if result.returncode != 0:
        print(f"FAIL: git diff fehlgeschlagen: {result.stderr.strip()}")
        return None
    entries = []
    for line in result.stdout.splitlines():
        parts = line.split("\t")
        if len(parts) == 2:
            entries.append((parts[0][:1], parts[1]))
        elif len(parts) == 3:  # Rename: alter Pfad = Manipulation, neuer Pfad = Anlage
            entries.append((parts[0][:1], parts[1]))
            entries.append(("A", parts[2]))
    return entries


def main() -> int:
    """Prüft Archiv-Integrität (K5) und den Drift je Inhalts-Datei gegen den Bound."""
    root = repo_root()
    entries = numstat(root)
    if entries is None:
        return 1
    statuses = name_status(root)
    if statuses is None:
        return 1

    failed = False

    # 1) K5: Archiv-Integrität – historische Archive sind unveränderlich (Change-Only)
    manipulated = [(st, path) for st, path in statuses if is_archive(path) and st != "A"]
    for st, path in manipulated:
        print(f"FAIL: Archiv manipuliert ({st}): {path}")
        failed = True
    if not manipulated:
        print("OK: Archiv-Integrität – keine Änderung/Löschung/Umbenennung historischer Archive.")

    # 2) Drift-Bound nur für Inhalts-Dateien (B8: regelkonforme Versionierung ist kein Drift)
    content = [e for e in entries if not is_archive(e[0])]
    for path, added, deleted in (e for e in entries if is_archive(e[0])):
        print(f"OK: Archiv ergänzt (§9.1b/§10.7): {path} (+{added}/-{deleted}) – zählt nicht als Drift")
    if not content:
        print("OK: Keine Inhalt-Änderungen an AGENTS.md / tier1-base.")
        return 1 if failed else 0

    total_changed = 0
    total_lines = 0
    for path, added, deleted in content:
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
