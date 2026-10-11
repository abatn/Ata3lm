"""Slow Consolidation / Write-Back – Vorarbeit (§10.3, Status Auftrag).

Echte Dateisystem-Tests (kein Netz, kein Fake): tier3-Puffer + echte PROV-O-Records
(`provenance.build_record`) → collect → SFT-Dataset → mark → flush.

Quelle (Belegt): arXiv:2608.22215 §3.4 (Write-Back/Slow Consolidation).
Kaggle-Stub: ohne injizierten `train_fn` bleibt `write_back` → NotImplementedError
(das Θ→Θ′-Training läuft NICHT hier). Der **geschlossene Zyklus** ist über echte
`train_fn`/`probe_fn`-Injektion testbar (kein GPU, kein Fake-Ergebnis).
"""

import json
from pathlib import Path

import provenance
import pytest
import slow_consolidation as sc


def _write_tier3(tier3: Path, key: str, fact: str) -> Path:
    tier3.mkdir(parents=True, exist_ok=True)
    p = tier3 / f"{key}.md"
    p.write_text(fact, encoding="utf-8")
    return p


def _record(log: Path, *, fact: str, activity: str, source: str = "tool:verified", now: float = 10.0) -> dict:
    rec = provenance.build_record(fact=fact, activity=activity, agent="pipeline", source=source, now=now)
    provenance.append_record(log, rec)
    return rec


def _fixture(tmp_path: Path):
    """tier3: 3 aktive Fakten + 1 Archiv; PROV-Log mit write-new/write-update/non-write/untrusted/missing."""
    tier3 = tmp_path / "tier3"
    tier3.mkdir()
    log = tier3 / "provenance.jsonl"
    _write_tier3(tier3, "hauptstadt-xylophonia", "Zentaria ist die Hauptstadt Xylophoniens.")
    _write_tier3(tier3, "hauptstadt-frankreich", "Paris ist die Hauptstadt Frankreichs (neu).")
    _write_tier3(tier3, "untrusted-fakt", "Fakt aus unsicherer Quelle.")
    _write_tier3(tier3, "archiv-fakt", "alter Stand")
    # Archiv-Stand darf NICHT gesammelt werden:
    (tier3 / "hauptstadt-frankreich.superseded-9-abcd1234.md").write_text("Paris (alt)", encoding="utf-8")

    _record(log, fact="Zentaria ist die Hauptstadt Xylophoniens.", activity="write-new", now=1.0)
    _record(log, fact="Paris ist die Hauptstadt Frankreichs (neu).", activity="write-update", source="user", now=2.0)
    _record(log, fact="nur Historie", activity="non-write-history", source="tool:verified", now=3.0)
    _record(log, fact="Fakt aus unsicherer Quelle.", activity="write-new", source="web:untrusted", now=4.0)
    _record(log, fact="gibt es nicht im Puffer", activity="write-new", source="tool:verified", now=5.0)
    # Duplikat (gleicher Inhalt) → nur einmal sammeln:
    _record(log, fact="Zentaria ist die Hauptstadt Xylophoniens.", activity="write-new", now=6.0)
    return tier3, log


# ----------------------------------------------------------------- collect_pending
def test_collect_filter_trusted_write_und_datei(tmp_path):
    tier3, log = _fixture(tmp_path)
    pend = sc.collect_pending(tier3, log)
    keys = sorted(p["key"] for p in pend)
    # non-write-history, untrusted, missing-file, Archiv alle raus; Duplikat dedupliziert
    assert keys == ["hauptstadt-frankreich", "hauptstadt-xylophonia"]
    by = {p["key"]: p for p in pend}
    assert by["hauptstadt-xylophonia"]["class"] == "write-new"
    assert by["hauptstadt-xylophonia"]["source"] == "tool:verified"
    assert by["hauptstadt-frankreich"]["class"] == "write-update"
    # fact = echter Pufferinhalt; sha256 == content_hash(fact)
    for p in pend:
        assert p["fact"] == (tier3 / f"{p['key']}.md").read_text(encoding="utf-8")
        assert p["sha256"] == provenance.content_hash(p["fact"])
        assert p["question"]  # rekonstruiert/nicht leer


