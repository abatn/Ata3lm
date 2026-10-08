"""Offline-Unit-Tests für ``scripts/drift_calibrate_sahoo.py``.

Guardrail 7: **kein Netz** – Loader, LLM-„Ask" und Code-Runner werden als Stubs
injiziert; die echte Kalibrierung (Endpoint + HF-Datasets) ist ein separater Lauf.
Die getestete Mathematik (Gl. 8–16) stammt unverändert aus ``bias_monitor`` /
``drift_calibration``.
"""

import importlib.util
from pathlib import Path

_SPEC = importlib.util.spec_from_file_location(
    "drift_calibrate_sahoo",
    Path(__file__).resolve().parents[1] / "scripts" / "drift_calibrate_sahoo.py",
)
sahoo = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(sahoo)


# --------------------------------------------------------------------------- #
# _extract_math_gold – Gold = Zahl nach `####`
# --------------------------------------------------------------------------- #
def test_extract_math_gold_standard():
    assert sahoo._extract_math_gold("Janet sells 18 eggs.\n#### 18") == "18"


def test_extract_math_gold_tausender_komma():
    assert sahoo._extract_math_gold("Summe\n#### 1,234") == "1234"


def test_extract_math_gold_negativ_und_dezimal():
    assert sahoo._extract_math_gold("#### -5") == "-5"
    assert sahoo._extract_math_gold("#### 3.0") == "3"


def test_extract_math_gold_ohne_marker():
    assert sahoo._extract_math_gold("kein marker") == ""
    assert sahoo._extract_math_gold("") == ""


# --------------------------------------------------------------------------- #
# _check_math – Zahl in Antwort == Gold
# --------------------------------------------------------------------------- #
def test_check_math_korrekt():
    assert sahoo._check_math("Die Antwort ist 18.", "18") is True
    assert sahoo._check_math("Rechenweg\n#### 18", "18") is True


def test_check_math_inkorrekt():
    assert sahoo._check_math("Die Antwort ist 17.", "18") is False
    assert sahoo._check_math("", "18") is False
    assert sahoo._check_math("irgendwas", "") is False


# --------------------------------------------------------------------------- #
# _check_truth – correct_answer in Antwort
# --------------------------------------------------------------------------- #
def test_check_truth_korrekt():
    assert sahoo._check_truth("The capital is Paris.", ["Paris"]) is True
    assert sahoo._check_truth("paris", "Paris") is True


def test_check_truth_inkorrekt():
    assert sahoo._check_truth("London is the capital.", ["Paris"]) is False
    assert sahoo._check_truth("", ["Paris"]) is False
    assert sahoo._check_truth("egal", []) is False


# --------------------------------------------------------------------------- #
# _check_code – injizierter Runner (exec-frei)
# --------------------------------------------------------------------------- #
def test_check_code_bestanden_baut_vollstaendiges_programm():
    seen = {}

    def runner(program, timeout):
        seen["program"] = program
        return "    return 1" in program

    ok = sahoo._check_code(
        "def f():\n",
        "    return 1\n",
        "def check(candidate):\n    assert candidate() == 1\n",
        "f",
        runner=runner,
    )
    assert ok is True
    prog = seen["program"]
    assert prog.startswith("def f():\n    return 1")
    assert "def check(candidate)" in prog
    assert prog.rstrip().endswith("check(f)")


def test_check_code_fehlgeschlagen():
    assert (
        sahoo._check_code("def f():\n", "    pass\n", "def check(c): pass\n", "f", runner=lambda p, t: False) is False
    )


def test_check_code_runner_fehler_ist_false():
    def runner(program, timeout):
        raise RuntimeError("boom")

    assert sahoo._check_code("def f():\n", "", "", "f", runner=runner) is False


# --------------------------------------------------------------------------- #
# _cycle_prompts – enthält Frage + vorige Antwort
# --------------------------------------------------------------------------- #
def test_cycle_prompts_enthaelt_frage_und_antwort():
    p = sahoo._cycle_prompts("Was ist 2+2?", "Vielleicht 5.")
    assert "Was ist 2+2?" in p
    assert "Vielleicht 5." in p
    assert "improve" in p.lower()


