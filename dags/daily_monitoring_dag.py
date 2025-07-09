from airflow import DAG
from airflow.operators.python import PythonOperator
from github_pipeline.utils.aws_utils import is_s3_enabled, bucket_name
from datetime import datetime, timedelta
from monitor import run_monitoring
from pathlib import Path
import re
from glob import glob
import sys
import s3fs

"""
DAG: daily_monitoring_dag

This Airflow DAG runs daily monitoring on GitHub features.

Tasks:
- 🧪 Compare the two latest feature files to detect data drift using Evidently
- 🚨 Trigger alerts via Slack and Email if drift or anomaly spikes are detected
- 📊 Save drift reports as JSON and HTML in the reports/ directory

This DAG complements the daily inference DAG by validating data quality and stability.
"""

# Add github_pipeline to PYTHONPATH
sys.path.append(str(Path(__file__).resolve().parents[1] / "github_pipeline"))

default_args = {
    "owner": "rajat",
    "retries": 1,
    "retry_delay": timedelta(minutes=2),
}


def get_two_latest_timestamps():
    """
    Get the two latest available feature timestamps.
    Supports both local and S3.
    Returns: (reference_ts, current_ts)
    """
    timestamps = []
    pattern = r"actor_features_(\d{4}-\d{2}-\d{2}-\d{2})\.parquet"

    if is_s3_enabled():
        fs = s3fs.S3FileSystem()
        files = fs.ls(f"{bucket_name}/features/")
        for file in files:
            if "actor_features" in file:
                match = re.search(pattern, file)
                if match:
                    timestamps.append(match.group(1))
    else:
        files = glob("data/features/actor_features_*.parquet")
        for file in files:
            match = re.search(pattern, file)
            if match:
                timestamps.append(match.group(1))

    timestamps = sorted(timestamps)
    if len(timestamps) < 2:
        raise RuntimeError(
            "[ERROR] Need at least two feature files for drift monitoring."
        )

    return timestamps[-2], timestamps[-1]


def run_monitoring_wrapper(**kwargs):
    """
    Run monitoring using two latest available timestamps.
    """
    ref_ts, cur_ts = get_two_latest_timestamps()
    print(f"[INFO] Monitoring drift: ref={ref_ts}, current={cur_ts}")
    run_monitoring(reference_ts=ref_ts, current_ts=cur_ts)


with DAG(
    dag_id="daily_monitoring_dag",
    default_args=default_args,
    description="Run daily monitoring for drift and quality",
    schedule_interval="@daily",
    start_date=datetime(2025, 7, 2),
    catchup=False,
    tags=["github", "monitoring"],
) as dag:

    monitor_task = PythonOperator(
        task_id="run_drift_monitoring",
        python_callable=run_monitoring_wrapper,
    )
