FROM apache/airflow:2.9.1

# Official way to install Python dependencies
COPY requirements.txt .

USER airflow
RUN pip install --no-cache-dir -r requirements.txt