"""Ladepfad tier2 → tier3: GAAMA-Hybrid-Retrieval + Validation-Gated Consolidation.

Quellen: GAAMA (arXiv:2603.27910) · Kairos „Validation-Gated Hebbian Learning"
(NeurIPS 2025, ceur-ws.org/Vol-4162/paper4.pdf). Offline, kein Netz.
Graph-Kanten kommen aus `gaama_extract` (Extraktion) – KEINE erfundenen Kanten.
"""

import lru_cache as lru

INDEX = """# Tier 2 – Concept Index

| Konzept | Ort (Datei) | Tier |
|---|---|---|
| 8 Stufen | ontology.md | 1 |
| 5 Phasen | ontology.md | 1 |
| Identität | identity.md | 1 |
| Kernbeziehungen | core-relations.md | 1 |
| Fast Write Routing | connector.md | 1 |
"""


def _index(tmp_path):
    p = tmp_path / "concept-index.md"
    p.write_text(INDEX, encoding="utf-8")
    return p


def test_parse_concept_index_5_konzepte(tmp_path):
    concepts = lru.parse_concept_index(_index(tmp_path))
    assert [c["concept"] for c in concepts] == [
        "8 Stufen",
        "5 Phasen",
        "Identität",
        "Kernbeziehungen",
        "Fast Write Routing",
    ]


def test_hybrid_scores_mit_expliziten_kanten():
    items = [("ep1", "8 stufen lifecycle"), ("ep2", "5 phasen"), ("fact1", "8 stufen sind lifecycle-stufen")]
    edges = [("ep1", "ep2", "NEXT"), ("fact1", "ep1", "DERIVED_FROM")]
    ranked = lru.hybrid_scores("8 stufen", items, edges)
    assert len(ranked) == 3 and ranked[0][0] in {"ep1", "fact1"}
    assert all(isinstance(s, float) for _, s in ranked)


def test_ppr_propagiert_ueber_kante():
    nodes = ["A", "B", "C"]
    edges = [("A", "B", "ABOUT_CONCEPT")]
    ppr = lru.edge_type_aware_ppr(nodes, edges, {"A": 1.0})
    assert ppr["B"] > ppr["C"]


def test_ppr_ignoriert_unbekannte_endpunkte():
    ppr = lru.edge_type_aware_ppr(["A"], [("A", "X", "NEXT")], {"A": 1.0})
    assert set(ppr) == {"A"}


def test_ppr_ohne_break_iteriert_zu_ende():
    ppr = lru.edge_type_aware_ppr(["A", "B"], [("A", "B", "NEXT")], {"A": 1.0}, iters=1)
    assert set(ppr) == {"A", "B"}


def test_fill_from_graph_laedt_topk():
    wm = lru.WorkingMemory(capacity=15)
    items = [("ep1", "8 stufen"), ("ep2", "5 phasen"), ("fact1", "fast write routing")]
    edges = [("ep1", "ep2", "NEXT")]
    loaded = wm.fill_from_graph("8 stufen phasen", items, edges, top_k=3)
    assert len(loaded) == 3
    assert all(e["concept"] in wm.items for e in loaded)
    assert all(v["value"].startswith("gaama-graph") for v in wm.items.values())


def test_fill_from_graph_min_score_filtert():
    wm = lru.WorkingMemory(capacity=15)
    loaded = wm.fill_from_graph("x", [("a", "8 stufen")], [], top_k=1, min_score=1.1)
    assert loaded == [] and len(wm.items) == 0


def test_validation_gate_quality_und_novelty_orthogonal():
    ok = lru.validation_gate({"logical": 0.9, "grounding": 0.8, "novelty": 0.1, "alignment": 0.7})
    assert ok["consolidate"] is True and ok["novelty"] == 0.1  # novelty blockiert NICHT
    bad = lru.validation_gate({"logical": 0.9, "grounding": 0.5, "novelty": 0.9, "alignment": 0.7})
    assert bad["consolidate"] is False and bad["quality"]["grounding"] == 0.5


def test_consolidate_edges_gated():
    wm = lru.WorkingMemory(capacity=15)
    wm.store("A", "x")
    wm.store("B", "y")
    edges = [("A", "B", "ABOUT_CONCEPT")]
    fail = wm.consolidate_edges(edges, {"logical": 0.9, "grounding": 0.2, "alignment": 0.9})
    assert fail["consolidated"] is False and wm.items["A"]["edge_weight"] == 1.0
    ok = wm.consolidate_edges(edges, {"logical": 0.9, "grounding": 0.9, "alignment": 0.9})
    assert ok["consolidated"] is True and set(ok["strengthened"]) == {"A", "B"}
    assert wm.items["A"]["edge_weight"] == 1.1 and wm.items["B"]["edge_weight"] == 1.1


def test_consolidate_edges_key_nicht_in_wm():
    wm = lru.WorkingMemory(capacity=15)
    wm.store("A", "x")
    r = wm.consolidate_edges([("A", "Z", "ABOUT_CONCEPT")], {"logical": 0.9, "grounding": 0.9, "alignment": 0.9})
    assert r["consolidated"] is True and r["strengthened"] == ["A"]


def test_hub_dampening_grad_ueber_schwelle():
    nodes = ["hub"] + [f"n{i}" for i in range(51)]
    edges = [("hub", f"n{i}", "NEXT") for i in range(51)]  # Grad 51 > 50
    ppr = lru.edge_type_aware_ppr(nodes, edges, {"hub": 1.0})
    assert set(ppr) == set(nodes)


def test_degree_correction_an_und_aus():
    nodes, edges = ["A", "B"], [("A", "B", "NEXT")]
    a = lru.edge_type_aware_ppr(nodes, edges, {"A": 1.0}, degree_correction=True)
    b = lru.edge_type_aware_ppr(nodes, edges, {"A": 1.0}, degree_correction=False)
    assert set(a) == set(b) == {"A", "B"}


def test_expand_subgraph_tiefe_und_ende():
    edges = [("A", "B", "NEXT"), ("B", "C", "NEXT"), ("C", "D", "NEXT")]
    sub = lru.expand_subgraph(edges, ["A"], depth=2)
    assert ("A", "B", "NEXT") in sub and ("B", "C", "NEXT") in sub and ("C", "D", "NEXT") not in sub
    assert lru.expand_subgraph(edges, ["D"], depth=2) == []


def test_bidirectional():
    assert lru._bidirectional([("A", "B", "NEXT")]) == [("A", "B", "NEXT"), ("B", "A", "NEXT")]


def test_hub_dampening_deaktiviert():
    ppr = lru.edge_type_aware_ppr(["A", "B"], [("A", "B", "NEXT")], {"A": 1.0}, hub_dampening_threshold=0)
    assert set(ppr) == {"A", "B"}


def test_fill_from_tier2_5_konzepte(tmp_path):
    """Ladepfad aus tier2-index/concept-index.md: 5 Konzepte -> Tier3."""
    wm = lru.WorkingMemory(capacity=15)
    loaded = wm.fill_from_tier2("8 stufen phasen identität", concepts_path=_index(tmp_path), top_k=5)
    assert len(loaded) == 5
    assert all(e["concept"] in wm.items for e in loaded)
    assert {e["concept"] for e in loaded} == {
        "8 Stufen",
        "5 Phasen",
        "Identität",
        "Kernbeziehungen",
        "Fast Write Routing",
    }
