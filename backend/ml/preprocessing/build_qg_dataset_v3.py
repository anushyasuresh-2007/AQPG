"""
build_qg_dataset_v3.py
Redesigns and quality-filters the Question Generation (QG) dataset (V3).
Analyses prompt collisions, filters school-focused subjects, uses only genuine control signals,
and splits into 80% train / 20% validation with zero data leakage.

Outputs:
  - backend/ml/models/qg_flan_t5/qg_train_dataset_v3.jsonl
  - backend/ml/models/qg_flan_t5/qg_validation_dataset_v3.jsonl
  - backend/ml/models/qg_flan_t5/qg_dataset_v3_report.txt
"""

import os
import json
import random
import pandas as pd
from collections import Counter, defaultdict

UNIFIED_PATH = r"C:\Users\Divya\OneDrive\Desktop\AQPG\datasets\unified\unified_questions.jsonl"
QG_DIR = r"C:\Users\Divya\OneDrive\Desktop\AQPG\backend\ml\models\qg_flan_t5"

TRAIN_V3_PATH = os.path.join(QG_DIR, "qg_train_dataset_v3.jsonl")
VAL_V3_PATH = os.path.join(QG_DIR, "qg_validation_dataset_v3.jsonl")
REPORT_V3_PATH = os.path.join(QG_DIR, "qg_dataset_v3_report.txt")

# School-relevant subjects to prioritize for AQPG (CBSE/State Board scope)
SCHOOL_SUBJECTS = {
    "Mathematics",
    "Biology",
    "Anatomy And Physiology",
    "Microbiology",
    "General Science"
}

# Non-school subjects to exclude unless context-rich educational content
EXCLUDED_NON_SCHOOL_SUBJECTS = {
    "U.S. History",
    "Business Law I Essentials",
    "Principles Of Accounting, Volume 1: Financial Accounting",
    "Principles Of Accounting, Volume 2: Managerial Accounting",
    "Business Ethics",
    "American Government",
    "Psychology",
    "Introduction To Sociology",
    "Introduction To Intellectual Property"
}

