# github_pipeline/inference.py

import argparse
from glob import glob
import re
from github_pipeline.utils.aws_utils import (
    read_parquet,
    write_parquet,
    load_pickle,
    is_s3_enabled,
)


def run_inference(timestamp: str):
    """
    Runs anomaly inference on actor-level features using Isolation Forest.

    Input:  data/features/actor_features_{timestamp}.parquet
    Output: data/features/actor_predictions_{timestamp}.parquet
    """

    print(f"[INFO] Running inference for timestamp: {timestamp}")

    input_file = f"features/actor_features_{timestamp}.parquet"
    output_file = f"features/actor_predictions_{timestamp}.parquet"

    # Load data
    try:
        df = read_parquet(input_file)
    except FileNotFoundError:
        raise FileNotFoundError(f"[ERROR] Input file not found: {input_file}")

    features = [
        "event_count",
        "pr_count",
        "issue_open_count",
        "fork_count",
        "repo_diversity",
    ]
    X = df[features].fillna(0)

    # ✅ Load model
    try:
        scaler, model = load_pickle("isolation_forest.pkl")
    except FileNotFoundError:
        raise FileNotFoundError("[ERROR] Model file not found: isolation_forest.pkl")

    # ✅ Predict
    X_scaled = scaler.transform(X)
    preds = model.predict(X_scaled)
    scores = model.decision_function(X_scaled)

    df["anomaly_score"] = scores
    df["anomaly"] = preds == -1

    # Save output
    write_parquet(df, output_file)
    print(
        f"[INFO] Inference complete. Output saved to {'s3' if is_s3_enabled() else 'local'}: {output_file}"
    )


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
