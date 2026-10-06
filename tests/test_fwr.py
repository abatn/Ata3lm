"""FWR-Tests: 3-Klassen-Kaskade + Gate – ECHTE Calls (AGENTS.md Guardrail 7).

Kein Fake/skriptet: `classify()`/`_ask()` laufen gegen das **echte** NVIDIA-Endpoint
(Key via `conftest.py`/`opencode.json`). Transiente 503 werden mit Backoff wiederholt
(`_live.call`) – echte Verifikation, keine Ersatzantwort.
"""

import fast_write_router as fwr
from _live import call

SMALL = fwr.SMALL_MODEL
LARGE = fwr.LARGE_MODEL


# ------------------------------------------------- Stufe 1: non-write (real)
def test_non_write_real():
    r = call(fwr.classify, "What is the capital of France?", "Paris is the capital of France.", "Paris")
    assert r["class"] == "non-write"
    assert r["stage"] == 1 and r["escalated"] is False and r["gate"] == "allow"  # K6/B5: Labelraum


# ------------------------------------------------- Stufe 2: write-new (real)
def test_write_new_real():
    r = call(fwr.classify, "What is the capital of Xylophonia?", "The capital of Xylophonia is Zentaria.", "Zentaria")
    assert r["class"] == "write-new"
    assert r["stage"] == 2 and r["escalated"] is True and r["gate"] == "ask"


# ---------------------------------------------- Stufe 2: write-update (real)
def test_write_update_real():
    r = call(
        fwr.classify,
        "What is the largest desert in the world?",
        "The largest desert in the world is the Sahara.",
        "Sahara",
    )
    assert r["class"] == "write-update"
    assert r["gate"] == "ask"


# --------------------------------------------------- uncertain (real, §10.4)
def test_uncertain_real():
    r = call(
        fwr.classify,
        "What is the capital of Xylophonia?",
        "Xylophonia is a fictional country with no capital.",
        "Zentaria",
    )
    assert r["class"] == "uncertain" and r["gate"] == "ask"


# ------------------------------------------------------------- Konstanten
def test_modelle_defaults_ohne_ausgemustertes_modell():
    """AGENTS.md:252 – Defaults = nano-30b / ultra-550b (gemma-2b ist 404)."""
    assert SMALL == "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning"
    assert LARGE == "nvidia/nemotron-3-ultra-550b-a55b"
    assert "gemma" not in SMALL and "gemma" not in LARGE


def test_refusal_marker_und_matches():
    assert fwr.is_refusal("I don't know.") is True
    assert fwr.is_refusal("The answer is Paris.") is False
    assert fwr._matches("The Sahara is the largest desert.", "sahara") is True
    assert fwr._matches("The Sahara...", "Antarctic Desert") is False


# ------------------------------------------------- _ask (echter Endpoint)
def test_ask_real_ohne_und_mit_memory():
    a = call(fwr._ask, SMALL, "Answer in one word: capital of France?")
    assert isinstance(a, str) and a.strip()
    b = call(fwr._ask, LARGE, "What is the capital of France?", memory="Paris is the capital of France.")
    assert isinstance(b, str) and b.strip()


# ------------------------------------------------------------- MemRouter (Paper)
def test_memrouter_forward_only_und_parametrizahl():
    mr = fwr.MemRouter()
    r = mr.classify("What is the capital of France?", "Paris is the capital.", "Paris")
    assert r["class"] in ["non-write", "write-new", "write-update"]
    assert r["method"] == "memrouter" and r["forward_only"] is True
    assert r["params"] == 384 * 31250 + 31250 * 3


def test_embed_router_normalisiert_und_leerer_text():
    v = fwr._embed_router("Paris paris TOKYO")
    assert abs(float((v**2).sum()) - 1.0) < 1e-9
    assert float((fwr._embed_router("") ** 2).sum()) == 0.0


def test_compare_router_10_liefert_10_laeufe():
    out = fwr.compare_router_10()
    assert len(out["runs"]) == 10
    assert out["memrouter_p50_ms"] < out["llm_p50_ms"]
    assert out["speedup"] == round(out["llm_p50_ms"] / out["memrouter_p50_ms"], 1)
    assert out["memrouter_params"] == fwr.MemRouter().params


def test_decide_alle_zweige():
    """Reine Entscheidungslogik (Paper §3.1/§10.7) – deterministisch, ohne LLM."""
    assert fwr._decide(True, False, True) == ("write-new", "ask")
    assert fwr._decide(False, False, True) == ("write-update", "ask")
    assert fwr._decide(False, True, True) == ("uncertain", "ask")  # large korrekt -> kein write
    assert fwr._decide(False, False, False) == ("uncertain", "ask")


def test_import_ohne_key_kein_crash(monkeypatch):
    """A9: Import ohne OPENAI_API_KEY crasht nicht (lazy Client)."""
    import importlib

    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_BASE_URL", raising=False)
    mod = importlib.reload(fwr)
    assert mod._client is None
