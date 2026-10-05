"""CI-Preflight (scripts/ci_preflight.py): liest opencode.json, gibt keine Keys aus (F1)."""

import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace

_SPEC = importlib.util.spec_from_file_location(
    "ci_preflight", Path(__file__).resolve().parents[1] / "scripts" / "ci_preflight.py"
)
cip = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(cip)


def _fake_openai(monkeypatch, content="pong"):
    resp = SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=content))])
    completions = SimpleNamespace(create=lambda **kwargs: resp)
    client_cls = lambda **kwargs: SimpleNamespace(chat=SimpleNamespace(completions=completions))  # noqa: E731
    import openai

    monkeypatch.setattr(openai, "OpenAI", client_cls)


def test_preflight_liest_opencode_json_ohne_key_ausgabe(tmp_path, monkeypatch, capsys):
    cfg = tmp_path / "opencode.json"
    cfg.write_text(
        json.dumps(
            {"provider": {"nvidia-llama-nemotron": {"options": {"apiKey": "SECRET-xyz", "baseURL": "http://x/v1"}}}}
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(cip, "_CFG", cfg)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_BASE_URL", raising=False)
    _fake_openai(monkeypatch)
    rc = cip.main()
    out = capsys.readouterr().out
    assert rc == 0 and "SECRET-xyz" not in out  # Key wird nie ausgegeben


def test_preflight_ohne_key_fail(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(cip, "_CFG", tmp_path / "fehlt.json")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    assert cip.main() == 1
    assert "FAIL" in capsys.readouterr().out
