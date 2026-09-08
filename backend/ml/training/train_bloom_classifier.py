"""
train_bloom_classifier.py
Trains Bloom's Taxonomy Classifier on 17,800+ annotated questions from the unified dataset.
Saves model pipeline artifacts to backend/ml/models/bloom_classifier/
"""

import os
import json
import joblib
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, accuracy_score, f1_score

UNIFIED_JSONL = r"C:\Users\Divya\OneDrive\Desktop\AQPG\datasets\unified\unified_questions.jsonl"
MODEL_DIR = r"C:\Users\Divya\OneDrive\Desktop\AQPG\backend\ml\models\bloom_classifier"

VALID_BLOOMS = ["Remember", "Understand", "Apply", "Analyze", "Evaluate", "Create"]

def train_bloom_classifier():
    os.makedirs(MODEL_DIR, exist_ok=True)
    
    print("=" * 80)
    print("TRAINING BLOOM'S TAXONOMY CLASSIFIER")
    print("=" * 80)
    
    # 1. Load Unified Dataset
    records = []
    with open(UNIFIED_JSONL, "r", encoding="utf-8") as f:
        for line in f:
            records.append(json.loads(line))
            
    df = pd.DataFrame(records)
    print(f"Loaded {len(df)} total unified records.")
    
    # 2. Filter Labeled Samples
    df_labeled = df[df['bloom_level'].isin(VALID_BLOOMS)].copy()
    print(f"Labeled samples available for training: {len(df_labeled)}")
    print("\nClass distribution:")
    print(df_labeled['bloom_level'].value_counts())
    
    X = df_labeled['question'].fillna("")
    y = df_labeled['bloom_level']
    
    # 3. Train / Test Split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )
    print(f"\nTrain set: {len(X_train)} samples | Test set: {len(X_test)} samples")
    
    # 4. TF-IDF Vectorization
    print("\nExtracting TF-IDF features (ngram_range=(1,2), max_features=25000)...")
    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        max_features=25000,
        sublinear_tf=True,
        stop_words='english'
    )
    X_train_tfidf = vectorizer.fit_transform(X_train)
    X_test_tfidf = vectorizer.transform(X_test)
    
    # 5. Train Classifier (Logistic Regression with balanced class weights)
    print("Training Logistic Regression Classifier...")
    clf = LogisticRegression(
        C=2.0,
        max_iter=1000,
        class_weight='balanced',
        solver='saga',
        random_state=42,
        n_jobs=-1
    )
    clf.fit(X_train_tfidf, y_train)
    
    # 6. Evaluate
    y_pred = clf.predict(X_test_tfidf)
    acc = accuracy_score(y_test, y_pred)
    f1_macro = f1_score(y_test, y_pred, average='macro')
    
    print("\n" + "=" * 80)
    print(f"EVALUATION METRICS (Accuracy: {acc*100:.2f}%, Macro F1: {f1_macro:.4f})")
    print("=" * 80)
    report_str = classification_report(y_test, y_pred, digits=4)
    print(report_str)
    
    # 7. Save Model Artifacts
    vec_path = os.path.join(MODEL_DIR, "tfidf_vectorizer.pkl")
    model_path = os.path.join(MODEL_DIR, "bloom_classifier_model.pkl")
    meta_path = os.path.join(MODEL_DIR, "bloom_model_metadata.json")
    
    joblib.dump(vectorizer, vec_path)
    joblib.dump(clf, model_path)
    
    metadata = {
        "model_type": "TF-IDF + LogisticRegression (Balanced)",
        "train_samples": len(X_train),
        "test_samples": len(X_test),
        "accuracy": acc,
        "f1_macro": f1_macro,
        "classes": list(clf.classes_),
        "vectorizer_features": len(vectorizer.vocabulary_)
    }
    
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
        
    print(f"\n[SUCCESS] Vectorizer saved to: {vec_path}")
    print(f"[SUCCESS] Classifier saved to: {model_path}")
    print(f"[SUCCESS] Metadata saved to: {meta_path}")
    
    # 8. Enrich Unlabeled Records in Unified Dataset
    print("\n" + "=" * 80)
    print("ENRICHING UNLABELED RECORDS WITH PREDICTED BLOOM LEVELS")
    print("=" * 80)
    
    unlabeled_mask = df['bloom_level'].isnull() | (~df['bloom_level'].isin(VALID_BLOOMS))
    num_unlabeled = unlabeled_mask.sum()
    
    if num_unlabeled > 0:
        X_unlabeled_tfidf = vectorizer.transform(df.loc[unlabeled_mask, 'question'].fillna(""))
        df.loc[unlabeled_mask, 'bloom_level'] = clf.predict(X_unlabeled_tfidf)
        print(f"Predicted & updated Bloom taxonomy levels for {num_unlabeled} unannotated records!")
        
        # Overwrite unified JSONL & CSV with fully labeled records
        updated_records = df.to_dict(orient="records")
        with open(UNIFIED_JSONL, "w", encoding="utf-8") as f:
            for rec in updated_records:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        print(f"[SUCCESS] Updated unified JSONL with 100% Bloom predictions: {UNIFIED_JSONL}")
        
    return metadata

if __name__ == "__main__":
    train_bloom_classifier()
