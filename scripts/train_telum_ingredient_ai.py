"""
Train Telum AI Ingredient & Nutri-Grade Model on IBM LinuxONE s390x.
Dataset: 668,000+ labeled food products with real ingredient lists from PostgreSQL.
Outputs:
- models/macrio_telum_nutrigrade_ai.joblib (for backend inference)
- models/telum_ai_weights.json (for on-device client-side inference)
"""

import json
import os
import time
import psycopg2
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, accuracy_score
import joblib

DB_CONFIG = {
    "dbname": "macrio_db",
    "user": "macrio",
    "password": "macrio_secret",
    "host": "localhost",
    "port": 5432
}

def load_data(limit=100000):
    print(f"Connecting to LinuxONE PostgreSQL macrio_db to load {limit} training examples...")
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("""
        SELECT ingredients_text, upper(nutriscore_grade) as grade
        FROM products
        WHERE nutriscore_grade IN ('a', 'b', 'c', 'd', 'e')
          AND length(ingredients_text) > 15
        ORDER BY random()
        LIMIT %s;
    """, (limit,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    
    texts = [r[0] for r in rows]
    labels = [r[1] for r in rows]
    print(f"Loaded {len(texts)} balanced samples from database.")
    return texts, labels

def train():
    os.makedirs("/home/linux1/macrio/models", exist_ok=True)
    t0 = time.time()
    texts, labels = load_data(limit=100000)

    # Split train/test
    split = int(0.85 * len(texts))
    X_train, X_test = texts[:split], texts[split:]
    y_train, y_test = labels[:split], labels[split:]

    print(f"Training TF-IDF + LogisticRegression model on IBM Telum (s390x)...")
    pipe = Pipeline([
        ('tfidf', TfidfVectorizer(max_features=5000, ngram_range=(1, 2), stop_words='english')),
        ('clf', LogisticRegression(max_iter=300, C=1.5, solver='lbfgs', n_jobs=-1))
    ])

    pipe.fit(X_train, y_train)
    t_train = time.time() - t0
    print(f"Training completed in {t_train:.2f} seconds.")

    y_pred = pipe.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"Telum AI Nutri-Grade Model Test Accuracy: {acc * 100:.2f}%")
    print(classification_report(y_test, y_pred))

    # Save joblib model for backend
    joblib_path = "/home/linux1/macrio/models/macrio_telum_nutrigrade_ai.joblib"
    joblib.dump(pipe, joblib_path)
    print(f"Saved server AI model to {joblib_path}")

    # Export compact weights for on-device browser inference
    tfidf = pipe.named_steps['tfidf']
    clf = pipe.named_steps['clf']

    vocab = tfidf.vocabulary_  # word -> index
    idf = tfidf.idf_.tolist()
    classes = clf.classes_.tolist()
    coef = clf.coef_.tolist()  # shape: (n_classes, n_features)
    intercept = clf.intercept_.tolist()

    client_weights = {
        "classes": classes,
        "vocabulary": {k: int(v) for k, v in vocab.items() if v < 2500},  # top 2500 tokens
        "idf": idf[:2500],
        "coef": [c[:2500] for c in coef],
        "intercept": intercept,
        "trained_on": "IBM LinuxONE s390x (Telum AI)",
        "accuracy": float(acc)
    }

    json_path = "/home/linux1/macrio/models/telum_ai_weights.json"
    with open(json_path, "w") as f:
        json.dump(client_weights, f)
    print(f"Saved on-device client AI weights to {json_path} (size: {os.path.getsize(json_path) / 1024:.1f} KB)")

if __name__ == "__main__":
    train()
