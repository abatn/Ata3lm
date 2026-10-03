#!/usr/bin/env python3
"""
Reflective Agent – laufender Prozess (HeLa-Mem, ACL 2026).

Quelle: HeLa-Mem, arXiv:2604.16839, §3.3 "Reflective Memory Agent" + §4.4.
Wörtlich aus dem Paper:
  - Hub Detection (Eq. 2): D(v_i) = sum_{j in N(i)} w_ij > delta_hub
  - "the agent retrieves the hub node along with its strongly connected neighbors.
     The LLM synthesizes this cluster of related memories to identify common themes
     and causal relationships, abstracting them into declarative semantic entries.
     These distilled records are stored in the Semantic Memory Store."
  - Adaptive Forgetting: below retention threshold.

Lab-Prinzip: keine Erfindung – Mechanismus wörtlich aus der Quelle; nur die
Dateipfade sind die Projekt-Bindung (Auftrag).
"""

import json
import os
from pathlib import Path

# Projekt-Pfade (Auftrag)
ROOT = Path("/home/opc/knowledge-agent")
GRAPH_FILE = Path(os.environ.get("HELA_GRAPH", str(ROOT / "data/memory/tier1-base/episodic_graph.json")))
STRUCTURED = ROOT / "knowledge/structured"
INDEX_DIR = ROOT / "data/memory/tier2-index"

# HeLa-Mem-Parameter (Paper §3.3): delta_hub = Schwellwert für Hub-Konsolidierung
DELTA_HUB = float(os.environ.get("HELA_DELTA_HUB", "1.0"))
# Adaptive Forgetting (HeLa-Mem §3.3): DREI Bedingungen gleichzeitig:
#   (1) total edge weight < delta_prune  (strukturelle Irrelevanz)
#   (2) inactive duration  > delta_age   (temporale Dormanz)
#   (3) zero recent access
DELTA_PRUNE = float(os.environ.get("HELA_DELTA_PRUNE", "0.05"))  # Auftrag
DELTA_AGE_DAYS = float(os.environ.get("HELA_DELTA_AGE_DAYS", "60"))  # Auftrag (HeLa-Mem tau=60)
RETAIN_MIN = float(os.environ.get("HELA_RETAIN_MIN", "0.05"))  # legacy (nur 1 Bedingung)

# --- SEAA HMM-Trägheit (arXiv:2609.17331) ---
# Zustandsraum (Paper §5.7.1): K=4 latente Zustände
HMM_STATES = int(os.environ.get("SEAA_STATES", "4"))  # K (SEAA Table 2)
HMM_LR = float(os.environ.get("SEAA_LR", "0.05"))  # eta (SEAA Table 2)
HMM_BETA = float(os.environ.get("SEAA_BETA", "4.0"))  # beta (SEAA Table 2)
# Paper §5.7.1: S = {calm, alert, impulsive, pessimistic}
STATE_NAMES = ["calm", "alert", "impulsive", "pessimistic"]


def _row_normalize(P):
    return P / P.sum(axis=1, keepdims=True)


def _matrix_from_raw(raw: str, k: int):
    """LLM-Rohtext -> K×K-Matrix oder None (reine Funktion; mit echten Strings testbar)."""
    import re

    import numpy as np

    m = re.search(r"\[[\s\S]*\]", raw or "")
    if not m:
        return None  # NOOP: kein JSON im Text
    try:
        candidate = np.array(json.loads(m.group(0)), dtype=float)
    except Exception:
        return None
    return candidate if candidate.shape == (k, k) else None  # NOOP: falsche Form


