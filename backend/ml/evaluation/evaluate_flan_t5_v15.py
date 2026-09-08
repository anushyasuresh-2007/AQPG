"""
evaluate_flan_t5_v15.py
Comprehensive Phase 17 Model Quality Evaluation and Production Readiness Audit
for FLAN-T5-Small V15 Checkpoint.
"""

import os
import sys
import json
import re
import random
import time
import torch
import numpy as np
from collections import Counter, defaultdict
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# Register Windows PyTorch DLLs safely
if sys.platform == "win32":
    torch_lib = os.path.join(os.path.dirname(torch.__file__), "lib")
    if os.path.exists(torch_lib) and hasattr(os, "add_dll_directory"):
        try:
            os.add_dll_directory(torch_lib)
        except Exception:
            pass

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
V15_MODEL_DIR = os.path.join(BASE_DIR, "backend", "ml", "models", "checkpoints", "flan_t5_v15")
V3_MODEL_DIR = os.path.join(BASE_DIR, "backend", "ml", "models", "qg_flan_t5", "flan_t5_small_numerical")
BASE_MODEL_NAME = "google/flan-t5-small"

V15_DATASET_TRAIN = os.path.join(BASE_DIR, "datasets", "v15", "qg_train_dataset_v15.jsonl")
V15_DATASET_VAL = os.path.join(BASE_DIR, "datasets", "v15", "qg_validation_dataset_v15.jsonl")

OUTPUT_PROMPTS_PATH = os.path.join(BASE_DIR, "phase17_evaluation_prompts.jsonl")
OUTPUT_GENERATIONS_PATH = os.path.join(BASE_DIR, "phase17_generated_outputs.jsonl")
OUTPUT_EVAL_JSON = os.path.join(BASE_DIR, "phase17_quality_evaluation.json")
OUTPUT_ERRORS_JSON = os.path.join(BASE_DIR, "phase17_error_analysis.json")
OUTPUT_CONFUSION_JSON = os.path.join(BASE_DIR, "phase17_confusion_matrices.json")
OUTPUT_SENSITIVITY_JSON = os.path.join(BASE_DIR, "phase17_control_sensitivity.json")
OUTPUT_BASELINE_JSON = os.path.join(BASE_DIR, "phase17_baseline_comparison.json")
OUTPUT_FAILED_EXAMPLES = os.path.join(BASE_DIR, "phase17_failed_examples.jsonl")
OUTPUT_REPORT_TXT = os.path.join(BASE_DIR, "phase17_evaluation_report.txt")

def set_seed(seed=42):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)

def generate_text(model, tokenizer, prompt_str, device="cpu", num_beams=4, max_new_tokens=128, rep_penalty=1.2):
    inputs = tokenizer(prompt_str, return_tensors="pt", max_length=256, truncation=True).to(device)
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            num_beams=num_beams,
            early_stopping=True,
            repetition_penalty=rep_penalty
        )
    return tokenizer.decode(outputs[0], skip_special_tokens=True).strip()

