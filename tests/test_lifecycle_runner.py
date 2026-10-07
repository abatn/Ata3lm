"""8-Stufen-Runner (data/memory/lifecycle_runner.py) — echter Durchlauf (Guardrail 7).

Stufe 5 (Denken) ruft die **echte** LLM-Reflexion (`reflective_agent.parse_transition_delta`).
Ohne Key/Endpoint → **NOOP** (None), keine erfundene Matrix. Der Matrix-Zweig wird über den
realen Parser `_matrix_from_raw` (echter Code, echte Eingabe) als Test-Seam geprüft.
"""

import json

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
    # N6 §9.1: kein raw-Write vor dem Mandat -> gar kein WM-Eintrag
    assert wm.search("raw:wo") is None


def test_n6_kein_raw_write_vor_mandat(tmp_path, monkeypatch):
    """N6 §9.1: deny-Mandat -> kein `raw:`-Eintrag in Working Memory (keine Mutation vor Gate)."""
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
        "Geheim?",
        "Kontakt: max@example.com",
        "x",
        classify_fn=_classify("write-new"),
        structured_dir=tmp_path / "s",
        tier3_dir=tmp_path / "t",
        wm=wm,
        mandate_obj=deny,
    )
    assert out["results"]["Gedächtnis"]["ok"] is False
    assert wm.search("raw:geheim") is None  # N6: nichts vor dem Mandat geschrieben


def test_n7_gate_drift_werden_durchgereicht(tmp_path, monkeypatch):
    """N7 §9.3/§9.1c: Runner reicht self_update/approvers/drift an route_and_store durch."""
    import bias_monitor

    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    # (a) self_update + zwei Personen -> Schreibfreigabe über den Runner
    out = lr.run_cycle(
        "Gesetz X",
        "neu",
        "c",
        classify_fn=lambda q, f, c: {"class": "write-update", "gate": "ask"},
        structured_dir=tmp_path / "s",
        tier3_dir=tmp_path / "t",
        now=1.0,
        self_update=True,
        approvers=["Batnini", "Verifier2"],
    )
    assert out["results"]["Gedächtnis"]["ok"] is True
    assert ("approval", "approved") in out["results"]["Gedächtnis"]["steps"]
    # (b) explizites Drift-Gate ask -> kein Write vor Freigabe
    drift = bias_monitor.BiasDriftMonitor(baseline={"non-write": 1.0}, tau=0.01)
    out2 = lr.run_cycle(
        "Q",
        "F",
        "C",
        classify_fn=_classify("write-new"),
        structured_dir=tmp_path / "s2",
        tier3_dir=tmp_path / "t2",
        now=1.0,
        drift=drift,
    )
    assert out2["results"]["Gedächtnis"]["ok"] is False
    assert not (tmp_path / "s2").exists()


def test_n7_wissen_plus_echte_verteilung(tmp_path, monkeypatch):
    """N7 §9.1c: Stufe 8 nutzt die echte Klasse des Laufs gegen die injizierte Referenz."""
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    out = lr.run_cycle(
        "Q",
        "F",
        "F",
        classify_fn=_classify("non-write"),
        structured_dir=tmp_path / "s",
        tier3_dir=tmp_path / "t",
        drift_baseline={"non-write": 0.5, "write": 0.5},  # Bedingung 3: injizierte Referenz
    )
    assert out["results"]["Wissen+"]["DI"] > 0.0  # nicht mehr konstant 0.0


# --------------------------------------------------------------- S1 §9.1c/§9.2b


def test_s1_coldstart_ohne_referenz_ask(tmp_path, monkeypatch):
    """S1 §10.4: ohne Referenz ⇒ `ask` (nie still `ok`); Bootstrap wird gesetzt (Lesart A)."""
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("LIFECYCLE_DRIFT_BASELINE", raising=False)
    ref = tmp_path / "r.json"
    monkeypatch.setenv("LIFECYCLE_DRIFT_REFERENCE", str(ref))
    out = lr.run_cycle(
        "Q",
        "F",
        "F",
        classify_fn=_classify("non-write"),
        structured_dir=tmp_path / "s",
        tier3_dir=tmp_path / "t",
    )
    w = out["results"]["Wissen+"]
    assert w["gate"] == "ask" and w["DI"] is None
    assert ref.exists()  # Cold-Start-Bootstrap (Initialisierung, kein Fortschreiben)