def parse_transition_delta(text: str, k: int):
    """Δ(R_t): Richtungsmatrix aus dem Reflexionstext (SEAA Eq. 2).

    Die Matrix kommt **ausschließlich vom LLM**. Gibt es keine gültige K×K-Matrix
    (kein Key, kein JSON, falsche Form, Fehler), wird **NICHTS** geliefert
    (`None`) – kein Update, keine Ersatz-Matrix, kein Crash (NOOP).

    Quellen (verifiziert 2026-10-01, HTTP 200):
      - SEAA (arXiv:2609.17331): Δ(R_t) ist K×K (K=4, Paper §5.7.1).
      - Mem0-Memory-Operationen: vier Aktionen ADD/UPDATE/DELETE/**NONE**;
        NONE = „no change" (keine Änderung, wenn nichts Verwertbares vorliegt).
        https://github.com/mem0ai/mem0/blob/v1.0.10/docs/open-source/features/custom-update-memory-prompt.mdx
      - „Honest Lying" (arXiv:2605.29463, ICML-2026-Workshop): ungeprüfte
        Selbst-Diagnosen im Schreibpfad sind schädlich – „a memory system that
        stores confident, plausible-sounding but wrong beliefs is worse than no
        memory at all" → hier: lieber NOOP als eine erfundene Matrix.
    """
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        return None  # NOOP: ohne LLM keine Matrix
    try:
        from openai import OpenAI

        client = OpenAI(api_key=key, base_url=os.environ.get("OPENAI_BASE_URL"))
        # SEAA §4.2: Die Reflexion beantwortet 4 Fragen; (4) ist die
        # "language-to-parameter mapping" = strukturierte Edit von P_t.
        prompt = (
            "Review this reflection; state was one of the agent's latent states.\n"
            "(1) Did the action match my usual inertia?\n"
            "(2) Which inertial tendency drove the decision, and was it biased?\n"
            "(3) How should that tendency be adjusted?\n"
            f"(4) What is the corresponding structured edit to P_t? "
            f"Return ONLY a JSON array of {k} arrays of {k} numbers (the direction matrix delta), "
            f"row-normalizable, where a negative diagonal entry means less inertia (more deviation).\n"
            f"Reflection:\n{text}"
        )
        resp = client.chat.completions.create(
            model=os.environ.get("HELA_MODEL", "nvidia/nemotron-3-ultra-550b-a55b"),
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2000,
            temperature=0.0,
        )
        msg = resp.choices[0].message
        raw = msg.content or getattr(msg, "reasoning_content", None) or ""
        return _matrix_from_raw(raw, k)
    except Exception:
        return None  # NOOP: Fehler -> überspringen


HMM_NOOP_NOTE = "HMM-Update übersprungen (keine LLM-Matrix)"


class HMMInertia:
    """SEAA HMM-Trägheit: editierbare Zustandsübergangsmatrix (arXiv:2609.17331).

    Zwei Wege (beide im Paper):
      - Eq. 2 (LLM):  P_{t+1} = Normalize(P_t + eta * Delta(R_t))  [update_from_reflection]
      - Eq. 3/4 (LLM-frei, "direct numerical realization of Eq. 2") [step_free_prototype]
        P_t = softmax(log P_base + beta * V_t)
        r_t = cos(b_z, n_t) - 0.80 + eps
        V_{t+1}[z] = clip(V_t[z] + eta * tanh(2 r_t))
    Zustandsraum (Paper §5.7.1): K=4, S={calm, alert, impulsive, pessimistic}.

    NOOP (Mem0 „NONE", Honest Lying arXiv:2605.29463): ohne gültige LLM-Matrix
    bleibt P_t unverändert – kein Update, kein Crash, keine Ersatz-Matrix.
    """

    def __init__(self, states: int = HMM_STATES, lr: float = HMM_LR, beta: float = HMM_BETA):
        import numpy as np

        self.K = states
        self.lr = lr
        self.beta = beta
        self.P = np.full((states, states), 1.0 / states)  # uniform (SEAA Listing 1)
        # P_base diagonal-dominant (SEAA Table 2)
        self.P_base = np.full((states, states), 0.1)
        np.fill_diagonal(self.P_base, 0.7)
        self.V = np.zeros(states)  # state-preference vector (init 0, SEAA §5.7.1)
        self.z = 0  # current latent state
        # Prototyp-Verhalten pro Zustand (3 Traits, SEAA §5.7.1)
        self.state_behavior = np.array(
            [
                [0.8, 0.2, 0.4],  # calm
                [0.5, 0.5, 0.6],  # alert
                [0.2, 0.9, 0.7],  # impulsive
                [0.3, 0.1, 0.2],  # pessimistic
            ]
        )

    def update_from_reflection(self, text: str, delta=None):
        """Eq. 2 (LLM): Reflexion ändert die Übergangswahrscheinlichkeiten.

        NOOP: liefert `parse_transition_delta` keine gültige K×K-Matrix, wird
        NICHTS geändert (`P_t` bleibt), und das Ergebnis trägt
        `skipped=True` + `note=HMM_NOOP_NOTE`. `delta` kann als echte Matrix
        vorab übergeben werden (dann kein LLM-Call).
        """
        if delta is None:
            delta = parse_transition_delta(text, self.K)
        if delta is None:
            return {
                "before": self.P.tolist(),
                "after": self.P.tolist(),
                "delta": None,
                "lr": self.lr,
                "skipped": True,
                "note": HMM_NOOP_NOTE,
            }
        before = self.P.copy()
        self.P = _row_normalize(self.P + self.lr * delta)
        return {
            "before": before.tolist(),
            "after": self.P.tolist(),
            "delta": delta.tolist(),
            "lr": self.lr,
            "skipped": False,
        }

    def step_free_prototype(self, n_t=None):
        """LLM-freier Kern (SEAA §5.7.1, Eq. 3/4). Kein LLM nötig."""
        import numpy as np

        if n_t is None:
            n_t = np.array([0.4, 0.4, 0.2])  # persönliches Erfahrungsbedürfnis
        z = self.z
        b = self.state_behavior[z]
        cos = float(np.dot(b, n_t) / (np.linalg.norm(b) * np.linalg.norm(n_t) + 1e-9))
        r = cos - 0.80 + np.random.randn() * 0.10  # Eq. 4
        self.V[z] = np.clip(self.V[z] + self.lr * np.tanh(2 * r), -10, 10)  # Eq. 4
        # Eq. 3: P_t = softmax(log P_base + beta * V_t); V[j] verstärkt Spalte j
        # (Übergänge IN Zustand j) -> konzentriert P auf dominante Zustände.
        self.P = np.exp(np.log(self.P_base) + self.beta * self.V[None, :])
        self.P = self.P / self.P.sum(axis=1, keepdims=True)
        # Zustandsübergang (Eq. 3): sample nächster Zustand
        self.z = int(np.random.choice(self.K, p=self.P[z]))
        return {
            "state": STATE_NAMES[z],
            "next_state": STATE_NAMES[self.z],
            "r": round(r, 4),
            "V": [round(v, 4) for v in self.V.tolist()],
            "P_row0": [round(x, 4) for x in self.P[0].tolist()],
        }


