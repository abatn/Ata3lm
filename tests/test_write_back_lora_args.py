"""Rek 127: additive LoRA-CLI-Args im Write-Back-Zyklus (AGENTS.md §9-Gate).

Testet NUR die reine Argument-Abbildung und ENV-Durchreichung (kein torch/GPU).
Defaults = bisheriges Verhalten (kein ENV-Override). Guardrail 4: keine
bestehende Signatur geändert.

Quellen:
- arXiv:2312.03732 (rsLoRA: use_rslora, alpha/sqrt(r))
- arXiv:2402.12354 (LoRA+: eta_B = lambda * eta_A)
- arXiv:2405.09673 (TMLR: Full-FT-Vergleich)
"""

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "kaggle"))

WBC_SCRIPT = ROOT / "kaggle" / "write_back_cycle.py"
TRAIN_SCRIPT = ROOT / "kaggle" / "train_slow_consolidation.py"


def _load_wbc():
    spec = importlib.util.spec_from_file_location("write_back_cycle_test", WBC_SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    # __file__ wird fuer ROOT-Berechnung gebraucht
    module.__file__ = str(WBC_SCRIPT)
    sys.modules["write_back_cycle_test"] = module
    spec.loader.exec_module(module)
    return module


def _load_train():
    spec = importlib.util.spec_from_file_location("train_slow_consolidation_test", TRAIN_SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# ---------------------------------------------------------------- write_back_cycle CLI
def test_wbc_parse_args_new_defaults_are_none():
    """Alle neuen LoRA-Args defaulten auf None (kein ENV-Override)."""
    wbc = _load_wbc()
    args = wbc._parse_args([])
    assert args.lora_r is None
    assert args.lora_alpha is None
    assert args.learning_rate is None
    assert args.use_rslora is False
    assert args.full_ft is False
    assert args.lora_plus_ratio is None


def test_wbc_parse_args_new_values_parse():
    """Neue Args werden korrekt geparst."""
    wbc = _load_wbc()
    args = wbc._parse_args(
        [
            "--lora-r",
            "64",
            "--lora-alpha",
            "256",
            "--learning-rate",
            "1e-4",
            "--use-rslora",
            "--full-ft",
            "--lora-plus-ratio",
            "10.0",
        ]
    )
    assert args.lora_r == 64
    assert args.lora_alpha == 256
    assert args.learning_rate == 1e-4
    assert args.use_rslora is True
    assert args.full_ft is True
    assert args.lora_plus_ratio == 10.0


def test_wbc_parse_args_existing_args_unchanged():
    """Guardrail 4: bestehende Args bleiben unverändert."""
    wbc = _load_wbc()
    args = wbc._parse_args(["--n", "50", "--gpu", "0", "--seed", "7", "--approver", "Batnini", "--approver", "Taoufik"])
    assert args.n == 50
    assert args.gpu == "0"
    assert args.seed == 7
    assert args.approver == ["Batnini", "Taoufik"]


# ---------------------------------------------------- write_back_cycle ENV pass-through
def test_wbc_train_fn_sets_env_only_when_args_set(tmp_path):
    """ENV wird nur gesetzt, wenn der Arg explizit gesetzt ist (additiv)."""
    wbc = _load_wbc()
    out_dir = tmp_path / "train_out"

    # Ohne Args: KEINE LoRA-ENV gesetzt (nur BASE_MODEL + SEED wie bisher).
    train_fn = wbc._make_train_fn(out_dir, gpu="0", seed=42, base_model="test-model")
    captured_env = {}

    # subprocess.run mocken, um env zu captchen
    import subprocess

    original_run = subprocess.run

    def mock_run(cmd, env=None, **kwargs):
        captured_env.clear()
        captured_env.update(env or {})

        class FakeProc:
            returncode = 1
            stderr = "mock"

        return FakeProc()

    subprocess.run = mock_run
    try:
        train_fn("dummy.jsonl", "test-model")
    finally:
        subprocess.run = original_run

    assert captured_env["BASE_MODEL"] == "test-model"
    assert captured_env["SEED"] == "42"
    # Keine Lora-ENV ohne Args
    assert "LORA_R" not in captured_env
    assert "LORA_ALPHA" not in captured_env
    assert "LEARNING_RATE" not in captured_env
    assert "LORA_USE_RSLORA" not in captured_env
    assert "FULL_FT" not in captured_env
    assert "LORA_PLUS_RATIO" not in captured_env


def test_wbc_train_fn_sets_env_when_args_provided(tmp_path):
    """ENV wird gesetzt, wenn Args explizit übergeben werden (rsLoRA gesperrt, P-132)."""
    wbc = _load_wbc()
    out_dir = tmp_path / "train_out"

    train_fn = wbc._make_train_fn(
        out_dir,
        gpu="0",
        seed=42,
        base_model="test-model",
        lora_r=64,
        lora_alpha=256,
        learning_rate=1e-4,
        use_rslora=False,
        full_ft=False,
        lora_plus_ratio=10.0,
    )
    captured_env = {}

    import subprocess

    original_run = subprocess.run

    def mock_run(cmd, env=None, **kwargs):
        captured_env.clear()
        captured_env.update(env or {})

        class FakeProc:
            returncode = 1
            stderr = "mock"

        return FakeProc()

    subprocess.run = mock_run
    try:
        train_fn("dummy.jsonl", "test-model")
    finally:
        subprocess.run = original_run

    assert captured_env["LORA_R"] == "64"
    assert captured_env["LORA_ALPHA"] == "256"
    assert captured_env["LEARNING_RATE"] == "0.0001"
    # P-132: rsLoRA ist im Write-Back-Pfad gesperrt ⇒ kein ENV-Override.
    assert "LORA_USE_RSLORA" not in captured_env
    assert captured_env["LORA_PLUS_RATIO"] == "10.0"
    assert "FULL_FT" not in captured_env  # full_ft=False


def test_wbc_train_fn_sets_full_ft_env(tmp_path):
    """FULL_FT=1 wird gesetzt, wenn --full-ft gesetzt."""
    wbc = _load_wbc()
    out_dir = tmp_path / "train_out"

    train_fn = wbc._make_train_fn(out_dir, gpu="0", seed=42, base_model="test-model", full_ft=True)
    captured_env = {}

    import subprocess

    original_run = subprocess.run

    def mock_run(cmd, env=None, **kwargs):
        captured_env.clear()
        captured_env.update(env or {})

        class FakeProc:
            returncode = 1
            stderr = "mock"

        return FakeProc()

    subprocess.run = mock_run
    try:
        train_fn("dummy.jsonl", "test-model")
    finally:
        subprocess.run = original_run

    assert captured_env["FULL_FT"] == "1"


# ------------------------------------------------------ train_slow_consolidation ENV
def test_train_env_defaults_match_previous_behavior():
    """Defaults in train_slow_consolidation.py = bisheriges Verhalten."""
    module = _load_train()
    assert module.LORA_R == 16
    assert module.LORA_ALPHA == 32
    assert module.LORA_DROPOUT == 0.05
    assert module.LORA_USE_RSLORA is False
    assert module.LORA_PLUS_RATIO == 0.0
    assert module.FULL_FT is False


def test_train_env_reads_lora_r_alpha(monkeypatch):
    """LORA_R / LORA_ALPHA werden aus ENV gelesen."""
    monkeypatch.setenv("LORA_R", "64")
    monkeypatch.setenv("LORA_ALPHA", "256")
    module = _load_train()
    assert module.LORA_R == 64
    assert module.LORA_ALPHA == 256


def test_train_env_reads_use_rslora(monkeypatch):
    """LORA_USE_RSLORA wird aus ENV gelesen (1/true/yes = True)."""
    monkeypatch.setenv("LORA_USE_RSLORA", "1")
    module = _load_train()
    assert module.LORA_USE_RSLORA is True

    monkeypatch.setenv("LORA_USE_RSLORA", "true")
    module2 = _load_train()
    assert module2.LORA_USE_RSLORA is True


def test_train_env_reads_full_ft(monkeypatch):
    """FULL_FT wird aus ENV gelesen (1 = True)."""
    monkeypatch.setenv("FULL_FT", "1")
    module = _load_train()
    assert module.FULL_FT is True


def test_train_env_reads_lora_plus_ratio(monkeypatch):
    """LORA_PLUS_RATIO wird aus ENV gelesen (float)."""
    monkeypatch.setenv("LORA_PLUS_RATIO", "10.5")
    module = _load_train()
    assert module.LORA_PLUS_RATIO == 10.5


def test_train_parse_args_unchanged():
    """Guardrail 4: train-Skript-CLI unverändert (keine neuen Args dort)."""
    module = _load_train()
    args = module.parse_args([])
    assert (args.dataset, args.out, args.source, args.gpu, args.epochs) == (None, None, None, None, None)
