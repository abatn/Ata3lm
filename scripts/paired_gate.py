#!/usr/bin/env python3
"""Paired-Gate über Θ′-Probe-Antworten (SAGE, arXiv:2609.36043) — externer Grader (§6).

Liest die `--answers`-JSONL des Θ′-Probe-Dumps
(`kaggle/e2e_theta_probe.py --answers-out`); Schema je Zeile:
`{"question", "gold", "base_answer", "adapter_answer"}`.

Bewertet **per Item** beide Antworten mit einem **externen** Grader (Vergleich gegen
`gold`, §6) und ruft den SAGE-Gate `acceptance_gate.evaluate(base_flags, adapter_flags)`
→ `accept` / `reject` / `abstain`. Damit ersetzt der Entscheid den naiven
Aggregat-Vergleich (`em_base < em_adapter`), der Regressionen verschleiern kann.

**Kein Fake:** Gold stammt aus dem Datensatz; der Grader ist **Code** (striktes EM
oder Teilstring), kein LLM-Gefühl. Nur Standardbibliothek.

Quellen: SAGE arXiv:2609.36043; AGENTS.md §9.1d/§6; Rekursion 103/111.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "data" / "memory"))

import acceptance_gate  # noqa: E402

_PUNCT = re.compile(r"[^\w\s]", re.UNICODE)
_WS = re.compile(r"\s+")
_MODES = ("strict", "substring")


def norm(text: str) -> str:
    """Normalisieren für striktes EM: lowercase, Interpunktion weg, Whitespace kollabieren."""
    return _WS.sub(" ", _PUNCT.sub(" ", str(text).lower())).strip()


def grade(gold: str, pred: str, mode: str) -> bool:
    """Externer Grader (§6): striktes (normalisiertes) EM oder Teilstring."""
    if mode not in _MODES:
        raise ValueError(f"unbekannter Modus: {mode!r} (erlaubt: {_MODES})")
    if mode == "strict":
        return norm(gold) == norm(pred)
    gold_l, pred_l = str(gold).strip().lower(), str(pred).strip().lower()
    return bool(gold_l) and gold_l in pred_l


def load_rows(path: Path) -> list:
    """JSONL einlesen (leere Zeilen übersprungen)."""
    rows = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def evaluate_rows(rows: list, *, mode: str, alpha: float, n_resamples: int, seed: int) -> dict:
    """Per-Item-Grader + SAGE-Gate über bereits geladene Antwort-Zeilen."""
    base = [grade(r["gold"], r["base_answer"], mode) for r in rows]
    cand = [grade(r["gold"], r["adapter_answer"], mode) for r in rows]
    res = acceptance_gate.evaluate(base, cand, alpha=alpha, n_resamples=n_resamples, seed=seed)
    res["n"] = len(rows)
    res["mode"] = mode
    res["em_base"] = sum(base)
    res["em_adapter"] = sum(cand)
    return res


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Paired-Gate (SAGE) über Θ′-Probe-Antworten.")
    ap.add_argument("--answers", required=True, help="JSONL: question/gold/base_answer/adapter_answer")
    ap.add_argument("--mode", choices=list(_MODES), default="strict", help="Grader-Modus (Default: strict)")
    ap.add_argument("--alpha", type=float, default=0.05, help="Signifikanz (Default: 0.05)")
    ap.add_argument("--n-resamples", type=int, default=10000, help="Bootstrap-Resamples (Default: 10000)")
    ap.add_argument("--seed", type=int, default=0, help="Bootstrap-Seed (Default: 0)")
    ap.add_argument("--out", default="paired_gate_result.json", help="Ergebnis-JSON (Default: paired_gate_result.json)")
    args = ap.parse_args(argv)

    path = Path(args.answers)
    if not path.exists():
        print(f"FEHLER: answers-Datei fehlt: {path} (kein Fake).", file=sys.stderr)
        return 1
    rows = load_rows(path)
    if not rows:
        print("FEHLER: keine Zeilen in --answers (kein Fake).", file=sys.stderr)
        return 1

    res = evaluate_rows(rows, mode=args.mode, alpha=args.alpha, n_resamples=args.n_resamples, seed=args.seed)
    Path(args.out).write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
    kurz = {k: res[k] for k in ("decision", "n", "mode", "em_base", "em_adapter", "delta", "p_win", "p_loss", "ci")}
    print(json.dumps(kurz, ensure_ascii=False))
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI
    raise SystemExit(main())
