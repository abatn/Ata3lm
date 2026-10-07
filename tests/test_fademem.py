"""FadeMem – adaptive Exponential-Decay-Eviction (AGENTS.md §9.2b Vergessen / §11.1 tier3).

Quelle (verifiziert, HTTP): FadeMem ICASSP 2026, DOI 10.1109/icassp55912.2026.11462095;
arXiv:2601.18642 – „retention is governed by adaptive exponential decay functions
modulated by semantic relevance, access frequency, and temporal patterns."

Rein rechnerisch (kein Netz/LLM) – die Tests prüfen die Numerik, nicht ein Modell.
"""

import lru_cache as lc


def _wm(tmp_path, monkeypatch, **kw):
    monkeypatch.setattr(lc, "TIER2", tmp_path / "tier2")
    monkeypatch.setattr(lc, "STRUCTURED", tmp_path / "structured")
    return lc.WorkingMemory(**kw)


def _entry(importance=0.5, hits=0, last_used=0):
    return {"importance": importance, "hits": hits, "last_used": last_used}


# --- (a) Monotonie: sinkt mit Alter; steigt mit Relevanz/Frequenz ---
def test_decay_sinkt_mit_alter():
    e = _entry(importance=0.5, hits=0, last_used=0)
    assert lc.decay_score(e, now=0) > lc.decay_score(e, now=50) > 0


def test_decay_steigt_mit_relevanz():
    assert lc.decay_score(_entry(importance=0.9), now=20) > lc.decay_score(_entry(importance=0.2), now=20)


def test_decay_steigt_mit_frequenz():
    assert lc.decay_score(_entry(importance=0.5, hits=8), now=20) > lc.decay_score(
        _entry(importance=0.5, hits=0), now=20
    )


def test_decay_frisch_ist_relevanz():
    # age = 0 -> Verfallsfaktor 1 -> Score = Relevanz
    assert lc.decay_score(_entry(importance=0.7, last_used=5), now=5) == 0.7


def test_decay_frequenz_saettigt():
    # freq_norm ist auf 1.0 gedeckelt -> 10 und 100 Zugriffe gleich
    a = lc.decay_score(_entry(importance=0.5, hits=10, last_used=0), now=20)
    b = lc.decay_score(_entry(importance=0.5, hits=100, last_used=0), now=20)
    assert a == b


def test_decay_gamma_daempft_verfall():
    e = _entry(importance=0.5, hits=5, last_used=0)
    assert lc.decay_score(e, now=30, gamma=3.0) > lc.decay_score(e, now=30, gamma=0.0)


# --- (b) Eviction verdrängt das „unwichtigste" zuerst ---
def test_eviction_verdraengt_unwichtigstes(tmp_path, monkeypatch):
    wm = _wm(tmp_path, monkeypatch, capacity=2, policy="fademem")
    wm.store("wichtig", "x", importance=0.9)
    wm.store("unwichtig", "y", importance=0.1)
    wm.store("dritter", "z")  # Capacity 2 überschritten -> Eviction
    assert wm.evicted == ["unwichtig"]
    assert "unwichtig" not in wm.items
    assert (tmp_path / "tier2" / "evicted-index.md").exists()


def test_haeufig_und_relevant_ueberlebt_trotz_alter(tmp_path, monkeypatch):
    wm = _wm(tmp_path, monkeypatch, capacity=2, policy="fademem")
    wm.store("alt_relevant", "x", importance=1.0)
    wm.access("alt_relevant")  # Zugriffsfrequenz steigt (hits>0)
    wm.tick += 30  # stark altern lassen
    wm.store("neu_aber_unwichtig", "y", importance=0.1)
    wm.store("dritter", "z")
    assert wm.evicted == ["neu_aber_unwichtig"]
    assert "alt_relevant" in wm.items  # relevant + häufig > frisch + irrelevant


def test_pinned_nie_verdraengt(tmp_path, monkeypatch):
    wm = _wm(tmp_path, monkeypatch, capacity=1, policy="fademem")
    wm.store("core", "x", pinned=True, importance=0.05)
    wm.store("schwach", "y", importance=0.1)
    assert "core" in wm.items
    assert wm.evicted == ["schwach"]


def test_lru_policy_unveraendert(tmp_path, monkeypatch):
    # Regressionsschutz: fademem ist opt-in; lru/value bleiben wie zuvor.
    wm = _wm(tmp_path, monkeypatch, capacity=2, policy="lru")
    wm.store("a", "1")
    wm.store("b", "2")
    wm.store("c", "3")
    assert wm.evicted == ["a"]


# --- (c) Grenzfälle: leer / alles frisch / alles gepinnt ---
def test_grenzfall_leer(tmp_path, monkeypatch):
    wm = _wm(tmp_path, monkeypatch, policy="fademem")
    assert wm._evict_fademem() is None
    assert wm.evicted == []


def test_grenzfall_alles_frisch(tmp_path, monkeypatch):
    wm = _wm(tmp_path, monkeypatch, capacity=2, policy="fademem")
    wm.store("a", "1", importance=0.6)
    wm.store("b", "2", importance=0.2)
    # beide nahezu frisch -> Score ≈ Relevanz -> b ist das niedrigste
    assert wm._evict_fademem() == "b"


def test_grenzfall_alles_gepinnt(tmp_path, monkeypatch):
    wm = _wm(tmp_path, monkeypatch, capacity=1, policy="fademem")
    wm.store("p", "x", pinned=True)
    wm.store("q", "y", pinned=True)
    assert wm._evict_fademem() is None
    assert set(wm.items) == {"p", "q"}
