"""
train_flan_t5_v16.py
Step 3, 4, 5, 7, 8: Controlled FLAN-T5-Small V16 Training Pipeline.
Executes pre-training base evaluation, full multi-epoch cross-entropy training,
checkpoint saving, and integrity verification.
"""

import os
import sys
import json
import time
import math
import random
import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader
from transformers import (
    AutoTokenizer,
    AutoModelForSeq2SeqLM,
    get_linear_schedule_with_warmup
)

# Safely add PyTorch DLL directory on Windows
if sys.platform == "win32":
    torch_lib = os.path.join(os.path.dirname(torch.__file__), "lib")
    if os.path.exists(torch_lib) and hasattr(os, "add_dll_directory"):
        try:
            os.add_dll_directory(torch_lib)
        except Exception:
            pass

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
V16_TRAIN_PATH = os.path.join(BASE_DIR, "datasets", "v16", "qg_train_dataset_v16.jsonl")
V16_VAL_PATH = os.path.join(BASE_DIR, "datasets", "v16", "qg_validation_dataset_v16.jsonl")

CHECKPOINT_DIR = os.path.join(BASE_DIR, "backend", "ml", "models", "checkpoints", "flan_t5_v16_small")
os.makedirs(CHECKPOINT_DIR, exist_ok=True)

OUT_CONFIG_JSON = os.path.join(BASE_DIR, "v16_training_config.json")
OUT_TRAIN_METRICS = os.path.join(BASE_DIR, "phase20_training_metrics.json")
OUT_CHECKPOINT_VERIF = os.path.join(BASE_DIR, "phase20_checkpoint_verification.json")
OUT_EVAL_PROMPTS = os.path.join(BASE_DIR, "phase20_evaluation_prompts.jsonl")
OUT_BASE_OUTPUTS = os.path.join(BASE_DIR, "phase20_base_outputs.jsonl")

BASE_MODEL_NAME = "google/flan-t5-small"

def set_seed(seed=42):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)

def normalize_rng_state(raw_rng):
    if raw_rng is None:
        return None
    if isinstance(raw_rng, torch.Tensor):
        return raw_rng.detach().to(device="cpu", dtype=torch.uint8).contiguous()
    if isinstance(raw_rng, np.ndarray):
        return torch.from_numpy(raw_rng).to(device="cpu", dtype=torch.uint8).contiguous()
    if isinstance(raw_rng, (list, tuple)):
        return torch.tensor(raw_rng, dtype=torch.uint8, device="cpu").contiguous()
    raise TypeError(f"Unsupported RNG state type: {type(raw_rng)}")

class QGDataset(Dataset):
    def __init__(self, jsonl_path, tokenizer, max_input_len=128, max_target_len=256):
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