def test_collect_questions_overrides_rekonstruktion(tmp_path):
    tier3, log = _fixture(tmp_path)
    pend = sc.collect_pending(tier3, log, questions={"hauptstadt-xylophonia": "Was ist die Hauptstadt Xylophoniens?"})
    by = {p["key"]: p for p in pend}
    assert by["hauptstadt-xylophonia"]["question"] == "Was ist die Hauptstadt Xylophoniens?"
    # ohne Override: aus Key rekonstruiert
    assert by["hauptstadt-frankreich"]["question"] == "hauptstadt frankreich"


def test_collect_state_filtert_konsolidiertes(tmp_path):
    tier3, log = _fixture(tmp_path)
    state = tmp_path / "state.json"
    # F3: nur mit gebundenem Hash (+ positivem Probe) gilt der Fakt als konsolidiert.
    sc.mark_consolidated(
        ["hauptstadt-xylophonia"], state, facts={"hauptstadt-xylophonia": "Zentaria ist die Hauptstadt Xylophoniens."}
    )
    pend = sc.collect_pending(tier3, log, state_path=state)
    assert [p["key"] for p in pend] == ["hauptstadt-frankreich"]


def test_collect_leerer_puffer_und_fehlendes_log(tmp_path):
    assert sc.collect_pending(tmp_path / "leer", tmp_path / "leer" / "provenance.jsonl") == []


# ----------------------------------------------------------------- robuste Randfälle (tolerante Parser)
def test_read_jsonl_toleriert_defekte_und_nicht_dict_zeilen(tmp_path):
    """Kein Crash bei defekten Zeilen (kein Fake-Record, §6/§10.3)."""
    log = tmp_path / "prov.jsonl"
    good = provenance.build_record(fact="F", activity="write-new", agent="a", source="tool:verified", now=1.0)
    log.write_text(
        "\n"  # Leerzeile -> übersprungen
        + "{kaputt\n"  # defektes JSON -> übersprungen
        + "42\n"  # valides JSON, aber kein dict -> übersprungen
        + json.dumps(good, ensure_ascii=False)
        + "\n",
        encoding="utf-8",
    )
    recs = sc._read_jsonl(log)
    assert len(recs) == 1 and recs[0]["entity"]["sha256"] == good["entity"]["sha256"]


def test_read_jsonl_fehlende_datei_ist_leer(tmp_path):
    assert sc._read_jsonl(tmp_path / "gibt-es-nicht.jsonl") == []


def test_load_state_nicht_dict_ist_leer(tmp_path):
    state = tmp_path / "state.json"
    state.write_text("[1, 2, 3]", encoding="utf-8")  # valides JSON, aber keine Map
    assert sc._load_state(state) == {"consolidated": [], "entries": {}}


def test_load_state_legacy_und_defekte_entries(tmp_path):
    """N2-Rückwärtskompatibilität: altes Key-Listen-Format + tolerante `entries`."""
    legacy = tmp_path / "legacy.json"
    legacy.write_text('{"consolidated": null}', encoding="utf-8")
    assert sc._load_state(legacy) == {"consolidated": [], "entries": {}}
    mixed = tmp_path / "mixed.json"
    mixed.write_text(
        json.dumps({"consolidated": ["k1"], "entries": {"k1": {"fact_sha256": "abc"}, "k2": "kein-dict"}}),
        encoding="utf-8",
    )
    got = sc._load_state(mixed)
    assert got["consolidated"] == ["k1"]
    assert got["entries"] == {"k1": {"fact_sha256": "abc", "model": None, "probe_passed": None}}


def test_flush_leerer_key_wird_uebersprungen(tmp_path):
    state = tmp_path / "state.json"
    sc.mark_consolidated([], state)  # gültige Beleg-Datei (leer)
    res = sc.flush(["", "fehlt"], tmp_path / "tier3", state_path=state)
    assert res["ok"] and res["blocked"] == ["fehlt"] and res["missing"] == [] and res["removed"] == []


