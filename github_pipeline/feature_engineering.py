# github_pipeline/feature_engineering.py

import pandas as pd
import argparse
from pathlib import Path
from glob import glob
import re


def run_feature_engineering(timestamp: str):
    input_file = f"data/processed/{timestamp}.parquet"
    output_file = f"data/features/actor_features_{timestamp}.parquet"

    if not Path(input_file).exists():
        raise FileNotFoundError(f"[ERROR] Input file {input_file} does not exist")

    df = pd.read_parquet(input_file)
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
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    agg.to_parquet(output_file, index=False)

    print(f"[INFO] Saved engineered features to: {output_file}")
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
