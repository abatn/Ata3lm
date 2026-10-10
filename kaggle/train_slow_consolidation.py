"""M1b — Kaggle-Training: Slow Consolidation (Write-Back, Theta -> Theta').

Status: Auftrag / unverifiziert-lokal. Dieser Code ist hier NICHT ausfuehrbar
(keine GPU, ML-Bibliotheken lokal nicht installiert). Er wird vom Menschen auf
Kaggle (GPU) ausgefuehrt. Kein Fake-Erfolg wird behauptet.

Quelle des Verfahrens: AGENTS.md §10.3 (Write-Back / Slow Consolidation),
connectors/fast-write-routing.md, Paper arXiv:2608.22215 §3.4.
Dataset-Format: Chat (messages / conversations / prompt+response).

Waehlbare Datenquelle (`SFT_SOURCE`), klar gekennzeichnet:
  - `zsre`     : **§10.3-Konsolidierungskorpus** aus dem offiziellen ZsRE-Benchmark
                 (`community-datasets/qa_zre`, HF; Levy et al. 2017). Fakten aus
                 arXiv:2608.22215v2 Appendix A.1. Braucht Kaggle-Internet.
  - `local`    : von M1 erzeugtes `consolidation_sft.jsonl` (Default, §10.3).
  - `capybara` : **DEMO** (`LDJnr/Capybara`) – NICHT der §10.3-Korpus.

Aufruf (Kaggle) – CLI (bevorzugt) oder Umgebungsvariablen:
    !python train_slow_consolidation.py --dataset /kaggle/working/train_f6.jsonl \
        --out /kaggle/working --source local --gpu 0 --epochs 3
    bzw. ENV: SFT_SOURCE, BASE_MODEL, SFT_DATASET_PATH, OUTPUT_DIR, NUM_EPOCHS,
    MAX_LENGTH, SEED, HF_TOKEN, ZSRE_N, ZSRE_SPLIT, CAPYBARA_N, CAPYBARA_SPLIT.
    CLI-Argumente ueberschreiben die ENV-Werte.

Hinweis (Hardware, belegt): bf16-Mathematik braucht Compute Capability >= 8.0
(Ampere+). Auf Turing (T4, sm_75) faellt das Skript automatisch auf fp16 zurueck
(`torch.cuda.get_device_capability`), weil der TRL-Fused-Kernel sonst mit
"gemm input type at::BFloat16 and output type float ... 8.0 or higher" abbricht.
Quelle: PyTorch-Doku `torch.cuda.is_bf16_supported`; CUDA-GEMM bf16->fp32 ab sm_80.
"""

import argparse
import hashlib
import json
import os
import platform
import random
import time

SEED = int(os.environ.get("SEED", "42"))
BASE_MODEL = os.environ.get("BASE_MODEL", "Qwen/Qwen2.5-0.5B-Instruct")
OUTPUT_DIR = os.environ.get("OUTPUT_DIR", os.environ.get("KAGGLE_WORKING_DIR", "."))
ADAPTER_DIR = os.path.join(OUTPUT_DIR, "adapter")
OUTPUT_JSON = os.path.join(OUTPUT_DIR, "kaggle_output.json")
MAX_LENGTH = int(os.environ.get("MAX_LENGTH", "1024"))
NUM_EPOCHS = float(os.environ.get("NUM_EPOCHS", "3"))
PER_DEVICE_BATCH = int(os.environ.get("PER_DEVICE_BATCH", "4"))
GRAD_ACCUM = int(os.environ.get("GRAD_ACCUM", "4"))
LEARNING_RATE = float(os.environ.get("LEARNING_RATE", "2e-4"))
LORA_R = int(os.environ.get("LORA_R", "16"))
LORA_ALPHA = int(os.environ.get("LORA_ALPHA", "32"))
LORA_DROPOUT = float(os.environ.get("LORA_DROPOUT", "0.05"))
DATASET_NAME = "consolidation_sft.jsonl"

# Datenquelle: zsre (§10.3-Korpus) | local (M1-JSONL) | capybara (DEMO)
SFT_SOURCE = os.environ.get("SFT_SOURCE", "local").strip().lower()
ZSRE_DATASET = os.environ.get("ZSRE_DATASET", "community-datasets/qa_zre")
ZSRE_SPLIT = os.environ.get("ZSRE_SPLIT", "train")
ZSRE_N = int(os.environ.get("ZSRE_N", "10000"))
CAPYBARA_DATASET = os.environ.get("CAPYBARA_DATASET", "LDJnr/Capybara")
CAPYBARA_SPLIT = os.environ.get("CAPYBARA_SPLIT", "train")
CAPYBARA_N = int(os.environ.get("CAPYBARA_N", "10000"))