def test_s1_checkpoint_gleich_ok(tmp_path, monkeypatch):
    """S1 §9.2b: Lauf == Checkpoint ⇒ DI=0, gate=allow (K6/B5-Labelraum)."""
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("LIFECYCLE_DRIFT_BASELINE", raising=False)
    ref = tmp_path / "r.json"
    ref.write_text('{"non-write": 1.0}', encoding="utf-8")
    monkeypatch.setenv("LIFECYCLE_DRIFT_REFERENCE", str(ref))
    out = lr.run_cycle(
        "Q",
        "F",
        "F",
        classify_fn=_classify("non-write"),
        structured_dir=tmp_path / "s",
        tier3_dir=tmp_path / "t",
    )
    w = out["results"]["Wissen+"]
    assert w["DI"] == 0.0 and w["gate"] == "allow"


def test_s1_verschobene_verteilung_ask(tmp_path, monkeypatch):
    """S1 §9.2b: verschobene Verteilung ⇒ DI>0, gate=ask."""
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("LIFECYCLE_DRIFT_BASELINE", raising=False)
    ref = tmp_path / "r.json"
    ref.write_text('{"write": 1.0}', encoding="utf-8")
    monkeypatch.setenv("LIFECYCLE_DRIFT_REFERENCE", str(ref))
    out = lr.run_cycle(
        "Q",
        "F",
        "F",
        classify_fn=_classify("non-write"),
        structured_dir=tmp_path / "s",
        tier3_dir=tmp_path / "t",
    )
    w = out["results"]["Wissen+"]
    assert w["DI"] > 0.0 and w["gate"] == "ask"


def test_s1_checkpoint_nur_bei_revised_fortschreiben(tmp_path, monkeypatch):
    """B5 (K6): M(t)→M(t+1) nur bei revised = ok AND gate == "allow"; deny/ask halten den Stand."""
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("LIFECYCLE_DRIFT_BASELINE", raising=False)
    ref = tmp_path / "r.json"
    ref.write_text('{"write": 0.5, "non-write": 0.5}', encoding="utf-8")
    monkeypatch.setenv("LIFECYCLE_DRIFT_REFERENCE", str(ref))
    # (a) ok + gate allow (tau gross genug) ⇒ revised ⇒ Checkpoint wird fortgeschrieben
    out = lr.run_cycle(
        "Q",
        "F",
        "F",
        classify_fn=_classify("write-new"),
        structured_dir=tmp_path / "s1",
        tier3_dir=tmp_path / "t1",
        tau=0.5,
    )
    w = out["results"]["Wissen+"]
    assert out["results"]["Gedächtnis"]["ok"] is True and w["gate"] == "allow"
    assert w["revised"] is True
    assert json.loads(ref.read_text(encoding="utf-8")) == {"write": 1.0}
    # (b) deny-Mandat ⇒ Akt nicht ok ⇒ Referenz bleibt unverändert
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
    out2 = lr.run_cycle(
        "Q2",
        "F",
        "F",
        classify_fn=_classify("write-new"),
        structured_dir=tmp_path / "s2",
        tier3_dir=tmp_path / "t2",
        mandate_obj=deny,
    )
    assert out2["results"]["Gedächtnis"]["ok"] is False
    assert out2["results"]["Wissen+"]["revised"] is False  # deny ⇒ revised=False
    assert json.loads(ref.read_text(encoding="utf-8")) == {"write": 1.0}  # unverändert
    # (c) ok, aber Drift-Gate ask VOR dem Write ⇒ KEIN Write (A2) und kein Fortschreiben (B5)
    ref.write_text('{"write": 0.5, "non-write": 0.5}', encoding="utf-8")
    out3 = lr.run_cycle(
        "Q3",
        "F",
        "F",
        classify_fn=_classify("write-new"),
        structured_dir=tmp_path / "s3",
        tier3_dir=tmp_path / "t3",
        tau=0.05,
    )
    w3 = out3["results"]["Wissen+"]
    assert out3["results"]["Gedächtnis"]["ok"] is False  # A2: Checkpoint gatet VOR der Mutation
    assert not (tmp_path / "s3").exists()  # kein Write vor der Freigabe (§9.1c)
    assert w3["gate"] == "ask" and w3["revised"] is False  # B5: revised nie bei ask
    assert json.loads(ref.read_text(encoding="utf-8")) == {"write": 0.5, "non-write": 0.5}  # unverändert


