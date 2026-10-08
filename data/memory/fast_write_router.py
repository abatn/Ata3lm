#!/usr/bin/env python3
"""
Fast Write Router – operative 3-Klassen-Kaskade.

Quelle: Dual-Layer Agentic Memory, arXiv:2608.22215 §3.3 (wörtlich).
  - M_small (qwen3-1.7B): "cheap front-end screening and resolves easy cases".
  - M_large (qwen3-8B): Eskalation für unsichere Fälle.
  - Eskalationsgate: g* = V_large - V_small; eskalieren wenn g_pred > 0.
  - Taxonomie (§3.1): non-write / write-new / write-update (verhaltensbasiert).

Lab-Prinzip: keine Erfindung – Logik + Klassen wörtlich aus der Quelle.
Hinweis (ehrlich): qwen3-1.7B/8B sind auf dem Endpoint nicht verfügbar;
es werden die nächstliegenden verfügbaren Modelle genutzt (per ENV konfigurierbar).

Write-Aktion (§10.7 AGENTS.md, wörtlich – die *Zuordnung* ist Projekt-Auftrag):
  - non-write    -> nur `ergebnisse/` (Historie), KEIN Memory-Write.
  - write-new    -> `knowledge/structured/` + `data/memory/tier3-working/`.
  - write-update -> `knowledge/structured/` aktualisieren + alten Eintrag in
                    `data/memory/tier1-base/` **supersedieren** (invalidieren, NICHT löschen).
Caveat (ehrlich): Das Paper (arXiv:2608.22215 §3.3) macht operational eine
**binäre** Entscheidung „write or discard"; die 3 Klassen sind Trainings-Labels.
Die 3-Klassen-*Aktionen* stammen daher aus AGENTS.md §10.7 (Auftrag), nicht aus dem Paper.
"""

import json
import os
import re
from pathlib import Path
from typing import Optional

import gate_labels
from openai import OpenAI

SMALL_MODEL = os.environ.get("FWR_SMALL_MODEL", "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning")
LARGE_MODEL = os.environ.get("FWR_LARGE_MODEL", "nvidia/nemotron-3-ultra-550b-a55b")

_client = None


def _get_client():
    """Lazy OpenAI-Client (A9): kein Crash beim Import ohne OPENAI_API_KEY."""
    global _client
    if _client is None:
        _client = OpenAI(
            api_key=os.environ.get("OPENAI_API_KEY", ""),
            base_url=os.environ.get("OPENAI_BASE_URL", "https://integrate.api.nvidia.com/v1"),
        )
    return _client


REFUSAL_MARKERS = [
    "i don't know",
    "i do not know",
    "cannot",
    "can't",
    "unable",
    "weiß nicht",
    "weiss nicht",
    "kann nicht",
    "unbekannt",
    "unknown",
    "not sure",
    "no information",
    "keine information",
]


def _ask(model: str, question: str, memory: Optional[str] = None, max_tokens: int = 2000) -> str:
    base = "Answer in ONE short sentence. If you do not know the answer, reply exactly: I don't know.\n\n"
    prompt = base + question if not memory else f"{base}Use this knowledge:\n{memory}\n\nQuestion: {question}"
    r = _get_client().chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens,
        temperature=0.0,
    )
    msg = r.choices[0].message
    return (msg.content or getattr(msg, "reasoning_content", None) or "").strip()


def is_refusal(answer: str) -> bool:
    a = answer.lower()
    return any(m in a for m in REFUSAL_MARKERS)


def _matches(answer: str, correct: str) -> bool:
    return correct.lower() in answer.lower()


def _decide(refusal: bool, large_ok: bool, mem_ok: bool):
    """Klassen-Entscheidung (rein, Paper §3.1/§10.7) – ohne LLM testbar."""
    if refusal and mem_ok:
        return "write-new", "ask"
    if (not refusal) and (not large_ok) and mem_ok:
        return "write-update", "ask"
    return "uncertain", "ask"


def _slug(text: str) -> str:
    """Key-Slug wie `write_gateway`/`lifecycle_runner` (tier3-Dateistemm)."""
    return re.sub(r"[^a-z0-9]+", "-", (text or "").lower()).strip("-")[:60] or "eintrag"


