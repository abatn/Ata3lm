"""Retry/Backoff gegen transiente LLM-Endpoint-Fehler (data/memory/llm_retry.py).

Offline: der Client ist minimal gefakt (nur das Retry-Verhalten wird geprueft);
der echte Endpoint-Pfad bleibt in den Netz-Tests (Guardrail 7).
"""

import types

import llm_retry as lr
import pytest


class _FakeResp:
    def __init__(self, value):
        self.choices = [types.SimpleNamespace(message=types.SimpleNamespace(content=value))]


class _FakeExc(Exception):
    def __init__(self, msg, status=None):
        super().__init__(msg)
        self.status_code = status


class _FakeClient:
    """Minimal-Client: `create` liefert/`raises` die Items der Reihe nach."""

    def __init__(self, seq):
        self._seq = list(seq)
        self.calls = 0
        self.models = []
        self.chat = types.SimpleNamespace(completions=self)

    def create(self, **kwargs):
        self.calls += 1
        self.models.append(kwargs.get("model"))
        item = self._seq.pop(0)
        if isinstance(item, Exception):
            raise item
        return item


def test_is_transient_klassifikation():
    assert lr.is_transient(_FakeExc("x", 503)) is True
    assert lr.is_transient(_FakeExc("Error code: 404 page not found")) is True
    assert lr.is_transient(_FakeExc("bad request", 400)) is False


def test_create_with_retry_erster_erfolg(monkeypatch):
    monkeypatch.setattr(lr.time, "sleep", lambda *_: None)
    client = _FakeClient([_FakeResp("ok")])
    assert lr.create_with_retry(client, model="m").choices[0].message.content == "ok"
    assert client.calls == 1


def test_create_with_retry_nach_transient(monkeypatch):
    monkeypatch.setattr(lr.time, "sleep", lambda *_: None)
    client = _FakeClient([_FakeExc("503", 503), _FakeResp("ok")])
    assert lr.create_with_retry(client, model="m").choices[0].message.content == "ok"
    assert client.calls == 2


def test_create_with_retry_erschoepft_raise(monkeypatch):
    monkeypatch.setattr(lr.time, "sleep", lambda *_: None)
    client = _FakeClient([_FakeExc("503", 503) for _ in range(lr.RETRY_ATTEMPTS)])
    with pytest.raises(_FakeExc):
        lr.create_with_retry(client, model="m")
    assert client.calls == lr.RETRY_ATTEMPTS


def test_create_with_retry_nicht_transient_sofort(monkeypatch):
    monkeypatch.setattr(lr.time, "sleep", lambda *_: None)
    client = _FakeClient([_FakeExc("bad request", 400)])
    with pytest.raises(_FakeExc):
        lr.create_with_retry(client, model="m")
    assert client.calls == 1


def test_create_with_retry_modellkette_fallback(monkeypatch):
    """404 am ersten Modell -> naechstes Modell der Kette (echter Fallback)."""
    monkeypatch.setattr(lr.time, "sleep", lambda *_: None)
    client = _FakeClient([_FakeExc("404 page not found"), _FakeResp("ok")])
    out = lr.create_with_retry(client, models=["primary", "fallback"])
    assert out.choices[0].message.content == "ok"
    assert client.models == ["primary", "fallback"]
