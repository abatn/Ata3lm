"""Ingestion-Hook (data/memory/ingestion_hook.py) – Gate · Privacy · Graph · Enrichment.

Kein Netz: der optionale GLiNER-Pfad wird mit einem Fake-Modell geprüft, das
Log wird auf `tmp_path` umgebogen (kein Repo-Schreibzugriff).
"""
import asyncio
import json
import sys
import types

import ingestion_hook as ih


# --------------------------------------------------------------- PrivacyFilter
def test_privacy_scan_private_tag_und_secrets():
    p = ih.PrivacyFilter()
    assert p.scan("ok text") == (True, "ok")
    assert p.scan("x <private>geheim</private> y")[0] is False
    assert "private-Tag" in p.scan("x <private>geheim</private> y")[1]
    for probe in ["api_key = ABCDEFGH12345678", "sk-proj-ABCDEFGHIJKLMNOPQRSTUVWX",
                  "ghp_ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
                  "AKIAIOSFODNN7EXAMPLE",
                  "Bearer abcdefghijklmnopqrstuvwxyz123456",
                  "postgres://user:pw@host:5432/db"]:
        clean, why = p.scan(probe)
        assert clean is False and "Secret-Muster" in why


def test_privacy_redact_und_eigene_patterns():
    p = ih.PrivacyFilter()
    out = p.redact("Key sk-proj-ABCDEFGHIJKLMNOPQRSTUVWX und <private>X</private>")
    assert "sk-proj" not in out and "[REDACTED:secret]" in out
    assert "[REDACTED:private]" in out
    assert ih.PrivacyFilter(patterns=[]).scan("sk-proj-ABCDEFGHIJKLMNOPQRSTUVWX") == (True, "ok")


# --------------------------------------------------------------- EncodingGate
def test_gate_alle_ablehnungsgruende():
    g = ih.EncodingGate()
    assert g.check("text" * 5, "unbekannt", 1.0).reason.startswith("Typ")
    assert "zu kurz" in g.check("kurz", "prompt", 1.0).reason
    assert "zu lang" in g.check("x" * 9000, "prompt", 1.0).reason
    assert "Quellvertrauen" in g.check("lang genug hier", "prompt", 0.1).reason
    assert g.check("Mein Key: sk-proj-ABCDEFGHIJKLMNOPQRSTUVWX", "prompt", 1.0).reason.startswith("Privacy")
    ok = g.check("Der Knowledge-Agent nutzt Fast Write Routing.", "prompt", 0.9)
    assert ok.accepted is True and ok.reason == "ok"
    custom = ih.EncodingGate(allowed={"note"}, privacy=ih.PrivacyFilter(patterns=[]))
    assert custom.check("lang genug hier", "note", 1.0).accepted is True


# ---------------------------------------------------------- Entity-Resolution
def test_gliner_available_true_und_false(monkeypatch):
    monkeypatch.setitem(sys.modules, "gliner", types.ModuleType("gliner"))
    assert ih.gliner_available() is True
    monkeypatch.setitem(sys.modules, "gliner", None)      # import -> ImportError
    assert ih.gliner_available() is False


def test_get_gliner_laedt_einmal(monkeypatch):
    calls = []

    class FakeGLiNER:
        @staticmethod
        def from_pretrained(name):
            calls.append(name)
            return {"model": name}

    fake = types.ModuleType("gliner")
    fake.GLiNER = FakeGLiNER
    monkeypatch.setitem(sys.modules, "gliner", fake)
    monkeypatch.setattr(ih, "_GLINER", None)
    first = ih._get_gliner()
    assert first == {"model": "urchade/gliner_multi-v2.1"}
    assert ih._get_gliner() is first and len(calls) == 1   # nur einmal geladen


