"""Memory-Tests: 3-Tier-Struktur + Guards aus `data/memory/` (§9.1b, §9.2).

Rein lokal (Dateisystem + reine Funktionen), kein Netzwerk, keine Schreibweise
außer in temp-losen Assertions.
"""

from pathlib import Path

import bias_monitor as bm
import trust

ROOT = Path(__file__).resolve().parents[1]
MEM = ROOT / "data" / "memory"


# ------------------------------------------------------- Struktur / Version
def test_drei_tiers_und_shared_liegen_vor():
    for p in ["tier1-base", "tier2-index", "tier3-working", "shared"]:
        assert (MEM / p).is_dir(), p


def test_versionierung_v1_bis_v4_vorhanden():
    for v in ["v1", "v2", "v3", "v4"]:
        assert (MEM / "tier1-base/versions" / v).is_dir(), v


def test_gitignore_schliesst_artefakte_aus():
    """Working-Log + Shared-Store sind Artefakte und bleiben unversioniert."""
    gi = (ROOT / ".gitignore").read_text(encoding="utf-8")
    assert "data/memory/tier3-working/ingestion_log.jsonl" in gi
    assert "data/memory/shared/shared_store.jsonl" in gi


# ---------------------------------------------------------------- §9.2 Privacy
def test_pii_wird_erkannt_und_entfernt():
    pii = trust.PIIFilter()
    text = "Kontakt: max.mustermann@example.com, IBAN DE89370400440532013000"
    assert {"email", "iban"} <= set(pii.detect(text))  # Zusatz: Ziffernreihe trifft auch phone
    assert pii.detect("Ruf mich an: +49 30 1234567") == ["phone"]
    out = pii.minimize(text)
    assert "max.mustermann@example.com" not in out
    assert "DE89370400440532013000" not in out
    assert "Kontakt:" in out  # übriger Text bleibt (sparse)
    assert pii.anonymize(text) == out  # Alias löscht ebenfalls


def test_poisoning_guard_verwirft_unverifiziertes_und_fremde_quellen():
    g = trust.PoisoningGuard()
    assert g.admit({"source": "user", "verified": True})["admitted"] is True
    assert g.admit({"source": "web:untrusted", "verified": True})["admitted"] is False
    assert g.admit({"source": "user", "verified": False})["admitted"] is False


def test_bias_check_flagt_ueber_tau():
    bc = trust.BiasCheck(checkpoint=0.05, tau=0.10)
    assert bc.check(0.06)["status"] == "ok"
    assert bc.check(0.20)["status"] == "flag"


# --------------------------------------------------------------- §9.1c Drift
def test_jsd_null_bei_identischen_verteilungen():
    p = {"a": 0.5, "b": 0.5}
    assert bm.jsd(p, p) == 0.0
    assert bm.jsd(p, {"a": 1.0, "b": 0.0}) == bm.jsd({"a": 1.0, "b": 0.0}, p)


def test_capped_simplex_einacht_summe_und_w_max():
    v = bm.capped_simplex({"a": 1.0, "b": 0.01}, w_max=0.6)
    assert abs(sum(v.values()) - 1.0) < 1e-9
    assert max(v.values()) <= 0.6 + 1e-9
    assert v["a"] == 0.6


def test_drift_monitor_flagt_nur_ueber_tau():
    m = bm.BiasDriftMonitor(baseline={"a": 0.5, "b": 0.5}, tau=0.10)
    ok = m.observe({"a": 0.5, "b": 0.5}, step=1)
    assert ok["flagged"] is False and ok["gate"] == "allow"  # K6/B5: Labelraum allow|ask|deny
    assert ok["DI"] == 0.0
    bad = m.observe({"a": 1.0, "b": 0.0}, step=2)
    assert bad["DI"] > 0.10
    assert bad["flagged"] is True and bad["gate"] == "ask"
    rep = m.report()
    assert rep["steps"] == 2 and rep["flagged_steps"] == [2]


def test_entropy_und_grenzfaelle():
    assert bm.entropy({"a": 1.0}) == 0.0
    assert abs(bm.entropy({"a": 0.5, "b": 0.5}) - 1.0) < 1e-9
    assert bm.capped_simplex({}) == {}


def test_capped_simplex_mehrere_iterationen_und_obergrenze():
    v = bm.capped_simplex({"a": 1.0, "b": 1.0, "c": 1.0}, w_max=0.1)
    assert max(v.values()) <= 0.1 + 1e-9


def test_trust_demo_laeuft(capsys):
    trust._demo()
    out = capsys.readouterr().out
    assert "Privacy" in out and "Poisoning-Guard" in out and "Bias" in out


def test_bias_monitor_demo_laeuft(capsys):
    bm._demo()
    out = capsys.readouterr().out
    assert "Drift" in out


def test_capped_simplex_ohne_iterationen():
    """Branch 61->74: Schleife läuft nie (iters=0) -> keine Kappung."""
    v = bm.capped_simplex({"a": 1.0}, w_max=0.6, iters=0)
    assert v == {"a": 1.0}
