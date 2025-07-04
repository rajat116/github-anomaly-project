# github_pipeline/parse_gharchive.py

import gzip
import json
import argparse
import pandas as pd
from pathlib import Path
from urllib.request import urlretrieve
from datetime import datetime, timedelta


def get_latest_available_timestamp() -> str:
    """
    Returns the most recent past hour timestamp in format YYYY-MM-DD-HH (UTC)
    """
    dt = datetime.utcnow() - timedelta(hours=1)
    return dt.strftime("%Y-%m-%d-%H")


def download_gharchive_json_gz(timestamp: str, output_dir: str = "data/raw") -> str:
    """
    Download GitHub Archive .json.gz file for a given timestamp like '2024-01-01-16'
    """
    year, month, day, hour = timestamp.split("-")
    url = f"https://data.gharchive.org/{year}-{month}-{day}-{hour}.json.gz"

    Path(output_dir).mkdir(parents=True, exist_ok=True)
    out_path = f"{output_dir}/{timestamp}.json.gz"

    if Path(out_path).exists():
        print(f"[INFO] Raw file already exists: {out_path}")
    else:
        urlretrieve(url, out_path)
        print(f"[INFO] Downloaded {url} to {out_path}")
    return out_path


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


def run_ingestion(timestamp: str = None, max_events: int = 100_000) -> str:
    """
    Main function to download, parse, and save GitHub event data.
    Returns path to saved processed file.
    """
    if timestamp is None:
        timestamp = get_latest_available_timestamp()

    print(f"[INFO] Starting ingestion for timestamp: {timestamp}")
    raw_path = download_gharchive_json_gz(timestamp)
    df = parse_gharchive_json_gz(raw_path, max_events=max_events)

    out_dir = Path("data/processed")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{timestamp}.parquet"
    df.to_parquet(out_path, index=False)

    print(f"[INFO] Parsed {len(df)} events")
    print(f"[INFO] Saved structured data to {out_path}")
    return str(out_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--timestamp", help="Format: YYYY-MM-DD-HH. If not provided, uses latest.")
    args = parser.parse_args()

    run_ingestion(timestamp=args.timestamp)