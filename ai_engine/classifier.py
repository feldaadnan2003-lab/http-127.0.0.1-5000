"""TF-IDF + Logistic Regression text classifier for government report categorization."""
import os

import joblib
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

from ai_engine.text_processor import preprocess

VECTORIZER_FILE = "tfidf_vectorizer.joblib"
MODEL_FILE = "logistic_regression_model.joblib"
METRICS_FILE = "training_metrics.joblib"


class ReportClassifier:
    """Wraps a TF-IDF vectorizer and a Logistic Regression classifier."""

    def __init__(self, model_dir: str):
        self.model_dir = model_dir
        self.vectorizer: TfidfVectorizer | None = None
        self.model: LogisticRegression | None = None
        self.metrics: dict = {}

    # ------------------------------------------------------------------
    # Training
    # ------------------------------------------------------------------
    def train(self, texts, labels, test_size: float = 0.2, random_state: int = 42):
        processed = [preprocess(t) for t in texts]

        x_train, x_test, y_train, y_test = train_test_split(
            processed, labels, test_size=test_size, random_state=random_state, stratify=labels
        )

        self.vectorizer = TfidfVectorizer(
            max_features=5000,
            ngram_range=(1, 2),
            min_df=1,
            sublinear_tf=True,
        )
        x_train_vec = self.vectorizer.fit_transform(x_train)
        x_test_vec = self.vectorizer.transform(x_test)

        self.model = LogisticRegression(
            max_iter=1000,
            C=5.0,
            class_weight="balanced",
        )
        self.model.fit(x_train_vec, y_train)

        train_accuracy = self.model.score(x_train_vec, y_train)
        test_accuracy = self.model.score(x_test_vec, y_test)

        self.metrics = {
            "train_accuracy": round(train_accuracy, 4),
            "test_accuracy": round(test_accuracy, 4),
            "n_samples": len(texts),
            "n_features": x_train_vec.shape[1],
            "classes": list(self.model.classes_),
        }
        return self.metrics

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------
    def save(self):
        os.makedirs(self.model_dir, exist_ok=True)
        joblib.dump(self.vectorizer, os.path.join(self.model_dir, VECTORIZER_FILE))
        joblib.dump(self.model, os.path.join(self.model_dir, MODEL_FILE))
        joblib.dump(self.metrics, os.path.join(self.model_dir, METRICS_FILE))

    def load(self):
        self.vectorizer = joblib.load(os.path.join(self.model_dir, VECTORIZER_FILE))
        self.model = joblib.load(os.path.join(self.model_dir, MODEL_FILE))
        metrics_path = os.path.join(self.model_dir, METRICS_FILE)
        self.metrics = joblib.load(metrics_path) if os.path.exists(metrics_path) else {}
        return self

    def is_ready(self) -> bool:
        return self.model is not None and self.vectorizer is not None

    # ------------------------------------------------------------------
    # Inference
    # ------------------------------------------------------------------
    def predict(self, raw_text: str) -> dict:
        if not self.is_ready():
            raise RuntimeError("Classifier model is not loaded. Run train_model.py first.")

        processed = preprocess(raw_text)
        vector = self.vectorizer.transform([processed])
        probabilities = self.model.predict_proba(vector)[0]
        classes = self.model.classes_

        best_idx = int(np.argmax(probabilities))
        category = classes[best_idx]
        confidence = float(probabilities[best_idx])

        ranked = sorted(
            zip(classes, probabilities), key=lambda kv: kv[1], reverse=True
        )
        top_predictions = [
            {"category": c, "probability": round(float(p), 4)} for c, p in ranked[:3]
        ]

        return {
            "category": category,
            "confidence": round(confidence, 4),
            "top_predictions": top_predictions,
        }


_classifier_instance: ReportClassifier | None = None


def get_classifier(model_dir: str) -> ReportClassifier:
    """Singleton accessor so the (relatively expensive) model is loaded once per process."""
    global _classifier_instance
    if _classifier_instance is None:
        _classifier_instance = ReportClassifier(model_dir)
        _classifier_instance.load()
    return _classifier_instance
