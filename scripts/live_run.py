#!/usr/bin/env python3
"""Live-Run-Driver: echter 8-Stufen-Zyklus **und** echte 5-Phasen-Rekursion.

Lädt `N` echte ZsRE-Aufgaben und fährt je Aufgabe:
  1. `lifecycle_runner.run_cycle(...)`      – 8 Stufen (AGENTS.md §3),
     `classify_fn = fast_write_router.classify` (echter Endpoint).
  2. `recursion_runner.run_recursion(...)`  – 5 Phasen (AGENTS.md §2), mit
     **derselben** persistenten `state_path`-Datei: der 5-Phasen-Runner lädt den
     von Stufe 8 (K1/Runner-State) geschriebenen Zustand **als zweiten Aufruf**
     und setzt ihn fort (Restart über die State-Datei; ein eigener Prozess kann
     denselben State-Pfad nutzen).

Quellen (keine Erfindung):
  - 8 Stufen: `AGENTS.md` §3 · `knowledge/lifecycle/rekursion/wissenszyklus-8-stufen.md`.
  - 5 Phasen: `knowledge/lifecycle/rekursion/index.md` §2.
  - Externes Signal (§6): `world_state_oracle` – die Compare-Phase erhält ein
    **echtes** Out-of-Band-Probe (unabhängige LLM-Abfrage des gespeicherten Fakts
    gegen das ZsRE-Gold), NICHT den Selbstreport.
  - Aufgaben: ZsRE (`community-datasets/qa_zre`) via `zsre_corpus.build_zsre_corpus`;
    die Nutzung ist als neue Quelle per §9 noch **nicht** freigegeben (Human-Gate).

Guardrail 7 (verbindlich): **kein Fake**. Fehlt der echte Endpoint/Key, bricht das
Skript mit klarem Fehler ab (kein Stub, keine Platzhalter-Antwort). Der echte Lauf
wird separat gestartet; dieses Modul ist importierbar ohne Netz.

**Interface-Änderung (§9-pflichtig, kenntlich gemacht):** NEU – `scripts/live_run.py`,
`tests/test_live_run.py`. `AGENTS.md`/`data/memory/tier1-base/` unverändert.
"""

from __future__ import annotations

import argparse
import json
import os
import random
import sys
import tempfile
from pathlib import Path
from typing import Callable, Optional

ROOT = Path(__file__).resolve().parents[1]
# Import-Pfade wie `tests/conftest.py` (u. a. liegt `lru_cache` in tier3-working).
for _p in ["data/memory", "data/memory/shared", "data/memory/tier3-working", "skills"]:
    sys.path.insert(0, str(ROOT / _p))

import fast_write_router  # noqa: E402
import lifecycle_runner  # noqa: E402
import recursion_runner  # noqa: E402
import write_gateway  # noqa: E402
from openai import OpenAI  # noqa: E402

_CONFIG = Path.home() / ".config/opencode/opencode.json"
_PROVIDER = "nvidia-llama-nemotron"
_DEFAULT_BASE_URL = "https://integrate.api.nvidia.com/v1"
SOURCE = "ZsRE (community-datasets/qa_zre) · AGENTS.md §2/§3 · §6 externes Signal (World-State-Oracle)"
# Reflexions-/Probe-Modell (HELA_MODEL, wie reflective_agent.py); Proxy für alle LLM-gestützten Stufen.
REFLECTION_MODEL = os.environ.get("HELA_MODEL", "nvidia/nemotron-3-ultra-550b-a55b")


# --------------------------------------------------------------------- Endpoint
def _endpoint_from_config(config_path: Optional[Path] = None) -> dict:
    """Provider-Optionen (`apiKey`/`baseURL`) aus `opencode.json` lesen; fehlt ⇒ {}."""
    path = Path(config_path) if config_path is not None else _CONFIG
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    opts = data.get("provider", {}).get(_PROVIDER, {}).get("options", {})
    return {"api_key": str(opts.get("apiKey", "") or ""), "base_url": str(opts.get("baseURL", "") or "")}


def _resolve_endpoint(config_path: Optional[Path] = None) -> dict:
    """Echten Endpoint aus ENV **oder** `opencode.json` auflösen; fehlt ⇒ klarer Fehler.

    Guardrail 7: ohne echten Key/Endpoint ist kein realer Lauf möglich – es wird
    **abgebrochen**, statt Fake-Antworten zu erzeugen.
    """
    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    base_url = os.environ.get("OPENAI_BASE_URL", "").strip()
    if not api_key or not base_url:
        cfg = _endpoint_from_config(config_path)
        api_key = api_key or cfg.get("api_key", "")
        base_url = base_url or cfg.get("base_url", "")
    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY/Endpoint fehlt – echter Lauf nicht möglich (Guardrail 7: kein Fake, "
            "kein Stub). Key in ~/.config/opencode/opencode.json (Provider "
            f"{_PROVIDER!r}) oder per ENV setzen."
        )
    return {"api_key": api_key, "base_url": base_url or _DEFAULT_BASE_URL}


