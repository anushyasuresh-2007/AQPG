"""
bloom_service.py
Service for classifying question text into Bloom's Taxonomy levels using the trained ML model.
"""

import os
import joblib
from typing import Dict, Any, Optional

MODEL_DIR = r"C:\Users\Divya\OneDrive\Desktop\AQPG\backend\ml\models\bloom_classifier"

_vectorizer = None
_classifier = None

def _load_model():
    global _vectorizer, _classifier
    if _vectorizer is None or _classifier is None:
        vec_path = os.path.join(MODEL_DIR, "tfidf_vectorizer.pkl")
        model_path = os.path.join(MODEL_DIR, "bloom_classifier_model.pkl")
        
        if os.path.exists(vec_path) and os.path.exists(model_path):
            _vectorizer = joblib.load(vec_path)
            _classifier = joblib.load(model_path)
        else:
            _vectorizer = False
            _classifier = False

def predict_bloom_level(question_text: str) -> Dict[str, Any]:
    """
    Predicts Bloom's taxonomy level for a given question string.
    Returns dictionary with predicted level and confidence probabilities.
    """
    _load_model()
    
    if not question_text or not question_text.strip():
        return {"bloom_level": "Understand", "confidence": 0.0, "source": "fallback"}
        
    if _vectorizer and _classifier:
        try:
            X = _vectorizer.transform([question_text.strip()])
            predicted_class = _classifier.predict(X)[0]
            
            # Predict probabilities if supported
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
            print(f"[bloom_service] Error during classification: {e}")
            
    # Rule-based action-verb heuristic fallback if ML model is unavailable
    q_lower = question_text.lower()
    if any(verb in q_lower for verb in ["define", "list", "state", "recall", "name", "who", "when", "where", "what is"]):
        level = "Remember"
    elif any(verb in q_lower for verb in ["explain", "describe", "summarize", "contrast", "discuss", "illustrate"]):
        level = "Understand"
    elif any(verb in q_lower for verb in ["calculate", "solve", "apply", "compute", "determine", "find", "implement"]):
        level = "Apply"
    elif any(verb in q_lower for verb in ["analyze", "compare", "differentiate", "examine", "distinguish"]):
        level = "Analyze"
    elif any(verb in q_lower for verb in ["evaluate", "assess", "justify", "critique", "judge", "validate"]):
        level = "Evaluate"
    elif any(verb in q_lower for verb in ["design", "construct", "formulate", "create", "develop", "propose"]):
        level = "Create"
    else:
        level = "Understand"
        
    return {
        "bloom_level": level,
        "confidence": 0.6,
        "probabilities": {},
        "source": "heuristic_rule"
    }

if __name__ == "__main__":
    res1 = predict_bloom_level("Define compound interest.")
    print("Test 1:", res1)
    res2 = predict_bloom_level("Calculate the momentum of a 50kg vehicle moving at 20 m/s.")
    print("Test 2:", res2)
