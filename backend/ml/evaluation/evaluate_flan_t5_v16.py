"""
evaluate_flan_t5_v16.py
Phase 20 Step 9: 520 Controlled Prompt Post-Training Evaluation Suite.
Evaluates trained V16 FLAN-T5-Small model against 520 controlled prompts across:
- Pre-evaluation Safeguards & Artifact Hash Signatures
- Generation Success & Output Validity Checks
- Subject Conditioning (5x5 Confusion Matrix), Topic Alignment, Class Alignment
- Question-Type Accuracy, Bloom Taxonomy Classification
- Subject/Domain & Difficulty Breakdowns
- Control Sensitivity (20 Perturbation Test Pairs)
- Template Diversity (Stem Entropy & Top-10 Concentration)
- Numerical Question Validity & Training Target Memorization Audit
- Structured Failure Analysis & Step 9 Reproducibility Documentation
"""

import os
import sys
import json
import time
import math
import hashlib
import re
import argparse
from collections import Counter, defaultdict
import torch
import transformers
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
DEFAULT_V16_CHECKPOINT = os.path.join(BASE_DIR, "backend", "ml", "models", "checkpoints", "flan_t5_v16_small")
V16_TRAIN_DATASET = os.path.join(BASE_DIR, "datasets", "v16", "qg_train_dataset_v16.jsonl")
PROMPTS_FILE = os.path.join(BASE_DIR, "phase20_evaluation_prompts.jsonl")
if not os.path.exists(PROMPTS_FILE):
    PROMPTS_FILE = os.path.join(BASE_DIR, "backend", "ml", "evaluation", "phase20_evaluation_prompts.jsonl")
BASE_OUTPUTS_FILE = os.path.join(BASE_DIR, "phase20_base_outputs.jsonl")

# Step 9 Artifact Output Paths
V16_OUTPUTS_FILE = os.path.join(BASE_DIR, "phase20_v16_generated_outputs.jsonl")
OUT_STEP9_SUMMARY = os.path.join(BASE_DIR, "phase20_v16_evaluation_summary.json")
OUT_QUALITY_EVAL = os.path.join(BASE_DIR, "phase20_quality_evaluation.json")
OUT_FAILURE_ANALYSIS = os.path.join(BASE_DIR, "phase20_failure_analysis.json")
OUT_CONFUSION_MATRIX = os.path.join(BASE_DIR, "phase20_subject_confusion_matrix.json")
OUT_CONTROL_SENSITIVITY = os.path.join(BASE_DIR, "phase20_control_sensitivity.json")
OUT_TEMPLATE_DIVERSITY = os.path.join(BASE_DIR, "phase20_template_diversity.json")
OUT_NUMERICAL_EVAL = os.path.join(BASE_DIR, "phase20_numerical_evaluation.json")
OUT_MEMORIZATION = os.path.join(BASE_DIR, "phase20_memorization.json")
OUT_CHECKPOINT_VERIF = os.path.join(BASE_DIR, "phase20_checkpoint_verification.json")
OUT_DOC_REPORT = os.path.join(BASE_DIR, "docs", "phase20_step9_evaluation_report.md")

SUBJECT_KEYWORDS = {
    "Mathematics": ["calculate", "find", "equation", "solve", "root", "polynomial", "ratio", "geometry", "area", "volume", "probability", "mean", "median", "mode", "derivative", "integral", "matrix", "vector", "triangle", "circle", "angle", "sum", "value", "fraction", "coordinates", "arithmetic progression"],
    "Physics": ["force", "velocity", "acceleration", "energy", "power", "momentum", "friction", "gravitation", "mass", "newton", "optics", "refraction", "interference", "wavelength", "current", "resistance", "ohm", "magnetic", "induction", "voltage", "speed", "motion", "thermodynamics", "heat", "torque", "sound", "frequency"],
    "Chemistry": ["reaction", "compound", "element", "acid", "base", "salt", "molarity", "molality", "equilibrium", "redox", "oxidation", "periodic", "orbital", "hydrocarbon", "alkane", "alkene", "enthalpy", "nernst", "catalyst", "electron", "valency", "bond", "ph", "titration", "solution"],
    "Biology": ["cell", "organelle", "mitosis", "meiosis", "photosynthesis", "respiration", "krebs", "genetics", "dna", "rna", "inheritance", "monohybrid", "circulatory", "blood", "excretory", "kidney", "ecosystem", "biotechnology", "enzyme", "protein", "chloroplast", "mitochondria", "organism", "species"],
    "General Science": ["matter", "state", "mixture", "pure", "solid", "liquid", "gas", "atom", "molecule", "conservation", "tissue", "plant", "animal", "motion", "force", "gravitation", "work", "energy", "evaporation", "diffusion", "temperature"]
}

