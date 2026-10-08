"""F1/F2/F3 (Audit 75095d5): fail-closed Inhalt-/Probe-Bindung der Konsolidierung.

Verbindliche Repro-Fälle mit **echten** tmp-Dateien (kein Netz, kein Mock):

  - **F1** `flush` löscht nur bei **Hash-Gleichheit** (`entries[key].fact_sha256` ==
    Hash des aktuellen Datei-Inhalts) **und** positivem Probe; ein nach dem Erfolg
    geänderter Fakt bleibt im Puffer.
  - **F2** `mark_consolidated(..., probe_passed=False)` verbucht den Key **nicht**
    als konsolidiert (und stuft eine frühere Konsolidierung **herab**) ⇒ kein
    Discard/Flush.
  - **F3** `_is_consolidated`: **unbekannter Hash ⇒ False** (fail-closed) ⇒
    Legacy-States ohne Hash sind **inert**; ein geänderter Fakt wird nicht versteckt.

Quellen (Belegt, im Gesetz): arXiv:2608.22215 §3.4 (Flush nur nach Erfolg, sonst
bleibt der Fakt; AGENTS.md §10.3); `connectors/gaama.md` (Kairos/Validation-Gated:
nur ein **positiver** Probe erlaubt Konsolidierung). Key-Zuordnung = Projekt-Auftrag.
"""

import json
from pathlib import Path

import fast_write_router as fwr
import provenance
import slow_consolidation as sc

KEY = "hauptstadt-frankreich"
OLD_FACT = "Paris ist die Hauptstadt Frankreichs."
NEW_FACT = "Lyon ist die neue Hauptstadt Frankreichs."
QUESTION = "Hauptstadt Frankreich?"


def _tier3(tmp_path: Path, fact: str, key: str = KEY):
    """Echte tier3-Datei + echter PROV-O-Record (write-new)."""
    tier3 = tmp_path / "tier3"
    tier3.mkdir(parents=True, exist_ok=True)
    (tier3 / f"{key}.md").write_text(fact, encoding="utf-8")
    log = tier3 / "provenance.jsonl"
    provenance.append_record(
        log,
        provenance.build_record(fact=fact, activity="write-new", agent="t", source="tool:verified", now=1.0),
    )
    return tier3, log


# --------------------------------------------------------------------- F1
def test_flush_preserves_fact_updated_after_success(tmp_path):
    """F1: Hash-Bindung – ein nach dem Erfolg geänderter Fakt wird NICHT geflusht.

    (rot gegen 75095d5: dort wurde allein der Key geprüft und der geänderte Fakt
    gelöscht; grün nach Fix: Hash-Mismatch ⇒ `blocked`, Datei bleibt.)
    """
    tier3, _log = _tier3(tmp_path, OLD_FACT)
    state = tmp_path / "state.json"
    sc.mark_consolidated([KEY], state, facts={KEY: OLD_FACT})

    # Fakt nach dem Erfolg geändert (write-update): der alte Hash passt nicht mehr.
    (tier3 / f"{KEY}.md").write_text(NEW_FACT, encoding="utf-8")
    res = sc.flush([KEY], tier3, state_path=state)
    assert res["removed"] == [] and res["blocked"] == [KEY]
    assert (tier3 / f"{KEY}.md").read_text(encoding="utf-8") == NEW_FACT

    # Nach erneutem Erfolg (neuer Hash gebunden) ist der Flush wieder erlaubt.
    sc.mark_consolidated([KEY], state, facts={KEY: NEW_FACT})
    res2 = sc.flush([KEY], tier3, state_path=state)
    assert res2["removed"] == [KEY] and not (tier3 / f"{KEY}.md").exists()


def test_flush_legacy_state_without_hash_is_blocked(tmp_path):
    """F1/F3: Legacy-State (reine Key-Liste, kein Eintrag/Hash) ⇒ inert ⇒ kein Löschen."""
    tier3 = tmp_path / "tier3"
    tier3.mkdir()
    f = tier3 / f"{KEY}.md"
    f.write_text(OLD_FACT, encoding="utf-8")
    state = tmp_path / "state.json"
    state.write_text(json.dumps({"consolidated": [KEY]}), encoding="utf-8")  # Legacy-Format

    res = sc.flush([KEY], tier3, state_path=state)
    assert res["removed"] == [] and res["blocked"] == [KEY] and f.exists()
    assert fwr.discard_if_consolidated(OLD_FACT, question=QUESTION, state_path=state) is None


