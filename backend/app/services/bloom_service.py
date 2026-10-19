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
    is_narrative_question = bool(re.search(r"\b(why|how|when|who|where)\s+(did|was|were|has|have|had)?\s*.*?\bwrite\b", q))
    if not is_narrative_question:
        create_patterns = [
            r"^(you are to\s+|please\s+)?write\s+(an?\s+)?(formal\s+|informal\s+|application\s+)?(letter|notice|report|speech|article|summary|analytical paragraph|dialogue|composition)\b",
            r"\bwrite\s+(an?\s+)?(formal\s+|informal\s+|application\s+)?(letter|notice|report|speech|article|summary|analytical paragraph|dialogue|composition)\s+(to|about|for|on|highlighting|complaining|inviting)\b",
            r"\bdraft\s+(an?\s+)?(formal\s+|informal\s+)?(notice|poster|advertisement|invitation|reply|job\s+application)\b",
            r"\b(compose|create)\s+(an?\s+)?(poem|paragraph|essay|story|dialogue)\b",
            r"\b(design|construct|formulate|devise|propose)\s+(an?\s+)?(new\s+)?(solution|model|system|circuit|experiment|algorithm|framework|plan)\b",
            r"\b(respond\s+to\s+an?\s+advertisement|job\s+application\s+with\s+(a\s+)?(comprehensive\s+)?bio-data)\b",
            r"^(as\s+the\s+[^,]+,\s*)?(write|draft)\s+(an?\s+)?(formal\s+|informal\s+|official\s+)?(speech|article|notice|report|letter|invitation)\b",
        ]
        if any(re.search(pat, q) for pat in create_patterns):
            return "Create"

    # Mathematical expression / integral / limit evaluation is procedural (Apply)
    if re.search(r"\bevaluate\s*(:|the\s+(trigonometric|definite|indefinite|matrix)?\s*(expression|integral|limit|derivative|determinant))\b", q):
        return "Apply"

    # High-order: Evaluate (Critique, justification, assessing trade-offs, defending stand)
    eval_patterns = [
        r"\bcritically\s+(evaluate|assess|examine|analyze|discuss|appraise)\b",
        r"\bevaluate\b",
        r"\bassess\b",
        r"\bjustify\s+(your|this|the|whether|why)\b",
        r"\bdo you agree\b",
        r"\bdiscuss\b.*\b(conflict|moral|dilemma|implications|vulnerability|trade-offs|themes?)\b",
        r"\b(critique|appraise|judge the merits|evaluate the advantages)\b",
        r"\b(assess|evaluate)\s+(the\s+)?(strategic|economic|operational|pedagogical|ethical|environmental|practical|effectiveness|benefits|limitations|validity|impact|utility|feasibility|relevance|trade-offs?)\b",
    ]
    if any(re.search(pat, q) for pat in eval_patterns):
        return "Evaluate"

    # High-order: Analyze (Breaking down, comparative analysis, causes, inference, mechanisms)
    analyze_patterns = [
        r"\b(compare|contrast|examine|investigate)\b",
        r"\banalyze\b",
        r"\bwhat\s+(factors?|causes?)\s+led\s+to\b",
        r"\bwhat\s+(inference|conclusion)\s+can\s+be\s+drawn\b",
        r"\binfer\s+the\s+(author's|poet's|character's)\b",
        r"\b(distinguish|differentiate)\s+between\b.*\b(evolution|mechanism|principle|consequences?|significance|implications?|functions?|difference|operational)\b",
        r"\bexplain\s+(the\s+)?(operational\s+|underlying\s+|molecular\s+)?(mechanism|process of credit creation|working principle|how power sharing)\b",
        r"\bexplain\s+(the\s+)?(significance|symbolism|metaphor|irony|imagery|implications?)\b",
        r"\bhow\s+does\s+.*(function|operate|mechanism|differ)\b",
        r"\bhow\s+(did|does)\s+.*(change|transform|shift|react|evolve)\b",
        r"\bwhat\s+(does|do)\s+.*(indicate|imply|reflect|signify)\b",
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


def infer_bloom_level_hindi(question_text: str) -> str:
    """
    Infer Bloom's Taxonomy cognitive level for Hindi questions based on Devanagari action verbs and phrasing.
    """
    if not question_text or not question_text.strip():
        return "Understand"
    q = question_text.strip()

    # Create (Synthesis, letter/essay writing, dialogue creation, proposing plans)
    if any(re.search(p, q) for p in [
        r"(पत्र|निबंध|अनुच्छेद|प्रारूप|संवाद|कहानी|कविता)\s*(लिखिए|लिखें|रचना|तैयार\s*कीजिए)",
        r"(रचना\s*कीजिए|परिकल्पना\s*कीजिए|प्रारूप\s*तैयार)",
        r"नई\s*(योजना|समाधान)\s*(प्रस्तुत|बनाइए)",
    ]):
        return "Create"

    # Evaluate (Critique, justification, assessing claims, discussing significance)
    if any(re.search(p, q) for p in [
        r"(समीक्षा|मूल्यांकन|औचित्य|विवेचना)\s*(कीजिए|करें|लिखिए)",
        r"आलोचनात्मक\s*(समीक्षा|मूल्यांकन|व्याख्या)",
        r"(सार्थकता|महत्व)\s*सिद्ध\s*कीजिए",
        r"क्या\s*आप\s*सहमत\s*हैं",
        r"स्पष्ट\s*कीजिए\s*कि.*(केवल|नहीं)",
        r"(उचित|अनुचित)\s*ठहराइए",
    ]):
        return "Evaluate"

    # Analyze (Breaking down, comparative analysis, causes, inference, satirical purpose)
    if any(re.search(p, q) for p in [
        r"(विश्लेषण|तुलना|अंतर\s*स्पष्ट|तर्क\s*सहित)\s*(कीजिए|करें|लिखिए)",
        r"(किन\s*कमियों|व्यंग्य|विशेषताएँ\s*उभरकर|चरित्र\s*की\s*विशेषताएँ)",
        r"(कारण\s*बताइए|प्रभाव\s*स्पष्ट|निष्कर्ष\s*निकालिए)",
    ]):
        return "Analyze"

    # Apply (Calculations, solving, applying grammatical rules, sentence transformation)
    if any(re.search(p, q) for p in [
        r"(गणना\s*कीजिए|हल\s*कीजिए|वाक्य\s*बनाइए|रूपांतरण\s*कीजिए|परिवर्तन\s*कीजिए)",
        r"(प्रयोग\s*करके\s*दिखाइए|संधि\s*विच्छेद|समास\s*विग्रह)",
    ]):
        return "Apply"

    # Remember (Factual recall, listing, definitions, naming, who/when/where)
    if any(re.search(p, q) for p in [
        r"(परिभाषा\s*दीजिए|परिभाषित\s*कीजिए|नाम\s*लिखिए|सूची\s*बनाइए)",
        r"\b(कब|कहाँ|किसने|किसे)\b",
        r"(उल्लेख\s*कीजिए|नाम\s*बताइए|दो\s*उदाहरण\s*दीजिए)",
    ]):
        return "Remember"

    # Understand (Explanation, descriptions, summaries, illustrations)
    if any(re.search(p, q) for p in [
        r"(व्याख्या\s*कीजिए|स्पष्ट\s*कीजिए|वर्णन\s*कीजिए|भाव\s*स्पष्ट|आशय\s*स्पष्ट|प्रकाश\s*डालिए|विशेषताएँ\s*लिखिए|संक्षेप\s*में)",
        r"से\s*क्या\s*(तात्पर्य|अभिप्राय)\s*है",
    ]):
        return "Understand"

    return "Understand"


def validate_bloom_level(
    question_text: str,
    target_bloom: str,
    language: Optional[str] = None,
) -> Tuple[bool, str, str]:
    """
    Validate whether the cognitive demand of a question matches the target Bloom's level.
    Rejects questions whose cognitive task operation severely contradicts the target Bloom level.
    Returns: (is_valid, inferred_level, reason)
    """
    target_clean = target_bloom.strip().title()

    # Tamil script range (\u0B80-\u0BFF) is outside the current project scope
    if bool(re.search(r"[\u0B80-\u0BFF]", question_text)):
        return False, "Unsupported", (
            "Tamil script is outside the current project scope and cannot be validated for Bloom cognitive level."
        )

    # Devanagari script range (\u0900-\u097F)
    has_devanagari = bool(re.search(r"[\u0900-\u097F]", question_text))
    if has_devanagari:
        lang_clean = (language or "").strip().lower()
        if lang_clean not in ("hindi", "hi"):
            return False, "Unsupported", (
                "Devanagari script requires explicit Hindi language context for Bloom validation; "
                "unconditional Indic bypass is disabled."
            )
        inferred = infer_bloom_level_hindi(question_text)
    else:
        inferred = infer_bloom_level(question_text)

    if target_clean not in BLOOM_HIERARCHY:
        return True, inferred, "Target Bloom level is non-standard; accepting."

    if inferred == target_clean:
        context_str = " (Hindi language context)" if has_devanagari else ""
        return True, inferred, f"Exact match for cognitive level '{target_clean}'{context_str}."

    t_val = BLOOM_HIERARCHY[target_clean]
    i_val = BLOOM_HIERARCHY[inferred]

    # Comparative distinctions ("distinguish between", "differentiate") are valid across Understand and Analyze
    q_low = question_text.lower()
    if target_clean in ("Understand", "Analyze"):
        if any(re.search(p, q_low) for p in [r"\bdistinguish\s+between\b", r"\bdifferentiate\s+between\b", r"\bdifference\s+between\b"]):
            return True, inferred, f"Comparative distinction is valid for '{target_clean}' in secondary curricula."
        if any(re.search(p, q_low) for p in [r"\bexplain\s+(the\s+)?(operational\s+|working\s+)?mechanism\b", r"\bhow\s+does\s+.*(operate|work|function)\b"]):
            return True, inferred, f"Mechanistic explanation is valid for '{target_clean}' in secondary curricula."
        if any(re.search(p, q_low) for p in [r"\bexplain\s+(the\s+)?(significance|importance|role|consequences?)\b"]):
            return True, inferred, f"Explaining significance or role is valid for '{target_clean}' in secondary curricula."

    # Adjacent levels (distance <= 1) are pedagogically acceptable in classroom contexts
    # EXCEPTION: "Remember" must NEVER accept high-order cognitive requests (Analyze, Evaluate, Create)
    if target_clean == "Remember" and i_val >= 4:
        return False, inferred, f"Question requires {inferred} (cognitive level {i_val}), which severely exceeds target Remember (level 1)."

    if target_clean in ("Evaluate", "Create") and i_val < t_val:
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
