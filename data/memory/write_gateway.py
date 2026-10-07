#!/usr/bin/env python3
"""
Einheitliches Write-Gateway (K2) — EIN Schreibpfad für Wissens-Writes.

Befund (Bericht §2 K2): `pipeline.route_and_store`, `fast_write_router.apply_write_action`,
`skill_interpreter`-Writes und der MCP-`write` schrieben eigenständig; Supersede/Trust/
PII/Provenienz griffen nicht überall (Audit B3/N5).

**Feste Reihenfolge (Auftrag K2, verbindlich):**
1. Mandat (§9) · 2. FWR (§10) · 3. Trust/PII (§9.2a) · 4. Poisoning (§9.2c) ·
5. Human-/Zwei-Personen-Freigabe (§9.3) · 6. Drift (§9.1c) ·
7. Supersede (§10.7) · 8. Write · 9. Shared · 10. Provenienz (K3, PROV-O).
Freigabe + Drift liegen **VOR** jeder Mutation (K2-STOPP: kein Aufrufer schreibt direkt;
die einzigen `write_text`-Stellen sind `_commit`/`supersede_entry` in diesem Modul).

Status (§6): Reihenfolge + Durchsetzung = **Auftrag** (K2). Die Schutz-Muster sind in
AGENTS.md §9/§10 belegt (MPBench/A-MemGuard §9.2c, MCP-Spec „Implementors SHOULD").
Gate-Labels: einheitlicher Labelraum `allow|ask|deny` (K6/B5, `gate_labels`).
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import time
from pathlib import Path
from typing import Optional

import approval
import gate_labels
import mandate
import provenance
import trust


class DomainRejection(Exception):
    """Fachliche Ablehnung (§9.2c/§9.3) – darf NIE durch einen lokalen Fallback geschrieben werden.

    K7/B3 (Auftrag): Ein *fachliches* `rejected` (Tri-Color-Red, blue-geschützt,
    unbekannter Trust, Poisoning) ist KEIN Transport-/SDK-Ausfall und darf den
    geschützten §11-Fallback niemals als Write umgehen.
    """


def is_domain_rejection(result: object) -> bool:
    """True nur für ein fachliches `rejected` (Tri-Color/Gate) – NICHT für Transport-/SDK-Ausfall."""
    return isinstance(result, dict) and result.get("status") == "rejected"


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", (text or "").lower()).strip("-")[:60] or "eintrag"


def _approval_sha(content: str, targets) -> str:
    """R01/A1 (Auftrag): Freigabe an **Inhalt + gesamte Zielmenge** binden (§9.3).

    Der Diff-Hash wird aus dem Inhalt UND **allen** Zielpfaden (kanonisch sortiert)
    gebildet, damit
      - eine alte, für einen anderen Inhalt/Ziel erteilte Zwei-Personen-Freigabe nicht
        wiederverwendet werden kann (Freigabe-Replay, R01) **und**
      - `also_write`-Ziele mitgebunden sind: eine für die Primärdatei erteilte Freigabe
        deckt ein zusätzliches (nicht genehmigtes) Ziel NICHT ab (A1).
    Ein einzelnes Ziel bleibt rückwärtskompatibel: ``sha256(content \\x00 target)``.
    Bindung = sha256-Inhalt-Hash aus `provenance`.
    """
    if isinstance(targets, (str, os.PathLike)):
        targets = [targets]
    parts = sorted(str(Path(t)) for t in targets)
    return provenance.content_hash(content + "\x00" + "\x00".join(parts))


def default_mandate(agent: str = "knowledge-agent") -> "mandate.Mandate":
    """System-Mandat der Gateway-Schreibpfade: `write:memory` auf `data/memory` (§9)."""
    return mandate.Mandate(
        mandate_id=f"write-gateway-{agent}",
        principal="Batnini",
        agent=agent,
        actions=frozenset({"write:memory"}),
        resources=frozenset({"data/memory"}),
        amount_limit=1.0,
        max_uses=100_000,
        valid_from=0.0,
        valid_until=1e12,
        approval_threshold=0.5,
    )


def _default_classify(question: str, fact: str, correct: str) -> dict:
    """Fester Fast-Write-Router (lazy import – kein Key beim Import nötig)."""
    import fast_write_router

    return fast_write_router.classify(question, fact, correct)


# --------------------------------------------------------------------- Gates
def _gate_mandate(mandate_obj, agent: str, now: float):
    m = mandate_obj if mandate_obj is not None else default_mandate(agent)
    dec = mandate.assess(m, action="write:memory", resource="data/memory", amount=0.0, now=now)
    return dec, gate_labels.normalize(dec["decision"])


def _gate_trust_pii(content: str):
    clean = trust.PIIFilter().minimize(content)  # §9.2a: PII vor dem Store entfernen
    return clean, ("trust", "PII entfernt" if clean != content else "keine PII")


def _gate_poisoning(origin: str, verified: bool):
    adm = trust.PoisoningGuard().admit({"source": origin, "verified": verified})  # §9.2c
    return adm["admitted"], ("poisoning", "admitted" if adm["admitted"] else "rejected"), adm["reason"]


def _gate_approval(approval_obj, approvers, subject: str, diff_sha: str):
    """§9.3 Zwei-Personen-Freigabe; Rückgabe: (state, Bindung für PROV-O).

    R01 (Auftrag): Ist eine bestehende Freigabe (`approval_obj`) an einen **anderen**
    Diff gebunden als den aktuell zu schreibenden Inhalt/Ziel (`diff_sha`), wird sie
    abgelehnt (`state="rejected"`, `replay=True`) – Freigabe-Replay-Schutz.
    """
    a = approval_obj if approval_obj is not None else approval.TwoPersonApproval(subject=subject)
    if a.diff_sha is not None and a.diff_sha != diff_sha:
        return "rejected", {
            "state": "rejected",
            "approvers": list(a.approvers),
            "diff_sha": a.diff_sha,
            "expected_diff_sha": diff_sha,
            "replay": True,
        }
    for person in approvers or []:
        a.approve(person, diff_sha=diff_sha)
    a.finalize()
    binding = {"state": a.state, "approvers": list(a.approvers), "diff_sha": a.diff_sha}
    return a.state, binding


def _gate_drift(drift, label: str):
    """§9.1c Drift-Gate VOR der Mutation. Rückgabe: (gate, step-Eintrag)."""
    if drift is None:
        return gate_labels.ALLOW, None
    d = drift.observe({label: 1.0}, step=1)  # echte Verteilung des Laufs
    return gate_labels.normalize(d["gate"]), ("drift", d["DI"])


# --------------------------------------------------- Mutation (EIN write_text-Pfad)
LOCK_STALE_S = 60.0  # Auftrag (K5): Locks älter als 60s gelten als abgebrochen


def _acquire_lock(lock: Path):
    """Lock-Datei (O_EXCL) gegen parallele Schreibkonflikte (K5); stale Locks werden ersetzt."""
    lock.parent.mkdir(parents=True, exist_ok=True)  # Zielordner ggf. vor dem Lock anlegen
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


def _archive_file(path: Path, now: float) -> Path:
    """Alten Stand archivieren (§10.7: invalidieren, NICHT löschen) – eindeutiger Name.

    N3/K5: `{stem}.superseded-{ts}-{sha1[:8]}{suffix}` + Kollisions-Recheck, damit
    zwei Updates in derselben Sekunde einander nicht überschreiben.
    """
    old = path.read_text(encoding="utf-8")
    h = hashlib.sha1(old.encode("utf-8")).hexdigest()[:8]
    archived = path.with_name(f"{path.stem}.superseded-{int(now)}-{h}{path.suffix}")
    n = 1
    while archived.exists():
        archived = path.with_name(f"{path.stem}.superseded-{int(now)}-{h}-{n}{path.suffix}")
        n += 1
    archived.write_text(old, encoding="utf-8")
    return archived


def _commit(targets, now: float, supersede_existing: bool, append: bool = False) -> dict:
    """EINZIGER Mutation-Punkt: Ziele schreiben, alten Stand archivieren (falls gefordert).

    `targets` = Liste aus (Pfad, Inhalt); erster Eintrag = Primärziel (dessen alter
    Stand archiviert und als `superseded` gemeldet wird). K5: Lock am Primärziel
    gegen parallele Schreibkonflikte – `conflict != None` ⇒ KEIN Write.

    R08/A3 (Auftrag): Mehrziel-Write **atomar/transaktional** – erst ALLE Ziele prüfen
    (z. B. kein Verzeichnis als Dateiziel), dann schreiben. Ist ein Ziel ungültig ODER
    schlägt ein Schreibvorgang (I/O-Fehler am 2. Ziel) fehl, wird der **Vorzustand per
    Rollback** wiederhergestellt: kein halb-geschriebener Zustand, keine inkonsistente
    Provenienz (`error`, `written=[]`). `append=True` hängt an (JSONL-Historie, R20)
    statt zu überschreiben.
    """
    primary = Path(targets[0][0])
    for target, _content in targets:  # R08: Vorprüfung VOR jeder Mutation
        t = Path(target)
        if t.exists() and t.is_dir():
            return {"written": [], "superseded": None, "conflict": None, "error": f"Ziel ist ein Verzeichnis: {t}"}
    lock = Path(str(primary) + ".lock")
    fd = _acquire_lock(lock)
    if fd is None:
        return {"written": [], "superseded": None, "conflict": "lock gehalten (paralleler Schreibkonflikt)"}
    backups: dict = {}  # A3: Vorzustand je Ziel (None = Datei existierte nicht)
    archived_primary = None
    try:
        for target, _content in targets:  # A3: Snapshot VOR der ersten Mutation
            t = Path(target)
            backups[str(t)] = t.read_text(encoding="utf-8") if t.exists() else None
        written: list = []
        superseded = None
        for i, (target, content) in enumerate(targets):
            target = Path(target)
            target.parent.mkdir(parents=True, exist_ok=True)
            if i == 0 and supersede_existing:
                if target.exists():
                    archived = _archive_file(target, now)
                    archived_primary = archived
                    superseded = {
                        "key": target.stem,
                        "old_found": True,
                        "archived": str(archived),
                        "at": now,
                    }
                else:
                    superseded = {"key": target.stem, "old_found": False, "archived": None, "at": now}
            if append:
                # R20: JSONL-Anhang – genau ein Event pro Zeile (Trust/PII strippt \n).
                with target.open("a", encoding="utf-8") as fh:
                    fh.write(content.rstrip("\n") + "\n")
            else:
                target.write_text(content, encoding="utf-8")
            written.append(str(target))
        return {"written": written, "superseded": superseded, "conflict": None}
    except OSError as exc:
        # A3 (Auftrag): Transaktion/Recovery – JEDES bereits geschriebene Ziel auf den
        # Vorzustand zurücksetzen (best effort), damit kein Teilzustand bleibt.
        for target, _content in targets:
            t = Path(target)
            old = backups.get(str(t))
            try:
                if old is None:
                    t.unlink(missing_ok=True)
                else:
                    t.write_text(old, encoding="utf-8")
            except OSError:  # pragma: no cover - Rollback ist best effort
                pass
        if archived_primary is not None:
            try:
                archived_primary.unlink(missing_ok=True)
            except OSError:  # pragma: no cover - Rollback ist best effort
                pass
        return {
            "written": [],
            "superseded": None,
            "conflict": None,
            "error": f"Write fehlgeschlagen – Rollback, kein Teilzustand ({exc})",
        }
    finally:
        os.close(fd)
        lock.unlink(missing_ok=True)


def supersede_entry(tier1_dir, key: str, new_fact: str, now: float) -> dict:
    """tier1-Eintrag supersedieren (§10.7) + supersede.jsonl (Evidence).

    Ersetzt `fast_write_router._supersede`; K5: monotone Namen mit Inhalts-Hash +
    Kollisions-Recheck + Lock (parallele Schreibkonflikte ⇒ `ok: False`, kein Write).
    A3 (Auftrag): transaktional – scheitert das Schreiben/Protokollieren, wird der alte
    Stand per Rollback wiederhergestellt (kein halb-supersedierter Eintrag).
    """
    tier1_dir = Path(tier1_dir)
    tier1_dir.mkdir(parents=True, exist_ok=True)
    old_file = tier1_dir / f"{key}.md"
    lock = Path(str(old_file) + ".lock")
    fd = _acquire_lock(lock)
    if fd is None:
        return {
            "key": key,
            "old_found": False,
            "archived": None,
            "log": None,
            "ok": False,
            "reason": "lock gehalten (paralleler Schreibkonflikt)",
        }
    try:
        old_found = old_file.exists()
        old_text = old_file.read_text(encoding="utf-8") if old_found else None
        archived = _archive_file(old_file, now) if old_found else None
        try:
            old_file.write_text(new_fact, encoding="utf-8")
            log = tier1_dir / "supersede.jsonl"
            rec = {"key": key, "archived": str(archived) if archived else None, "new": new_fact, "at": now}
            with log.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
        except OSError as exc:
            # A3: Rollback – alten Eintrag (bzw. dessen Abwesenheit) + Archiv zurücksetzen.
            try:
                if old_found:
                    old_file.write_text(old_text, encoding="utf-8")
                else:
                    old_file.unlink(missing_ok=True)
                if archived is not None:
                    archived.unlink(missing_ok=True)
            except OSError:  # pragma: no cover - Rollback ist best effort
                pass
            return {
                "key": key,
                "old_found": old_found,
                "archived": None,
                "log": None,
                "ok": False,
                "reason": f"tier1-Write fehlgeschlagen – Rollback, kein Teilzustand ({exc})",
            }
        return {
            "key": key,
            "old_found": old_found,
            "archived": str(archived) if archived else None,
            "log": str(log),
            "ok": True,
        }
    finally:
        os.close(fd)
        lock.unlink(missing_ok=True)


# --------------------------------------------------------------- Öffentliche API
def store_file(
    *,
    target: Path,
    content: str,
    mandate_obj=None,
    now: float = 0.0,
    activity: str = "write",
    agent: str = "knowledge-agent",
    origin: str = "user",
    verified: bool = True,
    drift=None,
    drift_label: Optional[str] = None,
    require_approval: bool = False,
    approval_obj=None,
    approvers=None,
    approval_subject: str = "",
    supersede: bool = True,
    also_write=None,
    shared_tier=None,
    shared_key: Optional[str] = None,
    provenance_log=None,
    domain_rejected: bool = False,
    append: bool = False,
) -> dict:
    """EIN Schreibpfad (K2) für einen direkten Datei-Write mit voller Gate-Kette.

    Reihenfolge: Mandat → Trust/PII → Poisoning → Freigabe (§9.3) → Drift (§9.1c)
    → Supersede/Write → Shared → Provenienz (K3). Freigabe + Drift VOR Mutation.

    K7/B3 (§9, §11): `domain_rejected=True` ist ein **harter Backstop** — ein
    fachliches `rejected` wird nie geschrieben, auch nicht über einen Fallback.

    **Interface-Änderung (§9-pflichtig, kenntlich gemacht):** `append=True` (R20)
    hängt an ein Ziel an (statt zu überschreiben) — für JSONL-Historien, damit
    wiederholte Events erhalten bleiben. Die Freigabe wird an den **aktuellen Inhalt +
    die gesamte Zielmenge** gebunden (`_approval_sha`, R01/A1) statt nur an Inhalt +
    Primärziel; `also_write`-Ziele sind damit mitgebunden.
    """
    steps: list = []
    if domain_rejected:
        return {
            "ok": False,
            "gate": gate_labels.DENY,
            "written": [],
            "superseded": None,
            "reason": "fachliche Ablehnung (domain rejected) – kein Write (§9.2c/§9.3)",
            "steps": steps,
        }
    dec, gate = _gate_mandate(mandate_obj, agent, now)
    steps.append(("mandate", dec["decision"]))
    if not gate_labels.is_allow(gate):
        return {"ok": False, "gate": gate, "written": [], "superseded": None, "reason": dec["reason"], "steps": steps}

    clean, tstep = _gate_trust_pii(content)
    steps.append(tstep)
    ok, pstep, preason = _gate_poisoning(origin, verified)
    steps.append(pstep)
    if not ok:
        return {
            "ok": False,
            "gate": gate_labels.DENY,
            "written": [],
            "superseded": None,
            "reason": f"Poisoning-Guard: {preason}",
            "steps": steps,
        }

    target = Path(target)
    # A1 (Auftrag): Zielmenge VOR der Freigabe festlegen und die Freigabe an ALLE Ziele
    # binden (Primärziel + `also_write`), damit kein nicht-genehmigtes Ziel mitgeschrieben wird.
    targets = [(target, clean)] + [(Path(p), clean) for p in (also_write or [])]
    binding = None
    if require_approval:
        state, binding = _gate_approval(
            approval_obj, approvers, approval_subject or str(target),
            _approval_sha(clean, [t for t, _ in targets]),
        )
        steps.append(("approval", state))
        if state != "approved":
            replay = bool((binding or {}).get("replay"))
            return {
                "ok": False,
                "gate": gate_labels.DENY if replay else gate_labels.ASK,
                "approval": state,
                "written": [],
                "superseded": None,
                "reason": "Freigabe-Replay: diff_sha passt nicht zu Inhalt/Ziel (§9.3)"
                if replay
                else "Zwei-Personen-Freigabe nicht approved (§9.3)",
                "steps": steps,
            }

    gate, dstep = _gate_drift(drift, drift_label or activity)
    if dstep is not None:
        steps.append(dstep)
    if not gate_labels.is_allow(gate):
        return {
            "ok": False,
            "gate": gate,
            "written": [],
            "superseded": None,
            "reason": f"Drift-Gate {gate}: kein Write vor Freigabe (§9.1c)",
            "steps": steps,
        }

    # K3-STOPP VOR der Mutation: Record mit Inhalt-Hash + Freigabe-Bindung bauen.
    old_content = target.read_text(encoding="utf-8") if (supersede and target.exists()) else None
    try:
        record = provenance.build_record(
            fact=clean,
            activity=activity,
            agent=agent,
            source=origin,
            now=now,
            revision_of=f"entity:{provenance.content_hash(old_content)[:16]}" if old_content is not None else None,
            invalidated_at=now if old_content is not None else None,
            approval=binding,
            require_approval=require_approval,
        )
    except provenance.ProvenanceError as exc:
        return {
            "ok": False,
            "gate": gate_labels.DENY,
            "written": [],
            "superseded": None,
            "reason": f"Provenienz (K3): {exc}",
            "steps": steps,
        }

    targets = [(target, clean)] + [(Path(p), clean) for p in (also_write or [])]
    res = _commit(targets, now, supersede_existing=supersede, append=append)
    if res.get("conflict") or res.get("error"):
        return {
            "ok": False,
            "gate": gate_labels.ASK,
            "written": [],
            "superseded": None,
            "reason": res.get("conflict") or res.get("error"),
            "steps": steps,
        }
    steps.append(("write", activity))

    shared_res = None
    if shared_tier is not None:
        shared_res = shared_tier.write(agent, shared_key or target.stem, clean)  # Shared-Schritt
        steps.append(("shared", shared_res.get("ok")))

    log = Path(provenance_log) if provenance_log is not None else target.parent / "provenance.jsonl"
    provenance.append_record(log, record)  # dauerhaftes Provenienz-Protokoll (K3)
    steps.append(("provenance", record["entity"]["sha256"][:12]))
    return {
        "ok": True,
        "gate": gate,
        "written": res["written"],
        "superseded": res["superseded"],
        "provenance": record,
        "provenance_log": str(log),
        "shared": shared_res,
        "steps": steps,
    }


def store(
    *,
    question: str,
    fact: str,
    correct: str = "",
    classify_fn=None,
    mandate_obj=None,
    now: float = 0.0,
    structured_dir,
    tier3_dir,
    tier1_dir=None,
    history_dir=None,
    drift=None,
    self_update: bool = False,
    approval_obj=None,
    approvers=None,
    supersede_fn=None,
    agent: str = "knowledge-agent",
    origin: str = "tool:verified",
    verified: bool = True,
    shared_tier=None,
    provenance_log=None,
) -> dict:
    """Wissens-Write über die volle K2-Kette (inkl. FWR-Entscheidung, §10).

    Layout (AGENTS.md §10.7): non-write → nur Historie · write-new → `structured/`
    + `tier3/` · write-update → `structured/` (+Archiv), `tier3/` falls vorhanden,
    optionaler tier1-Supersede (§10.7).

    **Interface-Änderung (§9-pflichtig, kenntlich gemacht):** Die Zwei-Personen-
    Freigabe wird an **Inhalt + gesamte Zielmenge** gebunden (`_approval_sha`, R01/A1).
    Die non-write-Historie wird **angehängt** (JSONL, R20) statt überschrieben. Ein
    tier1-Supersede-Konflikt führt zu einem **Teilfehler** (R09: `ok=False`,
    `partial=True`) — nicht mehr zu `ok=True`.
    """
    steps: list = []
    dec, gate = _gate_mandate(mandate_obj, agent, now)
    steps.append(("mandate", dec["decision"]))
    if not gate_labels.is_allow(gate):
        return {"ok": False, "gate": gate, "reason": dec["reason"], "steps": steps}

    router = (classify_fn or _default_classify)(question, fact, correct)
    cls = router["class"]
    steps.append(("fwr", cls))
    name = f"{_slug(question)}.md"
    structured_file = Path(structured_dir) / name

    if cls == "non-write":
        out = {
            "ok": True,
            "action": "non-write",
            "gate": gate_labels.ALLOW,
            "written": [],
            "superseded": None,
            "steps": steps,
        }
        if history_dir is not None:
            hist = Path(history_dir) / f"{_slug(question)}.non-write.jsonl"
            hist_content = json.dumps({"question": question, "class": cls, "at": now}, ensure_ascii=False) + "\n"
            hres = store_file(
                target=hist,
                content=hist_content,
                mandate_obj=mandate_obj,
                now=now,
                activity="non-write-history",
                agent=agent,
                origin=origin,
                verified=verified,
                supersede=False,
                provenance_log=provenance_log,
                append=True,  # R20: wiederholte non-write-Events erhalten (JSONL append)
            )
            out["written"] = hres.get("written", [])
            out["ok"] = hres["ok"]
            out["reason"] = hres.get("reason")
        return out

    if cls not in ("write-new", "write-update"):
        # §10.4: Router unsicher (uncertain) -> Human-Gate, KEIN Write
        return {
            "ok": False,
            "action": cls,
            "gate": gate_labels.ASK,
            "reason": "Router uncertain -> Human-Gate (§10.4)",
            "written": [],
            "steps": steps,
        }

    router_gate = gate_labels.normalize(router.get("gate", gate_labels.ALLOW))
    freigegebenes_self_update = self_update and router_gate == gate_labels.ASK
    if not gate_labels.is_allow(router_gate) and not freigegebenes_self_update:
        # §10.4: ask -> Freigabe erforderlich; `deny` wird nie umgangen (K6/B5).
        return {
            "ok": False,
            "action": cls,
            "gate": router_gate,
            "reason": f"Router-Gate {router_gate}: Freigabe erforderlich (§10.4)",
            "written": [],
            "steps": steps,
        }

    clean, tstep = _gate_trust_pii(fact)
    steps.append(tstep)
    ok, pstep, preason = _gate_poisoning(origin, verified)
    steps.append(pstep)
    if not ok:
        return {
            "ok": False,
            "action": cls,
            "gate": gate_labels.DENY,
            "reason": f"Poisoning-Guard: {preason}",
            "written": [],
            "steps": steps,
        }

    # A1 (Auftrag): Zielmenge VOR der Freigabe festlegen und die Freigabe an ALLE Ziele
    # binden (structured + ggf. tier3), damit kein nicht-genehmigtes Ziel mitgeschrieben wird.
    tier3_file = Path(tier3_dir) / name
    targets = [(structured_file, clean)]
    if cls == "write-new":
        targets.append((tier3_file, clean))  # §10.7: structured + tier3
    elif tier3_file.exists():
        targets.append((tier3_file, clean))  # N4: nur existierende Arbeitskopie aktualisieren

    binding = None
    if self_update:
        state, binding = _gate_approval(
            approval_obj, approvers, question, _approval_sha(clean, [t for t, _ in targets])
        )
        steps.append(("approval", state))
        if state != "approved":
            replay = bool((binding or {}).get("replay"))
            return {
                "ok": False,
                "action": cls,
                "gate": gate_labels.DENY if replay else gate_labels.ASK,
                "approval": state,
                "written": [],
                "reason": "Freigabe-Replay: diff_sha passt nicht zu Inhalt/Ziel (§9.3)"
                if replay
                else "Zwei-Personen-Freigabe nicht approved (§9.3)",
                "steps": steps,
            }

    gate, dstep = _gate_drift(drift, cls)
    if dstep is not None:
        steps.append(dstep)
    if not gate_labels.is_allow(gate):
        return {
            "ok": False,
            "action": cls,
            "gate": gate,
            "reason": f"Drift-Gate {gate}: kein Write vor Freigabe (§9.1c)",
            "written": [],
            "steps": steps,
        }

    old_content = structured_file.read_text(encoding="utf-8") if structured_file.exists() else None
    try:
        record = provenance.build_record(
            fact=clean,
            activity=cls,
            agent=agent,
            source=origin,
            now=now,
            revision_of=f"entity:{provenance.content_hash(old_content)[:16]}" if old_content is not None else None,
            invalidated_at=now if old_content is not None else None,
            approval=binding,
            require_approval=self_update,
        )
    except provenance.ProvenanceError as exc:
        return {
            "ok": False,
            "action": cls,
            "gate": gate_labels.DENY,
            "reason": f"Provenienz (K3): {exc}",
            "written": [],
            "steps": steps,
        }

    res = _commit(targets, now, supersede_existing=(cls == "write-update"))
    if res.get("conflict") or res.get("error"):
        return {
            "ok": False,
            "action": cls,
            "gate": gate_labels.ASK,
            "written": [],
            "reason": res.get("conflict") or res.get("error"),
            "steps": steps,
        }
    steps.append(("write", cls))
    superseded_structured = res["superseded"] if cls == "write-update" else None

    superseded_tier1 = None
    if cls == "write-update" and tier1_dir is not None:
        # §10.7: alten tier1-Eintrag supersedieren (invalidieren, NICHT löschen)
        superseded_tier1 = (supersede_fn or supersede_entry)(tier1_dir, _slug(question), clean, now)
        steps.append(("supersede", superseded_tier1.get("old_found")))
        if not superseded_tier1.get("ok", True):
            # R09 (Auftrag): tier1-Konflikt ⇒ Gesamt-Update unvollständig, NICHT ok=True.
            log = Path(provenance_log) if provenance_log is not None else Path(tier3_dir) / "provenance.jsonl"
            provenance.append_record(log, record)  # K3: der geschriebene Teil bleibt belegt
            steps.append(("provenance", record["entity"]["sha256"][:12]))
            return {
                "ok": False,
                "action": cls,
                "gate": gate_labels.ASK,
                "partial": True,
                "written": res["written"],
                "superseded": superseded_structured,
                "superseded_structured": superseded_structured,
                "superseded_tier1": superseded_tier1,
                "provenance": record,
                "provenance_log": str(log),
                "reason": f"tier1-Konflikt: Update unvollständig ({superseded_tier1.get('reason')})",
                "steps": steps,
            }

    shared_res = None
    if shared_tier is not None:
        shared_res = shared_tier.write(agent, _slug(question), clean)  # Shared-Schritt
        steps.append(("shared", shared_res.get("ok")))

    log = Path(provenance_log) if provenance_log is not None else Path(tier3_dir) / "provenance.jsonl"
    provenance.append_record(log, record)
    steps.append(("provenance", record["entity"]["sha256"][:12]))
    return {
        "ok": True,
        "action": cls,
        "gate": gate,
        "written": res["written"],
        "superseded": superseded_structured,
        "superseded_structured": superseded_structured,
        "superseded_tier1": superseded_tier1,
        "provenance": record,
        "provenance_log": str(log),
        "shared": shared_res,
        "steps": steps,
    }