# --------------------------------------------------------------------- F2
def test_failed_probe_cannot_enable_discard_or_flush(tmp_path):
    """F2: negativer Probe ⇒ weder als konsolidiert verbucht noch Discard/Flush.

    (rot gegen 75095d5: `probe_passed` wurde ignoriert und der Key als konsolidiert
    verbucht; grün nach Fix: kein Verbuchen, kein Discard, kein Löschen.)
    """
    tier3, _log = _tier3(tmp_path, OLD_FACT)
    state = tmp_path / "state.json"
    sc.mark_consolidated([KEY], state, facts={KEY: OLD_FACT}, probe_passed=False)

    loaded = sc._load_state(state)
    assert loaded["consolidated"] == []
    assert loaded["entries"][KEY]["probe_passed"] is False
    assert loaded["entries"][KEY]["fact_sha256"] == provenance.content_hash(OLD_FACT)

    res = sc.flush([KEY], tier3, state_path=state)
    assert res["removed"] == [] and res["blocked"] == [KEY]
    assert (tier3 / f"{KEY}.md").exists()
    assert fwr.discard_if_consolidated(OLD_FACT, question=QUESTION, state_path=state) is None


def test_probe_regression_demotes_prior_consolidation(tmp_path):
    """F2: ein späterer negativer Probe stuft eine frühere Konsolidierung herab."""
    tier3, _log = _tier3(tmp_path, OLD_FACT)
    state = tmp_path / "state.json"
    sc.mark_consolidated([KEY], state, facts={KEY: OLD_FACT}, probe_passed=True)
    assert sc._load_state(state)["consolidated"] == [KEY]

    sc.mark_consolidated([KEY], state, facts={KEY: OLD_FACT}, probe_passed=False)  # Probe-Regression
    assert sc._load_state(state)["consolidated"] == []
    assert sc.flush([KEY], tier3, state_path=state)["removed"] == []
    assert fwr.discard_if_consolidated(OLD_FACT, question=QUESTION, state_path=state) is None


# --------------------------------------------------------------------- F3
def test_consolidated_old_key_does_not_hide_updated_fact(tmp_path):
    """F3: gleicher Key, geänderter Fakt (neuer Hash) ⇒ wieder `pending`.

    (rot gegen 75095d5: bei unbekanntem Hash galt der Key als konsolidiert und der
    aktualisierte Fakt wurde ausgeblendet; grün nach Fix: fail-closed ⇒ sichtbar.)
    """
    tier3, log = _tier3(tmp_path, OLD_FACT)
    state = tmp_path / "state.json"
    sc.mark_consolidated([KEY], state, facts={KEY: OLD_FACT})

    # Unveränderter Fakt ist (hash-gebunden) konsolidiert ⇒ nicht mehr pending.
    assert sc.collect_pending(tier3, log, state_path=state) == []

    # Gleicher Key, NEUER Inhalt (write-update) ⇒ wieder konsolidierbar.
    (tier3 / f"{KEY}.md").write_text(NEW_FACT, encoding="utf-8")
    provenance.append_record(
        log,
        provenance.build_record(fact=NEW_FACT, activity="write-update", agent="t", source="tool:verified", now=2.0),
    )
    pend = sc.collect_pending(tier3, log, state_path=state)
    assert [p["key"] for p in pend] == [KEY]
    assert pend[0]["fact"] == NEW_FACT


def test_router_does_not_discard_changed_answer_for_old_key(tmp_path):
    """F3: der Router verwirft nur die inhaltsgleiche Antwort, nicht die geänderte."""
    state = tmp_path / "state.json"
    sc.mark_consolidated([KEY], state, facts={KEY: OLD_FACT})

    # Unveränderte Antwort ⇒ konsolidiert ⇒ non-write.
    d = fwr.discard_if_consolidated(OLD_FACT, question=QUESTION, state_path=state)
    assert d is not None and d["class"] == "non-write" and d["consolidated_key"] == KEY

    # Geänderte Antwort zum selben Key ⇒ NICHT verworfen (kein `non-write`).
    assert fwr.discard_if_consolidated(NEW_FACT, question=QUESTION, state_path=state) is None


def test_is_consolidated_unknown_hash_is_fail_closed():
    """F3 (Einheit): unbekannter Hash (None / kein Eintrag) ⇒ False, nicht True."""
    assert sc._is_consolidated(None, "abc") is False
    assert sc._is_consolidated({"fact_sha256": None, "probe_passed": True}, "abc") is False
    assert sc._is_consolidated({"fact_sha256": "abc", "probe_passed": None}, "abc") is False
    assert sc._is_consolidated({"fact_sha256": "abc", "probe_passed": True}, "abc") is True
    assert sc._is_consolidated({"fact_sha256": "abc", "probe_passed": True}, "other") is False
