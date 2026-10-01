"""FWR-Tests: 3-Klassen-Kaskade + Gate (AGENTS.md:306-307, §10.1, §10.4).

Bedingungen sind wörtlich aus dem Gesetz; alle LLM-Antworten sind skriptet.
"""
import fast_write_router as fwr

SMALL = fwr.SMALL_MODEL
LARGE = fwr.LARGE_MODEL


def _script(monkeypatch, small, large_zero, large_mem):
    """Fake `_ask`: small/large zero-shot ohne Memory, large MIT Memory."""
    calls = []

    def fake(model, question, memory=None, max_tokens=2000):
        calls.append({"model": model, "with_memory": memory is not None})
        if memory is not None:
            return large_mem
        return small if model == SMALL else large_zero

    monkeypatch.setattr(fwr, "_ask", fake)
    return calls


# ---------------------------------------------------------------- Stufe 1
def test_non_write_wenn_small_zutrift(monkeypatch):
    calls = _script(monkeypatch, "The capital of France is Paris.",
                    "x", "x")
    r = fwr.classify("What is the capital of France?",
                     "Paris is the capital of France.", "Paris")
    assert r["class"] == "non-write"
    assert r["stage"] == 1
    assert r["escalated"] is False
    assert r["gate"] == "none"          # §10.1: nicht speichern
    assert len(calls) == 1              # keine Eskalation an den großen Router


# ---------------------------------------------------------------- Stufe 2
def test_write_update_greift_wenn_large_falsch_und_mem_korrekt(monkeypatch):
    """Fall „Größte Wüste": large falsch, mit Memory korrekt -> write-update."""
    _script(monkeypatch,
            "The Antarctic Desert is the largest desert in the world.",
            "The largest desert in the world is the Antarctic Desert.",
            "The largest desert in the world is the Sahara.")
    r = fwr.classify("What is the largest desert in the world?",
                     "The largest desert in the world is the Sahara.", "Sahara")
    assert r["class"] == "write-update"
    assert r["stage"] == 2 and r["escalated"] is True
    assert r["checks"] == {"refusal": False, "large_correct": False,
                           "memory_correct": True}
    assert r["gate"] == "ask"           # §9: self_update an tier1-base


def test_write_new_nur_bei_verweigerung_und_mem_korrekt(monkeypatch):
    _script(monkeypatch, "I don't know.", "I don't know.",
            "The capital of Xylophonia is Zentaria.")
    r = fwr.classify("What is the capital of Xylophonia?",
                     "The capital of Xylophonia is Zentaria.", "Zentaria")
    assert r["class"] == "write-new"
    assert r["checks"] == {"refusal": True, "large_correct": False,
                           "memory_correct": True}
    assert r["gate"] == "ask"           # §10.4: neue Quelle


def test_kein_write_update_wenn_mem_falsch(monkeypatch):
    """Die alte Falle: Verweigerung OHNE korrekten Memory -> kein write-update."""
    _script(monkeypatch, "I don't know.", "I don't know.",
            "Xylophonia has no capital.")
    r = fwr.classify("What is the capital of Xylophonia?",
                     "Xylophonia is a fictional country with no capital.",
                     "Zentaria")
    assert r["class"] == "uncertain"
    assert r["checks"]["memory_correct"] is False
    assert r["gate"] == "ask"           # §10.4: Unsicherheit -> Human-Gate


def test_large_korrekt_aber_small_falsch_wird_nicht_geschrieben(monkeypatch):
    _script(monkeypatch, "I don't know.", "The largest desert is the Sahara.",
            "The largest desert in the world is the Sahara.")
    r = fwr.classify("What is the largest desert in the world?",
                     "The largest desert in the world is the Sahara.", "Sahara")
    assert r["class"] == "uncertain"
    assert r["gate"] == "ask"


# ------------------------------------------------------------- Konstanten
def test_modelle_defaults_ohne_ausgemustertes_modell():
    """AGENTS.md:252 – Defaults = nano-30b / super-120b (gemma-2b ist 404)."""
    assert SMALL == "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning"
    assert LARGE == "nvidia/nemotron-3-super-120b-a12b"
    assert "gemma" not in SMALL and "gemma" not in LARGE


def test_refusal_marker_und_matches():
    assert fwr.is_refusal("I don't know.") is True
    assert fwr.is_refusal("The answer is Paris.") is False
    assert fwr._matches("The Sahara is the largest desert.", "sahara") is True
    assert fwr._matches("The Sahara...", "Antarctic Desert") is False


# ------------------------------------------------- _ask (ohne Netz: Fake-Client)
from types import SimpleNamespace


def _fake_client(msg, calls):
    class Completions:
        def create(self, **kw):
            calls.append(kw)
            return SimpleNamespace(choices=[SimpleNamespace(message=msg)])

    return SimpleNamespace(chat=SimpleNamespace(completions=Completions()))


def test_ask_ohne_memory_und_mit_memory(monkeypatch):
    calls = []
    monkeypatch.setattr(fwr, "_client",
                        _fake_client(SimpleNamespace(content=" Paris "), calls))
    assert fwr._ask(SMALL, "Capital?") == "Paris"
    assert "Use this knowledge:" not in calls[0]["messages"][0]["content"]
    assert fwr._ask(LARGE, "Capital?", memory="Paris ist es.") == "Paris"
    assert "Use this knowledge:" in calls[1]["messages"][0]["content"]
    assert calls[1]["model"] == LARGE and calls[1]["temperature"] == 0.0


def test_ask_faellt_auf_reasoning_content_zurueck(monkeypatch):
    msg = SimpleNamespace(content=None, reasoning_content="  Denk-Antwort  ")
    monkeypatch.setattr(fwr, "_client", _fake_client(msg, []))
    assert fwr._ask(SMALL, "Frage?") == "Denk-Antwort"


# ------------------------------------------------------------- MemRouter (Paper)
def test_memrouter_forward_only_und_parametrizahl():
    mr = fwr.MemRouter()
    r = mr.classify("What is the capital of France?",
                    "Paris is the capital.", "Paris")
    assert r["class"] in ["non-write", "write-new", "write-update"]
    assert r["method"] == "memrouter" and r["forward_only"] is True
    assert r["params"] == 384 * 31250 + 31250 * 3


def test_embed_router_normalisiert_und_leerer_text():
    v = fwr._embed_router("Paris paris TOKYO")
    assert abs(float((v ** 2).sum()) - 1.0) < 1e-9
    assert float((fwr._embed_router("") ** 2).sum()) == 0.0


def test_compare_router_10_liefert_10_laeufe():
    out = fwr.compare_router_10()
    assert len(out["runs"]) == 10
    assert out["memrouter_p50_ms"] < out["llm_p50_ms"]
    assert out["speedup"] == round(out["llm_p50_ms"] / out["memrouter_p50_ms"], 1)
    assert out["memrouter_params"] == fwr.MemRouter().params
