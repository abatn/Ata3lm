#!/usr/bin/env python3
"""Out-of-Band-Evaluation: World-State-Oracle (echtes externes Signal, §6).

Quellen (VOR Nutzung per curl geprüft, HTTP 200, 2026-10-07):
  - Park, H. & Choi, B.: „When Do Agent Loops Mistake Stagnation for Progress?
    Self-Evaluation Bias and Externally Grounded Verification in Long-Running
    Autonomous LLM Agent Loops", arXiv:2607.25152 (v2, 29.09.2026),
    DOI 10.48550/arXiv.2607.25152.
    Abstract wörtlich: „A **world-state oracle**, unfakeable in principle, is
    enforced by container and network isolation and verified at every run." und
    „For open-ended objectives whose success signal lives outside the transcript,
    scaling up the judge is not enough; **out-of-band evaluation with real-world
    access is a structural requirement**." Ebenso: „Self-report was thus
    uninformative."
    <https://arxiv.org/abs/2607.25152>
  - Zenodo Concept-DOI ``10.5281/zenodo.21594735`` (Deposit desselben Papers;
    der Concept-DOI löst auf die jeweils neueste Version auf).
    <https://doi.org/10.5281/zenodo.21594735>

Belegte Mechanik: Der Selbstreport des Agenten ist KEIN ausreichendes Signal;
Compare braucht ein **externes** Ergebnis (echter Code-Run / Datei-Check / DB),
das vom Agenten unabängig und „infakeable" ist (World-State-Oracle).

Status-Trennung (§6/§9.1): Die Existenz des World-State-Oracle + die
Notwendigkeit von Out-of-Band-Evaluation sind **Belegt** (Quelle oben). Die
Übersetzung in einen Score (``successes``/``failures`` → Gate-Band) ist
Projekt-**Auftrag**.

Guardrail 7: ``probe`` ist ein **echtes** Callable. Fehlt es, ist es nicht
aufrufbar oder schlägt es fehl, gibt es **kein** Signal (``ok=False``,
``signal="kein externes Signal"``) – kein Ersatz durch Selbstreport.
"""

from __future__ import annotations

from typing import Any, Callable, Optional

#: Sentinel-Signal: ohne echtes externes Probe liegt kein Signal vor (§1/§6).
NO_SIGNAL = "kein externes Signal"

Signal = "externes Signal (World-State-Oracle)"


def _interpret(raw: Any) -> tuple[bool, Any, int, int]:
    """Probe-Rückgabe → ``(ok, evidence, successes, failures)``.

    - ``dict`` mit ``"ok"``: ``ok`` maßgeblich; ``successes``/``failures``
      optional (Default: 1/0 bei Erfolg, 0/1 bei Misserfolg), ``evidence``
      optional (Default: das Dict selbst).
    - sonst: Wahrheitswert von ``raw`` (bool-artig).
    """
    if isinstance(raw, dict) and "ok" in raw:
        ok = bool(raw.get("ok"))
        successes = int(raw.get("successes", 1 if ok else 0))
        failures = int(raw.get("failures", 0 if ok else 1))
        return ok, raw.get("evidence", raw), successes, failures
    ok = bool(raw)
    successes = 1 if ok else 0
    failures = 0 if ok else 1
    return ok, {"result": raw}, successes, failures


def evaluate(claim: str, probe: Optional[Callable[[], Any]]) -> dict:
    """Prüft ``claim`` gegen ein **echtes** externes Probe (World-State-Oracle).

    ``probe`` wird ausgeführt (z. B. Code-Run, Datei-Check, DB-Query) und liefert
    entweder einen Wahrheitswert oder ein Dict ``{"ok": bool, ...}``.

    Rückgabe (immer): ``{"ok", "evidence", "signal", "reason", "claim",
    "successes", "failures"}``.

    **Kein Fake (§6/Guardrail 7):** ohne aufrufbares Probe oder bei Probe-Fehler
    ist ``ok=False`` und ``signal="kein externes Signal"`` – der Selbstreport des
    Agenten ersetzt das externe Signal NICHT.
    """
    if probe is None or not callable(probe):
        return {
            "ok": False,
            "evidence": None,
            "signal": NO_SIGNAL,
            "reason": "kein externes Signal (kein echtes Probe-Callable)",
            "claim": claim,
            "successes": 0,
            "failures": 0,
        }
    try:
        raw = probe()
    except Exception as e:  # noqa: BLE001 – jedes echte Probe darf scheitern
        return {
            "ok": False,
            "evidence": None,
            "signal": NO_SIGNAL,
            "reason": f"Probe-Fehler: {type(e).__name__}: {e}",
            "claim": claim,
            "successes": 0,
            "failures": 0,
        }
    ok, evidence, successes, failures = _interpret(raw)
    if ok:
        signal = Signal
        reason = None
    else:
        signal = NO_SIGNAL
        reason = "Probe lief, lieferte aber kein positives externes Ergebnis"
    return {
        "ok": ok,
        "evidence": evidence,
        "signal": signal,
        "reason": reason,
        "claim": claim,
        "successes": successes,
        "failures": failures,
    }


if __name__ == "__main__":  # pragma: no cover - CLI
    import json

    print(json.dumps(evaluate("2+2==4", lambda: 2 + 2 == 4), ensure_ascii=False, indent=2))
