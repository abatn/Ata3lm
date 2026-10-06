"""Gate-Labelraum (K6/B5): `allow|ask|deny` – Normalisierung + fail-safe.

Auftrag K6 (Interface-Änderung genehmigt durch Auftrag K1–K7, 2026-10-06):
ein Labelraum für alle Gate-Felder; unbekannte Labels ⇒ `ask` (nie still erlaubt).
"""

import gate_labels as gl


def test_labelraum_genau_drei_labels():
    assert gl.GATE_LABELS == ("allow", "ask", "deny")


def test_normalize_kanonische_labels():
    assert gl.normalize("allow") == "allow"
    assert gl.normalize("ask") == "ask"
    assert gl.normalize("deny") == "deny"


def test_normalize_altlabelraeume_k6_befund():
    """ok|ask (bias_monitor/lyapunov) · none|ask (fwr) · ALLOW|REVIEW|DENY (mandate)."""
    assert gl.normalize("ok") == "allow"
    assert gl.normalize("none") == "allow"
    assert gl.normalize("ALLOW") == "allow"
    assert gl.normalize("REVIEW") == "ask"
    assert gl.normalize("DENY") == "deny"


def test_normalize_unbekannt_fail_safe_ask():
    for raw in ("was-auch-immer", "", None, 42, "OK!?"):
        assert gl.normalize(raw) == "ask", f"unbekanntes Label nicht fail-safe: {raw!r}"


def test_normalize_trimmt_whitespace():
    assert gl.normalize("  allow  ") == "allow"
    assert gl.normalize("\task\n") == "ask"


def test_is_allow_nur_explizites_allow():
    assert gl.is_allow("allow") is True
    assert gl.is_allow("ok") is True  # Alt-Label
    assert gl.is_allow("none") is True  # Alt-Label
    assert gl.is_allow("ask") is False
    assert gl.is_allow("deny") is False  # `gate != "ask"`-Fehler wäre hier True!
    assert gl.is_allow("unbekannt") is False


def test_is_deny():
    assert gl.is_deny("deny") is True
    assert gl.is_deny("DENY") is True
    assert gl.is_deny("ask") is False
    assert gl.is_deny("allow") is False
    assert gl.is_deny("unbekannt") is False
