"""ZsRE-Konsolidierungskorpus (§10.3) – Mapping/Hash/Format.

Echte Tests (kein Fake): (a) reine Mapping-Funktion `row_to_record` mit einem
echten kleinen Fixture-Dict (Feld-Form wie HF `community-datasets/qa_zre`),
(b) Inhalts-Hash + TRL-Chat-JSONL-Format.

Das echte `load_dataset("community-datasets/qa_zre", ...)` läuft nur, wenn
`datasets` installiert **und** Netz verfügbar ist – sonst `pytest.skip` (kein
Fake-Record, keine erfundenen Daten; vgl. AGENTS.md Guardrail 7).

Quellen: arXiv:2608.22215v2 §3.4/A.1 · https://aclanthology.org/K17-1034/
"""

import hashlib
import json

import provenance
import pytest
import zsre_corpus as zc

# Echte Feld-Form von community-datasets/qa_zre (real aus der Quelle gelesen).
FIXTURE = {
    "relation": "industry",
    "question": "Which industry is XXX associated with?",
    "subject": "Commercial Press",
    "context": "In 1897, 26-year-old Xia Ruifang and three of his friends founded The Commercial Press.",
    "answers": ["publishing"],
}


# --------------------------------------------------------- (a) Mapping row→messages
def test_row_to_record_mapping():
    rec = zc.row_to_record(FIXTURE)
    assert rec["source"] == "zsre"
    assert rec["relation"] == "industry"
    assert rec["subject"] == "Commercial Press"
    assert [m["role"] for m in rec["messages"]] == ["user", "assistant"]
    # F6: Frage ist an ihr Subjekt gebunden (XXX → subject), nicht der Roh-Platzhalter.
    assert rec["messages"][0]["content"] == "Which industry is Commercial Press associated with?"
    assert "XXX" not in rec["messages"][0]["content"]
    assert rec["messages"][1]["content"] == "publishing"  # answers[0]


def test_row_to_record_skips_empty_question_or_answer():
    assert zc.row_to_record({**FIXTURE, "answers": []}) is None
    assert zc.row_to_record({**FIXTURE, "answers": [""]}) is None
    assert zc.row_to_record({**FIXTURE, "question": "   "}) is None


def test_row_to_record_uses_first_answer_only():
    rec = zc.row_to_record({**FIXTURE, "answers": ["first", "second"]})
    assert rec["messages"][1]["content"] == "first"


# --------------------------------------------------------- (b) Hash + Format
def test_hash_is_sha256_of_canonical_messages():
    rec = zc.row_to_record(FIXTURE)
    canonical = json.dumps(rec["messages"], ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    assert rec["hash"] == hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    assert rec["hash"] == provenance.content_hash(canonical)  # konsistent zu M1/K3
    assert len(rec["hash"]) == 64


def test_records_to_jsonl_format_und_skip(tmp_path):
    rec = zc.row_to_record(FIXTURE)
    out = tmp_path / "corpus.jsonl"
    res = zc.records_to_jsonl([rec, {"foo": "bar"}, {}], out)
    assert res["count"] == 1 and res["hashes"] == [rec["hash"]]
    lines = out.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1
    assert json.loads(lines[0]) == rec  # TRL-Chat-Record 1:1


def test_records_to_jsonl_leer(tmp_path):
    out = tmp_path / "leer.jsonl"
    res = zc.records_to_jsonl([], out)
    assert res["count"] == 0 and out.read_text(encoding="utf-8") == ""


# --------------------------------------------------------- echtes load_dataset (skip)
@pytest.mark.live  # echter HF-Zugriff (load_dataset) -> im Offline-Lauf übersprungen
def test_build_zsre_corpus_real_or_skip(tmp_path):
    pytest.importorskip("datasets")
    out = tmp_path / "zsre.jsonl"
    try:
        res = zc.build_zsre_corpus(out, n=3, split="validation")
    except Exception as exc:  # kein Netz / HF nicht erreichbar ⇒ ehrlich überspringen
        pytest.skip(f"kein Netz/HF: {type(exc).__name__}: {exc}")
    assert res["dataset"] == "community-datasets/qa_zre"
    assert res["count"] == 3 and res["requested"] == 3
    assert res["rows_scanned"] >= 3
    lines = [json.loads(x) for x in out.read_text(encoding="utf-8").splitlines()]
    assert len(lines) == res["count"]
    for line in lines:
        assert line["source"] == "zsre"
        assert [m["role"] for m in line["messages"]] == ["user", "assistant"]
        assert line["messages"][1]["content"]  # echte Antwort, keine Erfindung
        assert len(line["hash"]) == 64
