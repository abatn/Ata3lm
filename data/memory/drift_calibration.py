#!/usr/bin/env python3
"""Kalibrier-Harness für den Drift-Schwellwert (GDI / SAHOO, Gl. 14–16).

Quelle (**Belegt**): arXiv:2603.06333 (SAHOO, ICLR-2026-Workshop), Appendix B –
Gl. 14 ``w* = argmax_w Σ_i AUC(GDI_i(w), y_i^drift)``, Gl. 15
``τ* = argmax_τ F1(GDI > τ, y^drift)``, Gl. 16 95%-CI = 0.025-/0.975-Quantile
von ``B≈2000`` Bootstrap-Replikaten. In ``AGENTS.md`` §9.1c zitiert ⇒ **keine
neue Quelle**. Die Einzelsignale (Gl. 8–11), GDI (Gl. 12–13) und die
Kalibrier-Primitive (``calibrate_weights``, ``calibrate_tau``, ``bootstrap_ci``)
liefert ``data/memory/bias_monitor.py`` – dieses Modul ruft sie nur auf.

Status-Trennung (vgl. ``AGENTS.md`` §6/§9.1c):
  - **Belegt:** Gl. 8–16 (Drift-Signale, GDI, Gewichts-/τ-Kalibrierung,
    Bootstrap-CI); erfunden wird nichts.
  - **Auftrag (Projekt, §6):** Statt der im Paper genannten Experten-Annotation
    („obtained via expert annotation during calibration") dient ein **externes
    Grader-Signal** (Grader/Code-Run/DB) als Label. Mapping gesetzt: Grader
    „bestanden" (kein Drift) ⇒ ``y_drift = 0``, sonst ``y_drift = 1``.
  - **Auftrag:** Struktur-Features (Gl. 10) = Länge, Zeilenzahl,
    Codeblock-Anzahl, Listenpunkte; distributional-Sample (Gl. 11) = auf den
    gemeinsamen Maximalwert normierte Zeilen-Tokenzahlen. Beides legt die Quelle
    nicht fest.

Guardrail 7: ``embed_fn`` und ``grader_fn`` sind injizierbar. Der Default-Grader
(``world_state_oracle`` + ``evaluator_version``, echter LLM/Netz-Aufruf) wird nur
**lazy** gebaut und im Unit-Test NICHT aufgerufen – der echte Kalibrierlauf ist
separat.
"""

from __future__ import annotations

import re
from typing import Callable, Optional

import bias_monitor as bm

#: Struktur-Features (Gl. 10) – Auftrag: Länge, Zeilen, Codeblöcke, Listenpunkte.
STRUCT_KEYS = ("length", "lines", "code_blocks", "list_items")

#: Auftrag (§6): Label-Mapping. Grader bestanden (kein Drift) ⇒ 0, sonst 1.
LABEL_NO_DRIFT = 0
LABEL_DRIFT = 1

_LIST_RE = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+")
_TOKEN_RE = re.compile(r"\w+")

_NOTE_EMPTY = (
    "keine Samples: Gewichte = Default (Auftrag), τ = 0.0, CI = [0.0, 0.0]; "
    "τ wird erst im ECHTEN Kalibrierlauf gesetzt."
)
_NOTE = (
    "τ* datengetrieben nach Gl. 15; im echten Lauf mit externem Grader-Signal "
    "(§6) gesetzt, hier nur Harness. Gl.-16-CI über das GDI-Mittel (die Statistik "
    "je Replikat benennt die Quelle nicht). Label-Mapping (Auftrag): "
    "Grader bestanden ⇒ y_drift=0, sonst 1."
)


def _tokens(text: str) -> list:
    """Einfache Tokenisierung (``\\w+``, kleingeschrieben) für Gl. 9 – Auftrag."""
    return _TOKEN_RE.findall(text.lower())


