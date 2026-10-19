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
hier, sondern auf **Kaggle** (separater Teil). Ohne injizierten Trainer bleibt
`write_back(...)` ein ehrlicher Stub (`NotImplementedError`) – es wird kein Training
simuliert/erfunden. Das **Modul erfindet nichts**; die Tests injizieren
Kontrollfluss-Doubles. Der **geschlossene Zyklus** (Sammeln → SFT-Dataset →
injiziertes Training → Probe → Flush) ist über `train_fn`/`probe_fn` **testbar ohne
GPU** und gilt erst durch einen **echten externen Lauf** (Kaggle/Ollama) als
verifiziert. `loss`/`adapter_path` werden nur durchgereicht.

Caveat (ehrlich): Die PROV-O-Records (K3, `provenance.py`) binden den **Inhalt-Hash**
und die **Aktivität**, aber NICHT den auslösenden Prompt. `collect_pending`
rekonstruiert die SFT-Frage daher aus dem Memory-Key (= Slug des Prompts, verlustarm)
bzw. nutzt eine übergebene `questions`-Zuordnung. Die **Fakten** (assistant-content)
sind real aus dem externen Puffer gelesen.

**Interface-Änderung (§9-pflichtig, kenntlich gemacht):** Alle hier definierten
Funktionen/Signaturen (`collect_pending`, `build_sft_dataset`, `mark_consolidated`,
`flush`, `write_back`) sowie die neuen optionalen Runner-Parameter
`consolidation_state_path` sind §9-pflichtig und **freigegeben** (`approved`
Batnini + Taoufik, 2026-10-08).

**Nachtrag (2026-10-10, additiv):** `write_back` erhält **rückwärtskompatible**
keyword-only optionale Injektions-Parameter `train_fn`, `probe_fn`, `tier3_dir`,
`provenance_log`, `state_path` (Interface additiv; §9.3 = **freigegeben** —
Batnini + Taoufik, 2026-10-11; ≥ 2 distinkte Personen). Bestehende Aufrufe (`write_back(dataset, model)`)
bleiben unverändert (ehrlicher Stub).

**N2/N3 (Auftrag Phase 2, Audit b09a0a9; §9-Freigabe `approved` Batnini + Taoufik,
2026-10-08):** Konsolidierung wird an den **Inhalt** gebunden (`fact_sha256` je Key;
ein geänderter Fakt bleibt nicht versteckt), und `flush` löscht **nur mit Erfolgs-
beleg** (`state_path` verpflichtend) und **nie** Archiv-Stände (`.superseded-`).
Das alte State-Format `{"consolidated": [keys]}` wird weiterhin gelesen, gilt aber
nach F3 als **inert** (Hash unbekannt ⇒ nicht konsolidiert).

**F1/F2/F3 (Auftrag Phase 2, Audit 75095d5; §9-Freigabe `approved` Batnini +
Taoufik, 2026-10-08):** Verschärfung von N2/N3 auf **fail-closed**:
  - **F1** `flush` löscht nur bei **Hash-Gleichheit** (`entries[key].fact_sha256` ==
    `content_hash(Datei-Inhalt)`) **und** `probe_passed=True`; geänderter Fakt,
    unbekannter Hash, fehlender Eintrag oder negativer Probe ⇒ **blocked**, kein
    Löschen.
  - **F2** `mark_consolidated(..., probe_passed=False)` verbucht den Key **nicht**
    als konsolidiert (und **stuft** eine frühere Konsolidierung **herab**);
    `flush`/`discard_if_consolidated` respektieren nur den **positiven** Probe.
  - **F3** `_is_consolidated`: **unbekannter Hash ⇒ False** (fail-closed). ⟹
    **Legacy-States ohne Hash sind ab jetzt inert** – sie verhindern weder Sammeln
    noch erneutes Schreiben.
