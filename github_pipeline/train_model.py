# github_pipeline/train_model.py

import argparse
import mlflow
from pathlib import Path
from glob import glob
import joblib
import re
import tempfile
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from github_pipeline.utils.aws_utils import (
    read_parquet,
    write_parquet,
    save_pickle,
    bucket_name,
    is_s3_enabled,
)


def run_training(timestamp: str):
    """
    Trains an Isolation Forest model for anomaly detection using actor features for a given timestamp.

    Steps:
    - Loads feature parquet file.
    - Scales the data and trains the model.
    - Computes anomaly scores and flags.
    - Logs parameters, metrics, and artifacts to MLflow.
    - Saves the model and prediction results to disk and registry.

    Outputs:
    - models/isolation_forest.pkl
    - models/last_trained.txt
    - data/features/actor_predictions_<timestamp>.parquet
    """

    print("[INFO] Starting model training...")

    input_file = f"features/actor_features_{timestamp}.parquet"
    output_file = f"features/actor_predictions_{timestamp}.parquet"
    model_file = "isolation_forest.pkl"

    experiment_name = "anomaly_detection_github"
    registered_model_name = "github-anomaly-isolation-forest"

    # Load features
    df = read_parquet(input_file)
    features = [
        "event_count",
        "pr_count",
        "issue_open_count",
        "fork_count",
        "repo_diversity",
    ]
    X = df[features].fillna(0)

    # Scale
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # MLflow experiment
    mlflow.set_tracking_uri("http://mlflow-server:5000")
    mlflow.set_experiment(experiment_name)
    with mlflow.start_run():
        mlflow.log_param("timestamp", timestamp)
        mlflow.log_param("model_type", "IsolationForest")
        mlflow.log_param("n_estimators", 100)

        model = IsolationForest(n_estimators=100, contamination=0.05, random_state=42)
        model.fit(X_scaled)

        # Predict
        df["anomaly_score"] = model.decision_function(X_scaled)
        df["anomaly"] = model.predict(X_scaled) == -1

        # Compute metrics
        mean_score = df["anomaly_score"].mean()
        std_score = df["anomaly_score"].std()
        anomaly_rate = df["anomaly"].mean()  # since anomaly is 0/1

        # Log metrics
        mlflow.log_metric("mean_anomaly_score", mean_score)
        mlflow.log_metric("std_anomaly_score", std_score)
        mlflow.log_metric("anomaly_rate", anomaly_rate)

        # Save model and scaler
        save_pickle((scaler, model), model_file)
        # For MLflow: save temporary local copy
        if is_s3_enabled():

            with tempfile.NamedTemporaryFile(delete=False, suffix=".pkl") as tmp_model:
                joblib.dump((scaler, model), tmp_model)
                mlflow.log_artifact(tmp_model.name)
        else:
            mlflow.log_artifact(f"models/{model_file}")

        # Also log model to registry
        mlflow.sklearn.log_model(
            model, artifact_path="model", registered_model_name=registered_model_name
        )

        # Save timestamp of training
        model_dir = Path("models")
        model_dir.mkdir(parents=True, exist_ok=True)
        with open(model_dir / "last_trained.txt", "w") as f:
            f.write(timestamp)

        # Save predictions
        write_parquet(df, output_file)

        # For MLflow: save temporary local copy
        if is_s3_enabled():
            import tempfile

            with tempfile.NamedTemporaryFile(
                delete=False, suffix=".parquet"
            ) as tmp_pred:
                df.to_parquet(tmp_pred.name, index=False)
                mlflow.log_artifact(tmp_pred.name)
        else:
            mlflow.log_artifact(f"data/{output_file}")

        print(df[["actor", "anomaly_score", "anomaly"]].head())

    print("[INFO] Training completed successfully.")


def main():
    """
    Automatically detect the latest available timestamp and run training.
    Supports both local and S3.
    """
    pattern = r"actor_features_(\d{4}-\d{2}-\d{2}-\d{2})\.parquet"
    timestamps = []

    if is_s3_enabled():
        import s3fs

        fs = s3fs.S3FileSystem()
        files = fs.ls(f"{bucket_name}/features/")
        print("[INFO] Searching for files on S3...")
        for f in files:
            match = re.search(pattern, f)
            if match:
                timestamps.append(match.group(1))
    else:
        print("[INFO] Searching for files locally...")
        files = glob("data/features/actor_features_*.parquet")
        for f in files:
            match = re.search(pattern, f)
            if match:
                timestamps.append(match.group(1))

    if not timestamps:
        raise RuntimeError("[ERROR] No valid feature files found.")

    latest_ts = sorted(timestamps)[-1]
    print(f"[INFO] Found latest timestamp: {latest_ts}")
    run_training(latest_ts)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--timestamp",
        help="Format: YYYY-MM-DD-HH. If not set, uses latest available file.",
    )
    args = parser.parse_args()

    if args.timestamp:
        run_training(args.timestamp)
    else:
        main()
