"""P-132: rsLoRA ist im Write-Back-Zyklus gesperrt (fail-closed).

Beleg (Quelle): kontrollierter A/B `P-131` (Lauf 2026-10-22) — identischer
Code/Daten/Seed/Umgebung, einzige Variable `LORA_USE_RSLORA`:
Arm rsLoRA (α/√r = 32) → 1/15 = 6,7 % mit Degeneration 13/15 "Jamaica";
Arm non-rsLoRA (α/r = 4) → 15/15 ohne Degeneration.
Doku: `ergebnisse/rekursion/132-ab-rslora-p1-bestaetigt.md` §4, Proposal
`ergebnisse/proposals/P-132-rslora-sperre-write-back.md` (§9.3: Batnini + Taoufik,
2026-10-22). arXiv:2312.03732 (rsLoRA: use_rslora, alpha/sqrt(r)).

Die Tests laufen **ohne** GPU und **ohne** LLM-Endpoint (Guardrail 7: keine Fake-
Antworten, nur echte Code-Pfade):
1. `_rslora_blocked()` liefert eine belegtragende Meldung.
2. `main(["--use-rslora"])` bricht **vor** jedem Seiteneffekt ab (kein Training).
3. `_make_train_fn(..., use_rslora=True)` wirft (Defense in Depth) und setzt den
   ENV **nicht**.
"""

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "kaggle"))

WBC_SCRIPT = ROOT / "kaggle" / "write_back_cycle.py"


def _load_wbc():
    spec = importlib.util.spec_from_file_location("write_back_cycle_rslora_guard", WBC_SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    module.__file__ = str(WBC_SCRIPT)
    sys.modules["write_back_cycle_rslora_guard"] = module
    spec.loader.exec_module(module)
    return module


def test_rslora_blocked_message_ist_belegtragend():
    """Die Sperr-Meldung nennt Ursache, Belege und den Forschungspfad."""
    wbc = _load_wbc()
    msg = wbc._rslora_blocked()
    assert msg
    assert "P-132" in msg
    assert "1/15" in msg and "15/15" in msg
    assert "kaggle/train_slow_consolidation.py" in msg


def test_main_bricht_vor_seiteneffekten_ab(capsys):
    """`--use-rslora` ⇒ Exit 1 mit FEHLER-Meldung, kein Training/ENV-Setup."""
    wbc = _load_wbc()
    rc = wbc.main(["--use-rslora"])
    assert rc == 1
    err = capsys.readouterr().err
    assert "FEHLER" in err
    assert "P-132" in err


def test_make_train_fn_wirft_und_setzt_kein_env(tmp_path):
    """Defense in Depth: `_make_train_fn` wirft und ruft kein Training auf."""
    wbc = _load_wbc()
    train_fn = wbc._make_train_fn(
        tmp_path / "train_out",
        gpu="0",
        seed=42,
        base_model="test-model",
        use_rslora=True,
    )

    calls = []
    import subprocess

    original_run = subprocess.run

    def mock_run(cmd, env=None, **kwargs):
        calls.append(env or {})
        raise AssertionError("Training darf bei gesperrtem rsLoRA nicht starten")

    subprocess.run = mock_run
    try:
        try:
            train_fn("dummy.jsonl", "test-model")
        except RuntimeError as exc:
            assert "P-132" in str(exc)
        else:
            raise AssertionError("RuntimeError erwartet")
    finally:
        subprocess.run = original_run

    assert not calls