def test_a2_checkpoint_gatet_vor_write(tmp_path, monkeypatch):
    """A2 §9.1c: die persistierte Drift-Referenz (Checkpoint) gatet die Mutation VOR dem Write."""
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("LIFECYCLE_DRIFT_BASELINE", raising=False)
    ref = tmp_path / "r.json"
    ref.write_text('{"non-write": 1.0}', encoding="utf-8")
    monkeypatch.setenv("LIFECYCLE_DRIFT_REFERENCE", str(ref))
    out = lr.run_cycle(
        "Q",
        "F",
        "F",
        classify_fn=_classify("write-new"),
        structured_dir=tmp_path / "s",
        tier3_dir=tmp_path / "t",
        tau=0.10,
    )
    assert out["results"]["Gedächtnis"]["ok"] is False  # {non-write} vs {write} → ask vor dem Write
    assert not (tmp_path / "s").exists()  # kein Write vor der Freigabe


def test_a5_baseline_und_beobachtung_kanonisiert(tmp_path, monkeypatch):
    """A5/R16: Baseline `{write-update:1}` und Beobachtung `write-new` liegen im EINEN Labelraum."""
    import bias_monitor

    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    drift = bias_monitor.BiasDriftMonitor(baseline={"write-update": 1.0}, tau=0.10)
    out = lr.run_cycle(
        "Q",
        "F",
        "F",
        classify_fn=_classify("write-new"),
        structured_dir=tmp_path / "s",
        tier3_dir=tmp_path / "t",
        drift=drift,
        tau=0.10,
    )
    assert out["results"]["Gedächtnis"]["ok"] is True  # {write} == kanonisierte Baseline → allow
    assert out["results"]["Wissen+"]["gate"] == "allow"


def test_a5_canonicalize_distribution_aggregiert():
    """A5/R16: Kategorien werden kanonisiert und aggregiert (Altformat-Migration)."""
    assert lr._canonicalize_distribution({"write-new": 0.3, "write-update": 0.7}) == {"write": 1.0}
    assert lr._canonicalize_distribution({"none": 1.0}) == {"non-write": 1.0}
    assert lr._canonicalize_distribution({"unbekannt": 0.5}) == {"unbekannt": 0.5}


def test_s1_helfer_referenz(tmp_path, monkeypatch):
    """S1: Load/Save der Checkpoint-Referenz inkl. Fehlerzweige (fehlt/kaputt/leer)."""
    ref = tmp_path / "sub" / "r.json"
    monkeypatch.setenv("LIFECYCLE_DRIFT_REFERENCE", str(ref))
    assert lr._load_drift_reference() is None  # fehlt -> None
    ref.parent.mkdir(parents=True, exist_ok=True)
    ref.write_text("{kaputt", encoding="utf-8")
    assert lr._load_drift_reference() is None  # ungültiges JSON -> None
    ref.write_text("{}", encoding="utf-8")
    assert lr._load_drift_reference() is None  # leeres Dict -> None
    lr._save_drift_reference({"write": 1.0})
    assert lr._load_drift_reference() == {"write": 1.0}


