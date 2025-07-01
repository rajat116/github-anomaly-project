import gzip
import json
import pandas as pd
from pathlib import Path

def parse_gharchive_json_gz(filepath, max_events=100_000):
    """
    Parse a GitHub Archive .json.gz file into a DataFrame
    """
    rows = []

    with gzip.open(filepath, 'rt', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if i >= max_events:
                break
            try:
                event = json.loads(line)
                row = {
                    "id": event.get("id"),
                    "type": event.get("type"),
                    "created_at": event.get("created_at"),
                    "repo": event.get("repo", {}).get("name"),
                    "actor": event.get("actor", {}).get("login"),
                }
                rows.append(row)
            except json.JSONDecodeError:
                continue

    return pd.DataFrame(rows)

if __name__ == "__main__":
    input_file = "data/raw/2024-01-01-15.json.gz"
    output_file = "data/processed/2024-01-01-15.parquet"

    df = parse_gharchive_json_gz(input_file)
    print(df.head())
    print(f"Parsed {len(df)} events")

    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(output_file, index=False)
    print(f"Saved structured data to {output_file}")