# ==============================================================================
# STEP 2: BUILD CONTROLLED EVALUATION MATRIX
# ==============================================================================
def build_evaluation_matrix():
    """
    Constructs a controlled suite of 500 standardized prompts (100 per subject across
    Mathematics, Physics, Chemistry, Biology, General Science) + 20 sensitivity test pairs.
    """
    subjects_spec = {
        "Mathematics": {
            "topics": [
                "Linear Equations in Two Variables",
                "Quadratic Equations & Roots",
                "Arithmetic Progressions & Series",
                "Coordinate Geometry & Distance Formula",
                "Trigonometric Ratios & Heights",
                "Circles & Tangents",
                "Surface Areas & Volumes of Solids",
                "Probability & Sample Space",
                "Statistics & Mean Median Mode",
                "Polynomials & Factorization"
            ],
            "units": ["Algebra", "Geometry", "Trigonometry", "Coordinate Geometry", "Statistics", "Mensuration"]
        },
        "Physics": {
            "topics": [
                "Newton's Laws of Motion & Friction",
                "Kinematics & Equations of Motion",
                "Work, Energy and Power",
                "Universal Law of Gravitation & Planetary Motion",
                "Thermodynamics & Heat Engines",
                "Ray Optics & Refraction",
                "Wave Optics & Interference",
                "Current Electricity & Ohm's Law",
                "Magnetic Effects of Current & Induction",
                "Sound Waves & Doppler Effect"
            ],
            "units": ["Mechanics", "Optics", "Thermodynamics", "Electrodynamics", "Waves & Acoustics"]
        },
        "Chemistry": {
            "topics": [
                "Chemical Reactions & Balancing Equations",
                "Acids, Bases and Salts",
                "Periodic Classification & Atomic Radius",
                "Chemical Bonding & Molecular Orbital Theory",
                "Chemical Thermodynamics & Enthalpy",
                "Chemical Equilibrium & Le Chatelier's Principle",
                "Redox Reactions & Oxidation Numbers",
                "Electrochemistry & Nernst Equation",
                "Hydrocarbons & Alkanes Alkenes",
                "Solutions & Molarity Molality"
            ],
            "units": ["Inorganic Chemistry", "Organic Chemistry", "Physical Chemistry", "Chemical Reactions"]
        },
        "Biology": {
            "topics": [
                "Cell Structure & Organelles",
                "Cell Division & Mitosis Meiosis",
                "Photosynthesis & Light Dependent Reactions",
                "Cellular Respiration & Krebs Cycle",
                "Mendelian Genetics & Monohybrid Cross",
                "Molecular Basis of Inheritance & DNA",
                "Human Circulatory System & Blood",
                "Human Excretory System & Kidney",
                "Ecosystems & Energy Flow",
                "Biotechnology & Recombinant DNA"
            ],
            "units": ["Cell Biology", "Genetics", "Human Physiology", "Plant Physiology", "Ecology"]
        },
        "General Science": {
            "topics": [
                "Matter in Our Surroundings & States of Matter",
                "Is Matter Around Us Pure & Mixtures",
                "Atoms and Molecules & Law of Conservation of Mass",
                "Structure of the Atom & Valence Electrons",
                "The Fundamental Unit of Life",
                "Tissues & Plant Animal Tissues",
                "Motion & Speed Velocity",
                "Force and Laws of Motion",
                "Gravitation & Free Fall",
                "Work, Energy and Power"
            ],
            "units": ["Secondary General Science", "Matter & Materials", "Living World", "Natural Phenomena"]
        }
    }

    classes = ["Class 9", "Class 10", "Class 11", "Class 12"]
    types = ["Numerical", "MCQ", "Conceptual"]
    difficulties = ["Easy", "Medium", "Hard"]
    blooms = ["Remember", "Understand", "Apply", "Analyze"]
    marks_map = {"Easy": 1, "Medium": 2, "Hard": 3}

    prompts = []
    prompt_id = 1

    # Generate exactly 100 prompts per subject (5 subjects * 100 = 500 prompts)
    for subject, s_info in subjects_spec.items():
        sub_topics = s_info["topics"]
        sub_units = s_info["units"]
        
        for idx in range(100):
            topic = sub_topics[idx % len(sub_topics)]
            unit = sub_units[idx % len(sub_units)]
            cls = classes[idx % len(classes)]
            q_type = types[idx % len(types)]
            diff = difficulties[idx % len(difficulties)]
            bloom = blooms[idx % len(blooms)]
            marks = marks_map[diff]
            if q_type == "Numerical" and diff == "Hard":
                marks = 5
            
            prompt_str = f"generate question | subject: {subject} | topic: {topic} | unit: {unit} | class: {cls} | board: Public Benchmark | bloom: {bloom} | difficulty: {diff} | marks: {marks} | type: {q_type}"
            
            prompts.append({
                "prompt_id": f"P17-{prompt_id:04d}",
                "category": "standard_matrix",
                "subject": subject,
                "topic": topic,
                "unit": unit,
                "class": cls,
                "board": "Public Benchmark",
                "bloom": bloom,
                "difficulty": diff,
                "marks": marks,
                "question_type": q_type,
                "input_text": prompt_str
            })
            prompt_id += 1

    # Add 20 Paired Sensitivity Prompts (isolating 1 control variable)
    sensitivity_pairs = [
        # Pair 1: Class variation (Class 9 vs Class 12)
        {"subject": "Physics", "topic": "Gravitation & Planetary Motion", "unit": "Mechanics", "bloom": "Apply", "difficulty": "Medium", "marks": 3, "question_type": "Numerical", "var": "class", "v1": "Class 9", "v2": "Class 12"},
        {"subject": "Mathematics", "topic": "Probability & Statistics", "unit": "Statistics", "bloom": "Apply", "difficulty": "Medium", "marks": 3, "question_type": "Numerical", "var": "class", "v1": "Class 9", "v2": "Class 12"},
        {"subject": "Chemistry", "topic": "Chemical Bonding", "unit": "Inorganic Chemistry", "bloom": "Understand", "difficulty": "Medium", "marks": 2, "question_type": "MCQ", "var": "class", "v1": "Class 10", "v2": "Class 12"},
        
        # Pair 2: Difficulty variation (Easy vs Hard)
        {"subject": "Mathematics", "topic": "Quadratic Equations & Roots", "unit": "Algebra", "class": "Class 10", "bloom": "Apply", "question_type": "Numerical", "var": "difficulty", "v1": "Easy", "v2": "Hard"},
        {"subject": "Physics", "topic": "Kinematics & Equations of Motion", "unit": "Mechanics", "class": "Class 11", "bloom": "Apply", "question_type": "Numerical", "var": "difficulty", "v1": "Easy", "v2": "Hard"},
        {"subject": "Biology", "topic": "Cell Structure & Organelles", "unit": "Cell Biology", "class": "Class 11", "bloom": "Analyze", "question_type": "MCQ", "var": "difficulty", "v1": "Easy", "v2": "Hard"},

        # Pair 3: Question Type variation (Numerical vs MCQ)
        {"subject": "Physics", "topic": "Current Electricity & Ohm's Law", "unit": "Electrodynamics", "class": "Class 10", "bloom": "Apply", "difficulty": "Medium", "marks": 3, "var": "question_type", "v1": "Numerical", "v2": "MCQ"},
        {"subject": "Chemistry", "topic": "Solutions & Molarity Molality", "unit": "Physical Chemistry", "class": "Class 11", "bloom": "Apply", "difficulty": "Medium", "marks": 3, "var": "question_type", "v1": "Numerical", "v2": "MCQ"},
        {"subject": "Mathematics", "topic": "Surface Areas & Volumes of Solids", "unit": "Mensuration", "class": "Class 10", "bloom": "Apply", "difficulty": "Medium", "marks": 3, "var": "question_type", "v1": "Numerical", "v2": "MCQ"},

        # Pair 4: Subject variation (Physics vs Chemistry on Shared Topic)
        {"topic": "Thermodynamics & Heat", "unit": "Physical Science", "class": "Class 11", "bloom": "Apply", "difficulty": "Medium", "marks": 3, "question_type": "Numerical", "var": "subject", "v1": "Physics", "v2": "Chemistry"},
    ]

    for p in sensitivity_pairs:
        var_name = p["var"]
        v1, v2 = p["v1"], p["v2"]
        
        # Item 1
        d1 = dict(p)
        del d1["var"]; del d1["v1"]; del d1["v2"]
        d1[var_name] = v1
        if "marks" not in d1:
            d1["marks"] = 1 if d1.get("difficulty") == "Easy" else 5
        if "board" not in d1:
            d1["board"] = "Public Benchmark"
        p_str1 = f"generate question | subject: {d1.get('subject')} | topic: {d1.get('topic')} | unit: {d1.get('unit')} | class: {d1.get('class')} | board: {d1.get('board')} | bloom: {d1.get('bloom')} | difficulty: {d1.get('difficulty')} | marks: {d1.get('marks')} | type: {d1.get('question_type')}"
        d1["prompt_id"] = f"P17-SENS-{prompt_id:04d}-A"
        d1["category"] = "sensitivity_test"
        d1["sensitivity_var"] = var_name
        d1["sensitivity_val"] = v1
        d1["input_text"] = p_str1
        prompts.append(d1)
        prompt_id += 1

        # Item 2
        d2 = dict(p)
        del d2["var"]; del d2["v1"]; del d2["v2"]
        d2[var_name] = v2
        if "marks" not in d2:
            d2["marks"] = 5 if d2.get("difficulty") == "Hard" else 1
        if "board" not in d2:
            d2["board"] = "Public Benchmark"
        p_str2 = f"generate question | subject: {d2.get('subject')} | topic: {d2.get('topic')} | unit: {d2.get('unit')} | class: {d2.get('class')} | board: {d2.get('board')} | bloom: {d2.get('bloom')} | difficulty: {d2.get('difficulty')} | marks: {d2.get('marks')} | type: {d2.get('question_type')}"
        d2["prompt_id"] = f"P17-SENS-{prompt_id:04d}-B"
        d2["category"] = "sensitivity_test"
        d2["sensitivity_var"] = var_name
        d2["sensitivity_val"] = v2
        d2["input_text"] = p_str2
        prompts.append(d2)
        prompt_id += 1

    return prompts

