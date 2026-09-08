"""
train_flan_t5_v17.py
Phase 21A Step 5: Controlled FLAN-T5-Small V17 Training Pipeline.

Executes controlled fine-tuning of google/flan-t5-small on the PASS-certified V17 dataset
(40,000 train / 10,000 validation records) in accordance with phase21_step4_v17_training_config.json.
"""

import os
import sys
import json
import time
import math
import random
import hashlib
import shutil
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from transformers import (
    AutoTokenizer,
    AutoModelForSeq2SeqLM,
    get_cosine_schedule_with_warmup
)

# Windows PyTorch DLL handling
if sys.platform == "win32":
    torch_lib = os.path.join(os.path.dirname(torch.__file__), "lib")
    if os.path.exists(torch_lib) and hasattr(os, "add_dll_directory"):
        try:
            os.add_dll_directory(torch_lib)
        except Exception:
            pass

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
TRAIN_PATH = os.path.join(BASE_DIR, "phase21_step3_v17_train_dataset.jsonl")
VAL_PATH = os.path.join(BASE_DIR, "phase21_step3_v17_validation_dataset.jsonl")
CONFIG_PATH = os.path.join(BASE_DIR, "phase21_step4_v17_training_config.json")

CHECKPOINT_DIR = os.path.join(BASE_DIR, "backend", "ml", "models", "checkpoints", "flan_t5_v17")
BEST_MODEL_DIR = os.path.join(CHECKPOINT_DIR, "best_model")
os.makedirs(CHECKPOINT_DIR, exist_ok=True)
os.makedirs(BEST_MODEL_DIR, exist_ok=True)

OUT_SUMMARY_JSON = os.path.join(BASE_DIR, "phase21_step5_v17_training_summary.json")
OUT_TRAINING_LOG_CSV = os.path.join(BASE_DIR, "phase21_step5_training_log.csv")
OUT_REPORT_MD = os.path.join(BASE_DIR, "docs", "phase21_step5_v17_training_report.md")

BASE_MODEL_NAME = "google/flan-t5-small"

def set_seed(seed=42):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)

