"""Tests für scripts/paired_gate.py (SAGE-Paired-Gate-CLI).

Quelle: SAGE arXiv:2609.36043; AGENTS.md §9.1d/§6. Kein Netz, kein Fake:
deterministische Standardbibliothek-Logik über echte JSONL-Dateien.
"""

import importlib.util
import json
import sys
from pathlib import Path

import pytest

_SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "paired_gate.py"
_spec = importlib.util.spec_from_file_location("paired_gate", _SCRIPT)
pg = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(pg)


# --------------------------------------------------------------------------- norm
def test_norm_kollabiert_und_entfernt_interpunktion():
    assert pg.norm("  Hello, World!  ") == "hello world"
    assert pg.norm("A.B") == "a b"


# -------------------------------------------------------------------------- grade
def test_grade_strict_normalisiert():
    assert pg.grade("Berlin", "berlin.", "strict") is True  # Interpunktion/Groß-klein normalisiert
    assert pg.grade("Berlin", "Bern", "strict") is False


def test_grade_substring():
    assert pg.grade("aircraft", "The company produces aircraft.", "substring") is True
    assert pg.grade("aircraft", "automobile engine", "substring") is False
    assert pg.grade("", "irgendwas", "substring") is False  # leeres Gold ⇒ nie positiv


def test_grade_unbekannter_modus_wirft():
    with pytest.raises(ValueError, match="unbekannter Modus"):
        pg.grade("a", "a", "exakt")


# ---------------------------------------------------------------------- load_rows
def test_load_rows_ueberspringt_leere_zeilen(tmp_path):
    p = tmp_path / "a.jsonl"
    p.write_text(
        json.dumps({"question": "q", "gold": "g", "base_answer": "b", "adapter_answer": "a"}) + "\n\n",
        encoding="utf-8",
    )
    rows = pg.load_rows(p)
    assert rows == [{"question": "q", "gold": "g", "base_answer": "b", "adapter_answer": "a"}]


# ------------------------------------------------------------------ evaluate_rows
def _rows(base_hits, cand_hits, n=200):
    rows = []
    for i in range(n):
        rows.append(
            {
                "question": f"q{i}",
                "gold": "treffer",
                "base_answer": "treffer" if i < base_hits else "falsch",
                "adapter_answer": "treffer" if i < cand_hits else "falsch",
            }
        )
    return rows


def test_evaluate_rows_accept_klarer_gewinn():
    res = pg.evaluate_rows(_rows(8, 40), mode="strict", alpha=0.05, n_resamples=500, seed=0)
    assert res["decision"] == "accept"
    assert res["n"] == 200 and res["mode"] == "strict"
    assert res["em_base"] == 8 and res["em_adapter"] == 40
    assert res["compare"]["wins"] == 32 and res["compare"]["losses"] == 0


def test_evaluate_rows_reject_klarer_verlust():
    res = pg.evaluate_rows(_rows(40, 8), mode="strict", alpha=0.05, n_resamples=500, seed=0)
    assert res["decision"] == "reject"
    assert res["em_base"] == 40 and res["em_adapter"] == 8


def test_evaluate_rows_abstain_bei_gleichstand():
    res = pg.evaluate_rows(_rows(10, 10, n=50), mode="substring", alpha=0.05, n_resamples=200, seed=0)
    assert res["decision"] == "abstain"
    assert res["mode"] == "substring"


# --------------------------------------------------------------------------- main
def test_main_schreibt_ergebnis(tmp_path):
    answers = tmp_path / "theta_answers.jsonl"
    answers.write_text(
        "\n".join(json.dumps(r) for r in _rows(8, 40)) + "\n",
        encoding="utf-8",
    )
    out = tmp_path / "res.json"
    rc = pg.main(["--answers", str(answers), "--out", str(out), "--n-resamples", "300", "--seed", "1"])
    assert rc == 0
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["decision"] == "accept"
    assert data["em_base"] == 8 and data["em_adapter"] == 40


def test_main_fehlende_datei_ist_fehler(tmp_path, capsys):
    rc = pg.main(["--answers", str(tmp_path / "nope.jsonl"), "--out", str(tmp_path / "x.json")])
    assert rc == 1
    assert "FEHLER" in capsys.readouterr().err


def test_main_leere_datei_ist_fehler(tmp_path, capsys):
    empty = tmp_path / "empty.jsonl"
    empty.write_text("\n\n", encoding="utf-8")
    rc = pg.main(["--answers", str(empty), "--out", str(tmp_path / "x.json")])
    assert rc == 1
    assert "FEHLER" in capsys.readouterr().err


def test_modul_in_sys_path_importierbar():
    """Der Script-Import fügt data/memory in sys.path ein (Import-Vertrag)."""
    assert any(p.endswith("data/memory") for p in sys.path)
