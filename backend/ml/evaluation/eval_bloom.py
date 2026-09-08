"""
eval_bloom.py
Evaluation script for trained Bloom Taxonomy Classifier.
"""

import os
import json
import joblib
import pandas as pd
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, f1_score

MODEL_DIR = r"C:\Users\Divya\OneDrive\Desktop\AQPG\backend\ml\models\bloom_classifier"
UNIFIED_JSONL = r"C:\Users\Divya\OneDrive\Desktop\AQPG\datasets\unified\unified_questions.jsonl"

def evaluate_bloom_classifier():
    vec_path = os.path.join(MODEL_DIR, "tfidf_vectorizer.pkl")
    model_path = os.path.join(MODEL_DIR, "bloom_classifier_model.pkl")
    
    if not os.path.exists(vec_path) or not os.path.exists(model_path):
        print(f"[ERROR] Trained model files not found in {MODEL_DIR}. Please run train_bloom_classifier.py first!")
        return
        
    print("Loading vectorizer and model...")
    vectorizer = joblib.load(vec_path)
    model = joblib.load(model_path)
    
    # Load evaluation dataset
    records = []
    with open(UNIFIED_JSONL, "r", encoding="utf-8") as f:
        for line in f:
            records.append(json.loads(line))
            
    df = pd.DataFrame(records)
    valid_blooms = ["Remember", "Understand", "Apply", "Analyze", "Evaluate", "Create"]
    df_eval = df[df['bloom_level'].isin(valid_blooms)]
    
    print(f"\nEvaluating model performance on {len(df_eval)} labeled samples...")
    X_tfidf = vectorizer.transform(df_eval['question'].fillna(""))
    y_true = df_eval['bloom_level']
    y_pred = model.predict(X_tfidf)
    
    acc = accuracy_score(y_true, y_pred)
    f1_macro = f1_score(y_true, y_pred, average='macro')
    
    print("\n" + "=" * 80)
    print(f"OVERALL ACCURACY: {acc*100:.2f}% | MACRO F1-SCORE: {f1_macro:.4f}")
    print("=" * 80)
    print("\nCLASSIFICATION REPORT PER BLOOM CATEGORY:")
    print(classification_report(y_true, y_pred, digits=4))
    
    cm = confusion_matrix(y_true, y_pred, labels=valid_blooms)
    cm_df = pd.DataFrame(cm, index=valid_blooms, columns=valid_blooms)
    print("\nCONFUSION MATRIX:")
    print(cm_df)
    print("=" * 80)

if __name__ == "__main__":
    evaluate_bloom_classifier()