def test_s1_konfigurierte_baseline_env(monkeypatch):
    """S1 §9.1c: `LIFECYCLE_DRIFT_BASELINE` (JSON) — alle Zweige."""
    monkeypatch.delenv("LIFECYCLE_DRIFT_BASELINE", raising=False)
    assert lr._configured_drift_baseline() is None  # unset
    monkeypatch.setenv("LIFECYCLE_DRIFT_BASELINE", "   ")
    assert lr._configured_drift_baseline() is None  # leer
    monkeypatch.setenv("LIFECYCLE_DRIFT_BASELINE", "kein json")
    assert lr._configured_drift_baseline() is None  # ungültiges JSON
    monkeypatch.setenv("LIFECYCLE_DRIFT_BASELINE", "[1, 2]")
    assert lr._configured_drift_baseline() is None  # kein Dict
    monkeypatch.setenv("LIFECYCLE_DRIFT_BASELINE", '{"write": 1.0}')
    assert lr._configured_drift_baseline() == {"write": 1.0}  # gültig


def test_s1_env_baseline_im_lauf(tmp_path, monkeypatch):
    """S1: Env-Erwartung steuert Stufe 8 (verschoben ⇒ ask) — ohne Datei-Referenz."""
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setenv("LIFECYCLE_DRIFT_REFERENCE", str(tmp_path / "r.json"))
    monkeypatch.setenv("LIFECYCLE_DRIFT_BASELINE", '{"write": 1.0}')
    out = lr.run_cycle(
        "Q",
        "F",
        "F",
        classify_fn=_classify("non-write"),
        structured_dir=tmp_path / "s",
        tier3_dir=tmp_path / "t",
    )
    assert out["results"]["Wissen+"]["gate"] == "ask"  # gegen Env-Erwartung verschoben


# ---------------------------------------------------------------- B4/B5 (K6)


def test_b4_keine_graph_oder_wm_mutation_ohne_mandat(tmp_path, monkeypatch):
    """B4 (K6): Mandat vor JEDER Mutation – auch Graph (§9). Ohne Mandat kein Bootstrap."""
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("LIFECYCLE_DRIFT_BASELINE", raising=False)
    ref = tmp_path / "ref.json"
    monkeypatch.setenv("LIFECYCLE_DRIFT_REFERENCE", str(ref))
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
    graph = ingestion_hook.MemoryGraph()
    wm = lru_cache.WorkingMemory(capacity=15)
    wm.store("n1", "v1")
    out = lr.run_cycle(
        "Q?",
        "Fakt X",
        "x",
        classify_fn=_classify("write-new"),
        structured_dir=tmp_path / "s",
        tier3_dir=tmp_path / "t",
        wm=wm,
        graph=graph,
        relations=[("a", "related", "b")],
        edges=[("n1", "n1", "NEXT")],
        mandate_obj=deny,
    )
    w = out["results"]["Wissen"]
    assert w["skipped"] is True and w["added_edges"] == 0
    assert graph.nodes == {} and graph.edges == {}  # B4: keine Graph-Mutation
    k = out["results"]["Kognition"]
    assert k["skipped"] is True and k["strengthened"] == []
    assert wm.items["n1"].get("edge_weight", 1.0) == 1.0  # unverändert (keine Konsolidierung)
    assert out["results"]["Wissen+"]["reference"] == "blocked"
    assert not ref.exists()  # B4: kein Bootstrap ohne Mandat


# ------------------------------------------ R04/R16: Drift VOR dem Write, ein Labelraum
def test_r04_default_drift_gatet_vor_write(tmp_path, monkeypatch):
    """R04: die Default-Env-Erwartung muss VOR der Mutation (Stufe 3) greifen."""
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setenv("LIFECYCLE_DRIFT_BASELINE", '{"write": 0.5, "non-write": 0.5}')
    out = lr.run_cycle(
        "Q",
        "F",
        "F",
        classify_fn=_classify("write-new"),
        structured_dir=tmp_path / "s",
        tier3_dir=tmp_path / "t",
        tau=0.01,  # Verschiebung {write:1.0} vs Baseline → ask VOR dem Write
    )
    assert out["results"]["Gedächtnis"]["ok"] is False
    assert not (tmp_path / "s").exists()  # kein Write vor der Freigabe (§9.1c)