def load_graph(path: Path) -> dict:
    return json.loads(path.read_text())


def hub_score(graph: dict, node: str) -> float:
    """Eq. 2: D(v_i) = sum_{j in N(i)} w_ij  (associative strength)."""
    return sum(graph.get("edges", {}).get(node, {}).values())


def neighbors(graph: dict, node: str) -> list:
    return list(graph.get("edges", {}).get(node, {}).keys())


def detect_hubs(graph: dict) -> list:
    """Nodes mit D(v_i) > delta_hub (HeLa-Mem §3.3 Hub Detection)."""
    return [n for n in graph.get("nodes", {}) if hub_score(graph, n) > DELTA_HUB]


def detect_forgetting(graph: dict, now_days: float = 0.0) -> list:
    """Adaptive Forgetting (HeLa-Mem §3.3): nur wenn ALLE drei Bedingungen gelten:
      (1) hub_score (total edge weight) < delta_prune,
      (2) inaktive Dauer > delta_age,
      (3) zero recent access.
    Fehlende Metadaten werden als „aktiv" gewertet (konservativ, kein Löschen)."""
    out = []
    for n in graph.get("nodes", {}):
        node = graph["nodes"][n]
        weight = hub_score(graph, n)
        last = float(node.get("last_access_days", now_days))
        age = now_days - last
        access = int(node.get("recent_access", 1))
        if weight < DELTA_PRUNE and age > DELTA_AGE_DAYS and access == 0:
            out.append(n)
    return out


def resolve_conflict(facts: list, subject: str, predicate: str, obj: str, now_iso: str) -> dict:
    """Konfliktlösung (Memory Survey + Graphiti): bei Widerspruch wird der alte
    Fakt NICHT gelöscht, sondern mit Supersede-Marker invalidiert; der neue gilt.

    - Memory Survey (arXiv:2603.07670): „contradiction detection", „temporal
      versioning (prefer the newest record)".
    - Graphiti (arXiv:2501.13956, Projekt): alte Fakten invalidieren, nicht löschen.
    """
    delta = {"conflict": False, "superseded": [], "added": None}
    for f in facts:
        if f.get("s") == subject and f.get("p") == predicate and f.get("status") == "valid" and f.get("o") != obj:
            f["status"] = "superseded"
            f["invalid_at"] = now_iso
            delta["superseded"].append(dict(f))
            delta["conflict"] = True
    new = {"s": subject, "p": predicate, "o": obj, "status": "valid", "valid_from": now_iso, "invalid_at": None}
    facts.append(new)
    delta["added"] = dict(new)
    return delta


