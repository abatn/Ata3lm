#!/usr/bin/env python3
"""M1-E2E: Wirkt Θ'? — Basis vs. Adapter auf denselben Probes (AGENTS.md §10.3).

Paper-Test (arXiv:2608.22215 §3.4): Ein Fakt gilt als konsolidiert, wenn das
feinjustierte Modell seine Probe(n) OHNE Retrieval korrekt beantwortet.
Vergleicht Exact-Match (Substring) von Basis (`Qwen/Qwen2.5-0.5B-Instruct`)
gegen den LoRA-Adapter (`Batnini/knowledge-agent-sft-lora`). Echter GPU-Lauf (Kaggle).
Erfolgs-Kriterium: `em_adapter > em_base` (Fakten internalisiert).

Status: Auftrag/unverifiziert-lokal (braucht GPU). KEINE Fake-Zahlen.
Quelle: AGENTS.md §10.3 · arXiv:2608.22215 §3.4 · kaggle/train_slow_consolidation.py
"""

from __future__ import annotations

import argparse
import json
import os
import random
import time
from pathlib import Path


def load_rows(path: str, n: int) -> list:
    """JSONL (`messages` [user, assistant]) → Liste (question, answer), erste n."""
    rows: list = []
    p = Path(path)
    if not p.exists():
        raise SystemExit(f"Dataset nicht gefunden: {path}")
    with p.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            msgs = rec.get("messages") or []
            if len(msgs) >= 2 and msgs[0].get("content") and msgs[1].get("content"):
                rows.append((str(msgs[0]["content"]), str(msgs[1]["content"])))
            if len(rows) >= n:
                break
    return rows


def main() -> None:
    ap = argparse.ArgumentParser(description="M1-E2E Basis vs. Adapter (Θ').")
    ap.add_argument("--dataset", default=os.environ.get("E2E_DATASET_PATH", "consolidation_sft.jsonl"))
    ap.add_argument("-n", "--num", type=int, default=int(os.environ.get("E2E_N", "200")))
    ap.add_argument("--base-model", default=os.environ.get("BASE_MODEL", "Qwen/Qwen2.5-0.5B-Instruct"))
    ap.add_argument("--adapter", default=os.environ.get("ADAPTER", "Batnini/knowledge-agent-sft-lora"))
    ap.add_argument("--out", default=os.environ.get("OUTPUT_JSON", "e2e_theta_result.json"))
    ap.add_argument("--seed", type=int, default=42)
    # Notebook-tolerant: Kernel-/colab-Args (z. B. `-f kernel.json`) ignorieren.
    args, _unknown = ap.parse_known_args()

    import torch
    from peft import PeftModel
    from transformers import AutoModelForCausalLM, AutoTokenizer

    if not torch.cuda.is_available():
        raise SystemExit("Keine GPU — M1-E2E muss auf Kaggle mit GPU laufen (kein Fake).")

    random.seed(args.seed)
    rows = load_rows(args.dataset, args.num)
    if not rows:
        raise SystemExit(f"Keine Probes in {args.dataset}")
    random.shuffle(rows)

    tok = AutoTokenizer.from_pretrained(args.base_model)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    dtype = torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16
    base = AutoModelForCausalLM.from_pretrained(args.base_model, torch_dtype=dtype).cuda().eval()

    def answer(model, question: str) -> str:
        enc = tok.apply_chat_template(
            [{"role": "user", "content": question}],
            add_generation_prompt=True,
            return_tensors="pt",
            return_dict=True,
        )
        inputs = {k: v.to(model.device) for k, v in enc.items()}
        with torch.no_grad():
            out = model.generate(**inputs, max_new_tokens=16, do_sample=False)
        return tok.decode(out[0][inputs["input_ids"].shape[-1] :], skip_special_tokens=True).strip()

    def exact_match(model) -> int:
        hit = 0
        for question, gold in rows:
            pred = answer(model, question).lower()
            g = gold.lower().strip()
            if g and (g in pred or pred[: len(g)] == g):
                hit += 1
        return hit

    t0 = time.time()
    # N8 (Auftrag): Basismessung VOR `PeftModel.from_pretrained` — PeftModel wickelt
    # DASSELBE Basismodul ein und addiert die Adapter am Modell (PEFT-Doku:
    # https://huggingface.co/docs/peft/en/package_reference/peft_model —
    # `disable_adapter`: "Use this to run inference on the base model"; LoRA injiziert
    # Matrizen "into each layer":
    # https://huggingface.co/docs/peft/en/package_reference/lora). Eine Basis-
    # messung danach misst MIT Adapter (Kaggle-Lauf 2026-10-07: em_base == em_adapter,
    # Δ=0). Akzeptanz: em_base misst das unveränderte Basismodell.
    # Hinweis: `elapsed_s` enthält seit N8 auch die Adapter-Ladezeit (Messung umschließt
    # notwendigerweise den Ladeschritt).
    em_base = exact_match(base)
    adapter = PeftModel.from_pretrained(base, args.adapter).eval().cuda()
    em_adapter = exact_match(adapter)
    result = {
        "status": "Auftrag/unverifiziert-lokal",
        "base_model": args.base_model,
        "adapter": args.adapter,
        "n": len(rows),
        "em_base": em_base,
        "em_adapter": em_adapter,
        "em_base_ratio": round(em_base / len(rows), 4),
        "em_adapter_ratio": round(em_adapter / len(rows), 4),
        "delta": em_adapter - em_base,
        "gpu": torch.cuda.get_device_name(0),
        "seed": args.seed,
        "elapsed_s": round(time.time() - t0, 1),
        "source": "AGENTS.md §10.3 · arXiv:2608.22215 §3.4",
    }
    Path(args.out).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