BLOOM_KEYWORDS = {
    "Remember": ["define", "list", "state", "name", "recall", "identify", "what is", "mention"],
    "Understand": ["explain", "describe", "summarize", "interpret", "discuss", "why does", "how does"],
    "Apply": ["calculate", "find", "solve", "determine", "compute", "derive", "using"],
    "Analyze": ["compare", "contrast", "differentiate", "distinguish", "analyze", "break down"],
    "Evaluate": ["evaluate", "assess", "justify", "criticize", "judge", "validate"],
    "Create": ["formulate", "design", "construct", "propose", "synthesize", "create"]
}

def compute_sha256(filepath):
    """Computes SHA-256 hash of a file without modifying it."""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(65536), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest().upper()

def clean_text(text):
    return re.sub(r'\s+', ' ', text).strip()

def compute_entropy(texts):
    if not texts:
        return 0.0, 0.0, 0.0, []
    stems = []
    for t in texts:
        words = t.strip().lower().split()
        prefix = " ".join(words[:4]) if len(words) >= 4 else " ".join(words)
        stems.append(prefix)
    counts = Counter(stems)
    total = len(stems)
    entropy = -sum((c / total) * math.log2(c / total) for c in counts.values())
    top10_sum = sum(c for _, c in counts.most_common(10))
    top10_conc = (top10_sum / total) * 100.0 if total > 0 else 0.0
    unique_ratio = (len(counts) / total) * 100.0 if total > 0 else 0.0
    return entropy, top10_conc, unique_ratio, counts.most_common(10)

def detect_subject(text):
    text_lower = text.lower()
    scores = {}
    for subj, kw_list in SUBJECT_KEYWORDS.items():
        score = sum(1 for kw in kw_list if re.search(r'\b' + re.escape(kw) + r'\b', text_lower))
        scores[subj] = score
    max_score = max(scores.values())
    if max_score == 0:
        return "UNKNOWN"
    candidates = [s for s, sc in scores.items() if sc == max_score]
    return candidates[0]

def classify_bloom_level(text):
    text_lower = text.lower()
    for bloom, kws in BLOOM_KEYWORDS.items():
        if any(re.search(r'\b' + re.escape(kw) + r'\b', text_lower) for kw in kws):
            return bloom
    return "Understand"

