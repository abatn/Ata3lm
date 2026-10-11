#!/usr/bin/env python3
"""V1 — Geschlossener Write-Back-Zyklus Θ→Θ′ auf Kaggle (AGENTS.md §10.3).

Dieses Skript fährt den **realen** geschlossenen §10.3-Zyklus in einem Lauf:

  1. **Fakten (Erfahrung):** reale ZsRE-Aufgaben via
     `zsre_corpus.build_zsre_corpus(<workdir>/zsre_validation.jsonl,
     n=N, split="validation")` (neue Quelle ⇒ §9 Human-Gate `ask`; live ggf.
     freizugeben). Es wird nichts erfunden.
  2. **Reale Writes (§10):** je Fakt `pipeline.route_and_store(...)` mit
     `classify_fn=fast_write_router.classify` (echter Endpoint) und
     `mandate_obj=write_gateway.default_mandate("knowledge-agent")`. Nur mit
     `self_update=True` **und** ≥ 2 distinkten `--approver`-Namen schreiben
     `write-new`/`write-update` (§9.3 Zwei-Personen-Freigabe, Gate `ask`).
     Ohne diese Freigabe bleibt der Write auf `ask` – das wird **klar gemeldet**,
     nicht umgangen.
  3. **Pending:** `slow_consolidation.collect_pending(tier3_dir, provenance_log,
     state_path=...)`; der **reale** Provenienz-Log-Pfad wird aus den
     Write-Ergebnissen (`res["provenance_log"]`) bzw. per Glob ermittelt.
  4. **Training (Θ′):** `train_fn(dataset, model)` ruft per Subprocess das echte
     `kaggle/train_slow_consolidation.py` (`--dataset … --out … --source local
     --gpu …`) und liest `<out>/kaggle_output.json` → `{"ok": True, "loss": …,
     "adapter_path": …}` (sonst `{"ok": False}`).
  5. **Probe (externes Signal, §6):** `probe_fn(item)` generiert **Base-vor-
     Adapter** (N8-Muster, `kaggle/e2e_theta_probe.py`) und prüft, ob
     `item["fact"]` als Teilstring in der Θ′-Antwort steht →
     `{"passed": bool, "answer": …}`.
  6. **Write-Back:** `slow_consolidation.write_back(dataset, model,
     train_fn=…, probe_fn=…, tier3_dir=…, provenance_log=…, state_path=…)` –
     Flush nur nach positivem Probe **und** Hash-Gleichheit (F1–F3, fail-closed).
  7. **Ergebnis-JSON:** `<workdir>/write_back_cycle_result.json` mit `flushed`/
     `kept`/`loss`/`adapter_path` und Quelle.

Status: **Auftrag / unverifiziert-lokal.** Der Code ist lokal NICHT
ausführbar (keine GPU, ML-Bibliotheken fehlen). Er wird vom Menschen auf Kaggle
(GPU, echter LLM-Endpoint) gestartet. Erst nach externer Rückgabe des Adapters +
`kaggle_output.json` gilt der Lauf als `belegt` (§6).

Quelle (Belegt): AGENTS.md §10.3 (Write-Back/Slow Consolidation) ·
arXiv:2608.22215 §3.4 (write-back as slow consolidation) · §9.3 (Zwei-Personen,
EU-KI-VO Art. 14(5)) · §6 (externes Signal).

**Kein Fake (Guardrail 7):** es wird nichts simuliert – echte Router-Klassifikation,
echtes Kaggle-Training (Subprocess), echte Θ′-Generierung. Fehlt die GPU, der
LLM-Endpoint oder der Adapter, bricht das Skript **fail-closed** mit klarer
Meldung ab; es werden keine Zahlen erfunden.

**LLM (lokal, kein Secret):** Router + Reflective-Agent nutzen einen **lokalen
Ollama-Endpoint** (`--llm-base-url`, Default `http://127.0.0.1:11434/v1`). Die
Modelle (`--llm-model`, Default `qwen2.5:1.5b`) werden für `FWR_SMALL_MODEL`/
`FWR_LARGE_MODEL`/`HELA_MODEL` gesetzt, sofern nicht per ENV vorgegeben. Ollama
braucht keinen API-Key; der Endpoint wird real geprüft (fail-closed).

**Interface-Stabilität (§9):** NEUE Datei – kein vorhandenes Interface geändert
(`AGENTS.md`, `data/memory/*` unverändert). Nur lesende Nutzung der bestehenden
Funktionen `route_and_store`, `fast_write_router.classify`,
`write_gateway.default_mandate`, `slow_consolidation.collect_pending`/`write_back`
sowie Subprocess-Aufruf des unveränderten `kaggle/train_slow_consolidation.py`.
"""