def test_resolve_entities_regelbasiert_und_sortiert():
    text = "Der Knowledge-Agent nutzt Fast Write Routing im Konstrukt (Stufe Handeln)."
    ents = ih.resolve_entities(text, backend="rules")
    assert ih.resolve_entities(text, backend="rules") == ents          # reproduzierbar
    types_ = {e["entity_type"] for e in ents}
    assert {"Concept", "Phase", "Stage"} <= types_
    assert all(e["backend"] == "rules" and e["confidence"] == 1.0 for e in ents)
    assert ih.resolve_entities("berechne_median", backend="rules")[0]["entity_type"] == "Solver"


def test_resolve_entities_gliner_explizit_ohne_modell(monkeypatch):
    monkeypatch.setattr(ih, "gliner_available", lambda: False)
    assert ih.resolve_entities("egal", backend="gliner") == []


def test_resolve_entities_mit_echtem_gliner_pfad(monkeypatch):
    class Model:
        def predict_entities(self, text, labels, threshold):
            assert threshold == 0.4 and labels == ["Solver", "Concept"]
            return [{"label": "Solver", "text": "berechne_median", "start": 0,
                     "end": 15, "score": 0.98765}]

    monkeypatch.setattr(ih, "gliner_available", lambda: True)
    monkeypatch.setattr(ih, "_get_gliner", lambda: Model())
    out = ih.resolve_entities("berechne_median", labels=["Solver", "Concept"])
    assert out == [{"entity_type": "Solver", "span": "berechne_median", "start": 0,
                    "end": 15, "confidence": 0.9877, "backend": "gliner"}]


# ------------------------------------------------------------- Graph + Konsolidierung
def test_graph_add_node_edge_weight():
    g = ih.MemoryGraph()
    g.add_node("a")
    g.add_node("a", last_access=5.0)
    assert g.nodes["a"] == {"last_access": 0.0, "recent_access": 0}
    g.edges[("a", "p", "b")] = 0.7
    g.edges[("c", "p", "a")] = 0.3
    assert g.edge_weight("a") == 1.0


def test_update_graph_dedup_und_konflikte():
    g = ih.MemoryGraph()
    d = ih.update_graph(g, [{"span": "a"}, "b"], [("a", "supersedes", "b")])
    assert d["added_nodes"] == ["a", "b"] and d["added_edges"] == [("a", "supersedes", "b")]
    assert ih.update_graph(g, [], [("a", "supersedes", "b")])["deduped"] == [("a", "supersedes", "b")]
    d2 = ih.update_graph(g, [], [("b", "supersedes", "a")])            # Gegenrichtung
    assert d2["rejected"][0][1].startswith("Konflikt: Gegenrichtung")
    d3 = ih.update_graph(g, [], [("i", "hasEnd", "2024-05-01")], weights={("i", "hasEnd", "2024-05-01"): 0.4})
    assert d3["added_edges"] and g.edges[("i", "hasEnd", "2024-05-01")] == 0.4
    d4 = ih.update_graph(g, [], [("i", "hasEnd", "2024-06-01")])        # funktionaler Konflikt
    assert d4["rejected"][0][1].startswith("Konflikt: i hasEnd bereits")


def test_consolidate_hub_forgotten_kept():
    g = ih.MemoryGraph()
    now = 1_000_000_000.0
    g.add_node("hub", last_access=now, recent_access=5)
    g.edges[("hub", "e", "n1")] = 0.9
    g.edges[("hub", "e", "n2")] = 0.9
    g.add_node("alt", last_access=now - 100 * 86400, recent_access=0)
    g.edges[("alt", "e", "n9")] = 0.1
    g.add_node("frisch", last_access=now, recent_access=1)
    rep = ih.consolidate(g, now)
    assert [h["node"] for h in rep["hubs"]] == ["hub"]
    assert [f["node"] for f in rep["forgotten"]] == ["alt"]
    assert [k["node"] for k in rep["kept"]] == ["frisch"]


