import os
import re
from glob import glob
from pathlib import Path
from github_pipeline.utils.aws_utils import is_s3_enabled, bucket_name
import s3fs


def run_cleanup(verbose: bool = True):
    folders = ["raw", "processed", "features"]
    patterns = [
        r".*_(\d{4}-\d{2}-\d{2}-\d{2})\.parquet",
        r".*/(\d{4}-\d{2}-\d{2}-\d{2})\.json\.gz",
    ]

    all_files = []
    all_timestamps = set()
    file_timestamp_map = {}

    if is_s3_enabled():
        fs = s3fs.S3FileSystem()
        for folder in folders:
            prefix = f"{bucket_name}/{folder}/"
            try:
                files = fs.ls(prefix)
                for file in files:
                    for pattern in patterns:
                        match = re.search(pattern, file)
                        if match:
                            ts = match.group(1)
                            all_files.append(file)
                            all_timestamps.add(ts)
                            file_timestamp_map[file] = ts
                            break
            except FileNotFoundError:
                print(f"[CLEANUP] No files found in: {prefix} — skipping.")
    else:
        for folder in ["data/" + f for f in folders]:
            files = glob(f"{folder}/*")
            for file in files:
                for pattern in patterns:
                    match = re.search(pattern, file)
                    if match:
                        ts = match.group(1)
                        all_files.append(file)
                        all_timestamps.add(ts)
                        file_timestamp_map[file] = ts
                        break

    if not all_timestamps:
        print("[CLEANUP] No timestamped files found.")
        return

    # ✅ Always keep at least the 3 most recent timestamps
    keep_set = set(sorted(all_timestamps)[-3:])

    # ✅ Also keep last trained timestamp
    try:
        trained_ts = Path("models/last_trained.txt").read_text().strip()
        keep_set.add(trained_ts)
    except Exception:
        pass

    deleted = []
    for file in all_files:
        ts = file_timestamp_map.get(file)
        if ts and ts not in keep_set:
            try:
                if is_s3_enabled():
                    fs.rm(file)
                else:
                    os.remove(file)
                deleted.append(file)
            except Exception as e:
                print(f"[ERROR] Failed to delete {file}: {e}")

    if verbose:
        print(f"[CLEANUP] Deleted {len(deleted)} old files.")
        for f in deleted:
            print(f" - {f}")
        print(f"[CLEANUP] Retained timestamps: {sorted(keep_set)}")
