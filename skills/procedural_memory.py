#!/usr/bin/env python3
"""
Procedural Memory (L4) – versionierte, auditierbare Skill-Verwaltung.

Quellen (verifiziert 2026-10-01, HTTP 200):
  - Mem^p (arXiv:2508.06433, ACL Findings 2026): "treats procedural memory as a
    first-class optimization object"; Build/Retrieval/**Update**; dynamische
    Update-Strategien (addition, validation filtering, reflection, **dynamic
    discarding / deprecate**).
  - AFTER (arXiv:2606.23127): persistente Skill-Files als "first-class artifact
    outside the base prompt"; Skill-Refinement + Transfer.
  - ProcMEM (arXiv:2602.01869): Skill-MDP; **PPO-style trust-region verification
    (PPO Gate)** vor Aufnahme in die Prozedur-Memory; score-based pruning.
  - Graph-based Agent Memory (arXiv:2602.05665): "Procedural Memory: Encodes
    skills, routines, and immutable rules."

Lab-Prinzip: Mechanik = aus den Quellen; die konkrete Versionierung/Audit-
Mechanik ist Projekt-Vorgabe (Auftrag). Kein Skill wird ohne `approved` geändert
(Human-Gate, vgl. AGENTS.md §9).
"""
from __future__ import annotations

import difflib
import hashlib
import shutil
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path("/home/opc/knowledge-agent")
SKILLS = ROOT / "skills"
AUDIT = SKILLS / "AUDIT.md"
DIFF_DIR = SKILLS / "audit-diffs"
RESERVED = "versions"          # reservierter Ordnername für Snapshots


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]


def active_skills() -> list[Path]:
    """Aktive SKILL.md (Version-Snapshots unter `versions/` ausgeschlossen)."""
    return sorted(p for p in SKILLS.rglob("SKILL.md") if RESERVED not in p.parts)


def _ensure_audit() -> None:
    if not AUDIT.exists():
        AUDIT.write_text(
            "# Skills – Audit-Log (Procedural Memory L4)\n\n"
            "> Jede Änderung an einem Skill: Aktion + Begründung (+ Diff-Datei).\n"
            "> Quellen: Mem^p (arXiv:2508.06433), AFTER (arXiv:2606.23127), "
            "ProcMEM (arXiv:2602.01869).\n\n"
            "| Zeit (UTC) | Skill | Aktion | Begründung |\n|---|---|---|---|\n",
            encoding="utf-8")


def _rel(skill_file: Path) -> str:
    try:
        return str(skill_file.relative_to(ROOT))
    except ValueError:
        return str(skill_file)


def audit(skill_file: Path, action: str, reason: str, diff: str = "") -> None:
    _ensure_audit()
    rel = _rel(skill_file)
    with open(AUDIT, "a", encoding="utf-8") as f:
        f.write(f"| {_now()} | `{rel}` | {action} | {reason} |\n")
    if diff:
        DIFF_DIR.mkdir(parents=True, exist_ok=True)
        (DIFF_DIR / f"{_sha(str(skill_file))}-{_sha(_now())}.diff").write_text(diff, encoding="utf-8")


def snapshot(skill_file: Path, version: str, reason: str) -> Path:
    """Legt eine versionierte Kopie an: skills/<name>/versions/<version>/SKILL.md."""
    vdir = skill_file.parent / "versions" / version
    vdir.mkdir(parents=True, exist_ok=True)
    dst = vdir / "SKILL.md"
    if dst.exists():
        return dst                              # Versionen sind UNVERÄNDERLICH (kein Overwrite)
    shutil.copy2(skill_file, dst)
    audit(skill_file, action=f"snapshot {version}", reason=reason)
    return dst