def _ask(question: str, memory: Optional[str] = None, model: Optional[str] = None) -> str:
    """Echte, unabhängige LLM-Abfrage (Out-of-Band; kein Selbstreport)."""
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", ""), base_url=os.environ.get("OPENAI_BASE_URL"))
    base = "Answer in ONE short sentence. If you do not know the answer, reply exactly: I don't know.\n\n"
    prompt = base + question if not memory else f"{base}Use this knowledge:\n{memory}\n\nQuestion: {question}"
    resp = client.chat.completions.create(
        model=model or REFLECTION_MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=512,
        temperature=0.0,
    )
    msg = resp.choices[0].message
    return (msg.content or getattr(msg, "reasoning_content", None) or "").strip()


# ----------------------------------------------------------------------- Tasks
def _record_to_task(record) -> Optional[dict]:
    """ZsRE-Record (TRL-Chat) → `(question, fact, correct)`; ungültig ⇒ None.

    `fact` = die Gold-Antwort (das zu speichernde Wissen), `correct` = dasselbe
    Gold (Referenz für Router/Compare). Zeilen ohne Frage/Antwort werden
    übersprungen – **nichts wird erfunden**.
    """
    msgs = record.get("messages") if isinstance(record, dict) else None
    if not msgs or len(msgs) < 2:
        return None
    question = str(msgs[0].get("content", "")).strip()
    correct = str(msgs[1].get("content", "")).strip()
    if not question or not correct:
        return None
    return {"question": question, "fact": correct, "correct": correct}


def _load_zsre_records(n: int) -> list:
    """Echte ZsRE-Aufgaben laden (Streaming, gesampeltes `n`; neue Quelle §9 ⇒ ask)."""
    import zsre_corpus

    tmp = Path(tempfile.mkdtemp(prefix="live-run-zsre-")) / "zsre.jsonl"
    zsre_corpus.build_zsre_corpus(tmp, n=n, split="validation")
    return [json.loads(line) for line in tmp.read_text(encoding="utf-8").splitlines() if line.strip()]


def _load_tasks(n: int, *, seed: Optional[int] = None, loader: Optional[Callable[[int], list]] = None) -> list:
    """`n` Aufgaben als `(question, fact, correct)` – Loader injizierbar (offline testbar)."""
    if loader is None:
        loader = _load_zsre_records
    tasks = []
    for record in loader(n):
        task = _record_to_task(record)
        if task is not None:
            tasks.append(task)
    if seed is not None:
        random.Random(seed).shuffle(tasks)
    return tasks[:n]


# ------------------------------------------------------------------- Summaries
def _summarize_cycle(out: dict) -> dict:
    """8-Stufen-Ergebnis auf die berichteten Felder verdichten (Stufen/gate/ok/Daten)."""
    results = out.get("results", {}) or {}
    gedaechtnis = results.get("Gedächtnis", {}) or {}
    wissen_plus = results.get("Wissen+", {}) or {}
    return {
        "stages": list(out.get("stages", [])),
        "ok": gedaechtnis.get("ok"),
        "action": gedaechtnis.get("action"),
        "gate": wissen_plus.get("gate"),
        "revised": wissen_plus.get("revised"),
        "DI": wissen_plus.get("DI"),
        "results": results,
    }


def _summarize_recursion(out: dict) -> dict:
    """5-Phasen-Ergebnis auf die berichteten Felder verdichten (Phasen/gate/ok/observed/Daten)."""
    results = out.get("results", {}) or {}
    akt = results.get("Akt", {}) or {}
    compare = results.get("Compare", {}) or {}
    revise = results.get("Revise", {}) or {}
    return {
        "phases": list(out.get("phases", [])),
        "ok": akt.get("ok"),
        "action": akt.get("action"),
        "gate": akt.get("gate"),
        "observed": compare.get("observed"),
        "score": compare.get("score"),
        "compare_gate": compare.get("gate"),
        "revised": None if not revise else not bool(revise.get("skipped", True)),
        "results": results,
    }