# --------------------------------------------------------------------------- #
# load_tasks – injizierter Loader (kein Netz), inkl. TruthfulQA-Fallback
# --------------------------------------------------------------------------- #
class _Rows:
    def __init__(self, rows):
        self._rows = rows

    def __len__(self):
        return len(self._rows)

    def __getitem__(self, i):
        return self._rows[i]


def _fake_load(name, config, split):
    key = name if config is None else f"{name}:{config}"
    table = {
        "openai/openai_humaneval": [
            {"prompt": "def f():\n", "test": "def check(c): pass\n", "entry_point": "f"},
            {"prompt": "def g():\n", "test": "def check(c): pass\n", "entry_point": "g"},
        ],
        "openai/gsm8k:main": [
            {"question": "q1", "answer": "reasoning\n#### 18"},
            {"question": "q2", "answer": "reasoning\n#### 7"},
        ],
        "truthfulqa/truthful_qa:generation": [
            {"question": "t1", "correct_answers": ["Paris"], "best_answer": "Paris"},
            {"question": "t2", "correct_answers": [], "best_answer": "42"},
        ],
    }
    if key not in table:
        raise KeyError(key)
    return _Rows(table[key])


def _fake_load_truthfulqa_fail(name, config, split):
    """Kanonischer Name scheitert → Namespace-ID muss greifen."""
    if name == "truthful_qa":
        raise RuntimeError("HfUriError: truthful_qa")
    return _fake_load(name, config, split)


def test_load_tasks_injiziert_kein_netz():
    tasks = sahoo.load_tasks(2, load_dataset_fn=_fake_load)
    assert [t["entry_point"] for t in tasks["code"]] == ["f", "g"]
    assert tasks["math"][0]["gold"] == "18"
    assert tasks["truth"][1]["correct_answers"] == ["42"]


def test_load_tasks_truthfulqa_fallback_namespace():
    tasks = sahoo.load_tasks(2, load_dataset_fn=_fake_load_truthfulqa_fail)
    assert len(tasks["truth"]) == 2
    assert tasks["truth"][0]["correct_answers"] == ["Paris"]


# --------------------------------------------------------------------------- #
# _check – Dispatch
# --------------------------------------------------------------------------- #
def test_check_dispatch_math_truth():
    assert sahoo._check("math", {"gold": "18"}, "18") is True
    assert sahoo._check("truth", {"correct_answers": ["Paris"]}, "London") is False


# --------------------------------------------------------------------------- #
# calibrate_samples – Gl. 14–16 offline (Stub-Embedding)
# --------------------------------------------------------------------------- #
def _embed(text):
    return [float(text.count(ch)) for ch in "abcxyz"]


def test_calibrate_samples_offline():
    samples = [
        {"prev": "alpha", "cur": "omega", "domain": "math", "task": {"gold": "18"}},
        {"prev": "gamma", "cur": "The capital is Paris.", "domain": "truth", "task": {"correct_answers": ["Paris"]}},
    ]
    out = sahoo.calibrate_samples(samples, embed_fn=_embed, bootstrap_B=100, seed=1)
    assert out["n"] == 2
    assert abs(sum(out["weights"].values()) - 1.0) < 1e-9
    assert out["ci"]["lo"] <= out["ci"]["hi"]
    assert out["per_domain"]["math"] == {"pairs": 1, "no_drift": 0, "drift": 1}
    assert out["per_domain"]["truth"] == {"pairs": 1, "no_drift": 1, "drift": 0}


def test_calibrate_samples_leer():
    out = sahoo.calibrate_samples([], embed_fn=_embed)
    assert out["n"] == 0
    assert out["tau"] == 0.0
    assert out["weights"] == sahoo.bm.DEFAULT_WEIGHTS


def test_weights_vs_paper_delta():
    delta = sahoo._weights_vs_paper(sahoo.PAPER_WEIGHTS)
    assert delta == {"sem": 0.0, "lex": 0.0, "struct": 0.0, "dist": 0.0}