# --------------------------------------------------------------- EnrichmentQueue
def test_worker_verarbeitet_und_ist_fail_soft(tmp_path):
    async def run_ok():
        q = ih.EnrichmentQueue(log_path=tmp_path / "log.jsonl")   # im Loop anlegen!
        assert q.graph.nodes == {}
        task = asyncio.create_task(q.worker())
        await q.submit({"text": "Der Knowledge-Agent nutzt Fast Write Routing."})
        await q.queue.join()
        task.cancel()
        return q

    q = asyncio.run(run_ok())
    assert q.processed[0]["steps"] == ["entity-resolution", "graph-update", "consolidation"]
    assert q.processed[0]["entities"]


def test_worker_fail_soft_bei_fehler(tmp_path, monkeypatch):
    def boom(*a, **k):
        raise RuntimeError("kaputt")

    monkeypatch.setattr(ih, "resolve_entities", boom)

    async def run():
        q = ih.EnrichmentQueue(log_path=tmp_path / "log.jsonl")
        task = asyncio.create_task(q.worker())
        await q.submit({"text": "x"})
        await q.queue.join()
        task.cancel()
        return q

    assert asyncio.run(run()).processed == []     # fail-soft: kein Absturz


# --------------------------------------------------------------- IngestionHook
def test_hook_lifecycle_dedup_und_gate(tmp_path):
    text = "Der Knowledge-Agent nutzt Fast Write Routing im Konstrukt."

    async def run():
        hook = ih.IngestionHook(log_path=tmp_path / "ingest.jsonl")
        start = await hook.on_session_start("s1")
        r1 = await hook.on_user_prompt_submit("s1", text, "prompt", 0.9)
        r2 = await hook.on_user_prompt_submit("s1", text, "prompt", 0.9)      # Duplikat
        r3 = await hook.on_user_prompt_submit("s1", "kurz", "prompt", 0.9)   # Gate
        end = await hook.on_session_end("s1")
        return start, r1, r2, r3, end

    start, r1, r2, r3, end = asyncio.run(run())
    assert start.decision == "session_start" and end.decision == "session_end"
    assert r1.decision == "accepted" and r1.enrichment == "queued"
    assert r2.decision == "rejected" and "Duplikat" in r2.reason
    assert r3.decision == "rejected" and "zu kurz" in r3.reason
    assert r1.tags["session_id"] == "s1" and r1.tags["source_type"] == "prompt"
    assert (tmp_path / "ingest.jsonl").read_text(encoding="utf-8").count("\n") == 5


def test_hook_faengt_ausnahmen(tmp_path, monkeypatch):
    def boom(self, _rec):
        raise OSError("Platte voll")

    monkeypatch.setattr(ih.IngestionHook, "_append", boom)

    async def run():
        hook = ih.IngestionHook(log_path=tmp_path / "ingest.jsonl")
        return (await hook.on_session_start("s1"),
                await hook.on_user_prompt_submit("s1", "lang genug hier", "prompt", 1.0),
                await hook.on_session_end("s1"))

    assert asyncio.run(run()) == (None, None, None)


def test_demo_laeuft_im_tmp(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(ih, "DEFAULT_LOG", tmp_path / "demo.jsonl")
    asyncio.run(ih._demo())
    out = capsys.readouterr().out
    assert "Lifecycle + Gate + Dedup" in out
    assert "Enrichment (async) verarbeitet:" in out
    lines = (tmp_path / "demo.jsonl").read_text(encoding="utf-8").strip().splitlines()
    assert all(json.loads(l)["session_id"] == "sess-001" for l in lines)


def test_update_graph_knoten_bereits_vorhanden():
    """Branch 246->244: Entity ist schon im Graph -> if-Zweig nicht genommen."""
    g = ih.MemoryGraph()
    g.add_node("a")
    d = ih.update_graph(g, [{"span": "a"}, "b"], [])
    assert d["added_nodes"] == ["b"]          # "a" war bereits vorhanden