def simulate_lifecycle() -> dict:
    """Lifecycle-Demo: Konsolidierung (Hub), Adaptive Forgetting (3 Bed.), Konflikt."""
    # Synthetischer Graph (kein Schreiben nach tier1-base)
    graph = {
        "nodes": {
            "hub_n2": {"content": "Hub", "last_access_days": 100.0, "recent_access": 3},
            "isolated_n5": {"content": "isoliert", "last_access_days": 0.0, "recent_access": 0},
        },
        "edges": {"hub_n2": {"n0": 0.9, "n1": 0.9}, "isolated_n5": {"n9": 0.01}},
    }
    now = 100.0
    hubs = detect_hubs(graph)
    forgotten = detect_forgetting(graph, now_days=now)

    facts = [
        {
            "s": "solver",
            "p": "current_version",
            "o": "berechne_durchschnitt",
            "status": "valid",
            "valid_from": "2026-09-30",
            "invalid_at": None,
        }
    ]
    conflict = resolve_conflict(facts, "solver", "current_version", "berechne_median", "2026-10-01")
    return {
        "consolidation": {"hubs": hubs, "action": "hebbian-distillation"},
        "forgetting": {"forgotten": forgotten, "conditions": "weight<delta_prune AND age>delta_age AND access==0"},
        "conflict": conflict,
    }


def distill(graph: dict, hub: str) -> dict:
    """Hebbian Distillation: Hub + stark verbundene Nachbarn -> semantischer Eintrag.

    Der LLM-Schritt aus dem Paper wird hier optional über OPENAI_* ausgeführt;
    ohne LLM wird die Cluster-Struktur deterministisch zusammengefasst (Auftrag).
    """
    ns = neighbors(graph, hub)
    node_texts = [graph["nodes"][hub].get("content", hub)] + [
        graph["nodes"][n].get("content", n) for n in ns if n in graph.get("nodes", {})
    ]
    cluster = " | ".join(node_texts)

    # Optionaler LLM-Syntheseschritt (Paper: "The LLM synthesizes this cluster")
    key = os.environ.get("OPENAI_API_KEY")
    if key:
        try:
            from openai import OpenAI

            client = OpenAI(api_key=key, base_url=os.environ.get("OPENAI_BASE_URL"))
            prompt = (
                "Synthesize this cluster of related memories into a single declarative "
                f"semantic entry (common themes + causal relationships):\n{cluster}"
            )
            resp = client.chat.completions.create(
                model=os.environ.get("HELA_MODEL", "nvidia/nemotron-3-ultra-550b-a55b"),
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2000,
                temperature=0.0,
            )
            msg = resp.choices[0].message
            summary = _summary_from_raw(msg.content or getattr(msg, "reasoning_content", None), cluster)
        except Exception as e:
            summary = f"(LLM nicht verfügbar: {e}) {cluster}"
    else:
        summary = cluster

    return {"hub": hub, "neighbors": ns, "summary": summary, "hub_score": hub_score(graph, hub)}


def _summary_from_raw(raw, cluster: str) -> str:
    """LLM-Rohtext -> Summary; leer -> „(LLM leer) …" (reine Funktion, real testbar)."""
    s = (raw or "").strip()
    return s if s else f"(LLM leer) {cluster}"


def write_semantic(entry: dict) -> Path:
    """Destillierten Eintrag in den semantischen Store schreiben (knowledge/structured/)."""
    STRUCTURED.mkdir(parents=True, exist_ok=True)
    path = STRUCTURED / f"distilled-hub-{entry['hub']}.md"
    path.write_text(
        f"# Destilliert: Hub {entry['hub']}\n\n"
        f"- Ontologie-Bezug: Wissen (2) – Hebbian Distillation\n"
        f"- Quelle: HeLa-Mem (arXiv:2604.16839)\n"
        f"- Evidence: Hub-Score D(v)={entry['hub_score']:.2f} > delta_hub\n"
        f"- Status: destilliert\n"
        f"- Nachbarn: {', '.join(entry['neighbors'])}\n\n"
        f"## Destilliertes semantisches Wissen\n\n{entry['summary']}\n\n"
        f"## Quellen\n- https://arxiv.org/abs/2604.16839\n"
    )
    return path