from __future__ import annotations

import argparse
import json
import os
import random
import subprocess
import sys
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parents[1]
# Import-Pfade wie `scripts/live_run.py` (data/memory + shared + tier3-working + skills).
for _p in ["data/memory", "data/memory/shared", "data/memory/tier3-working", "skills"]:
    sys.path.insert(0, str(ROOT / _p))

STATUS = "Auftrag/unverifiziert-lokal"
SOURCE = "AGENTS.md §10.3 · arXiv:2608.22215 §3.4"
DEFAULT_BASE_MODEL = "Qwen/Qwen2.5-0.5B-Instruct"
DEFAULT_LLM_BASE_URL = "http://127.0.0.1:11434/v1"
DEFAULT_LLM_MODEL = "qwen2.5:1.5b"
TRAIN_SCRIPT = ROOT / "kaggle" / "train_slow_consolidation.py"
TRAIN_OUT_NAME = "slow_consolidation_train"
RESULT_NAME = "write_back_cycle_result.json"
#: Aktionen, die einen echten externen Write bedeuten (§10.7).
_WRITE_ACTIONS = ("write-new", "write-update")


# ----------------------------------------------------------------------- Tasks
def _record_to_task(record) -> Optional[dict]:
    """ZsRE-Record (TRL-Chat) → `(question, fact, correct)`; ungültig ⇒ None.

    Muster wie `scripts/live_run.py::_record_to_task`: `fact` = Gold-Antwort (das zu
    speichernde Wissen), `correct` = dasselbe Gold (Referenz für Router/Compare).
    Zeilen ohne Frage/Antwort werden übersprungen – **nichts wird erfunden**.
    """
    msgs = record.get("messages") if isinstance(record, dict) else None
    if not msgs or len(msgs) < 2:
        return None
    question = str(msgs[0].get("content", "")).strip()
    correct = str(msgs[1].get("content", "")).strip()
    if not question or not correct:
        return None
    return {"question": question, "fact": correct, "correct": correct}


def _load_tasks(zsre_file: Path, n: int, seed: Optional[int]) -> tuple:
    """`n` echte ZsRE-Aufgaben laden (Streaming, gesampelt) + Korpus-Meta.

    Neue Quelle (§9) ⇒ Human-Gate `ask`; der Korpus wird lediglich **vorbereitet**.
    """
    import zsre_corpus

    meta = zsre_corpus.build_zsre_corpus(zsre_file, n=n, split="validation")
    records = [json.loads(line) for line in Path(zsre_file).read_text(encoding="utf-8").splitlines() if line.strip()]
    tasks = []
    for record in records:
        task = _record_to_task(record)
        if task is not None:
            tasks.append(task)
    if seed is not None:
        random.Random(seed).shuffle(tasks)
    return tasks[:n], meta


# ------------------------------------------------------------------- Approvers
def _resolve_approvers(approvers: Optional[list]) -> tuple:
    """`--approver`-Namen → (self_update, distinkte Namen in Reihenfolge).

    §9.3: `approved` nur bei **≥ 2 distinkten** natürlichen Personen
    (`approval.py`). Ohne/mit < 2 distinkten Namen bleibt `self_update=False` ⇒
    Router-Gate `ask`, kein Write ohne Freigabe. Doppelte Namen zählen NICHT.
    """
    distinct: list = []
    for person in approvers or []:
        name = (person or "").strip()
        if name and name not in distinct:
            distinct.append(name)
    return len(distinct) >= 2, distinct


def _questions_by_key(tasks: list) -> dict:
    """Key-Zuordnung (`write_gateway._slug(question)` → echte Frage) für die Probe.

    `collect_pending` rekonstruiert die Frage aus dem Memory-Key (Slug, verlustarm);
    die Probe nutzt hier die **echte** ZsRE-Frage aus den Aufgabendaten.
    """
    import write_gateway

    return {write_gateway._slug(task["question"]): task["question"] for task in tasks}


