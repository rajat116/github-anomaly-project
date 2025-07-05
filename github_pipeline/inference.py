# github_pipeline/inference.py

import argparse
import pandas as pd
import joblib
from pathlib import Path
from glob import glob
import re


def run_inference(timestamp: str):
    print(f"[INFO] Running inference for timestamp: {timestamp}")

    input_file = f"data/features/actor_features_{timestamp}.parquet"
    output_file = f"data/features/actor_predictions_{timestamp}.parquet"

    if not Path(input_file).exists():
        raise FileNotFoundError(f"[ERROR] Input file {input_file} not found.")

    # Load data
    df = pd.read_parquet(input_file)
    features = [
        "event_count",
        "pr_count",
        "issue_open_count",
        "fork_count",
        "repo_diversity",
    ]
    X = df[features].fillna(0)

    # ✅ Load model
    model_file = Path("models/isolation_forest.pkl")
    if not model_file.exists():
        raise FileNotFoundError(
            "[ERROR] Model file not found: models/isolation_forest.pkl"
        )

    scaler, model = joblib.load(model_file)

    # ✅ Predict
    X_scaled = scaler.transform(X)
    preds = model.predict(X_scaled)
    scores = model.decision_function(X_scaled)

    df["anomaly_score"] = scores
    df["anomaly"] = preds == -1

    # Save output
    df.to_parquet(output_file, index=False)
    print(f"[INFO] Inference complete. Output saved to {output_file}")


def main():
    # Auto-select the latest timestamp
    files = glob("data/features/actor_features_*.parquet")
    timestamps = []

    for f in files:
        match = re.search(r"actor_features_(\d{4}-\d{2}-\d{2}-\d{2})\.parquet", f)
        if match:
            timestamps.append(match.group(1))

    if not timestamps:
        raise RuntimeError("[ERROR] No feature parquet files found in data/features/")

    latest_ts = sorted(timestamps)[-1]
    print(f"[INFO] Using latest timestamp: {latest_ts}")
    run_inference(latest_ts)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--timestamp", help="Format: YYYY-MM-DD-HH (optional)")

    args = parser.parse_args()
    if args.timestamp:
        run_inference(args.timestamp)
    else:
        main()