def update_index(entry: dict) -> Path:
    """Konzept-Index aktualisieren: Konzept -> Ort (tier2-index/). Idempotent."""
    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    path = INDEX_DIR / "hub-index.md"
    header = "# Tier 2 – Hub-Index (Reflective Agent)\n\n| Konzept | Ort | Hub-Score |\n|---|---|---|\n"
    rows = {}
    if path.exists():
        for ln in path.read_text().splitlines():
            if ln.startswith("| Hub "):
                parts = [p.strip() for p in ln.strip("|").split("|")]
                rows[parts[0]] = ln
    rows[f"Hub {entry['hub']}"] = (
        f"| Hub {entry['hub']} | `knowledge/structured/distilled-hub-{entry['hub']}.md` | D={entry['hub_score']:.2f} |"
    )
    path.write_text(header + "\n".join(rows[k] for k in sorted(rows)) + "\n")
    return path


def run_once() -> dict:
    graph = load_graph(GRAPH_FILE)
    hubs = detect_hubs(graph)
    forgotten = detect_forgetting(graph)
    hmm = HMMInertia()  # SEAA-HMM-Trägheitsmatrix
    results = []
    routed: list = []
    # Pipeline-Aufrufer (A): opt-in, verbindet die Prozess-Kette (pipeline.py).
    route_pipeline = os.environ.get("PIPELINE_ROUTE") == "1"
    _pipe = None
    if route_pipeline:
        import time

        import mandate as _md
        import pipeline as _pl

        now = time.time()
        _reg = _md.MandateRegistry()
        _mandate = _reg.issue(
            principal="Batnini",
            agent="knowledge-agent",
            actions={"write:memory"},
            resources={"data/memory"},
            amount_limit=100.0,
            max_uses=1000,
            valid_from=0.0,
            valid_until=now + 31_536_000,
            approval_threshold=50.0,
        )
        _pipe = _pl
    for hub in hubs:
        entry = distill(graph, hub)
        sem = write_semantic(entry)
        idx = update_index(entry)
        # SEAA: Reflexion ändert die HMM-Übergangswahrscheinlichkeiten (Eq. 2)
        p_change = hmm.update_from_reflection(entry["summary"])
        if route_pipeline:  # destillierter Hub = neues semantisches Wissen → write-new
            routed.append(
                _pipe.route_and_store(
                    question=f"hub-{hub}",
                    fact=entry["summary"],
                    correct="",
                    classify_fn=lambda q, f, c: {"class": "write-new"},
                    mandate_obj=_mandate,
                    now=now,
                    structured_dir=STRUCTURED,
                    tier3_dir=ROOT / "data/memory/tier3-working",
                )
            )
        results.append(
            {
                "hub": hub,
                "score": entry["hub_score"],
                "semantic": str(sem),
                "index": str(idx),
                "hmm_P_before": p_change["before"],
                "hmm_P_after": p_change["after"],
                "hmm_skipped": p_change["skipped"],
            }
        )
    # Red-Queen-Loop (§9.3 freigegeben 2026-10-02, Batnini + taouefik):
    # DAUERHAFT AKTIV (Default an); expliziter Aus-Schalter RQGM_LOOP=0 für Debug/Tests.
    rqgm = None
    if os.environ.get("RQGM_LOOP", "1") != "0":
        import evaluator_version as _rq

        anchor = _rq.GroundTruthAnchor(items=list(_rq.ANCHOR_ITEMS), source="demo")
        loop = _rq.RedQueenLoop(anchor, checkpoints={1, 2, 4, 8})
        rqgm = loop.run([_rq.EvaluatorVersion("", _rq.make_grader(t), threshold=t) for t in (0.0, 0.5, 0.7)])
    return {
        "hubs": hubs,
        "forgotten": forgotten,
        "distilled": results,
        "hmm_states": hmm.K,
        "hmm_lr": hmm.lr,
        "rqgm": rqgm,
        "pipeline": routed if route_pipeline else None,
    }