SOURCE_NOTES = {
    "zsre": "§10.3 (Write-Back-Korpus aus ZsRE, arXiv:2608.22215v2 A.1)",
    "local": "M1 consolidation_sft.jsonl (lokal, §10.3)",
    "capybara": "DEMO (Capybara) - NICHT der §10.3-Korpus",
}

REQUIRED_LIBS = {
    "transformers": "transformers",
    "peft": "peft",
    "trl": "trl",
    "bitsandbytes": "bitsandbytes",
    "datasets": "datasets",
    "accelerate": "accelerate",
    "torch": "torch",
}


def set_seed(seed):
    random.seed(seed)
    os.environ["PYTHONHASHSEED"] = str(seed)
    try:
        import numpy as np

        np.random.seed(seed)
    except Exception:
        pass
    import torch

    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    try:
        from transformers import set_seed as hf_set_seed

        hf_set_seed(seed)
    except Exception:
        pass


def get_hf_token():
    token = os.environ.get("HF_TOKEN") or os.environ.get("HUGGING_FACE_HUB_TOKEN")
    if token:
        return token
    try:
        from kaggle_secrets import UserSecretsClient

        return UserSecretsClient().get_secret("HF_TOKEN")
    except Exception:
        return None


def library_versions():
    versions = {}
    for key, mod_name in REQUIRED_LIBS.items():
        try:
            mod = __import__(mod_name)
            versions[key] = getattr(mod, "__version__", "unknown")
        except Exception:
            versions[key] = None
    return versions


def find_dataset():
    explicit = os.environ.get("SFT_DATASET_PATH")
    candidates = []
    if explicit:
        candidates.append(explicit)
    candidates.append(os.path.join(os.getcwd(), DATASET_NAME))
    for root in ("/kaggle/input", "/kaggle/working", os.getcwd()):
        if os.path.isdir(root):
            for dirpath, _dirnames, filenames in os.walk(root):
                if DATASET_NAME in filenames:
                    candidates.append(os.path.join(dirpath, DATASET_NAME))
    for path in candidates:
        if path and os.path.isfile(path):
            return os.path.abspath(path)
    raise FileNotFoundError(
        f"'{DATASET_NAME}' nicht gefunden. Lege es als Kaggle-Dataset unter "
        f"/kaggle/input/<slug>/ ab oder setze SFT_DATASET_PATH."
    )


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def normalize_messages(record):
    if isinstance(record.get("messages"), list):
        out = []
        for msg in record["messages"]:
            role = msg.get("role") or msg.get("from")
            content = msg.get("content", msg.get("value", ""))
            out.append({"role": str(role), "content": str(content)})
        return out
    if isinstance(record.get("conversations"), list):
        role_map = {"human": "user", "gpt": "assistant", "system": "system", "user": "user", "assistant": "assistant"}
        out = []
        for msg in record["conversations"]:
            role = role_map.get(str(msg.get("from", "user")), str(msg.get("from", "user")))
            out.append({"role": role, "content": str(msg.get("value", ""))})
        return out
    if "prompt" in record and "response" in record:
        return [
            {"role": "user", "content": str(record["prompt"])},
            {"role": "assistant", "content": str(record["response"])},
        ]
    if isinstance(record.get("text"), str):
        return None
    raise ValueError(f"Unbekanntes Datensatz-Format. Keys: {sorted(record.keys())}")


def load_dataset_rows(path):
    from datasets import Dataset

    rows = []
    row_hashes = []
    with open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            record = json.loads(line)
            messages = normalize_messages(record)
            if messages is None:
                rows.append({"text": record["text"]})
            else:
                rows.append({"messages": messages})
            if isinstance(record.get("hash"), str):
                row_hashes.append(record["hash"])
    if not rows:
        raise ValueError(f"Datensatz '{path}' enthaelt keine Zeilen.")
    return Dataset.from_list(rows), row_hashes