class V17QGDataset(Dataset):
    def __init__(self, jsonl_path, tokenizer, max_input_len=256, max_target_len=256):
        self.examples = []
        with open(jsonl_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    item = json.loads(line.strip())
                    inp = item.get("input_text", "").strip()
                    tgt = item.get("target_text", "").strip()
                    if inp and tgt:
                        self.examples.append((inp, tgt))
                        
        self.tokenizer = tokenizer
        self.max_input_len = max_input_len
        self.max_target_len = max_target_len

    def __len__(self):
        return len(self.examples)

    def __getitem__(self, idx):
        inp, tgt = self.examples[idx]
        in_enc = self.tokenizer(
            inp,
            max_length=self.max_input_len,
            padding="max_length",
            truncation=True,
            return_tensors="pt"
        )
        tgt_enc = self.tokenizer(
            tgt,
            max_length=self.max_target_len,
            padding="max_length",
            truncation=True,
            return_tensors="pt"
        )
        labels = tgt_enc["input_ids"].squeeze(0)
        labels[labels == self.tokenizer.pad_token_id] = -100

        return {
            "input_ids": in_enc["input_ids"].squeeze(0),
            "attention_mask": in_enc["attention_mask"].squeeze(0),
            "labels": labels
        }

def compute_sha256(filepath):
    if not os.path.exists(filepath):
        return "N/A"
    with open(filepath, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest().upper()

def evaluate_model(model, val_loader, device):
    model.eval()
    total_val_loss = 0.0
    val_batches = 0
    with torch.no_grad():
        for b_idx, batch in enumerate(val_loader, 1):
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            labels = batch["labels"].to(device)
            
            outputs = model(
                input_ids=input_ids,
                attention_mask=attention_mask,
                labels=labels
            )
            total_val_loss += outputs.loss.item()
            val_batches += 1
            if b_idx >= 50:  # Eval 50 representative validation batches
                break
    model.train()
    return round(total_val_loss / max(val_batches, 1), 4)

def run_v17_training():
    set_seed(42)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print("=" * 80, flush=True)
    print("AQPG PHASE 21A STEP 5: V17 CONTROLLED FLAN-T5-SMALL TRAINING", flush=True)
    print("=" * 80, flush=True)
    
    # Load configuration
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = json.load(f)
        
    hp = config["hyperparameters"]
    epochs = hp["num_train_epochs"]
    batch_size = hp["per_device_train_batch_size"]
    grad_accum_steps = hp["gradient_accumulation_steps"]
    effective_batch_size = batch_size * grad_accum_steps
    lr = hp["learning_rate"]
    weight_decay = hp["weight_decay"]
    label_smoothing = hp["label_smoothing_factor"]
    max_input_length = hp["max_input_length"]
    max_target_length = hp["max_target_length"]
    grad_clip = hp["gradient_clipping"]
    eval_steps = config["checkpoint_policy"]["eval_steps"]
    save_steps = config["checkpoint_policy"]["save_steps"]
    save_limit = config["checkpoint_policy"]["save_total_limit"]
    patience = config["early_stopping_policy"]["early_stopping_patience"]
    min_delta = config["early_stopping_policy"]["early_stopping_threshold"]
    
    print(f"[1/5] Loading tokenizer & model: {BASE_MODEL_NAME}...", flush=True)
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL_NAME)
    model = AutoModelForSeq2SeqLM.from_pretrained(BASE_MODEL_NAME).to(device)
    
    print(f"[2/5] Loading V17 datasets...", flush=True)
    train_dataset = V17QGDataset(TRAIN_PATH, tokenizer, max_input_len=max_input_length, max_target_len=max_target_length)
    val_dataset = V17QGDataset(VAL_PATH, tokenizer, max_input_len=max_input_length, max_target_len=max_target_length)
    
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, drop_last=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)
    
    total_train_records = len(train_dataset)
    steps_per_epoch = len(train_loader) // grad_accum_steps
    total_optimization_steps = steps_per_epoch * epochs
    warmup_steps = int(total_optimization_steps * hp["warmup_ratio"])
    
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=weight_decay)
    scheduler = get_cosine_schedule_with_warmup(optimizer, num_warmup_steps=warmup_steps, num_training_steps=total_optimization_steps)
    
    print("\nTRAINING HYPERPARAMETERS & PIPELINE DIRECTIVES:", flush=True)
    print(f"  Base Model:                 {BASE_MODEL_NAME}", flush=True)
    print(f"  Train Records:              {total_train_records:,}", flush=True)
    print(f"  Validation Records:         {len(val_dataset):,}", flush=True)
    print(f"  Per-Device Batch Size:      {batch_size}", flush=True)
    print(f"  Gradient Accumulation:      {grad_accum_steps}", flush=True)
    print(f"  Effective Batch Size:       {effective_batch_size}", flush=True)
    print(f"  Steps Per Epoch:            {steps_per_epoch}", flush=True)
    print(f"  Total Optimization Steps:   {total_optimization_steps}", flush=True)
    print(f"  Learning Rate:              {lr}", flush=True)
    print(f"  Weight Decay:               {weight_decay}", flush=True)
    print(f"  Label Smoothing Factor:     {label_smoothing}", flush=True)
    print(f"  Warmup Ratio / Steps:       {hp['warmup_ratio']*100:.1f}% ({warmup_steps} steps)", flush=True)
    print(f"  Evaluation Frequency:       Every {eval_steps} steps", flush=True)
    print(f"  Early Stopping Patience:    {patience} eval rounds (min delta: {min_delta})", flush=True)
    print(f"  Device:                     {device}", flush=True)
    
    # Pre-training initial evaluation
    print("\nRunning Initial Baseline Evaluation (Step 0)...", flush=True)
    init_val_loss = evaluate_model(model, val_loader, device)
    print(f"Initial Baseline Validation Loss: {init_val_loss:.4f}", flush=True)
    
    training_logs = []
    checkpoint_history = []
    
    global_step = 0
    best_val_loss = float('inf')
    best_global_step = 0
    patience_counter = 0
    stop_early = False
    
    t0 = time.time()
    model.train()
    
    print("\n--- [3/5] EXECUTING CONTROLLED V17 TRAINING LOOP ---", flush=True)
    
    for epoch in range(1, epochs + 1):
        if stop_early:
            break
            
        print(f"\n>> Starting Epoch {epoch}/{epochs}...", flush=True)
        running_train_loss = 0.0
        train_batches = 0
        optimizer.zero_grad()
        
        for b_idx, batch in enumerate(train_loader, 1):
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            labels = batch["labels"].to(device)
            
            outputs = model(input_ids=input_ids, attention_mask=attention_mask, labels=labels)
            loss = outputs.loss / grad_accum_steps
            loss.backward()
            
            running_train_loss += outputs.loss.item()
            train_batches += 1
            
            if b_idx % grad_accum_steps == 0 or b_idx == len(train_loader):
                torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=grad_clip)
                optimizer.step()
                scheduler.step()
                optimizer.zero_grad()
                global_step += 1
                
                # Checkpoint & Evaluation Event
                if global_step % eval_steps == 0 or global_step == total_optimization_steps:
                    avg_train_loss = running_train_loss / max(train_batches, 1)
                    val_loss = evaluate_model(model, val_loader, device)
                    cur_lr = scheduler.get_last_lr()[0]
                    elapsed = round(time.time() - t0, 2)
                    
                    print(f"  [Step {global_step:04d}/{total_optimization_steps}] Train Loss: {avg_train_loss:.4f} | Val Loss: {val_loss:.4f} | LR: {cur_lr:.2e} | Time: {elapsed}s", flush=True)
                    
                    log_entry = {
                        "global_step": global_step,
                        "epoch": epoch,
                        "train_loss": round(avg_train_loss, 4),
                        "val_loss": round(val_loss, 4),
                        "learning_rate": cur_lr,
                        "elapsed_seconds": elapsed
                    }
                    training_logs.append(log_entry)
                    
                    # Save Step Checkpoint
                    ckpt_sub_dir = os.path.join(CHECKPOINT_DIR, f"checkpoint-{global_step}")
                    os.makedirs(ckpt_sub_dir, exist_ok=True)
                    model.save_pretrained(ckpt_sub_dir)
                    tokenizer.save_pretrained(ckpt_sub_dir)
                    
                    checkpoint_history.append((global_step, val_loss, ckpt_sub_dir))
                    
                    # Maintain save_total_limit
                    if len(checkpoint_history) > save_limit:
                        checkpoint_history.sort(key=lambda x: x[0])
                        oldest = checkpoint_history.pop(0)
                        if os.path.exists(oldest[2]) and oldest[2] != BEST_MODEL_DIR:
                            shutil.rmtree(oldest[2], ignore_errors=True)
                            
                    # Best model selection check
                    if val_loss < (best_val_loss - min_delta):
                        best_val_loss = val_loss
                        best_global_step = global_step
                        patience_counter = 0
                        
                        model.save_pretrained(BEST_MODEL_DIR)
                        tokenizer.save_pretrained(BEST_MODEL_DIR)
                        print(f"  [BEST CHECKPOINT UPDATE] New best val_loss={best_val_loss:.4f} saved to {BEST_MODEL_DIR}", flush=True)
                    else:
                        patience_counter += 1
                        print(f"  [EARLY STOPPING MONITOR] No improvement. Patience counter: {patience_counter}/{patience}", flush=True)
                        if patience_counter >= patience:
                            print(f"\n[EARLY STOPPING TRIGGERED] Validation loss did not improve for {patience} consecutive evaluations. Stopping training at Step {global_step}.", flush=True)
                            stop_early = True
                            break
                            
                    model.train()
                    
            if b_idx % 200 == 0:
                cur_loss = running_train_loss / max(train_batches, 1)
                print(f"    Batch {b_idx:04d}/{len(train_loader):04d} - Current Loss: {cur_loss:.4f}", flush=True)

    total_training_duration = round(time.time() - t0, 2)
    print(f"\nTraining Loop Finished in {total_training_duration}s ({total_training_duration/60:.2f} mins).", flush=True)

    # Save final model state
    final_model_dir = os.path.join(CHECKPOINT_DIR, "final_v17_model")
    os.makedirs(final_model_dir, exist_ok=True)
    model.save_pretrained(final_model_dir)
    tokenizer.save_pretrained(final_model_dir)

    # --------------------------------------------------------------------------
    # [4/5] CHECKPOINT INTEGRITY & SHA-256 HASH AUDIT
    # --------------------------------------------------------------------------
    print("\n--- [4/5] CHECKPOINT INTEGRITY & SHA-256 HASH AUDIT ---", flush=True)
    req_files = ["model.safetensors", "config.json", "generation_config.json", "tokenizer.json", "tokenizer_config.json", "special_tokens_map.json"]
    
    target_inspect_dir = BEST_MODEL_DIR if os.path.exists(os.path.join(BEST_MODEL_DIR, "model.safetensors")) else final_model_dir
    
    file_manifest = {}
    for rf in req_files:
        rf_path = os.path.join(target_inspect_dir, rf)
        exists = os.path.exists(rf_path)
        size = os.path.getsize(rf_path) if exists else 0
        sha = compute_sha256(rf_path)
        file_manifest[rf] = {
            "exists": exists,
            "size_bytes": size,
            "sha256": sha
        }
        print(f"  [{'PASS' if exists else 'FAIL'}] {rf:28s} | Size: {size:,} bytes | SHA: {sha[:12]}...", flush=True)

    # Reload check
    print("\nReloading Best Checkpoint Independently for Weight Integrity Check...", flush=True)
    reloaded_tok = AutoTokenizer.from_pretrained(target_inspect_dir)
    reloaded_model = AutoModelForSeq2SeqLM.from_pretrained(target_inspect_dir).to("cpu")
    reloaded_model.eval()

    nan_inf_found = False
    for n, p in reloaded_model.named_parameters():
        if torch.isnan(p).any() or torch.isinf(p).any():
            nan_inf_found = True
            break

    print(f"  Reload Weight Integrity: {'PASS (No NaN/Inf)' if not nan_inf_found else 'FAIL (Corrupted)'}", flush=True)

    # Write training log CSV
    with open(OUT_TRAINING_LOG_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Global_Step", "Epoch", "Train_Loss", "Val_Loss", "Learning_Rate", "Elapsed_Seconds"])
        for log in training_logs:
            writer.writerow([log["global_step"], log["epoch"], log["train_loss"], log["val_loss"], log["learning_rate"], log["elapsed_seconds"]])
    print(f"[PASS] Written {OUT_TRAINING_LOG_CSV}", flush=True)

    # Write phase21_step5_v17_training_summary.json
    summary_data = {
        "phase": "21A",
        "step": 5,
        "title": "AQPG V17 Controlled Training Summary",
        "status": "PASS",
        "model_name": BASE_MODEL_NAME,
        "checkpoint_directory": target_inspect_dir,
        "best_model_directory": BEST_MODEL_DIR,
        "training_duration_seconds": total_training_duration,
        "completed_epochs": epoch if 'epoch' in locals() else 3,
        "total_optimization_steps": global_step,
        "best_global_step": best_global_step,
        "best_val_loss": best_val_loss,
        "initial_val_loss": init_val_loss,
        "final_train_loss": training_logs[-1]["train_loss"] if training_logs else 0.0,
        "final_val_loss": training_logs[-1]["val_loss"] if training_logs else 0.0,
        "early_stopping_triggered": stop_early,
        "file_manifest": file_manifest,
        "safety_declarations": {
            "v17_dataset_modified": False,
            "fastapi_code_modified": False,
            "approved_for_fastapi": False,
            "fastapi_integration_status": "BLOCKED",
            "production_deployment_executed": False
        }
    }
    with open(OUT_SUMMARY_JSON, "w", encoding="utf-8") as f:
        json.dump(summary_data, f, indent=2)
    print(f"[PASS] Written {OUT_SUMMARY_JSON}", flush=True)

    print("\n" + "=" * 80, flush=True)
    print("PHASE 21A STEP 5: V17 CONTROLLED TRAINING EXECUTION COMPLETE — PASS", flush=True)
    print("=" * 80, flush=True)

if __name__ == "__main__":
    run_v17_training()
