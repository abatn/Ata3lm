#!/usr/bin/env python3
"""
Prüft relative Markdown-Links in allen *.md-Dateien des Repos auf Existenz.

Externe Links (http/https/mailto) und reine Anker (#...) werden ignoriert.
Ein Anker an einem relativen Ziel wird vor der Prüfung abgeschnitten.

Exit-Code: 0 = alle Ziele vorhanden, 1 = mindestens ein Ziel fehlt.
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

SKIP_DIRS = {".venv", ".git", "__pycache__"}
LINK_RE = re.compile(r"\]\(([^)]+)\)")
IGNORED_PREFIXES = ("http://", "https://", "mailto:", "#")


def iter_markdown(root: Path) -> list:
    """Sammelt alle *.md-Dateien unter root."""
    found = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [name for name in dirnames if name not in SKIP_DIRS]
        for name in filenames:
            if name.lower().endswith(".md"):
                found.append(Path(dirpath) / name)
    return sorted(found)


def extract_targets(text: str) -> list:
    """Extrahiert alle Link-Ziele aus ](ZIEL) und entfernt optionale Titel."""
    targets = []
    for match in LINK_RE.finditer(text):
        raw = match.group(1).strip()
        if raw.startswith("<") and raw.endswith(">"):
            target = raw[1:-1].strip()
        else:
            target = raw.split(" ", 1)[0]
        targets.append(target)
    return targets


def main() -> int:
    """Prüft alle relativen Link-Ziele und gibt fehlende aus."""
    root = Path(__file__).resolve().parent.parent
    missing = []
    checked = 0

    for md_file in iter_markdown(root):
        try:
            text = md_file.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            missing.append((md_file, f"<unlesbar: {exc}>"))
            continue
        for target in extract_targets(text):
            if not target or target.startswith(IGNORED_PREFIXES):
                continue
            path_part = target.split("#", 1)[0]
            path_part = re.sub(r":\d+(-\d+)?$", "", path_part)  # Zeilenbereiche wie datei.md:12-15
            if not path_part:
                continue
            checked += 1
            destination = (md_file.parent / path_part).resolve()
            root_relative = (root / path_part).resolve()
            if not destination.exists() and not root_relative.exists():
                missing.append((md_file, target))

    for md_file, target in missing:
        print(f"FEHLT: {md_file.relative_to(root)} -> {target}")

    print(f"Geprüft: {checked} relative Links – {len(missing)} fehlend.")
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
