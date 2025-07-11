# tests/test_pipeline_integration.py

import os
import re
import pandas as pd
from glob import glob
from pathlib import Path
from github_pipeline.feature_engineering import run_feature_engineering
from github_pipeline.inference import run_inference


def test_pipeline_local_end_to_end():
    """
    Integration test for the local pipeline:
    - Loads latest processed data
    - Runs feature engineering
    - Runs inference using pre-trained model
    - Verifies that outputs are created correctly
    """

    # Ensure S3 is not enabled for local test
    assert (
        os.getenv("USE_S3", "false").lower() == "false"
    ), "USE_S3 must be false for local integration test"

    # Get latest available processed data file
    processed_files = sorted(glob("data/processed/*.parquet"))
    assert processed_files, "[ERROR] No processed files found in 'data/processed/'."

    latest_file = processed_files[-1]
    match = re.search(r"(\d{4}-\d{2}-\d{2}-\d{2})\.parquet", latest_file)
    assert match, "[ERROR] Could not extract timestamp from latest file name."

    timestamp = match.group(1)
    print(f"[INFO] Running integration test with timestamp: {timestamp}")

    # Define expected paths
    features_path = Path(f"data/features/actor_features_{timestamp}.parquet")
    predictions_path = Path(f"data/features/actor_predictions_{timestamp}.parquet")
    model_path = Path("models/isolation_forest.pkl")

    # Ensure model exists
    assert model_path.exists(), f"[ERROR] Model file not found: {model_path}"

    # Run feature engineering if not already done
    if not features_path.exists():
        run_feature_engineering(timestamp)
    assert features_path.exists(), "[FAIL] Features file was not created."

    # Run inference if not already done
    if not predictions_path.exists():
        run_inference(timestamp)
    assert predictions_path.exists(), "[FAIL] Predictions file was not created."

    # Optionally, verify predictions contain expected columns
    df_pred = pd.read_parquet(predictions_path)
    required_cols = {"actor", "anomaly_score", "anomaly"}
    assert required_cols.issubset(
        df_pred.columns
    ), "[FAIL] Missing expected columns in prediction output."

    print("✅ Integration test passed.")