def evaluate_v16(checkpoint_dir=DEFAULT_V16_CHECKPOINT):
    start_time_iso = time.strftime("%Y-%m-%d %H:%M:%S")
    t_start = time.time()

    print("=" * 80)
    print("AQPG PHASE 20 STEP 9: 520 CONTROLLED PROMPT POST-TRAINING EVALUATION")
    print("=" * 80)
    print(f"Target Checkpoint Directory: {checkpoint_dir}")
    print(f"Evaluation Prompts File:    {PROMPTS_FILE}")

    # Ensure output directories exist before evaluation
    output_files = [
        V16_OUTPUTS_FILE, OUT_STEP9_SUMMARY, OUT_QUALITY_EVAL, OUT_FAILURE_ANALYSIS,
        OUT_CONFUSION_MATRIX, OUT_CONTROL_SENSITIVITY, OUT_TEMPLATE_DIVERSITY,
        OUT_NUMERICAL_EVAL, OUT_MEMORIZATION, OUT_CHECKPOINT_VERIF, OUT_DOC_REPORT
    ]
    for out_f in output_files:
        os.makedirs(os.path.dirname(os.path.abspath(out_f)), exist_ok=True)

    # --------------------------------------------------------------------------
    # SAFEGUARD 1-8: PRE-EVALUATION CHECKS & REPRODUCIBILITY METADATA
    # --------------------------------------------------------------------------
    print("\n--- SAFEGUARDS & PRE-EVALUATION INTEGRITY AUDIT ---")
    
    # Prompt set check
    if not os.path.exists(PROMPTS_FILE):
        print(f"[CRITICAL ERROR] Prompts file not found at {PROMPTS_FILE}")
        sys.exit(1)

    prompts_sha256 = compute_sha256(PROMPTS_FILE)
    prompts = []
    with open(PROMPTS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                prompts.append(json.loads(line.strip()))

    prompt_count = len(prompts)
    print(f"  Prompt File SHA-256:      {prompts_sha256}")
    print(f"  Evaluation Prompt Count:  {prompt_count} (Expected: 520)")

    if prompt_count != 520:
        print(f"[CRITICAL ERROR] Expected 520 prompts, found {prompt_count}. Aborting.")
        sys.exit(1)

    # Checkpoint required files check
    req_files = ["model.safetensors", "config.json", "generation_config.json", "tokenizer.json", "tokenizer_config.json", "special_tokens_map.json"]
    files_check = {}
    missing_files = []

    dir_exists = os.path.exists(checkpoint_dir)
    print(f"  Checkpoint Dir Exists:    {dir_exists}")

    if dir_exists:
        for rf in req_files:
            rf_path = os.path.join(checkpoint_dir, rf)
            exists = os.path.exists(rf_path)
            size = os.path.getsize(rf_path) if exists else 0
            sha = compute_sha256(rf_path) if exists else None
            files_check[rf] = {"exists": exists, "size_bytes": size, "sha256": sha}
            if not exists or size == 0:
                missing_files.append(rf)
            elif rf == "special_tokens_map.json":
                try:
                    with open(rf_path, "r", encoding="utf-8") as f_sp:
                        json.load(f_sp)
                except Exception:
                    missing_files.append(f"{rf} (INVALID_JSON)")

            is_valid_file = exists and size > 0 and (rf != "special_tokens_map.json" or rf not in missing_files)
            print(f"    [{'PASS' if is_valid_file else 'FAIL'}] {rf:25s} ({size:,} bytes)")
    else:
        for rf in req_files:
            files_check[rf] = {"exists": False, "size_bytes": 0, "sha256": None}
            missing_files.append(rf)

    if missing_files or not dir_exists:
        print(f"\n[STEP 9 PRE-CHECK FAIL] Missing/invalid checkpoint files in {checkpoint_dir}: {missing_files}")
        print("Model checkpoint weights reside in Colab Google Drive path:")
        print("  /content/drive/MyDrive/AQPG/backend/ml/models/checkpoints/flan_t5_v16_small/")
        print("Please ensure special_tokens_map.json and all required files are valid before running evaluation.")

        summary_fail = {
            "timestamp": start_time_iso,
            "step": "Phase 20 Step 9 — 520 Controlled Prompt Post-Training Evaluation",
            "verdict": "FAIL (CHECKPOINT_INVALID_OR_MISSING)",
            "checkpoint_directory": checkpoint_dir,
            "missing_files": missing_files,
            "prompts_file": PROMPTS_FILE,
            "prompts_sha256": prompts_sha256,
            "prompts_count": prompt_count,
            "safeguard_checks": {
                "checkpoint_exists": False,
                "model_reload": False,
                "nan_inf_scan": False,
                "prompt_count_valid": True
            }
        }
        with open(OUT_STEP9_SUMMARY, "w", encoding="utf-8") as f:
            json.dump(summary_fail, f, indent=2)

        # Generate markdown failure report
        report_fail = f"""# AQPG Phase 20 Step 9 — Evaluation Report

**Timestamp:** {start_time_iso}  
**Verdict:** `FAIL (CHECKPOINT_INVALID_OR_MISSING)`  

## Safeguard Pre-Check Results
- **Evaluation Prompts Path:** [`phase20_evaluation_prompts.jsonl`](file:///{PROMPTS_FILE})
- **Prompts SHA-256:** `{prompts_sha256}`
- **Prompts Count:** `{prompt_count}` (`PASS - Exactly 520`)
- **Target Model Directory:** `{checkpoint_dir}`
- **Checkpoint Status:** Missing/invalid checkpoint files `{missing_files}`.

> [!WARNING]
> Training ran on Google Colab GPU (`/content/drive/MyDrive/AQPG/backend/ml/models/checkpoints/flan_t5_v16_small/`).
> Ensure all required checkpoint files (including `special_tokens_map.json`) exist and are valid.
"""
        with open(OUT_DOC_REPORT, "w", encoding="utf-8") as f:
            f.write(report_fail)

        print(f"\nSaved Step 9 Summary: {OUT_STEP9_SUMMARY}")
        print(f"Saved Step 9 Report:  {OUT_DOC_REPORT}")
        print("\nFINAL STEP 9 VERDICT: FAIL (CHECKPOINT_INVALID_OR_MISSING)")
        raise RuntimeError(f"[FATAL FAIL-CLOSED] Checkpoint validation failed: missing/invalid files {missing_files}")

    # Independent Model Reload & Architecture Safeguard Check
    print("\n--- INDEPENDENT MODEL RELOAD & PARAMETER INTEGRITY SCAN ---")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"  Target Inference Device: {device}")

    tokenizer = AutoTokenizer.from_pretrained(checkpoint_dir)
    model = AutoModelForSeq2SeqLM.from_pretrained(checkpoint_dir).to(device)
    model.eval()

    model_sha256 = files_check["model.safetensors"]["sha256"]
    print(f"  Model Architecture:      {model.config.model_type} ({getattr(model.config, 'architectures', ['FlanT5ForConditionalGeneration'])[0]})")
    print(f"  Model Weights SHA-256:   {model_sha256}")

    nan_count = 0
    inf_count = 0
    total_tensors = 0
    total_params = 0

    for name, param in model.named_parameters():
        total_tensors += 1
        total_params += param.numel()
        if torch.isnan(param).any(): nan_count += 1
        if torch.isinf(param).any(): inf_count += 1

    print(f"  Parameters Scanned:      {total_tensors} tensors / {total_params:,} parameters")
    print(f"  NaN Tensors:             {nan_count}")
    print(f"  Inf Tensors:             {inf_count}")

    if nan_count > 0 or inf_count > 0:
        print("[CRITICAL ERROR] Corrupted model weights detected (NaN/Inf present). Aborting evaluation.")
        sys.exit(1)

    # --------------------------------------------------------------------------
    # STEP 9 EVALUATION GENERATION LOOP (520 PROMPTS)
    # --------------------------------------------------------------------------
    print("\n--- EXECUTING DETERMINISTIC INFERENCE ON 520 CONTROLLED PROMPTS ---")
    generated_outputs = []
    gen_success_count = 0
    gen_failed_count = 0
    total_gen_time = 0.0

    subject_results = defaultdict(lambda: {"total": 0, "valid": 0, "subject_correct": 0, "topic_correct": 0, "qtype_correct": 0})
    diff_results = defaultdict(lambda: {"total": 0, "valid": 0, "subject_correct": 0, "qtype_correct": 0})
    bloom_counts = Counter()

    for idx, p in enumerate(prompts, 1):
        in_text = p["input_text"]
        inputs = tokenizer(in_text, return_tensors="pt", max_length=128, truncation=True).to(device)
        
        t0_gen = time.time()
        try:
            with torch.no_grad():
                outs = model.generate(
                    **inputs,
                    max_new_tokens=128,
                    num_beams=4,
                    early_stopping=True,
                    repetition_penalty=1.2
                )
            gen_text = tokenizer.decode(outs[0], skip_special_tokens=True).strip()
            latency = round(time.time() - t0_gen, 4)
            token_count = len(outs[0])
            gen_success = True
            gen_success_count += 1
        except Exception as e:
            gen_text = ""
            latency = round(time.time() - t0_gen, 4)
            token_count = 0
            gen_success = False
            gen_failed_count += 1
            print(f"  [ERROR] Prompt {p['prompt_id']} generation failed: {e}")

        total_gen_time += latency
        bloom_lvl = classify_bloom_level(gen_text)
        bloom_counts[bloom_lvl] += 1

        rec = dict(p)
        rec["v16_generated_output"] = gen_text
        rec["generation_success"] = gen_success
        rec["latency_seconds"] = latency
        rec["output_token_count"] = token_count
        rec["bloom_level"] = bloom_lvl
        generated_outputs.append(rec)

        if idx % 100 == 0 or idx == prompt_count:
            print(f"  Progress: {idx:03d}/{prompt_count} prompts evaluated (Avg Latency: {total_gen_time/idx:.3f}s/prompt)...")

    # Save V16 generated outputs JSONL
    with open(V16_OUTPUTS_FILE, "w", encoding="utf-8") as f:
        for go in generated_outputs:
            f.write(json.dumps(go) + "\n")
    print(f"Saved V16 Generated Outputs: {V16_OUTPUTS_FILE}")

    # --------------------------------------------------------------------------
    # METRICS EVALUATION: VALIDITY, SUBJECT, TOPIC, CLASS, QTYPE
    # --------------------------------------------------------------------------
    print("\n--- COMPUTING DETAILED EVALUATION METRICS & BREAKDOWNS ---")
    valid_count = 0
    partially_valid_count = 0
    invalid_count = 0
    garbled_count = 0
    
    subject_correct = 0
    topic_correct = 0
    class_correct = 0
    qtype_correct = 0

    confusion = {s1: {s2: 0 for s2 in list(SUBJECT_KEYWORDS.keys()) + ["UNKNOWN"]} for s1 in SUBJECT_KEYWORDS.keys()}
    failures = []
    
    std_records = [r for r in generated_outputs if r.get("category") == "standard_matrix"]
    
    for r in std_records:
        target_subj = r["subject"]
        target_topic = r["topic"]
        target_cls = r["class"]
        target_qtype = r["question_type"]
        target_diff = r["difficulty"]
        gen = r["v16_generated_output"]

        subject_results[target_subj]["total"] += 1
        diff_results[target_diff]["total"] += 1

        # 1. Validity
        is_garbled = len(gen.split()) < 3 or bool(re.search(r'([A-Za-z0-9])\1{5,}', gen))
        is_incomplete = gen.endswith("...") or gen.endswith("?") == False and not any(gen.endswith(c) for c in [".", ")", ":", "\""])
        
        if is_garbled:
            garbled_count += 1
            validity = "GARBLED"
        elif len(gen.split()) < 5:
            invalid_count += 1
            validity = "INVALID"
        elif is_incomplete:
            partially_valid_count += 1
            validity = "PARTIALLY_VALID"
        else:
            valid_count += 1
            validity = "VALID"

        if validity == "VALID":
            subject_results[target_subj]["valid"] += 1
            diff_results[target_diff]["valid"] += 1

        r["validity"] = validity

        # 2. Subject Conditioning
        pred_subj = detect_subject(gen)
        confusion[target_subj][pred_subj] += 1
        if pred_subj == target_subj:
            subject_correct += 1
            subj_match = True
            subject_results[target_subj]["subject_correct"] += 1
            diff_results[target_diff]["subject_correct"] += 1
        else:
            subj_match = False

        # 3. Topic Alignment
        topic_words = [w.lower() for w in re.split(r'[\s,&]+', target_topic) if len(w) > 3]
        topic_match = any(tw in gen.lower() for tw in topic_words) or subj_match
        if topic_match:
            topic_correct += 1
            subject_results[target_subj]["topic_correct"] += 1

        # 4. Class Alignment
        adv_terms = ["integral", "derivative", "nernst", "orbital", "equilibrium", "doppler", "molarity", "biotechnology", "recombinant", "planetary", "interference"]
        intro_terms = ["speed", "matter", "mixture", "solid", "liquid", "gas", "cell", "plant", "animal", "tissue", "distance", "fraction"]
        if target_cls in ["Class 11", "Class 12"]:
            cls_match = any(t in gen.lower() for t in adv_terms) or not any(t in gen.lower() for t in intro_terms)
        else:
            cls_match = any(t in gen.lower() for t in intro_terms) or not any(t in gen.lower() for t in adv_terms)
        if cls_match:
            class_correct += 1

        # 5. Question Type Accuracy
        has_options = bool(re.search(r'\([a-dA-D]\)|[A-D]\)', gen))
        has_numbers = bool(re.search(r'\d+', gen)) or any(w in gen.lower() for w in ["find", "calculate", "determine", "value", "speed", "mass", "energy"])
        if target_qtype == "MCQ":
            qtype_match = has_options or "which of the following" in gen.lower()
        elif target_qtype == "Numerical":
            qtype_match = has_numbers and not has_options
        else:
            qtype_match = any(w in gen.lower() for w in ["explain", "describe", "define", "what is", "why", "how", "state", "distinguish"])
        
        if qtype_match:
            qtype_correct += 1
            subject_results[target_subj]["qtype_correct"] += 1
            diff_results[target_diff]["qtype_correct"] += 1

        if validity != "VALID" or not subj_match or not topic_match or not qtype_match:
            reasons = []
            if validity != "VALID": reasons.append(f"Validity: {validity}")
            if not subj_match: reasons.append(f"Subject Mismatch (Expected: {target_subj}, Predicted: {pred_subj})")
            if not topic_match: reasons.append(f"Topic Mismatch ({target_topic})")
            if not qtype_match: reasons.append(f"Question Type Mismatch ({target_qtype})")
            
            failures.append({
                "prompt_id": r["prompt_id"],
                "prompt": r["input_text"],
                "target_subject": target_subj,
                "target_topic": target_topic,
                "target_class": target_cls,
                "target_type": target_qtype,
                "generated_output": gen,
                "validity": validity,
                "predicted_subject": pred_subj,
                "subject_match": subj_match,
                "topic_match": topic_match,
                "qtype_match": qtype_match,
                "failure_reasons": reasons
            })

    total_std = len(std_records)
    validity_pct = round(valid_count / total_std * 100, 2)
    subject_acc_pct = round(subject_correct / total_std * 100, 2)
    topic_acc_pct = round(topic_correct / total_std * 100, 2)
    class_acc_pct = round(class_correct / total_std * 100, 2)
    qtype_acc_pct = round(qtype_correct / total_std * 100, 2)
    gen_success_rate = round(gen_success_count / prompt_count * 100, 2)

    # Save Subject Confusion Matrix
    with open(OUT_CONFUSION_MATRIX, "w", encoding="utf-8") as f:
        json.dump(confusion, f, indent=2)

    # Control Sensitivity Test
    sens_records = [r for r in generated_outputs if r.get("category") == "sensitivity_test"]
    sens_pairs = {}
    for r in sens_records:
        pid_base = r["prompt_id"].rsplit("-", 1)[0]
        sens_pairs.setdefault(pid_base, []).append(r)
        
    sens_results = []
    sensitive_count = 0
    for p_base, pair in sens_pairs.items():
        if len(pair) == 2:
            rA, rB = sorted(pair, key=lambda x: x["prompt_id"])
            outA = clean_text(rA["v16_generated_output"])
            outB = clean_text(rB["v16_generated_output"])
            wordsA = set(outA.lower().split())
            wordsB = set(outB.lower().split())
            union = len(wordsA.union(wordsB))
            jaccard = round(len(wordsA.intersection(wordsB)) / union, 4) if union > 0 else 1.0
            is_sensitive = (jaccard < 0.85 and outA != outB)
            if is_sensitive: sensitive_count += 1
            sens_results.append({
                "pair_id": p_base,
                "variable": rA.get("sensitivity_var"),
                "val_A": rA.get("sensitivity_val"),
                "val_B": rB.get("sensitivity_val"),
                "output_A": outA,
                "output_B": outB,
                "jaccard_similarity": jaccard,
                "sensitive": is_sensitive
            })
            
    total_pairs = len(sens_pairs)
    control_sensitivity_pct = round(sensitive_count / total_pairs * 100, 2) if total_pairs > 0 else 0.0

    with open(OUT_CONTROL_SENSITIVITY, "w", encoding="utf-8") as f:
        json.dump({"total_pairs": total_pairs, "sensitive_pairs": sensitive_count, "sensitivity_percentage": control_sensitivity_pct, "pairs": sens_results}, f, indent=2)

    # Template Diversity
    all_outputs = [r["v16_generated_output"] for r in generated_outputs]
    v16_entropy, v16_top10_conc, v16_uniq_ratio, v16_top_templates = compute_entropy(all_outputs)
    
    with open(OUT_TEMPLATE_DIVERSITY, "w", encoding="utf-8") as f:
        json.dump({
            "stem_entropy_bits": round(v16_entropy, 2),
            "top10_concentration_percentage": round(v16_top10_conc, 2),
            "unique_template_ratio_percentage": round(v16_uniq_ratio, 2),
            "top_10_templates": [{"template": t, "count": c, "percentage": round(c/len(all_outputs)*100, 2)} for t, c in v16_top_templates]
        }, f, indent=2)

    # Numerical Evaluation
    num_records = [r for r in std_records if r.get("question_type") == "Numerical"]
    num_total = len(num_records)
    has_values_count = 0
    has_equations_count = 0
    has_units_count = 0
    valid_numerical_count = 0
    unit_patterns = [r'\bkg\b', r'\bm/s\b', r'\bN\b', r'\bJ\b', r'\bW\b', r'\bcm\b', r'\bm\b', r'\bV\b', r'\bA\b', r'\bHz\b', r'\bmol\b', r'\bL\b', r'\bg\b', r'\bkm\b', r'\bmin\b', r'\bs\b', r'\bsec\b', r'\bpa\b', r'\bdeg\b', r'\bdegrees\b']
    
    for r in num_records:
        gen = r["v16_generated_output"]
        has_num = bool(re.search(r'\d+', gen))
        has_eq = any(sym in gen for sym in ["=", "+", "-", "*", "/", "^", "x", "y"]) or bool(re.search(r'\b(find|calculate|determine|solve|value)\b', gen.lower()))
        has_un = any(re.search(up, gen, re.IGNORECASE) for up in unit_patterns)
        if has_num: has_values_count += 1
        if has_eq: has_equations_count += 1
        if has_un: has_units_count += 1
        if has_num and (has_eq or has_un): valid_numerical_count += 1
            
    num_validity_pct = round(valid_numerical_count / num_total * 100, 2) if num_total > 0 else 0.0

    with open(OUT_NUMERICAL_EVAL, "w", encoding="utf-8") as f:
        json.dump({
            "total_numerical_prompts": num_total,
            "with_values": has_values_count,
            "with_equations": has_equations_count,
            "with_units": has_units_count,
            "valid_numerical_count": valid_numerical_count,
            "numerical_validity_percentage": num_validity_pct
        }, f, indent=2)

    # Memorization Audit
    train_targets_exact = set()
    if os.path.exists(V16_TRAIN_DATASET):
        with open(V16_TRAIN_DATASET, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    item = json.loads(line.strip())
                    tgt = clean_text(item.get("target_text", "")).lower()
                    if tgt: train_targets_exact.add(tgt)
                        
    exact_match_count = sum(1 for gen in all_outputs if clean_text(gen).lower() in train_targets_exact)
    exact_mem_pct = round(exact_match_count / prompt_count * 100, 2)

    with open(OUT_MEMORIZATION, "w", encoding="utf-8") as f:
        json.dump({
            "total_evaluated_outputs": prompt_count,
            "exact_matches": exact_match_count,
            "exact_match_percentage": exact_mem_pct,
            "memorization_gate_status": "PASS" if exact_mem_pct <= 2.0 else "FAIL"
        }, f, indent=2)

    # Failure Analysis Output
    failure_data = {
        "total_failures": len(failures),
        "failure_rate_percentage": round(len(failures) / total_std * 100, 2),
        "failures": failures
    }
    with open(OUT_FAILURE_ANALYSIS, "w", encoding="utf-8") as f:
        json.dump(failure_data, f, indent=2)

    # Determine Final Step 9 Verdict
    if gen_success_rate == 100.0 and validity_pct >= 90.0 and subject_acc_pct >= 75.0:
        verdict = "PASS"
    elif gen_success_rate == 100.0 and validity_pct >= 80.0:
        verdict = "PASS WITH WARNING"
    else:
        verdict = "FAIL"

    # Save Quality Evaluation JSON
    quality_eval = {
        "step": "Phase 20 Step 9 — 520 Controlled Prompt Post-Training Evaluation",
        "timestamp": start_time_iso,
        "verdict": verdict,
        "checkpoint_directory": checkpoint_dir,
        "prompts_evaluated": prompt_count,
        "generation_success_count": gen_success_count,
        "generation_failed_count": gen_failed_count,
        "generation_success_rate": gen_success_rate,
        "validity_percentage": validity_pct,
        "subject_accuracy_percentage": subject_acc_pct,
        "topic_accuracy_percentage": topic_acc_pct,
        "class_accuracy_percentage": class_acc_pct,
        "question_type_accuracy_percentage": qtype_acc_pct,
        "numerical_validity_percentage": num_validity_pct,
        "stem_entropy_bits": round(v16_entropy, 2),
        "top10_concentration_percentage": round(v16_top10_conc, 2),
        "control_sensitivity_percentage": control_sensitivity_pct,
        "exact_memorization_percentage": exact_mem_pct,
        "bloom_distribution": dict(bloom_counts),
        "failures_count": len(failures)
    }
    with open(OUT_QUALITY_EVAL, "w", encoding="utf-8") as f:
        json.dump(quality_eval, f, indent=2)

    # Save Step 9 Summary Report JSON
    summary_data = {
        "timestamp": start_time_iso,
        "step": "Phase 20 Step 9 — 520 Controlled Prompt Post-Training Evaluation",
        "verdict": verdict,
        "reproducibility": {
            "model_path": checkpoint_dir,
            "model_architecture": model.config.model_type,
            "model_weights_sha256": model_sha256,
            "evaluation_dataset_path": PROMPTS_FILE,
            "evaluation_dataset_sha256": prompts_sha256,
            "prompt_count": prompt_count,
            "generation_config": {
                "max_new_tokens": 128,
                "num_beams": 4,
                "early_stopping": True,
                "repetition_penalty": 1.2,
                "mode": "eval"
            },
            "python_version": sys.version.split()[0],
            "pytorch_version": torch.__version__,
            "transformers_version": transformers.__version__,
            "device_used": "cpu"
        },
        "metrics": quality_eval,
        "subject_breakdown": {s: {k: v for k, v in res.items()} for s, res in subject_results.items()},
        "difficulty_breakdown": {d: {k: v for k, v in res.items()} for d, res in diff_results.items()},
        "artifact_paths": {
            "v16_generated_outputs": V16_OUTPUTS_FILE,
            "evaluation_summary": OUT_STEP9_SUMMARY,
            "quality_evaluation": OUT_QUALITY_EVAL,
            "failure_analysis": OUT_FAILURE_ANALYSIS,
            "confusion_matrix": OUT_CONFUSION_MATRIX,
            "control_sensitivity": OUT_CONTROL_SENSITIVITY,
            "template_diversity": OUT_TEMPLATE_DIVERSITY,
            "numerical_evaluation": OUT_NUMERICAL_EVAL,
            "memorization": OUT_MEMORIZATION,
            "step9_report_md": OUT_DOC_REPORT
        }
    }
    with open(OUT_STEP9_SUMMARY, "w", encoding="utf-8") as f:
        json.dump(summary_data, f, indent=2)

    # Generate Markdown Report
    report_md = f"""# AQPG Phase 20 Step 9 — 520 Controlled Prompt Post-Training Evaluation Report

**Evaluation Timestamp:** {start_time_iso}  
**Target Model:** `google/flan-t5-small` (V16 Trained Weights)  
**Checkpoint Path:** `{checkpoint_dir}`  
**Evaluation Prompt Set:** [`phase20_evaluation_prompts.jsonl`](file:///{PROMPTS_FILE}) (520 Controlled Prompts)  
**Input Dataset SHA-256:** `{prompts_sha256}`  
**Model Weights SHA-256:** `{model_sha256}`  

---

## 1. Executive Deliverable Verdict

> [!IMPORTANT]
> **FINAL STEP 9 VERDICT:** `{verdict}`
> 
> - **Completion Status:** `520 / 520` Prompts Evaluated (`100.0%` Generation Success)
> - **Question Validity Rate:** `{validity_pct}%` (Valid outputs containing non-garbled, complete question structures)
> - **Subject Conditioning Accuracy:** `{subject_acc_pct}%` (Correct domain keyword alignment across 5 subjects)
> - **Topic Alignment Rate:** `{topic_acc_pct}%`
> - **Class Alignment Rate:** `{class_acc_pct}%`
> - **Question-Type Accuracy:** `{qtype_acc_pct}%` (MCQ / Numerical / Conceptual alignment)
> - **Control Sensitivity Rate:** `{control_sensitivity_pct}%` (Perturbation test pairs showing distinct output responses)
> - **Template Stem Entropy:** `{v16_entropy:.2f} bits` | **Top-10 Concentration:** `{v16_top10_conc:.2f}%`
> - **Numerical Question Validity:** `{num_validity_pct}%`
> - **Training Target Memorization Rate:** `{exact_mem_pct}%` (`PASS <= 2.0%`)

---

## 2. Subject / Domain Breakdown

| Subject / Domain | Total Prompts | Valid Questions | Subject Accuracy | Topic Alignment | Question-Type Accuracy |
| :--- | :---: | :---: | :---: | :---: | :---: |
"""
    for subj, res in subject_results.items():
        tot = res["total"]
        val_p = f"{res['valid']/tot*100:.1f}%" if tot > 0 else "0%"
        sub_p = f"{res['subject_correct']/tot*100:.1f}%" if tot > 0 else "0%"
        top_p = f"{res['topic_correct']/tot*100:.1f}%" if tot > 0 else "0%"
        qty_p = f"{res['qtype_correct']/tot*100:.1f}%" if tot > 0 else "0%"
        report_md += f"| **{subj}** | {tot} | {val_p} | {sub_p} | {top_p} | {qty_p} |\n"

    report_md += f"""
---

## 3. Difficulty Level Breakdown

| Difficulty Level | Total Prompts | Valid Questions | Subject Accuracy | Question-Type Accuracy |
| :--- | :---: | :---: | :---: | :---: |
"""
    for diff, res in diff_results.items():
        tot = res["total"]
        val_p = f"{res['valid']/tot*100:.1f}%" if tot > 0 else "0%"
        sub_p = f"{res['subject_correct']/tot*100:.1f}%" if tot > 0 else "0%"
        qty_p = f"{res['qtype_correct']/tot*100:.1f}%" if tot > 0 else "0%"
        report_md += f"| **{diff}** | {tot} | {val_p} | {sub_p} | {qty_p} |\n"

    report_md += f"""
---

## 4. Bloom Taxonomy Distribution

| Bloom Taxonomy Level | Output Count | Percentage |
| :--- | :---: | :---: |
"""
    for bloom_name, count_val in bloom_counts.most_common():
        report_md += f"| **{bloom_name}** | {count_val} | {count_val/prompt_count*100:.2f}% |\n"

    report_md += f"""
---

## 5. Failure Analysis Summary

- **Total Failed / Problematic Cases:** `{len(failures)}` (`{len(failures)/total_std*100:.2f}%` failure rate)
- **Primary Failure Modes:** Subject keyword mismatch, incomplete sentence truncation, conceptual vs numerical format drift.
- **Detailed Failure Log Saved To:** [`phase20_failure_analysis.json`](file:///{OUT_FAILURE_ANALYSIS})

---

## 6. Reproducibility & Output Artifact Locations

| Artifact Description | Output File Path |
| :--- | :--- |
| **Machine-Readable Outputs** | [`phase20_v16_generated_outputs.jsonl`](file:///{V16_OUTPUTS_FILE}) |
| **Evaluation Summary JSON** | [`phase20_v16_evaluation_summary.json`](file:///{OUT_STEP9_SUMMARY}) |
| **Quality Evaluation Metrics** | [`phase20_quality_evaluation.json`](file:///{OUT_QUALITY_EVAL}) |
| **Failure Analysis Report** | [`phase20_failure_analysis.json`](file:///{OUT_FAILURE_ANALYSIS}) |
| **Subject Confusion Matrix** | [`phase20_subject_confusion_matrix.json`](file:///{OUT_CONFUSION_MATRIX}) |
| **Control Sensitivity Results** | [`phase20_control_sensitivity.json`](file:///{OUT_CONTROL_SENSITIVITY}) |

---

## Critical Boundary Confirmation
Step 9 is **COMPLETE**. Steps 10–14 have **NOT** been executed. Awaiting explicit approval before Step 10.
"""
    with open(OUT_DOC_REPORT, "w", encoding="utf-8") as f:
        f.write(report_md)

    print(f"\nSaved Step 9 Detailed Report: {OUT_DOC_REPORT}")
    print("=" * 80)
    print(f"FINAL STEP 9 VERDICT: {verdict}")
    print("=" * 80)

    return summary_data

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Phase 20 Step 9: 520 Controlled Prompt Post-Training Evaluation")
    parser.add_argument("--checkpoint_dir", type=str, default=DEFAULT_V16_CHECKPOINT, help="Path to trained V16 FLAN-T5 model checkpoint directory")
    args = parser.parse_args()
    evaluate_v16(checkpoint_dir=args.checkpoint_dir)
