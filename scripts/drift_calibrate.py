#!/usr/bin/env python3
"""Reale Drift-Kalibrierung (SAHOO Gl. 14–16) mit externem Grader-Signal (§6).

Läuft **lokal** über den NVIDIA-Endpoint (keine GPU nötig):
- Validierungsset: `N` Aufgaben aus ZsRE (question + gold).
- `prev` = LLM-Antwort **ohne** Memory; `cur` = LLM-Antwort **mit** Memory (= gold).
  (Der „Verbesserungsschritt" = Hinzufügen des Wissens; Drift = wie stark die
  Antwort sich dadurch ändert — Auftrag, an §10.3 angelehnt.)
- `grader_fn(prev, cur, reference)` = **externes Signal (§6)**: `gold in cur` ⇒
  bestanden (kein Drift), sonst Drift. Kein Fake: gold aus dem echten Datensatz.
- `embed_fn` = Endpoint-Embeddings.
- `drift_calibration.calibrate(...)` → Gewichte (Gl. 14), `tau` (Gl. 15), CI (Gl. 16).

Quellen: arXiv:2603.06333 (SAHOO, Gl. 14–16, in AGENTS.md §9.1c); §6 (externes Signal).
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "data" / "memory"))

_CFG = Path.home() / ".config/opencode/opencode.json"
if not os.environ.get("OPENAI_API_KEY") and _CFG.exists():
    _o = (
        json.loads(_CFG.read_text(encoding="utf-8"))
        .get("provider", {})
        .get("nvidia-llama-nemotron", {})
        .get("options", {})
    )
    os.environ.setdefault("OPENAI_API_KEY", _o.get("apiKey", ""))
    os.environ.setdefault("OPENAI_BASE_URL", _o.get("baseURL", "https://integrate.api.nvidia.com/v1"))

import drift_calibration  # noqa: E402
import zsre_corpus  # noqa: E402
from openai import OpenAI  # noqa: E402

MODEL = os.environ.get("DRIFT_MODEL", "nvidia/nemotron-3-super-120b-a12b")
# `nvidia/llama-3.2-nv-embedqa-1b-v1` etc. sind für das Konto nicht provisioniert (404);
# `nemotron-3-embed-1b` ist verfügbar (HTTP 200, dim 2048) – real geprüft.
EMBED = os.environ.get("DRIFT_EMBED_MODEL", "nvidia/nemotron-3-embed-1b")
N = int(os.environ.get("DRIFT_N", "12"))

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"], base_url=os.environ["OPENAI_BASE_URL"])


def ask(q: str, memory: str | None = None) -> str:
    base = "Answer in ONE short sentence. If you do not know the answer, reply exactly: I don't know.\n\n"
    prompt = base + q if not memory else f"{base}Use this knowledge:\n{memory}\n\nQuestion: {q}"
    r = client.chat.completions.create(
        model=MODEL, messages=[{"role": "user", "content": prompt}], max_tokens=512, temperature=0.0
    )
    msg = r.choices[0].message
    return (msg.content or getattr(msg, "reasoning_content", None) or "").strip()


def embed(text: str) -> list:
    r = client.embeddings.create(model=EMBED, input=text or " ")
    return list(r.data[0].embedding)


def grader(_prev: str, cur: str, reference: str | None) -> bool:
    """Externes Signal (§6): gold (reference) in der Antwort enthalten?"""
    return bool(reference) and reference.lower().strip() in (cur or "").lower()


def _load_answer_samples(path: str) -> list:
    """JSONL (question, gold, base_answer, adapter_answer) → samples (Θ vs. Θ′)."""
    samples = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        r = json.loads(line)
        samples.append({"prev": r["base_answer"], "cur": r["adapter_answer"], "reference": r["gold"]})
    return samples


def main() -> None:
    import argparse

    ap = argparse.ArgumentParser(description="Reale Drift-Kalibrierung (SAHOO Gl. 14-16).")
    ap.add_argument(
        "--answers",
        default=os.environ.get("DRIFT_ANSWERS", ""),
        help="JSONL (question, gold, base_answer, adapter_answer). Ohne: generiert prev/cur via LLM-Endpoint aus ZsRE.",
    )
    ap.add_argument("-n", "--num", type=int, default=N)
    ap.add_argument(
        "--out", default=os.environ.get("DRIFT_OUT", str(ROOT / "ergebnisse" / "drift-calibration-result.json"))
    )
    args = ap.parse_args()

    if args.answers:
        samples = _load_answer_samples(args.answers)
        dataset = "theta_answers.jsonl (Base Θ vs. Adapter Θ', Kaggle e2e_theta_probe)"
    else:
        tmp = ROOT / "ergebnisse" / "_zsre_drift_tmp.jsonl"
        res = zsre_corpus.build_zsre_corpus(tmp, n=args.num, split="validation")
        rows = [json.loads(line) for line in tmp.read_text(encoding="utf-8").splitlines() if line.strip()]
        tmp.unlink(missing_ok=True)
        samples = []
        for r in rows:
            q = r["messages"][0]["content"]
            gold = r["messages"][1]["content"]
            prev = ask(q)
            cur = ask(q, memory=gold)
            samples.append({"prev": prev, "cur": cur, "reference": gold})
            print(f"Q: {q}\n  prev={prev!r}\n  cur ={cur!r}\n  gold={gold!r}", flush=True)
        dataset = res.get("dataset")

    out = drift_calibration.calibrate(samples, embed_fn=embed, grader_fn=grader)
    payload = {
        "n": out["n"],
        "tau": out["tau"],
        "weights": out["weights"],
        "ci": out["ci"],
        "auc": out["auc"],
        "f1": out["f1"],
        "model": MODEL,
        "embed_model": EMBED,
        "dataset": dataset,
        "source": "arXiv:2603.06333 Gl.14-16 · AGENTS.md §9.1c · §6 externes Signal",
    }
    outp = Path(args.out)
    outp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print("\n=== KALIBRIERUNG ===")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    print(f"\ngeschrieben: {outp}")


if __name__ == "__main__":
    main()