def build_phase20_evaluation_prompts():
    """
    Constructs 520 controlled prompts across subjects, classes, question types, and difficulties.
    """
    subjects_spec = {
        "Mathematics": [
            "Linear Equations in Two Variables", "Quadratic Equations & Roots",
            "Arithmetic Progressions & Series", "Coordinate Geometry & Distance Formula",
            "Trigonometric Ratios & Heights", "Circles & Tangents",
            "Surface Areas & Volumes of Solids", "Probability & Sample Space",
            "Statistics & Mean Median Mode", "Polynomials & Factorization"
        ],
        "Physics": [
            "Newton's Laws of Motion & Friction", "Kinematics & Equations of Motion",
            "Work, Energy and Power", "Universal Law of Gravitation & Planetary Motion",
            "Thermodynamics & Heat Engines", "Ray Optics & Refraction",
            "Wave Optics & Interference", "Current Electricity & Ohm's Law",
            "Magnetic Effects of Current & Induction", "Sound Waves & Doppler Effect"
        ],
        "Chemistry": [
            "Chemical Reactions & Balancing Equations", "Acids, Bases and Salts",
            "Periodic Classification & Atomic Radius", "Chemical Bonding & Molecular Orbital Theory",
            "Chemical Thermodynamics & Enthalpy", "Chemical Equilibrium & Le Chatelier's Principle",
            "Redox Reactions & Oxidation Numbers", "Electrochemistry & Nernst Equation",
            "Hydrocarbons & Alkanes Alkenes", "Solutions & Molarity Molality"
        ],
        "Biology": [
            "Cell Structure & Organelles", "Cell Division & Mitosis Meiosis",
            "Photosynthesis & Light Dependent Reactions", "Cellular Respiration & Krebs Cycle",
            "Mendelian Genetics & Monohybrid Cross", "Molecular Basis of Inheritance & DNA",
            "Human Circulatory System & Blood", "Human Excretory System & Kidney",
            "Ecosystems & Energy Flow", "Biotechnology & Recombinant DNA"
        ],
        "General Science": [
            "Matter in Our Surroundings & States of Matter", "Is Matter Around Us Pure & Mixtures",
            "Atoms and Molecules & Law of Conservation of Mass", "Structure of the Atom & Valence Electrons",
            "The Fundamental Unit of Life", "Tissues & Plant Animal Tissues",
            "Motion & Speed Velocity", "Force and Laws of Motion",
            "Gravitation & Free Fall", "Work, Energy and Power"
        ]
    }

    classes = ["Class 9", "Class 10", "Class 11", "Class 12"]
    types = ["Numerical", "MCQ", "Conceptual"]
    difficulties = ["Easy", "Medium", "Hard"]
    marks_map = {"Easy": 1, "Medium": 2, "Hard": 3}

    prompts = []
    pid = 1

    for subject, topics in subjects_spec.items():
        for i in range(100):
            topic = topics[i % len(topics)]
            cls = classes[i % len(classes)]
            q_type = types[i % len(types)]
            diff = difficulties[i % len(difficulties)]
            marks = 5 if (q_type == "Numerical" and diff == "Hard") else marks_map[diff]
            
            p_str = f"generate question | subject: {subject} | topic: {topic} | class: {cls} | difficulty: {diff} | marks: {marks} | type: {q_type}"
            
            prompts.append({
                "prompt_id": f"P20-{pid:04d}",
                "category": "standard_matrix",
                "subject": subject,
                "topic": topic,
                "class": cls,
                "difficulty": diff,
                "marks": marks,
                "question_type": q_type,
                "input_text": p_str
            })
            pid += 1

    # 20 Sensitivity pairs
    sensitivity_pairs = [
        {"subject": "Physics", "topic": "Gravitation & Planetary Motion", "difficulty": "Medium", "marks": 3, "question_type": "Numerical", "var": "class", "v1": "Class 9", "v2": "Class 12"},
        {"subject": "Mathematics", "topic": "Probability & Statistics", "difficulty": "Medium", "marks": 3, "question_type": "Numerical", "var": "class", "v1": "Class 9", "v2": "Class 12"},
        {"subject": "Chemistry", "topic": "Chemical Bonding", "difficulty": "Medium", "marks": 2, "question_type": "MCQ", "var": "class", "v1": "Class 10", "v2": "Class 12"},
        {"subject": "Mathematics", "topic": "Quadratic Equations & Roots", "class": "Class 10", "question_type": "Numerical", "var": "difficulty", "v1": "Easy", "v2": "Hard"},
        {"subject": "Physics", "topic": "Kinematics & Equations of Motion", "class": "Class 11", "question_type": "Numerical", "var": "difficulty", "v1": "Easy", "v2": "Hard"},
        {"subject": "Biology", "topic": "Cell Structure & Organelles", "class": "Class 11", "question_type": "MCQ", "var": "difficulty", "v1": "Easy", "v2": "Hard"},
        {"subject": "Physics", "topic": "Current Electricity & Ohm's Law", "class": "Class 10", "difficulty": "Medium", "marks": 3, "var": "question_type", "v1": "Numerical", "v2": "MCQ"},
        {"subject": "Chemistry", "topic": "Solutions & Molarity Molality", "class": "Class 11", "difficulty": "Medium", "marks": 3, "var": "question_type", "v1": "Numerical", "v2": "MCQ"},
        {"subject": "Mathematics", "topic": "Surface Areas & Volumes of Solids", "class": "Class 10", "difficulty": "Medium", "marks": 3, "var": "question_type", "v1": "Numerical", "v2": "MCQ"},
        {"topic": "Thermodynamics & Heat", "class": "Class 11", "difficulty": "Medium", "marks": 3, "question_type": "Numerical", "var": "subject", "v1": "Physics", "v2": "Chemistry"}
    ]

    for p in sensitivity_pairs:
        v_name = p["var"]
        v1, v2 = p["v1"], p["v2"]
        
        d1 = dict(p); del d1["var"]; del d1["v1"]; del d1["v2"]; d1[v_name] = v1
        if "marks" not in d1: d1["marks"] = 1 if d1.get("difficulty") == "Easy" else 5
        p1 = f"generate question | subject: {d1.get('subject')} | topic: {d1.get('topic')} | class: {d1.get('class')} | difficulty: {d1.get('difficulty')} | marks: {d1.get('marks')} | type: {d1.get('question_type')}"
        d1["prompt_id"] = f"P20-SENS-{pid:04d}-A"; d1["category"] = "sensitivity_test"; d1["sensitivity_var"] = v_name; d1["sensitivity_val"] = v1; d1["input_text"] = p1
        prompts.append(d1); pid += 1

        d2 = dict(p); del d2["var"]; del d2["v1"]; del d2["v2"]; d2[v_name] = v2
        if "marks" not in d2: d2["marks"] = 5 if d2.get("difficulty") == "Hard" else 1
        p2 = f"generate question | subject: {d2.get('subject')} | topic: {d2.get('topic')} | class: {d2.get('class')} | difficulty: {d2.get('difficulty')} | marks: {d2.get('marks')} | type: {d2.get('question_type')}"
        d2["prompt_id"] = f"P20-SENS-{pid:04d}-B"; d2["category"] = "sensitivity_test"; d2["sensitivity_var"] = v_name; d2["sensitivity_val"] = v2; d2["input_text"] = p2
        prompts.append(d2); pid += 1

    return prompts

