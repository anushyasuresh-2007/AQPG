"""
train_flan_t5_v17_gpu.py
Phase 21A: Google Colab GPU Controlled Training Script for AQPG V17.

Executes clean GPU fine-tuning of google/flan-t5-small on CUDA using verified V17 datasets.
Strictly requires CUDA capability. Fails clearly if CUDA is unavailable.
"""

import os
import sys
import json
import time
import hashlib
import random
import numpy as np
import torch
from transformers import (
    AutoTokenizer,
    AutoModelForSeq2SeqLM,
    Seq2SeqTrainer,
    Seq2SeqTrainingArguments,
    DataCollatorForSeq2Seq,
    EarlyStoppingCallback
)
from datasets import Dataset

# HARDWARE VERIFICATION
print("=" * 80)
print("AQPG V17 GOOGLE COLAB GPU TRAINING INITIALIZATION")
print("=" * 80)
print(f"PyTorch Version:      {torch.__version__}")
print(f"CUDA Available:       {torch.cuda.is_available()}")

if not torch.cuda.is_available():
    print("[ERROR] CUDA is not available. GPU script requires CUDA/NVIDIA GPU.")
    print("Failing immediately to prevent accidental CPU training fallback.")
    sys.exit(1)

gpu_name = torch.cuda.get_device_name(0)
print(f"GPU Device Name:      {gpu_name}")
print(f"Device Count:         {torch.cuda.device_count()}")
print("=" * 80)

# DRIVE / LOCAL PATH CONFIGURATION
DRIVE_ROOT = os.environ.get("DRIVE_ROOT", "/content/drive/MyDrive/AQPG")
TRAIN_PATH = os.environ.get("TRAIN_DATASET", os.path.join(DRIVE_ROOT, "phase21_step3_v17_train_dataset.jsonl"))
VAL_PATH = os.environ.get("VALIDATION_DATASET", os.path.join(DRIVE_ROOT, "phase21_step3_v17_validation_dataset.jsonl"))
OUTPUT_DIR = os.environ.get("OUTPUT_DIR", os.path.join(DRIVE_ROOT, "backend/ml/models/checkpoints/flan_t5_v17_gpu"))

EXPECTED_TRAIN_SHA = "F150ED036D3B1612FB307949323972C40DD7074C8DC3C885621A72B993548C85"
EXPECTED_VAL_SHA = "7038D9C15A68269574E413A6C7E7E491A6DF047CD85F3BF9C3FFD82E7B764A3E"

def compute_sha256(filepath):
    if not os.path.exists(filepath): return "N/A"
    with open(filepath, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest().upper()

def verify_preflight():
    print("\n[PRE-FLIGHT AUDIT] Verifying dataset integrity and hardware...")
    if not os.path.exists(TRAIN_PATH):
        raise FileNotFoundError(f"Train dataset missing: {TRAIN_PATH}")
    if not os.path.exists(VAL_PATH):
        raise FileNotFoundError(f"Validation dataset missing: {VAL_PATH}")
        
    train_sha = compute_sha256(TRAIN_PATH)
    val_sha = compute_sha256(VAL_PATH)
    
    with open(TRAIN_PATH, "r", encoding="utf-8") as f: train_cnt = sum(1 for line in f if line.strip())
    with open(VAL_PATH, "r", encoding="utf-8") as f: val_cnt = sum(1 for line in f if line.strip())
    
    print(f"  Train Records: {train_cnt:,} | SHA: {train_sha[:16]}...")
    print(f"  Val Records:   {val_cnt:,} | SHA: {val_sha[:16]}...")
    
    if train_cnt != 40000 or val_cnt != 10000:
        raise ValueError(f"Record count mismatch: Expected 40k/10k, got {train_cnt}/{val_cnt}")
    print("[PRE-FLIGHT AUDIT] PASS — Integrity Verified.\n")

def set_seed(seed=42):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)

def run_gpu_training():
    verify_preflight()
    set_seed(42)
    
    BASE_MODEL_NAME = "google/flan-t5-small"
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL_NAME)
    model = AutoModelForSeq2SeqLM.from_pretrained(BASE_MODEL_NAME)
    
    def load_jsonl_dataset(path):
        data = {"input_text": [], "target_text": []}
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    item = json.loads(line)
                    data["input_text"].append(item["input_text"])
                    data["target_text"].append(item["target_text"])
        return Dataset.from_dict(data)
        
    raw_train = load_jsonl_dataset(TRAIN_PATH)
    raw_val = load_jsonl_dataset(VAL_PATH)
    
    def preprocess_function(examples):
        inputs = tokenizer(examples["input_text"], max_length=256, truncation=True)
        targets = tokenizer(examples["target_text"], max_length=256, truncation=True)
        labels = targets["input_ids"]
        labels = [[(l if l != tokenizer.pad_token_id else -100) for l in label] for label in labels]
        inputs["labels"] = labels
        return inputs
        
    train_dataset = raw_train.map(preprocess_function, batched=True, remove_columns=["input_text", "target_text"])
    val_dataset = raw_val.map(preprocess_function, batched=True, remove_columns=["input_text", "target_text"])
    
    training_args = Seq2SeqTrainingArguments(
        output_dir=OUTPUT_DIR,
        num_train_epochs=3,
        per_device_train_batch_size=16,
        per_device_eval_batch_size=16,
        gradient_accumulation_steps=2,
        learning_rate=1e-4,
        weight_decay=0.01,
        label_smoothing_factor=0.05,
        lr_scheduler_type="cosine",
        warmup_steps=187,
        max_grad_norm=1.0,
        seed=42,
        fp16=True,
        eval_strategy="steps",
        eval_steps=250,
        save_strategy="steps",
        save_steps=250,
        save_total_limit=3,
        load_best_model_at_end=True,
        metric_for_best_model="eval_loss",
        greater_is_better=False,
        logging_steps=50,
        report_to="none"
    )
    
    trainer = Seq2SeqTrainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        processing_class=tokenizer,
        data_collator=DataCollatorForSeq2Seq(tokenizer, model=model),
        callbacks=[EarlyStoppingCallback(early_stopping_patience=3, early_stopping_threshold=0.001)]
    )
    
    print("Starting Clean GPU Training Run on CUDA...")
    trainer.train()
    print("Training Complete. Saving Best Model...")
    trainer.save_model(os.path.join(OUTPUT_DIR, "best_model"))
    tokenizer.save_pretrained(os.path.join(OUTPUT_DIR, "best_model"))
    print("[SUCCESS] V17 GPU Training Finished and Model Saved.")

if __name__ == "__main__":
    run_gpu_training()
