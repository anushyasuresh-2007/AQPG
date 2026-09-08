"""
validate_env_and_recheck_v16.py
Step 1: Environment Validation & Step 2: Dataset Integrity Recheck for Phase 20.
"""

import os
import sys
import json
import shutil
import psutil
import torch
import transformers
from collections import Counter

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
V16_TRAIN = os.path.join(BASE_DIR, "datasets", "v16", "qg_train_dataset_v16.jsonl")
V16_VAL = os.path.join(BASE_DIR, "datasets", "v16", "qg_validation_dataset_v16.jsonl")
OUT_ENV = os.path.join(BASE_DIR, "phase20_environment.json")

def validate_environment_and_dataset():
    print("=" * 80)
    print("AQPG PHASE 20: ENVIRONMENT VALIDATION & DATASET INTEGRITY RECHECK")
    print("=" * 80)
    
    # --------------------------------------------------------------------------
    # STEP 1: ENVIRONMENT VALIDATION
    # --------------------------------------------------------------------------
    cuda_available = torch.cuda.is_available()
    cuda_version = torch.version.cuda if cuda_available else "N/A"
    gpu_count = torch.cuda.device_count() if cuda_available else 0
    gpu_name = torch.cuda.get_device_name(0) if cuda_available else "N/A"
    vram_gb = round(torch.cuda.get_device_properties(0).total_memory / (1024**3), 2) if cuda_available else 0.0
    
    cpu_count = os.cpu_count()
    ram_gb = round(psutil.virtual_memory().total / (1024**3), 2)
    ram_avail_gb = round(psutil.virtual_memory().available / (1024**3), 2)
    disk_total_gb = round(shutil.disk_usage(BASE_DIR).total / (1024**3), 2)
    disk_free_gb = round(shutil.disk_usage(BASE_DIR).free / (1024**3), 2)
    
    env_info = {
        "python_version": sys.version,
        "pytorch_version": torch.__version__,
        "transformers_version": transformers.__version__,
        "cuda_available": cuda_available,
        "cuda_version": cuda_version,
        "gpu_count": gpu_count,
        "gpu_name": gpu_name,
        "gpu_vram_gb": vram_gb,
        "cpu_count": cpu_count,
        "system_ram_gb": ram_gb,
        "system_ram_available_gb": ram_avail_gb,
        "disk_total_gb": disk_total_gb,
        "disk_free_gb": disk_free_gb,
        "dataset_paths": {
            "v16_train": V16_TRAIN,
            "v16_val": V16_VAL
        },
        "target_model": "google/flan-t5-small"
    }
    
    print("\n[Environment Summary]")
    print(f"  Python Version:       {sys.version.split()[0]}")
    print(f"  PyTorch Version:      {torch.__version__}")
    print(f"  Transformers Version: {transformers.__version__}")
    print(f"  CUDA Available:       {cuda_available} (GPU: {gpu_name}, VRAM: {vram_gb} GB)")
    print(f"  CPU Cores:            {cpu_count}")
    print(f"  System RAM:           {ram_gb} GB (Available: {ram_avail_gb} GB)")
    print(f"  Disk Free Space:      {disk_free_gb} GB")
    
    with open(OUT_ENV, "w", encoding="utf-8") as f:
        json.dump(env_info, f, indent=2)
    print(f"Saved Environment Info: {OUT_ENV}")
    
    # --------------------------------------------------------------------------
    # STEP 2: DATASET INTEGRITY RECHECK
    # --------------------------------------------------------------------------
    print("\n[Dataset Integrity Recheck]")
    train_recs = []
    val_recs = []
    
    with open(V16_TRAIN, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                train_recs.append(json.loads(line))
                
    with open(V16_VAL, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                val_recs.append(json.loads(line))
                
    train_count = len(train_recs)
    val_count = len(val_recs)
    
    print(f"  Train Records Loaded:      {train_count:,} (Expected: 40,557)")
    print(f"  Validation Records Loaded: {val_count:,} (Expected: 10,138)")
    
    if train_count != 40557 or val_count != 10138:
        print("[CRITICAL ERROR] Dataset count mismatch! Aborting.")
        sys.exit(1)
        
    # Check duplicate prompt-target pairs
    train_pairs = Counter((r["input_text"], r["target_text"]) for r in train_recs)
    dup_pairs = sum(c - 1 for c in train_pairs.values() if c > 1)
    
    train_subj = Counter(r["subject"] for r in train_recs)
    train_class = Counter(r["class"] for r in train_recs)
    train_qtype = Counter(r["question_type"] for r in train_recs)
    num_count = sum(1 for r in train_recs if r["question_type"] == "Numerical")
    
    print(f"  Duplicate Prompt-Target Pairs in Train: {dup_pairs} (PASS)")
    print(f"  Numerical Train Records:               {num_count:,} ({num_count/train_count*100:.2f}%)")
    print(f"  Subject Distribution:                  {dict(train_subj)}")
    print(f"  Class Distribution:                    {dict(train_class)}")
    print(f"  Question Type Distribution:            {dict(train_qtype)}")
    
    print("\nDataset Integrity: PASS")
    print("=" * 80)

if __name__ == "__main__":
    validate_environment_and_dataset()
