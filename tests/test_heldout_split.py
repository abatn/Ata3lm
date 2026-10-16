"""P-B: disjunkter Held-out-Split im Write-Back-Zyklus (AGENTS.md §10.3, §9.1c).

Echte Tests ohne Netz: Records in der echten TRL-Chat-Form (wie
`zsre_corpus.row_to_record` sie erzeugt) und eine echte JSONL-Eval-Datei.
Keine Fakes, keine skripteten Antworten (Guardrail 7).

Belegte Ausgangslage: Eval-Set `ergebnisse/zsre-eval-f6.jsonl` und Train-Set
hatten Overlap 20/20 Fragen (Rek. 109/113, Kaggle-Lauf).
"""

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "kaggle"))

import write_back_cycle as wbc  # noqa: E402


def _rec(question: str, answer: str) -> dict:
    return {
        "messages": [
            {"role": "user", "content": question},
            {"role": "assistant", "content": answer},
        ],
        "source": "zsre",
    }


RECORDS = [
    _rec("Which industry is Commercial Press associated with?", "publishing"),
    _rec("Who founded Acme Corp?", "Jane Doe"),
    _rec("Where is Lake Vanda located?", "Antarctica"),
    _rec("What language is spoken in Quebec?", "French"),
]


def test_select_tasks_without_exclusion_keeps_all_rows():
    # Abwaertskompatibel: ohne exclude_questions bleibt das Verhalten gleich.
    tasks = wbc.select_tasks(RECORDS, n=10, seed=None)
    assert len(tasks) == 4


def test_select_tasks_excludes_eval_questions_overlap_zero():
    eval_questions = {RECORDS[0]["messages"][0]["content"], RECORDS[1]["messages"][0]["content"]}
    tasks = wbc.select_tasks(RECORDS, n=10, seed=None, exclude_questions=eval_questions)
    task_questions = {t["question"] for t in tasks}
    assert task_questions.isdisjoint(eval_questions)  # Overlap == 0
    assert len(tasks) == 2


def test_select_tasks_seed_shuffle_after_exclusion_respects_n():
    eval_questions = {RECORDS[0]["messages"][0]["content"]}
    tasks = wbc.select_tasks(RECORDS, n=2, seed=42, exclude_questions=eval_questions)
    assert len(tasks) == 2
    assert all(t["question"] not in eval_questions for t in tasks)


def test_eval_questions_reads_jsonl_and_none_is_empty(tmp_path):
    eval_file = tmp_path / "eval.jsonl"
    eval_file.write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) for r in RECORDS[:2]) + "\n\n",
        encoding="utf-8",
    )
    got = wbc._eval_questions(eval_file)
    assert got == {RECORDS[0]["messages"][0]["content"], RECORDS[1]["messages"][0]["content"]}
    assert wbc._eval_questions(None) == set()


def test_flush_and_probe_share_grader_strict_decision():
    # P-A: Probe (write_back_cycle) und Gate nutzen denselben Grader → gleiche Entscheidung.
    import acceptance_gate as ag

    assert wbc._grade is ag.grade
    assert ag.grade("Publishing.", "publishing") is True  # normalisiert
    assert ag.grade("publishing house in Beijing", "publishing") is False  # strict: kein Teilstring
    assert ag.grade("publishing\nfoo bar", "publishing") is True  # erste Zeile extrahiert
    assert ag.grade("", "publishing") is False
    assert ag.grade("x", "") is False  # leeres Gold → nie Treffer


def test_base_rate_guard_abstains_on_zero_base():
    import acceptance_gate as ag

    assert ag.base_rate_guard(0, 200) is not None  # em_base 0 → abstain
    assert ag.base_rate_guard(8, 200) is None
    assert ag.base_rate_guard(0, 0) == "keine Items"


def test_grade_rejects_unknown_mode():
    import acceptance_gate as ag

    with pytest.raises(ValueError):
        ag.grade("a", "a", mode="fuzzy")
    assert ag.grade("the big city", "big", mode="substring") is True


def test_eval_questions_missing_file_fails_loud(tmp_path):
    with pytest.raises(FileNotFoundError):
        wbc._eval_questions(tmp_path / "fehlt.jsonl")
