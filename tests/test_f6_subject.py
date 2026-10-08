"""F6 (Audit 75095d5): ZsRE-Fragen müssen an ihr Subjekt gebunden sein.

Die Frage enthält in ZsRE den Platzhalter ``XXX``; ``row_to_record`` muss ihn
durch das ``subject`` ersetzen, damit der Subjektbezug nicht verloren geht
(arXiv:2608.22215 §4.1 „fact corpus from ZsRE … behavioral labeling";
RQGM-Forderung „subjektgebundene QA-Daten"). **Formatänderung §9 approved**
(Batnini + Taoufik, 2026-10-08).

Offline mit Fixture-Dict (echte Feld-Form von ``community-datasets/qa_zre``,
Guardrail 7 – keine erfundenen Daten, kein Netz).
"""

import zsre_corpus as zc

# Reales Beispiel: ZsRE-Frage mit Platzhalter + Subjekt + Gold-Antwort.
FIXTURE = {
    "relation": "cause of death",
    "question": "In one word, how did XXX die?",
    "subject": "Chen Yi-hsiung",
    "context": "Chen Yi-hsiung committed suicide in 2006.",
    "answers": ["suicide"],
}


def test_question_binds_subject():
    rec = zc.row_to_record(FIXTURE)
    content = rec["messages"][0]["content"]
    assert "Chen Yi-hsiung" in content  # Subjekt ist in der Frage
    assert "XXX" not in content  # Platzhalter ersetzt
    assert rec["subject"] == "Chen Yi-hsiung"  # Subjektfeld gesetzt
    assert rec["messages"][1]["content"] == "suicide"


def test_question_without_subject_keeps_placeholder():
    rec = zc.row_to_record({**FIXTURE, "subject": None})
    assert "XXX" in rec["messages"][0]["content"]  # kein Erfinden ohne Subjekt
    assert rec["subject"] is None


def test_question_without_placeholder_unchanged():
    row = {**FIXTURE, "question": "Where was Chen Yi-hsiung born?"}
    rec = zc.row_to_record(row)
    assert rec["messages"][0]["content"] == "Where was Chen Yi-hsiung born?"


def test_subject_binding_replaces_all_occurrences():
    row = {**FIXTURE, "question": "How did XXX die and who mourned XXX?"}
    rec = zc.row_to_record(row)
    assert rec["messages"][0]["content"] == ("How did Chen Yi-hsiung die and who mourned Chen Yi-hsiung?")
    assert "XXX" not in rec["messages"][0]["content"]