Quelle (Belegt): nur ein **positiver** Probe erlaubt Konsolidierung
(Kairos/Validation-Gated, `connectors/gaama.md`); §10.3 (arXiv:2608.22215 §3.4):
Flush nur nach Erfolg, sonst bleibt der Fakt.
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
    """Konsolidierungs-Zustand lesen; fehlend/defekt ⇒ leer.

    Rückgabe: ``{"consolidated": [keys], "entries": {key: {...}}}``.
    **Rückwärtskompatibel (N2):** das alte Format ``{"consolidated": [keys]}`` wird
    weiter gelesen – dann fehlen die ``entries`` und der konsolidierte Inhalt-Hash
    gilt als **unbekannt** (Key-Match bleibt gültig, s. `_is_consolidated`).
    """
    empty = {"consolidated": [], "entries": {}}
    try:
        data = json.loads(Path(state_path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return empty
    if not isinstance(data, dict):
        return empty
    keys = data.get("consolidated")
    consolidated = [str(k) for k in keys] if isinstance(keys, list) else []
    entries: dict = {}
    raw_entries = data.get("entries")
    if isinstance(raw_entries, dict):
        for k, v in raw_entries.items():
            if isinstance(v, dict):
                entries[str(k)] = {
                    "fact_sha256": v.get("fact_sha256"),
                    "model": v.get("model"),
                    "probe_passed": v.get("probe_passed"),
                }
    return {"consolidated": consolidated, "entries": entries}


def _is_consolidated(entry: Optional[dict], current_sha: Optional[str]) -> bool:
    """Gilt ein Fakt als konsolidiert? **Nur** bei positivem Probe **und** Hash-Gleichheit.

    F3 (Audit 75095d5, **fail-closed**):
      - Kein `entry` (Legacy-State = reine Key-Liste) ⇒ **False** (Hash unbekannt).
      - `probe_passed` ist nicht `True` (fehlt/None/False) ⇒ **False** (nur **positiv**
        geprüfte Fakten sind konsolidiert; Kairos/Validation-Gated, `connectors/gaama.md`).
      - `fact_sha256` fehlt/None ⇒ **False** (Hash unbekannt).
      - sonst konsolidiert **nur**, wenn `stored == current_sha`; ein geänderter Fakt
        (neuer Hash, gleicher Key) ist wieder konsolidierbar.
    """
    if not entry:
        return False
    if entry.get("probe_passed") is not True:
        return False
    stored = entry.get("fact_sha256")
    if not stored:
        return False
    return stored == current_sha


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
    state = _load_state(state_path) if state_path is not None else {"consolidated": [], "entries": {}}
    done = set(state.get("consolidated") or [])
    entries = state.get("entries") or {}
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
        try:
            fact = p.read_text(encoding="utf-8")
        except OSError:  # pragma: no cover - unlesbare Datei überspringen
            continue
        # F3 (fail-closed): nur ausschließen, wenn der AKTUELLE Fakt-Hash ==
        # konsolidierter Hash UND der Probe positiv ist. Unbekannter Hash ⇒ nicht
        # ausblenden (Legacy-States sind inert).
        if key in done and _is_consolidated(entries.get(key), provenance.content_hash(fact)):
            continue
        seen.add(sha)
        pending.append(
            {
                "key": key,
                "path": str(p),
                "fact": fact,
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


def mark_consolidated(
    keys, state_path, *, success: bool = True, facts=None, model=None, probe_passed: bool = True
) -> dict:
    """Keys als konsolidiert verbuchen – **nur nach Erfolg** (AGENTS.md §10.3).

    `success=False` (Training fehlgeschlagen) ⇒ **kein** Verbuchen; der Fakt bleibt
    damit im externen Puffer. Idempotent (keine Doppel-Keys).

    **N2:** je Key wird zusätzlich `fact_sha256` (Inhalt des konsolidierten Fakts),
    optional `model` und `probe_passed` verbucht. `facts` = Mapping Key → Fakt-Inhalt;
    fehlt es, bleibt der Hash **unbekannt** (fail-closed ⇒ nicht konsolidiert, F3). Ein
    erneutes Verbuchen desselben Keys **aktualisiert** den Hash (nach write-update +
    Retraining ist der neue Fakt wieder konsolidiert).

    **F2 (Audit 75095d5):** `probe_passed=False` verbucht den Key **nicht** in
    `consolidated` und **stuft** eine frühere Konsolidierung **herab** (kein Discard/
    Flush ohne **positiven** Probe; `connectors/gaama.md`).

    **Interface-Änderung (§9-pflichtig, kenntlich gemacht, `approved` Batnini +
    Taoufik 2026-10-08):** neue optionale Parameter `success` (nur nach Erfolg, §10.3)
    sowie `facts`/`model`/`probe_passed` (N2-Inhaltsbindung/F2-Probe).
    """
    state = _load_state(state_path)
    known = list(state.get("consolidated") or [])
    entries = dict(state.get("entries") or {})
    if not success:
        return {
            "ok": False,
            "path": str(state_path),
            "consolidated": known,
            "added": [],
            "reason": "Training nicht erfolgreich (§10.3)",
        }
    added: list = []
    for k in (str(k) for k in (keys or []) if str(k)):
        entry = dict(entries.get(k) or {})
        if facts and k in facts:
            entry["fact_sha256"] = provenance.content_hash(str(facts[k]))
        entry["model"] = model if model is not None else entry.get("model")
        entry["probe_passed"] = bool(probe_passed)
        entries[k] = entry
        if probe_passed:
            if k not in known:
                known.append(k)
                added.append(k)
        elif k in known:  # F2: negativer Probe ⇒ frühere Konsolidierung herabgestuft
            known.remove(k)
    state["consolidated"] = known
    state["entries"] = entries
    _write_state(state_path, state)
    return {"ok": True, "path": str(state_path), "consolidated": known, "added": added, "entries": entries}


def flush(keys, tier3_dir, *, state_path=None) -> dict:
    """Konsolidierte Fakten aus dem **externen Puffer** entfernen (AGENTS.md §10.3).

    Erfolgreich konsolidiert ⇒ tier3-Datei löschen; fehlgeschlagen ⇒ bleibt.

    **N3 (Audit b09a0a9):**
      - **Ohne `state_path` wird nichts gelöscht** – jeder Key ist `blocked`
        (kein ungeprüftes Entfernen; §10.3 „nur nach Erfolg").
      - Der Erfolg wird **aus dem Beleg** (`state_path`/`mark_consolidated`) gelesen,
        nicht aus bloßer Aufruferangabe: nur dort verbuchte Keys werden entfernt.
      - Archiv-Stände (`.superseded-` im Namen) = Historie und werden **nie**
        gelöscht (§10.7 „invalidieren, NICHT löschen").

    **F1 (Audit 75095d5, fail-closed):** Gelöscht wird **nur** bei **Hash-Gleichheit**
    (`entries[key].fact_sha256 == content_hash(Datei-Inhalt)`) **und** positivem Probe
    (`probe_passed=True`). Ein **geänderter Fakt** (Hash-Mismatch), ein **unbekannter
    Hash** (kein Eintrag / `fact_sha256=None`) oder ein negativer Probe ⇒ **`blocked`**,
    die Datei bleibt. Eine fehlende Datei meldet `missing` (bereits weg).

    **Interface-Änderung (§9-pflichtig, kenntlich gemacht, `approved` Batnini +
    Taoufik 2026-10-08):** `state_path` ist für einen Flush **erforderlich**; ohne ihn
    wird verweigert (Default ⇒ sicher).
    """
    tier3 = Path(tier3_dir)
    raw = [str(k) for k in (keys or []) if str(k)]
    if state_path is None:
        return {
            "ok": False,
            "removed": [],
            "missing": [],
            "blocked": raw,
            "reason": "Flush ohne Erfolgsbeleg verweigert (N3/§10.3)",
        }
    state = _load_state(state_path)
    done = set(state.get("consolidated") or [])
    entries = state.get("entries") or {}
    removed: list = []
    missing: list = []
    blocked: list = []
    for k in raw:
        if ".superseded-" in k:  # N3: Archiv = Historie, NIE löschen (§10.7)
            blocked.append(k)
            continue
        if k not in done:
            blocked.append(k)  # §10.3: nur nach Erfolg/positivem Probe entfernen
            continue
        f = tier3 / f"{Path(k).stem}.md"
        if not f.exists():
            missing.append(k)  # bereits entfernt/nie geschrieben – kein Fake-Erfolg
            continue
        current = provenance.content_hash(f.read_text(encoding="utf-8"))
        if not _is_consolidated(entries.get(k), current):
            blocked.append(k)  # F1: Hash unbekannt/geändert oder Probe negativ ⇒ bleibt
            continue
        f.unlink()
        removed.append(k)
    return {"ok": True, "removed": removed, "missing": missing, "blocked": blocked}


def _probe_positive(result) -> bool:
    """Externes Probe-Signal auswerten – **fail-closed** (nur explizit positiv).

    Wahr ist nur ein ``True`` bzw. ein Dict mit ``passed is True`` oder ``ok is True``.
    Alles andere (``None``, ``False``, leeres/negatives Dict) ⇒ **nicht** konsolidiert
    (§10.3: Flush nur nach Erfolg; `connectors/gaama.md`: nur ein **positiver** Probe
    erlaubt Konsolidierung – Kairos/Validation-Gated).
    """
    if isinstance(result, dict):
        return result.get("passed") is True or result.get("ok") is True
    return result is True


def write_back(
    dataset_path,
    model: Optional[str] = None,
    *,
    train_fn=None,
    probe_fn=None,
    tier3_dir=None,
    provenance_log=None,
    state_path=None,
    guard_fn=None,
    questions=None,
) -> dict:
    """Geschlossener Zyklus Θ→Θ′ (Write-Back) – **injizierbar, ohne GPU** (§10.3).

    Ablauf (durchgängig fail-closed):
      1. ``pending = collect_pending(tier3_dir, provenance_log, state_path=...)``;
         ohne Puffer/Log oder ohne pending ⇒
         ``{"ok": True, "flushed": [], "kept": [], "note": "keine pending"}``
         (nichts zu tun, kein Fake).
      2. ``build_sft_dataset(pending, dataset_path)`` – Korpus **real** schreiben.
      3. Ohne injizierten ``train_fn`` ⇒ **``NotImplementedError``** – der eigentliche
         Trainingsschritt läuft extern auf Kaggle (ehrlicher Stub, unverändert).
      4. ``trained = train_fn(dataset_path, model)``; meldet ``train_fn`` keinen Erfolg
         (``ok`` fehlt/``False``) ⇒ **kein Flush**, ``{"ok": False, ...}`` (fail-closed).
      5. Je pending-Fakt: nur bei **positivem** ``probe_fn(item)`` (externes Signal,
         `_probe_positive`) **und** vorhandenem ``state_path`` wird
         ``mark_consolidated(..., success=True, probe_passed=True)`` verbucht (bindet
         den Inhalt-Hash); sonst bleibt der Fakt im Puffer.
      6. ``flush(keys, tier3_dir, state_path=...)`` entfernt **nur** die belegten,
         hash-gleichen Keys (F1) aus dem externen Puffer.

    Jeder Rückgabe-Pfad trägt ``probe_results`` (echtes Probe-Signal je Fakt;
    Audit H1-H5 — Evidenz §9.1d; leer, wenn noch nicht geprobt wurde).

    **Kein Fake:** ``train_fn``/``probe_fn`` sind echte Injektionspunkte; ohne sie
    bleibt das ehrliche Verhalten (Stub bzw. kein Flush). ``loss``/``adapter_path``
    werden **ausschließlich** aus ``trained`` durchgereicht – nie erfunden. Die
    Hash-Konsistenz ist über ``mark_consolidated(facts=...)`` (bindet den aktuellen
    Fakt-Hash) **und** ``flush`` (F1: löscht nur bei Hash-Gleichheit) durchgesetzt;
    ein geänderter Fakt bleibt damit im Puffer.

    **Interface-Erweiterung (additiv/rückwärtskompatibel):** die neuen keyword-only
    optionalen Parameter `train_fn`, `probe_fn`, `tier3_dir`, `provenance_log`,
    `state_path`, `questions` (Key→echte Frage; wird an ``collect_pending``
    durchgereicht, damit Train- und Probe-Frage übereinstimmen — §10.3)
    (Interface additiv; §9.3 = **freigegeben** — Batnini + Taoufik,
    2026-10-11; ≥ 2 distinkte Personen).
    Bestehende Aufrufe (``write_back(dataset, model)``) verhalten sich unverändert.
    """
    # 3) Ehrlicher Stub: ohne injizierten Trainer kein FS-Zugriff, kein Fake (§10.3).
    if train_fn is None:
        raise NotImplementedError(
            f"Slow Consolidation (Θ→Θ′ SFT) läuft auf {TRAIN_LOCATION} (separater Teil); "
            f"diese Vorarbeit endet bei build_sft_dataset(out_path). Dataset: {dataset_path}"
            + (f", model={model}" if model else "")
            + "; für den geschlossenen Zyklus train_fn (und probe_fn) injizieren."
        )

    # 1) Pending sammeln – nur mit echtem Puffer/Log; sonst nichts zu tun.
    if tier3_dir is None or provenance_log is None:
        pending: list = []
    else:
        pending = collect_pending(tier3_dir, provenance_log, state_path=state_path, questions=questions)
    if not pending:
        return {"ok": True, "flushed": [], "kept": [], "note": "keine pending", "probe_results": []}

    # 2) SFT-Korpus real schreiben (kein Fake-Satz).
    build_sft_dataset(pending, dataset_path)

    # 3) Externes SFT (injiziert). Kein Erfolg ⇒ fail-closed, KEIN Flush.
    trained = train_fn(dataset_path, model)
    if not (isinstance(trained, dict) and trained.get("ok")):
        return {
            "ok": False,
            "flushed": [],
            "kept": [p["key"] for p in pending],
            "reason": "Training nicht erfolgreich (§10.3)",
            "probe_results": [],
        }

    # 4) Probe-gesteuertes Verbuchen (externes Signal; nur positive Fakten).
    positives: list = []
    probe_results: list = []
    for item in pending:
        raw = probe_fn(item) if probe_fn is not None else None
        probe_results.append(raw)
        if state_path is not None and _probe_positive(raw):
            positives.append(item)

    # 4b) Run-Level-Guard (z. B. Base-Rate, AGENTS.md §9.1d/§10.3): Einwand ⇒ abstain,
    #     KEINE Verbuchung und KEIN Flush.
    if guard_fn is not None:
        reason = guard_fn(probe_results)
        if reason:
            return {
                "ok": False,
                "decision": "abstain",
                "flushed": [],
                "kept": [p["key"] for p in pending],
                "reason": reason,
                "probe_results": probe_results,
            }

    flush_keys: list = []
    for item in positives:
        mark_consolidated(
            [item["key"]],
            state_path,
            success=True,
            facts={item["key"]: item["fact"]},
            model=model,
            probe_passed=True,
        )
        flush_keys.append(item["key"])

    # 5) Flush **nur** nach Beleg (oben verbucht, success=True) – F1 prüft den Hash.
    res = flush(flush_keys, tier3_dir, state_path=state_path)
    flushed = list(res.get("removed") or [])
    kept = [p["key"] for p in pending if p["key"] not in flushed]
    return {
        "ok": bool(res.get("ok")),
        "flushed": flushed,
        "kept": kept,
        "loss": trained.get("loss"),
        "adapter_path": trained.get("adapter_path"),
        "probe_results": probe_results,
    }


if __name__ == "__main__":  # pragma: no cover - CLI
    import sys

    tier3 = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("data/memory/tier3-working")
    log = Path(sys.argv[2]) if len(sys.argv) > 2 else tier3 / "provenance.jsonl"
    pend = collect_pending(tier3, log)
    print(json.dumps({"pending": len(pend), "keys": [p["key"] for p in pend]}, ensure_ascii=False, indent=2))
