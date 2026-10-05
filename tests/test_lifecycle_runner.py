"""8-Stufen-Runner (data/memory/lifecycle_runner.py) — echter Durchlauf (Guardrail 7).

Stufe 5 (Denken) ruft die **echte** LLM-Reflexion (`reflective_agent.parse_transition_delta`).
Ohne Key/Endpoint → **NOOP** (None), keine erfundene Matrix. Der Matrix-Zweig wird über den
realen Parser `_matrix_from_raw` (echter Code, echte Eingabe) als Test-Seam geprüft.
"""

import ingestion_hook
import lifecycle_runner as lr
import lru_cache
import mandate
import reflective_agent as ra


def _classify(cls):
    return lambda q, f, c: {"class": cls}


def test_vollstaendiger_durchlauf(tmp_path, monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)  # Denken offline -> NOOP (kein Fake)
    wm = lru_cache.WorkingMemory(capacity=15)
    out = lr.run_cycle(
        "Wo?",
        "Kontakt: max@example.com, Version 2.",
        "Version 2.",
        classify_fn=_classify("write-new"),
        structured_dir=tmp_path / "structured",
        tier3_dir=tmp_path / "tier3",
        reflection_text="The action matched my usual inertia.",
        energies=[1.0, 0.9],
        wm=wm,
    )
    assert out["stages"] == list(lr.STAGES)
    assert len(out["trace"]) == 8
    assert out["results"]["Erfahrung"]["stored"].startswith("raw:")  # schreibt M
    assert out["results"]["Gedächtnis"]["ok"] is True  # pipeline schreibt
    assert out["results"]["Denken"]["self_feedback"] is None  # NOOP (offline)
    assert out["results"]["Nicht-Kognition"]["damping"] == 1.0  # stabil
    assert out["results"]["Handeln"]["stored"].startswith("action:")  # Aktion → M
    assert "gate" in out["results"]["Wissen+"]


def test_denken_matrix_zweig(tmp_path):
    """Matrix-Zweig über den realen Parser (Test-Seam; echte Eingabe, echter Code)."""
    out = lr.run_cycle(
        "Q",
        "Fakt",
        "Fakt",
        classify_fn=_classify("write-new"),
        structured_dir=tmp_path / "s",
        tier3_dir=tmp_path / "t",
        reflection_text="[[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]]",
        reflect_fn=ra._matrix_from_raw,
    )
    assert out["results"]["Denken"]["self_feedback"] == 1.0


def test_noop_und_instabil(tmp_path, monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    out = lr.run_cycle(
        "Frage?",
        "Fakt ohne Matrix.",
        "Fakt",
        classify_fn=_classify("non-write"),
        structured_dir=tmp_path / "structured",
        tier3_dir=tmp_path / "tier3",
        reflection_text="keine matrix",
        energies=[1.0, 2.0],  # steigend -> instabil -> Dämpfung
    )
    assert out["results"]["Denken"]["self_feedback"] is None  # NOOP
    assert out["results"]["Nicht-Kognition"]["damping"] == 0.5
    assert out["results"]["Gedächtnis"]["action"] == "none"  # non-write


def test_ueberschreibungen(tmp_path):
    out = lr.run_cycle(
        "Q",
        "Fakt",
        "Fakt",
        classify_fn=_classify("write-new"),
        structured_dir=tmp_path / "s",
        tier3_dir=tmp_path / "t",
        wm=lru_cache.WorkingMemory(),
        graph=ingestion_hook.MemoryGraph(),
        relations=[("a", "related", "b")],
        edges=[("a", "b", "NEXT")],
        dims={"logical": 0.9, "grounding": 0.9, "alignment": 0.9, "novelty": 0.5},
        drift_baseline={"non-write": 0.5, "write": 0.5},
        mandate_obj=lr._default_mandate(),
        reflect_fn=ra._matrix_from_raw,
    )
    assert out["results"]["Wissen"]["added_edges"] == 1


def test_stage_mechanism_vollstaendig():
    assert set(lr.STAGE_MECHANISM) == set(lr.STAGES)


def test_denied_lifecycle_stoppt_writes(tmp_path, monkeypatch):
    """§9.1/§9.2a: bei Mandats-deny kein Action-Write, revised=False, PII gefiltert (F3)."""
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    deny = mandate.Mandate(
        mandate_id="d",
        principal="P",
        agent="a",
        actions=frozenset({"read:repo"}),
        resources=frozenset({"data/memory"}),
        amount_limit=1.0,
        max_uses=100,
        valid_from=0.0,
        valid_until=1e12,
        approval_threshold=0.5,
    )
    wm = lru_cache.WorkingMemory(capacity=15)
    out = lr.run_cycle(
        "Wo?",
        "Kontakt: max@example.com bitte melden",
        "x",
        classify_fn=_classify("write-new"),
        structured_dir=tmp_path / "s",
        tier3_dir=tmp_path / "t",
        wm=wm,
        mandate_obj=deny,
    )
    assert out["results"]["Gedächtnis"]["ok"] is False
    assert out["results"]["Handeln"]["skipped"] is True
    assert out["results"]["Wissen+"]["revised"] is False
    assert "max@example.com" not in wm.search("raw:wo")["value"]  # PII entfernt
