# scripts/feature_engineering.py

import pandas as pd
import os

# Load raw GitHub event data
input_file = "data/processed/2024-01-01-15.parquet"
output_file = "data/features/actor_features_2024-01-01-15.parquet"

df = pd.read_parquet(input_file)
df["created_at"] = pd.to_datetime(df["created_at"])

# Floor timestamps to hourly
df["timestamp_hour"] = df["created_at"].dt.floor("h")

# Add a column for counting PRs
df["is_pr"] = df["type"] == "PullRequestEvent"
df["is_issue"] = df["type"].str.contains("Issue")
df["is_fork"] = df["type"] == "ForkEvent"

# Group by actor and hour
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

# Save features
os.makedirs(os.path.dirname(output_file), exist_ok=True)
agg.to_parquet(output_file, index=False)
print(f"Saved features to: {output_file}")
print(agg.head())
