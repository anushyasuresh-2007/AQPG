"""
run_post_training_validation_audit.py
Executes Phase 2-9 post-training validation and model quality audit for AQPG FLAN-T5 Numerical QG pilot.
"""

import os
import sys
import json
import re
import random
import torch
import numpy as np
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
QG_DIR = os.path.join(BASE_DIR, "ml", "models", "qg_flan_t5")
FINE_TUNED_MODEL_DIR = os.path.join(QG_DIR, "flan_t5_small_numerical")
BASE_MODEL_NAME = "google/flan-t5-small"
EVAL_JSON_PATH = os.path.join(QG_DIR, "numerical_pilot_evaluation.json")
VAL_V3_PATH = os.path.join(QG_DIR, "qg_validation_dataset_v3.jsonl")

def set_seed(seed=42):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)

def generate_question(model, tokenizer, prompt_str, device="cpu", num_beams=4, repetition_penalty=1.2, max_new_tokens=150):
    inputs = tokenizer(prompt_str, return_tensors="pt", max_length=256, truncation=True).to(device)
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            num_beams=num_beams,
            early_stopping=True,
            repetition_penalty=repetition_penalty
        )
    return tokenizer.decode(outputs[0], skip_special_tokens=True).strip()

def run_audit():
    set_seed(42)
    device = "cpu"
    
    print("=" * 80)
    print("PHASE 1 & 2: VERIFY ARTIFACTS AND LOAD FINE-TUNED MODEL")
    print("=" * 80)
    
    if not os.path.exists(FINE_TUNED_MODEL_DIR):
        print(f"ERROR: Model dir does not exist: {FINE_TUNED_MODEL_DIR}")
        sys.exit(1)
        
    print(f"Loading Fine-Tuned Model from: {FINE_TUNED_MODEL_DIR}")
    ft_tokenizer = AutoTokenizer.from_pretrained(FINE_TUNED_MODEL_DIR)
    ft_model = AutoModelForSeq2SeqLM.from_pretrained(FINE_TUNED_MODEL_DIR).to(device)
    ft_model.eval()
    print("Fine-Tuned Model & Tokenizer loaded successfully!")
    
    print(f"\nLoading Base Model from: {BASE_MODEL_NAME}")
    base_tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL_NAME)
    base_model = AutoModelForSeq2SeqLM.from_pretrained(BASE_MODEL_NAME).to(device)
    base_model.eval()
    print("Base Model & Tokenizer loaded successfully!")

    # Phase 2: Checkpoint Reload Test on 10 Validation Prompts
    val_records = []
    with open(VAL_V3_PATH, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                item = json.loads(line.strip())
                if str(item.get("question_type", "")).lower() == "numerical" or item.get("source_dataset") == "gsm8k_reasoning":
                    val_records.append(item)
                    
    sample_10 = val_records[:10]
    print("\nPhase 2 Reload Test (10 Validation Prompts):")
    phase2_results = []
    for idx, r in enumerate(sample_10, 1):
        prompt = r['input_text']
        gen_q = generate_question(ft_model, ft_tokenizer, prompt, device)
        phase2_results.append({
            "idx": idx,
            "prompt": prompt,
            "gen_q": gen_q,
            "is_non_empty": len(gen_q) > 0
        })
        print(f"  [{idx}] Gen: {gen_q}")

    # Phase 5: Control Adherence Test (20 Carefully Selected Control Prompts)
    control_prompts = [
        # Mathematics
        {"subject": "Mathematics", "topic": "Word Problems & Calculation", "bloom": "Remember", "difficulty": "easy", "marks": 1},
        {"subject": "Mathematics", "topic": "Word Problems & Calculation", "bloom": "Understand", "difficulty": "easy", "marks": 2},
        {"subject": "Mathematics", "topic": "Word Problems & Calculation", "bloom": "Apply", "difficulty": "medium", "marks": 3},
        {"subject": "Mathematics", "topic": "Word Problems & Calculation", "bloom": "Analyze", "difficulty": "hard", "marks": 5},
        {"subject": "Mathematics", "topic": "Algebra & Equations", "bloom": "Apply", "difficulty": "medium", "marks": 3},
        {"subject": "Mathematics", "topic": "Geometry & Mensuration", "bloom": "Analyze", "difficulty": "hard", "marks": 5},
        {"subject": "Mathematics", "topic": "Percentage & Ratio", "bloom": "Understand", "difficulty": "easy", "marks": 2},
        
        # Physics
        {"subject": "Physics", "topic": "Kinematics & Motion", "bloom": "Remember", "difficulty": "easy", "marks": 1},
        {"subject": "Physics", "topic": "Kinematics & Motion", "bloom": "Apply", "difficulty": "medium", "marks": 3},
        {"subject": "Physics", "topic": "Work, Energy & Power", "bloom": "Analyze", "difficulty": "hard", "marks": 5},
        {"subject": "Physics", "topic": "Electricity & Magnetism", "bloom": "Apply", "difficulty": "medium", "marks": 3},
        {"subject": "Physics", "topic": "Optics & Light", "bloom": "Understand", "difficulty": "easy", "marks": 2},
        {"subject": "Physics", "topic": "Thermodynamics", "bloom": "Analyze", "difficulty": "hard", "marks": 5},

        # Chemistry
        {"subject": "Chemistry", "topic": "Stoichiometry & Mole Concept", "bloom": "Apply", "difficulty": "medium", "marks": 3},
        {"subject": "Chemistry", "topic": "Stoichiometry & Mole Concept", "bloom": "Analyze", "difficulty": "hard", "marks": 5},
        {"subject": "Chemistry", "topic": "Chemical Kinetics & Rates", "bloom": "Apply", "difficulty": "medium", "marks": 3},
        {"subject": "Chemistry", "topic": "Solutions & Concentration", "bloom": "Understand", "difficulty": "easy", "marks": 2},
        {"subject": "Chemistry", "topic": "Electrochemistry", "bloom": "Remember", "difficulty": "easy", "marks": 1},
        {"subject": "Chemistry", "topic": "Thermodynamics in Chemistry", "bloom": "Analyze", "difficulty": "hard", "marks": 5},
        {"subject": "Chemistry", "topic": "Gas Laws & Pressure", "bloom": "Apply", "difficulty": "medium", "marks": 3},
    ]

    print("\n" + "=" * 80)
    print("PHASE 5 & 9: 20 CONTROL PROMPTS — BASE VS FINE-TUNED MODEL COMPARISON")
    print("=" * 80)

    comparison_results = []
    for idx, ctrl in enumerate(control_prompts, 1):
        prompt_str = f"generate question | subject: {ctrl['subject']} | topic: {ctrl['topic']} | bloom: {ctrl['bloom']} | difficulty: {ctrl['difficulty']} | marks: {ctrl['marks']} | type: Numerical"
        
        base_gen = generate_question(base_model, base_tokenizer, prompt_str, device)
        ft_gen = generate_question(ft_model, ft_tokenizer, prompt_str, device)
        
        comparison_results.append({
            "idx": idx,
            "ctrl": ctrl,
            "prompt_str": prompt_str,
            "base_gen": base_gen,
            "ft_gen": ft_gen
        })
        
        print(f"\nPROMPT [{idx}]: {ctrl['subject']} | {ctrl['topic']} | Bloom:{ctrl['bloom']} | Diff:{ctrl['difficulty']} | Marks:{ctrl['marks']}")
        print(f"  BASE MODEL:       {base_gen}")
        print(f"  FINE-TUNED MODEL: {ft_gen}")

    # Phase 6: Generation Diversity Test
    print("\n" + "=" * 80)
    print("PHASE 6: GENERATION DIVERSITY TEST (10 GENERATIONS)")
    print("=" * 80)
    div_prompt = "generate question | subject: Mathematics | topic: Percentage & Ratio | bloom: Apply | difficulty: medium | marks: 3 | type: Numerical"
    
    div_outputs = []
    # Test across beam sizes and temperatures for sampling diversity
    for i in range(10):
        # vary beam / sampling seed slightly
        set_seed(42 + i)
        inputs = ft_tokenizer(div_prompt, return_tensors="pt", max_length=256, truncation=True).to(device)
        with torch.no_grad():
            outputs = ft_model.generate(
                **inputs,
                max_new_tokens=150,
                do_sample=True,
                top_p=0.92,
                temperature=0.7 + (i * 0.05),
                repetition_penalty=1.2
            )
        g_text = ft_tokenizer.decode(outputs[0], skip_special_tokens=True).strip()
        div_outputs.append(g_text)
        print(f"  Diversity [{i+1}]: {g_text}")

    unique_div = len(set(div_outputs))
    exact_dup_rate = round((10 - unique_div) / 10 * 100, 2)
    print(f"Diversity Summary: {unique_div}/10 Unique Generations. Exact Duplicate Rate: {exact_dup_rate}%")

    # Output audit summary payload
    audit_output = {
        "phase2_reload": phase2_results,
        "phase5_9_comparison": comparison_results,
        "phase6_diversity": {
            "prompt": div_prompt,
            "generations": div_outputs,
            "unique_count": unique_div,
            "exact_duplicate_rate": exact_dup_rate
        }
    }

    with open(os.path.join(QG_DIR, "post_training_validation_raw.json"), "w", encoding="utf-8") as f:
        json.dump(audit_output, f, indent=2)
    print(f"\nSaved post-training raw evaluation data to: {os.path.join(QG_DIR, 'post_training_validation_raw.json')}")

if __name__ == "__main__":
    run_audit()
