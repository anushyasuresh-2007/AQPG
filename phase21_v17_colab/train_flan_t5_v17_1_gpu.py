"""
train_flan_t5_v17_1_gpu.py
AQPG V17.1: Google Colab GPU Numerical Stability & Smoke Test Training Script.

Executes clean GPU 100-step smoke test of google/flan-t5-small on CUDA using verified V17 datasets.
Applies numerical stability fixes:
- fp16 = False (FP32 precision)
- bf16 = False
- learning_rate = 5e-5
- label_smoothing_factor = 0.0
- weight_decay = 0.01
- max_grad_norm = 1.0
- warmup_steps = 187
- max_steps = 100

Strictly requires CUDA capability. Fails immediately if CUDA is unavailable.
"""

import os
import sys
import json
import time
import math
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
    EarlyStoppingCallback,
    TrainerCallback
)
from datasets import Dataset

# HARDWARE VERIFICATION
print("=" * 80)
print("AQPG V17.1 GOOGLE COLAB GPU NUMERICAL STABILITY SMOKE TEST INITIALIZATION")
print("=" * 80)
print(f"PyTorch Version:      {torch.__version__}")
print(f"CUDA Available:       {torch.cuda.is_available()}")

if not torch.cuda.is_available():
    print("[ERROR] CUDA is not available. V17.1 GPU training script requires CUDA/NVIDIA GPU.")
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
OUTPUT_DIR = os.environ.get("OUTPUT_DIR", os.path.join(DRIVE_ROOT, "backend/ml/models/checkpoints/flan_t5_v17_1_gpu_smoketest"))

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
    if train_sha != EXPECTED_TRAIN_SHA or val_sha != EXPECTED_VAL_SHA:
        raise ValueError("Dataset SHA-256 hash mismatch! Read-only dataset policy violated.")
    print("[PRE-FLIGHT AUDIT] PASS — Dataset Hashes and Record Counts Verified.\n")

def set_seed(seed=42):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)

class NumericalStabilityCallback(TrainerCallback):
    def __init__(self):
        self.has_nan_or_inf = False
        self.metrics_history = []

    def on_log(self, args, state, control, logs=None, **kwargs):
        if logs is None:
            return
        
        self.metrics_history.append({"step": state.global_step, "logs": dict(logs)})
        
        for key, val in logs.items():
            if isinstance(val, (int, float)):
                if math.isnan(val) or math.isinf(val):
                    self.has_nan_or_inf = True
                    err_msg = f"[CRITICAL NUMERICAL FAILURE] NaN/Inf detected at step {state.global_step} for metric '{key}': {val}"
                    print("\n" + "!" * 80)
                    print(err_msg)
                    print("!" * 80 + "\n")
                    raise ValueError(err_msg)