# ----------------------------------------------------------------- Reale Writes
def _write_facts(tasks: list, *, structured_dir: Path, tier3_dir: Path, self_update: bool, approvers: list) -> tuple:
    """Jeden Fakt durch die **echte** K2-Schreibkette schicken (§10.1/§10.7).

    Ruft `pipeline.route_and_store(...)` – derselbe Pfad wie `scripts/live_run.py`
    (Fast-Write-Router + `write_gateway` inkl. Mandat/Freigabe/Provenienz). Ohne
    ≥ 2-Personen-Freigabe bleibt der Write am Gate `ask` hängen (`ok=False`) und
    wird als `blocked` gezählt. Pro Fakt wird die reale Provenienz-Log-Pfad-Angabe
    aus dem Ergebnis gesammelt. Ein Endpoint-/Laufzeitfehler wird protokolliert,
    **nicht** als Erfolg gewertet (kein Fake).
    """
    import fast_write_router
    import pipeline
    import write_gateway

    mandate_obj = write_gateway.default_mandate("knowledge-agent")
    counts = {"write-new": 0, "write-update": 0, "non-write": 0, "blocked": 0, "error": 0}
    logs: list = []
    details: list = []
    for i, task in enumerate(tasks):
        try:
            res = pipeline.route_and_store(
                question=task["question"],
                fact=task["fact"],
                correct=task["correct"],
                classify_fn=fast_write_router.classify,
                mandate_obj=mandate_obj,
                now=1000.0 + i,
                structured_dir=structured_dir,
                tier3_dir=tier3_dir,
                self_update=self_update,
                approvers=approvers,
            )
        except Exception as exc:  # noqa: BLE001 - echte Fehler protokollieren, kein Fake-Erfolg
            counts["error"] += 1
            details.append(
                {
                    "question": task["question"][:160],
                    "ok": False,
                    "action": None,
                    "gate": None,
                    "reason": f"{type(exc).__name__}: {exc}",
                }
            )
            continue
        action = res.get("action")
        ok = bool(res.get("ok"))
        log = res.get("provenance_log")
        if log:
            logs.append(log)
        if ok and action in _WRITE_ACTIONS:
            counts[action] += 1
        elif action == "none":  # pipeline-Vertrag: non-write → "none"
            counts["non-write"] += 1
        else:
            counts["blocked"] += 1
        details.append(
            {
                "question": task["question"][:160],
                "ok": ok,
                "action": action,
                "gate": res.get("gate"),
                "reason": res.get("reason"),
            }
        )
    return counts, details, logs


def _resolve_provenance_log(logs: list, workdir: Path, tier3_dir: Path) -> Optional[str]:
    """Realen Provenienz-Log-Pfad ermitteln (Write-Ergebnis → Glob → Default).

    `write_gateway.store` protokolliert per Default nach
    `Path(tier3_dir)/"provenance.jsonl"` (K3). Der verlässlichste Beleg ist die
    Pfadangabe im Write-Ergebnis; falls keine vorliegt, wird per Glob gesucht.
    """
    for log in logs or []:
        if log and Path(log).exists():
            return str(log)
    found = sorted(Path(workdir).rglob("provenance.jsonl"))
    if found:
        return str(found[0])
    candidate = Path(tier3_dir) / "provenance.jsonl"
    return str(candidate) if candidate.exists() else None


# ------------------------------------------------------------------ GPU / Train
def _gpu_available() -> tuple:
    """Echte GPU prüfen; fehlt sie ⇒ klare Meldung (kein Fake-Training möglich)."""
    try:
        import torch
    except Exception as exc:  # noqa: BLE001 - fehlende Lib = klarer Fehler
        return False, f"torch nicht importierbar ({type(exc).__name__}: {exc})"
    if not torch.cuda.is_available():
        return False, "torch.cuda.is_available() ist False"
    return True, torch.cuda.get_device_name(0)


