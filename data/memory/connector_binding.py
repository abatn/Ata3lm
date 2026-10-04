#!/usr/bin/env python3
"""Connector-Binding (SHACL/W3C): liest `connectors/*.md` und ruft den genannten Prozess auf.

Quellen (verifiziert):
  - **W3C SHACL** (Shapes Constraint Language, Rec. 2017): https://www.w3.org/TR/shacl/
    — „a language for validating RDF graphs against a set of conditions … shapes".
  - **AGENTS.md §5** (Wie eine Wolke): Connectoren als revidierbare Zuordnung.
  - Zuordnung Connector → Prozess: `ergebnisse/connector-prozess.md` (Auftrag) + `## Prozess` in
    jeder `connectors/*.md`.

Lab-Prinzip §6: keine Erfindung — die Zuordnung steht im Repo; SHACL prüft die Invariante
(„jeder Connector hat ≥ 1 Prozess", `sh:minCount 1`). **§11:** MCP-Record in-process,
Fallback auf lokale Memory.
"""

from __future__ import annotations

import asyncio
import re
from pathlib import Path

import bias_monitor
import evaluator_version
import fast_write_router
import ingestion_hook
import lru_cache
import pipeline
import reflective_agent
import shared_memory
import trust

ROOT = Path(__file__).resolve().parents[2]  # repo-relativ (CI-tauglich)
CONNECTORS = ROOT / "connectors"

# SHACL-Shape (W3C): „jeder Connector hat ≥ 1 Prozess" (minCount 1).
CONNECTOR_SHAPE = """
@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix ex: <http://example.org/connector#> .
ex:ConnectorShape a sh:NodeShape ;
  sh:targetClass ex:Connector ;
  sh:property [ sh:path ex:process ; sh:minCount 1 ; sh:nodeKind sh:IRI ] .
"""


def parse_connector(path: Path) -> dict:
    """`connectors/*.md` → {name, process, phase} (aus `## Prozess (Aufruf)`)."""
    path = Path(path)
    text = path.read_text(encoding="utf-8")
    m = re.search(r"Dieser Connector bedient:\s*`([^`]+)`\s*—\s*(.+)", text)
    return {"name": path.stem, "process": m.group(1) if m else None, "phase": m.group(2).strip() if m else ""}


def validate_connector(spec: dict) -> dict:
    """SHACL-Validierung der Invariante `sh:minCount 1` auf `ex:process` (echte pyshacl-Engine)."""
    import rdflib
    from shacl_inferenz import validate

    ttl = f"@prefix ex: <http://example.org/connector#> .\nex:{spec['name']} a ex:Connector"
    if spec["process"]:
        ttl += f" ; ex:process ex:{re.sub(r'[^A-Za-z0-9_]', '_', spec['process'])}"
    ttl += " ."
    graph = rdflib.Graph()
    graph.parse(data=ttl, format="turtle")
    shapes = rdflib.Graph()
    shapes.parse(data=CONNECTOR_SHAPE, format="turtle")
    conforms, _ = validate(graph, shapes)
    return {"conforms": conforms, "shape": "ex:ConnectorShape (sh:minCount 1)"}


# --- Prozess-Executoren (echte Funktionen, offline) ---
def _p_pipeline(ctx: dict) -> dict:
    return pipeline.route_and_store(
        question=ctx["question"],
        fact=ctx["fact"],
        correct=ctx["correct"],
        classify_fn=ctx["classify_fn"],
        mandate_obj=ctx["mandate_obj"],
        now=ctx["now"],
        structured_dir=ctx["structured_dir"],
        tier3_dir=ctx["tier3_dir"],
    )


def _p_reflective(ctx: dict) -> dict:
    return reflective_agent.simulate_lifecycle()


def _p_bias(ctx: dict) -> dict:
    return bias_monitor.BiasDriftMonitor(baseline={"a": 0.5, "b": 0.5}, tau=0.1).observe({"a": 0.6, "b": 0.4}, step=1)


def _p_trust(ctx: dict) -> dict:
    return {"minimized": trust.PIIFilter().minimize(ctx["fact"])}


def _p_shared(ctx: dict) -> dict:
    st = shared_memory.SharedTier()
    st.write("agent", "connector-binding", "v")
    return st.sync()