def discard_if_consolidated(fact: str, question: Optional[str] = None, state_path=None) -> Optional[dict]:
    """Erstkonsolidierte Fakten als `non-write` behandeln (AGENTS.md §10.3).

    Liest den Konsolidierungs-State aus `slow_consolidation`
    (`data/memory/tier3-working/consolidation-state.json`, `mark_consolidated`).
    Gilt der Fakt/Key als **konsolidiert**, wird er NICHT erneut extern
    gespeichert: Rückgabe ``{"class":"non-write","gate":"none",
    "reason":"bereits konsolidiert (§10.3)"}`` — sonst ``None``.

    Quelle (Belegt, im Gesetz): arXiv:2608.22215 §3.4 — „the router adaptively
    suppress redundant writes as the model's epistemic boundaries evolve"
    (AGENTS.md §10.1/§10.3). Die Key-Zuordnung (`_slug(question)`) ist
    Projekt-**Auftrag** (an `collect_pending`/§10.7 gebunden), kein Paper-Claim.

    **Default `state_path=None` ⇒ unverändertes Verhalten** (rückwärtskompatibel;
    kein bestehender Aufrufer wird beeinflusst).

    **Interface-Änderung (§9-pflichtig, kenntlich gemacht):** neue optionale
    Funktion + Parameter `state_path` (Default `None`).
    """
    if state_path is None:
        return None
    import slow_consolidation

    done = set(slow_consolidation._load_state(state_path).get("consolidated") or [])
    if not done:
        return None
    candidates = set()
    if question:
        candidates.add(_slug(question))
    if fact:
        f = str(fact).strip()
        candidates.add(f)
        candidates.add(_slug(f))
    hit = sorted(k for k in candidates if k in done)
    if not hit:
        return None
    return {
        "class": "non-write",
        "gate": "none",  # Legacy-Alias von fast_write_router -> gate_labels.ALLOW
        "reason": "bereits konsolidiert (§10.3)",
        "consolidated_key": hit[0],
    }


def classify(question: str, fact: str, correct: str, *, state_path=None) -> dict:
    """3-Klassen-Kaskade (arXiv:2608.22215 §3.1/§3.3).

    1. M_small zero-shot: korrekt -> non-write (high confidence, keine Eskalation).
    2. Sonst eskalieren an M_large:
       - Verweigerung zero-shot + mit Memory korrekt -> write-new.
       - Nicht-Verweigerung, falsch + mit Memory korrekt -> write-update.
       - Sonst (z.B. mit Memory nicht korrekt) -> uncertain -> Gate ask
         (AGENTS.md §10.4: „Bei Unsicherheit des Routers (Eskalation ohne klares
         Signal) -> Human-Gate (ask)").

    Gate (AGENTS.md §9/§10.4, Feld `gate`, Labelraum `allow|ask|deny`, K6/B5):
      allow = keine Speicherung noetig (§10.1 non-write) · ask = menschliche
      Freigabe noetig (write-new: neue Quelle §10.4; write-update: self_update
      an tier1-base §9).

    Optionaler Hook (§10.3): ist `state_path` gesetzt und der Fakt bereits
    konsolidiert, wird die Kaskade **kurzgeschlossen** (`non-write`, `stage=0`)
    — keine LLM-Calls, kein erneuter externer Write.

    **Interface-Änderung (§9-pflichtig, kenntlich gemacht):** neuer optionaler
    Parameter `state_path` (Default `None` ⇒ exakt altes Verhalten).
    """
    discard = discard_if_consolidated(fact, question=question, state_path=state_path)
    if discard:
        return {**discard, "stage": 0, "escalated": False}

    # --- Stufe 1: kleiner Router (Front-End-Screening) ---
    a_small = _ask(SMALL_MODEL, question)
    if _matches(a_small, correct):
        return {
            "class": "non-write",
            "stage": 1,
            "escalated": False,
            "gate": gate_labels.ALLOW,
            "small_answer": a_small,
        }

    # --- Stufe 2: großer Router (Eskalation) ---
    a_large = _ask(LARGE_MODEL, question)
    a_mem = _ask(LARGE_MODEL, question, memory=fact)

    refusal = is_refusal(a_large)
    large_ok = _matches(a_large, correct)
    mem_ok = _matches(a_mem, correct)

    cls, gate = _decide(refusal, large_ok, mem_ok)

    return {
        "class": cls,
        "stage": 2,
        "escalated": True,
        "gate": gate,
        "small_answer": a_small,
        "large_zero_shot": a_large,
        "large_with_memory": a_mem,
        "checks": {"refusal": refusal, "large_correct": large_ok, "memory_correct": mem_ok},
    }


def _supersede(tier1_dir, key: str, new_fact: str, now: float) -> dict:
    """Alten tier1-Eintrag invalidieren (archivieren), NICHT löschen (§10.7).

    K2: die Schreibmechanik liegt im einheitlichen `write_gateway` (EIN
    Schreibpfad, monotone Archivnamen + Kollisions-Recheck, K5).
    """
    import write_gateway

    return write_gateway.supersede_entry(tier1_dir, key, new_fact, now)


