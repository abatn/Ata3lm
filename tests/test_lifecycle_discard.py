"""M4: Geschlossener Lifecycle — Router „senses consolidation" → discard (§10.3).

`discard_if_consolidated` behandelt bereits-konsolidierte Fakten als `non-write`
(kein erneuter externer Write). Kein Netz: reine State-/Dateisystem-Logik
(echte Dateien, echter Parser), daher unter Guardrail 7 zulässig.

Quelle (Belegt, im Gesetz): arXiv:2608.22215 §3.4 — „the router adaptively
suppress redundant writes as the model's epistemic boundaries evolve"
(AGENTS.md §10.1/§10.3). Key-Zuordnung = Projekt-Auftrag.
"""

import json
from pathlib import Path

import fast_write_router as fwr
import gate_labels
import provenance
import pytest

REAL_STATE = Path(__file__).resolve().parents[1] / "data/memory/tier3-working/consolidation-state.json"


def _state(tmp_path, keys, *, facts=None, probe_passed=True):
    """Konsolidierungs-State im N2-Format (Hash-Bindung je Key).

    F3 (Audit 75095d5): Legacy-States ohne Hash sind **inert**; daher wird hier der
    Inhalt-Hash gebunden. `facts` = Mapping Key → Fakt-Inhalt (fehlt ⇒ Hash None).
    """
    facts = facts or {}
    entries = {
        k: {
            "fact_sha256": provenance.content_hash(facts[k]) if k in facts else None,
            "model": None,
            "probe_passed": probe_passed,
        }
        for k in keys
    }
    p = tmp_path / "consolidation-state.json"
    p.write_text(json.dumps({"consolidated": list(keys), "entries": entries}), encoding="utf-8")
    return p


# ------------------------------------------------ (a) konsolidiert ⇒ non-write
def test_hook_konsolidiert_ist_non_write(tmp_path):
    state = _state(tmp_path, ["hauptstadt-frankreich"], facts={"hauptstadt-frankreich": "Paris"})
    d = fwr.discard_if_consolidated("Paris", question="Hauptstadt Frankreich?", state_path=state)
    assert d["class"] == "non-write"
    assert d["gate"] == "none"
    assert gate_labels.normalize(d["gate"]) == gate_labels.ALLOW  # "none" = Legacy-Alias
    assert "konsolidiert" in d["reason"]
    assert d["consolidated_key"] == "hauptstadt-frankreich"


def test_classify_kurzschluss_ohne_llm(tmp_path):
    """Konsolidiert ⇒ Kaskade VOR Stufe 1 (stage=0), kein LLM-Call."""
    state = _state(tmp_path, ["hauptstadt-frankreich"], facts={"hauptstadt-frankreich": "Paris"})
    r = fwr.classify("Hauptstadt Frankreich?", "Paris", "Paris", state_path=state)
    assert r["class"] == "non-write" and r["stage"] == 0 and r["escalated"] is False
    assert r["gate"] == "none" and r["consolidated_key"] == "hauptstadt-frankreich"


def test_apply_write_action_kein_externer_write(tmp_path):
    """Angeforderte Klasse write-new wird auf non-write herabgestuft: nur Historie."""
    state = _state(tmp_path, ["hauptstadt-frankreich"], facts={"hauptstadt-frankreich": "Paris"})
    r = fwr.apply_write_action(
        "write-new",
        question="Hauptstadt Frankreich?",
        fact="Paris",
        structured_dir=tmp_path / "s",
        tier3_dir=tmp_path / "t3",
        results_dir=tmp_path / "ergebnisse",
        state_path=state,
    )
    assert r["ok"] and r["action"] == "non-write" and r["discarded"] is True
    assert r["gate"] == "none" and "konsolidiert" in r["reason"]
    assert not (tmp_path / "s").exists() and not (tmp_path / "t3").exists()
    hist = list((tmp_path / "ergebnisse").glob("*.non-write.jsonl"))
    assert len(hist) == 1 and json.loads(hist[0].read_text(encoding="utf-8"))["class"] == "non-write"


