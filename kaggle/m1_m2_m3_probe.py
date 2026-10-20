#!/usr/bin/env python3
"""M1/M2/M3 — read-only Messskript (KEIN Training, KEIN Write-Back).

Wird von einem Menschen auf Kaggle (GPU) ausgefuehrt.

Reihenfolge (Amendment A1, 2026-10-20 — R3a/R3b geschlossen):
  Pass 1  M1        Base-Instanz #1, 15 Probes, VOR jedem Wrap
  Pass 2  M1_repeat dieselbe Instanz #1  -> Deterministische-Baseline (muss 15/15 sein)
          [Instanz #1 wird freigegeben]
  Pass 3  M1b       Base-Instanz #2, UNWRAPPED -> Referenz fuer den Canary (gleiche Instanz!)
  Pass 4  M2        dieselbe Instanz #2 + B2' (rsLoRA)
  Pass 5  canary    dieselbe Instanz #2, disable_adapter() -> MUSS M1b item-fuer-item reproduzieren
  Pass 6  M2_repeat dieselbe Instanz #2, Adapter wieder an -> Adapter-Pfad-Determinismus
          [Instanz #2 wird freigegeben]
  Pass 7  M1c       Base-Instanz #3, UNWRAPPED -> gepaarte Referenz fuer M3
  Pass 8  M3        dieselbe Instanz #3 + B2 (non-rsLoRA)

  R3a: der Canary vergleicht gegen M1b (GLEICHE Instanz, unwrapped) — kein Cross-Instance-Rauschen.
  R3b: Positivkontrolle M2 (Adapter an) vs. canary (Adapter aus) auf derselben Instanz;
       plus Logit-Witness (pre-/post-wrap) und Struktur-Witness (injizierte lora_B != 0).

Verboten und daher NICHT enthalten: `kaggle/write_back_cycle.py` (trainiert + schreibt,
`write_back_cycle.py:420-421`), `self_update`, `route_and_store`, `slow_consolidation.write_back`,
`train_fn`, jede Erzeugung von Zahlen ohne GPU (ohne GPU: Status "nicht ausgefuehrt").

Grader: spiegelt `data/memory/acceptance_gate.py:95-131`. Ist das Repo-File erreichbar,
wird die Uebereinstimmung fuer ALLE gemessenen Paare geprueft; Abweichung => Abbruch.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import sys
import traceback
from collections import Counter
from pathlib import Path

# ---------------------------------------------------------------- Grader
_PUNCT = str.maketrans({c: " " for c in ".,;:!?\"'()[]{}"})


def _normalize(text: str) -> str:
    return " ".join(str(text or "").lower().translate(_PUNCT).split())


def extract_answer(text: str) -> str:
    for line in str(text or "").splitlines():
        if line.strip():
            return line.strip()
    return ""


def grade(answer: str, gold: str, *, mode: str = "strict") -> bool:
    g = _normalize(gold)
    if not g:
        return False
    a = _normalize(extract_answer(answer))
    if mode == "strict":
        return a == g
    if mode == "substring":
        return g in a
    raise ValueError(f"unknown grader mode: {mode!r}")


# ---------------------------------------------------------------- Hilfen
def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_probes(path: Path) -> list[dict]:
    probes: list[dict] = []
    raw = 0
    with path.open(encoding="utf-8") as fh:
        for lineno, line in enumerate(fh, 1):
            line = line.strip()
            if not line:
                continue
            raw += 1
            rec = json.loads(line)
            msgs = rec.get("messages") or []
            if len(msgs) >= 2:
                q, g = str(msgs[0]["content"]), str(msgs[1]["content"])
            else:
                q, g = str(rec.get("question", "")), str(rec.get("gold", ""))
            if not q or not g:
                raise ValueError(f"Zeile {lineno} unbrauchbar (leere Frage/Gold) — kein stilles Skip")
            probes.append({"key": rec.get("key"), "question": q, "gold": g})
    if raw != len(probes):
        raise ValueError("Zeilenzahl != Probe-Zahl")
    return probes


def repo_grader_crosscheck(pairs: list[tuple[str, str]], repo_root: Path) -> str:
    try:
        import importlib.util

        spec = importlib.util.spec_from_file_location("ag", repo_root / "data/memory/acceptance_gate.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
    except Exception as exc:  # noqa: BLE001
        return f"crosscheck skipped: {type(exc).__name__}: {exc}"
    for answer, gold in pairs:
        for mode in ("strict", "substring"):
            if mod.grade(answer, gold, mode=mode) != grade(answer, gold, mode=mode):
                raise RuntimeError(f"Grader-Mismatch ({mode}): answer={answer!r} gold={gold!r}")
    return f"ok (repo acceptance_gate.py identisch, {len(pairs)} Paare x 2 Modi)"


def write_json(path: Path, obj) -> None:
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")


def parse_version(v: str) -> tuple[int, ...]:
    parts = []
    for chunk in str(v).split(".")[:2]:
        digits = "".join(ch for ch in chunk if ch.isdigit())
        parts.append(int(digits) if digits else 0)
    return tuple(parts)


def item_diff(a: list[dict], b: list[dict]) -> dict:
    """Item-fuer-Item Vergleich zweier Messdurchlaeufe (Join per question)."""
    amap = {r["question"]: r["raw_output"] for r in a}
    bmap = {r["question"]: r["raw_output"] for r in b}
    common = sorted(set(amap) & set(bmap))
    diff = [q for q in common if amap[q] != bmap[q]]
    return {
        "matched": len(common) - len(diff),
        "n": len(common),
        "ratio": (len(common) - len(diff)) / max(1, len(common)),
        "mismatch_items": diff,
    }


# ---------------------------------------------------------------- Hauptlauf
def main() -> int:
    ap = argparse.ArgumentParser(description="M1/M2/M3 read-only (Base / B2' / B2) + Canaries")
    ap.add_argument("--dataset", required=True)
    ap.add_argument("--base-model", required=True)
    ap.add_argument("--base-revision", required=True)
    ap.add_argument("--tokenizer-revision", required=True)
    ap.add_argument("--adapter-b2prime", required=True)
    ap.add_argument("--adapter-b2", required=True)
    ap.add_argument("--expect-dataset-sha", required=True)
    ap.add_argument("--expect-b2prime-sha", required=True)
    ap.add_argument("--expect-b2-sha", required=True)
    ap.add_argument("--expect-base-commit", default=None, help="optional: 40-hex Commit der Basis")
    ap.add_argument("--expect-tokenizer-commit", default=None, help="optional: 40-hex Commit des Tokenizers")
    ap.add_argument("--ref-b2prime-json", default=None, help="Altlauf-Result-JSON fuer Regel 6 (P-2b)")
    ap.add_argument("--expect-ref-sha", default=None)
    ap.add_argument("--expect-probes", type=int, default=15)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--max-new-tokens", type=int, default=16)
    ap.add_argument("--repo-root", default=None)
    args = ap.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    status_path = out_dir / "status.json"
    passes_log: list[dict] = []

    def bail(reason: str, **extra) -> int:
        write_json(status_path, {"status": "nicht ausgefuehrt", "reason": reason, **extra})
        print(f"STATUS: nicht ausgefuehrt — {reason}")
        return 0

    # ---------------------------------------------------------- Preflight
    try:
        import torch
    except Exception as exc:  # noqa: BLE001
        return bail(f"torch nicht importierbar: {exc}")
    if not torch.cuda.is_available():
        return bail("keine GPU sichtbar (torch.cuda.is_available() == False); kein Fake-Lauf")
    try:
        import peft
        import transformers
    except Exception as exc:  # noqa: BLE001
        return bail(f"transformers/peft nicht importierbar: {exc}")

    try:
        import importlib.metadata as md

        torchao = md.version("torchao")
    except Exception:  # noqa: BLE001
        torchao = None
    if torchao and parse_version(torchao) < (0, 16):
        return bail(
            f"torchao {torchao} < 0.16.0 bricht peft bei der LoRA-Injektion "
            "(Beleg: kaggle/write_back_cycle.py:576-584). Fix: pip uninstall -y torchao "
            "oder pip install -U 'torchao>=0.16.0'. Kein stiller Abbruch."
        )

    ds = Path(args.dataset)
    a_p = Path(args.adapter_b2prime)
    a_b = Path(args.adapter_b2)
    needed = [
        ds,
        a_p / "adapter_model.safetensors",
        a_p / "adapter_config.json",
        a_b / "adapter_model.safetensors",
        a_b / "adapter_config.json",
    ]
    for p in needed:
        if not p.exists():
            return bail(f"Pflichtartefakt fehlt: {p}")
    try:
        cfg_p = json.loads((a_p / "adapter_config.json").read_text())
        cfg_b = json.loads((a_b / "adapter_config.json").read_text())
    except Exception as exc:  # noqa: BLE001
        return bail(f"adapter_config.json unlesbar: {exc}")

    ds_sha = sha256(ds)
    ap_sha = sha256(a_p / "adapter_model.safetensors")
    ab_sha = sha256(a_b / "adapter_model.safetensors")
    pins = {
        "dataset": (args.expect_dataset_sha, ds_sha),
        "b2prime": (args.expect_b2prime_sha, ap_sha),
        "b2": (args.expect_b2_sha, ab_sha),
    }
    bad = {k: {"expected": v[0], "actual": v[1]} for k, v in pins.items() if v[0] != v[1]}
    if bad:
        return bail(f"Artefakt-Hashes weichen von der Pin-Liste ab: {bad}")

    for label, cfg in (("b2prime", cfg_p), ("b2", cfg_b)):
        if cfg.get("base_model_name_or_path") != args.base_model:
            return bail(f"{label}: base_model_name_or_path={cfg.get('base_model_name_or_path')} != {args.base_model}")
        if cfg.get("r") != 64 or cfg.get("lora_alpha") != 256:
            return bail(f"{label}: r/alpha unerwartet ({cfg.get('r')}/{cfg.get('lora_alpha')}) — Pin-Verwechslung")
    if cfg_p.get("use_rslora") is not True or cfg_b.get("use_rslora") is not False:
        return bail(f"use_rslora unerwartet: b2prime={cfg_p.get('use_rslora')} b2={cfg_b.get('use_rslora')}")

    try:
        probes = load_probes(ds)
    except Exception as exc:  # noqa: BLE001
        return bail(f"Probe-Datei unbrauchbar: {type(exc).__name__}: {exc}")
    if len(probes) != args.expect_probes:
        return bail(f"erwartet {args.expect_probes} Probes, gefunden {len(probes)}")
    if len({p["question"] for p in probes}) != len(probes):
        return bail("Fragen nicht eindeutig — Join per question unmoeglich")

    # Referenz (Regel 6) — VOR der GPU-Zeit
    ref_map: dict = {}
    ref_cmp: dict = {"reference": args.ref_b2prime_json, "available": False}
    if args.ref_b2prime_json:
        refp = Path(args.ref_b2prime_json)
        if not refp.exists():
            return bail(f"Referenz-Altlauf fehlt: {refp}")
        try:
            ref_sha = sha256(refp)
        except Exception as exc:  # noqa: BLE001
            return bail(f"Referenz-Hash nicht berechenbar: {exc}")
        if args.expect_ref_sha and ref_sha != args.expect_ref_sha:
            return bail(f"Referenz-Hash weicht ab: erwartet {args.expect_ref_sha}, ist {ref_sha}")
        try:
            ref = json.loads(refp.read_text())
            ref_map = {p["question"]: p.get("answer", "") for p in ref.get("probe_results", [])}
        except Exception as exc:  # noqa: BLE001
            return bail(f"Referenz-Altlauf unlesbar: {type(exc).__name__}: {exc}")
        if len(ref_map) != len(probes) or set(ref_map) != {p["question"] for p in probes}:
            return bail(
                f"Referenz-Fragensatz passt nicht zu den Probes "
                f"({len(ref_map)} vs {len(probes)}) — Regel 6 waere unzuverlaessig"
            )
        ref_cmp = {
            "reference": str(refp),
            "reference_sha256": ref_sha,
            "available": True,
            "n_reference_items": len(ref_map),
            "question_set_identical": True,
            "hinweis": "5a9ed27a... ist die SHA256 der Result-JSON, KEIN Git-Commit",
        }

    n = len(probes)
    GOOD, BAD, DIFF = math.ceil(0.733 * n), math.floor(0.267 * n), math.ceil(0.2 * n)
    COLLAPSE_MIN = math.ceil(0.8 * n)
    NOISE_BUDGET = 2

    from peft import PeftModel
    from transformers import AutoModelForCausalLM, AutoTokenizer

    dtype = torch.float16

    def load_base():
        torch.manual_seed(args.seed)
        kw = {"revision": args.base_revision}
        try:
            m = AutoModelForCausalLM.from_pretrained(args.base_model, dtype=dtype, **kw)
        except TypeError:
            m = AutoModelForCausalLM.from_pretrained(args.base_model, torch_dtype=dtype, **kw)
        return m.cuda().eval()

    tok = AutoTokenizer.from_pretrained(args.base_model, revision=args.tokenizer_revision)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    if getattr(tok, "chat_template", None) is None:
        return bail("Tokenizer ohne chat_template — apply_chat_template wuerde crashen")

    resolved = {
        "requested_base_revision": args.base_revision,
        "requested_tokenizer_revision": args.tokenizer_revision,
        "base_commit": None,
        "base_commit_source": "unresolved",
        "tokenizer_commit": None,
        "tokenizer_commit_source": "unresolved",
    }
    init_kwargs = getattr(tok, "init_kwargs", None) or {}
    if isinstance(init_kwargs, dict):
        resolved["tokenizer_commit"] = init_kwargs.get("_commit_hash") or init_kwargs.get("commit_hash")
        resolved["tokenizer_commit_source"] = (
            "tokenizer.init_kwargs._commit_hash" if resolved["tokenizer_commit"] else "unresolved"
        )

    def answer(model, question: str) -> str:
        enc = tok.apply_chat_template(
            [{"role": "user", "content": question}],
            add_generation_prompt=True,
            return_tensors="pt",
            return_dict=True,
        )
        inputs = {k: v.to(model.device) for k, v in enc.items()}
        with torch.no_grad():
            out = model.generate(**inputs, max_new_tokens=args.max_new_tokens, do_sample=False)
        return tok.decode(out[0][inputs["input_ids"].shape[-1] :], skip_special_tokens=True).strip()

    def last_logits(model, question: str):
        enc = tok.apply_chat_template(
            [{"role": "user", "content": question}],
            add_generation_prompt=True,
            return_tensors="pt",
            return_dict=True,
        )
        inputs = {k: v.to(model.device) for k, v in enc.items()}
        with torch.no_grad():
            out = model(**inputs)
        return out.logits[0, -1, :].float().cpu()

    def measure(model, tag: str, instance: str) -> list[dict]:
        torch.manual_seed(args.seed)
        rows = []
        for p in probes:
            raw = answer(model, p["question"])
            rows.append(
                {
                    "pass": tag,
                    "instance": instance,
                    "key": p["key"],
                    "question": p["question"],
                    "gold": p["gold"],
                    "raw_output": raw,
                    "strict": grade(raw, p["gold"], mode="strict"),
                    "substring": grade(raw, p["gold"], mode="substring"),
                    "gold_in_raw_output": _normalize(p["gold"]) in _normalize(raw),
                }
            )
        passes_log.append(
            {
                "pass": tag,
                "instance": instance,
                "n": len(rows),
                "strict": sum(1 for r in rows if r["strict"]),
                "substring": sum(1 for r in rows if r["substring"]),
            }
        )
        return rows

    def counts(rows: list[dict]) -> dict:
        return {
            "n": len(rows),
            "strict": sum(1 for r in rows if r["strict"]),
            "substring": sum(1 for r in rows if r["substring"]),
            "gold_in_raw_output": sum(1 for r in rows if r["gold_in_raw_output"]),
        }

    def collapse(rows: list[dict]) -> tuple[bool, str | None, int]:
        vals = [r["raw_output"].strip() for r in rows]
        if not vals:
            return False, None, 0
        top, cnt = Counter(vals).most_common(1)[0]
        return cnt >= COLLAPSE_MIN, top, cnt

    def vram_free() -> bool:
        return torch.cuda.memory_allocated() < 1.0 * (1024**3)

    try:
        # ---------------------------------------------- Instanz #1: M1 + M1_repeat
        inst1 = load_base()
        if not resolved["base_commit"]:
            resolved["base_commit"] = getattr(getattr(inst1, "config", None), "_commit_hash", None)
            resolved["base_commit_source"] = "config._commit_hash" if resolved["base_commit"] else "unresolved"
        m1_rows = measure(inst1, "M1_base", "base#1")
        m1r_rows = measure(inst1, "M1_repeat", "base#1")
        del inst1
        torch.cuda.empty_cache()
        if not vram_free():
            return bail("VRAM nach Freigabe von Instanz #1 nicht freigegeben (Referenz-Leck)")

        # ---------------------------------------------- Instanz #2: M1b -> M2 -> canary -> M2_repeat
        inst2 = load_base()
        m1b_rows = measure(inst2, "M1b_base", "base#2")
        logit_probe = probes[0]["question"]
        logits_pre = last_logits(inst2, logit_probe)
        inst2 = PeftModel.from_pretrained(inst2, str(a_p)).eval().cuda()
        logits_post = last_logits(inst2, logit_probe)
        max_logit_delta = float(torch.max(torch.abs(logits_post - logits_pre)).item())
        argmax_changed = int(torch.argmax(logits_pre).item()) != int(torch.argmax(logits_post).item())
        m2_rows = measure(inst2, "M2_b2prime", "base#2")
        with inst2.disable_adapter():
            canary_rows = measure(inst2, "canary_disable_adapter", "base#2")
        m2r_rows = measure(inst2, "M2_repeat", "base#2")
        # Struktur-Witness: injizierte lora_Module und trainierte lora_B.
        # PEFT registriert die Adapter als nn.ModuleDict je Adapter-Name
        # (peft/tuners/lora/layer.py:134/263) => der Modulpfad lautet
        # "...lora_A.<adapter_name>"; der LoraLayer selbst traegt lora_A UND lora_B.
        lora_modules_total, lora_b_nonzero = 0, 0
        for _name, mod in inst2.named_modules():
            a_dict = getattr(mod, "lora_A", None)
            b_dict = getattr(mod, "lora_B", None)
            if a_dict is None or b_dict is None:
                continue
            lora_modules_total += 1
            for lora_b in b_dict.values():
                weight = getattr(lora_b, "weight", None)
                if weight is None:
                    continue
                try:
                    if float(weight.detach().abs().max().item()) > 0:
                        lora_b_nonzero += 1
                        break
                except Exception:  # noqa: BLE001
                    pass
        del inst2
        torch.cuda.empty_cache()
        if not vram_free():
            return bail("VRAM nach Freigabe von Instanz #2 nicht freigegeben (Referenz-Leck)")

        # ---------------------------------------------- Instanz #3: M1c -> M3
        inst3 = load_base()
        m1c_rows = measure(inst3, "M1c_base", "base#3")
        inst3 = PeftModel.from_pretrained(inst3, str(a_b)).eval().cuda()
        m3_rows = measure(inst3, "M3_b2", "base#3")
        del inst3
        torch.cuda.empty_cache()
    except Exception as exc:  # noqa: BLE001
        write_json(
            status_path,
            {"status": "fehlgeschlagen", "error": f"{type(exc).__name__}: {exc}", "traceback": traceback.format_exc()},
        )
        print(f"STATUS: fehlgeschlagen — {type(exc).__name__}: {exc}")
        print(traceback.format_exc())
        return 1

    # ---------------------------------------------------------- Rausch-/Canary-/PC-Bloecke
    determinism = item_diff(m1_rows, m1r_rows)
    determinism.update(
        {
            "a": "M1_base",
            "b": "M1_repeat",
            "same_instance": True,
            "threshold": 1.0,
            "status": "pass" if determinism["matched"] == n else "fail",
        }
    )
    cross_noise = item_diff(m1_rows, m1b_rows)
    cross_noise.update(
        {
            "a": "M1_base",
            "b": "M1b_base",
            "same_instance": False,
            "budget": NOISE_BUDGET,
            "within_budget": cross_noise["n"] - cross_noise["matched"] <= NOISE_BUDGET,
            "status": "informational",
        }
    )
    canary = item_diff(m1b_rows, canary_rows)
    canary.update(
        {
            "a": "M1b_base",
            "b": "canary_disable_adapter",
            "same_instance": True,
            "threshold": 1.0,
            "status": "pass" if canary["matched"] == n else "fail",
            "hinweis": "Referenz ist M1b (dieselbe Instanz, unwrapped) — kein Cross-Instance-Rauschen",
        }
    )
    pc_gen = item_diff(m2_rows, canary_rows)
    pc_gen.update(
        {
            "a": "M2_b2prime",
            "b": "canary_disable_adapter",
            "same_instance": True,
            "criterion": "differing_items >= 1",
            "differing_items": n - pc_gen["matched"],
        }
    )
    pc_adapter_path = item_diff(m2_rows, m2r_rows)
    positive_control = {
        "w1_generation": pc_gen,
        "w2_logit": {
            "probe": logit_probe,
            "max_abs_logit_delta": max_logit_delta,
            "argmax_changed": argmax_changed,
            "source": "pre-wrap vs post-wrap, Instanz #2",
        },
        "w3_structural": {
            "lora_modules_total": lora_modules_total,
            "lora_B_nonzero": lora_b_nonzero,
            "target_modules_expected": cfg_p.get("target_modules"),
        },
        "w4_adapter_path_determinism": {
            "a": "M2_b2prime",
            "b": "M2_repeat",
            "matched": pc_adapter_path["matched"],
            "n": pc_adapter_path["n"],
        },
    }
    pc_pass = pc_gen["differing_items"] >= 1
    positive_control["status"] = "pass" if pc_pass else "fail"
    positive_control["interpretation"] = (
        "M2 != canary auf >= 1 Item => Adapter war aktiv (Positivkontrolle bestanden)."
        if pc_pass
        else "PC-Fail: M2 == canary => der Adapter aendert keine Greedy-Antwort. "
        "Nur falls Logit-Delta > 0 UND lora_B_nonzero > 0 (Adapter geladen + trainiert) "
        "=> Regel 8 (No-op). Sonst Regel 9."
    )

    # ---------------------------------------------------------- Formatkontrolle
    coll = {}
    for tag, rows in (
        ("M1_base", m1_rows),
        ("M1b_base", m1b_rows),
        ("M1c_base", m1c_rows),
        ("M2_b2prime", m2_rows),
        ("M3_b2", m3_rows),
    ):
        c, top, cnt = collapse(rows)
        coll[tag] = {"collapse": c, "top_answer": top, "top_count": cnt}
    fmt = {
        "collapse_min_items": COLLAPSE_MIN,
        "per_pass": coll,
        "b2prime_strict_vs_substring_diff_items": [r["question"] for r in m2_rows if r["strict"] != r["substring"]],
        "b2_strict_vs_substring_diff_items": [r["question"] for r in m3_rows if r["strict"] != r["substring"]],
        "note": "substring prueft gold ⊂ antwort (acceptance_gate.py:123-130); "
        "gold 'Jamaica Plain' vs antwort 'Jamaica' ist in BEIDEN Modi FAIL.",
    }

    # ---------------------------------------------------------- Regel 6 (P-2b)
    if ref_cmp.get("available"):
        m2_map = {r["question"]: r["raw_output"] for r in m2_rows}
        same = sum(1 for q, ans in ref_map.items() if m2_map.get(q) == ans)
        ref_cmp.update(
            {
                "items_identical_to_altlauf": same,
                "items_differing": len(ref_map) - same,
                "interpretation": "identisch => Messkette reproduzierbar; abweichend => Regel 6 (P-2b). "
                "+/-1 Item ist allein kein Beleg. Caveat: der Altlauf pinnte keine "
                "Base-Revision => Abweichung kann Pinning-Artefakt sein.",
            }
        )

    # ---------------------------------------------------------- Entscheidung (9 Regeln)
    c_m1, c_m1r, c_m1b = counts(m1_rows), counts(m1r_rows), counts(m1b_rows)
    c_m1c, c_m2, c_m3 = counts(m1c_rows), counts(m2_rows), counts(m3_rows)
    rules: list[tuple[int, str]] = []
    decision, rule_no = "unentschieden", None
    failed: list[str] = []

    if determinism["status"] != "pass":
        failed.append("determinism_baseline")
    if not cross_noise["within_budget"]:
        failed.append("cross_instance_noise")
    if canary["status"] != "pass":
        failed.append("canary")
    if not pc_pass:
        failed.append("positive_control")
    if coll["M1_base"]["collapse"] or coll["M1b_base"]["collapse"]:
        failed.append("base_collapse")
    # Regel 9 (Preregistration:99) verlangt Degeneration in M1/M1b/M2/M3.
    if coll["M2_b2prime"]["collapse"]:
        failed.append("m2_collapse")
    if coll["M3_b2"]["collapse"]:
        failed.append("m3_collapse")

    if failed:
        rule_no = 9
        if determinism["status"] != "pass":
            rules.append((9, f"Deterministische-Baseline M1 vs M1_repeat: {determinism['matched']}/{n}"))
        if not cross_noise["within_budget"]:
            rules.append(
                (9, f"Cross-Instance-Noise M1 vs M1b: {n - cross_noise['matched']}/{n} > Budget {NOISE_BUDGET}")
            )
        if canary["status"] != "pass":
            rules.append(
                (
                    9,
                    f"Canary-Fail: disable_adapter reproduziert M1b nur {canary['matched']}/{canary['n']} "
                    "(gleiche Instanz) — PEFT-Pfad oder Messkette, KEIN Cross-Instance-Rauschen",
                )
            )
        if not pc_pass:
            if max_logit_delta > 0 and lora_b_nonzero > 0:
                rules.append(
                    (
                        9,
                        "Positive-Control-Fail M2 == canary, aber Logit-Delta > 0 und lora_B != 0 "
                        "=> Regel 8 (No-op) wird unten geprueft",
                    )
                )
            else:
                rules.append(
                    (
                        9,
                        f"Positive-Control-Fail: M2 == canary, Logit-Delta {max_logit_delta}, "
                        f"lora_B_nonzero {lora_b_nonzero} => Adapter nicht wirksam (Artefaktproblem)",
                    )
                )
        if coll["M1_base"]["collapse"] or coll["M1b_base"]["collapse"]:
            rules.append((9, "Base degeneriert (identische Antwort bei >= COLLAPSE_MIN) — Diagnose blockiert"))
        if coll["M2_b2prime"]["collapse"]:
            rules.append(
                (
                    9,
                    f"M2 degeneriert ({coll['M2_b2prime']['top_count']}/{n} identische Antwort "
                    f"{coll['M2_b2prime']['top_answer']!r}) — Diagnose blockiert, kein P-1/P-2/P-3-Zweig",
                )
            )
        if coll["M3_b2"]["collapse"]:
            rules.append(
                (
                    9,
                    f"M3 degeneriert ({coll['M3_b2']['top_count']}/{n} identische Antwort "
                    f"{coll['M3_b2']['top_answer']!r}) — Diagnose blockiert, kein P-1/P-2/P-3-Zweig",
                )
            )
    else:
        # gepaarte Basisreferenzen: M1b (Instanz #2) fuer M2, M1c (Instanz #3) fuer M3
        b2, b3 = c_m1b["strict"], c_m1c["strict"]
        if b2 >= GOOD and c_m2["strict"] <= BAD and c_m3["strict"] >= b3 - 2:
            decision, rule_no = "P-1 (deskriptiv konsistent, nicht bewiesen)", 1
            rules.append((1, f"M1b={b2}/{n}, M2={c_m2['strict']}/{n}, M3={c_m3['strict']}/{n}"))
        elif b2 >= GOOD and c_m2["strict"] <= BAD and c_m3["strict"] <= BAD:
            decision, rule_no = "Adapter-/Trainingsschaden (nicht spezifisch rsLoRA)", 2
            rules.append((2, f"M1b={b2}/{n}, M2={c_m2['strict']}/{n}, M3={c_m3['strict']}/{n}"))
        elif b2 <= BAD and c_m2["strict"] >= b2 and c_m3["strict"] >= b2:
            decision, rule_no = "P-3 Base/Prompt/Daten (Kandidat)", 3
            rules.append((3, f"M1b={b2}/{n}, M2={c_m2['strict']}/{n}, M3={c_m3['strict']}/{n}"))
        elif b2 <= BAD and c_m2["strict"] <= b2 - DIFF and c_m3["strict"] <= b2 - DIFF:
            decision, rule_no = "Adapterschaden auf schwacher Base (Kandidat)", 4
            rules.append((4, f"M1b={b2}/{n}, M2={c_m2['strict']}/{n}, M3={c_m3['strict']}/{n}"))
        elif c_m2["strict"] >= b2 + DIFF:
            decision, rule_no = "Adapter hilft deskriptiv; P-1 nicht gestuetzt", 7
            rules.append((7, f"M1b={b2}/{n}, M2={c_m2['strict']}/{n}, M3={c_m3['strict']}/{n}"))
        elif abs(c_m2["strict"] - b2) <= 2:
            decision, rule_no = "No-op (M2 ~ M1b); keine Ursache ableitbar", 8
            rules.append((8, f"M1b={b2}/{n}, M2={c_m2['strict']}/{n}, M3={c_m3['strict']}/{n}"))
        else:
            rule_no = 9
            rules.append(
                (
                    9,
                    f"gemischtes Ergebnis (M1b={b2}/{n}, M2={c_m2['strict']}/{n}, "
                    f"M3={c_m3['strict']}/{n}) -> nicht zuordenbar",
                )
            )

    rules.append((5, "P-2a: N8 invalidiert base_answer/em_base/changed/Delta (write_back_cycle.py:420-421/442-445)"))
    if ref_cmp.get("available"):
        if ref_cmp["items_identical_to_altlauf"] == ref_cmp["n_reference_items"]:
            rules.append(
                (
                    6,
                    f"P-2b: M2 reproduziert das Altlauf-15-Tupel exakt "
                    f"({ref_cmp['items_identical_to_altlauf']}/{ref_cmp['n_reference_items']})",
                )
            )
        else:
            rules.append(
                (
                    6,
                    f"P-2b: M2 weicht vom Altlauf ab "
                    f"({ref_cmp['items_identical_to_altlauf']}/{ref_cmp['n_reference_items']} identisch) "
                    "=> Artefakt-/Eval-/Umgebungs-Mismatch moeglich",
                )
            )
    else:
        rules.append((6, "P-2b: nicht ausgefuehrt (kein Referenz-Altlauf uebergeben)"))

    # ---------------------------------------------------------- Ausgaben
    all_rows = m1_rows + m1r_rows + m1b_rows + m2_rows + canary_rows + m2r_rows + m1c_rows + m3_rows
    pairs = [(r["raw_output"], r["gold"]) for r in all_rows]
    crosscheck = "skipped (--repo-root nicht gesetzt)"
    if args.repo_root:
        try:
            crosscheck = repo_grader_crosscheck(pairs, Path(args.repo_root))
        except Exception as exc:  # noqa: BLE001
            write_json(
                status_path, {"status": "nicht ausgefuehrt", "reason": f"Grader-Crosscheck fehlgeschlagen: {exc}"}
            )
            print(f"STATUS: nicht ausgefuehrt — Grader-Crosscheck fehlgeschlagen: {exc}")
            return 0

    with (out_dir / "per_item.jsonl").open("w", encoding="utf-8") as fh:
        for r in all_rows:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")

    chat_template_sha = hashlib.sha256((getattr(tok, "chat_template", "") or "").encode("utf-8")).hexdigest()
    manifest = {
        "status": "ausgefuehrt",
        "generated_by": "m1_m2_m3_probe.py (read-only, kein Training; Amendment A1: R3a/R3b)",
        "base_model": args.base_model,
        "resolved_commits": resolved,
        "fingerprints": {
            "tokenizer_chat_template_sha256": chat_template_sha,
            "tokenizer_vocab_size": getattr(tok, "vocab_size", None),
            "tokenizer_name_or_path": getattr(tok, "name_or_path", None),
        },
        "dataset": str(ds),
        "dataset_sha256": ds_sha,
        "n_probes": n,
        "adapter_b2prime": str(a_p),
        "adapter_b2prime_sha256": ap_sha,
        "adapter_b2prime_cfg_sha256": sha256(a_p / "adapter_config.json"),
        "adapter_b2": str(a_b),
        "adapter_b2_sha256": ab_sha,
        "adapter_b2_cfg_sha256": sha256(a_b / "adapter_config.json"),
        "b2prime_cfg": {
            "r": cfg_p.get("r"),
            "alpha": cfg_p.get("lora_alpha"),
            "use_rslora": cfg_p.get("use_rslora"),
            "base_model_name_or_path": cfg_p.get("base_model_name_or_path"),
            "target_modules": cfg_p.get("target_modules"),
            "lora_dropout": cfg_p.get("lora_dropout"),
        },
        "b2_cfg": {
            "r": cfg_b.get("r"),
            "alpha": cfg_b.get("lora_alpha"),
            "use_rslora": cfg_b.get("use_rslora"),
            "base_model_name_or_path": cfg_b.get("base_model_name_or_path"),
            "target_modules": cfg_b.get("target_modules"),
            "lora_dropout": cfg_b.get("lora_dropout"),
        },
        "env": {
            "python": platform.python_version(),
            "torch": torch.__version__,
            "transformers": transformers.__version__,
            "peft": peft.__version__,
            "torchao": torchao,
            "gpu": torch.cuda.get_device_name(0),
            "capability": torch.cuda.get_device_capability(0),
            "dtype": "float16",
        },
        "decoding": {
            "max_new_tokens": args.max_new_tokens,
            "do_sample": False,
            "seed": args.seed,
            "reseeded_before_each_pass": True,
        },
        "thresholds": {
            "good": GOOD,
            "bad": BAD,
            "diff": DIFF,
            "collapse_min": COLLAPSE_MIN,
            "cross_instance_noise_budget": NOISE_BUDGET,
            "hinweis": "deskriptiv; n=15 => 1 Item = 6,7 pp; keine Signifikanz",
        },
        "grader_crosscheck": crosscheck,
        "measurement_passes": passes_log,
        "counts": {
            "M1_base": c_m1,
            "M1_repeat": c_m1r,
            "M1b_base": c_m1b,
            "M2_b2prime": c_m2,
            "canary_disable_adapter": counts(canary_rows),
            "M2_repeat": counts(m2r_rows),
            "M1c_base": c_m1c,
            "M3_b2": c_m3,
        },
        "determinism_baseline": determinism,
        "cross_instance_noise": cross_noise,
        "canary": canary,
        "positive_control": positive_control,
        "format_control": fmt,
        "regel6_reference": ref_cmp,
        "decision": {
            "result": decision,
            "rule": rule_no,
            "precondition_failed": failed or None,
            "base_reference_used": {"M2": "M1b_base", "M3": "M1c_base"},
            "rules": [{"nr": num, "text": t} for num, t in rules],
        },
        "grenzen": [
            "Die 15 Zeilen sind TRAININGSzeilen (Dataset 18caaae7...) => M2/M3 messen Memorization, keine Generalisierung.",
            "M3 hat ein Ceiling: der B2-Adapter beantwortete im Altlauf alle 15 Gold-Strings exakt (15/15) "
            "=> M3 kann P-1 vs. P-3 nicht trennen. Diskriminativ waere ein Held-out-Probe-Set.",
            "M3 ist ein historischer Code-Stand (der B2-Adapter hat use_rslora=false) => 'konsistent mit P-1', nicht bewiesen.",
            "Cross-Instance-Noise (M1 vs M1b) ist Rauschen und wird NICHT als Diagnose verwendet; "
            "alle Regelvergleiche nutzen gepaarte Referenzen (M1b fuer M2, M1c fuer M3).",
        ],
    }
    write_json(out_dir / "manifest.json", manifest)
    write_json(
        status_path,
        {"status": "ausgefuehrt", "decision": decision, "rule": rule_no, "precondition_failed": failed or None},
    )
    print(json.dumps(manifest["decision"], ensure_ascii=False, indent=2))
    print(json.dumps(manifest["counts"], ensure_ascii=False, indent=2))
    print(f"Canary (vs M1b, gleiche Instanz): {canary['matched']}/{canary['n']}")
    print(
        f"Positivkontrolle M2 vs canary: differing_items={pc_gen['differing_items']} "
        f"(Logit-Delta {max_logit_delta:.6f}, lora_B_nonzero {lora_b_nonzero})"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
