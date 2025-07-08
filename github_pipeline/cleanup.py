import os
from glob import glob
import re
from pathlib import Path


def run_cleanup(verbose: bool = True):
    """
    Delete all old files from data folders except:
    - Last 2 timestamps
    - The timestamp used in latest model training (stored in models/last_trained.txt)
    """

    folders = [
        "data/raw",
        "data/processed",
        "data/features",
    ]

    patterns = [
        r".*_(\d{4}-\d{2}-\d{2}-\d{2})\.parquet",
        r".*/(\d{4}-\d{2}-\d{2}-\d{2})\.json\.gz",
    ]

    # Detect all timestamps
    all_timestamps = set()
    for folder in folders:
        for file in glob(f"{folder}/*"):
            for pattern in patterns:
                match = re.search(pattern, file)
                if match:
                    all_timestamps.add(match.group(1))

    if not all_timestamps:
        print("[CLEANUP] No timestamped files found.")
        return

    keep_set = set(sorted(all_timestamps)[-2:])  # Keep last 2 by default

    # Add model-trained timestamp
    model_info = Path("models/last_trained.txt")
    if model_info.exists():
        trained_ts = model_info.read_text().strip()
        keep_set.add(trained_ts)

    deleted = []

    # Delete files not in keep_set
    for folder in folders:
        for file in glob(f"{folder}/*"):
            ts = None
            for pattern in patterns:
                match = re.search(pattern, file)
                if match:
                    ts = match.group(1)
                    break
            if ts and ts not in keep_set:
                try:
                    os.remove(file)
                    deleted.append(file)
                except Exception as e:
                    print(f"[ERROR] Failed to delete {file}: {e}")

    if verbose:
        print(f"[CLEANUP] Deleted {len(deleted)} old files.")
        for f in deleted:
            print(f" - {f}")
        print(f"[CLEANUP] Retained timestamps: {sorted(keep_set)}")