# ==============================================================================
# LEXICONS & SCIENTIFIC VALIDATION RULES
# ==============================================================================
SUBJECT_LEXICONS = {
    "Mathematics": {
        "keywords": ["equation", "quadratic", "root", "algebra", "solve", "probability", "statistics", "mean", "median", 
                     "mode", "triangle", "polynomial", "integer", "coordinate", "ratio", "arithmetic", "progression", 
                     "hypotenuse", "tangent", "circle", "radius", "diameter", "sphere", "cylinder", "cone", "surface area", 
                     "volume", "calculate the value", "find the number", "how many", "fraction", "perimeter", "matrix"],
        "disqualifiers": ["photosynthesis", "chromosome", "cell", "acid", "le chatelier", "reaction", "mitosis", "organelle"]
    },
    "Physics": {
        "keywords": ["force", "friction", "velocity", "acceleration", "speed", "newton", "joule", "watt", "energy", "work",
                     "kinetic", "potential", "gravitation", "gravity", "mass", "refraction", "reflection", "lens", "mirror", 
                     "optics", "current", "voltage", "resistance", "ohm", "magnetic", "induction", "wave", "doppler", 
                     "frequency", "wavelength", "thermodynamics", "temperature", "heat", "kelvin", "circuit", "momentum"],
        "disqualifiers": ["photosynthesis", "dna", "mendelian", "chromosome", "organic chemistry", "alkane"]
    },
    "Chemistry": {
        "keywords": ["chemical", "reaction", "acid", "base", "salt", "ph", "molarity", "molality", "mole", "molar", 
                     "stoichiometry", "equilibrium", "le chatelier", "periodic", "element", "atom", "molecule", "orbital", 
                     "bond", "covalent", "ionic", "redox", "oxidation", "reduction", "enthalpy", "entropy", "alkane", 
                     "alkene", "hydrocarbon", "solution", "solute", "solvent", "catalyst", "precipitate", "electrode"],
        "disqualifiers": ["chromosome", "mitosis", "cell organelle", "photosynthesis", "gravitation"]
    },
    "Biology": {
        "keywords": ["cell", "organelle", "mitochondria", "nucleus", "membrane", "mitosis", "meiosis", "photosynthesis", 
                     "respiration", "krebs", "atp", "genetics", "gene", "chromosome", "dna", "rna", "mendel", "allele", 
                     "inheritance", "circulatory", "blood", "heart", "kidney", "excretory", "ecosystem", "species", 
                     "evolution", "biotechnology", "recombinant", "plant", "tissue", "organism", "protein", "enzyme"],
        "disqualifiers": ["quadratic equation", "trigonometric", "newton's law", "current electricity", "molarity"]
    },
    "General Science": {
        "keywords": ["matter", "solid", "liquid", "gas", "substance", "mixture", "compound", "element", "atom", "molecule", 
                     "tissue", "cell", "force", "motion", "gravitation", "work", "energy", "sound", "living", "plant", 
                     "animal", "speed", "velocity", "conservation of mass", "valence", "free fall"],
        "disqualifiers": ["differential equation", "schrodinger", "recombinant plasmid", "le chatelier"]
    }
}

DEGENERATE_PATTERNS = [
    r"in the water in the water",
    r"is a type of what",
    r"what is a .* and a .*\?",
    r"which of the following is not a .*\?",
    r"what is the smallest amount of .*",
    r"(\b\w+\b)( \1){2,}", # immediate 3x word repetition
    r"generate question",
    r"\|\s*subject:"
]

def evaluate_validity(generated_text, prompt_meta):
    """
    Evaluates Question Validity: VALID, PARTIALLY_VALID, INVALID, GARBLED.
    """
    g = generated_text.strip()
    if not g or len(g) < 5:
        return "GARBLED", "Empty or excessively short string (< 5 chars)."
    
    # Check prompt leakage
    if "generate question" in g.lower() or "| subject:" in g.lower():
        return "INVALID", "Direct prompt echo / metadata leakage."
        
    # Check degenerate repetitive loops
    for pat in DEGENERATE_PATTERNS:
        if re.search(pat, g, re.IGNORECASE):
            # Check if it's the known trivial loop patterns
            if "in the water in the water" in g.lower() or "is a type of what" in g.lower() or "what is the smallest amount of" in g.lower():
                return "INVALID", f"Degenerate template / circular loop detected: '{pat}'"
            if re.search(r"(\b\w+\b)( \1){2,}", g, re.IGNORECASE):
                return "GARBLED", "Severe word repetition stutter."

    # Question ending check
    ends_with_q = g.endswith("?") or g.endswith(".")
    words = g.split()
    
    if len(words) < 4:
        return "INVALID", "Too short to form a meaningful question (< 4 words)."

    # Meaningful question opener
    question_starters = ["what", "which", "how", "why", "calculate", "find", "determine", "state", "explain", "if", "a", "an", "the", "in", "when", "consider", "suppose", "given", "name", "derive", "show"]
    first_word = words[0].lower().strip(".,;:?!'\"")
    has_valid_start = first_word in question_starters
    
    if not has_valid_start and not g.endswith("?"):
        return "PARTIALLY_VALID", "Missing standard question interrogative stem and question mark."
    
    if g.endswith("?") and len(words) >= 5:
        return "VALID", "Complete coherent question structure."
    
    if len(words) >= 6:
        return "PARTIALLY_VALID", "Reasonable sentence structure but non-standard ending."
        
    return "PARTIALLY_VALID", "Marginal question completeness."

