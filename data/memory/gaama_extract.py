#!/usr/bin/env python3
"""GAAMA-Extraktion (paper-konform): Episoden -> Facts/Concepts/Reflections + typisierte Kanten.

Quellen (verifiziert 2026-10-03, siehe ergebnisse/gaama-schema.md):
  - GAAMA arXiv:2603.27910 – Table 1 (4 Knoten-, 5 Kantentypen), Table 2 (Kantengewichte).
  - Repo https://github.com/swarna-kpaul/gaama – `services/graph_edges.py`
    (`build_edges_from_nodes`, `_normalize_edge_type`), `services/llm_extractors.py`,
    `prompts/fact_generation.md`, `prompts/reflection_generation.md`.

Lab-Prinzip §6: Schema wörtlich aus der Quelle; der LLM-Aufruf ist **injizierbar**
(`llm_fn`), damit Tests offline laufen. Keine erfundenen Kanten: alle Kanten stammen
aus Extraktion (EdgeSpecs) — nicht aus Datei-Orten.
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]  # repo-relativ (S6, CI-tauglich)

# GAAMA Table 1 (wörtlich: 5 Kantentypen) + Table 2 (Gewichte)
NODE_KINDS = ("episode", "fact", "reflection", "concept")
EDGE_TYPES = ("NEXT", "DERIVED_FROM", "DERIVED_FROM_FACT", "HAS_CONCEPT", "ABOUT_CONCEPT")
EDGE_WEIGHTS = {
    "NEXT": 0.8,
    "DERIVED_FROM": 0.8,
    "DERIVED_FROM_FACT": 0.5,
    "HAS_CONCEPT": 0.8,
    "ABOUT_CONCEPT": 0.8,
}

# Prompts (Schema + Regeln aus dem GAAMA-Repo, prompts/fact_generation.md bzw.
# prompts/reflection_generation.md; Platzhalter werden zur Laufzeit gefüllt).
FACT_PROMPT = """# Extract facts and concepts from conversation episodes
You are a knowledge extraction system. Extract NEW factual claims AND topic concepts.
Rules (facts): single atomic claim; do not duplicate existing facts; resolve relative
dates to absolute dates; do not extract events as facts; each fact lists its concepts.
Rules (concepts): short topic labels (2-5 words, snake_case); no person names, generic
words, adjectives or dates; reuse existing concepts; 1-3 concepts per episode; each
concept linked to the episode IDs it appears in.
Output JSON only, no markdown fences:
{"facts":[{"fact_text":str,"belief":float,"source_episode_ids":[str],"concepts":[str]}],
 "concepts":[{"concept_label":str,"episode_ids":[str]}]}
