"""MCP-Kontext-Steuerung: TTC-Katalog + Token-Messung + Lazy-Gating.

Quellen (verifiziert, §6):
  - TERSE Tool Catalog (TTC) Spec v1.0 — Zenodo 10.5281/zenodo.19869008:
    kompakte Repräsentation mit den Zusatzfeldern `WHEN` (semantischer Trigger),
    `ERR` (Fehlervertrag), `TAGS` (Retrieval-Taxonomie); gemessen 66,6 % Token-
    Reduktion (1.948 → 650) über 10 MCP-Tools.
  - Tool Attention — arXiv:2604.21816: Dynamic Tool Gating + Lazy Schema Loading
    (Top-k gaten, Schema erst bei Bedarf).
  - Strayspark („How many tools should an MCP server expose?"): Token-Budget bindet
    vor der Tool-Anzahl; 22 Tools = 9.456 Token; ~430 Schema-Token/Tool; char/4-Schätzung.
  - RAG-MCP: Selection Collapse (Tool-Auswahl ~13,62 % bei vollem Katalog).

Lab-Prinzip §6: Format = TTC-Spec; Gating = Tool Attention; Messung = char/4 (Strayspark).
Keine Erfindung: `WHEN/ERR/TAGS` sind im MCP-JSON-Schema nicht enthalten → Defaults aus
dem Referenz-Konverter (TTC) abgeleitet (WHEN=PURPOSE, ERR="unknown", TAGS=Namens-Tokens).
"""

from __future__ import annotations

import json
import re


def count_tokens(text: str) -> int:
    """Token-Schätzung char/4 (Strayspark; tiktoken nicht installiert)."""
    return max(1, len(text or "") // 4)


def _tokens(text: str) -> list:
    return re.findall(r"[a-z0-9]+", (text or "").lower())


def _type_of(schema: dict) -> str:
    t = schema.get("type")
    if isinstance(t, list):
        t = t[0] if t else "any"
    return t or "any"


def mcp_schema_to_ttc(tool: dict) -> str:
    """MCP-JSON-Schema (Tool) → TTC-Block (TTC Spec v1.0)."""
    name = tool.get("name", "tool")
    desc = (tool.get("description") or "").strip().replace("\n", " ")
    params = tool.get("parameters") or tool.get("inputSchema") or {}
    props = params.get("properties", {}) if isinstance(params, dict) else {}
    required = set(params.get("required", []) if isinstance(params, dict) else [])
    in_parts = [f"{p}:{_type_of(s)}" + ("" if p in required else "?") for p, s in props.items()]
    out = tool.get("outputSchema") or tool.get("returns") or "any"
    tags = sorted({t for t in re.split(r"[._]", name) if t})
    lines = [
        f"TOOL {name}",
        f"  PURPOSE: {desc or name}",
        f"  IN: {', '.join(in_parts) if in_parts else '-'}",
        f"  OUT: {out if isinstance(out, str) else 'any'}",
        f"  ERR: {tool.get('err', 'unknown')}",
        f"  WHEN: {tool.get('when', desc or name)}",
        f"  TAGS: {', '.join(tool.get('tags', tags))}",
    ]
    return "\n".join(lines)


def build_catalog(tools: list) -> str:
    """TTC-Katalog aus mehreren MCP-Tools."""
    return "\n\n".join(mcp_schema_to_ttc(t) for t in tools)


def measure(tools: list) -> dict:
    """Token-Messung vor (MCP-JSON-Schema) / nach (TTC) + Reduktion (%)."""
    before = sum(count_tokens(json.dumps(t, ensure_ascii=False)) for t in tools)
    after = count_tokens(build_catalog(tools))
    reduction = round(100.0 * (before - after) / before, 1) if before else 0.0
    return {"tools": len(tools), "tokens_before": before, "tokens_after": after, "reduction_pct": reduction}


def iso_score(query: str, text: str) -> float:
    """Intent-Schema-Overlap (Tool Attention): Bag-of-Words-Cosine (deterministisch)."""
    q, t = _tokens(query), _tokens(text)
    if not q or not t:
        return 0.0
    inter = len(set(q) & set(t))
    return inter / ((len(set(q)) * len(set(t))) ** 0.5)


def lazy_gate(query: str, tools: list, top_k: int = 5) -> list:
    """Dynamic Tool Gating (Tool Attention): nur Top-k relevante Tools laden."""
    scored = [
        (t.get("name", "tool"), iso_score(query, f"{t.get('name', '')} {t.get('description', '')}")) for t in tools
    ]
    return [{"name": n, "score": round(s, 4)} for n, s in sorted(scored, key=lambda kv: -kv[1])[:top_k]]


def top_k_per_stage(tools: list, stages: dict, top_k: int = 5) -> dict:
    """Top-k Tools je Stufe (Auftrag): `stages` = {stage: query}."""
    return {stage: lazy_gate(query, tools, top_k) for stage, query in stages.items()}