def test_mark_consolidated_meta_n2(tmp_path):
    """N2: `facts`/`model`/`probe_passed` werden je Key verbucht (Hash-Bindung)."""
    state = tmp_path / "state.json"
    r = sc.mark_consolidated(
        ["k1", "k2"],
        state,
        facts={"k1": "Inhalt 1"},  # k2 fehlt im Mapping ⇒ Hash bleibt unbekannt
        model="qwen3-8B",
    )
    assert r["added"] == ["k1", "k2"]
    loaded = sc._load_state(state)
    assert loaded["entries"]["k1"]["fact_sha256"] == provenance.content_hash("Inhalt 1")
    assert loaded["entries"]["k1"]["model"] == "qwen3-8B"
    assert loaded["entries"]["k1"]["probe_passed"] is True
    assert loaded["entries"]["k2"]["fact_sha256"] is None


# ----------------------------------------------------------------- build_sft_dataset
def test_build_sft_dataset_format_und_hash(tmp_path):
    tier3, log = _fixture(tmp_path)
    pend = sc.collect_pending(tier3, log)
    out = tmp_path / "sft.jsonl"
    res = sc.build_sft_dataset(pend, out)
    assert res["ok"] and res["count"] == len(pend) == len(res["hashes"])
    lines = [json.loads(x) for x in out.read_text(encoding="utf-8").splitlines()]
    assert len(lines) == res["count"]
    canon = {
        "hauptstadt-xylophonia": "Zentaria ist die Hauptstadt Xylophoniens.",
        "hauptstadt-frankreich": "Paris ist die Hauptstadt Frankreichs (neu).",
    }
    for line in lines:
        msgs = line["messages"]
        assert [m["role"] for m in msgs] == ["user", "assistant"]
        assert msgs[1]["content"] == canon[line["key"]]  # Fakt real aus Puffer
        # Inhalts-Hash je Zeile == SHA-256 der kanonisch serialisierten messages
        expected = provenance.content_hash(json.dumps(msgs, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
        assert line["hash"] == expected
        assert line["class"] in ("write-new", "write-update")


def test_build_sft_dataset_ueberspringt_leere_eintraege(tmp_path):
    out = tmp_path / "sft.jsonl"
    res = sc.build_sft_dataset(
        [{"key": "a", "question": "", "fact": "F"}, {"key": "b", "question": "Q", "fact": ""}], out
    )
    assert res["count"] == 0 and res["hashes"] == [] and out.read_text(encoding="utf-8") == ""


# ----------------------------------------------------------------- mark_consolidated
def test_mark_nur_nach_erfolg(tmp_path):
    state = tmp_path / "state.json"
    bad = sc.mark_consolidated(["f1"], state, success=False)
    assert bad["ok"] is False and bad["added"] == [] and not state.exists()
    good = sc.mark_consolidated(["f1", "f1", "f2"], state)
    assert good["ok"] and good["added"] == ["f1", "f2"]
    # idempotent
    again = sc.mark_consolidated(["f1"], state)
    assert again["added"] == [] and again["consolidated"] == ["f1", "f2"]


# ----------------------------------------------------------------- flush
def test_flush_entfernt_nur_konsolidierte(tmp_path):
    tier3, _log = _fixture(tmp_path)
    state = tmp_path / "state.json"
    # F1: Löschen nur bei Hash-Gleichheit eines positiven Probes.
    sc.mark_consolidated(
        ["hauptstadt-xylophonia"], state, facts={"hauptstadt-xylophonia": "Zentaria ist die Hauptstadt Xylophoniens."}
    )
    res = sc.flush(["hauptstadt-xylophonia"], tier3, state_path=state)
    assert res["removed"] == ["hauptstadt-xylophonia"]
    assert not (tier3 / "hauptstadt-xylophonia.md").exists()
    # nicht markierter Key bleibt stehen (blocked) – §10.3: fehlgeschlagen ⇒ bleibt
    blocked = sc.flush(["hauptstadt-frankreich"], tier3, state_path=state)
    assert blocked["blocked"] == ["hauptstadt-frankreich"] and blocked["removed"] == []
    assert (tier3 / "hauptstadt-frankreich.md").exists()
    # Archiv-Stand bleibt unangetastet
    assert list(tier3.glob("*.superseded-*.md"))


def test_flush_ohne_state_verweigert_n3(tmp_path):
    """N3 (Audit b09a0a9): ohne Erfolgsbeleg wird NICHTS gelöscht."""
    tier3, _log = _fixture(tmp_path)
    res = sc.flush(["hauptstadt-frankreich", "gibt-es-nicht"], tier3)
    assert res["ok"] is False and res["removed"] == [] and res["missing"] == []
    assert res["blocked"] == ["hauptstadt-frankreich", "gibt-es-nicht"]
    assert (tier3 / "hauptstadt-frankreich.md").exists()  # kein ungeprüftes Löschen


# ----------------------------------------------------------------- Kaggle-Stub
def test_write_back_ist_stub_kein_fake(tmp_path):
    with pytest.raises(NotImplementedError) as exc:
        sc.write_back(tmp_path / "sft.jsonl", model="qwen3-8B")
    assert sc.TRAIN_LOCATION in str(exc.value)


# --------------------------------------------- write_back: geschlossener Zyklus (§10.3)
def test_write_back_ohne_trainer_ist_stub_auch_mit_pfaden(tmp_path):
    """Ohne train_fn greift der ehrliche Stub – unabhängig von Puffer/Log (kein FS-Zugriff)."""
    with pytest.raises(NotImplementedError) as exc:
        sc.write_back(
            tmp_path / "sft.jsonl",
            model="qwen3-8B",
            tier3_dir=tmp_path / "tier3",
            provenance_log=tmp_path / "prov.jsonl",
        )
    assert sc.TRAIN_LOCATION in str(exc.value)


def test_write_back_leer_pending_note_kein_training(tmp_path):
    """Ohne Puffer/Log nichts zu tun ⇒ Note; das Training wird NICHT aufgerufen (§10.3)."""
    calls = []
    res = sc.write_back(tmp_path / "sft.jsonl", train_fn=lambda *a, **k: calls.append(a) or {"ok": True})
    assert res == {"ok": True, "flushed": [], "kept": [], "note": "keine pending"}
    assert calls == []  # kein Trainingslauf ohne pending


def test_write_back_train_fail_kein_flush(tmp_path):
    """Trainingsmisserfolg ⇒ fail-closed: kein Mark, kein Flush, Fakten bleiben (§10.3)."""
    tier3, log = _fixture(tmp_path)
    state = tmp_path / "state.json"
    dataset = tmp_path / "sft.jsonl"

    def train_fail(path, model):
        assert Path(path) == dataset and dataset.exists()  # Korpus real geschrieben
        return {"ok": False, "loss": 0.5, "adapter_path": "/should/not/leak"}

    res = sc.write_back(dataset, tier3_dir=tier3, provenance_log=log, state_path=state, train_fn=train_fail)
    assert res["ok"] is False and res["flushed"] == []
    assert sorted(res["kept"]) == ["hauptstadt-frankreich", "hauptstadt-xylophonia"]
    assert not state.exists()  # kein Erfolg verbucht
    assert (tier3 / "hauptstadt-xylophonia.md").exists()
    assert (tier3 / "hauptstadt-frankreich.md").exists()


def test_write_back_probe_positiv_flusht(tmp_path):
    """Positiver externer Probe ⇒ Hash-gebundenes Mark + Flush; loss/adapter durchgereicht."""
    tier3, log = _fixture(tmp_path)
    state = tmp_path / "state.json"
    seen = {}

    def probe(item):
        seen[item["key"]] = item["fact"]  # echte pending-Einträge, nichts erfunden
        return {"passed": True}

    res = sc.write_back(
        tmp_path / "sft.jsonl",
        "qwen3-8B",
        tier3_dir=tier3,
        provenance_log=log,
        state_path=state,
        train_fn=lambda path, model: {"ok": True, "loss": 0.123, "adapter_path": "/kaggle/adapter"},
        probe_fn=probe,
    )
    assert res["ok"] is True
    assert sorted(res["flushed"]) == ["hauptstadt-frankreich", "hauptstadt-xylophonia"]
    assert res["kept"] == []
    assert res["loss"] == 0.123 and res["adapter_path"] == "/kaggle/adapter"
    assert not (tier3 / "hauptstadt-xylophonia.md").exists()
    assert not (tier3 / "hauptstadt-frankreich.md").exists()
    assert seen == {
        "hauptstadt-xylophonia": "Zentaria ist die Hauptstadt Xylophoniens.",
        "hauptstadt-frankreich": "Paris ist die Hauptstadt Frankreichs (neu).",
    }


def test_write_back_probe_negativ_kein_flush(tmp_path):
    """Negativer Probe ⇒ kein Mark, kein Flush; Fakten bleiben im Puffer (§10.3)."""
    tier3, log = _fixture(tmp_path)
    state = tmp_path / "state.json"
    res = sc.write_back(
        tmp_path / "sft.jsonl",
        tier3_dir=tier3,
        provenance_log=log,
        state_path=state,
        train_fn=lambda path, model: {"ok": True, "loss": 0.001},
        probe_fn=lambda item: False,
    )
    assert res["ok"] is True and res["flushed"] == []
    assert sorted(res["kept"]) == ["hauptstadt-frankreich", "hauptstadt-xylophonia"]
    assert (tier3 / "hauptstadt-xylophonia.md").exists()
    assert not state.exists()  # nichts verbucht


def test_write_back_ohne_probe_fn_kein_flush(tmp_path):
    """Ohne probe_fn kein externes Signal ⇒ kein Flush (fail-closed)."""
    tier3, log = _fixture(tmp_path)
    state = tmp_path / "state.json"
    res = sc.write_back(
        tmp_path / "sft.jsonl",
        tier3_dir=tier3,
        provenance_log=log,
        state_path=state,
        train_fn=lambda path, model: {"ok": True},
    )
    assert res["flushed"] == [] and sorted(res["kept"]) == ["hauptstadt-frankreich", "hauptstadt-xylophonia"]
    assert (tier3 / "hauptstadt-xylophonia.md").exists()


def test_write_back_ohne_state_kein_flush(tmp_path):
    """Ohne state_path kein Erfolgsbeleg ⇒ kein Verbuchen/Flush (N3, fail-closed)."""
    tier3, log = _fixture(tmp_path)
    res = sc.write_back(
        tmp_path / "sft.jsonl",
        tier3_dir=tier3,
        provenance_log=log,
        state_path=None,
        train_fn=lambda path, model: {"ok": True},
        probe_fn=lambda item: {"passed": True},
    )
    assert res["flushed"] == []
    assert sorted(res["kept"]) == ["hauptstadt-frankreich", "hauptstadt-xylophonia"]
    assert (tier3 / "hauptstadt-xylophonia.md").exists()


# ------------------------------------- fail-closed Pfade (F1/F2/F3, Einheit)
def test_is_consolidated_fail_closed_early_returns():
    """F3: kein Eintrag / negativer Probe / unbekannter Hash ⇒ False; sonst Hash-Gleichheit."""
    assert sc._is_consolidated(None, "h") is False  # kein Eintrag
    assert sc._is_consolidated({}, "h") is False  # leerer Eintrag
    assert sc._is_consolidated({"fact_sha256": "h", "probe_passed": False}, "h") is False
    assert sc._is_consolidated({"fact_sha256": None, "probe_passed": True}, "h") is False
    assert sc._is_consolidated({"fact_sha256": "h", "probe_passed": True}, "h") is True
    assert sc._is_consolidated({"fact_sha256": "h", "probe_passed": True}, "other") is False


def test_mark_negative_probe_demotes_prior(tmp_path):
    """F2: negativer Probe stuft eine frühere Konsolidierung herab (kein Flush)."""
    state = tmp_path / "state.json"
    sc.mark_consolidated(["k1"], state, facts={"k1": "F"})
    assert sc._load_state(state)["consolidated"] == ["k1"]
    sc.mark_consolidated(["k1"], state, facts={"k1": "F"}, probe_passed=False)  # Herabstufung
    # Negativer Probe für einen NICHT zuvor konsolidierten Key ⇒ kein Remove (elif False).
    sc.mark_consolidated(["k2"], state, facts={"k2": "G"}, probe_passed=False)
    loaded = sc._load_state(state)
    assert loaded["consolidated"] == []
    assert loaded["entries"]["k1"]["probe_passed"] is False
    assert loaded["entries"]["k2"]["probe_passed"] is False


def test_flush_superseded_archive_nie_loeschen(tmp_path):
    """N3: Archivstände (`.superseded-`) werden nie gelöscht (blocked)."""
    tier3 = tmp_path / "tier3"
    tier3.mkdir()
    arch = tier3 / "x.superseded-1-abcd.md"
    arch.write_text("alt", encoding="utf-8")
    state = tmp_path / "state.json"
    sc.mark_consolidated([], state)
    res = sc.flush(["x.superseded-1-abcd"], tier3, state_path=state)
    assert res["blocked"] == ["x.superseded-1-abcd"] and res["removed"] == []
    assert arch.exists()


def test_flush_fehlende_datei_meldet_missing(tmp_path):
    """F1: fehlende Datei ⇒ `missing` (bereits weg); weder entfernt noch blockiert."""
    tier3 = tmp_path / "tier3"
    tier3.mkdir()
    state = tmp_path / "state.json"
    sc.mark_consolidated(["weg"], state, facts={"weg": "Inhalt"})
    res = sc.flush(["weg"], tier3, state_path=state)
    assert res["missing"] == ["weg"] and res["removed"] == [] and res["blocked"] == []


def test_flush_hash_mismatch_blocked(tmp_path):
    """F1: geänderter Fakt (Hash-Mismatch) ⇒ blocked, Datei bleibt."""
    tier3 = tmp_path / "tier3"
    tier3.mkdir()
    f = tier3 / "f.md"
    f.write_text("neu", encoding="utf-8")
    state = tmp_path / "state.json"
    sc.mark_consolidated(["f"], state, facts={"f": "alt"})
    res = sc.flush(["f"], tier3, state_path=state)
    assert res["blocked"] == ["f"] and res["removed"] == []
    assert f.read_text(encoding="utf-8") == "neu"


# ----------------------------------------------------------------- Runner-Hooks (lesend)
def _mandate():
    import mandate

    return mandate.Mandate(
        mandate_id="t",
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


def test_recursion_runner_hook(tmp_path):
    import recursion_runner as rr

    tier3 = tmp_path / "tier3"
    log = tier3 / "provenance.jsonl"
    _write_tier3(tier3, "fakt-a", "Fakt A.")
    _record(log, fact="Fakt A.", activity="write-new")
    state = tmp_path / "state.json"

    out = rr.run_recursion(
        "Wo?",
        "Fakt A.",
        "Fakt A.",
        classify_fn=lambda q, f, c: {"class": "non-write"},
        mandate_obj=_mandate(),
        structured_dir=tmp_path / "structured",
        tier3_dir=tier3,
        consolidation_state_path=state,
    )
    assert [p["key"] for p in out["pending_consolidation"]] == ["fakt-a"]
    # Default (ohne Hook) ⇒ unverändertes Verhalten, kein neues Feld
    out2 = rr.run_recursion(
        "Wo?",
        "Fakt A.",
        "Fakt A.",
        classify_fn=lambda q, f, c: {"class": "non-write"},
        mandate_obj=_mandate(),
        structured_dir=tmp_path / "structured",
        tier3_dir=tier3,
    )
    assert "pending_consolidation" not in out2


def test_lifecycle_runner_hook(tmp_path, monkeypatch):
    import lifecycle_runner as lr

    # Isolation: der Cold-Start-Bootstrap darf NICHT die globale Referenz beschreiben.
    monkeypatch.setenv("LIFECYCLE_DRIFT_REFERENCE", str(tmp_path / "drift-reference.json"))
    tier3 = tmp_path / "tier3"
    log = tier3 / "provenance.jsonl"
    _write_tier3(tier3, "fakt-b", "Fakt B.")
    _record(log, fact="Fakt B.", activity="write-update")
    state = tmp_path / "state.json"

    out = lr.run_cycle(
        "Wo?",
        "Fakt B.",
        "Fakt B.",
        classify_fn=lambda q, f, c: {"class": "non-write"},
        structured_dir=tmp_path / "structured",
        tier3_dir=tier3,
        consolidation_state_path=state,
    )
    assert [p["key"] for p in out["pending_consolidation"]] == ["fakt-b"]
