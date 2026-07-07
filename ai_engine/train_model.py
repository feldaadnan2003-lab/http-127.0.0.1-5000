"""Trains the TF-IDF + Logistic Regression classifier and persists it to disk.

Usage:
    python ai_engine/train_model.py
"""
import os
import sys

import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ai_engine.classifier import ReportClassifier  # noqa: E402

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATASET_PATH = os.path.join(BASE_DIR, "data", "dataset.csv")
MODEL_DIR = os.path.join(BASE_DIR, "ai_engine", "saved_models")


def main():
    if not os.path.exists(DATASET_PATH):
        print("Dataset not found, generating it first...")
        from data.generate_dataset import main as generate_main
        generate_main()

    df = pd.read_csv(DATASET_PATH)
    df = df.dropna(subset=["text", "category"])

    print(f"Loaded {len(df)} samples across {df['category'].nunique()} categories.")

    classifier = ReportClassifier(MODEL_DIR)
    metrics = classifier.train(df["text"].tolist(), df["category"].tolist())
    classifier.save()

    print("Training complete.")
    print(f"  Train accuracy : {metrics['train_accuracy'] * 100:.2f}%")
    print(f"  Test accuracy  : {metrics['test_accuracy'] * 100:.2f}%")
    print(f"  Feature count  : {metrics['n_features']}")
    print(f"  Classes        : {', '.join(metrics['classes'])}")
    print(f"Model artifacts saved to: {MODEL_DIR}")


if __name__ == "__main__":
    main()
