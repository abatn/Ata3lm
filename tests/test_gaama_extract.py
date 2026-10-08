"""GAAMA-Extraktion: Schema + Kanten + ECHTE LLM-Calls (AGENTS.md Guardrail 7).

Schema/Kanten-Tests sind reine Logik (echter Code). Die Extraktions-/Routing-Tests
laufen gegen das **echte** Endpoint (`_live.call`); keine Fakes/skripteten Antworten.
"""

import json

import gaama_extract as ge
import pytest
from _live import call


# ------------------------------------------------------ reine Schema-Logik
def test_normalize_edge_type():
    assert ge.normalize_edge_type("has concept") == "HAS_CONCEPT"
    assert ge.normalize_edge_type("next") == "NEXT"
    assert ge.normalize_edge_type("BOGUS") == "DERIVED_FROM"  # Fallback (wörtlich Repo)
    assert ge.normalize_edge_type(None) == "DERIVED_FROM"


def test_strip_json_block():
    assert ge._strip_json_block('```json\n{"a":1}\n```') == '{"a":1}'
    assert ge._strip_json_block('```\n{"a":1}\n```') == '{"a":1}'
    assert ge._strip_json_block('{"a":1}') == '{"a":1}'


def test_build_edges_gueltig_und_ungueltig():
    ids = ["a", "b", "c"]
    specs = [
        {"source_index": 0, "target_index": 1, "edge_type": "NEXT"},
        {"source_index": 1, "target_index": 2, "edge_type": "bogus"},  # -> DERIVED_FROM
        {"source_index": 0, "target_index": 0, "edge_type": "NEXT"},  # self-loop -> skip
        {"source_index": 0, "target_index": 9, "edge_type": "NEXT"},  # out of range -> skip
        {"source_index": None, "target_index": 1, "edge_type": "NEXT"},  # None -> skip
    ]
    assert ge.build_edges(ids, specs) == [("a", "b", "NEXT"), ("b", "c", "DERIVED_FROM")]


def test_build_graph_alle_kantentypen():
    episodes = [{"id": "ep1", "text": "A"}, {"id": "ep2", "text": "B"}]
    facts = [{"id": "f1", "fact_text": "F1", "source_episode_ids": ["ep1", "epX"], "concepts": ["c1", "cX"]}]
    concepts = [{"concept_label": "c1", "episode_ids": ["ep1", "epX"]}]
    reflections = [{"id": "r1", "reflection_text": "R1", "source_fact_ids": ["f1", "fX"]}]
    g = ge.build_graph(episodes, facts, concepts, reflections)
    kinds = {n["kind"] for n in g["nodes"]}
    types = {e[2] for e in g["edges"]}
    assert kinds == {"episode", "fact", "concept", "reflection"}
    assert types == {"NEXT", "DERIVED_FROM", "ABOUT_CONCEPT", "HAS_CONCEPT", "DERIVED_FROM_FACT"}
    assert ("ep1", "ep2", "NEXT") in g["edges"]
    assert ("f1", "ep1", "DERIVED_FROM") in g["edges"]
    assert ("f1", "concept:c1", "ABOUT_CONCEPT") in g["edges"]
    assert ("ep1", "concept:c1", "HAS_CONCEPT") in g["edges"]
    assert ("r1", "f1", "DERIVED_FROM_FACT") in g["edges"]
    assert not any("epX" in e or "cX" in e or "fX" in e for e in g["edges"])


def test_build_graph_ohne_ids_erzeugt_fallback():
    g = ge.build_graph(
        [{"id": "ep1", "text": "A"}], [{"fact_text": "F"}], [{"concept_label": "c"}], [{"reflection_text": "R"}]
    )
    ids = {n["id"] for n in g["nodes"]}
    assert "fact-0" in ids and "reflection-0" in ids


def test_load_episodes(tmp_path):
    p = tmp_path / "episodic_graph.json"
    p.write_text(json.dumps({"nodes": {"n0": {"content": "X"}, "n1": {"content": "Y"}}, "edges": {}}), encoding="utf-8")
    eps = ge.load_episodes(p)
    assert [e["id"] for e in eps] == ["n0", "n1"] and eps[0]["text"] == "X"


# --------------------------------------------------- ECHTE LLM-Extraktion
@pytest.mark.network
def test_extract_facts_concepts_real():
    eps = [{"id": "ep1", "text": "The capital of Xylophonia is Zentaria.", "date": "2026-01-01"}]
    out = call(ge.extract_facts_concepts, eps)
    assert isinstance(out["facts"], list) and isinstance(out["concepts"], list)


@pytest.mark.network
def test_extract_reflections_real():
    facts = [
        {"id": "f1", "fact_text": "The capital of Xylophonia is Zentaria."},
        {"id": "f2", "fact_text": "Zentaria hosts the annual Xylophonia festival."},
    ]
    out = call(ge.extract_reflections, facts)
    assert isinstance(out, list)


# --------------------------------------------------- ECHTES Routing / Persistenz
@pytest.mark.network
def test_route_extracted_facts_real():
    facts = [{"fact_text": "The capital of Xylophonia is Zentaria."}]
    out = call(ge.route_extracted_facts, facts)  # realer fast_write_router.classify
    assert out[0]["class"] in {"non-write", "write-new", "write-update", "uncertain"}


@pytest.mark.network
def test_persist_extracted_facts_real(tmp_path):
    facts = [
        {"fact_text": "The capital of Xylophonia is Zentaria.", "source": "user", "verified": True},
        {"fact_text": "Fakt B", "source": "web:untrusted", "verified": True},  # §9.2c: nicht vertrauenswürdig
        {"fact_text": "Fakt C", "source": "user", "verified": False},  # §9.2c: nicht verifiziert
    ]
    out = call(
        ge.persist_extracted_facts,
        facts,
        structured_dir=tmp_path / "s",
        tier3_dir=tmp_path / "t3",
        results_dir=tmp_path / "r",  # kein Write ins echte ergebnisse/rekursion
    )
    assert out[0]["admitted"] is True and out[1]["admitted"] is False and out[2]["admitted"] is False