def run_pre_training_base_evaluation(tokenizer, prompts, device="cpu"):
    """
    Step 5: Pre-training baseline evaluation using raw google/flan-t5-small.
    """
    if os.path.exists(OUT_BASE_OUTPUTS):
        with open(OUT_BASE_OUTPUTS, "r", encoding="utf-8") as f:
            lines = [l for l in f if l.strip()]
        if len(lines) == len(prompts):
            print(f"\n--- STEP 5: Base model outputs already exist at {OUT_BASE_OUTPUTS} ({len(lines)} outputs). Preserving existing evaluation.")
            return

    print("\n--- STEP 5: EVALUATING PRE-TRAINING BASE MODEL (google/flan-t5-small) ---")
    base_model = AutoModelForSeq2SeqLM.from_pretrained(BASE_MODEL_NAME).to(device)
    base_model.eval()
    
    base_outputs = []
    t0 = time.time()
    for idx, p in enumerate(prompts, 1):
        in_text = p["input_text"]
        inputs = tokenizer(in_text, return_tensors="pt", max_length=128, truncation=True).to(device)
        with torch.no_grad():
            outs = base_model.generate(**inputs, max_new_tokens=128, num_beams=4, early_stopping=True, repetition_penalty=1.2)
        gen_text = tokenizer.decode(outs[0], skip_special_tokens=True).strip()
        
        base_outputs.append({
            "prompt_id": p["prompt_id"],
            "subject": p["subject"],
            "topic": p["topic"],
            "class": p["class"],
            "input_text": in_text,
            "base_generated_output": gen_text
        })
        if idx % 100 == 0 or idx == len(prompts):
            print(f"  Base Evaluated: {idx:03d}/{len(prompts)} prompts...")
            
    with open(OUT_BASE_OUTPUTS, "w", encoding="utf-8") as f:
        for bo in base_outputs:
            f.write(json.dumps(bo) + "\n")
    print(f"Saved Base Pre-Training Outputs: {OUT_BASE_OUTPUTS} ({time.time()-t0:.2f}s)")
    del base_model
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