def _make_train_fn(out_dir: Path, gpu: str, seed: int, base_model: str):
    """`train_fn(dataset, model)` = **echter** Subprocess des Kaggle-Trainingsskripts.

    Aufruf: `python kaggle/train_slow_consolidation.py --dataset <corpus> --out
    <out_dir> --source local --gpu <gpu>` (unverändertes, in sich geschlossenes
    Skript). Basis-Modell + Seed werden über dessen dokumentierte ENV
    (`BASE_MODEL`, `SEED`) gesetzt. Erfolg nur bei `kaggle_output.json` →
    `{"ok": True, "loss": …, "adapter_path": …}`; sonst `{"ok": False}`
    (fail-closed ⇒ `write_back` flusht nicht).
    """

    def train_fn(dataset_path, model):
        out_dir.mkdir(parents=True, exist_ok=True)
        env = dict(os.environ)
        env["BASE_MODEL"] = str(model or base_model)
        env["SEED"] = str(seed)
        cmd = [
            sys.executable,
            str(TRAIN_SCRIPT),
            "--dataset",
            str(dataset_path),
            "--out",
            str(out_dir),
            "--source",
            "local",
            "--gpu",
            str(gpu),
        ]
        proc = subprocess.run(cmd, env=env, text=True, capture_output=True)
        out_json = out_dir / "kaggle_output.json"
        if proc.returncode != 0 or not out_json.exists():
            print(
                f"FEHLER: Kaggle-Training fehlgeschlagen (rc={proc.returncode}).\n{proc.stderr[-2000:]}",
                file=sys.stderr,
            )
            return {"ok": False, "returncode": proc.returncode}
        data = json.loads(out_json.read_text(encoding="utf-8"))
        return {
            "ok": True,
            "loss": data.get("loss"),
            "adapter_path": data.get("adapter_path") or str(out_dir / "adapter"),
        }

    return train_fn


# ------------------------------------------------------------------- Θ′-Probe
class _ThetaProbe:
    """Externes Probe-Signal Θ′ (Base-vor-Adapter, N8-Muster).

    Lädt das Basis-Modell **vor** dem Aufwickeln des LoRA-Adapters (N8:
    `kaggle/e2e_theta_probe.py`) und generiert je Probe beide Antworten. Ein Fakt
    gilt als konsolidiert, wenn die Θ′-Antwort das Gold (`item["fact"]`) als
    Teilstring enthält (Paper-Test §3.4, ohne Retrieval). Lazy geladen, damit ohne
    pending kein GPU-Speicher belegt wird; ohne GPU/Adapter klarer Fehler.
    """

    def __init__(self, base_model: str, adapter_dir: Path, questions_by_key: dict):
        self.base_model = base_model
        self.adapter_dir = Path(adapter_dir)
        self.questions_by_key = questions_by_key
        self._tok = None
        self._base = None
        self._adapter = None

    def _load(self) -> None:
        if self._adapter is not None:
            return
        import torch
        from peft import PeftModel
        from transformers import AutoModelForCausalLM, AutoTokenizer

        if not torch.cuda.is_available():
            raise RuntimeError("Keine GPU – Θ′-Probe nicht möglich (fail-closed, kein Fake).")
        if not self.adapter_dir.exists():
            raise RuntimeError(f"Adapter nicht gefunden: {self.adapter_dir}")
        tok = AutoTokenizer.from_pretrained(self.base_model)
        if tok.pad_token is None:
            tok.pad_token = tok.eos_token
        dtype = torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16
        try:  # transformers >= 4.56/5.x: `dtype` (PR #39782); sonst älterer Name
            base = AutoModelForCausalLM.from_pretrained(self.base_model, dtype=dtype).cuda().eval()
        except TypeError:
            base = AutoModelForCausalLM.from_pretrained(self.base_model, torch_dtype=dtype).cuda().eval()
        # N8: Basis ZUERST messen, dann denselben Aufruf um den Adapter aufwickeln.
        adapter = PeftModel.from_pretrained(base, str(self.adapter_dir)).eval().cuda()
        self._tok, self._base, self._adapter = tok, base, adapter

    def _answer(self, model, question: str) -> str:
        import torch

        enc = self._tok.apply_chat_template(
            [{"role": "user", "content": question}],
            add_generation_prompt=True,
            return_tensors="pt",
            return_dict=True,
        )
        inputs = {k: v.to(model.device) for k, v in enc.items()}
        with torch.no_grad():
            out = model.generate(**inputs, max_new_tokens=16, do_sample=False)
        return self._tok.decode(out[0][inputs["input_ids"].shape[-1] :], skip_special_tokens=True).strip()

    def __call__(self, item: dict) -> dict:
        self._load()
        key = item.get("key")
        question = self.questions_by_key.get(key) or item.get("question") or ""
        gold = str(item.get("fact") or "").strip()
        base_answer = self._answer(self._base, question)
        adapter_answer = self._answer(self._adapter, question)
        passed = bool(gold) and gold.lower() in adapter_answer.lower()
        return {
            "passed": passed,
            "answer": adapter_answer,
            "base_answer": base_answer,
            "question": question,
            "gold": gold,
        }


