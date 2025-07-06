# tests/test_train_model.py
import joblib
import pandas as pd
from github_pipeline.train_model import run_training
from unittest.mock import patch


@patch("github_pipeline.train_model.mlflow")
def test_run_training_end_to_end(mock_mlflow, tmp_path, monkeypatch):
    # ----------------------------
    # Step 1: Set up test timestamp and paths
    # ----------------------------
    timestamp = "2024-01-01-15"
    features_dir = tmp_path / "data" / "features"
    model_dir = tmp_path / "models"
    features_dir.mkdir(parents=True)
    model_dir.mkdir()

    input_file = features_dir / f"actor_features_{timestamp}.parquet"
    model_file = model_dir / "isolation_forest.pkl"
    output_file = features_dir / f"actor_predictions_{timestamp}.parquet"
    marker_file = model_dir / "last_trained.txt"

    # ----------------------------
    # Step 2: Create dummy data
    # ----------------------------
    df = pd.DataFrame(
        {
            "actor": ["user1", "user2"],
            "event_count": [5, 10],
            "pr_count": [1, 2],
            "issue_open_count": [0, 3],
            "fork_count": [1, 0],
            "repo_diversity": [0.5, 0.8],
        }
    )
    df.to_parquet(input_file)

    # ----------------------------
    # Step 3: Patch paths used by train_model
    # ----------------------------
    monkeypatch.chdir(tmp_path)  # change CWD to tmp_path

    # ----------------------------
    # Step 4: Run actual function
    # ----------------------------
    run_training(timestamp)

    # ----------------------------
    # Step 5: Assertions
    # ----------------------------
    assert model_file.exists(), "Model file not saved"
    assert output_file.exists(), "Output parquet not saved"
    assert marker_file.exists(), "Training timestamp not saved"

    scaler, model = joblib.load(model_file)
    assert hasattr(model, "predict"), "Model not valid"
    assert hasattr(scaler, "transform"), "Scaler not valid"

    df_pred = pd.read_parquet(output_file)
    assert "anomaly_score" in df_pred.columns
    assert "anomaly" in df_pred.columns
