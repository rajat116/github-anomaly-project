from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import sys
import os
from pathlib import Path

# Ensure github_pipeline is in the PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'github_pipeline')))

from train_model import main as retrain_model

default_args = {
    'owner': 'rajat',
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id='weekly_model_retraining',
    default_args=default_args,
    description='Weekly retraining of Isolation Forest model on latest GitHub data',
    schedule_interval='@weekly',  # Runs every Sunday at midnight
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['retraining', 'ml', 'github'],
) as dag:

    retrain_task = PythonOperator(
        task_id='retrain_model',
        python_callable=retrain_model,
    )