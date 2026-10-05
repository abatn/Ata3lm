"""Bi-temporale Semantik (data/memory/bi_temporal.py) – valid time × transaction time."""

import bi_temporal as bt


def _store():
    st = bt.BiTemporalStore()
    st.assert_fact("Ivan", "works_at", "Globex", valid_from="2024-01-01", recorded_at="2024-01-01")
    st.assert_fact("Ivan", "works_at", "Moonshot", valid_from="2024-03-01", recorded_at="2024-03-15")
    return st


def test_widerspruch_invalidiert_statt_loeschen():
    st = _store()
    assert len(st.facts) == 2  # nichts gelöscht
    alt = st.facts[0]
    assert alt.valid_to == "2024-03-01"  # Welt: endet, als der neue begann
    assert alt.superseded_at == "2024-03-15"  # Wissen: verworfen bei Speicherung
    assert st.facts[1].supersedes == 0


def test_kein_widerspruch_bei_gleichem_objekt():
    st = bt.BiTemporalStore()
    st.assert_fact("Ivan", "works_at", "Globex", "2024-01-01", "2024-01-01")
    r = st.assert_fact("Ivan", "works_at", "Globex", "2024-02-01", "2024-02-01")
    assert r["superseded"] is None  # gleiches Objekt → kein Supersede
    assert st.facts[0].superseded_at is None


def test_as_of_kennt_nur_was_wir_damals_wussten():
    st = _store()
    assert [f["obj"] for f in st.as_of("2024-02-01", "2024-02-01")] == ["Globex"]
    assert [f["obj"] for f in st.as_of("2024-04-01", "2024-04-01")] == ["Moonshot"]
    # Wissen vom 2024-04-01 kennt bereits den Supersede (2024-03-15) -> nichts mehr
    # F4: bei Kenntnis 2024-04-01 ist der alte Fakt (Globex, gültig bis 2024-03-01) korrekt.
    assert [f["obj"] for f in st.as_of("2024-02-01", "2024-04-01")] == ["Globex"]
    # Wissen vom 2024-03-01 (vor dem Supersede) hielt Globex noch für gültig
    assert [f["obj"] for f in st.as_of("2024-02-01", "2024-03-01")] == ["Globex"]


def test_as_of_vor_bekanntwerden_der_korrektur():
    """F4: Wissen vom 2024-03-10 (vor Kenntnis der Korrektur) → Globex, nicht []."""
    st = _store()
    assert [f["obj"] for f in st.as_of("2024-03-10", "2024-03-10")] == ["Globex"]


def test_world_state_und_knowledge_as_of_einzeln():
    st = _store()
    assert [f["obj"] for f in st.world_state_as_of("2024-02-01")] == ["Globex"]
    assert [f["obj"] for f in st.world_state_as_of("2024-04-01")] == ["Moonshot"]
    assert [f["obj"] for f in st.knowledge_as_of("2024-04-01")] == ["Moonshot"]


def test_demo_laeuft(capsys):
    bt._demo()
    out = capsys.readouterr().out
    assert "Retroaktives Update" in out and "as_of(valid=" in out