def canonical_sha256(messages):
    """SHA-256 ueber die kanonisch serialisierten `messages` (Inhalts-Hash je Zeile).

    Gleiche Semantik wie M1 (`provenance.content_hash`) und `zsre_corpus`: bindet
    den Adapter an den Zeileninhalt (vgl. AGENTS.md §6).
    """
    canonical = json.dumps(messages, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def load_zsre_rows(n, split, dataset_name):
    """§10.3-Korpus aus dem offiziellen ZsRE-Benchmark streamen (HF).

    Quelle: `community-datasets/qa_zre` (Levy et al. 2017); Fakten-Korpus des
    Papers arXiv:2608.22215v2 (Appendix A.1). Je Fakt ein Chat-Beispiel
    `(question, answers[0])`.

    Subjektbindung (analog `data/memory/zsre_corpus.py::row_to_record`; die
    Formatänderung ist dort §9-approved, Batnini + Taoufik, 2026-10-08): enthält
    die ``question`` den ZsRE-Platzhalter ``XXX`` **und** ist ein ``subject``
    vorhanden, wird ``XXX`` durch das Subjekt ersetzt (alle Vorkommen). Fehlt das
    ``subject``, bleibt die Frage unverändert - es wird nichts erfunden. Die Logik
    ist hier **inline gespiegelt**, weil dieses Skript laut `kaggle/README.md`
    „in sich geschlossen" auf Kaggle laeuft und `zsre_corpus.py` dort nicht
    mitgeliefert wird.

    Zeilen ohne nicht-leere Frage oder Antwort werden uebersprungen (reale Daten -
    es wird nichts erfunden).
    """
    from datasets import Dataset, load_dataset

    stream = load_dataset(dataset_name, split=split, streaming=True)
    rows = []
    row_hashes = []
    scanned = 0
    skipped = 0
    for row in stream:
        scanned += 1
        question = str(row.get("question") or "").strip()
        subject = str(row.get("subject") or "").strip()
        if "XXX" in question and subject:  # Subjektbindung (analog row_to_record)
            question = question.replace("XXX", subject)
        answers = row.get("answers") or []
        answer = str(answers[0]).strip() if answers else ""
        if not question or not answer:
            skipped += 1
            continue
        messages = [
            {"role": "user", "content": question},
            {"role": "assistant", "content": answer},
        ]
        rows.append({"messages": messages})
        row_hashes.append(canonical_sha256(messages))
        if len(rows) >= n:
            break
    if not rows:
        raise ValueError(f"ZsRE '{dataset_name}'[{split}] lieferte keine verwertbaren Zeilen.")
    meta = {"rows_scanned": scanned, "skipped_empty": skipped, "requested": n, "split": split, "dataset": dataset_name}
    return Dataset.from_list(rows), row_hashes, meta


def load_capybara_rows(n, split, dataset_name):
    """**DEMO**-Korpus aus Capybara streamen (HF) - NICHT der §10.3-Korpus.

    Quelle: `LDJnr/Capybara` (Felder `source`, `conversation` = Liste
    `{input, output}`). Nur zur Demonstration des Write-Back-Laufs.
    """
    from datasets import Dataset, load_dataset

    stream = load_dataset(dataset_name, split=split, streaming=True)
    rows = []
    row_hashes = []
    scanned = 0
    skipped = 0
    for row in stream:
        scanned += 1
        messages = []
        for turn in row.get("conversation") or []:
            inp = str(turn.get("input") or "").strip()
            out = str(turn.get("output") or "").strip()
            if inp and out:
                messages.append({"role": "user", "content": inp})
                messages.append({"role": "assistant", "content": out})
        if not messages:
            skipped += 1
            continue
        rows.append({"messages": messages})
        row_hashes.append(canonical_sha256(messages))
        if len(rows) >= n:
            break
    if not rows:
        raise ValueError(f"Capybara '{dataset_name}'[{split}] lieferte keine verwertbaren Zeilen.")
    meta = {"rows_scanned": scanned, "skipped_empty": skipped, "requested": n, "split": split, "dataset": dataset_name}
    return Dataset.from_list(rows), row_hashes, meta


def final_train_loss(trainer):
    for record in reversed(trainer.state.log_history):
        if "loss" in record and record["loss"] is not None:
            return float(record["loss"])
    return None


def parse_args(argv=None):
    """CLI (optional) – ueberschreibt die ENV-Werte. Alle Argumente sind optional."""
    ap = argparse.ArgumentParser(description="M1b Slow Consolidation (Theta -> Theta').")
    ap.add_argument(
        "--source",
        choices=["zsre", "local", "capybara"],
        default=None,
        help="Datenquelle (ueberschreibt SFT_SOURCE).",
    )
    ap.add_argument(
        "--dataset",
        default=None,
        help="Pfad zur Chat-JSONL (setzt SFT_DATASET_PATH; fuer --source local).",
    )
    ap.add_argument("--out", default=None, help="Ausgabeordner (setzt OUTPUT_DIR).")
    ap.add_argument("--epochs", type=float, default=None, help="Ueberschreibt NUM_EPOCHS.")
    ap.add_argument("--gpu", default=None, help="Setzt CUDA_VISIBLE_DEVICES (z.B. 0).")
    return ap.parse_args(argv)


def main(argv=None):
    global SFT_SOURCE, NUM_EPOCHS, OUTPUT_DIR, ADAPTER_DIR, OUTPUT_JSON
    args = parse_args(argv)
    if args.gpu is not None:
        os.environ["CUDA_VISIBLE_DEVICES"] = str(args.gpu)
    if args.source:
        SFT_SOURCE = args.source.strip().lower()
    if args.dataset:
        os.environ["SFT_DATASET_PATH"] = args.dataset
    if args.out:
        OUTPUT_DIR = args.out
        ADAPTER_DIR = os.path.join(OUTPUT_DIR, "adapter")
        OUTPUT_JSON = os.path.join(OUTPUT_DIR, "kaggle_output.json")
    if args.epochs is not None:
        NUM_EPOCHS = args.epochs

    started = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    set_seed(SEED)

    import torch
    from peft import LoraConfig
    from transformers import AutoTokenizer, BitsAndBytesConfig
    from trl import SFTConfig, SFTTrainer

    hf_token = get_hf_token()
    gpu = torch.cuda.get_device_name(0) if torch.cuda.is_available() else None
    if gpu is None:
        raise RuntimeError("Keine GPU gefunden. M1b muss auf Kaggle mit GPU laufen.")

    # bf16-Mathematik braucht Compute Capability >= 8.0 (Ampere+); Turing (T4, sm_75)
    # unterstuetzt nur *emuliertes* bf16 -> der TRL-Fused-Kernel (addmm bf16->fp32)
    # bricht sonst ab ("... only supported for CUDA devices with compute capability
    # 8.0 or higher"). Daher anhand der echten Capability waehlen (belegt:
    # PyTorch-Doku is_bf16_supported(including_emulation); CUDA-GEMM bf16->fp32 ab sm_80).
    cc_major, cc_minor = torch.cuda.get_device_capability(0)
    compute_dtype = torch.bfloat16 if cc_major >= 8 else torch.float16

    source_meta = {}
    if SFT_SOURCE == "zsre":
        dataset, row_hashes, source_meta = load_zsre_rows(ZSRE_N, ZSRE_SPLIT, ZSRE_DATASET)
        dataset_path, dataset_hash = None, None
        dataset_label = ZSRE_DATASET
    elif SFT_SOURCE == "capybara":
        dataset, row_hashes, source_meta = load_capybara_rows(CAPYBARA_N, CAPYBARA_SPLIT, CAPYBARA_DATASET)
        dataset_path, dataset_hash = None, None
        dataset_label = CAPYBARA_DATASET
    elif SFT_SOURCE == "local":
        dataset_path = find_dataset()
        dataset_hash = sha256_file(dataset_path)
        dataset, row_hashes = load_dataset_rows(dataset_path)
        dataset_label = DATASET_NAME
        source_meta = {"dataset": DATASET_NAME, "split": None, "requested": None, "rows_scanned": len(dataset)}
    else:
        raise ValueError(f"Unbekannter SFT_SOURCE={SFT_SOURCE!r}. Erlaubt: zsre | local | capybara.")
    source_note = SOURCE_NOTES.get(SFT_SOURCE, "unbekannt")
    row_hash_aggregate = hashlib.sha256("\n".join(row_hashes).encode("utf-8")).hexdigest() if row_hashes else None

    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL, token=hf_token)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    # Offizielles QLoRA-Muster (TRL/PEFT): das Modell wird VOM TRAINER geladen.
    # `model_init_kwargs={"dtype": compute_dtype}` setzt die Ladepraezision (T4 -> fp16).
    # WICHTIG: Mixed Precision (AMP) bleibt KOMPLETT AUS (fp16=False, bf16=False):
    # TRL zwingt bei 4-Bit-Modellen alle trainierbaren Parameter nach bf16
    # (TRL v1.14.2 sft_trainer.py L1162-1169), und fp16=True erzeugt einen
    # GradScaler (transformers v5.19.0 training_args.py L1581-1586 ->
    # accelerate v1.15.0 accelerator.py L563-584) -> unscale_ auf bf16-Grads ->
    # NotImplementedError "_amp_foreach_non_finite_check_and_unscale_cuda ...
    # 'BFloat16'". Ohne AMP existiert kein GradScaler -> unscale_ entfaellt.
    # Gemischte Praezision (fp16-Base + bf16-Adapter) ist im Forward abgedeckt
    # (PEFT v0.21.2 lora/layer.py L1100-1113: Cast auf Adapter-Dtype + zurueck).
    # Quellen:
    #  https://github.com/huggingface/trl/blob/v1.14.2/trl/trainer/sft_trainer.py#L1162-L1169
    #  https://github.com/huggingface/transformers/blob/v5.19.0/src/transformers/training_args.py#L1581-L1586
    #  https://github.com/huggingface/accelerate/blob/v1.15.0/src/accelerate/accelerator.py#L563-L584
    #  https://github.com/huggingface/peft/blob/v0.21.2/src/peft/tuners/lora/layer.py#L1100-L1113
    #  https://huggingface.co/docs/peft/main/en/developer_guides/quantization
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_use_double_quant=True,
        bnb_4bit_compute_dtype=compute_dtype,
    )
    model_init_kwargs = {"dtype": compute_dtype}
    if hf_token:
        model_init_kwargs["token"] = hf_token

    lora_config = LoraConfig(
        r=LORA_R,
        lora_alpha=LORA_ALPHA,
        lora_dropout=LORA_DROPOUT,
        bias="none",
        task_type="CAUSAL_LM",
        target_modules="all-linear",  # QLoRA-Stil (PEFT-Doku)
    )

    sft_args = SFTConfig(
        output_dir=ADAPTER_DIR,
        num_train_epochs=NUM_EPOCHS,
        per_device_train_batch_size=PER_DEVICE_BATCH,
        gradient_accumulation_steps=GRAD_ACCUM,
        gradient_checkpointing=True,
        learning_rate=LEARNING_RATE,
        logging_steps=10,
        save_strategy="epoch",
        max_length=MAX_LENGTH,
        packing=False,
        model_init_kwargs=model_init_kwargs,
        # AMP komplett aus (Details siehe Kommentar oben): weder fp16 noch bf16,
        # damit kein GradScaler existiert und `unscale_` bf16-Grads nie trifft.
        fp16=False,
        bf16=False,
        optim="paged_adamw_8bit",
        seed=SEED,
        data_seed=SEED,
        report_to="none",
    )

    trainer = SFTTrainer(
        model=BASE_MODEL,
        args=sft_args,
        train_dataset=dataset,
        peft_config=lora_config,
        quantization_config=bnb_config,
        processing_class=tokenizer,
    )

    train_result = trainer.train()
    trainer.save_model(ADAPTER_DIR)
    tokenizer.save_pretrained(ADAPTER_DIR)

    loss = final_train_loss(trainer)
    if loss is None and hasattr(train_result, "training_loss"):
        loss = float(train_result.training_loss)

    output = {
        "status": "Auftrag/unverifiziert-lokal",
        "note": "Erzeugt auf Kaggle GPU. Adapter muss vom Menschen zurueckgegeben werden.",
        "base_model": BASE_MODEL,
        "adapter_path": os.path.abspath(ADAPTER_DIR),
        "output_json": os.path.abspath(OUTPUT_JSON),
        "loss": loss,
        "sft_source": SFT_SOURCE,
        "source_note": source_note,
        "dataset": dataset_label,
        "dataset_path": dataset_path,
        "dataset_hash_sha256": dataset_hash,
        "dataset_split": source_meta.get("split"),
        "dataset_requested": source_meta.get("requested"),
        "dataset_rows_scanned": source_meta.get("rows_scanned"),
        "dataset_skipped_empty": source_meta.get("skipped_empty"),
        "dataset_row_hash_count": len(row_hashes),
        "dataset_row_hash_aggregate_sha256": row_hash_aggregate,
        "dataset_rows": len(dataset),
        "seed": SEED,
        "num_train_epochs": NUM_EPOCHS,
        "max_length": MAX_LENGTH,
        "learning_rate": LEARNING_RATE,
        "lora_r": LORA_R,
        "lora_alpha": LORA_ALPHA,
        "compute_dtype": str(compute_dtype).replace("torch.", ""),
        "amp": "disabled (fp16=False, bf16=False)",
        "compute_capability": f"sm_{cc_major}{cc_minor}",
        "model_init_dtype": str(compute_dtype).replace("torch.", ""),
        "gpu": gpu,
        "started_utc": started,
        "finished_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "library_versions": library_versions(),
        "python": platform.python_version(),
        "source": "AGENTS.md §10.3 · arXiv:2608.22215 §3.4",
    }
    with open(OUTPUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(output, fh, indent=2, ensure_ascii=False)

    print(json.dumps(output, indent=2, ensure_ascii=False))
    return output


if __name__ == "__main__":
    main()
