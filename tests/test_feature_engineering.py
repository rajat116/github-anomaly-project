# tests/test_feature_engineering.py

import pandas as pd
from github_pipeline.feature_engineering import run_feature_engineering


def test_run_feature_engineering(tmp_path, monkeypatch):
    # ----------------------------
    # Step 1: Setup test timestamp and paths
    # ----------------------------
    timestamp = "2024-01-01-15"
    input_dir = tmp_path / "data" / "processed"
    output_dir = tmp_path / "data" / "features"
    input_dir.mkdir(parents=True)

    input_file = input_dir / f"{timestamp}.parquet"
    output_file = output_dir / f"actor_features_{timestamp}.parquet"

    # ----------------------------
    # Step 2: Create dummy GitHub-like event data
    # ----------------------------
    df = pd.DataFrame(
        {
            "actor": ["user1", "user1", "user2"],
            "created_at": [
                "2024-01-01T15:10:00Z",
                "2024-01-01T15:20:00Z",
                "2024-01-01T15:30:00Z",
            ],
            "type": ["PullRequestEvent", "IssueCommentEvent", "ForkEvent"],
            "repo": ["repo1", "repo2", "repo3"],
        }
    )
    df.to_parquet(input_file)

    # ----------------------------
    # Step 3: Change CWD so script reads from local path
    # ----------------------------
    monkeypatch.chdir(tmp_path)

    # ----------------------------
    # Step 4: Run the function
    # ----------------------------
    run_feature_engineering(timestamp)

    # ----------------------------
    # Step 5: Assert expected output
    # ----------------------------
    assert output_file.exists(), "Output file not created"

    df_out = pd.read_parquet(output_file)
    expected_cols = {
        "actor",
        "timestamp_hour",
        "event_count",
        "pr_count",
        "issue_open_count",
        "fork_count",
        "repo_diversity",
    }
    assert expected_cols.issubset(df_out.columns), "Missing expected output columns"
    assert len(df_out) > 0, "No rows generated in output"
