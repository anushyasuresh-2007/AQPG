"""
bloom_service.py
Service for classifying and validating question text into Bloom's Taxonomy levels using
trained ML models and pedagogical cognitive-task heuristics.
"""

import os
import re
from typing import Dict, Any, Optional, Tuple

try:
    import joblib
except ImportError:
    joblib = None

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MODEL_DIR = os.path.join(BASE_DIR, "ml", "models", "bloom_classifier")

_vectorizer = None
_classifier = None


def _load_model():
    global _vectorizer, _classifier
    if _vectorizer is None or _classifier is None:
        if joblib is None:
            _vectorizer = False
            _classifier = False
            return

        vec_path = os.path.join(MODEL_DIR, "tfidf_vectorizer.pkl")
        model_path = os.path.join(MODEL_DIR, "bloom_classifier_model.pkl")

        if os.path.exists(vec_path) and os.path.exists(model_path):
            try:
                _vectorizer = joblib.load(vec_path)
                _classifier = joblib.load(model_path)
            except Exception:
                _vectorizer = False
                _classifier = False
        else:
            _vectorizer = False
            _classifier = False


BLOOM_HIERARCHY = {
    "Remember": 1,
    "Understand": 2,
    "Apply": 3,
    "Analyze": 4,
    "Evaluate": 5,
    "Create": 6,
}


def infer_bloom_level(question_text: str) -> str:
    """
    Infer the cognitive Bloom's Taxonomy level for a question based on the actual task required,
    using full-sentence cognitive operations rather than isolated single verbs.
    """
    if not question_text or not question_text.strip():
        return "Understand"

    q = question_text.strip().lower()

    # High-order: Create (Synthesis, drafting, writing formats, designing solutions)
    create_patterns = [
        r"\bwrite\s+(an?\s+)?(formal\s+|informal\s+|application\s+)?(letter|notice|report|speech|article|summary|analytical paragraph|dialogue|composition)\b",
        r"\bdraft\s+(an?\s+)?(notice|poster|advertisement|invitation|reply)\b",
        r"\b(compose|create)\s+(an?\s+)?(poem|paragraph|essay|story|dialogue)\b",
        r"\b(design|construct|formulate|devise|propose)\s+(an?\s+)?(new\s+)?(solution|model|system|circuit|experiment|algorithm|framework|plan)\b",
    ]
    if any(re.search(pat, q) for pat in create_patterns):
        return "Create"

    # High-order: Evaluate (Critique, justification, assessing trade-offs, defending stand)
    eval_patterns = [
        r"\bcritically\s+(evaluate|assess|examine|analyze)\b",
        r"\bevaluate\s+(whether|how|the\s+claim|the\s+statement|the\s+validity|the\s+effectiveness|the\s+truth|the\s+importance|the\s+merits|the\s+significance|the\s+role|the\s+impact|the\s+advantages|if)\b",
        r"\bjustify\s+(your|this|the|whether|why)\b",
        r"\bdo you agree\b",
        r"\bassess\s+(the\s+)?(validity|impact|extent|effectiveness|consequences?|significance|truth|advantages|merits|trade-offs)\b",
        r"\bassess\s+whether\b",
        r"\b(critique|appraise|judge the merits|evaluate the advantages)\b",
    ]
    if any(re.search(pat, q) for pat in eval_patterns):
        return "Evaluate"

    # High-order: Analyze (Breaking down, comparative analysis, causes, inference)
    analyze_patterns = [
        r"\b(compare|contrast|examine|investigate)\b",
        r"\banalyze\b",
        r"\bwhat\s+(factors?|causes?)\s+led\s+to\b",
        r"\bwhat\s+(inference|conclusion)\s+can\s+be\s+drawn\b",
        r"\binfer\s+the\s+(author's|poet's|character's)\b",
    ]
    if any(re.search(pat, q) for pat in analyze_patterns):
        return "Analyze"

    # Middle-order: Apply (Calculations, procedural execution, grammar transformation, conversions, code implementation)
    apply_patterns = [
        r"\b(calculate|compute|solve|find the value|determine the magnitude)\b",
        r"\bfind\s+the\s+(value|length|coordinates|distance|ratio|radius|area|volume|zeroes|zeros|term|sum|mean|median|mode|derivative|inverse)\b",
        r"\bdetermine\s+the\s+(magnitude|value|ratio|coordinates|general term|nature of roots)\b",
        r"\bevaluate\s+the\s+(trigonometric|definite|indefinite|matrix)?\s*(expression|integral|limit)\b",
        r"\brewrite\s+.*(passive|active|reported|indirect|voice)\b",
        r"\bchange\s+(the\s+voice|into\s+(passive|indirect|direct))\b",
        r"\bbalance\s+the\s+(chemical\s+)?equation\b",
        r"\busing\s+.*(formula|law|theorem)\b",
        r"\bwrite\s+(a\s+)?(python\s+|sql\s+|c\+\+\s+|java\s+)?(program|function|script|query|code|algorithm)\b",
    ]
    if any(re.search(pat, q) for pat in apply_patterns):
        return "Apply"

    # Low-order: Remember (Recall, naming, listing, stating definitions, stating laws)
    remember_patterns = [
        r"\bdefine\b",
        r"\bstate\s+(the\s+)?(law|principle|theorem|snell's|ohm's|newton's|bpt|thales)\b",
        r"\bname\s+(the\s+)?(author|poet|device|element|compound|hormone|organ|capital|part|scientist)\b",
        r"\blist\s+(two|three|four|any|\d+|the)?\s*(uses?|properties|examples|features|points|types)\b",
        r"\bwho\s+(was|wrote|discovered|invented|founded|led)\b",
        r"\bwhen\s+(was|did)\b",
        r"\bwhere\s+(is|was|did)\b",
        r"\bwhat\s+is\s+(the\s+chemical\s+formula|the\s+si\s+unit|the\s+symbol|meant\s+by)\b",
        r"\bmention\s+(any\s+|two\s+|three\s+)?(functions?|factors?|methods?|uses?)\b",
    ]
    if any(re.search(pat, q) for pat in remember_patterns):
        return "Remember"

    # Middle-order: Understand (Explaining, describing, differentiating, summarizing)
    understand_patterns = [
        r"\bexplain\b",
        r"\bdescribe\b",
        r"\bsummarize\b",
        r"\bwhy\s+does\b",
        r"\bgive\s+reasons?\b",
        r"\billustrate\b",
        r"\bdifferentiate\s+between\b",
        r"\bdistinguish\s+between\b",
    ]
    if any(re.search(pat, q) for pat in understand_patterns):
        return "Understand"

    return "Understand"