def propose_update(skill_file: Path, new_text: str, reason: str, approved: bool) -> dict:
    """Selektives Update: NUR mit `approved` angewandt (Human-Gate)."""
    old = skill_file.read_text(encoding="utf-8")
    diff = "".join(difflib.unified_diff(old.splitlines(keepends=True),
                                        new_text.splitlines(keepends=True),
                                        fromfile=str(skill_file), tofile=f"{skill_file} (neu)"))
    if not approved:
        audit(skill_file, "proposal (pending – NICHT angewandt)", reason, diff)
        return {"applied": False, "status": "pending", "reason": "kein approved (Human-Gate)"}
    vdir = skill_file.parent / "versions"
    existing = sorted(d.name for d in vdir.glob("v*")) if vdir.exists() else []
    nxt = f"v{len(existing) + 1}"
    skill_file.write_text(new_text, encoding="utf-8")
    snapshot(skill_file, nxt, reason=f"Update auf {nxt}")   # Version N = Zustand N
    audit(skill_file, f"update applied ({nxt})", reason, diff)
    return {"applied": True, "status": "approved", "version": nxt}


def rollback(skill_file: Path, version: str, reason: str) -> dict:
    """Stellt eine frühere Skill-Version wieder her (versions/<version>/SKILL.md).

    Quelle: Memory Survey (temporal versioning); TEA-Protokoll (arXiv:2506.12508:
    version manager, „access to historical records for analysis and rollback").
    Der aktuelle Stand wird vorher als neue Version gesichert (kein Verlust).
    """
    src = skill_file.parent / "versions" / version / "SKILL.md"
    if not src.exists():
        return {"ok": False, "reason": f"Version '{version}' nicht gefunden"}
    vdir = skill_file.parent / "versions"
    existing = sorted(d.name for d in vdir.glob("v*")) if vdir.exists() else []
    nxt = f"v{len(existing) + 1}"
    snapshot(skill_file, nxt, reason=f"Vorher-Stand vor Rollback auf {version}")
    skill_file.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
    audit(skill_file, f"rollback -> {version}", reason)
    return {"ok": True, "restored": version, "saved_current_as": nxt}


def _demo() -> None:
    global AUDIT, DIFF_DIR
    print("=== [1] Versionierung: v1-Snapshot aller aktiven Skills ===")
    skills = active_skills()
    for s in skills:
        dst = snapshot(s, "v1", reason="Baseline (Procedural Memory L4 eingeführt)")
        print(f"  {s.relative_to(ROOT)} -> {dst.relative_to(ROOT)}")
    print(f"  Snapshots: {len(skills)}")

    print("\n=== [2] Audit-Log ===")
    print(f"  {AUDIT.relative_to(ROOT)} geschrieben.")

    print("\n=== [3] Selektives Update (Human-Gate) ===")
    tmp = Path("/tmp/opencode/pm_demo"); tmp.mkdir(parents=True, exist_ok=True)
    AUDIT = tmp / "AUDIT.md"; DIFF_DIR = tmp / "diffs"   # Demo schreibt NICHT ins Repo-Audit
    demo_skill = tmp / "SKILL.md"
    demo_skill.write_text("---\nname: demo\ndescription: \"Demo-Skill.\"\n---\n\nAlt.\n", encoding="utf-8")
    snapshot(demo_skill, "v1", reason="Baseline (Demo)")     # v1 = Ausgangszustand
    new_text = "---\nname: demo\ndescription: \"Demo-Skill.\"\n---\n\nNeu.\n"
    r1 = propose_update(demo_skill, new_text, reason="Verbesserung", approved=False)
    print(f"  ohne approved -> applied={r1['applied']} status={r1['status']} ({r1['reason']})")
    print(f"  Inhalt unverändert? {demo_skill.read_text(encoding='utf-8').strip().endswith('Alt.')}")
    r2 = propose_update(demo_skill, new_text, reason="Verbesserung", approved=True)
    print(f"  mit approved  -> applied={r2['applied']} status={r2['status']} version={r2['version']}")
    print(f"  Inhalt geändert?  {demo_skill.read_text(encoding='utf-8').strip().endswith('Neu.')}")

    print("\n=== [4] Rollback (versions/vN) ===")
    rb = rollback(demo_skill, "v1", reason="Rollback-Test")
    print(f"  rollback -> {rb}")
    print(f"  Inhalt wieder v1? {demo_skill.read_text(encoding='utf-8').strip().endswith('Alt.')}")


if __name__ == "__main__":
    _demo()