# --- HeLa-Mem Dual-Path Spreading Activation Retrieval (arXiv:2604.16839 §3.4) ---
# Base Activation (Eq. 3): S_base(v_i) = (sim(q,e_i) + alpha*keyword_match) * gamma(v_i)
#   gamma(v_i) = exp(-dt/tau)  (Zeitzerfall), tau = 60 Tage
# Spreading Activation: S(v_j) = S_base(v_j) + beta * sum_{i in N(j)} S_base(v_i) * w_ij
# Parameter (HeLa-Mem): tau=60, beta=0.1, theta=0.6 (Spreading-Schwelle)
TAU_DAYS = float(os.environ.get("HELA_TAU_DAYS", "60"))
ALPHA = float(os.environ.get("HELA_ALPHA", "1.0"))
BETA = float(os.environ.get("HELA_BETA", "0.1"))
THETA = float(os.environ.get("HELA_THETA", "0.6"))


def _embed(text: str, dim: int = 64):
    """Einfache deterministische Embedding-Ersatzfunktion (Auftrag, kein Modell)."""
    import numpy as np

    v = np.zeros(dim)
    for tok in str(text).lower().split():
        v[hash(tok) % dim] += 1.0
    n = np.linalg.norm(v)
    return v / n if n > 0 else v


def _cos(a, b) -> float:
    import numpy as np

    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    return float(np.dot(a, b) / (na * nb)) if na > 0 and nb > 0 else 0.0


class DualPathRetrieval:
    """HeLa-Mem Dual-Path Retrieval: Base + Spreading Activation (arXiv:2604.16839 §3.4)."""

    def __init__(self, tau: float = TAU_DAYS, alpha: float = ALPHA, beta: float = BETA, theta: float = THETA):
        self.tau, self.alpha, self.beta, self.theta = tau, alpha, beta, theta

    def base_activation(self, graph: dict, query: str, now_days: float) -> dict:
        """Eq. 3: S_base(v_i) = (sim(q,e_i) + alpha*keyword_match) * gamma(v_i)."""
        import math

        q = _embed(query)
        q_tokens = set(query.lower().split())
        out = {}
        for nid, node in graph.get("nodes", {}).items():
            e = _embed(node.get("content", nid))
            sim = _cos(q, e)
            kw = len(q_tokens & set(str(node.get("content", "")).lower().split()))
            kw_match = 1.0 if kw > 0 else 0.0
            dt = max(0.0, now_days - float(node.get("timestamp_days", 0.0)))
            gamma = math.exp(-dt / self.tau)  # Zeitzerfall
            out[nid] = (sim + self.alpha * kw_match) * gamma
        return out

    def spreading_activation(self, graph: dict, s_base: dict) -> dict:
        """Spreading: S(v_j) = S_base(v_j) + beta * sum_{i in N(j)} S_base(v_i)*w_ij."""
        s = dict(s_base)
        for j in graph.get("nodes", {}):
            inflow = 0.0
            for i, edges in graph.get("edges", {}).items():
                if j in edges:  # i -> j Kante
                    inflow += s_base.get(i, 0.0) * edges[j]
            s[j] = s_base.get(j, 0.0) + self.beta * inflow
        return s

    def retrieve(self, graph: dict, query: str, now_days: float = 0.0, top_k: int = 5) -> dict:
        s_base = self.base_activation(graph, query, now_days)
        s = self.spreading_activation(graph, s_base)
        # Schwelle: nur Knoten über theta gelten als "aktiviert"
        activated = {k: round(v, 4) for k, v in s.items() if v >= self.theta}
        ranked = sorted(s.items(), key=lambda kv: -kv[1])[:top_k]
        # Spreading-Gewinn = S - S_base (welche Knoten durch Spreading dazukamen)
        gain = {k: round(s[k] - s_base.get(k, 0.0), 4) for k in s}
        return {
            "base": {k: round(v, 4) for k, v in s_base.items()},
            "spread": {k: round(v, 4) for k, v in s.items()},
            "gain": gain,
            "activated": activated,
            "top_k": [k for k, _ in ranked],
        }