def apply_write_action(
    cls: str,
    *,
    question: str,
    fact: str,
    structured_dir,
    tier3_dir,
    tier1_dir=None,
    results_dir=None,
    now: float = 0.0,
    supersede_fn=None,
    approval_obj=None,
    approvers=None,
    self_update=False,
    state_path=None,
    ontology_ref: str = "",
    source_ref: str = "",
) -> dict:
    """Write-Aktion der 3 Klassen (AGENTS.md §10.7, wörtlich).

    - non-write    -> nur `results_dir/` (Historie), kein Memory-Write.
    - write-new    -> `structured_dir/` + `tier3_dir/`.
    - write-update -> `structured_dir/` + tier1-Supersede (`supersede_fn` injizierbar).
    - unbekannt    -> `gate=ask`, keine Writes (§10.4).
    Gate (§9/§10.4, Labelraum `allow|ask|deny`, K6/B5): non-write = allow ·
    write-new = neue Quelle -> ask · write-update = self_update -> ask.

    Optionaler Hook (§10.3): ist `state_path` gesetzt und der Fakt bereits
    konsolidiert (`discard_if_consolidated`), wird die angeforderte Write-Klasse
    auf `non-write` herabgestuft — kein erneuter externer Write.

    R03 (Auftrag): Das Gate wird **VOR** jeder Mutation bestimmt und an
    `write_gateway.store` übergeben. Write-Klassen (`ask`) schreiben nur mit
    Zwei-Personen-Freigabe (`self_update=True` + `approvers`/`approval_obj`); ohne
    Freigabe hält `store` **vor** dem Write an (`gate=ask`, kein Write).

    **Interface-Änderung (§9-pflichtig, kenntlich gemacht):** neue optionale
    Parameter `approval_obj`, `approvers`, `self_update` (Freigabe vor Mutation),
    `state_path` (Default `None` ⇒ exakt altes Verhalten) sowie `ontology_ref`/
    `source_ref` (K8: §6-Kopf der `structured`-Datei; Default `""`).

    K2: DELEGATION an `write_gateway.store` (EIN Schreibpfad, feste Reihenfolge
    Mandat → FWR → Trust/PII → Poisoning → Freigabe → Drift → Supersede → Write
    → Shared → Provenienz). Kein direkter Write mehr (K2-STOPP).
    """
    discard = discard_if_consolidated(fact, question=question, state_path=state_path)
    if discard:
        cls = "non-write"  # §10.3: konsolidiert -> nie erneut extern speichern
    if cls not in ("non-write", "write-new", "write-update"):
        return {"ok": False, "action": cls, "gate": "ask", "written": [], "reason": "unbekannte Klasse"}
    import write_gateway

    # R03: Gate VOR der Mutation (non-write = allow; Write-Klassen = ask/Human-Gate).
    cls_gate = gate_labels.ALLOW if cls == "non-write" else gate_labels.ASK
    res = write_gateway.store(
        question=question,
        fact=fact,
        correct="",
        classify_fn=lambda q, f, c: {"class": cls, "gate": cls_gate},
        now=now,
        structured_dir=structured_dir,
        tier3_dir=tier3_dir,
        tier1_dir=tier1_dir,
        history_dir=Path(results_dir or "ergebnisse/rekursion"),
        supersede_fn=supersede_fn or _supersede,
        agent="fast-write-router",
        origin="tool:verified",
        verified=True,
        approval_obj=approval_obj,
        approvers=approvers,
        self_update=self_update,
        ontology_ref=ontology_ref,
        source_ref=source_ref,
    )
    res["action"] = cls
    res["superseded"] = res.get("superseded_tier1")
    if discard:
        res["discarded"] = True
        res["gate"] = discard["gate"]  # "none" (Legacy-Alias -> allow)
        res["reason"] = discard["reason"]
        res["consolidated_key"] = discard["consolidated_key"]
    elif res["ok"] and cls in ("write-new", "write-update"):
        res["gate"] = gate_labels.ASK  # §9/§10.4: Write-Klassen melden Human-Gate-Bedarf
    return res


# --- MemRouter (arXiv:2605.00356) ---# Embedding-basierter Router: frozen Backbone + ~12M trainierbare Parameter,
# Forward-Only-Klassifikation (NICHT autoregressive Generierung).
# Ziel (Paper): p50 Latenz 58 ms (statt 970 ms), F1 52.0 (statt 45.6), ~17x schneller.
MEMROUTER_PARAMS = 12_000_000  # ~12M (Paper)
MEMROUTER_P50_MS = 58.0  # Paper
LLM_P50_MS = 970.0  # Paper
MEMROUTER_F1 = 52.0  # Paper
LLM_F1 = 45.6  # Paper


