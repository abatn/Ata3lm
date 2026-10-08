#!/usr/bin/env python3
"""
ZsRE-Konsolidierungskorpus (AGENTS.md §10.3 Write-Back) – SFT-Chat-Format.

Quellen (VOR Nutzung real geprüft, HTTP 200, 2026-10-07):
  - Paper-Methode: **arXiv:2608.22215v2** §3.4 „Write-back as slow consolidation"
    + Appendix A.1 „Offline routing dataset and behavioral supervision": der
    Fakten-Korpus stammt aus dem **ZsRE**-Benchmark; write-back = (q,a)-Proben
    **und** sentence-level SFT. <https://arxiv.org/html/2608.22215v2>
  - Dataset: **`community-datasets/qa_zre`** (HF; Felder `relation, question,
    subject, context, answers`; train 8_400_000, validation 6_000, test 120_000).
    <https://huggingface.co/api/datasets/community-datasets/qa_zre>
  - Ursprung: Levy, Seo, Choi & Zettlemoyer (2017), *Zero-shot relation extraction
    via reading comprehension* (CoNLL), pp. 333–342.
    <https://aclanthology.org/K17-1034/>
  - JSONL-Format: TRL-Chat (`messages`).
    <https://huggingface.co/docs/trl/dataset_formats>

Status (ehrliche Trennung, vgl. AGENTS.md-Kopf):
  - **Belegt:** Fakten-Korpus = ZsRE (Paper); Dataset existiert + Felder (HF-API);
    Levy et al. 2017 (CoNLL).
  - **Auftrag (Projekt):** das hier gebaute Chat-Format/JSONL und das n-Sampling.
  - **§9 NEUE QUELLE ⇒ Human-Gate `ask`:** `community-datasets/qa_zre` steht noch
    **nicht** in der Ontologie (`data/memory/tier1-base/ontology.md`); die Nutzung
    ist **nicht vorab freigegeben**. Dieser Korpus ist lediglich **vorbereitet**.

Ehrlich (keine Erfindung, Guardrail 7): Die **volle** Menge ist aus der Quelle
verfügbar; hier wird nur ein **gesampeltes `n`** der ersten Zeilen verwendet.
Zeilen ohne nicht-leere Antwort werden übersprungen (reale Daten) – es wird
**nichts** erfunden.

**Interface (§9-pflichtig, kenntlich gemacht):** die Funktionen
`row_to_record`, `records_to_jsonl`, `build_zsre_corpus` sind NEU und NICHT
menschlich freigegeben (§9).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, Optional

import provenance

# Offizielle Quelle (NICHT erfinden – exakt diese ID).
DATASET_NAME = "community-datasets/qa_zre"
SOURCE = "zsre"
SOURCE_NOTE = "volle Menge aus Quelle verfuegbar; hier gesampeltes n"


def row_to_record(row: dict) -> Optional[dict]:
    """HF-ZsRE-Zeile → TRL-Chat-Record (reine Funktion, kein Netz, kein Fake).

    **Formatänderung (§9 approved, Batnini + Taoufik, 2026-10-08):** Die Frage
    wird an ihr **Subjekt** gebunden – im Paper die ``(knowledge, query,
    answer)``-Triples (arXiv:2608.22215 §4.1 „fact corpus from ZsRE …
    behavioral labeling"; RQGM-Forderung „subjektgebundene QA-Daten"). Enthält
    die ``question`` den ZsRE-Platzhalter ``XXX`` **und** ist ein ``subject``
    vorhanden, wird ``XXX`` durch das Subjekt ersetzt (alle Vorkommen). Das
    Subjekt bleibt zusätzlich als Feld erhalten. **Kein** Erfinden: fehlt das
    ``subject``, bleibt die Frage unverändert. (Ursprung der Platzhalter:
    Levy, Seo, Choi & Zettlemoyer 2017, CoNLL, ``K17-1034``.)

    Bildet den ersten Fakt ``answers[0]`` als assistant-Antwort zur (gebundenen)
    ``question``. Zeilen ohne nicht-leere Frage **oder** Antwort ergeben
    ``None`` (überspringen, nichts erfinden).

    Rückgabe::

        {"messages": [{"role":"user","content":<gebundene question>},
                      {"role":"assistant","content":<answers[0]>}],
         "source": "zsre", "relation": <relation>, "subject": <subject>,
         "hash": <sha256 der kanonisch serialisierten messages>}
    """
    question = str(row.get("question") or "").strip()
    subject = str(row.get("subject") or "").strip()
    if "XXX" in question and subject:  # Subjektbindung (Formatänderung §9 approved)
        question = question.replace("XXX", subject)
    answers = row.get("answers") or []
    answer = str(answers[0]).strip() if answers else ""
    if not question or not answer:
        return None
    messages = [
        {"role": "user", "content": question},
        {"role": "assistant", "content": answer},
    ]
    canonical = json.dumps(messages, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return {
        "messages": messages,
        "source": SOURCE,
        "relation": row.get("relation"),
        "subject": subject or None,
        "hash": provenance.content_hash(canonical),
    }


def records_to_jsonl(records: Iterable[dict], out_path) -> dict:
    """Records als JSONL schreiben (TRL-Chat-Format).

    Leere/ungültige Records (ohne `messages`) werden übersprungen. Gibt Zahl der
    geschriebenen Zeilen und die Zeilen-Hashes zurück.
    """
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    lines: list = []
    hashes: list = []
    for rec in records or []:
        if not isinstance(rec, dict) or not rec.get("messages"):
            continue
        lines.append(json.dumps(rec, ensure_ascii=False))
        hashes.append(rec.get("hash"))
    out.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
    return {"ok": True, "path": str(out), "count": len(lines), "hashes": hashes}


def build_zsre_corpus(
    out_path,
    n: int = 10000,
    split: str = "train",
    *,
    dataset_name: str = DATASET_NAME,
    streaming: bool = True,
) -> dict:
    """SFT-Konsolidierungskorpus aus ZsRE bauen (AGENTS.md §10.3).

    Lädt ``community-datasets/qa_zre`` (Default **Streaming** → nur die ersten
    Zeilen werden geholt, kein 2-GB-Download) und schreibt je Fakt ein
    TRL-Chat-Beispiel `(question, answers[0])` als JSONL.

    Gescannt wird, bis `n` valide Beispiele geschrieben sind oder die Quelle
    endet; Zeilen mit leerer Antwort werden gezählt (`skipped_empty`) und
    übersprungen (reale Daten – nichts erfinden).

    Returns:
        dict mit `count` (geschrieben), `requested`, `split`, `dataset`,
        `rows_scanned`, `skipped_empty`, `hashes`, `path`, `note`.
    """
    from datasets import load_dataset  # lokal importiert: Modul bleibt netzfrei nutzbar

    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    ds = load_dataset(dataset_name, split=split, streaming=streaming)
    count = 0
    rows_scanned = 0
    skipped = 0
    hashes: list = []  # nur bis HASH_CAP gehalten (Voll-Menge bleibt RAM-schonend)
    hash_cap = 10_000
    with out.open("w", encoding="utf-8") as fh:  # inkrementell schreiben (kein Voll-RAM)
        # Hinweis (B, 2026-10-07): der Zweig „Stream endet vor n" ist mit dem echten
        # 8,4-Mio-Korpus im Test nicht abbildbar -> Branch-Ausnahme (siehe Rekursion 075).
        for row in ds:  # pragma: no branch
            rows_scanned += 1
            rec = row_to_record(row)
            if rec is None:
                skipped += 1
                continue
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
            # Hinweis (B, 2026-10-07): die Kappungsgrenze (10k) wird nur beim Voll-Korpus
            # erreicht (RAM-Schutz); im Test nicht abbildbar -> Branch-Ausnahme.
            if len(hashes) < hash_cap:  # pragma: no branch
                hashes.append(rec.get("hash"))
            count += 1
            if count >= n:
                break
    return {
        "ok": True,
        "path": str(out),
        "count": count,
        "hashes": hashes,
        "requested": n,
        "split": split,
        "dataset": dataset_name,
        "rows_scanned": rows_scanned,
        "skipped_empty": skipped,
        "note": SOURCE_NOTE,
    }


if __name__ == "__main__":  # pragma: no cover - CLI
    import argparse

    parser = argparse.ArgumentParser(description="ZsRE-Konsolidierungskorpus (§10.3) bauen.")
    parser.add_argument("out_path", help="Ziel-JSONL (TRL-Chat-Format)")
    parser.add_argument("-n", "--num", type=int, default=10000, help="Anzahl gesampelter Fakten")
    parser.add_argument("--split", default="train", help="HF-Split (default: train)")
    args = parser.parse_args()
    print(json.dumps(build_zsre_corpus(args.out_path, n=args.num, split=args.split), ensure_ascii=False, indent=2))