# ------------------------------------------ (b) nicht-konsolidiert ⇒ unverändert
def test_nicht_konsolidiert_unveraendert(tmp_path):
    state = _state(tmp_path, ["anderer-key"])
    assert fwr.discard_if_consolidated("Paris", question="Hauptstadt Frankreich?", state_path=state) is None
    # Kaskade/Verhalten unverändert: write-new ohne Freigabe hält VOR der Mutation an
    r = fwr.apply_write_action(
        "write-new",
        question="Hauptstadt Frankreich?",
        fact="Paris",
        structured_dir=tmp_path / "s",
        tier3_dir=tmp_path / "t3",
        results_dir=tmp_path / "ergebnisse",
        state_path=state,
    )
    assert r["ok"] is False and r["gate"] == "ask"
    assert "discarded" not in r and not (tmp_path / "s").exists()


def test_nicht_konsolidiert_mit_freigabe_schreibt(tmp_path):
    state = _state(tmp_path, ["anderer-key"])
    r = fwr.apply_write_action(
        "write-new",
        question="Hauptstadt Xylophonia?",
        fact="Zentaria",
        structured_dir=tmp_path / "s",
        tier3_dir=tmp_path / "t3",
        now=1.0,
        self_update=True,
        approvers=["Batnini", "Verifier2"],
        state_path=state,
    )
    assert r["ok"] and r["action"] == "write-new" and "discarded" not in r
    assert (tmp_path / "s" / "hauptstadt-xylophonia.md").exists()


# --------------------------------------------- (c) Default None ⇒ kein Effekt
def test_default_state_path_kein_effekt(tmp_path):
    assert fwr.discard_if_consolidated("Paris", question="Hauptstadt Frankreich?") is None
    assert fwr.discard_if_consolidated("Paris", question="Hauptstadt Frankreich?", state_path=None) is None
    r = fwr.apply_write_action(
        "write-new",
        question="Hauptstadt Xylophonia?",
        fact="Zentaria",
        structured_dir=tmp_path / "s",
        tier3_dir=tmp_path / "t3",
        now=2.0,
        self_update=True,
        approvers=["Batnini", "Verifier2"],
    )
    assert r["ok"] and r["action"] == "write-new" and "discarded" not in r
    assert (tmp_path / "s" / "hauptstadt-xylophonia.md").exists()


# --------------------------------------------------- Robustheit / Randfälle
def test_leerer_oder_fehlender_state_kein_effekt(tmp_path):
    empty = _state(tmp_path, [])
    assert fwr.discard_if_consolidated("Paris", question="Q?", state_path=empty) is None
    missing = tmp_path / "gibt-es-nicht.json"
    assert fwr.discard_if_consolidated("Paris", question="Q?", state_path=missing) is None


def test_ohne_question_und_ohne_fakt_kein_treffer(tmp_path):
    state = _state(tmp_path, ["hauptstadt-frankreich"])
    assert fwr.discard_if_consolidated("", question=None, state_path=state) is None
    assert fwr.discard_if_consolidated("", state_path=state) is None


def test_echter_konsolidierungs_state():
    """F3 (Audit 75095d5): realer Legacy-State OHNE Inhalt-Hash ⇒ **inert** ⇒ kein Discard.

    Nur lesend (kein Schreiben in die reale `consolidation-state.json`). Bindet der
    State später Hashes, greift wieder die reguläre Hash-/Probe-Bindung.
    """
    if not REAL_STATE.exists():
        pytest.skip("kein Konsolidierungs-State vorhanden")
    assert not (json.loads(REAL_STATE.read_text(encoding="utf-8")).get("entries") or {})
    d = fwr.discard_if_consolidated(
        "0.10",
        question="Was ist die Standard-Drift-Grenze in AGENTS.md Abschnitt 9.1?",
        state_path=REAL_STATE,
    )
    assert d is None


def test_get_client_lazy_offline(monkeypatch):
    """A9/Coverage: der Lazy-Client ist offline konstruierbar (kein Netz-Call, gecacht).

    Schließt die Offline-Coverage-Lücke von `fast_write_router._get_client` (nur sonst
    über Netz-Tests erreicht); es wird lediglich ein Client-Objekt gebaut, kein Request.
    """
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("OPENAI_BASE_URL", "http://127.0.0.1:9/v1")
    monkeypatch.setattr(fwr, "_client", None)
    first = fwr._get_client()
    assert first is fwr._get_client()  # zweiter Aufruf: gecachter Pfad (kein Neu-Bau)
