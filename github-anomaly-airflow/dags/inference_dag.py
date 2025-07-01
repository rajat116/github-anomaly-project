from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import pandas as pd
import pickle, os, yaml

with open('/opt/airflow/config.yaml') as f:
    config = yaml.safe_load(f)

def run_batch_inference():
    model_path = config['model_path']
    feature_dir = config['feature_dir']
    prediction_dir = config['prediction_dir']

    with open(model_path, 'rb') as f:
        model = pickle.load(f)

    files = sorted(os.listdir(feature_dir))
    if not files:
        raise FileNotFoundError("No feature files found.")
    latest_file = os.path.join(feature_dir, files[-1])
    df = pd.read_parquet(latest_file)
    df['anomaly_score'] = model.decision_function(df.drop(columns=['timestamp'], errors='ignore'))

    ts = datetime.utcnow().strftime('%Y-%m-%d-%H')
    os.makedirs(prediction_dir, exist_ok=True)
    df.to_csv(os.path.join(prediction_dir, f"{ts}.csv"), index=False)
    print("✅ Inference complete")

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id='github_anomaly_inference',
    default_args=default_args,
    schedule_interval='@daily',
    catchup=False,
    tags=['github', 'inference'],
) as dag:
    task = PythonOperator(task_id='run_batch_inference', python_callable=run_batch_inference)
