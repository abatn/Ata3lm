"""Echte SHACL-Inferenz-Pipeline (rdflib + pyshacl) — Zeitintervall-Beispiel.

Quelle: Robaldo & Batsakis, Semantic Web Journal (swj3959). Guardrail 7: echte Engine.
"""

import sys
from pathlib import Path

import rdflib
import shacl_inferenz as si
from pyshacl.rules import RULES_ITERATE_LIMIT


def test_default_max_rounds_ist_offizieller_pyshacl_wert():
    assert si.DEFAULT_MAX_ROUNDS == RULES_ITERATE_LIMIT == 100


DATA = """
@prefix ex: <http://example.org/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
# i1: gültig (Beginn < Ende)
ex:i1 ex:hasBeginning ex:b1 ; ex:hasEnd ex:e1 .
ex:b1 ex:inXSDDateTime "2024-05-01T00:00:00"^^xsd:dateTime .
ex:e1 ex:inXSDDateTime "2024-05-10T00:00:00"^^xsd:dateTime .
# i2: ungültig (Ende < Beginn) — im expliziten Graphen NICHT sichtbar
ex:i2 ex:hasBeginning ex:b2 ; ex:hasEnd ex:e2 .
ex:b2 ex:inXSDDateTime "2024-05-10T00:00:00"^^xsd:dateTime .
ex:e2 ex:inXSDDateTime "2024-05-01T00:00:00"^^xsd:dateTime .
"""

RULES = [
    {
        "id": "R1",
        "construct": """
        PREFIX ex: <http://example.org/>
        CONSTRUCT { ?i ex:hasNegativeDuration true }
        WHERE {
          ?i ex:hasBeginning ?b ; ex:hasEnd ?e .
          ?b ex:inXSDDateTime ?tb . ?e ex:inXSDDateTime ?te .
          FILTER (?te < ?tb)
        }
        """,
    }
]

SHAPES = """
@prefix ex: <http://example.org/> .
@prefix sh: <http://www.w3.org/ns/shacl#> .
ex:NoNegativeDurationShape a sh:NodeShape ;
  sh:targetSubjectsOf ex:hasNegativeDuration ;
  sh:property [ sh:path ex:hasNegativeDuration ; sh:maxCount 0 ] .
"""


def test_inferenz_macht_invaliditaet_sichtbar():
    explicit = rdflib.Graph()
    explicit.parse(data=DATA, format="turtle")
    shapes = rdflib.Graph()
    shapes.parse(data=SHAPES, format="turtle")

    # 1) Validierung OHNE Inferenz (SHACL allein): erkennt i2 nicht.
    conforms_before, _ = si.validate(explicit, shapes)

    # 2) Inferenz bis Fixpunkt + Validierung auf dem materialisierten Graphen.
    result = si.pipeline(explicit, RULES, shapes)

    assert conforms_before is True
    assert result["conforms"] is False
    assert any(str(t[1]).endswith("hasNegativeDuration") for t in result["graph"])
    assert result["trace"][0]["new"][0]["rule"] == "R1"
    assert "hasNegativeDuration" in result["report"]


def test_transitive_huelle_mehrere_runden():
    g = rdflib.Graph()
    g.parse(
        data="""
        @prefix ex: <http://example.org/> .
        ex:a ex:before ex:b . ex:b ex:before ex:c . ex:c ex:before ex:a .
        """,
        format="turtle",
    )
    rules = [
        {
            "id": "R2",
            "construct": """
            PREFIX ex: <http://example.org/>
            CONSTRUCT { ?a ex:before ?c }
            WHERE { ?a ex:before ?b . ?b ex:before ?c }
            """,
        }
    ]
    g, trace = si.run_rules_to_fixpoint(g, rules, max_rounds=10)
    assert len(trace) >= 2
    ex = "http://example.org/"
    assert (rdflib.URIRef(ex + "a"), rdflib.URIRef(ex + "before"), rdflib.URIRef(ex + "a")) in g


def test_max_rounds_cap():
    g = rdflib.Graph()
    g.parse(
        data="""
        @prefix ex: <http://example.org/> .
        ex:a ex:before ex:b . ex:b ex:before ex:c .
        """,
        format="turtle",
    )
    rules = [
        {
            "id": "R2",
            "construct": """
            PREFIX ex: <http://example.org/>
            CONSTRUCT { ?a ex:before ?c }
            WHERE { ?a ex:before ?b . ?b ex:before ?c }
            """,
        }
    ]
    _, trace = si.run_rules_to_fixpoint(g, rules, max_rounds=1)
    assert len(trace) == 1


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "data" / "memory"))
    test_inferenz_macht_invaliditaet_sichtbar()
    test_transitive_huelle_mehrere_runden()
    print("ok")