def test_r16_ein_labelraum_vor_und_nach_write(tmp_path, monkeypatch):
    """R16: derselbe Labelraum vor/nach dem Write → kein falsches `ask`."""
    import bias_monitor

    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    drift = bias_monitor.BiasDriftMonitor(baseline={"write": 1.0}, tau=0.10)
    out = lr.run_cycle(
        "Q",
        "F",
        "F",
        classify_fn=_classify("write-new"),
        structured_dir=tmp_path / "s",
        tier3_dir=tmp_path / "t",
        drift=drift,
        tau=0.10,
    )
    assert out["results"]["Gedächtnis"]["ok"] is True  # {write} == Baseline → allow
    assert out["results"]["Wissen+"]["gate"] == "allow"


def test_drift_label_kanonisierung():
    """R16: `_drift_label` bildet beide Write-Schreibweisen auf EINEN Labelraum ab."""
    assert lr._drift_label("write-new") == "write"
    assert lr._drift_label("write-update") == "write"
    assert lr._drift_label("non-write") == "non-write"
    assert lr._drift_label("none") == "non-write"
    assert lr._drift_label("unbekannt") == "unbekannt"


# ------------------------------------------------ R07/R18: State-Save sichtbar + deny
def test_r07_state_save_wird_berichtet_und_cas_fortgesetzt(tmp_path, monkeypatch):
    """R07: `run_cycle` meldet das `save`-Ergebnis (kein Verschweigen); rev wächst monoton."""
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setenv("LIFECYCLE_DRIFT_REFERENCE", str(tmp_path / "d.json"))
    p = tmp_path / "state.json"
    out = lr.run_cycle(
        "Q",
        "F",
        "F",
        classify_fn=_classify("write-new"),
        structured_dir=tmp_path / "s",
        tier3_dir=tmp_path / "t",
        state_path=p,
    )
    assert out["state_save"]["ok"] is True and out["state_save"]["rev"] == 1
    out2 = lr.run_cycle(
        "Q2",
        "F",
        "F",
        classify_fn=_classify("write-new"),
        structured_dir=tmp_path / "s2",
        tier3_dir=tmp_path / "t2",
        state_path=p,
    )
    assert out2["state_save"]["rev"] == 2  # CAS via gelesener Revision


def test_r18_deny_persistiert_keinen_state(tmp_path, monkeypatch):
    """R18: abgelehnter Akt (Gedächtnis ok=False) → kein neuer Wissenszustand."""
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
    p = tmp_path / "state.json"
    out = lr.run_cycle(
        "Q",
        "F",
        "x",
        classify_fn=_classify("write-new"),
        structured_dir=tmp_path / "s",
        tier3_dir=tmp_path / "t",
        mandate_obj=deny,
        state_path=p,
    )
    assert out["results"]["Gedächtnis"]["ok"] is False
    assert out["state_save"]["ok"] is False and "kein neuer Wissenszustand" in out["state_save"]["reason"]
    assert not p.exists()  # R18: kein State-Write


def test_b5_deny_gate_revised_false(tmp_path, monkeypatch):
    """B5 (K6): deny-Gate ⇒ revised=False – auch bei ok=True (NIE `gate != ask`)."""
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    class _DenyMonitor:
        def observe(self, distribution, step=None):
            return {"DI": 0.5, "gate": "deny", "flagged": True}

    out = lr.run_cycle(
        "Q",
        "F",
        "F",
        classify_fn=_classify("non-write"),
        structured_dir=tmp_path / "s",
        tier3_dir=tmp_path / "t",
        drift=_DenyMonitor(),
    )
    w = out["results"]["Wissen+"]
    assert out["results"]["Gedächtnis"]["ok"] is True  # non-write läuft ohne Write durch
    assert w["gate"] == "deny" and w["revised"] is False  # B5: deny ⇒ nie revised
