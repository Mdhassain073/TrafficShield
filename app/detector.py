import numpy as np
from sklearn.ensemble import IsolationForest
from app.config import MODEL_CONTAMINATION, ALERT_THRESHOLD

class TrafficDetector:
    def __init__(self, contamination=MODEL_CONTAMINATION):
        self.model = IsolationForest(n_estimators=100, contamination=contamination, random_state=42)
        self.fitted = False

    def fit(self, X):
        self.model.fit(X)
        self.fitted = True

    def predict(self, X):
        if not self.fitted:
            raise ValueError("Model not trained. Call fit() first.")
        scores = -self.model.decision_function(X)
        labels = self.model.predict(X)
        return scores, labels

    def fit_predict(self, X):
        self.fit(X)
        return self.predict(X)

    def detect_suspicious(self, features_df):
        scores, labels = self.fit_predict(features_df)
        results = []

        print("📊 Anomaly detection output:")
        for ip, score, label in zip(features_df.index, scores, labels):
            status = "ANOMALOUS" if label == -1 else "NORMAL"
            print(f"🔎 {ip} | Score: {score:.3f} | Label: {label} ({status})")

            if label == -1 and score > ALERT_THRESHOLD:
                results.append((ip, score))

        return results
