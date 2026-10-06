"""SHACL-Inferenz-Pipeline mit echter Engine: Regeln bis Fixpunkt, dann Validierung.

Quelle (verifiziert, swj3959, S. 5, wörtlich):
    "our approach also iteratively applies SHACL-SPARQL rules until the inferred
     graph reaches closure, prior to validation."
    "programmatically re-executes the SHACL-SPARQL rules until no new triples are
     produced, and then validates the resulting knowledge graph against the SHACL shapes."

Engine: rdflib (SPARQL CONSTRUCT) + pyshacl (SHACL-Shapes). Guardrail 7: echt, keine Simulation.

Iterations-Cap (offiziell, aus der Engine übernommen — NICHT erfunden):
    pyshacl 0.40.1 `RULES_ITERATE_LIMIT = 100` (pyshacl/rules/__init__.py:89).
    Vergleich: TopBraid `shaclinfer -maxiterations` Default 1; Triply `maxIterations`
    Default 0; W3C SHACL 1.2 lässt den Wert implementierungsabhängig ("pre-configured
    maximum iteration count"). W3C SHACL-AF §8.4 definiert nur eine Einzel-Iteration
    ("left to future work"). HuggingFace: kein SHACL-Iterationswert.
"""

from __future__ import annotations

from pyshacl.rules import RULES_ITERATE_LIMIT

# Offizieller pyshacl-Wert (= 100), direkt aus der Engine importiert.
DEFAULT_MAX_ROUNDS = RULES_ITERATE_LIMIT


def run_rules_to_fixpoint(graph, rules, max_rounds: int = DEFAULT_MAX_ROUNDS):
    """Führt SPARQL-CONSTRUCT-Regeln iterativ aus, bis keine neuen Triples entstehen.

    `rules`: Liste von Dicts `{"id": str, "construct": "<SPARQL CONSTRUCT>"}`.
    Rückgabe: `(graph, trace)` mit `trace = [{"round": int, "new": [{"rule","triple"}]}]`.
    """
    trace = []
    for rnd in range(1, max_rounds + 1):
        new = []
        for rule in rules:
            for s, p, o in list(graph.query(rule["construct"])):
                triple = (s, p, o)
                if triple not in graph:
                    graph.add(triple)
                    new.append({"rule": rule["id"], "triple": (str(s), str(p), str(o))})
        trace.append({"round": rnd, "new": new})
        if not new:
            break
    return graph, trace


def validate(graph, shapes_graph):
    """Validiert den (materialisierten) Graphen mit pyshacl gegen die Shapes."""
    from pyshacl import validate as _validate

    conforms, _, report = _validate(graph, shacl_graph=shapes_graph, inference="none")
    return conforms, report


def pipeline(data_graph, rules, shapes_graph, max_rounds: int = DEFAULT_MAX_ROUNDS):
    """Inferenz (Fixpunkt) → Validierung. Rückgabe: Ergebnis-Dict.

    §6: Erreicht der Fixpunkt die Iterationsgrenze (`max_rounds`) **nicht**, wird die
    Inferenz als **unvollständig** ausgewiesen; `conforms` ist dann nicht belastbar.
    R17: Wurden bei vorhandenen Regeln **keine** Runden ausgeführt (z. B. `max_rounds=0`),
    ist die Inferenz ebenfalls **nicht** belastbar – `conforms_reliable=False`.
    """
    data_graph, trace = run_rules_to_fixpoint(data_graph, rules, max_rounds)
    conforms, report = validate(data_graph, shapes_graph)
    if not rules:
        complete, hint = True, None  # nichts zu inferieren ⇒ Validierung belastbar
    elif not trace:
        complete = False  # R17: Regeln vorhanden, aber keine Runde ausgeführt
        hint = "Keine Inferenzrunde ausgeführt (max_rounds=0) – Fixpunkt NICHT garantiert, conforms nicht belastbar"
    elif trace[-1]["new"]:
        complete = False
        hint = "Iterationsgrenze max_rounds erreicht – Fixpunkt NICHT garantiert, conforms nicht belastbar"
    else:
        complete, hint = True, None
    return {
        "conforms": conforms,
        "report": report,
        "trace": trace,
        "graph": data_graph,
        "inference_status": "vollständig" if complete else "unvollständig",
        "inference_complete": complete,
        "conforms_reliable": complete,
        "hint": hint,
    }