def _p_evaluator(ctx: dict) -> dict:
    return {"posterior": evaluator_version.posterior_mean(3, 1)}


def _p_fwr(ctx: dict) -> dict:
    cls, gate = fast_write_router._decide(False, True, True)
    return {"class": cls, "gate": gate}


def _p_lru(ctx: dict) -> dict:
    return lru_cache.spread_activation_scores(ctx["question"], [("a", "alpha"), ("b", "beta")], [])


def _p_ingestion(ctx: dict) -> dict:
    return {"entities": ingestion_hook.resolve_entities(ctx["fact"])}


# Connector → Prozess (Auftrag; Quelle: ergebnisse/connector-prozess.md).
PROCESS_REGISTRY = {
    "pipeline.py": _p_pipeline,
    "reflective_agent.py": _p_reflective,
    "bias_monitor.py": _p_bias,
    "trust.py": _p_trust,
    "shared_memory.py": _p_shared,
    "evaluator_version.py": _p_evaluator,
    "fast_write_router.py": _p_fwr,
    "lru_cache.py": _p_lru,
    "ingestion_hook.py": _p_ingestion,
}


def _record_binding(spec: dict, result: dict) -> dict:
    """Schreibt den Bindungs-Nachweis via MCP (in-process FastMCP); §11-Fallback lokal."""
    content = f"# Connector-Bindung: {spec['name']}\n\nProzess: `{spec['process']}`\nPhase: {spec['phase']}\n"
    key = f"binding-{spec['name']}.md"
    try:
        import mcp_memory_server

        server = mcp_memory_server.build_server()
        asyncio.run(
            server.call_tool("memory.write", {"scope": "tier2", "key": key, "content": content, "trust": "green"})
        )
        return {"via": "mcp", "key": key}
    except Exception as exc:  # noqa: BLE001 - §11-Fallback
        out = Path(result.get("fallback_dir", "/tmp")) / key
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(content, encoding="utf-8")
        return {"via": "local-fallback", "reason": str(exc)[:80], "key": key}


def bind(connector_path: Path, ctx: dict, *, registry: dict | None = None, mcp_record: bool = True) -> dict:
    """Bindet EINEN Connector: parse → SHACL-validieren → Prozess ausführen → MCP-Record."""
    spec = parse_connector(connector_path)
    reg = PROCESS_REGISTRY if registry is None else registry
    validation = validate_connector(spec)
    fn = reg.get(spec["process"])
    if fn is None:
        executed = {"executed": False, "reason": f"kein Executor für {spec['process']!r}"}
    else:
        executed = {"executed": True, "result": fn(ctx)}
    recorded = _record_binding(spec, executed) if mcp_record else None
    return {
        "connector": spec["name"],
        "process": spec["process"],
        "phase": spec["phase"],
        "shacl": validation,
        **executed,
        "recorded": recorded,
    }


def bind_all(ctx: dict, *, registry: dict | None = None, mcp_record: bool = True) -> list:
    """Bindet alle `connectors/*.md` (17)."""
    return [bind(p, ctx, registry=registry, mcp_record=mcp_record) for p in sorted(CONNECTORS.glob("*.md"))]


if __name__ == "__main__":  # pragma: no cover - CLI
    import json

    import mandate

    ctx = {
        "question": "Beispiel?",
        "fact": "Kontakt: max@example.com, Version 2.",
        "correct": "Version 2.",
        "classify_fn": lambda q, f, c: {"class": "write-new"},
        "mandate_obj": mandate.Mandate(
            mandate_id="connector-binding",
            principal="Batnini",
            agent="knowledge-agent",
            actions=frozenset({"write:memory"}),
            resources=frozenset({"data/memory"}),
            amount_limit=1.0,
            max_uses=10_000,
            valid_from=0.0,
            valid_until=1e12,
            approval_threshold=0.5,
        ),
        "now": 100.0,
        "structured_dir": "/tmp/connector-binding/structured",
        "tier3_dir": "/tmp/connector-binding/tier3",
    }
    out = bind(ROOT / "connectors/htac-agentdice.md", ctx)
    print(json.dumps(out, ensure_ascii=False, indent=2))
