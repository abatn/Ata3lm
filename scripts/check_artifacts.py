#!/usr/bin/env python3
"""
Prüft alle Artefakte im Repo auf syntaktische Gültigkeit.

Geprüft werden:
  - alle *.json via json.load
  - alle *.yml/*.yaml via yaml.safe_load (falls PyYAML installiert)
  - pyproject.toml via tomllib (Fallback tomli)
  - alle *.dot via `dot -Tsvg` (nur wenn graphviz im PATH)

Exit-Code: 0 = OK, 1 = mindestens ein Fehler.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SKIP_DIRS = {".venv", ".git", "__pycache__"}

try:
    import yaml
except ModuleNotFoundError:
    yaml = None


def iter_files(root: Path, suffixes: set) -> list:
    """Sammelt alle Dateien mit den gegebenen Endungen unter root."""
    found = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [name for name in dirnames if name not in SKIP_DIRS]
        for name in filenames:
            path = Path(dirpath) / name
            if path.suffix.lower() in suffixes:
                found.append(path)
    return sorted(found)


def toml_module():
    """Liefert tomllib bzw. tomli oder None, wenn keines verfügbar ist."""
    try:
        import tomllib

        return tomllib
    except ModuleNotFoundError:
        try:
            import tomli

            return tomli
        except ModuleNotFoundError:
            return None


def check_json(path: Path) -> str:
    """Parst eine JSON-Datei und liefert eine Fehlermeldung oder einen Leerstring."""
    try:
        with path.open(encoding="utf-8") as handle:
            json.load(handle)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        return str(exc)
    return ""


def check_yaml(path: Path) -> str:
    """Parst eine YAML-Datei und liefert eine Fehlermeldung oder einen Leerstring."""
    try:
        with path.open(encoding="utf-8") as handle:
            yaml.safe_load(handle)
    except (OSError, UnicodeDecodeError, yaml.YAMLError) as exc:
        return str(exc)
    return ""


def check_toml(path: Path, module) -> str:
    """Parst eine TOML-Datei und liefert eine Fehlermeldung oder einen Leerstring."""
    try:
        with path.open("rb") as handle:
            module.load(handle)
    except (OSError, module.TOMLDecodeError) as exc:
        return str(exc)
    return ""


def check_dot(path: Path, dot_binary: str) -> str:
    """Prüft eine DOT-Datei via `dot -Tsvg` und liefert eine Fehlermeldung oder einen Leerstring."""
    with tempfile.TemporaryDirectory() as tmp:
        output = Path(tmp) / (path.stem + ".svg")
        result = subprocess.run(
            [dot_binary, "-Tsvg", str(path), "-o", str(output)],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            message = result.stderr.strip() or result.stdout.strip()
            return message or "dot -Tsvg fehlgeschlagen"
    return ""


def main() -> int:
    """Führt alle Artefakt-Checks aus und gibt eine Zusammenfassung aus."""
    root = Path(__file__).resolve().parent.parent
    errors = []
    counts = {"json": 0, "yaml": 0, "toml": 0, "dot": 0}

    for path in iter_files(root, {".json"}):
        counts["json"] += 1
        message = check_json(path)
        if message:
            errors.append((path, message))

    if yaml is None:
        print("PyYAML nicht installiert – YAML-Check übersprungen.")
    else:
        for path in iter_files(root, {".yml", ".yaml"}):
            counts["yaml"] += 1
            message = check_yaml(path)
            if message:
                errors.append((path, message))

    module = toml_module()
    if module is None:
        print("tomllib/tomli nicht installiert – TOML-Check übersprungen.")
    else:
        pyproject = root / "pyproject.toml"
        if pyproject.is_file():
            counts["toml"] += 1
            message = check_toml(pyproject, module)
            if message:
                errors.append((pyproject, message))

    dot_binary = shutil.which("dot")
    dot_files = iter_files(root, {".dot"})
    if dot_binary is None:
        print(f"graphviz 'dot' nicht im PATH – DOT-Check übersprungen ({len(dot_files)} Datei(en)).")
    else:
        for path in dot_files:
            counts["dot"] += 1
            message = check_dot(path, dot_binary)
            if message:
                errors.append((path, message))

    for path, message in errors:
        print(f"FEHLER: {path.relative_to(root)}: {message}")

    print(
        "Geprüft: "
        f"{counts['json']} JSON, {counts['yaml']} YAML, {counts['toml']} TOML, {counts['dot']} DOT "
        f"– {len(errors)} Fehler."
    )
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