def structural_features(text: str) -> dict:
    """Struktur-Features (Gl. 10, Auftrag): Länge, Zeilen, Codeblöcke, Listenpunkte.

    - ``length``: Zeichenzahl (``len(text)``).
    - ``lines``: Zeilenzahl (``len(text.splitlines())``).
    - ``code_blocks``: Paare von ``` ``` ` ```-Zäunen (``text.count("```") // 2``).
    - ``list_items``: Zeilen, die mit ``-``/``*``/``+`` oder ``1.``/``1)`` beginnen.
    """
    lines = text.splitlines()
    list_items = 0
    for ln in lines:
        if _LIST_RE.match(ln):
            list_items += 1
    return {
        "length": float(len(text)),
        "lines": float(len(lines)),
        "code_blocks": float(text.count("```") // 2),
        "list_items": float(list_items),
    }


def _line_lengths(text: str) -> list:
    """Tokenzahl je nicht-leerer Zeile (1-D-Sample für Gl. 11, Auftrag)."""
    out = []
    for ln in text.splitlines():
        toks = _tokens(ln)
        if toks:
            out.append(float(len(toks)))
    return out


def _distributional(prev_text: str, cur_text: str) -> float:
    """Gl. 11 auf normierten Zeilen-Tokenzahlen (Auftrag, Wertebereich [0, 1]).

    Beide Samples werden auf den gemeinsamen Maximalwert skaliert und an
    ``bias_monitor.distributional_drift`` (1-D-Wasserstein, closed form)
    übergeben. Leere Eingaben ⇒ 0.0.
    """
    a = _line_lengths(prev_text)
    b = _line_lengths(cur_text)
    scale = max(a + b, default=0.0)
    if scale <= 0.0:
        return 0.0
    return bm.distributional_drift([x / scale for x in a], [x / scale for x in b])


def signal_vector(prev_text: str, cur_text: str, *, embed_fn: Callable) -> dict:
    """Vier Drift-Signale (Gl. 8–11) für ein Textpaar.

    ``embed_fn`` bildet Text → Embedding-Vektor (injizierbar). Rückgabe:
    ``{"semantic", "lexical", "structural", "distributional"}``, je in [0, 1].
    """
    sem = bm.semantic_drift(embed_fn(prev_text), embed_fn(cur_text))
    lex = bm.lexical_drift(_tokens(prev_text), _tokens(cur_text))
    stru = bm.structural_drift(structural_features(prev_text), structural_features(cur_text))
    dist = _distributional(prev_text, cur_text)
    return {"semantic": sem, "lexical": lex, "structural": stru, "distributional": dist}


def gdi_of(prev_text: str, cur_text: str, *, embed_fn: Callable, weights: Optional[dict] = None) -> float:
    """GDI (Gl. 12–13) für ein Textpaar; ``weights=None`` ⇒ Default (Auftrag)."""
    sig = signal_vector(prev_text, cur_text, embed_fn=embed_fn)
    return bm.gdi(sig["semantic"], sig["lexical"], sig["structural"], sig["distributional"], weights=weights)


def _scores_and_labels(samples: list, embed_fn: Callable, grade: Callable) -> tuple:
    """Gl. 12–14: je Sample den Signal-Dict + das externe Drift-Label.

    ``grade(prev, cur, reference)`` ist das **externe** Signal (§6). Mapping
    (Auftrag): bestanden ⇒ ``y_drift = 0``, sonst ``1``.
    """
    scores, labels = [], []
    for s in samples:
        sig = signal_vector(s["prev"], s["cur"], embed_fn=embed_fn)
        scores.append(
            {
                "sem": sig["semantic"],
                "lex": sig["lexical"],
                "struct": sig["structural"],
                "dist": sig["distributional"],
            }
        )
        passed = bool(grade(s["prev"], s["cur"], s.get("reference")))
        labels.append(LABEL_NO_DRIFT if passed else LABEL_DRIFT)
    return scores, labels


def _resolve_grader_fn(grader_fn: Optional[Callable]) -> Callable:
    """Injizierter Grader oder (lazy) Default-Grader aus dem World-State-Oracle."""
    if grader_fn is None:
        return _default_grader_fn()
    return grader_fn


def _default_grader_fn() -> Callable:
    """Default-Grader (§6, Auftrag): ``world_state_oracle`` + LLM-Judge.

    Lazy import (erst bei Aufruf). Der zurückgegebene Grader nutzt einen echten
    LLM-Judge (``evaluator_version.make_llm_grader``) hinter
    ``world_state_oracle.evaluate``. Er wird im Unit-Test NICHT aufgerufen
    (Netz/Guardrail 7); der echte Kalibrierlauf ist separat.
    """
    import evaluator_version as ev
    import world_state_oracle as wso

    judge = ev.make_llm_grader(lambda item: bool(item.get("unchanged", True)))

    def _grade(prev, cur, reference):  # pragma: no cover - echter LLM/Netz-Aufruf
        claim = "Text schreibt den Zustand ohne Goal-Drift fort"
        item = {"id": "drift", "text": cur, "rubric": prev, "unchanged": prev == cur}

        def probe():
            return {"ok": bool(judge(item))}

        return bool(wso.evaluate(claim, probe)["ok"])

    return _grade


def collect_samples(samples: list, *, embed_fn: Callable, grader_fn: Optional[Callable] = None) -> tuple:
    """Gl. 12–14: ``(gdi_values, labels)`` aus ``samples`` + externem Grader.

    ``samples`` = Liste ``{"prev", "cur", optional "reference"}``. ``grader_fn``
    wird injiziert (Stub im Test) oder lazy als Default gebaut. Label-Mapping
    (Auftrag): Grader bestanden ⇒ 0, sonst 1.
    """
    grade = _resolve_grader_fn(grader_fn)
    scores, labels = _scores_and_labels(samples, embed_fn, grade)
    gdi_values = [bm.gdi(sc["sem"], sc["lex"], sc["struct"], sc["dist"]) for sc in scores]
    return gdi_values, labels


def calibrate(
    samples: list,
    *,
    embed_fn: Callable,
    grader_fn: Optional[Callable] = None,
    bootstrap_B: int = 2000,
) -> dict:
    """Gl. 14–16: Gewichte ``w*``, Schwelle ``τ*`` und Bootstrap-CI.

    - Gl. 14: ``bm.calibrate_weights(scores, labels)`` (AUC-Maximierung).
    - Gl. 15: ``bm.calibrate_tau(gdi_values, labels)`` (F1-Maximierung).
    - Gl. 16: ``bm.bootstrap_ci(gdi_values, B=bootstrap_B)``.

    Rückgabe: ``{"weights", "tau", "ci", "n", "note", "auc", "f1"}``.
    """
    if not samples:
        return {
            "weights": dict(bm.DEFAULT_WEIGHTS),
            "tau": 0.0,
            "ci": {"lo": 0.0, "hi": 0.0},
            "n": 0,
            "note": _NOTE_EMPTY,
        }
    grade = _resolve_grader_fn(grader_fn)
    scores, labels = _scores_and_labels(samples, embed_fn, grade)
    cw = bm.calibrate_weights(scores, labels)
    w = cw["weights"]
    gdi_values = [bm.gdi(sc["sem"], sc["lex"], sc["struct"], sc["dist"], weights=w) for sc in scores]
    ct = bm.calibrate_tau(gdi_values, labels)
    ci = bm.bootstrap_ci(gdi_values, B=bootstrap_B)
    return {
        "weights": w,
        "tau": ct["tau"],
        "ci": ci,
        "n": len(samples),
        "note": _NOTE,
        "auc": cw["auc"],
        "f1": ct["f1"],
    }


if __name__ == "__main__":  # pragma: no cover - CLI
    import json

    print(json.dumps({"note": _NOTE}, ensure_ascii=False, indent=2))
