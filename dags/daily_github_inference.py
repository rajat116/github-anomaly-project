from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

from github_pipeline.parse_gharchive import run_ingestion
from github_pipeline.feature_engineering import run_feature_engineering
from github_pipeline.inference import run_inference
from github_pipeline.cleanup import run_cleanup


def get_yesterday_fixed_hour(ds: str, hour: int = 15) -> str:
    """
    Returns timestamp string in 'YYYY-MM-DD-HH' format for (ds - 1 day) at given hour.
    """
    dt = datetime.strptime(ds, "%Y-%m-%d") - timedelta(days=1)
    return dt.replace(hour=hour).strftime("%Y-%m-%d-%H")


def run_ingestion_wrapper(ds, **kwargs):
    ts = get_yesterday_fixed_hour(ds)
    run_ingestion(timestamp=ts)


def run_feature_engineering_wrapper(ds, **kwargs):
    ts = get_yesterday_fixed_hour(ds)
    run_feature_engineering(timestamp=ts)


def run_inference_wrapper(ds, **kwargs):
    ts = get_yesterday_fixed_hour(ds)
    run_inference(timestamp=ts)


default_args = {
    "owner": "rajat",
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="daily_github_inference",
    default_args=default_args,
    description="Fully automated daily GitHub inference pipeline",
    schedule_interval="@daily",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["github", "anomaly"],
) as dag:

    task_ingest = PythonOperator(
        task_id="download_and_parse_github_data",
        python_callable=run_ingestion_wrapper,
        provide_context=True,
    )

    task_feature_engineering = PythonOperator(
        task_id="run_feature_engineering",
        python_callable=run_feature_engineering_wrapper,
        provide_context=True,
    )

    task_inference = PythonOperator(
        task_id="run_model_inference",
        python_callable=run_inference_wrapper,
        provide_context=True,
    )

    task_cleanup = PythonOperator(  # ✅ NEW
        task_id="cleanup_old_files",
        python_callable=run_cleanup,
    )

    task_ingest >> task_feature_engineering >> task_inference >> task_cleanup