def run_v17_1_smoke_test():
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
        max_steps=100,
        per_device_train_batch_size=16,
        per_device_eval_batch_size=16,
        gradient_accumulation_steps=2,
        learning_rate=5e-5,
        weight_decay=0.01,
        label_smoothing_factor=0.0,
        lr_scheduler_type="cosine",
        warmup_steps=187,
        max_grad_norm=1.0,
        seed=42,
        fp16=False,
        bf16=False,
        eval_strategy="steps",
        eval_steps=50,
        save_strategy="steps",
        save_steps=50,
        save_total_limit=2,
        load_best_model_at_end=True,
        metric_for_best_model="eval_loss",
        greater_is_better=False,
        logging_steps=10,
        report_to="none"
    )
    
    stability_callback = NumericalStabilityCallback()
    
    trainer = Seq2SeqTrainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        processing_class=tokenizer,
        data_collator=DataCollatorForSeq2Seq(tokenizer, model=model),
        callbacks=[stability_callback, EarlyStoppingCallback(early_stopping_patience=3, early_stopping_threshold=0.001)]
    )
    
    print("Starting V17.1 Clean GPU Numerical Stability Smoke Test (100 Steps)...")
    start_time = time.time()
    train_result = trainer.train()
    end_time = time.time()
    
    print("Smoke Test Steps Complete. Evaluating Final Metrics...")
    eval_metrics = trainer.evaluate()
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    trainer.save_model(os.path.join(OUTPUT_DIR, "best_model"))
    tokenizer.save_pretrained(os.path.join(OUTPUT_DIR, "best_model"))
    
    final_train_loss = float(train_result.training_loss) if train_result.training_loss is not None else "N/A"
    final_eval_loss = float(eval_metrics.get("eval_loss", -1.0))
    
    # Extract last recorded grad_norm if present
    last_grad_norm = "N/A"
    for log_item in reversed(stability_callback.metrics_history):
        if "grad_norm" in log_item.get("logs", {}):
            last_grad_norm = log_item["logs"]["grad_norm"]
            break

    is_pass = (
        not stability_callback.has_nan_or_inf and
        final_eval_loss > 0 and
        not math.isnan(final_eval_loss) and
        not math.isinf(final_eval_loss)
    )

    report_data = {
        "title": "AQPG V17.1 GPU Numerical Stability Smoke Test Report",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "status": "PASS" if is_pass else "FAIL",
        "environment": {
            "gpu_name": gpu_name,
            "cuda_version": torch.version.cuda,
            "pytorch_version": torch.__version__,
            "cuda_available": True
        },
        "dataset_integrity": {
            "train_records": 40000,
            "validation_records": 10000,
            "train_sha256": EXPECTED_TRAIN_SHA,
            "validation_sha256": EXPECTED_VAL_SHA
        },
        "model_and_hyperparameters": {
            "base_model": BASE_MODEL_NAME,
            "fp16": False,
            "bf16": False,
            "learning_rate": 5e-5,
            "label_smoothing_factor": 0.0,
            "weight_decay": 0.01,
            "max_grad_norm": 1.0,
            "warmup_steps": 187,
            "effective_batch_size": 32,
            "max_steps": 100
        },
        "results": {
            "requested_steps": 100,
            "completed_steps": int(train_result.global_step),
            "final_train_loss": final_train_loss,
            "final_eval_loss": final_eval_loss,
            "final_grad_norm": last_grad_norm,
            "nan_detected": stability_callback.has_nan_or_inf,
            "inf_detected": stability_callback.has_nan_or_inf,
            "cpu_fallback": False,
            "duration_seconds": round(end_time - start_time, 2)
        },
        "decision": "PASS — READY FOR FULL V17.1 GPU TRAINING" if is_pass else "FAIL — DO NOT START FULL TRAINING",
        "safety_boundaries": {
            "approved_for_fastapi": False,
            "fastapi_integration_status": "BLOCKED"
        }
    }
    
    # Save json report
    report_json_path = os.path.join(DRIVE_ROOT, "phase21_v17_1_smoke_test_report.json")
    with open(report_json_path, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2)
        
    print(f"\n[REPORT GENERATED] {report_json_path}")
    print("=" * 60)
    print("AQPG V17.1 GPU NUMERICAL STABILITY SMOKE TEST")
    print("=" * 60)
    print(f"GPU:            {gpu_name}")
    print(f"CUDA:           {torch.version.cuda}")
    print(f"PyTorch:        {torch.__version__}")
    print(f"Dataset Train:  40,000 | Val: 10,000")
    print(f"Steps req:      100 | Steps completed: {train_result.global_step}")
    print(f"Final loss:     {final_train_loss}")
    print(f"Final eval_loss: {final_eval_loss}")
    print(f"Final grad_norm: {last_grad_norm}")
    print(f"NaN detected:   {'YES' if stability_callback.has_nan_or_inf else 'NO'}")
    print(f"Inf detected:   {'YES' if stability_callback.has_nan_or_inf else 'NO'}")
    print(f"CPU fallback:   NO")
    print(f"RESULT:         {report_data['decision']}")
    print("=" * 60)

if __name__ == "__main__":
    run_v17_1_smoke_test()
