"""N8 (Auftrag): Basismessung VOR `PeftModel.from_pretrained` (kaggle/e2e_theta_probe.py).

Echte Verifikation ohne GPU/Torch (lokal nicht installiert; der Skript-Lauf braucht
Kaggle-GPU — Guardrail 7: **kein** Fake-Modell, **keine** skripteten Antworten):

1) Struktur-Test (AST der **realen** Datei): `em_base = exact_match(base)` liegt
   zeilig VOR der Adapter-Erzeugung `PeftModel.from_pretrained`, `em_adapter` danach.
   Begründung: PeftModel wickelt dasselbe Basismodul ein (PEFT-Doku:
   https://huggingface.co/docs/peft/en/package_reference/peft_model, `disable_adapter`);
   eine Basismessung nach dem Laden misst MIT Adapter.
2) `load_rows` gegen echte JSONL-Dateien (tmp_path).

Der Laufzeit-Nachweis (`em_base` = unverändertes Basismodell) ist Teil des
GPU-Gesamtlaufs (§9 `ask` — Human-Gate).
"""

import ast
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SKRIPT = ROOT / "kaggle" / "e2e_theta_probe.py"


@pytest.fixture(scope="module")
def modul():
    spec = importlib.util.spec_from_file_location("e2e_theta_probe", SKRIPT)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)  # nur stdlib-Imports auf Modulebene -> kein torch noetig
    return m


def _messpositionen():
    """(em_base-Zeilen, PeftModel-Zeilen, em_adapter-Zeilen) aus dem echten AST von main()."""
    tree = ast.parse(SKRIPT.read_text(encoding="utf-8"))
    fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "main")
    em_base, peft, em_adapter = [], [], []
    for node in ast.walk(fn):
        if not isinstance(node, ast.Assign):
            continue
        for call in ast.walk(node.value):  # auch verschachtelte Aufrufe (.eval().cuda())
            if not isinstance(call, ast.Call):
                continue
            f = call.func
            if isinstance(f, ast.Name) and f.id == "exact_match" and call.args and isinstance(call.args[0], ast.Name):
                if call.args[0].id == "base":
                    em_base.append(node.lineno)
                elif call.args[0].id == "adapter":
                    em_adapter.append(node.lineno)
            if isinstance(f, ast.Attribute) and f.attr == "from_pretrained" and isinstance(f.value, ast.Name):
                if f.value.id == "PeftModel":
                    peft.append(node.lineno)
    return em_base, peft, em_adapter


def test_n8_basismessung_vor_peftmodel_vor_em_adapter():
    """N8: ALLE Basismessungen vor JEDEM PeftModel-Laden, em_adapter danach (echte Datei)."""
    em_base, peft, em_adapter = _messpositionen()
    assert em_base and peft and em_adapter, "Erwartete Aufrufe im Skript nicht gefunden"
    assert max(em_base) < min(peft)  # N8: em_base misst das unveraenderte Basismodell
    assert max(peft) < min(em_adapter)


def test_load_rows_erste_n_und_message_format(modul, tmp_path):
    p = tmp_path / "ds.jsonl"
    recs = [
        {"messages": [{"role": "user", "content": "F1?"}, {"role": "assistant", "content": "A1"}]},
        {"messages": [{"role": "user", "content": "F2?"}, {"role": "assistant", "content": "A2"}]},
        {"messages": [{"role": "user", "content": "F3?"}]},  # unvollstaendig -> verworfen
    ]
    p.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in recs), encoding="utf-8")
    rows = modul.load_rows(str(p), 2)
    assert rows == [("F1?", "A1"), ("F2?", "A2")]


def test_load_rows_fehlende_datei_system_exit(modul, tmp_path):
    with pytest.raises(SystemExit):
        modul.load_rows(str(tmp_path / "fehlt.jsonl"), 1)
