#!/usr/bin/env python3
"""
Slow Consolidation (Write-Back) – Vorarbeit für Θ→Θ′ (AGENTS.md §10.3).

Quelle (Belegt, im Gesetz): **Dual-Layer Agentic Memory with Fast Write Routing
and Slow Consolidation**, arXiv:2608.22215 §3.4 (Write-Back / Slow Consolidation):
  - Periodisches **Supervised Fine-Tuning (SFT)** von *write-new*/*write-update*-
    Fakten aus dem externen Memory (E) in das parametrische Gedächtnis (Θ → Θ′).
  - **Erfolgreiche** Konsolidierung → Fakt aus dem externen Puffer **entfernen** (Flush).
  - **Fehlgeschlagen** → Fakt **bleibt** im externen Puffer.
  - Paper-Wirkung: externer Speicher nach Write-Back ~32 % (von 64,81 % Baseline).

Status (ehrliche Trennung, vgl. AGENTS.md-Kopf):
  - **Belegt (Paper):** Mechanismus Write-Back + „erfolgreich ⇒ Flush / sonst bleibt".
  - **Auftrag (Projekt):** Sammeln (`collect_pending`), Dataset-Format
    (`build_sft_dataset`), Verbuchen (`mark_consolidated`), Entfernen (`flush`)
    und der Kaggle-Stub sind an das Projekt gebunden, KEIN Paper-Claim.

**Kein Fake (Guardrail 7):** Der eigentliche Trainingsschritt Θ→Θ′ läuft **NICHT**
hier, sondern auf **Kaggle** (separater Teil). `write_back(...)` ist ein ehrlicher
Stub (`NotImplementedError`) – es wird kein Training simuliert/erfunden.

Caveat (ehrlich): Die PROV-O-Records (K3, `provenance.py`) binden den **Inhalt-Hash**
und die **Aktivität**, aber NICHT den auslösenden Prompt. `collect_pending`
rekonstruiert die SFT-Frage daher aus dem Memory-Key (= Slug des Prompts, verlustarm)
bzw. nutzt eine übergebene `questions`-Zuordnung. Die **Fakten** (assistant-content)
sind real aus dem externen Puffer gelesen.

**Interface-Änderung (§9-pflichtig, kenntlich gemacht):** Alle hier definierten
Funktionen/Signaturen (`collect_pending`, `build_sft_dataset`, `mark_consolidated`,
`flush`, `write_back`) sowie die neuen optionalen Runner-Parameter
`consolidation_state_path` sind NEU und noch NICHT menschlich freigegeben (§9).
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional

import provenance
import trust

# §10.7: nur *write-new*/*write-update* werden konsolidiert (non-write wird nie extern gehalten).
WRITE_CLASSES = ("write-new", "write-update")

# Kaggle-Stub (ehrlich): das eigentliche Θ→Θ′-Training läuft dort.
TRAIN_LOCATION = "Kaggle"


def _read_jsonl(path) -> list:
    """JSONL tolerant lesen; fehlende Datei ⇒ leere Liste (Cold-Start)."""
    p = Path(path)
    if not p.exists():
        return []
    out: list = []
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            continue  # defekte Zeile überspringen (kein Crash, kein Fake-Record)
        if isinstance(rec, dict):
            out.append(rec)
    return out


def _load_state(state_path) -> dict:
    """Konsolidierungs-Zustand lesen; fehlend/defekt ⇒ leere Liste."""
    try:
        data = json.loads(Path(state_path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"consolidated": []}
    if not isinstance(data, dict):
        return {"consolidated": []}
    keys = data.get("consolidated")
    return {"consolidated": [str(k) for k in keys] if isinstance(keys, list) else []}


def _write_state(state_path, state: dict) -> str:
    """Zustand atomar schreiben (tmp + os.replace) – kein halber Zustand (vgl. K5)."""
    p = Path(state_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_name(p.name + ".tmp")
    tmp.write_text(json.dumps(state, ensure_ascii=False, sort_keys=True, indent=2), encoding="utf-8")
    os.replace(tmp, p)
    return str(p)


def _trusted_verified(record: dict) -> bool:
    """Trusted origin UND verified (§9.2c Poisoning-Guard, MPBench/TMA-NM).

    Ein PROV-O-Record entsteht nur NACH dem Poisoning-Gate, daher gilt ein fehlendes
    `verified`-Feld als `True` (der Store hat es bereits geprüft). Die **Quelle** wird
    erneut gegen die Allowlist geprüft (origin-bound) – eine manuell gefälschte Log-
    Zeile mit untrusted Quelle wird so verworfen.
    """
    guard = trust.PoisoningGuard()
    return guard.admit({"source": record.get("source"), "verified": bool(record.get("verified", True))})["admitted"]


def _index_tier3_by_hash(tier3_dir: Path) -> dict:
    """Aktive tier3-Dateien nach Inhalt-Hash indexieren (Archiv-Stände ausgenommen)."""
    by_hash: dict = {}
    if not tier3_dir.exists():
        return by_hash
    for p in sorted(tier3_dir.glob("*.md")):
        if ".superseded-" in p.name:  # §10.7: Archiv = Historie, nicht der aktive Puffer
            continue
        try:
            text = p.read_text(encoding="utf-8")
        except OSError:  # pragma: no cover - unlesbare Datei überspringen
            continue
        by_hash.setdefault(provenance.content_hash(text), []).append(p)
    return by_hash


def collect_pending(tier3_dir, provenance_log, *, state_path=None, questions=None) -> list:
    """Konsolidierbare Fakten sammeln (AGENTS.md §10.3).

    Filter (Verhaltenstest):
      - nur `activity.kind` in ``write-new`` | ``write-update`` (§10.7 · §10.3),
      - trusted origin UND verified (§9.2c),
      - Fakt liegt **noch** im externen Puffer (tier3-Datei vorhanden),
      - noch **nicht** konsolidiert (`state_path` aus `mark_consolidated`).

    Rückgabe je Fakt: ``{key, path, fact, class, source, sha256, question}``.
    `key` = tier3-Dateistemm (= ``_slug(question)``); `fact` = echter Pufferinhalt.

    **Interface-Änderung (§9-pflichtig, kenntlich gemacht):** neue optionale Parameter
    `state_path` (bereits Konsolidiertes ausfiltern) und `questions`
    (Key→Frage; ohne Angabe wird die Frage aus dem Key rekonstruiert).
    """
    tier3 = Path(tier3_dir)
    done = set(_load_state(state_path)["consolidated"]) if state_path is not None else set()
    by_hash = _index_tier3_by_hash(tier3)
    pending: list = []
    seen: set = set()
    for rec in _read_jsonl(provenance_log):
        kind = (rec.get("activity") or {}).get("kind")
        if kind not in WRITE_CLASSES:
            continue
        if not _trusted_verified(rec):
            continue
        sha = (rec.get("entity") or {}).get("sha256")
        if not sha or sha in seen:
            continue
        paths = by_hash.get(sha)
        if not paths:  # bereits geflusht / nie geschrieben ⇒ nicht (mehr) im Puffer
            continue
        p = paths[0]
        key = p.stem
        if key in done:
            continue
        seen.add(sha)
        pending.append(
            {
                "key": key,
                "path": str(p),
                "fact": p.read_text(encoding="utf-8"),
                "class": kind,
                "source": rec.get("source"),
                "sha256": sha,
                "question": (questions or {}).get(key, key.replace("-", " ")),
            }
        )
    return pending


def build_sft_dataset(pending, out_path) -> dict:
    """SFT-Dataset (JSONL, Chat-Format) bauen (AGENTS.md §10.3).

    Je Zeile: ``{"messages": [{"role":"user",...},{"role":"assistant",...}], "hash": ...}``
    plus Provenienz-Keys (`key`, `class`, `sha256`). `hash` = SHA-256 über die
    kanonisch serialisierten `messages` (Inhalts-Hash je Zeile, vgl. K3).

    Einträge ohne `question`/`fact` werden übersprungen (kein leerer Fake-Satz).
    """
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    lines: list = []
    hashes: list = []
    for item in pending or []:
        question, fact = item.get("question"), item.get("fact")
        if not question or not fact:
            continue
        messages = [
            {"role": "user", "content": question},
            {"role": "assistant", "content": fact},
        ]
        canonical = json.dumps(messages, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        h = provenance.content_hash(canonical)
        record = {
            "messages": messages,
            "hash": h,
            "key": item.get("key"),
            "class": item.get("class"),
            "sha256": item.get("sha256"),
        }
        lines.append(json.dumps(record, ensure_ascii=False))
        hashes.append(h)
    out.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
    return {"ok": True, "path": str(out), "count": len(lines), "hashes": hashes}


def mark_consolidated(keys, state_path, *, success: bool = True) -> dict:
    """Keys als konsolidiert verbuchen – **nur nach Erfolg** (AGENTS.md §10.3).

    `success=False` (Training fehlgeschlagen) ⇒ **kein** Verbuchen; der Fakt bleibt
    damit im externen Puffer. Idempotent (keine Doppel-Keys).

    **Interface-Änderung (§9-pflichtig, kenntlich gemacht):** neuer Parameter `success`
    kodiert die „nur nach Erfolg"-Regel aus §10.3.
    """
    state = _load_state(state_path)
    known = list(state.get("consolidated") or [])
    if not success:
        return {
            "ok": False,
            "path": str(state_path),
            "consolidated": known,
            "added": [],
            "reason": "Training nicht erfolgreich (§10.3)",
        }
    added: list = []
    for k in keys or []:
        k = str(k)
        if k and k not in known:
            known.append(k)
            added.append(k)
    state["consolidated"] = known
    _write_state(state_path, state)
    return {"ok": True, "path": str(state_path), "consolidated": known, "added": added}


def flush(keys, tier3_dir, *, state_path=None) -> dict:
    """Konsolidierte Fakten aus dem **externen Puffer** entfernen (AGENTS.md §10.3).

    Erfolgreich konsolidiert ⇒ tier3-Datei löschen; fehlgeschlagen ⇒ bleibt (wird hier
    nie übergeben). Ist `state_path` gesetzt, werden **nur** dort als konsolidiert
    verbuchte Keys entfernt – nicht verbuchte landen in `blocked` und bleiben stehen
    (STOPP: kein Flush ohne Erfolgs-Beleg). Archiv-Stände (`*.superseded-*`) = Historie
    und bleiben erhalten.

    **Interface-Änderung (§9-pflichtig, kenntlich gemacht):** neuer optionaler Parameter
    `state_path` (Erfolgs-Guard).
    """
    tier3 = Path(tier3_dir)
    done = set(_load_state(state_path)["consolidated"]) if state_path is not None else None
    removed: list = []
    missing: list = []
    blocked: list = []
    for k in keys or []:
        k = str(k)
        if not k:
            continue
        if done is not None and k not in done:
            blocked.append(k)  # §10.3: nur nach Erfolg entfernen
            continue
        f = tier3 / f"{Path(k).stem}.md"
        if f.exists():
            f.unlink()
            removed.append(k)
        else:
            missing.append(k)
    return {"ok": True, "removed": removed, "missing": missing, "blocked": blocked}


def write_back(dataset_path, model: Optional[str] = None) -> dict:
    """Θ→Θ′ SFT (Write-Back). **Stub** – das Training läuft auf Kaggle (kein Fake).

    Raises:
        NotImplementedError: immer – der eigentliche Trainingsschritt ist nicht Teil
        dieser Vorarbeit (AGENTS.md §10.3).
    """
    raise NotImplementedError(
        f"Slow Consolidation (Θ→Θ′ SFT) läuft auf {TRAIN_LOCATION} (separater Teil); "
        f"diese Vorarbeit endet bei build_sft_dataset(out_path). Dataset: {dataset_path}"
        + (f", model={model}" if model else "")
    )


if __name__ == "__main__":  # pragma: no cover - CLI
    import sys

    tier3 = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("data/memory/tier3-working")
    log = Path(sys.argv[2]) if len(sys.argv) > 2 else tier3 / "provenance.jsonl"
    pend = collect_pending(tier3, log)
    print(json.dumps({"pending": len(pend), "keys": [p["key"] for p in pend]}, ensure_ascii=False, indent=2))