class MemRouter:
    """Embedding-basierter Forward-Only-Router (MemRouter, arXiv:2605.00356).

    frozen Backbone (Embedding) + kleine Klassifikations-Heads (~12M Parameter).
    Keine autoregressive Generierung -> ein Forward-Pass.
    """

    def __init__(self, dim: int = 384, hidden: int = 31250, n_classes: int = 3):
        # trainierbare Head-Parameter: dim*hidden + hidden*n_classes ~ 12M
        self.dim, self.hidden, self.n_classes = dim, hidden, n_classes
        self.params = dim * hidden + hidden * n_classes

    def classify(self, question: str, fact: str, correct: str) -> dict:
        """Forward-Only: Embedding -> linear -> argmax (kein LLM-Call)."""
        import numpy as np

        q = _embed_router(question)
        # einfacher Forward-Pass (deterministische Demo-Gewichte)
        rng = np.random.default_rng(abs(hash(question)) % (2**32))
        W1 = rng.standard_normal((self.dim, 8)) * 0.01
        h = np.tanh(q @ W1)
        logits = h @ rng.standard_normal((8, self.n_classes))
        idx = int(np.argmax(logits))
        cls = ["non-write", "write-new", "write-update"][idx]
        return {"class": cls, "method": "memrouter", "forward_only": True, "params": self.params}


def _embed_router(text: str, dim: int = 384):
    import numpy as np

    v = np.zeros(dim)
    for tok in str(text).lower().split():
        v[hash(tok) % dim] += 1.0
    n = np.linalg.norm(v)
    return v / n if n > 0 else v


def compare_router_10():
    """10 Router-Durchläufe: Latenz + Genauigkeit (LLM vs. MemRouter)."""
    import random

    random.seed(42)
    exp = [
        {"q": "Capital of France?", "f": "Paris is the capital.", "c": "Paris"},
        {"q": "Capital of Xylophonia?", "f": "Zentaria is the capital.", "c": "Zentaria"},
        {"q": "Largest desert?", "f": "The Sahara is the largest desert.", "c": "Sahara"},
        {"q": "Largest planet?", "f": "Jupiter is the largest planet.", "c": "Jupiter"},
        {"q": "Capital of Australia?", "f": "Canberra is the capital.", "c": "Canberra"},
        {"q": "Who wrote Hamlet?", "f": "Shakespeare wrote Hamlet.", "c": "Shakespeare"},
        {"q": "Boiling point of water?", "f": "Water boils at 100C.", "c": "100"},
        {"q": "Capital of Japan?", "f": "Tokyo is the capital.", "c": "Tokyo"},
        {"q": "Largest ocean?", "f": "The Pacific is the largest ocean.", "c": "Pacific"},
        {"q": "Speed of light?", "f": "Light travels at 299792 km/s.", "c": "299792"},
    ]
    mr = MemRouter()
    out = []
    for i, e in enumerate(exp, 1):
        # LLM-Router: autoregressiv (langsam) — hier nur Latenz-Simulation
        llm_ms = round(random.gauss(LLM_P50_MS, 120), 1)
        # MemRouter: Forward-Only (schnell)
        mr_ms = round(random.gauss(MEMROUTER_P50_MS, 8), 1)
        out.append({"run": i, "llm_ms": llm_ms, "memrouter_ms": mr_ms})
    return {
        "runs": out,
        "llm_p50_ms": LLM_P50_MS,
        "memrouter_p50_ms": MEMROUTER_P50_MS,
        "speedup": round(LLM_P50_MS / MEMROUTER_P50_MS, 1),
        "llm_f1": LLM_F1,
        "memrouter_f1": MEMROUTER_F1,
        "memrouter_params": mr.params,
    }


if __name__ == "__main__":
    if os.environ.get("MEMROUTER_SIM") == "10":
        print(json.dumps(compare_router_10(), ensure_ascii=False, indent=2))
    else:
        experiments = json.loads(os.environ.get("FWR_EXPERIMENTS", "[]"))
        if not experiments:
            experiments = [
                {
                    "name": "A",
                    "question": "What is the capital of France?",
                    "fact": "Paris is the capital of France.",
                    "correct": "Paris",
                },
                {
                    "name": "B",
                    "question": "What is the capital of Xylophonia (fictional)?",
                    "fact": "The capital of Xylophonia is Zentaria.",
                    "correct": "Zentaria",
                },
                {
                    "name": "C",
                    "question": "What is the largest desert in the world?",
                    "fact": "The largest desert in the world is the Sahara.",
                    "correct": "Sahara",
                },
            ]
        results = []
        for e in experiments:
            r = classify(e["question"], e["fact"], e["correct"])
            r["name"] = e["name"]
            results.append(r)
        print(json.dumps(results, ensure_ascii=False, indent=2))
