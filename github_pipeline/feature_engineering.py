# github_pipeline/feature_engineering.py

import pandas as pd
import argparse
from glob import glob
import re
from github_pipeline.utils.aws_utils import (
    read_parquet,
    write_parquet,
    is_s3_enabled,
)


def run_feature_engineering(timestamp: str):
    """
    Generates actor-level hourly features from GitHub event logs
    for a given timestamp and saves them as a Parquet file.

    Input:  data/processed/{timestamp}.parquet
    Output: data/features/actor_features_{timestamp}.parquet
    """

    input_file = f"processed/{timestamp}.parquet"
    output_file = f"features/actor_features_{timestamp}.parquet"

    try:
        df = read_parquet(input_file)
    except FileNotFoundError:
        raise FileNotFoundError(f"[ERROR] Input file does not exist: {input_file}")

    df["created_at"] = pd.to_datetime(df["created_at"])

    # Floor timestamps to hourly
    df["timestamp_hour"] = df["created_at"].dt.floor("h")

    # Tag event types
    df["is_pr"] = df["type"] == "PullRequestEvent"
    df["is_issue"] = df["type"].str.contains("Issue", na=False)
    df["is_fork"] = df["type"] == "ForkEvent"

    # Group by actor + hour
    agg = (
        df.groupby(["actor", "timestamp_hour"])
        .agg(
            event_count=("type", "count"),
            pr_count=("is_pr", "sum"),
            issue_open_count=("is_issue", "sum"),
            fork_count=("is_fork", "sum"),
            repo_diversity=("repo", pd.Series.nunique),
        )
        .reset_index()
    )

    # Save output
    write_parquet(agg, output_file)
    print(
        f"[INFO] Saved engineered features to: {'s3' if is_s3_enabled() else 'local'} → {output_file}"
    )
    print(agg.head())


def main():
    files = glob("data/processed/*.parquet")
    timestamps = []

    for f in files:
        match = re.search(r"(\d{4}-\d{2}-\d{2}-\d{2})\.parquet", f)
        if match:
            timestamps.append(match.group(1))

    if not timestamps:
        raise RuntimeError("[ERROR] No valid processed data files found.")

    latest_ts = sorted(timestamps)[-1]
    print(f"[INFO] Using latest processed timestamp: {latest_ts}")
    run_feature_engineering(latest_ts)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--timestamp", help="Format: YYYY-MM-DD-HH (optional)")
    args = parser.parse_args()

    if args.timestamp:
        run_feature_engineering(args.timestamp)
    else:
        main()
