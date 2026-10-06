"""K4: Skills maschinell an Executoren binden (`process:` + JSON Schema + echte Ausführung).

Quellen (verifiziert):
  - Voyager (arXiv:2305.16291): „ever-growing skill library of executable code".
  - JSON Schema Draft 2020-12: https://json-schema.org/specification (Struktur).
Guardrail 7: jeder Executor wird REAL mit Eingabe→Berechtigung→Ergebnis getestet;
`doc-only` wird als solches getestet (ehrlich, kein Fake).
"""

from pathlib import Path

import mandate
import numpy as np
import pytest
import skill_interpreter as si

ROOT = Path(__file__).resolve().parents[1]
ACTIVE = si.list_skills()


def _mandate():
    return mandate.Mandate(
        mandate_id="k4",
        principal="Batnini",
        agent="knowledge-agent",
        actions=frozenset({"write:memory"}),
        resources=frozenset({"data/memory"}),
        amount_limit=1.0,
        max_uses=100,
        valid_from=0.0,
        valid_until=1e12,
        approval_threshold=0.5,
    )


def _ctx(tmp_path):
    """Vollständiger Eingabe-Kontext für alle registrierten Executoren."""
    return {
        "question": "Wo?",
        "fact": "Kontakt: max@example.com, Version 2.",
        "correct": "Version 2.",
        "classify_fn": lambda q, f, c: {"class": "write-new"},
        "mandate_obj": _mandate(),
        "now": 100.0,
        "structured_dir": tmp_path / "structured",
        "tier3_dir": tmp_path / "tier3",
        "results_dir": tmp_path / "results",
        "tier1_dir": tmp_path / "tier1",
        # Stufe 2 (FWR-Checks)
        "refusal": False,
        "large_correct": True,
        "memory_correct": True,
        # Stufe 6 (Trust-Guards)
        "origin": "user",
        "verified": True,
        "checkpoint": 0.0,
        "bias_current": 0.05,
        "tau": 0.10,
        # Stufe 5 (Drift)
        "baseline": {"a": 0.5, "b": 0.5},
        "distribution": {"a": 0.6, "b": 0.4},
        "step": 1,
        # Stufe 8 (Shared Tier)
        "agent": "agent",
        "key": "skill",
        "value": "v",
        "trust": 0.5,
        # Stufe 4/5 (HMM-Trägheit, SEAA Eq. 2)
        "reflection": "calm",
        "reflection_delta": np.eye(4) * 0.1,
        # Compare (Evaluator/κ)
        "successes": 3,
        "failures": 1,
        "rater_a": ["a", "b", "a", "b"],
        "rater_b": ["a", "b", "b", "b"],
    }


# --- Prozess-Zuordnung (Registry vollständig) ---


def test_default_registry_vollstaendig():
    erwartet = {
        "pipeline.py",
        "memory.write",
        "ingestion_hook.py",
        "fast_write_router.py",
        "trust.py",
        "bias_monitor.py",
        "shared_memory.py",
        "reflective_agent.py",
        "evaluator_version.py",
    }
    assert set(si.DEFAULT_REGISTRY) == erwartet
    assert all(callable(fn) for fn in si.DEFAULT_REGISTRY.values())


def test_process_schema_enum():
    assert si.PROCESS_SCHEMA["required"] == ["process"]
    assert "doc-only" in si.PROCESS_SCHEMA["properties"]["process"]["enum"]
    for key in si.DEFAULT_REGISTRY:
        assert key in si.PROCESS_SCHEMA["properties"]["process"]["enum"]


def test_validate_process_gueltig_und_ungueltig():
    assert si.validate_process({"process": "pipeline.py"})["valid"] is True
    assert si.validate_process({"process": "doc-only"})["valid"] is True
    # fehlendes Feld → Pflichtfeld fehlt
    assert si.validate_process({"name": "x"})["valid"] is False
    # unbekannter Wert → Enum-Verstoß
    assert si.validate_process({"process": "gibt-es-nicht"})["valid"] is False
    # Nicht-String → Typverstoß
    assert si.validate_process({"process": 42})["valid"] is False


def test_parse_skill_liefert_process():
    spec = si.parse_skill(ROOT / "skills/act/SKILL.md")
    assert spec["process"] == "pipeline.py"


# --- 14/14 Skills: Eingabe→Berechtigung→Ergebnis ---


@pytest.mark.parametrize("path", ACTIVE, ids=[p.parent.name for p in ACTIVE])
def test_skill_lauffaehig(path, tmp_path):
    spec = si.parse_skill(path)
    assert spec.get("process"), f"kein `process:`-Feld: {path}"
    assert si.validate_process(spec)["valid"] is True
    out = si.bind_skill(path, _ctx(tmp_path))
    assert out["status"] == "lauffähig" and out["executed"] is True
    assert isinstance(out["result"], dict) and out["result"]


def test_bind_all_14(tmp_path):
    outs = si.bind_all_skills(_ctx(tmp_path))
    assert len(outs) == 14
    assert all(o["status"] == "lauffähig" and o["executed"] is True for o in outs)
    assert {o["process"] for o in outs} == {
        "pipeline.py",
        "ingestion_hook.py",
        "fast_write_router.py",
        "trust.py",
        "bias_monitor.py",
        "shared_memory.py",
        "reflective_agent.py",
        "evaluator_version.py",
    }


def test_executor_berechtigung_wirkt(tmp_path):
    """Eingabe→Berechtigung→Ergebnis: Guards lehnen ab, wenn die Eingabe es verlangt."""
    # Trust: nicht verifizierte Quelle → Poisoning-Guard rejected (§9.2c)
    ctx = _ctx(tmp_path)
    ctx["verified"] = False
    assert si.DEFAULT_REGISTRY["trust.py"](ctx)["admission"]["admitted"] is False
    # Ingestion: zu kurzer Fakt → Encoding-Gate lehnt ab (Berechtigung)
    kurz = {**ctx, "fact": "kurz"}
    assert si.DEFAULT_REGISTRY["ingestion_hook.py"](kurz)["accepted"] is False
    # FWR: Verweigerung + mit Memory korrekt → write-new (§10.7)
    assert si.DEFAULT_REGISTRY["fast_write_router.py"]({**ctx, "refusal": True})["class"] == "write-new"


# --- Ehrliche Kennzeichnung: doc-only + unbound ---


def test_bind_doc_only(tmp_path):
    p = tmp_path / "docsonly" / "SKILL.md"
    p.parent.mkdir(parents=True)
    p.write_text("---\nname: docsonly\ndescription: d\nprocess: doc-only\n---\n\n## Prozesse\n", encoding="utf-8")
    out = si.bind_skill(p, _ctx(tmp_path))
    assert out["status"] == "doc-only" and out["executed"] is False and out["valid"] is True


def test_bind_unbound_ohne_registry(tmp_path):
    out = si.bind_skill(ROOT / "skills/act/SKILL.md", _ctx(tmp_path), registry={})
    assert out["status"] == "unbound" and out["executed"] is False


def test_bind_ohne_process_feld(tmp_path):
    p = tmp_path / "leer" / "SKILL.md"
    p.parent.mkdir(parents=True)
    p.write_text("---\nname: leer\ndescription: d\n---\n\n## Prozesse\n", encoding="utf-8")
    out = si.bind_skill(p, _ctx(tmp_path))
    assert out["valid"] is False and out["status"] == "unbound"