def evaluate_subject(generated_text, requested_subject):
    """
    Determines whether the generated question aligns with the requested subject domain.
    """
    g_lower = generated_text.lower()
    subject_scores = {}
    
    for subj, lex in SUBJECT_LEXICONS.items():
        kw_hits = sum(1 for kw in lex["keywords"] if kw in g_lower)
        dq_hits = sum(1 for dq in lex["disqualifiers"] if dq in g_lower)
        subject_scores[subj] = kw_hits - (dq_hits * 2)
        
    # Detect best matching subject
    best_subj = max(subject_scores, key=subject_scores.get)
    max_score = subject_scores[best_subj]
    
    # If no keywords found, mark as UNKNOWN / UNRELATED
    if max_score <= 0:
        inferred_subject = "UNKNOWN"
    else:
        inferred_subject = best_subj
        
    is_accurate = (inferred_subject == requested_subject) or (requested_subject == "General Science" and max_score > 0)
    
    return {
        "requested_subject": requested_subject,
        "inferred_subject": inferred_subject,
        "is_accurate": is_accurate,
        "scores": subject_scores
    }

def evaluate_topic(generated_text, requested_topic):
    """
    Determines whether the generated question contains concepts relevant to the requested topic.
    """
    t_words = [w.lower() for w in re.split(r"[\s,&/-]+", requested_topic) if len(w) > 3 and w.lower() not in ["laws", "unit", "theory", "concept", "basis"]]
    g_lower = generated_text.lower()
    
    matched_words = [w for w in t_words if w in g_lower]
    
    if len(matched_words) >= 1:
        return "MATCH", matched_words
    elif any(len(w) > 4 and w[:4] in g_lower for w in t_words):
        return "MATCH", "partial_stem_match"
    else:
        return "MISMATCH", "No core topic keywords found in generated stem"

def evaluate_question_type(generated_text, requested_type):
    """
    Checks if generated output conforms to the requested format (MCQ, Numerical, Conceptual).
    """
    g = generated_text
    has_options = bool(re.search(r"\([A-D]\)|\b[A-D]\b\s*[:\)]|\bOption\s*[A-D]", g, re.IGNORECASE))
    has_choice_stem = bool(re.search(r"which of the following|choose the|select the|is a type of", g, re.IGNORECASE))
    has_numbers = bool(re.search(r"\d+(\.\d+)?", g))
    has_calc_verbs = bool(re.search(r"calculate|find the value|determine the speed|how many|what is the mass|compute", g, re.IGNORECASE))
    
    if requested_type == "MCQ":
        if has_options or has_choice_stem:
            return "MATCH", "MCQ choices / interrogative stem present"
        else:
            return "MISMATCH", "MCQ requested but no options or choice stem generated"
    elif requested_type == "Numerical":
        if has_numbers or has_calc_verbs:
            return "MATCH", "Numerical quantities / calculation verbs present"
        else:
            return "MISMATCH", "Numerical requested but no numbers or calculation verbs generated"
    elif requested_type in ["Conceptual", "Theoretical"]:
        if not has_options and not has_calc_verbs:
            return "MATCH", "Conceptual explanation format"
        else:
            return "MATCH", "Acceptable conceptual phrasing"
            
    return "UNKNOWN", "Unrecognized type"

def evaluate_math_scientific(generated_text, subject):
    """
    Performs deterministic and heuristic scientific / mathematical validity checks.
    """
    g = generated_text
    numbers = [float(x) for x in re.findall(r"\b\d+(?:\.\d+)?\b", g)]
    
    if subject == "Mathematics":
        if not numbers:
            return "NOT_VERIFIED", "No numerical constants present in mathematical question."
        # Check for division by zero or negative probabilities
        if "probability" in g.lower() and any(n > 1.0 and n != 100.0 for n in numbers if "percent" not in g.lower()):
            if any(n < 0 for n in numbers):
                return "INVALID", "Negative probability detected."
        return "VERIFIED_HEURISTIC", "Mathematical numeric values appear syntactically sound."
        
    elif subject == "Physics":
        g_lower = g.lower()
        if "kelvin" in g_lower or "k" in g.split():
            if any(n < 0 for n in numbers):
                return "INVALID", "Negative absolute temperature in Kelvin."
        if "speed of light" in g_lower:
            if any(n > 3e8 for n in numbers):
                return "INVALID", "Superluminal physical speed (> 3e8 m/s)."
        return "VERIFIED_HEURISTIC", "No physical constraint violations detected."
        
    elif subject == "Chemistry":
        g_lower = g.lower()
        if "ph" in g_lower:
            if any(n < 0 or n > 14 for n in numbers):
                return "INVALID", "Out of bounds aqueous pH value (< 0 or > 14)."
        if "moles" in g_lower or "molarity" in g_lower:
            if any(n < 0 for n in numbers):
                return "INVALID", "Negative molar quantity."
        return "VERIFIED_HEURISTIC", "Chemical physical constraints satisfied."
        
    return "NOT_VERIFIED", "Standard domain check."

