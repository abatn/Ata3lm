"""Working Memory / LRU-Cache (data/memory/tier3-working/lru_cache.py).

Schreibpfade (Tier 2) werden auf `tmp_path` umgebogen.
"""

import lru_cache as lc


def _wm(tmp_path, monkeypatch, **kw):
    monkeypatch.setattr(lc, "TIER2", tmp_path / "tier2")
    monkeypatch.setattr(lc, "STRUCTURED", tmp_path / "structured")
    return lc.WorkingMemory(**kw)


def test_relevance_nach_typ():
    from pathlib import Path

    assert lc.relevance(Path("distilled-hub-x.md")) == 1.0
    assert lc.relevance(Path("entity-y.md")) == 1.0
    assert lc.relevance(Path("relation-z.md")) == 0.6
    assert lc.relevance(Path("sonstiges.md")) == 0.3


def test_store_search_access_und_dedup(tmp_path, monkeypatch):
    wm = _wm(tmp_path, monkeypatch)
    wm.store("a", "v1")
    assert wm.search("a")["value"] == "v1"
    wm.store("a", "v2")  # search-before-store: kein Duplikat
    assert wm.search("a")["value"] == "v1" and wm.search("a")["hits"] == 1
    assert wm.access("a")["hits"] == 2
    assert wm.access("gibt-es-nicht") is None


def test_eviction_lru_policy(tmp_path, monkeypatch):
    wm = _wm(tmp_path, monkeypatch, capacity=2, policy="lru")
    wm.store("a", "1")
    wm.store("b", "2")
    wm.store("c", "3")
    assert wm.evicted == ["a"] and "a" not in wm.items
    assert (tmp_path / "tier2" / "evicted-index.md").exists()


def test_eviction_value_policy_adaptive_und_fallback(tmp_path, monkeypatch):
    wm = _wm(tmp_path, monkeypatch, capacity=2, policy="value")
    wm.store("alt", "x", edge_weight=0.1)  # schwach, aber noch nicht alt genug
    wm.store("neu", "y")
    wm.store("dritter", "z")  # Fallback: niedrigster Score fliegt
    assert len(wm.items) == 2 and len(wm.evicted) == 1


def test_adaptive_forgetting_dreifache_bedingung(tmp_path, monkeypatch):
    wm = _wm(tmp_path, monkeypatch, capacity=1)
    wm.store("kandidat", "x", edge_weight=0.1)
    assert wm.should_forget("kandidat") is False  # age noch nicht erfüllt
    wm.tick += lc.DELTA_AGE + 1
    assert wm.should_forget("kandidat") is True  # alle drei Bedingungen
    wm.access("kandidat")  # recent_access = 1
    assert wm.should_forget("kandidat") is False


def test_evict_score_und_alles_gepinnt(tmp_path, monkeypatch):
    wm = _wm(tmp_path, monkeypatch, capacity=1)
    wm.store("p", "x", pinned=True, importance=1.0)
    wm.store("q", "y", pinned=True)
    assert wm._evict_lowest_score() is None  # alles gepinnt
    assert wm._evict_adaptive_forgetting() is None
    assert wm._evict_lru() is None  # alles gepinnt (lru-Pfad)
    assert wm.evict_score("q") == 0.75 * 0.5


def test_to_tier2_haengt_an_bestehende_datei_an(tmp_path, monkeypatch):
    wm = _wm(tmp_path, monkeypatch)
    wm._to_tier2("a", {})
    wm._to_tier2("b", {})
    text = (tmp_path / "tier2" / "evicted-index.md").read_text(encoding="utf-8")
    assert text.count("| a |") == 1 and text.count("| b |") == 1
    assert text.startswith("# Tier 2")


def test_fill_from_structured_und_router(tmp_path, monkeypatch):
    wm = _wm(tmp_path, monkeypatch, capacity=15)
    structured = tmp_path / "structured"
    structured.mkdir(parents=True)
    (structured / "README.md").write_text("skip", encoding="utf-8")
    (structured / "distilled-hub-a.md").write_text("x", encoding="utf-8")
    (structured / "relation-b.md").write_text("x", encoding="utf-8")
    (structured / "sonst-c.md").write_text("x", encoding="utf-8")  # 0.3 < 0.5 → nicht geladen
    loaded = wm.fill_from_structured()
    assert "distilled-hub-a" in loaded and "relation-b" in loaded
    assert "sonst-c" not in loaded and "README" not in loaded
    assert wm.items["distilled-hub-a"]["pinned"] is True

    loaded2 = wm.fill_from_router(
        [
            {"class": "write-update", "key": "u1"},
            {"class": "write-new", "key": "n1"},
            {"class": "non-write", "key": "skip"},
            {"class": "unbekannt", "key": "skip2"},
        ]
    )
    assert loaded2 == ["u1", "n1"]  # write-update zuerst, non-write nie
    assert wm.items["u1"]["pinned"] is True and wm.items["n1"]["pinned"] is False


def test_simulate_20_router_runs(tmp_path, monkeypatch):
    monkeypatch.setattr(lc, "TIER2", tmp_path / "tier2")
    monkeypatch.setattr(lc, "STRUCTURED", tmp_path / "structured")
    wm = lc.simulate_20_router_runs()
    assert len(wm.items) <= lc.CAPACITY
    assert wm.evicted and len(wm.log) > 0


def test_fill_from_structured_ohne_aufnahme_bei_vollem_cache(tmp_path, monkeypatch):
    """Branch 152->144: Item wird sofort verdrängt -> nicht als geladen gezählt."""
    wm = _wm(tmp_path, monkeypatch, capacity=1, policy="lru")
    wm.store("full", "x", pinned=True)
    structured = tmp_path / "structured"
    structured.mkdir(parents=True)
    (structured / "relation-b.md").write_text("x", encoding="utf-8")
    loaded = wm.fill_from_structured()
    assert loaded == []  # store() lief, Item ist sofort raus
    assert list(wm.items) == ["full"]