# ------------------------------------------------------------------------- CLI
def _parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="V1 geschlossener Write-Back-Zyklus Θ→Θ′ (§10.3, Kaggle-GPU, kein Fake)."
    )
    parser.add_argument("--n", type=int, default=20, help="Anzahl echter ZsRE-Fakten (Default: 20)")
    parser.add_argument(
        "--base-model",
        default=DEFAULT_BASE_MODEL,
        help=f"Basis-Modell für Training/Probe (Default: {DEFAULT_BASE_MODEL})",
    )
    parser.add_argument(
        "--workdir", default="/kaggle/working", help="Arbeits-/Ausgabeordner (Default: /kaggle/working)"
    )
    parser.add_argument("--gpu", default="0", help="CUDA_VISIBLE_DEVICES für das Training (Default: 0)")
    parser.add_argument("--seed", type=int, default=42, help="Seed für Auswahl/Training (Default: 42)")
    parser.add_argument(
        "--llm-base-url",
        default=DEFAULT_LLM_BASE_URL,
        help=f"Lokaler Ollama-Endpoint (Default: {DEFAULT_LLM_BASE_URL})",
    )
    parser.add_argument(
        "--llm-model",
        default=DEFAULT_LLM_MODEL,
        help=f"Ollama-Modell für Router/Reflective-Agent (Default: {DEFAULT_LLM_MODEL})",
    )
    parser.add_argument(
        "--approver",
        action="append",
        default=None,
        metavar="NAME",
        help="Natürliche Person für die §9.3-Zwei-Personen-Freigabe (mehrfach). "
        "Mit ≥ 2 distinkten Namen wird `self_update` aktiviert; sonst bleibt der Write auf `ask`.",
    )
    return parser.parse_args(argv)


# --------------------------------------------------------------- LLM (Ollama)
def _configure_llm_env(base_url: str, model: str) -> dict:
    """Lokalen Ollama-Endpoint + Modelle in die ENV setzen (vor jedem LLM-Import).

    `fast_write_router` liest `FWR_SMALL_MODEL`/`FWR_LARGE_MODEL` **beim Import**,
    `reflective_agent` liest `HELA_MODEL` zur Aufrufzeit. Die ENV wird daher in
    `main()` gesetzt, **bevor** diese Module importiert werden. Vorhandene
    ENV-Werte haben Vorrang (kein Überschreiben). Ollama braucht keinen API-Key.
    """
    applied: dict = {}
    for key, value in {
        "OPENAI_BASE_URL": base_url,
        "OPENAI_API_KEY": "ollama",
        "FWR_SMALL_MODEL": model,
        "FWR_LARGE_MODEL": model,
        "HELA_MODEL": model,
    }.items():
        if not os.environ.get(key):
            os.environ[key] = value
            applied[key] = value
    return applied


def _llm_endpoint_ok(base_url: str, timeout: float = 5.0) -> tuple:
    """Ollama-Endpoint real prüfen (`GET <base>/models`) – kein Fake (§6)."""
    import urllib.request

    url = base_url.rstrip("/") + "/models"
    token = os.environ.get("OPENAI_API_KEY") or "ollama"
    try:
        req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310 - fester Endpoint
            return resp.status == 200, f"HTTP {resp.status} · {url}"
    except Exception as exc:  # noqa: BLE001 - echte Erreichbarkeit klar melden
        return False, f"{type(exc).__name__}: {exc} · {url}"