def validate_bloom_level(question_text: str, target_bloom: str) -> Tuple[bool, str, str]:
    """
    Validate whether the cognitive demand of a question matches the target Bloom's level.
    Rejects questions whose cognitive task operation severely contradicts the target Bloom level.
    Returns: (is_valid, inferred_level, reason)
    """
    inferred = infer_bloom_level(question_text)
    target_clean = target_bloom.strip().title()

    if target_clean not in BLOOM_HIERARCHY:
        return True, inferred, "Target Bloom level is non-standard; accepting."

    if inferred == target_clean:
        return True, inferred, f"Exact match for cognitive level '{target_clean}'."

    t_val = BLOOM_HIERARCHY[target_clean]
    i_val = BLOOM_HIERARCHY[inferred]

    # Adjacent levels (distance <= 1) are pedagogically acceptable in classroom contexts
    # EXCEPTION: "Remember" must NEVER accept high-order cognitive requests (Analyze, Evaluate, Create)
    if target_clean == "Remember" and i_val >= 4:
        return False, inferred, f"Question requires {inferred} (cognitive level {i_val}), which severely exceeds target Remember (level 1)."

    if target_clean in ("Evaluate", "Create") and i_val <= 2:
        return False, inferred, f"Question requires only {inferred} (cognitive level {i_val}), which is insufficient for target {target_clean} (level {t_val})."

    if abs(t_val - i_val) <= 1:
        return True, inferred, f"Question cognitive level '{inferred}' is within acceptable pedagogical range of target '{target_clean}'."

    return False, inferred, f"Cognitive mismatch: Question performs '{inferred}' (level {i_val}) instead of target '{target_clean}' (level {t_val})."


def predict_bloom_level(question_text: str) -> Dict[str, Any]:
    """
    Predicts Bloom's taxonomy level for a given question string.
    Combines ML model predictions (if available) with task-based cognitive heuristics.
    """
    _load_model()

    if not question_text or not question_text.strip():
        return {"bloom_level": "Understand", "confidence": 0.0, "source": "fallback"}

    if _vectorizer and _classifier:
        try:
            X = _vectorizer.transform([question_text.strip()])
            predicted_class = _classifier.predict(X)[0]

            probs = {}
            if hasattr(_classifier, "predict_proba"):
                prob_vals = _classifier.predict_proba(X)[0]
                for idx, cls_name in enumerate(_classifier.classes_):
                    probs[cls_name] = float(prob_vals[idx])

            confidence = max(probs.values()) if probs else 1.0

            return {
                "bloom_level": predicted_class,
                "confidence": round(confidence, 4),
                "probabilities": probs,
                "source": "ml_bloom_classifier"
            }
        except Exception as e:
            print(f"[bloom_service] ML model error: {e}")

    # Robust cognitive-task inference
    inferred = infer_bloom_level(question_text)
    return {
        "bloom_level": inferred,
        "confidence": 0.85,
        "probabilities": {},
        "source": "cognitive_task_rule"
    }


if __name__ == "__main__":
    tests = [
        ("Define compound interest.", "Remember"),
        ("Calculate the momentum of a 50kg vehicle moving at 20 m/s.", "Apply"),
        ("Critically evaluate the impact of demonetization on small businesses.", "Evaluate"),
        ("Write a formal letter to the municipal commissioner complaining about poor roads.", "Create"),
        ("Explain why copper turns green when exposed to air.", "Understand"),
        ("Compare and contrast the causes of World War I and World War II.", "Analyze"),
    ]
    for q, target in tests:
        valid, inf, reason = validate_bloom_level(q, target)
        print(f"[{'PASS' if valid else 'FAIL'}] Target: {target} | Inferred: {inf} | {reason}")