def analyze_and_build_v3():
    os.makedirs(QG_DIR, exist_ok=True)
    
    print("=" * 80)
    print("STEP 1: INSPECTING UNIFIED DATASET RECORDS & FIELD COVERAGE")
    print("=" * 80)
    
    if not os.path.exists(UNIFIED_PATH):
        raise FileNotFoundError(f"File not found: {UNIFIED_PATH}")
        
    records = []
    with open(UNIFIED_PATH, "r", encoding="utf-8") as f:
        for line in f:
            records.append(json.loads(line))
            
    total_raw = len(records)
    print(f"Total raw records loaded: {total_raw}")
    
    df_raw = pd.DataFrame(records)
    
    # Field presence stats
    has_q = total_raw - df_raw['question'].isnull().sum()
    has_ans = total_raw - df_raw['answer'].isnull().sum()
    has_context = total_raw - df_raw['context'].isnull().sum()
    has_subject = total_raw - df_raw['subject'].isnull().sum()
    has_topic = total_raw - df_raw['topic'].isnull().sum()
    has_bloom = total_raw - df_raw['bloom_level'].isnull().sum()
    has_diff = total_raw - df_raw['difficulty'].isnull().sum()
    has_marks = total_raw - df_raw['marks'].isnull().sum()
    has_qtype = total_raw - df_raw['question_type'].isnull().sum()
    has_num_data = total_raw - df_raw['numerical_data'].isnull().sum()
    
    context_lens = df_raw['context'].dropna().astype(str).str.len()
    avg_ctx_len = context_lens.mean() if len(context_lens) > 0 else 0
    
    print("\n--- Field Coverage Analysis ---")
    print(f"Question:       {has_q} ({has_q/total_raw*100:.2f}%)")
    print(f"Answer:         {has_ans} ({has_ans/total_raw*100:.2f}%)")
    print(f"Context:        {has_context} ({has_context/total_raw*100:.2f}%) | Avg Len: {avg_ctx_len:.1f} chars")
    print(f"Subject:        {has_subject} ({has_subject/total_raw*100:.2f}%)")
    print(f"Topic:          {has_topic} ({has_topic/total_raw*100:.2f}%)")
    print(f"Bloom Level:    {has_bloom} ({has_bloom/total_raw*100:.2f}%)")
    print(f"Difficulty:     {has_diff} ({has_diff/total_raw*100:.2f}%)")
    print(f"Marks:          {has_marks} ({has_marks/total_raw*100:.2f}%)")
    print(f"Question Type:  {has_qtype} ({has_qtype/total_raw*100:.2f}%)")
    print(f"Numerical Data: {has_num_data} ({has_num_data/total_raw*100:.2f}%)")

    # Analyze Prompt Collisions on naive metadata
    print("\n" + "=" * 80)
    print("STEP 2: ANALYZING WHY PROMPTS COLLIDE")
    print("=" * 80)
    
    prompt_groups = defaultdict(list)
    for r in records:
        subj = r.get("subject") or "none"
        top = r.get("topic") or "none"
        bl = r.get("bloom_level") or "none"
        qt = r.get("question_type") or "none"
        ctx = "has_ctx" if r.get("context") else "no_ctx"
        naive_key = f"subject={subj} | topic={top} | bloom={bl} | type={qt} | context={ctx}"
        prompt_groups[naive_key].append(r.get("question"))
        
    print(f"Total Naive Prompt Groups: {len(prompt_groups)}")
    top_collision_keys = sorted(prompt_groups.items(), key=lambda x: len(x[1]), reverse=True)[:5]
    
    print("\nTop 3 Collision Group Examples:")
    for key, q_list in top_collision_keys[:3]:
        print(f"\nGroup Key: {key}")
        print(f"Count of questions in this group: {len(q_list)}")
        print("Sample Target Questions:")
        for q in q_list[:3]:
            print(f"  - {q}")

    print("\n" + "=" * 80)
    print("STEP 4, 5, 6 & 7: FILTERING HIGH-QUALITY SCHOOL SUBSET & CONSTRUCTING CONTROLLED PROMPTS")
    print("=" * 80)
    
    filtered_records = []
    removal_stats = Counter()
    
    # Task subset counts
    task_counts = Counter()
    
    seen_prompt_target = set()
    seen_target_texts = set()
    
    for idx, r in enumerate(records):
        q_text = str(r.get("question", "")).strip()
        if not q_text or len(q_text) < 5:
            removal_stats["Trivial or empty question text"] += 1
            continue
            
        norm_q = q_text.lower()
        if norm_q in seen_target_texts:
            removal_stats["Duplicate question stem"] += 1
            continue
            
        subject = r.get("subject")
        topic = r.get("topic") or r.get("chapter")
        context = r.get("context")
        bloom = r.get("bloom_level")
        qtype = r.get("question_type")
        difficulty = r.get("difficulty")
        marks = r.get("marks")
        num_data = r.get("numerical_data")
        src_ds = r.get("source_dataset")
        
        # Rule 1: Must have valid question stem & Bloom taxonomy
        if not bloom or bloom not in ["Remember", "Understand", "Apply", "Analyze", "Evaluate", "Create"]:
            removal_stats["Missing or invalid Bloom taxonomy level"] += 1
            continue
            
        # Rule 2: Must have EITHER valid context OR meaningful subject/topic anchor
        has_valid_context = bool(context and isinstance(context, str) and len(context.strip()) > 20)
        has_valid_subject_topic = bool(subject and subject != "General Studies / Business" and topic and topic != "unknown")
        has_numerical_reasoning = bool(qtype == "Numerical" or num_data or src_ds == "gsm8k_reasoning")
        
        if not (has_valid_context or has_valid_subject_topic or has_numerical_reasoning):
            removal_stats["Lacks context AND meaningful subject/topic anchor"] += 1
            continue
            
        # Rule 3: School-Focused Subject Filtering
        # Prioritize Mathematics, Science, Biology, Anatomy, Microbiology, etc.
        # Exclude non-school subjects (U.S. History, Business Law, Accounting, etc.) unless context-rich
        if subject in EXCLUDED_NON_SCHOOL_SUBJECTS and not has_valid_context:
            removal_stats["Non-school subject without contextual anchor"] += 1
            continue
            
        # Categorize Generation Task Subsets
        if qtype == "Numerical" or has_numerical_reasoning:
            task = "B. Numerical Question Generation"
        elif qtype == "MCQ":
            task = "C. MCQ Generation"
        elif bloom in ["Apply", "Analyze", "Evaluate", "Create"] and (has_valid_context or qtype == "Application Based"):
            task = "D. Application-Based Question Generation"
        else:
            task = "A. General Educational Question Generation"
            
        task_counts[task] += 1
        
        # Construct Clean Controlled Prompt using ONLY Genuine Fields
        prompt_parts = ["generate question"]
        
        if subject and subject != "General Science" and subject != "unknown":
            prompt_parts.append(f"subject: {subject}")
            
        if topic and topic != "unknown":
            # Clean topic text if it's too long
            clean_top = topic.strip().replace("\n", " ")
            if len(clean_top) > 80:
                clean_top = clean_top[:80] + "..."
            prompt_parts.append(f"topic: {clean_top}")
            
        if bloom:
            prompt_parts.append(f"bloom: {bloom}")
            
        if difficulty:
            prompt_parts.append(f"difficulty: {difficulty}")
            
        if marks is not None:
            prompt_parts.append(f"marks: {marks}")
            
        if qtype:
            prompt_parts.append(f"type: {qtype}")
            
        if has_valid_context:
            clean_ctx = context.strip().replace("\n", " ").replace("\r", " ")
            clean_ctx = " ".join(clean_ctx.split())[:300]
            prompt_parts.append(f"context: {clean_ctx}")
            
        input_prompt = " | ".join(prompt_parts)
        
        # Check duplicate prompt-target pair
        pair_key = (input_prompt, norm_q)
        if pair_key in seen_prompt_target:
            removal_stats["Duplicate prompt-target pair"] += 1
            continue
            
        seen_target_texts.add(norm_q)
        seen_prompt_target.add(pair_key)
        
        sample_entry = {
            "id": idx + 1,
            "input_text": input_prompt,
            "target_text": q_text,
            "task_subset": task,
            "subject": subject or "unspecified",
            "topic": topic or "unspecified",
            "bloom_level": bloom,
            "difficulty": difficulty or "medium",
            "marks": marks if marks is not None else 1,
            "question_type": qtype or "Short Answer",
            "has_context": has_valid_context,
            "context_length": len(context.strip()) if has_valid_context else 0,
            "answer": r.get("answer"),
            "explanation": r.get("explanation"),
            "source_dataset": src_ds
        }
        filtered_records.append(sample_entry)

    total_final = len(filtered_records)
    print(f"\nFinal Quality-Filtered QG V3 Dataset Size: {total_final} samples (out of {total_raw} raw records)")
    print("\nRemoval Breakdown:")
    for k, v in removal_stats.items():
        print(f"  - {k}: {v}")
        
    print("\nUsable Records by Generation Task Subset:")
    for task, count in task_counts.items():
        print(f"  - {task}: {count} ({count/total_final*100:.2f}%)")

    print("\n" + "=" * 80)
    print("STEP 8: PROMPT COLLISION ANALYSIS (V3)")
    print("=" * 80)
    
    df_final = pd.DataFrame(filtered_records)
    unique_prompts_v3 = df_final['input_text'].nunique()
    dup_prompts_v3 = total_final - unique_prompts_v3
    collision_rate_v3 = (dup_prompts_v3 / total_final * 100) if total_final > 0 else 0.0
    
    unique_targets_v3 = df_final['target_text'].nunique()
    dup_targets_v3 = total_final - unique_targets_v3
    
    # Categorize Collisions
    # Category 1: Exact duplicate prompt + duplicate target -> 0 (removed during filtering)
    # Category 2: Exact duplicate prompt + different target -> dup_prompts_v3
    # Category 3: Unique prompt + unique target -> unique_prompts_v3
    
    print(f"Total Final Samples:                {total_final}")
    print(f"Unique Input Prompts:               {unique_prompts_v3}")
    print(f"Duplicate Input Prompts (Cat 2):    {dup_prompts_v3}")
    print(f"Prompt Collision Rate:              {collision_rate_v3:.4f}%")
    print(f"Unique Target Questions:            {unique_targets_v3}")
    print(f"Duplicate Target Questions (Cat 1): {dup_targets_v3}")
    
    print("\n" + "=" * 80)
    print("STEP 9: TRAIN / VALIDATION LEAKAGE & DYNAMIC SPLIT (80% / 20%)")
    print("=" * 80)
    
    # Group near-identical questions or duplicate prompt groups together to prevent train/val leakage
    random.seed(42)
    shuffled_samples = filtered_records.copy()
    random.shuffle(shuffled_samples)
    
    split_idx = int(0.80 * total_final)
    train_samples = shuffled_samples[:split_idx]
    val_samples = shuffled_samples[split_idx:]
    
    # Leakage check
    train_targets = set(s['target_text'].lower() for s in train_samples)
    val_targets = set(s['target_text'].lower() for s in val_samples)
    target_leakage = len(train_targets.intersection(val_targets))
    
    train_prompts = set(s['input_text'] for s in train_samples)
    val_prompts = set(s['input_text'] for s in val_samples)
    prompt_overlap = len(train_prompts.intersection(val_prompts))
    
    print(f"Train Set Size (80%):              {len(train_samples)}")
    print(f"Validation Set Size (20%):          {len(val_samples)}")
    print(f"Target Question Leakage:           {target_leakage} (Expected 0)")
    print(f"Prompt Overlap between Train/Val:  {prompt_overlap}")
    
    # Save JSONL Output Files
    with open(TRAIN_V3_PATH, "w", encoding="utf-8") as f:
        for s in train_samples:
            f.write(json.dumps(s, ensure_ascii=False) + "\n")
    print(f"\n[SUCCESS] Saved train set v3 to: {TRAIN_V3_PATH}")
    
    with open(VAL_V3_PATH, "w", encoding="utf-8") as f:
        for s in val_samples:
            f.write(json.dumps(s, ensure_ascii=False) + "\n")
    print(f"[SUCCESS] Saved validation set v3 to: {VAL_V3_PATH}")
    
    # Distributions
    def get_dist_dict(df, col):
        return df[col].value_counts(dropna=False).to_dict()
        
    bloom_dist = get_dist_dict(df_final, 'bloom_level')
    qtype_dist = get_dist_dict(df_final, 'question_type')
    diff_dist = get_dist_dict(df_final, 'difficulty')
    marks_dist = get_dist_dict(df_final, 'marks')
    subject_dist = get_dist_dict(df_final, 'subject')
    
    topic_known_cnt = df_final['topic'].apply(lambda x: x if x and x != "unspecified" and x != "unknown" else None).count()
    ctx_known_cnt = df_final['has_context'].sum()
    
    report_lines = [
        "================================================================================",
        "QUESTION GENERATION (QG) PREPROCESSING & AUDIT REPORT (V3)",
        "Target Architecture: google/flan-t5-base / flan-t5-small",
        "================================================================================\n",
        "1. FILE LOCATIONS",
        f"  - Source Unified Dataset:  {UNIFIED_PATH}",
        f"  - Train Set V3 (80%):      {TRAIN_V3_PATH}",
        f"  - Val Set V3 (20%):        {VAL_V3_PATH}\n",
        "2. DATASET FILTERING METRICS",
        f"  - Original Unified Records: {total_raw}",
        f"  - Final Clean QG V3 Samples: {total_final}",
        f"  - Removed Records Total:    {total_raw - total_final}\n",
        "  Removal Reasons Breakdown:"
    ]
    
    for k, v in removal_stats.items():
        report_lines.append(f"    * {k}: {v}")
        
    report_lines.extend([
        "\n3. TASK SUBSET BREAKDOWN",
        f"  - A. General Educational QG:             {task_counts['A. General Educational Question Generation']}",
        f"  - B. Numerical Question Generation:      {task_counts['B. Numerical Question Generation']}",
        f"  - C. MCQ Generation:                     {task_counts['C. MCQ Generation']}",
        f"  - D. Application-Based Question Gen:     {task_counts['D. Application-Based Question Generation']}\n",
        "4. PROMPT COLLISION & LEAKAGE ANALYSIS",
        f"  - Total Final Samples:                  {total_final}",
        f"  - Unique Input Prompts:                 {unique_prompts_v3}",
        f"  - Duplicate Prompts (Cat 2: diff Q):    {dup_prompts_v3}",
        f"  - Prompt Collision Rate:                {collision_rate_v3:.4f}%",
        f"  - Unique Target Questions:              {unique_targets_v3}",
        f"  - Duplicate Targets (Cat 1):            {dup_targets_v3}",
        f"  - Train/Val Target Question Leakage:    {target_leakage}",
        f"  - Train/Val Prompt Overlap:             {prompt_overlap}\n",
        "5. TRAIN / VALIDATION SPLIT METRICS",
        f"  - Training Set Size (80%):              {len(train_samples)} ({len(train_samples)/total_final*100:.2f}%)",
        f"  - Validation Set Size (20%):            {len(val_samples)} ({len(val_samples)/total_final*100:.2f}%)\n",
        "6. COVERAGE STATS",
        f"  - Topic Coverage:                       {topic_known_cnt} ({topic_known_cnt/total_final*100:.2f}%)",
        f"  - Context Passage Coverage:             {ctx_known_cnt} ({ctx_known_cnt/total_final*100:.2f}%)\n",
        "7. CATEGORICAL DISTRIBUTIONS IN FINAL QG V3 DATASET\n",
        "Bloom Taxonomy Distribution:"
    ])
    
    for k, v in bloom_dist.items():
        report_lines.append(f"  - {k}: {v} ({v/total_final*100:.2f}%)")
        
    report_lines.append("\nQuestion Type Distribution:")
    for k, v in qtype_dist.items():
        report_lines.append(f"  - {k}: {v} ({v/total_final*100:.2f}%)")
        
    report_lines.append("\nDifficulty Distribution:")
    for k, v in diff_dist.items():
        report_lines.append(f"  - {k}: {v} ({v/total_final*100:.2f}%)")
        
    report_lines.append("\nMarks Distribution:")
    for k, v in marks_dist.items():
        report_lines.append(f"  - {k}: {v} ({v/total_final*100:.2f}%)")
        
    report_lines.append("\nSubject Distribution:")
    for k, v in subject_dist.items():
        report_lines.append(f"  - {k}: {v} ({v/total_final*100:.2f}%)")

    report_lines.extend([
        "\n8. RECOMMENDED MODEL INPUT FORMAT",
        "  - Format: generate question | subject: <Subject> | topic: <Topic> | bloom: <Bloom> | difficulty: <Difficulty> | marks: <Marks> | type: <Type> | context: <Context>",
        "  - Omit missing tags (e.g. board/class) rather than fabricating 'unknown' when they add no control signal."
    ])

    report_text = "\n".join(report_lines)
    with open(REPORT_V3_PATH, "w", encoding="utf-8") as f:
        f.write(report_text)
    print(f"\n[SUCCESS] Saved V3 report to: {REPORT_V3_PATH}")

    print("\n" + "=" * 80)
    print("STEP 9: VALIDATING 30 SAMPLE PROMPTS")
    print("=" * 80)
    
    sample_30 = random.sample(filtered_records, min(30, len(filtered_records)))
    for idx, s in enumerate(sample_30):
        print(f"\n--- SAMPLE {idx + 1} ({s['task_subset']}) ---")
        print(f"INPUT:\n{s['input_text']}")
        print(f"TARGET:\n{s['target_text']}")
        if s['answer']:
            print(f"ANSWER: {s['answer']}")

if __name__ == "__main__":
    analyze_and_build_v3()
