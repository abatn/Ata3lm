#!/usr/bin/env python3
"""
Scannt Text-Dateien im Repo nach typischen Secrets und API-Keys.

Gefundene Treffer werden maskiert als Datei:Zeile ausgegeben.

Exit-Code: 0 = keine Treffer, 1 = mindestens ein Treffer.
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

SKIP_DIRS = {".venv", ".git", "__pycache__"}
PATTERNS = [
    re.compile(r"nvapi-[A-Za-z0-9_\-]{20,}"),
    re.compile(r"sk-[A-Za-z0-9]{20,}"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"ghp_[A-Za-z0-9]{36}"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
]
# Kanonische Beispiel-/Doku-Keys (keine echten Secrets) – exakt erlaubt.
ALLOWLIST = [
    re.compile(r"ghp_ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"),
    re.compile(r"AKIAIOSFODNN7EXAMPLE"),
]


def iter_files(root: Path) -> list:
    """Sammelt alle Dateien unter root (ohne übersprungene Verzeichnisse)."""
    found = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [name for name in dirnames if name not in SKIP_DIRS]
        for name in filenames:
            found.append(Path(dirpath) / name)
    return sorted(found)


def mask(value: str) -> str:
    """Maskiert einen Treffer, sodass nur Randzeichen sichtbar bleiben."""
    if len(value) <= 8:
        return value[:2] + "***"
    return value[:4] + "***" + value[-2:]


def main() -> int:
    """Scannt alle Text-Dateien und gibt maskierte Treffer aus."""
    root = Path(__file__).resolve().parent.parent
    hits = []

    for path in iter_files(root):
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for line_number, line in enumerate(text.splitlines(), start=1):
            for pattern in PATTERNS:
                for match in pattern.finditer(line):
                    if any(allow.fullmatch(match.group()) for allow in ALLOWLIST):
                        continue
                    hits.append((path, line_number, mask(match.group())))

    for path, line_number, masked in hits:
        print(f"{path.relative_to(root)}:{line_number}: {masked}")

    print(f"Ergebnis: {len(hits)} Treffer.")
    return 1 if hits else 0


if __name__ == "__main__":
    sys.exit(main())
