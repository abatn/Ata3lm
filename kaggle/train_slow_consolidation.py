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

Aufruf (Kaggle):
    !python train_slow_consolidation.py
    bzw. Umgebungsvariablen setzen: SFT_SOURCE, BASE_MODEL, SFT_DATASET_PATH,
    OUTPUT_DIR, NUM_EPOCHS, MAX_LENGTH, SEED, HF_TOKEN, ZSRE_N, ZSRE_SPLIT,
    CAPYBARA_N, CAPYBARA_SPLIT.
"""

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
    `(question, answers[0])`. Zeilen ohne nicht-leere Antwort werden uebersprungen
    (reale Daten - es wird nichts erfunden).
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


def pick_target_modules(model):
    candidates = [
        "q_proj",
        "k_proj",
        "v_proj",
        "o_proj",
        "gate_proj",
        "up_proj",
        "down_proj",
    ]
    present = set()
    for name, _module in model.named_modules():
        present.add(name.split(".")[-1])
    selected = [c for c in candidates if c in present]
    return selected or ["q_proj", "v_proj"]


def final_train_loss(trainer):
    for record in reversed(trainer.state.log_history):
        if "loss" in record and record["loss"] is not None:
            return float(record["loss"])
    return None


def main():
    started = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    set_seed(SEED)

    import torch
    from peft import LoraConfig, prepare_model_for_kbit_training
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
    from trl import SFTConfig, SFTTrainer

    hf_token = get_hf_token()
    gpu = torch.cuda.get_device_name(0) if torch.cuda.is_available() else None
    if gpu is None:
        raise RuntimeError("Keine GPU gefunden. M1b muss auf Kaggle mit GPU laufen.")

    compute_dtype = torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16

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

    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=compute_dtype,
        bnb_4bit_use_double_quant=True,
    )
    model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL,
        quantization_config=bnb_config,
        device_map="auto",
        token=hf_token,
    )
    model.config.use_cache = False
    model = prepare_model_for_kbit_training(model, use_gradient_checkpointing=True)

    lora_config = LoraConfig(
        r=LORA_R,
        lora_alpha=LORA_ALPHA,
        lora_dropout=LORA_DROPOUT,
        bias="none",
        task_type="CAUSAL_LM",
        target_modules=pick_target_modules(model),
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
        bf16=(compute_dtype == torch.bfloat16),
        fp16=(compute_dtype == torch.float16),
        optim="paged_adamw_8bit",
        seed=SEED,
        data_seed=SEED,
        report_to="none",
    )

    trainer = SFTTrainer(
        model=model,
        args=sft_args,
        train_dataset=dataset,
        peft_config=lora_config,
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