def simulate_5_multihop(graph: dict = None):
    """5 Multi-Hop-Abfragen: zeigt, welche Knoten durch Spreading aktiviert werden."""
    if graph is None:
        graph = load_graph(GRAPH_FILE)
    dr = DualPathRetrieval()
    queries = [
        "Rekursions-Zyklus Compare Revise",
        "Solver Bug Integer-Division",
        "HMM Traegheit Revise",
        "Fast Write Routing entscheidet",
        "Minimum erstes Element",
    ]
    out = []
    for q in queries:
        r = dr.retrieve(graph, q, now_days=1.0, top_k=5)
        # Knoten, die NUR durch Spreading über theta kommen (nicht in base)
        spread_only = [k for k in r["spread"] if r["spread"][k] >= dr.theta and r["base"].get(k, 0.0) < dr.theta]
        out.append(
            {
                "query": q,
                "top_k": r["top_k"],
                "activated": list(r["activated"].keys()),
                "spread_only": spread_only,
                "gain": r["gain"],
            }
        )
    return out


def simulate_3_reflections():
    """3 verbale Reflexionen: jede parst Δ(R_t) und aktualisiert P_t.

    SEAA (arXiv:2609.17331): „reflection changing who the agent is" (Eq. 2).
    """
    hmm = HMMInertia()
    reflections = [
        "The action was wrong and led to a failure; I should deviate more.",
        "The action matched my usual inertia; keep this tendency.",
        "The decision was biased and needs adjustment.",
    ]
    out = []
    for i, text in enumerate(reflections, 1):
        before = hmm.P.copy()
        ch = hmm.update_from_reflection(text)
        out.append(
            {
                "reflection": i,
                "text": text,
                "P_before_row0": [round(x, 4) for x in before[0].tolist()],
                "P_after_row0": [round(x, 4) for x in ch["after"][0]],
                "delta_row0": ([round(x, 4) for x in ch["delta"][0]] if ch["delta"] is not None else None),
                "skipped": ch["skipped"],
                "note": ch.get("note", ""),
                "lr": hmm.lr,
            }
        )
    return out


# --- Lyapunov-bounded adaptive damping (WhyLab C3, arXiv-GitHub neogenesislab) ---
def lyapunov_check(energies: list, tau: float = 0.0) -> dict:
    """E[ΔV] ≤ 0 (WhyLab C3): mittlere Energieänderung nicht-positiv ⇒ stabil/kontraktiv.
    Bei Verletzung (E[ΔV] > tau) → Human-Gate (ask)."""
    if len(energies) < 2:
        return {"E_dV": 0.0, "stable": True, "gate": "ok", "note": "zu wenig Daten"}
    dV = [float(energies[i + 1]) - float(energies[i]) for i in range(len(energies) - 1)]
    e_dv = sum(dV) / len(dV)
    stable = e_dv <= tau
    return {
        "E_dV": round(e_dv, 4),
        "dV": [round(x, 4) for x in dV],
        "stable": stable,
        "gate": "ok" if stable else "ask",
    }


def simulate_lyapunov() -> dict:
    """Zwei Verläufe: stabil (E[ΔV] ≤ 0) vs. instabil (E[ΔV] > 0)."""
    stable_seq = [1.0, 0.8, 0.6, 0.45, 0.3, 0.2]  # fallende „Energie" (V sinkt)
    unstable_seq = [0.2, 0.3, 0.5, 0.8, 1.2, 1.7]  # steigende „Energie" (V wächst)
    return {"stable": lyapunov_check(stable_seq), "unstable": lyapunov_check(unstable_seq)}


if __name__ == "__main__":
    if os.environ.get("SPREAD_SIM") == "5":
        print(json.dumps(simulate_5_multihop(), ensure_ascii=False, indent=2))
    elif os.environ.get("SEAA_SIM") == "3":
        print(json.dumps(simulate_3_reflections(), ensure_ascii=False, indent=2))
    elif os.environ.get("MEMORY_LIFECYCLE_SIM") == "1":
        print(json.dumps(simulate_lifecycle(), ensure_ascii=False, indent=2))
    elif os.environ.get("LYAPUNOV_SIM") == "1":
        print(json.dumps(simulate_lyapunov(), ensure_ascii=False, indent=2))
    else:
        out = run_once()
        print(json.dumps(out, ensure_ascii=False, indent=2))