def find_latest_checkpoint(checkpoint_dir):
    """
    Scans checkpoint_dir for valid checkpoint directories containing trainer_state.pt,
    and returns (latest_ckpt_dir, global_step, epoch).
    """
    if not os.path.exists(checkpoint_dir):
        return None, 0, 1
    
    ckpt_dirs = []
    for d in os.listdir(checkpoint_dir):
        full_d = os.path.join(checkpoint_dir, d)
        if os.path.isdir(full_d):
            state_file = os.path.join(full_d, "trainer_state.pt")
            config_file = os.path.join(full_d, "config.json")
            if os.path.exists(state_file) and os.path.exists(config_file):
                try:
                    state = torch.load(state_file, map_location="cpu")
                    g_step = state.get("global_step", 0)
                    ep = state.get("epoch", 1)
                    ckpt_dirs.append((full_d, g_step, ep))
                except Exception:
                    pass
                    
    if not ckpt_dirs:
        return None, 0, 1
        
    ckpt_dirs.sort(key=lambda x: x[1], reverse=True)
    return ckpt_dirs[0][0], ckpt_dirs[0][1], ckpt_dirs[0][2]

def train_v16_model():
    set_seed(42)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print("=" * 80)
    print("AQPG PHASE 20: CONTROLLED V16 FLAN-T5-SMALL TRAINING")
    print("=" * 80)
    
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL_NAME)
    
    # --------------------------------------------------------------------------
    # STEP 6 & STEP 5: BUILD EVALUATION MATRIX & RUN PRE-TRAINING BASE EVALUATION
    # --------------------------------------------------------------------------
    eval_prompts = build_phase20_evaluation_prompts()
    with open(OUT_EVAL_PROMPTS, "w", encoding="utf-8") as f:
        for p in eval_prompts:
            f.write(json.dumps(p) + "\n")
    print(f"Saved {len(eval_prompts)} Controlled Evaluation Prompts to: {OUT_EVAL_PROMPTS}")
    
    run_pre_training_base_evaluation(tokenizer, eval_prompts, device=device)

    # --------------------------------------------------------------------------
    # STEP 3 & 4: DATASET LOADING & STEP CALCULATIONS
    # --------------------------------------------------------------------------
    print("\n--- STEP 3 & 4: DATASET LOADING & STEP CALCULATIONS ---")
    train_dataset = QGDataset(V16_TRAIN_PATH, tokenizer, max_input_len=128, max_target_len=256)
    val_dataset = QGDataset(V16_VAL_PATH, tokenizer, max_input_len=128, max_target_len=256)
    
    epochs = 3
    batch_size = 16 if torch.cuda.is_available() else 8
    grad_accum_steps = 2
    effective_batch_size = batch_size * grad_accum_steps
    
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, drop_last=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)
    
    total_train_records = len(train_dataset)
    steps_per_epoch = len(train_loader) // grad_accum_steps
    total_optimization_steps = steps_per_epoch * epochs
    
    lr = 3e-4
    warmup_steps = int(total_optimization_steps * 0.05)
    
    training_config = {
        "model_name": BASE_MODEL_NAME,
        "epochs": epochs,
        "train_records": total_train_records,
        "validation_records": len(val_dataset),
        "batch_size": batch_size,
        "gradient_accumulation_steps": grad_accum_steps,
        "effective_batch_size": effective_batch_size,
        "steps_per_epoch": steps_per_epoch,
        "total_optimization_steps": total_optimization_steps,
        "learning_rate": lr,
        "warmup_steps": warmup_steps,
        "max_input_length": 128,
        "max_target_length": 256,
        "weight_decay": 0.01,
        "gradient_clipping": 1.0,
        "seed": 42,
        "device": device
    }
    
    print(f"  Total Train Records:        {total_train_records:,}")
    print(f"  Effective Batch Size:       {effective_batch_size}")
    print(f"  Steps Per Epoch:            {steps_per_epoch:,}")
    print(f"  Total Target Epochs:        {epochs}")
    print(f"  Total Optimization Steps:   {total_optimization_steps:,}")
    print(f"  Learning Rate:              {lr}")
    print(f"  Warmup Steps:               {warmup_steps}")
    print(f"  Device:                     {device}")
    
    with open(OUT_CONFIG_JSON, "w", encoding="utf-8") as f:
        json.dump(training_config, f, indent=2)
    print(f"Saved Config: {OUT_CONFIG_JSON}")

    # --------------------------------------------------------------------------
    # STEP 7: MODEL TRAINING LOOP WITH AUTOMATIC CHECKPOINT RESUME
    # --------------------------------------------------------------------------
    print("\n--- STEP 7: EXECUTING FLAN-T5-SMALL V16 TRAINING (3 FULL EPOCHS) ---", flush=True)
    
    latest_ckpt_dir, resume_step, resume_epoch = find_latest_checkpoint(CHECKPOINT_DIR)
    
    if latest_ckpt_dir and resume_step > 0:
        print(f"\n[RESUME DETECTED] Valid checkpoint found at: {latest_ckpt_dir} (Global Step: {resume_step}, Epoch: {resume_epoch})", flush=True)
        print("Loading model weights and tokenizer from checkpoint...", flush=True)
        model = AutoModelForSeq2SeqLM.from_pretrained(latest_ckpt_dir).to(device)
        tokenizer = AutoTokenizer.from_pretrained(latest_ckpt_dir)
        model.train()
        
        optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=0.01)
        scheduler = get_linear_schedule_with_warmup(optimizer, num_warmup_steps=warmup_steps, num_training_steps=total_optimization_steps)
        
        state = torch.load(os.path.join(latest_ckpt_dir, "trainer_state.pt"), map_location="cpu")
        optimizer.load_state_dict(state["optimizer_state_dict"])
        scheduler.load_state_dict(state["scheduler_state_dict"])
        if "rng_state" in state and state["rng_state"] is not None:
            rng_tensor = normalize_rng_state(state["rng_state"])
            assert isinstance(rng_tensor, torch.Tensor), f"Expected torch.Tensor, got {type(rng_tensor)}"
            assert rng_tensor.dtype == torch.uint8, f"Expected uint8, got {rng_tensor.dtype}"
            assert rng_tensor.device.type == "cpu", f"Expected cpu device, got {rng_tensor.device}"
            torch.set_rng_state(rng_tensor)
            print("[RESUME SUCCESS] CPU RNG state restored.", flush=True)

        if "cuda_rng_state" in state and state["cuda_rng_state"] is not None:
            cuda_rng_tensor = normalize_rng_state(state["cuda_rng_state"])
            assert isinstance(cuda_rng_tensor, torch.Tensor), f"Expected torch.Tensor, got {type(cuda_rng_tensor)}"
            assert cuda_rng_tensor.dtype == torch.uint8, f"Expected uint8, got {cuda_rng_tensor.dtype}"
            if torch.cuda.is_available():
                torch.cuda.set_rng_state(cuda_rng_tensor)
                print("[RESUME SUCCESS] CUDA RNG state restored.", flush=True)
            else:
                print("[WARN] CUDA RNG state found, but CUDA is unavailable. Skipping CUDA RNG restoration.", flush=True)

        global_step = state["global_step"]
        start_epoch = state["epoch"]
        print(f"[RESUME SUCCESS] Resumed training state at Global Step {global_step}, Epoch {start_epoch}", flush=True)
    else:
        print("\nNo valid checkpoint found — future run will start fresh from step 0.", flush=True)
        model = AutoModelForSeq2SeqLM.from_pretrained(BASE_MODEL_NAME).to(device)
        model.train()
        
        optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=0.01)
        scheduler = get_linear_schedule_with_warmup(optimizer, num_warmup_steps=warmup_steps, num_training_steps=total_optimization_steps)
        global_step = 0
        start_epoch = 1
    
    epoch_metrics = []
    start_train_time = time.time()
    
    for epoch in range(start_epoch, epochs + 1):
        epoch_start_time = time.time()
        running_train_loss = 0.0
        train_batches = 0
        optimizer.zero_grad()
        
        print(f"\n>> Starting Epoch {epoch}/{epochs}...", flush=True)
        for b_idx, batch in enumerate(train_loader, 1):
            accumulated_step_target = (epoch - 1) * steps_per_epoch + math.ceil(b_idx / grad_accum_steps)
            if accumulated_step_target <= global_step:
                continue
                
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            labels = batch["labels"].to(device)
            
            outputs = model(input_ids=input_ids, attention_mask=attention_mask, labels=labels)
            loss = outputs.loss / grad_accum_steps
            loss.backward()
            
            running_train_loss += outputs.loss.item()
            train_batches += 1
            
            if b_idx % grad_accum_steps == 0 or b_idx == len(train_loader):
                torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
                optimizer.step()
                scheduler.step()
                optimizer.zero_grad()
                global_step += 1

                # Periodic Checkpoint Saving every 500 optimization steps
                if global_step % 500 == 0:
                    step_ckpt_dir = os.path.join(CHECKPOINT_DIR, f"checkpoint-{global_step}")
                    os.makedirs(step_ckpt_dir, exist_ok=True)
                    model.save_pretrained(step_ckpt_dir)
                    tokenizer.save_pretrained(step_ckpt_dir)
                    torch.save({
                        "global_step": global_step,
                        "epoch": epoch,
                        "optimizer_state_dict": optimizer.state_dict(),
                        "scheduler_state_dict": scheduler.state_dict(),
                        "rng_state": torch.get_rng_state(),
                        "cuda_rng_state": torch.cuda.get_rng_state() if torch.cuda.is_available() else None
                    }, os.path.join(step_ckpt_dir, "trainer_state.pt"))
                    print(f"  [CHECKPOINT SAVED] Periodic checkpoint written to: {step_ckpt_dir}", flush=True)

            if b_idx % 400 == 0 or b_idx == len(train_loader):
                cur_avg_loss = running_train_loss / max(train_batches, 1)
                print(f"  [Epoch {epoch} | Batch {b_idx:04d}/{len(train_loader):04d} | Step {global_step:04d}] Current Loss: {cur_avg_loss:.4f} (LR: {scheduler.get_last_lr()[0]:.2e})", flush=True)

        avg_epoch_train_loss = running_train_loss / max(train_batches, 1)
        
        # Validation Evaluation
        model.eval()
        running_val_loss = 0.0
        val_batches = 0
        with torch.no_grad():
            for v_idx, v_batch in enumerate(val_loader, 1):
                v_in = v_batch["input_ids"].to(device)
                v_att = v_batch["attention_mask"].to(device)
                v_lab = v_batch["labels"].to(device)
                v_out = model(input_ids=v_in, attention_mask=v_att, labels=v_lab)
                running_val_loss += v_out.loss.item()
                val_batches += 1
                
        avg_epoch_val_loss = running_val_loss / max(val_batches, 1)
        epoch_dur = round(time.time() - epoch_start_time, 2)
        model.train()
        
        print(f">> Epoch {epoch} Complete! Train Loss: {avg_epoch_train_loss:.4f} | Val Loss: {avg_epoch_val_loss:.4f} | Duration: {epoch_dur}s", flush=True)

        # Save Epoch Checkpoint
        epoch_ckpt_dir = os.path.join(CHECKPOINT_DIR, f"checkpoint-epoch-{epoch}")
        os.makedirs(epoch_ckpt_dir, exist_ok=True)
        model.save_pretrained(epoch_ckpt_dir)
        tokenizer.save_pretrained(epoch_ckpt_dir)
        torch.save({
            "global_step": global_step,
            "epoch": epoch,
            "optimizer_state_dict": optimizer.state_dict(),
            "scheduler_state_dict": scheduler.state_dict(),
            "rng_state": torch.get_rng_state(),
            "cuda_rng_state": torch.cuda.get_rng_state() if torch.cuda.is_available() else None
        }, os.path.join(epoch_ckpt_dir, "trainer_state.pt"))
        print(f"  [CHECKPOINT SAVED] Epoch {epoch} checkpoint written to: {epoch_ckpt_dir}", flush=True)
        
        epoch_metrics.append({
            "epoch": epoch,
            "train_loss": round(avg_epoch_train_loss, 4),
            "val_loss": round(avg_epoch_val_loss, 4),
            "duration_seconds": epoch_dur,
            "completed_steps": global_step
        })

    total_training_duration = round(time.time() - start_train_time, 2)
    print(f"\nTraining Complete in {total_training_duration}s ({total_training_duration/60:.2f} mins).", flush=True)

    # --------------------------------------------------------------------------
    # SAVE MODEL CHECKPOINT
    # --------------------------------------------------------------------------
    print(f"\nSaving Final V16 Checkpoint to: {CHECKPOINT_DIR}...")
    model.save_pretrained(CHECKPOINT_DIR)
    tokenizer.save_pretrained(CHECKPOINT_DIR)
    
    # Save training metrics
    train_results = {
        "total_epochs": epochs,
        "total_optimization_steps": global_step,
        "total_duration_seconds": total_training_duration,
        "final_train_loss": epoch_metrics[-1]["train_loss"],
        "final_val_loss": epoch_metrics[-1]["val_loss"],
        "epoch_metrics": epoch_metrics,
        "training_config": training_config
    }
    with open(OUT_TRAIN_METRICS, "w", encoding="utf-8") as f:
        json.dump(train_results, f, indent=2)
    print(f"Saved Training Metrics: {OUT_TRAIN_METRICS}")

    # --------------------------------------------------------------------------
    # STEP 8: CHECKPOINT INTEGRITY VERIFICATION
    # --------------------------------------------------------------------------
    print("\n--- STEP 8: CHECKPOINT INTEGRITY VERIFICATION ---")
    req_files = ["model.safetensors", "config.json", "generation_config.json", "tokenizer.json", "tokenizer_config.json", "special_tokens_map.json"]
    files_check = {}
    for rf in req_files:
        rf_path = os.path.join(CHECKPOINT_DIR, rf)
        exists = os.path.exists(rf_path)
        size = os.path.getsize(rf_path) if exists else 0
        files_check[rf] = {"exists": exists, "size_bytes": size}
        print(f"  [{'PASS' if exists else 'FAIL'}] {rf:25s} ({size:,} bytes)")
        
    print("\nReloading Checkpoint Independently for Integrity Check...")
    reloaded_tok = AutoTokenizer.from_pretrained(CHECKPOINT_DIR)
    reloaded_model = AutoModelForSeq2SeqLM.from_pretrained(CHECKPOINT_DIR).to("cpu")
    reloaded_model.eval()
    
    nan_inf_found = False
    for n, p in reloaded_model.named_parameters():
        if torch.isnan(p).any() or torch.isinf(p).any():
            nan_inf_found = True
            break
            
    print(f"  Reload Weight Integrity: {'PASS (No NaN/Inf)' if not nan_inf_found else 'FAIL (Corrupted)'}")
    
    # Test generation on sample prompt
    sample_p = "generate question | subject: Physics | topic: Newton's Laws & Friction | class: Class 11 | difficulty: Medium | marks: 3 | type: Numerical"
    s_in = reloaded_tok(sample_p, return_tensors="pt")
    with torch.no_grad():
        s_out = reloaded_model.generate(**s_in, max_new_tokens=64, num_beams=4)
    sample_gen = reloaded_tok.decode(s_out[0], skip_special_tokens=True)
    print(f"  Sample Prompt: {sample_p}")
    print(f"  Sample Generation: {sample_gen}")

    verif_data = {
        "checkpoint_directory": CHECKPOINT_DIR,
        "files": files_check,
        "all_files_present": all(v["exists"] for v in files_check.values()),
        "nan_inf_weights_present": nan_inf_found,
        "sample_generation_test": {
            "prompt": sample_p,
            "output": sample_gen
        },
        "status": "PASS" if not nan_inf_found and all(v["exists"] for v in files_check.values()) else "FAIL"
    }
    with open(OUT_CHECKPOINT_VERIF, "w", encoding="utf-8") as f:
        json.dump(verif_data, f, indent=2)
    print(f"Saved Checkpoint Verification: {OUT_CHECKPOINT_VERIF}")

    print("\n" + "=" * 80)
    print("PHASE 20 V16 TRAINING COMPLETE.")
    print("=" * 80)

if __name__ == "__main__":
    train_v16_model()
