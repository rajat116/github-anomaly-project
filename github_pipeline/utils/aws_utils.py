# github_pipeline/utils/aws_utils.py

import os
import s3fs
import pandas as pd
import joblib
import tempfile
from dotenv import load_dotenv

load_dotenv()

bucket_name = os.getenv("S3_BUCKET_NAME")
use_s3_env = os.getenv("USE_S3", "true").lower() == "true"


def is_s3_enabled():
    return bucket_name is not None and use_s3_env


def get_s3_path(relative_path):
    return f"s3://{bucket_name}/{relative_path}"


def write_parquet(df, relative_path):
    if is_s3_enabled():
        fs = s3fs.S3FileSystem(anon=False)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".parquet") as tmp:
            df.to_parquet(tmp.name, index=False)
            fs.put(tmp.name, get_s3_path(relative_path))
            os.remove(tmp.name)
    else:
        local_path = f"data/{relative_path}"
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        df.to_parquet(local_path, index=False)


def read_parquet(relative_path):
    if is_s3_enabled():
        return pd.read_parquet(
            get_s3_path(relative_path), storage_options={"anon": False}
        )
    else:
        local_path = f"data/{relative_path}"
        return pd.read_parquet(local_path)


def save_pickle(obj, relative_path):
    if is_s3_enabled():
        fs = s3fs.S3FileSystem(anon=False)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pkl") as tmp:
            joblib.dump(obj, tmp)
            tmp_path = tmp.name
        fs.put(tmp_path, get_s3_path(f"models/{relative_path}"))
        os.remove(tmp_path)
    else:
        local_path = f"models/{relative_path}"
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        with open(local_path, "wb") as f:
            joblib.dump(obj, f)


def load_pickle(relative_path):
    if is_s3_enabled():
        fs = s3fs.S3FileSystem(anon=False)
        path = get_s3_path(f"models/{relative_path}")
        with fs.open(path, "rb") as f:
            return joblib.load(f)
    else:
        local_path = f"models/{relative_path}"
        with open(local_path, "rb") as f:
            return joblib.load(f)