## Existing facts (do NOT duplicate)
{{existing_facts}}
## Existing concepts (reuse when applicable)
{{existing_concepts}}
## Related older episodes (context)
{{related_episodes}}
## New conversation episodes (extract from these)
{{new_episodes}}"""

REFLECTION_PROMPT = """# Generate new reflections from facts
A reflection is a generalized insight/preference/lesson emerging from MULTIPLE facts.
Rules: synthesize from multiple facts; do not duplicate; stand alone; may return zero.
Output JSON only, no markdown fences:
{"reflections":[{"reflection_text":str,"belief":float,"source_fact_ids":[str]}]}
## Existing reflections (do NOT duplicate)
{{existing_reflections}}
## Related existing facts (context)
{{related_facts}}
## New facts (generate reflections from these)
{{new_facts}}"""


def normalize_edge_type(raw: str) -> str:
    """Unbekannter Typ -> `DERIVED_FROM` (wörtlich `graph_edges._normalize_edge_type`)."""
    v = (raw or "").strip().upper().replace("-", "_").replace(" ", "_")
    return v if v in EDGE_TYPES else "DERIVED_FROM"


def _strip_json_block(text: str) -> str:
    """Markdown-Fences um JSON entfernen (wörtlich `llm_extractors._strip_json_block`)."""
    text = (text or "").strip()
    for pattern in (r"^```(?:json)?\s*\n?(.*?)\n?```\s*$", r"^```\s*\n?(.*?)\n?```\s*$"):
        m = re.search(pattern, text, re.DOTALL)
        if m:
            return m.group(1).strip()
    return text


def _default_llm(prompt: str, max_tokens: int = 8000) -> str:  # pragma: no cover - nur Netzbetrieb
    """Echter LLM-Aufruf (Endpoint aus der Umgebung, wie FWR). Tests nutzen `llm_fn`."""
    from openai import OpenAI

    client = OpenAI(
        api_key=os.environ.get("OPENAI_API_KEY", ""),
        base_url=os.environ.get("OPENAI_BASE_URL", "https://integrate.api.nvidia.com/v1"),
    )
    r = client.chat.completions.create(
        model=os.environ.get("GAAMA_EXTRACT_MODEL", "nvidia/nemotron-3-ultra-550b-a55b"),
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens,
        temperature=0.0,
    )
    msg = r.choices[0].message
    return (msg.content or getattr(msg, "reasoning_content", None) or "").strip()


def build_edges(node_ids: list, edge_specs: list) -> list:
    """EdgeSpecs (source_index,target_index,edge_type) -> [(src,dst,type)] (GAAMA).

    Wörtlich `graph_edges.build_edges_from_nodes`: ungültige Indizes/self-loops
    werden verworfen; unbekannter Typ -> `DERIVED_FROM`.
    """
    out = []
    n = len(node_ids)
    for spec in edge_specs or []:
        s, t = spec.get("source_index"), spec.get("target_index")
        if s is None or t is None or not (0 <= s < n) or not (0 <= t < n) or s == t:
            continue
        out.append((node_ids[s], node_ids[t], normalize_edge_type(spec.get("edge_type", ""))))
    return out


def extract_facts_concepts(episodes: list, llm_fn=None) -> dict:
    """Episoden -> {"facts":[...], "concepts":[...]} (GAAMA Step 2)."""
    eps_text = "\n".join(f"[{e['id']}] [{e.get('date', '')}] {e['text']}" for e in episodes) or "(none)"
    prompt = (
        FACT_PROMPT.replace("{{existing_facts}}", "(none)")
        .replace("{{existing_concepts}}", "(none)")
        .replace("{{related_episodes}}", "(none)")
        .replace("{{new_episodes}}", eps_text)
    )
    raw = (llm_fn or _default_llm)(prompt)
    data = json.loads(_strip_json_block(raw) or "{}")
    return {"facts": data.get("facts", []), "concepts": data.get("concepts", [])}


def extract_reflections(facts: list, llm_fn=None) -> list:
    """Facts -> Reflections (GAAMA Step 3)."""
    facts_text = "\n".join(f"[{f.get('id', '')}] {f.get('fact_text', '')}" for f in facts) or "(none)"
    prompt = (
        REFLECTION_PROMPT.replace("{{existing_reflections}}", "(none)")
        .replace("{{related_facts}}", "(none)")
        .replace("{{new_facts}}", facts_text)
    )
    raw = (llm_fn or _default_llm)(prompt)
    data = json.loads(_strip_json_block(raw) or "{}")
    return data.get("reflections", [])


def build_graph(episodes: list, facts: list, concepts: list, reflections: list) -> dict:
    """GAAMA-Graph: Knoten + Kanten (NEXT/DERIVED_FROM/HAS_CONCEPT/ABOUT_CONCEPT/DERIVED_FROM_FACT).

    Kanten entstehen AUSSCHLIESSLICH aus Extraktion (Quell-IDs) – keine Erfindung.
    """
    nodes = [{"id": e["id"], "kind": "episode", "text": e["text"]} for e in episodes]
    for i, f in enumerate(facts):
        nodes.append({"id": f.get("id") or f"fact-{i}", "kind": "fact", "text": f.get("fact_text", "")})
    for c in concepts:
        nodes.append(
            {"id": f"concept:{c.get('concept_label', '')}", "kind": "concept", "text": c.get("concept_label", "")}
        )
    for i, r in enumerate(reflections):
        nodes.append(
            {"id": r.get("id") or f"reflection-{i}", "kind": "reflection", "text": r.get("reflection_text", "")}
        )
    ids = {n["id"] for n in nodes}
    edges = []
    ep_ids = [e["id"] for e in episodes]
    for a, b in zip(ep_ids, ep_ids[1:]):
        edges.append((a, b, "NEXT"))
    for i, f in enumerate(facts):
        fid = f.get("id") or f"fact-{i}"
        for ep in f.get("source_episode_ids", []):
            if ep in ids:
                edges.append((fid, ep, "DERIVED_FROM"))
        for cl in f.get("concepts", []):
            cid = f"concept:{cl}"
            if cid in ids:
                edges.append((fid, cid, "ABOUT_CONCEPT"))
    for c in concepts:
        cid = f"concept:{c.get('concept_label', '')}"
        for ep in c.get("episode_ids", []):
            if ep in ids and cid in ids:
                edges.append((ep, cid, "HAS_CONCEPT"))
    for i, r in enumerate(reflections):
        rid = r.get("id") or f"reflection-{i}"
        for f_id in r.get("source_fact_ids", []):
            if rid in ids and f_id in ids:
                edges.append((rid, f_id, "DERIVED_FROM_FACT"))
    return {"nodes": nodes, "edges": edges}


def load_episodes(path=None) -> list:
    """Episoden aus `episodic_graph.json` (verbatim content) als GAAMA-Episode-Knoten."""
    path = Path(path or (ROOT / "data/memory/tier1-base/episodic_graph.json"))
    data = json.loads(path.read_text(encoding="utf-8"))
    return [
        {"id": nid, "kind": "episode", "text": (n.get("content") or ""), "date": ""}
        for nid, n in data.get("nodes", {}).items()
    ]


def route_extracted_facts(facts: list, classify_fn=None) -> list:
    """§10.1: jeder extrahierte Fact durch den **Fast Write Router** (erste Instanz).

    `classify_fn(fact) -> {"class", "gate"}` (injizierbar, offline testbar).
    Default (nur Netzbetrieb) nutzt `fast_write_router.classify` mit
    `question = fact["question"] | fact_text`, `fact = fact_text`,
    `correct = fact["correct"] | fact_text` — die Ableitung von question/correct
    ist **Auftrag** (nicht Paper-wörtlich).
    """
    classify_fn = classify_fn or _default_fact_classify
    out = []
    for f in facts:
        r = classify_fn(f)
        out.append({"fact": f.get("fact_text", ""), "class": r.get("class", "uncertain"), "gate": r.get("gate", "ask")})
    return out


def _default_fact_classify(fact: dict) -> dict:  # pragma: no cover - nur Netzbetrieb
    import fast_write_router

    text = fact.get("fact_text", "")
    return fast_write_router.classify(fact.get("question") or text, text, fact.get("correct") or text)


def persist_extracted_facts(
    facts: list,
    *,
    classify_fn=None,
    guard=None,
    structured_dir,
    tier3_dir,
    tier1_dir=None,
    results_dir=None,
    now: float = 0.0,
    write_fn=None,
) -> list:
    """Persistenz-Kette für extrahierte Facts: **§9.2c → §9.2a → §10.1 → Write**.

    1. §9.2c: `trust.PoisoningGuard.admit` — nur **trusted origin UND verified**.
    2. §9.2a: `trust.PIIFilter.minimize` (PII entfernen).
    3. §10.1: `route_extracted_facts` (Fast Write Router).
    4. Write: `fast_write_router.apply_write_action` (injizierbar via `write_fn`).
    """
    import trust

    guard = guard or trust.PoisoningGuard()
    pii = trust.PIIFilter()
    if write_fn is None:  # pragma: no cover - nur Netzbetrieb
        import fast_write_router

        write_fn = fast_write_router.apply_write_action
    out = []
    for f in facts:
        adm = guard.admit(f)
        if not adm["admitted"]:
            out.append({"fact": f.get("fact_text", ""), "admitted": False, "reason": adm["reason"]})
            continue
        text = pii.minimize(f.get("fact_text", ""))
        routed = route_extracted_facts([{**f, "fact_text": text}], classify_fn)[0]
        written = write_fn(
            routed["class"],
            question=text,
            fact=text,
            structured_dir=structured_dir,
            tier3_dir=tier3_dir,
            tier1_dir=tier1_dir,
            results_dir=results_dir,
            now=now,
        )
        out.append(
            {
                "fact": text,
                "admitted": True,
                "class": routed["class"],
                "gate": routed["gate"],
                "written": written.get("written", []),
            }
        )
    return out