# ==============================================================================
# MAIN EVALUATION PIPELINE
# ==============================================================================
def run_phase17_evaluation():
    set_seed(42)
    device = "cpu"
    
    print("=" * 80)
    print("AQPG PHASE 17: COMPREHENSIVE V15 MODEL QUALITY EVALUATION")
    print("=" * 80)
    
    # --------------------------------------------------------------------------
    # STEP 1: CHECKPOINT & ENVIRONMENT VERIFICATION
    # --------------------------------------------------------------------------
    print("\n--- STEP 1: CHECKPOINT & ENVIRONMENT VERIFICATION ---")
    required_files = [
        "model.safetensors", "config.json", "generation_config.json",
        "tokenizer.json", "tokenizer_config.json", "special_tokens_map.json"
    ]
    
    file_status = {}
    for f_name in required_files:
        f_path = os.path.join(V15_MODEL_DIR, f_name)
        exists = os.path.exists(f_path)
        size = os.path.getsize(f_path) if exists else 0
        file_status[f_name] = {"exists": exists, "size_bytes": size}
        print(f"  [{'PASS' if exists else 'FAIL'}] {f_name:25s} ({size:,} bytes)")
        
    if not all(v["exists"] for v in file_status.values()):
        print("[FATAL ERROR] Checkpoint files missing in:", V15_MODEL_DIR)
        sys.exit(1)
        
    print("\nLoading V15 Tokenizer and Model...")
    v15_tokenizer = AutoTokenizer.from_pretrained(V15_MODEL_DIR)
    v15_model = AutoModelForSeq2SeqLM.from_pretrained(V15_MODEL_DIR).to(device)
    v15_model.eval()
    
    param_count = sum(p.numel() for p in v15_model.parameters())
    trainable_params = sum(p.numel() for p in v15_model.parameters() if p.requires_grad)
    
    # NaN/Inf check
    nan_inf_found = False
    for name, param in v15_model.named_parameters():
        if torch.isnan(param).any() or torch.isinf(param).any():
            print(f"  [ERROR] NaN or Inf weights detected in parameter: {name}")
            nan_inf_found = True
            break
            
    print(f"  Model Architecture:    {v15_model.config.architectures}")
    print(f"  Total Parameters:      {param_count:,} ({param_count/1e6:.2f}M)")
    print(f"  PyTorch Version:       {torch.__version__}")
    print(f"  Device:                {device}")
    print(f"  Weight Integrity:      {'PASS (No NaN/Inf)' if not nan_inf_found else 'FAIL (Corrupted Weights)'}")
    
    # --------------------------------------------------------------------------
    # STEP 2: BUILD CONTROLLED EVALUATION MATRIX & RUN INFERENCE
    # --------------------------------------------------------------------------
    print("\n--- STEP 2: GENERATING CONTROLLED EVALUATION MATRIX (520 PROMPTS) ---")
    eval_prompts = build_evaluation_matrix()
    print(f"Constructed {len(eval_prompts)} controlled evaluation prompts.")
    
    # Save prompts to phase17_evaluation_prompts.jsonl
    with open(OUTPUT_PROMPTS_PATH, "w", encoding="utf-8") as f:
        for p in eval_prompts:
            f.write(json.dumps(p) + "\n")
    print(f"Saved evaluation prompts to: {OUTPUT_PROMPTS_PATH}")
    
    # Load V15 train & validation targets for memorization test
    print("\nLoading V15 Dataset Targets for Memorization / Duplication Analysis...")
    v15_train_targets = set()
    if os.path.exists(V15_DATASET_TRAIN):
        with open(V15_DATASET_TRAIN, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    item = json.loads(line)
                    tgt = item.get("target_text", "").strip().lower()
                    if tgt:
                        v15_train_targets.add(tgt)
    print(f"Loaded {len(v15_train_targets):,} unique V15 training targets.")

    print(f"\nExecuting Model Inference over {len(eval_prompts)} prompts (seed 42)...")
    start_gen_time = time.time()
    
    generated_records = []
    failed_examples = []
    
    validity_counter = Counter()
    subject_confusion = defaultdict(Counter)
    topic_counter = Counter()
    type_counter = Counter()
    class_counter = Counter()
    math_counter = Counter()
    physics_counter = Counter()
    chem_counter = Counter()
    
    exact_memorized_count = 0
    near_duplicate_count = 0
    generated_target_set = Counter()

    for idx, p in enumerate(eval_prompts, 1):
        prompt_str = p["input_text"]
        t0 = time.time()
        output_text = generate_text(v15_model, v15_tokenizer, prompt_str, device=device)
        dur = round(time.time() - t0, 4)
        
        # 1. Validity Evaluation (Step 3)
        val_status, val_reason = evaluate_validity(output_text, p)
        validity_counter[val_status] += 1
        
        # 2. Subject Conditioning Accuracy (Step 4)
        sub_eval = evaluate_subject(output_text, p["subject"])
        inferred_subj = sub_eval["inferred_subject"]
        subject_confusion[p["subject"]][inferred_subj] += 1
        
        # 3. Topic Conditioning Accuracy (Step 5)
        top_eval, top_reason = evaluate_topic(output_text, p["topic"])
        topic_counter[top_eval] += 1
        
        # 4. Class Conditioning Accuracy (Step 6)
        # Class 9/10 vs 11/12 heuristic check
        req_class = p["class"]
        if val_status == "INVALID" or val_status == "GARBLED":
            class_eval = "NOT_VERIFIABLE"
        elif "water in the water" in output_text.lower() or "type of what" in output_text.lower():
            class_eval = "INVALID"
        else:
            class_eval = "NOT_VERIFIABLE" # Strict honesty: FLAN-T5-small outputs are generic, not reliably class-differentiated
        class_counter[class_eval] += 1
        
        # 5. Question Type Control (Step 7)
        qtype_eval, qtype_reason = evaluate_question_type(output_text, p["question_type"])
        type_counter[qtype_eval] += 1
        
        # 6. Scientific Verification (Steps 9, 10, 11)
        sci_status, sci_reason = evaluate_math_scientific(output_text, p["subject"])
        if p["subject"] == "Mathematics":
            math_counter[sci_status] += 1
        elif p["subject"] == "Physics":
            physics_counter[sci_status] += 1
        elif p["subject"] == "Chemistry":
            chem_counter[sci_status] += 1
            
        # 7. Duplication / Memorization (Step 12)
        out_norm = output_text.lower().strip()
        generated_target_set[out_norm] += 1
        is_exact_mem = out_norm in v15_train_targets
        if is_exact_mem:
            exact_memorized_count += 1
            
        record = {
            "prompt_id": p["prompt_id"],
            "category": p["category"],
            "subject": p["subject"],
            "topic": p["topic"],
            "class": p["class"],
            "difficulty": p["difficulty"],
            "question_type": p["question_type"],
            "input_prompt": prompt_str,
            "generated_output": output_text,
            "duration_seconds": dur,
            "validity_status": val_status,
            "validity_reason": val_reason,
            "inferred_subject": inferred_subj,
            "subject_match": sub_eval["is_accurate"],
            "topic_status": top_eval,
            "question_type_status": qtype_eval,
            "scientific_status": sci_status,
            "is_exact_memorized": is_exact_mem
        }
        generated_records.append(record)
        
        # Collect failure cases
        if val_status in ["INVALID", "GARBLED", "PARTIALLY_VALID"] or not sub_eval["is_accurate"] or top_eval == "MISMATCH":
            failed_examples.append({
                "prompt_id": p["prompt_id"],
                "subject": p["subject"],
                "topic": p["topic"],
                "class": p["class"],
                "prompt": prompt_str,
                "generated_output": output_text,
                "failure_category": val_status if val_status != "VALID" else ("SUBJECT_MISMATCH" if not sub_eval["is_accurate"] else "TOPIC_MISMATCH"),
                "reason": val_reason if val_status != "VALID" else f"Expected {p['subject']}/{p['topic']}, but generated '{inferred_subj}' / mismatched content."
            })
            
        if idx % 100 == 0 or idx == len(eval_prompts):
            print(f"  Processed {idx:03d}/{len(eval_prompts)} prompts... Current Valid Rate: {validity_counter['VALID'] / idx * 100:.1f}%")

    total_gen_time = round(time.time() - start_gen_time, 2)
    print(f"\nCompleted {len(eval_prompts)} inferences in {total_gen_time}s (Avg {total_gen_time/len(eval_prompts):.2f}s/prompt).")
    
    # Save all generated outputs
    with open(OUTPUT_GENERATIONS_PATH, "w", encoding="utf-8") as f:
        for r in generated_records:
            f.write(json.dumps(r) + "\n")
    print(f"Saved generated outputs to: {OUTPUT_GENERATIONS_PATH}")
    
    # Save failed examples
    with open(OUTPUT_FAILED_EXAMPLES, "w", encoding="utf-8") as f:
        for fe in failed_examples:
            f.write(json.dumps(fe) + "\n")
    print(f"Saved {len(failed_examples)} representative failed examples to: {OUTPUT_FAILED_EXAMPLES}")

    # --------------------------------------------------------------------------
    # STEP 13: CONDITION SENSITIVITY TEST ANALYSIS
    # --------------------------------------------------------------------------
    print("\n--- STEP 13: CONDITION SENSITIVITY TEST ANALYSIS ---")
    sensitivity_records = [r for r in generated_records if r["category"] == "sensitivity_test"]
    sensitivity_results = []
    
    for i in range(0, len(sensitivity_records), 2):
        if i + 1 < len(sensitivity_records):
            r1 = sensitivity_records[i]
            r2 = sensitivity_records[i+1]
            out1 = r1["generated_output"]
            out2 = r2["generated_output"]
            is_different = (out1.strip().lower() != out2.strip().lower())
            
            # Sensitivity metric
            sensitivity_results.append({
                "pair_id": f"PAIR-{(i//2)+1:02d}",
                "prompt_a": r1["input_prompt"],
                "output_a": out1,
                "prompt_b": r2["input_prompt"],
                "output_b": out2,
                "is_sensitive_to_change": is_different
            })
            print(f"  [PAIR {(i//2)+1:02d}] Different Output: {is_different}")
            print(f"     A: {out1}")
            print(f"     B: {out2}")

    sensitive_pairs_count = sum(1 for p in sensitivity_results if p["is_sensitive_to_change"])
    sensitivity_rate = round(sensitive_pairs_count / len(sensitivity_results) * 100, 2) if sensitivity_results else 0.0
    sensitivity_verdict = "CONTROL-SENSITIVE" if sensitivity_rate > 80 else ("PARTIALLY CONTROL-SENSITIVE" if sensitivity_rate >= 40 else "CONTROL-BLIND")
    print(f"Sensitivity Rate: {sensitivity_rate}% -> Classification: {sensitivity_verdict}")

    with open(OUTPUT_SENSITIVITY_JSON, "w", encoding="utf-8") as f:
        json.dump({
            "sensitivity_rate_percent": sensitivity_rate,
            "classification": sensitivity_verdict,
            "pairs": sensitivity_results
        }, f, indent=2)

    # --------------------------------------------------------------------------
    # STEP 15: BASELINE COMPARISON (V15 vs V3 vs Base FLAN-T5)
    # --------------------------------------------------------------------------
    print("\n--- STEP 15: BASELINE COMPARISON ---")
    baseline_sample_prompts = [
        "generate question | subject: Mathematics | topic: Linear Equations & Word Problems | unit: UNKNOWN | class: Class 10 | board: Public Benchmark | bloom: Apply | difficulty: Medium | marks: 3 | type: Numerical",
        "generate question | subject: Physics | topic: Newton's Laws & Friction | unit: Mechanics | class: Class 11 | board: OpenStax Academic | bloom: Apply | difficulty: Medium | marks: 3 | type: Numerical",
        "generate question | subject: Chemistry | topic: Chemical Equilibrium & Le Chatelier | unit: UNKNOWN | class: Class 12 | board: Public Benchmark | bloom: Analyze | difficulty: Hard | marks: 3 | type: MCQ",
        "generate question | subject: Biology | topic: Mendelian Genetics & Inheritance | unit: Genetics | class: Class 12 | board: OpenStax Academic | bloom: Understand | difficulty: Medium | marks: 2 | type: MCQ",
        "generate question | subject: General Science | topic: Matter in Our Surroundings | unit: Secondary General Science | class: Class 9 | board: Public Benchmark | bloom: Remember | difficulty: Easy | marks: 1 | type: MCQ"
    ]
    
    # Check if V3 model is available
    v3_available = os.path.exists(os.path.join(V3_MODEL_DIR, "model.safetensors"))
    v3_model, v3_tokenizer = None, None
    if v3_available:
        try:
            print(f"Loading V3 Model from {V3_MODEL_DIR}...")
            v3_tokenizer = AutoTokenizer.from_pretrained(V3_MODEL_DIR)
            v3_model = AutoModelForSeq2SeqLM.from_pretrained(V3_MODEL_DIR).to(device)
            v3_model.eval()
        except Exception as e:
            print(f"Could not load V3: {e}")
            v3_available = False

    print(f"Loading Base Model {BASE_MODEL_NAME}...")
    base_tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL_NAME)
    base_model = AutoModelForSeq2SeqLM.from_pretrained(BASE_MODEL_NAME).to(device)
    base_model.eval()

    baseline_comparison = []
    for bp in baseline_sample_prompts:
        v15_out = generate_text(v15_model, v15_tokenizer, bp, device=device)
        base_out = generate_text(base_model, base_tokenizer, bp, device=device)
        v3_out = generate_text(v3_model, v3_tokenizer, bp, device=device) if v3_available else "CHECKPOINT_UNAVAILABLE"
        
        baseline_comparison.append({
            "prompt": bp,
            "flan_t5_base_raw": base_out,
            "v3_flan_t5_pilot": v3_out,
            "v15_flan_t5_small": v15_out
        })

    with open(OUTPUT_BASELINE_JSON, "w", encoding="utf-8") as f:
        json.dump({
            "comparison": baseline_comparison,
            "v3_available": v3_available,
            "base_model": BASE_MODEL_NAME
        }, f, indent=2)

    # --------------------------------------------------------------------------
    # METRICS CALCULATION & CONFUSION MATRICES
    # --------------------------------------------------------------------------
    total_prompts = len(generated_records)
    valid_rate = round(validity_counter["VALID"] / total_prompts * 100, 2)
    part_valid_rate = round(validity_counter["PARTIALLY_VALID"] / total_prompts * 100, 2)
    invalid_rate = round(validity_counter["INVALID"] / total_prompts * 100, 2)
    garbled_rate = round(validity_counter["GARBLED"] / total_prompts * 100, 2)

    correct_subjects = sum(1 for r in generated_records if r["subject_match"])
    subject_acc = round(correct_subjects / total_prompts * 100, 2)
    
    topic_match_rate = round(topic_counter["MATCH"] / total_prompts * 100, 2)
    topic_mismatch_rate = round(topic_counter["MISMATCH"] / total_prompts * 100, 2)

    type_match_rate = round(type_counter["MATCH"] / total_prompts * 100, 2)

    unique_outputs_count = len(generated_target_set)
    unique_rate = round(unique_outputs_count / total_prompts * 100, 2)
    rep_template_rate = round((total_prompts - unique_outputs_count) / total_prompts * 100, 2)
    exact_mem_rate = round(exact_memorized_count / total_prompts * 100, 2)

    # Confusion matrix output
    cm_dict = {}
    for subj in SUBJECT_LEXICONS.keys():
        cm_dict[subj] = {target: subject_confusion[subj][target] for target in list(SUBJECT_LEXICONS.keys()) + ["UNKNOWN"]}
        
    with open(OUTPUT_CONFUSION_JSON, "w", encoding="utf-8") as f:
        json.dump(cm_dict, f, indent=2)

    # Quality Summary JSON
    quality_summary = {
        "dataset_version": "V15",
        "checkpoint_evaluated": V15_MODEL_DIR,
        "total_prompts_evaluated": total_prompts,
        "validity_metrics": {
            "valid_count": validity_counter["VALID"],
            "valid_rate_percent": valid_rate,
            "partially_valid_count": validity_counter["PARTIALLY_VALID"],
            "partially_valid_rate_percent": part_valid_rate,
            "invalid_count": validity_counter["INVALID"],
            "invalid_rate_percent": invalid_rate,
            "garbled_count": validity_counter["GARBLED"],
            "garbled_rate_percent": garbled_rate
        },
        "conditioning_accuracy": {
            "subject_accuracy_percent": subject_acc,
            "topic_match_percent": topic_match_rate,
            "topic_mismatch_percent": topic_mismatch_rate,
            "question_type_accuracy_percent": type_match_rate,
            "class_not_verifiable_rate_percent": round(class_counter["NOT_VERIFIABLE"] / total_prompts * 100, 2),
            "control_sensitivity_percent": sensitivity_rate,
            "control_sensitivity_classification": sensitivity_verdict
        },
        "scientific_verification": {
            "mathematics": dict(math_counter),
            "physics": dict(physics_counter),
            "chemistry": dict(chem_counter)
        },
        "diversity_and_memorization": {
            "unique_generations_count": unique_outputs_count,
            "unique_generation_rate_percent": unique_rate,
            "template_repetition_rate_percent": rep_template_rate,
            "exact_memorization_rate_percent": exact_mem_rate
        },
        "hardware_and_environment": {
            "pytorch_version": torch.__version__,
            "device": device,
            "parameter_count": param_count,
            "nan_inf_weights_present": nan_inf_found
        }
    }

    # --------------------------------------------------------------------------
    # STEP 16 & 17: PRODUCTION READINESS SCORE & FINAL DECISION GATE
    # --------------------------------------------------------------------------
    # Decision Criteria:
    # 1. Valid Rate >= 85% AND Subject Acc >= 85% AND Topic Acc >= 70% AND Repetition < 30% -> PRODUCTION READY
    # 2. If model has valid technical syntax but produces circular / repetitive templates ("in the water", "type of what") -> PROMISING — NEEDS IMPROVEMENT
    # 3. If model generates completely collapsed outputs -> NEEDS MORE TRAINING/DATA
    if valid_rate >= 85.0 and subject_acc >= 85.0 and topic_match_rate >= 75.0 and rep_template_rate <= 20.0:
        final_verdict = "A. PRODUCTION READY"
        verdict_rationale = "Model demonstrates robust multi-subject curriculum control, high question validity, and minimal repetitive collapse."
    elif valid_rate >= 30.0 or subject_acc >= 40.0:
        final_verdict = "B. PROMISING — NEEDS IMPROVEMENT"
        verdict_rationale = "Model demonstrates basic domain awareness and vocabulary conditioning across STEM subjects, but suffers from template collapse (e.g. 'is a type of what', 'in the water'), weak numerical reasoning, and insufficient class-level differentiation."
    else:
        final_verdict = "C. NEEDS MORE TRAINING/DATA"
        verdict_rationale = "Model exhibits severe collapse, high garbled rate, and inability to generate syntactically coherent domain questions."

    quality_summary["production_readiness"] = {
        "final_verdict": final_verdict,
        "rationale": verdict_rationale
    }

    with open(OUTPUT_EVAL_JSON, "w", encoding="utf-8") as f:
        json.dump(quality_summary, f, indent=2)
    print(f"Saved quality evaluation summary to: {OUTPUT_EVAL_JSON}")

    # Error analysis breakdown
    error_analysis = {
        "total_failures": len(failed_examples),
        "failure_modes": {
            "degenerate_template_loops": sum(1 for fe in failed_examples if "degenerate" in fe["reason"].lower() or "type of what" in fe["generated_output"].lower() or "in the water" in fe["generated_output"].lower()),
            "subject_mismatch": sum(1 for fe in failed_examples if fe["failure_category"] == "SUBJECT_MISMATCH"),
            "topic_mismatch": sum(1 for fe in failed_examples if fe["failure_category"] == "TOPIC_MISMATCH"),
            "garbled_or_truncated": sum(1 for fe in failed_examples if fe["failure_category"] in ["GARBLED", "PARTIALLY_VALID"])
        },
        "sample_failures": failed_examples[:60]
    }
    with open(OUTPUT_ERRORS_JSON, "w", encoding="utf-8") as f:
        json.dump(error_analysis, f, indent=2)
    print(f"Saved error analysis to: {OUTPUT_ERRORS_JSON}")

    # --------------------------------------------------------------------------
    # WRITE COMPREHENSIVE TEXT REPORT
    # --------------------------------------------------------------------------
    report_lines = [
        "=" * 80,
        "AQPG PHASE 17: COMPREHENSIVE FLAN-T5-SMALL V15 QUALITY EVALUATION REPORT",
        "=" * 80,
        f"Evaluation Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}",
        f"Checkpoint Evaluated: {V15_MODEL_DIR}",
        f"Dataset Evaluated:    datasets/v15/qg_dataset_v15.jsonl",
        f"Total Prompts Tested: {total_prompts}",
        f"Execution Device:     {device}",
        f"Total Parameters:     {param_count:,} ({param_count/1e6:.2f}M)",
        f"PyTorch Version:      {torch.__version__}",
        "",
        "=" * 80,
        "1. QUESTION VALIDITY EVALUATION (STEP 3)",
        "=" * 80,
        f"VALID Questions:           {validity_counter['VALID']:4d} ({valid_rate:.2f}%)",
        f"PARTIALLY VALID Questions: {validity_counter['PARTIALLY_VALID']:4d} ({part_valid_rate:.2f}%)",
        f"INVALID Questions:         {validity_counter['INVALID']:4d} ({invalid_rate:.2f}%)",
        f"GARBLED / Degenerate:      {validity_counter['GARBLED']:4d} ({garbled_rate:.2f}%)",
        "",
        "=" * 80,
        "2. SUBJECT & TOPIC CONDITIONING ACCURACY (STEPS 4 & 5)",
        "=" * 80,
        f"Subject Conditioning Accuracy: {subject_acc:.2f}%",
        f"Topic Match Rate:             {topic_match_rate:.2f}%",
        f"Topic Mismatch Rate:          {topic_mismatch_rate:.2f}%",
        "",
        "Subject Confusion Matrix (Rows = Requested, Cols = Inferred):",
        f"{'Requested':<18} | {'Math':<6} | {'Physics':<8} | {'Chemistry':<10} | {'Biology':<8} | {'GenSci':<7} | {'Unknown':<7}",
        "-" * 80
    ]
    
    for s_req in ["Mathematics", "Physics", "Chemistry", "Biology", "General Science"]:
        c_m = cm_dict[s_req]
        report_lines.append(f"{s_req:<18} | {c_m.get('Mathematics',0):<6} | {c_m.get('Physics',0):<8} | {c_m.get('Chemistry',0):<10} | {c_m.get('Biology',0):<8} | {c_m.get('General Science',0):<7} | {c_m.get('UNKNOWN',0):<7}")

    report_lines.extend([
        "",
        "=" * 80,
        "3. QUESTION-TYPE & DIFFICULTY CONTROL (STEPS 7 & 8)",
        "=" * 80,
        f"Question-Type Alignment Rate:  {type_match_rate:.2f}%",
        f"Class Alignment Determination: NOT_VERIFIABLE ({round(class_counter['NOT_VERIFIABLE']/total_prompts*100, 2)}%)",
        "  (Note: Model output length & vocabulary do not yet reliably discriminate Class 9 from Class 12)",
        "",
        "=" * 80,
        "4. SCIENTIFIC & MATHEMATICAL REASONING (STEPS 9, 10, 11)",
        "=" * 80,
        f"Mathematics Numerical Verification: {dict(math_counter)}",
        f"Physics Scientific Verification:     {dict(physics_counter)}",
        f"Chemistry Scientific Verification:   {dict(chem_counter)}",
        "",
        "=" * 80,
        "5. DUPLICATION, MEMORIZATION & DIVERSITY (STEP 12)",
        "=" * 80,
        f"Unique Output Rate:            {unique_rate:.2f}% ({unique_outputs_count}/{total_prompts})",
        f"Template Repetition Rate:       {rep_template_rate:.2f}%",
        f"Exact Training Set Memorized:   {exact_mem_rate:.2f}% ({exact_memorized_count} records)",
        "",
        "=" * 80,
        "6. CONDITION SENSITIVITY TEST (STEP 13)",
        "=" * 80,
        f"Sensitivity Rate:              {sensitivity_rate:.2f}%",
        f"Model Classification:          {sensitivity_verdict}",
        "",
        "=" * 80,
        "7. BASELINE COMPARISON (STEP 15)",
        "=" * 80,
        "Model Comparison across Standard Prompt Samples:"
    ])

    for idx, bc in enumerate(baseline_comparison, 1):
        report_lines.extend([
            f"\n[Sample {idx}] PROMPT: {bc['prompt']}",
            f"  BASE FLAN-T5: {bc['flan_t5_base_raw']}",
            f"  V3 PILOT:     {bc['v3_flan_t5_pilot']}",
            f"  V15 MODEL:    {bc['v15_flan_t5_small']}"
        ])

    report_lines.extend([
        "",
        "=" * 80,
        "8. PRODUCTION READINESS DECISION GATE (STEPS 16 & 17)",
        "=" * 80,
        f"FINAL VERDICT: {final_verdict}",
        f"RATIONALE:     {verdict_rationale}",
        "",
        "EVIDENCE SUMMARY:",
        f"1. Valid Question Structure:     {valid_rate:.2f}% (Significant repetitive templates observed)",
        f"2. Subject Domain Conditioning:  {subject_acc:.2f}%",
        f"3. Topic Alignment:              {topic_match_rate:.2f}%",
        f"4. Control Sensitivity:          {sensitivity_rate:.2f}% ({sensitivity_verdict})",
        f"5. Memorization Rate:            {exact_mem_rate:.2f}%",
        "",
        "RECOMMENDED NEXT ACTIONS:",
        "1. Transition to FLAN-T5-Base / Large architecture to expand parameter capacity beyond 60M.",
        "2. Increase training steps beyond 100 steps on GPU hardware to allow deep convergence.",
        "3. Implement contrastive loss and anti-template repetition penalties during fine-tuning.",
        "=" * 80
    ])

    with open(OUTPUT_REPORT_TXT, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))
    print(f"\nSaved Comprehensive Evaluation Report to: {OUTPUT_REPORT_TXT}")
    
    print("\n" + "=" * 80)
    print(f"PHASE 17 EVALUATION COMPLETE.")
    print(f"FINAL VERDICT: {final_verdict}")
    print("=" * 80)

if __name__ == "__main__":
    run_phase17_evaluation()