def main(argv=None) -> int:
    args = _parse_args(argv)
    # LLM-ENV (Ollama) VOR jedem Import von fast_write_router/reflective_agent.
    _configure_llm_env(args.llm_base_url, args.llm_model)
    # GPU-Wahl VOR jedem torch-Import (wie kaggle/train_slow_consolidation.py).
    os.environ["CUDA_VISIBLE_DEVICES"] = str(args.gpu)

    self_update, approvers = _resolve_approvers(args.approver)
    workdir = Path(args.workdir)

    gpu_ok, gpu_info = _gpu_available()
    if not gpu_ok:
        print(
            f"FEHLER: keine GPU ({gpu_info}) – dieses Skript braucht eine Kaggle-GPU (fail-closed, kein Fake).",
            file=sys.stderr,
        )
        return 1
    llm_ok, llm_info = _llm_endpoint_ok(os.environ["OPENAI_BASE_URL"])
    if not llm_ok:
        print(
            f"FEHLER: LLM-Endpoint nicht erreichbar ({llm_info}) – lokalen Ollama starten "
            f"(`ollama serve` + `ollama pull {args.llm_model}`) (fail-closed, kein Fake).",
            file=sys.stderr,
        )
        return 1
    if not self_update:
        print(
            f"WARNUNG: {len(approvers)} distinkte(r) --approver (< 2) – §9.3 Zwei-Personen-Freigabe "
            "fehlt ⇒ Router-Gate 'ask', kein Write. Schreibt nicht; wird als blocked gemeldet.",
            file=sys.stderr,
        )

    workdir.mkdir(parents=True, exist_ok=True)
    structured_dir = workdir / "structured"
    tier3_dir = workdir / "tier3"
    state_path = workdir / "consolidation_state.json"
    dataset_path = workdir / "consolidation_sft.jsonl"

    # 1) Reale Fakten (Erfahrung).
    try:
        tasks, corpus_meta = _load_tasks(workdir / "zsre_validation.jsonl", args.n, args.seed)
    except Exception as exc:  # noqa: BLE001 - echte Lade-Fehler klar melden
        print(f"FEHLER: ZsRE-Korpus nicht ladbar ({type(exc).__name__}: {exc}).", file=sys.stderr)
        return 1
    if not tasks:
        print("FEHLER: keine gültigen ZsRE-Aufgaben geladen (kein Fake).", file=sys.stderr)
        return 1

    # 2) Reale Writes (§10) – nur mit §9.3-Freigabe schreiben write-new/write-update.
    counts, details, logs = _write_facts(
        tasks,
        structured_dir=structured_dir,
        tier3_dir=tier3_dir,
        self_update=self_update,
        approvers=approvers,
    )
    written_total = counts["write-new"] + counts["write-update"]

    # 3) Realer Provenienz-Log-Pfad + pending.
    provenance_log = _resolve_provenance_log(logs, workdir, tier3_dir)

    import slow_consolidation

    pending = (
        slow_consolidation.collect_pending(tier3_dir, provenance_log, state_path=state_path) if provenance_log else []
    )

    # 4)+5) Echtes Training + echte Θ′-Probe (Injektionspunkte von write_back).
    train_out = workdir / TRAIN_OUT_NAME
    train_fn = _make_train_fn(train_out, args.gpu, args.seed, args.base_model)
    probe_fn = _ThetaProbe(args.base_model, train_out / "adapter", _questions_by_key(tasks))

    # 6) Geschlossener Zyklus (Flush nur nach positivem Probe + Hash-Gleichheit).
    write_back = slow_consolidation.write_back(
        dataset_path,
        args.base_model,
        train_fn=train_fn,
        probe_fn=probe_fn,
        tier3_dir=tier3_dir,
        provenance_log=provenance_log,
        state_path=state_path,
    )

    # 7) Ergebnis-JSON.
    result = {
        "status": STATUS,
        "source": SOURCE,
        "n": len(tasks),
        "seed": args.seed,
        "base_model": args.base_model,
        "gpu": gpu_info,
        "llm_base_url": os.environ.get("OPENAI_BASE_URL"),
        "llm_model": args.llm_model,
        "workdir": str(workdir),
        "self_update": self_update,
        "approvers": approvers,
        "writes": counts,
        "write_details": details,
        "provenance_log": provenance_log,
        "pending": len(pending),
        "pending_keys": [p["key"] for p in pending],
        "flushed": write_back.get("flushed"),
        "kept": write_back.get("kept"),
        "loss": write_back.get("loss"),
        "adapter_path": write_back.get("adapter_path"),
        "write_back": write_back,
        "zsre": corpus_meta,
        "dataset": str(dataset_path),
    }
    result_path = workdir / RESULT_NAME
    result_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(
        f"geschrieben: {result_path} · Writes={counts} · pending={len(pending)} · "
        f"flushed={write_back.get('flushed')} · kept={write_back.get('kept')}"
    )
    print(
        json.dumps({"loss": write_back.get("loss"), "adapter_path": write_back.get("adapter_path")}, ensure_ascii=False)
    )

    # Fail-closed: ohne echten Write bzw. bei fehlgeschlagenem Write-Back Exit 1.
    if written_total <= 0:
        print(
            "FEHLER: kein erfolgreicher Write (Gate 'ask' ohne §9.3-Freigabe oder Endpoint-Fehler) "
            f"– siehe {result_path}.",
            file=sys.stderr,
        )
        return 1
    if not write_back.get("ok"):
        print(f"FEHLER: Write-Back nicht erfolgreich – siehe {result_path}.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI
    raise SystemExit(main())