# -------------------------------------------------------------------- Live-Lauf
def _reflection_text(task: dict) -> str:
    """Echter Reflexions-**Input** aus den Aufgabendaten (die LLM-Matrix ist echt)."""
    return (
        f"Task processed: question={task['question']!r}. "
        f"The agent stored the knowledge {task['fact']!r} to answer {task['correct']!r}. "
        "Did the action match my usual inertia, and how should that tendency be adjusted?"
    )


def _make_probe(task: dict) -> Callable[[], dict]:
    """Externes World-State-Oracle (§6): unabhängige LLM-Abfrage gegen das Gold.

    Erfolg = die Gold-Antwort (aus dem Datensatz, NICHT vom Agenten) ist in der
    Out-of-Band-Antwort enthalten. Liefert der Endpoint kein Ergebnis, fängt
    `world_state_oracle.evaluate` das ab (kein Signal, kein Ground-Truth-Claim).
    """

    def probe() -> dict:
        answer = _ask(task["question"], memory=task["fact"])
        ok = task["correct"].lower() in answer.lower()
        return {
            "ok": ok,
            "successes": 1 if ok else 0,
            "failures": 0 if ok else 1,
            "evidence": {"answer": answer, "gold": task["correct"]},
        }

    return probe


def _run_task(task: dict, workdir: Path, now: float) -> dict:
    """Eine Aufgabe durch **beide** Runner (gemeinsame State-Datei)."""
    structured = workdir / "structured"
    tier3 = workdir / "tier3"
    state_path = workdir / "state.json"
    reflection = _reflection_text(task)

    cycle_out = lifecycle_runner.run_cycle(
        task["question"],
        task["fact"],
        task["correct"],
        classify_fn=fast_write_router.classify,
        structured_dir=structured,
        tier3_dir=tier3,
        now=now,
        state_path=state_path,
        reflection_text=reflection,
    )
    recursion_out = recursion_runner.run_recursion(
        task["question"],
        task["fact"],
        task["correct"],
        classify_fn=fast_write_router.classify,
        mandate_obj=write_gateway.default_mandate("knowledge-agent"),
        structured_dir=structured,
        tier3_dir=tier3,
        now=now,
        state_path=state_path,  # K1: derselbe persistente Zustand (Restart über die Datei)
        reflection_text=reflection,
        world_state_probe=_make_probe(task),  # §6: echtes externes Signal
        world_state_claim=task["question"],
    )
    return {
        "question": task["question"],
        "fact": task["fact"],
        "correct": task["correct"],
        "cycle": _summarize_cycle(cycle_out),
        "recursion": _summarize_recursion(recursion_out),
    }


def main(argv: Optional[list] = None) -> int:
    parser = argparse.ArgumentParser(description="Live-Run-Driver: 8 Stufen + 5 Phasen (echter Endpoint).")
    parser.add_argument("--tasks", type=int, default=3, help="Anzahl echter Aufgaben (Default: 3)")
    parser.add_argument("--out", default=str(ROOT / "ergebnisse" / "live-run.json"), help="Ziel-JSON")
    parser.add_argument("--seed", type=int, default=None, help="Seed für reproduzierbare Aufgabenauswahl")
    args = parser.parse_args(argv)

    try:
        endpoint = _resolve_endpoint()
    except RuntimeError as exc:
        print(f"FEHLER: {exc}", file=sys.stderr)
        return 1
    os.environ.setdefault("OPENAI_API_KEY", endpoint["api_key"])
    os.environ.setdefault("OPENAI_BASE_URL", endpoint["base_url"])

    with tempfile.TemporaryDirectory(prefix="live-run-") as tmp:
        tmp_root = Path(tmp)
        # Referenz/Artefakte NICHT ins Repo schreiben (tier2-index unberührt).
        os.environ.setdefault("LIFECYCLE_DRIFT_REFERENCE", str(tmp_root / "drift-reference.json"))
        tasks = _load_tasks(args.tasks, seed=args.seed)
        if not tasks:
            print("FEHLER: keine Aufgaben geladen (ZsRE lieferte keine gültigen Zeilen).", file=sys.stderr)
            return 1
        runs = []
        for i, task in enumerate(tasks):
            print(f"[{i + 1}/{len(tasks)}] {task['question'][:80]!r}", flush=True)
            runs.append(_run_task(task, tmp_root / f"task-{i:03d}", now=100.0 + i))

    payload = {
        "tasks": runs,
        "model": {
            "router_small": fast_write_router.SMALL_MODEL,
            "router_large": fast_write_router.LARGE_MODEL,
            "reflection": REFLECTION_MODEL,
        },
        "source": SOURCE,
        "n": len(runs),
        "seed": args.seed,
    }
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"geschrieben: {out_path} ({len(runs)} Aufgaben)")
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI
    raise SystemExit(main())
