from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import pandas as pd
import pickle, os, yaml
from sklearn.ensemble import IsolationForest

with open('/opt/airflow/config.yaml') as f:
    config = yaml.safe_load(f)

def retrain_model():
    feature_dir = config['feature_dir']
    model_path = config['model_path']

    files = sorted(os.listdir(feature_dir))
    if not files:
        raise FileNotFoundError("No feature files to retrain on.")
    dfs = [pd.read_parquet(os.path.join(feature_dir, f)) for f in files]
    df = pd.concat(dfs)
    X = df.drop(columns=['timestamp'], errors='ignore')

    model = IsolationForest(n_estimators=100, contamination=0.05, random_state=42)
    model.fit(X)

    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)
    print("✅ Model retrained")

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id='github_anomaly_retraining',
    default_args=default_args,
    schedule_interval='@weekly',
    catchup=False,
    tags=['github', 'retrain'],
) as dag:
    task = PythonOperator(task_id='retrain_model', python_callable=retrain_model)
