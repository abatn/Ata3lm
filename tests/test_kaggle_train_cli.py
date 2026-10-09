"""Test fuer die CLI des Kaggle-Trainingsskripts (kaggle/train_slow_consolidation.py).

Prueft NUR die reine Argument-Abbildung (kein torch/GPU). Das Skript selbst
laeuft gemaess AGENTS.md §10.3 auf Kaggle (GPU). Kein Fake-Erfolg.
"""

import importlib.util
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "kaggle" / "train_slow_consolidation.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("train_slow_consolidation", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_parse_args_maps_cli_overrides():
    module = _load_module()
    args = module.parse_args(
        [
            "--dataset",
            "/k/x.jsonl",
            "--out",
            "/k/o",
            "--source",
            "local",
            "--gpu",
            "0",
            "--epochs",
            "2",
        ]
    )
    assert args.dataset == "/k/x.jsonl"
    assert args.out == "/k/o"
    assert args.source == "local"
    assert args.gpu == "0"
    assert args.epochs == 2.0


def test_parse_args_defaults_are_none():
    module = _load_module()
    args = module.parse_args([])
    assert (args.dataset, args.out, args.source, args.gpu, args.epochs) == (
        None,
        None,
        None,
        None,
        None,
    )


def test_parse_args_rejects_unknown_source():
    module = _load_module()
    with pytest.raises(SystemExit):
        module.parse_args(["--source", "bogus"])
